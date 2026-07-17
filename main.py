"""
Pipeline orchestrator.

Usage:
    python main.py
    python main.py --tickers RELIANCE.NS TCS.NS --percent-stop 0.07 --atr-mult 2.5
    python main.py --refresh   # force re-download instead of using cache

Output: output/results.json — a flat list of per-ticker, per-stop-type
metrics dicts, ready to hand to the AI filtering step described in
ai_filter_prompt.md.
"""
from __future__ import annotations

import argparse
import json
import logging

from config import DEFAULT_CONFIG, OUTPUT_DIR
from data_loader import load_universe
from signals import add_indicators
from backtest import run_percent_stop_backtest, run_atr_stop_backtest
from metrics import compute_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="52-week breakout screener & backtester")
    parser.add_argument("--tickers", nargs="+", default=None, help="Override the ticker universe")
    parser.add_argument("--start", default=DEFAULT_CONFIG.start_date)
    parser.add_argument("--end", default=DEFAULT_CONFIG.end_date)
    parser.add_argument("--lookback", type=int, default=DEFAULT_CONFIG.strategy.breakout_lookback)
    parser.add_argument("--percent-stop", type=float, default=DEFAULT_CONFIG.risk.percent_trailing_stop)
    parser.add_argument("--atr-period", type=int, default=DEFAULT_CONFIG.risk.atr_period)
    parser.add_argument("--atr-mult", type=float, default=DEFAULT_CONFIG.risk.atr_multiplier)
    parser.add_argument("--capital", type=float, default=DEFAULT_CONFIG.risk.initial_capital)
    parser.add_argument("--refresh", action="store_true", help="Force re-download, ignore cache")
    return parser.parse_args()


def run_pipeline(args: argparse.Namespace) -> list[dict]:
    tickers = args.tickers or DEFAULT_CONFIG.tickers
    logger.info("Universe: %d tickers", len(tickers))

    price_data = load_universe(tickers, args.start, args.end, force_refresh=args.refresh)

    results: list[dict] = []
    for ticker, df in price_data.items():
        if len(df) < args.lookback + args.atr_period:
            logger.warning("Skipping %s: insufficient history (%d rows)", ticker, len(df))
            continue

        df = add_indicators(df, lookback=args.lookback, atr_period=args.atr_period)
        df.attrs["ticker"] = ticker

        percent_result = run_percent_stop_backtest(
            df,
            initial_capital=args.capital,
            position_size_fraction=DEFAULT_CONFIG.risk.position_size_fraction,
            percent_stop=args.percent_stop,
        )
        atr_result = run_atr_stop_backtest(
            df,
            initial_capital=args.capital,
            position_size_fraction=DEFAULT_CONFIG.risk.position_size_fraction,
            atr_multiplier=args.atr_mult,
        )

        results.append(compute_metrics(percent_result, args.capital))
        results.append(compute_metrics(atr_result, args.capital))

        logger.info("Backtested %s (percent + ATR stop)", ticker)

    return results


def main() -> None:
    args = parse_args()
    results = run_pipeline(args)

    output_path = OUTPUT_DIR / "results.json"
    with open(output_path, "w") as f:
        json.dump(
            {
                "run_params": {
                    "start_date": args.start,
                    "end_date": args.end,
                    "breakout_lookback": args.lookback,
                    "percent_stop": args.percent_stop,
                    "atr_period": args.atr_period,
                    "atr_multiplier": args.atr_mult,
                    "initial_capital": args.capital,
                },
                "results": results,
            },
            f,
            indent=2,
        )
    logger.info("Wrote %d metric records to %s", len(results), output_path)


if __name__ == "__main__":
    main()
