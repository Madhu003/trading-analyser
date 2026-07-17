"""
Deterministic performance metrics computed from raw trade/equity data.
No LLM ever touches these numbers — the AI layer only reads this output.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest import BacktestResult


def max_drawdown_pct(equity_curve: pd.Series) -> float:
    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    return float(drawdown.min() * 100) if len(drawdown) else 0.0


def compute_metrics(result: BacktestResult, initial_capital: float) -> dict:
    trades = result.trades
    equity = result.equity_curve

    num_trades = len(trades)
    total_return_pct = (
        ((equity.iloc[-1] / initial_capital) - 1.0) * 100 if equity is not None and len(equity) else 0.0
    )

    if num_trades == 0:
        return {
            "ticker": result.ticker,
            "stop_type": result.stop_type,
            "num_trades": 0,
            "total_return_pct": round(total_return_pct, 2),
            "win_rate_pct": 0.0,
            "profit_factor": None,
            "max_drawdown_pct": round(max_drawdown_pct(equity), 2) if equity is not None else 0.0,
        }

    pnls = np.array([t.pnl for t in trades])
    wins = pnls[pnls > 0]
    losses = pnls[pnls <= 0]

    win_rate_pct = (len(wins) / num_trades) * 100
    gross_profit = wins.sum()
    gross_loss = abs(losses.sum())
    # profit_factor is undefined (infinite) with zero losses; report null rather
    # than a fabricated number so the AI filtering step doesn't hallucinate on it.
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else None

    return {
        "ticker": result.ticker,
        "stop_type": result.stop_type,
        "num_trades": num_trades,
        "total_return_pct": round(total_return_pct, 2),
        "win_rate_pct": round(win_rate_pct, 2),
        "profit_factor": round(profit_factor, 2) if profit_factor is not None else None,
        "max_drawdown_pct": round(max_drawdown_pct(equity), 2),
    }
