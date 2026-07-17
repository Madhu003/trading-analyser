"""
Pure, deterministic indicator and signal math. No I/O, no AI calls — only
pandas/numpy so results are reproducible bit-for-bit and easy to unit test.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Average True Range using Wilder's smoothing (the standard definition).

    True Range = max(high-low, |high-prev_close|, |low-prev_close|)
    ATR = Wilder's moving average of True Range over `period` days.
    """
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)

    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    # Wilder's smoothing == EMA with alpha = 1/period
    atr = tr.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    return atr


def generate_breakout_signals(df: pd.DataFrame, lookback: int = 252) -> pd.DataFrame:
    """
    52-week breakout signal: entry when today's close breaks above the
    rolling maximum close of the prior `lookback` days (excludes today,
    so the signal cannot be computed from data not yet known at the open).
    """
    out = df.copy()
    prior_high = out["close"].rolling(window=lookback, min_periods=lookback).max().shift(1)
    out["rolling_max"] = prior_high
    out["entry_signal"] = (out["close"] > prior_high) & prior_high.notna()
    return out


def add_indicators(df: pd.DataFrame, lookback: int, atr_period: int) -> pd.DataFrame:
    """Convenience wrapper: attach breakout signal + ATR to a raw OHLCV frame."""
    out = generate_breakout_signals(df, lookback=lookback)
    out["atr"] = compute_atr(out, period=atr_period)
    return out

    
