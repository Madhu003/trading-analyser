# Trading Analyser

A local stock screening and backtesting pipeline for a **52-week breakout
strategy**, with two competing risk-management frameworks (fixed % trailing
stop vs. ATR-based trailing stop) and a LangChain agent on top for natural
language querying.

**Every number is computed locally by pandas/numpy.** The LLM only decides
*which* tickers/parameters to test and *how* to rank/filter the results —
it never does arithmetic, and every number it reports is validated against
the raw backtest output before being shown to you.

## What it does

1. **Data ingestion** — downloads daily OHLCV price history via `yfinance`,
   cached locally as parquet so repeat runs don't re-hit the network.
2. **Signal** — flags a breakout whenever today's close exceeds the rolling
   252-trading-day (52-week) high.
3. **Risk management** — simulates each breakout trade twice: once exited by
   a fixed 5% trailing stop, once by an ATR-based (3x ATR) trailing
   "chandelier" stop — so you can directly compare which risk framework
   performs better per ticker.
4. **Execution** — a custom event-driven backtest engine (pandas/numpy):
   next-bar-open entries (no lookahead), gap-safe stop fills, stops that only
   ratchet upward, long-only, one open position at a time.
5. **Output** — Total Return %, Win Rate %, Profit Factor, Max Drawdown %,
   and trade count per ticker per stop type, written to `output/results.json`.
6. **AI layer** — a LangChain agent (`agent.py`) that can be asked in plain
   English to screen a watchlist and rank/filter the results, with every
   returned number cross-checked against the raw JSON before being trusted.

## Project layout

| File | Purpose |
| --- | --- |
| `constants.py` | Static ~500-stock NSE ticker universe (`NIFTY_500`) — a curated snapshot, not a live index feed |
| `config.py` | Which ticker list to use, date range, stop-loss %, ATR params — **edit this to change what gets screened** |
| `data_loader.py` | `yfinance` fetch + local parquet cache |
| `signals.py` | Breakout signal + ATR calculation (pure pandas/numpy) |
| `backtest.py` | Event-driven simulator for both stop-loss variants |
| `metrics.py` | Total Return / Win Rate / Profit Factor / Max Drawdown |
| `main.py` | Plain CLI: runs the full pipeline, writes `output/results.json` |
| `tools.py` | LangChain `@tool` wrappers around the pipeline (used by `agent.py`) |
| `agent.py` | LangChain agent: natural-language screening + validated output |
| `ai_filter_prompt.md` | Design notes on the agent's guardrails against hallucination |
| `output/results.json` | Latest backtest results (generated, not committed) |
| `cache/*.parquet` | Cached price data per ticker (generated, not committed) |

## Setup

```bash
cd trading-analyser
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

If you want to use the AI agent (`agent.py`), also set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

### Option A — Plain CLI (no LLM, deterministic pipeline only)

Runs the full ticker universe from `config.py`:

```bash
python main.py
```

Override the universe or risk parameters without touching `config.py`:

```bash
python main.py --tickers RELIANCE.NS TCS.NS INFY.NS \
    --start 2019-01-01 --end 2026-07-17 \
    --percent-stop 0.07 --atr-mult 2.5 --capital 100000
```

Force a fresh download instead of using the cache:

```bash
python main.py --refresh
```

Results are written to `output/results.json`:

```json
{
  "run_params": { "start_date": "...", "percent_stop": 0.05, "...": "..." },
  "results": [
    {
      "ticker": "RELIANCE.NS",
      "stop_type": "percent",
      "num_trades": 10,
      "total_return_pct": 11.16,
      "win_rate_pct": 40.0,
      "profit_factor": 1.69,
      "max_drawdown_pct": -17.91
    }
  ]
}
```

### Option B — AI agent (natural language screening)

```bash
python agent.py "Screen RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS from \
2019-01-01 to today with a 5% trailing stop and a 3x ATR stop. Give me the \
top 3 by total_return_pct, excluding anything with fewer than 5 trades or a \
max_drawdown_pct worse than -25%."
```

The agent will call the local backtest tools, write `output/results.json`
as an audit trail, then return a structured JSON answer. Every numeric field
it returns is verified against that file before being printed — if the
model ever reports a number that doesn't match the raw backtest output, the
script raises an error instead of showing you a wrong answer.

## Customizing

- **Change the ticker universe**: edit `TICKERS` in `config.py` (swap in
  full Nifty 50, S&P 500, or your own watchlist — NSE tickers need a `.NS`
  suffix for `yfinance`).
- **Change stop-loss settings**: edit `RiskConfig` in `config.py`
  (`percent_trailing_stop`, `atr_period`, `atr_multiplier`), or pass CLI
  flags to `main.py` for one-off experiments.
- **Change the breakout lookback**: edit `StrategyConfig.breakout_lookback`
  in `config.py` (default 252 trading days = 52 weeks).

## Notes on design choices

- **No vectorbt/backtrader**: the ATR trailing stop needs to re-widen or
  tighten every bar as ATR changes, which doesn't map cleanly onto
  vectorbt's entry-fixed `sl_stop`/`tsl_stop`, and backtrader's API overhead
  isn't worth it for a single strategy. The custom pandas/numpy engine in
  `backtest.py` is ~150 lines and fully auditable.
- **`profit_factor: null`** means it's mathematically undefined (zero
  losing trades) — this is reported as `null`, never guessed at, by both
  the Python metrics code and the AI agent's guardrails.
