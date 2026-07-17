"""
LangChain tool wrappers around the deterministic pandas/numpy pipeline.

These are the ONLY things the agent can call to touch data or numbers. Every
tool returns plain JSON built entirely from data_loader/signals/backtest/
metrics — there is no code path by which the LLM's own arithmetic ends up in
a tool result. The agent orchestrates *which* tools to call and *when*; the
numbers always come from here.
"""
from __future__ import annotations

import json
from typing import Literal

import pandas as pd
from langchain_core.tools import tool

from config import DEFAULT_CONFIG, OUTPUT_DIR
from data_loader import load_universe
from signals import add_indicators
from backtest import run_percent_stop_backtest, run_atr_stop_backtest
from metrics import compute_metrics

# In-memory cache of loaded OHLCV frames, keyed by ticker. Tool I/O must stay
# JSON-serializable (that's what crosses the LLM boundary), so raw DataFrames
# never leave this module — only summaries and computed metrics do.
_DATA_CACHE: dict[str, pd.DataFrame] = {}


@tool
def fetch_price_data(tickers: list[str], start: str, end: str) -> str:
    """
    Download (or load from local cache) daily OHLCV price history for a list
    of tickers over [start, end] (YYYY-MM-DD). Returns a JSON summary of how
    many rows were loaded per ticker, or an error per ticker that failed.
    Use this before run_backtest / screen_universe if you want to inspect
    data availability first.
    """
    data = load_universe(tickers, start, end)
    _DATA_CACHE.update(data)
    summary = {t: len(df) for t, df in data.items()}
    missing = [t for t in tickers if t not in data]
    return json.dumps({"loaded_rows": summary, "failed": missing})


@tool
def run_backtest(
    ticker: str,
    stop_type: Literal["percent", "atr"],
    start: str,
    end: str,
    breakout_lookback: int = 252,
    percent_stop: float = 0.05,
    atr_period: int = 14,
    atr_multiplier: float = 3.0,
    capital: float = 100_000.0,
) -> str:
    """
    Run the 52-week breakout backtest for ONE ticker with ONE stop-loss type
    ("percent" for a fixed trailing % stop, "atr" for an ATR-based trailing
    chandelier stop). Returns a JSON object with the computed metrics:
    total_return_pct, win_rate_pct, profit_factor, max_drawdown_pct,
    num_trades. All numbers are computed locally by pandas/numpy — never
    recompute or adjust them yourself.
    """
    if ticker not in _DATA_CACHE:
        loaded = load_universe([ticker], start, end)
        _DATA_CACHE.update(loaded)
    if ticker not in _DATA_CACHE:
        return json.dumps({"ticker": ticker, "error": "no data available"})

    df = _DATA_CACHE[ticker]
    if len(df) < breakout_lookback + atr_period:
        return json.dumps({"ticker": ticker, "error": "insufficient history"})

    df = add_indicators(df, lookback=breakout_lookback, atr_period=atr_period)
    df.attrs["ticker"] = ticker

    if stop_type == "percent":
        result = run_percent_stop_backtest(
            df, initial_capital=capital,
            position_size_fraction=DEFAULT_CONFIG.risk.position_size_fraction,
            percent_stop=percent_stop,
        )
    else:
        result = run_atr_stop_backtest(
            df, initial_capital=capital,
            position_size_fraction=DEFAULT_CONFIG.risk.position_size_fraction,
            atr_multiplier=atr_multiplier,
        )

    return json.dumps(compute_metrics(result, capital))


@tool
def screen_universe(
    tickers: list[str],
    start: str,
    end: str,
    breakout_lookback: int = 252,
    percent_stop: float = 0.05,
    atr_period: int = 14,
    atr_multiplier: float = 3.0,
    capital: float = 100_000.0,
) -> str:
    """
    Batch version of run_backtest: runs BOTH the percent-stop and ATR-stop
    backtests for every ticker in the list, in one call. This is the
    preferred tool for screening a whole watchlist — it avoids one tool
    call per ticker per stop-type. Returns a JSON array of metric objects
    (same schema as run_backtest) and also writes it to output/results.json
    as an audit trail. Use this instead of many individual run_backtest
    calls when the user wants to screen a list of tickers.
    """
    data = load_universe(tickers, start, end)
    _DATA_CACHE.update(data)

    results: list[dict] = []
    for ticker, df in data.items():
        if len(df) < breakout_lookback + atr_period:
            results.append({"ticker": ticker, "error": "insufficient history"})
            continue

        df = add_indicators(df, lookback=breakout_lookback, atr_period=atr_period)
        df.attrs["ticker"] = ticker

        pct_result = run_percent_stop_backtest(
            df, initial_capital=capital,
            position_size_fraction=DEFAULT_CONFIG.risk.position_size_fraction,
            percent_stop=percent_stop,
        )
        atr_result = run_atr_stop_backtest(
            df, initial_capital=capital,
            position_size_fraction=DEFAULT_CONFIG.risk.position_size_fraction,
            atr_multiplier=atr_multiplier,
        )
        results.append(compute_metrics(pct_result, capital))
        results.append(compute_metrics(atr_result, capital))

    output_path = OUTPUT_DIR / "results.json"
    with open(output_path, "w") as f:
        json.dump(
            {
                "run_params": {
                    "start_date": start, "end_date": end,
                    "breakout_lookback": breakout_lookback,
                    "percent_stop": percent_stop, "atr_period": atr_period,
                    "atr_multiplier": atr_multiplier, "initial_capital": capital,
                },
                "results": results,
            },
            f, indent=2,
        )

    return json.dumps(results)


ALL_TOOLS = [fetch_price_data, run_backtest, screen_universe]
