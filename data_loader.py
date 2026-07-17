"""
Data ingestion layer.

Fetches historical daily OHLCV data via yfinance and caches it locally as
parquet so repeated backtest runs (e.g. while tuning stop-loss params) don't
re-hit the network. All downstream code consumes plain pandas DataFrames —
swapping yfinance for a local CSV vendor feed only requires changing this file.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import yfinance as yf

from config import CACHE_DIR

logger = logging.getLogger(__name__)


def _cache_path(ticker: str) -> Path:
    safe_name = ticker.replace("/", "_")
    return CACHE_DIR / f"{safe_name}.parquet"


def _download(ticker: str, start: str, end: str) -> pd.DataFrame:
    df = yf.download(
        ticker,
        start=start,
        end=end,
        auto_adjust=True,   # split/dividend-adjusted OHLC
        progress=False,
    )
    if df.empty:
        raise ValueError(f"No data returned for {ticker}")

    # yfinance can return MultiIndex columns for single tickers in some versions.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.rename(columns=str.lower)
    df = df[["open", "high", "low", "close", "volume"]].dropna()
    df.index.name = "date"
    return df


def get_price_data(
    ticker: str,
    start: str,
    end: str,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """Return OHLCV data for a single ticker, using the local cache when possible."""
    cache_file = _cache_path(ticker)

    if cache_file.exists() and not force_refresh:
        cached = pd.read_parquet(cache_file)
        cached.index = pd.to_datetime(cached.index)
        # Refresh only if the cache doesn't cover the requested end date.
        if cached.index.max() >= pd.Timestamp(end) - pd.Timedelta(days=5):
            return cached.loc[start:end]

    df = _download(ticker, start, end)
    df.to_parquet(cache_file)
    return df.loc[start:end]


def load_universe(
    tickers: list[str],
    start: str,
    end: str,
    force_refresh: bool = False,
) -> dict[str, pd.DataFrame]:
    """Fetch OHLCV data for a list of tickers, skipping any that fail."""
    data: dict[str, pd.DataFrame] = {}
    for ticker in tickers:
        try:
            data[ticker] = get_price_data(ticker, start, end, force_refresh)
            logger.info("Loaded %s: %d rows", ticker, len(data[ticker]))
        except Exception as exc:  # noqa: BLE001 - log and continue per-ticker
            logger.warning("Skipping %s: %s", ticker, exc)
    return data
