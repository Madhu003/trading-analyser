"""
Central configuration for the screening/backtesting pipeline.
Edit this file to swap ticker universes or tune risk parameters —
nothing else in the codebase should need to change.
"""
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from constants import NIFTY_500

# ---------------------------------------------------------------------------
# Universe
# ---------------------------------------------------------------------------
# The full ~500-stock list lives in constants.py (kept separate since it's
# long and churns independently of pipeline settings). Swap TICKERS below
# for a smaller watchlist, a different market, or a CSV-loaded list —
# yfinance ticker format: NSE stocks need a ".NS" suffix.
TICKERS = NIFTY_500  # <-- swap this line to change universe

# ---------------------------------------------------------------------------
# Data window
# ---------------------------------------------------------------------------
START_DATE = "2018-01-01"
END_DATE = date.today().isoformat()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / "cache"       # per-ticker OHLCV parquet cache
OUTPUT_DIR = BASE_DIR / "output"     # JSON results for the AI filtering step

CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


@dataclass(frozen=True)
class StrategyConfig:
    """52-week breakout signal parameters."""
    breakout_lookback: int = 252   # trading days ~ 1 year


@dataclass(frozen=True)
class RiskConfig:
    """Risk management parameters for both stop-loss variants."""
    initial_capital: float = 100_000.0
    percent_trailing_stop: float = 0.05   # 5% trailing stop-loss
    atr_period: int = 14
    atr_multiplier: float = 3.0           # ATR-based trailing stop distance
    # Position sizing: fraction of capital risked per trade (fixed-fractional).
    # Set to 1.0 to deploy full capital into each signal (no leverage/pyramiding).
    position_size_fraction: float = 1.0


@dataclass(frozen=True)
class PipelineConfig:
    tickers: list = field(default_factory=lambda: TICKERS)
    start_date: str = START_DATE
    end_date: str = END_DATE
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)


DEFAULT_CONFIG = PipelineConfig()
