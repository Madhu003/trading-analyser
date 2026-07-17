"""
Event-driven backtest engine.

Deliberately NOT built on vectorbt/backtrader: a trailing ATR stop that must
recompute every bar off a rolling ATR value doesn't map cleanly onto
vectorbt's vectorized stop primitives (its sl_stop/tsl_stop are fixed at
entry), and backtrader pulls in a much heavier dependency + API surface than
this single-strategy pipeline needs. This engine is ~150 lines of pandas/
numpy, fully deterministic, and easy to audit line-by-line — which matters
more here than raw simulation speed for a few hundred tickers.

Rules enforced:
- Long-only, single open position per ticker at a time (no pyramiding).
- Entry signal computed on day T's close is executed at day T+1's open
  (no lookahead).
- Stops are checked intraday against that day's low; if the day's open
  already gaps below the stop, the fill is at the open (never a better
  price than what the market actually offered).
- Trailing stops only ratchet upward, never loosen.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class Trade:
    entry_date: pd.Timestamp
    entry_price: float
    exit_date: pd.Timestamp | None = None
    exit_price: float | None = None
    shares: float = 0.0
    exit_reason: str | None = None

    @property
    def pnl(self) -> float:
        if self.exit_price is None:
            return 0.0
        return (self.exit_price - self.entry_price) * self.shares

    @property
    def return_pct(self) -> float:
        if self.exit_price is None:
            return 0.0
        return (self.exit_price / self.entry_price) - 1.0


@dataclass
class BacktestResult:
    ticker: str
    stop_type: str
    trades: list[Trade] = field(default_factory=list)
    equity_curve: pd.Series | None = None


def _run_stop_simulation(
    df: pd.DataFrame,
    initial_capital: float,
    position_size_fraction: float,
    stop_type: str,
    percent_stop: float,
    atr_multiplier: float,
) -> BacktestResult:
    """
    Core loop shared by both stop-loss variants. `stop_type` is either
    "percent" (fixed trailing % stop) or "atr" (ATR-based chandelier stop).
    """
    dates = df.index
    opens = df["open"].to_numpy()
    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()
    closes = df["close"].to_numpy()
    signals = df["entry_signal"].to_numpy()
    atr = df["atr"].to_numpy() if "atr" in df.columns else np.full(len(df), np.nan)

    cash = initial_capital
    equity_curve = np.empty(len(df))
    trades: list[Trade] = []

    in_position = False
    pending_entry = False
    shares = 0.0
    entry_price = 0.0
    highest_since_entry = 0.0  # highest close (percent stop) / highest high (ATR stop)
    stop_price = 0.0
    current_trade: Trade | None = None

    for i in range(len(df)):
        # --- Handle a pending entry from yesterday's signal, at today's open ---
        if pending_entry and not in_position:
            entry_price = opens[i]
            capital_to_deploy = cash * position_size_fraction
            shares = capital_to_deploy / entry_price
            cash -= shares * entry_price
            in_position = True
            pending_entry = False
            highest_since_entry = closes[i] if stop_type == "percent" else highs[i]
            if stop_type == "percent":
                stop_price = highest_since_entry * (1 - percent_stop)
            else:
                stop_price = highest_since_entry - atr_multiplier * atr[i]
            current_trade = Trade(entry_date=dates[i], entry_price=entry_price, shares=shares)

        # --- Manage an open position: check stop, then ratchet it ---
        if in_position:
            # Gap-down protection: fill at open if the market opened below the stop.
            if opens[i] <= stop_price:
                exit_price = opens[i]
                cash += shares * exit_price
                current_trade.exit_date = dates[i]
                current_trade.exit_price = exit_price
                current_trade.exit_reason = "stop_gap"
                trades.append(current_trade)
                in_position = False
                current_trade = None
            elif lows[i] <= stop_price:
                exit_price = stop_price
                cash += shares * exit_price
                current_trade.exit_date = dates[i]
                current_trade.exit_price = exit_price
                current_trade.exit_reason = "stop_hit"
                trades.append(current_trade)
                in_position = False
                current_trade = None
            else:
                # Ratchet the trailing stop upward only.
                if stop_type == "percent":
                    highest_since_entry = max(highest_since_entry, closes[i])
                    stop_price = max(stop_price, highest_since_entry * (1 - percent_stop))
                else:
                    highest_since_entry = max(highest_since_entry, highs[i])
                    if not np.isnan(atr[i]):
                        stop_price = max(stop_price, highest_since_entry - atr_multiplier * atr[i])

        # --- Queue a new entry for tomorrow's open if today produced a signal ---
        if not in_position and not pending_entry and signals[i]:
            pending_entry = True

        # --- Mark-to-market equity ---
        equity_curve[i] = cash + (shares * closes[i] if in_position else 0.0)

    # Close any position still open at the end of the data window (mark at last close).
    if in_position and current_trade is not None:
        exit_price = closes[-1]
        cash += shares * exit_price
        current_trade.exit_date = dates[-1]
        current_trade.exit_price = exit_price
        current_trade.exit_reason = "end_of_data"
        trades.append(current_trade)
        equity_curve[-1] = cash

    return BacktestResult(
        ticker=df.attrs.get("ticker", "UNKNOWN"),
        stop_type=stop_type,
        trades=trades,
        equity_curve=pd.Series(equity_curve, index=dates, name="equity"),
    )


def run_percent_stop_backtest(
    df: pd.DataFrame,
    initial_capital: float,
    position_size_fraction: float,
    percent_stop: float,
) -> BacktestResult:
    return _run_stop_simulation(
        df,
        initial_capital=initial_capital,
        position_size_fraction=position_size_fraction,
        stop_type="percent",
        percent_stop=percent_stop,
        atr_multiplier=0.0,
    )


def run_atr_stop_backtest(
    df: pd.DataFrame,
    initial_capital: float,
    position_size_fraction: float,
    atr_multiplier: float,
) -> BacktestResult:
    return _run_stop_simulation(
        df,
        initial_capital=initial_capital,
        position_size_fraction=position_size_fraction,
        stop_type="atr",
        percent_stop=0.0,
        atr_multiplier=atr_multiplier,
    )
