"""
LangChain agent that orchestrates the full pipeline: it decides which
tickers/params to screen and calls the local pandas/numpy tools to do it,
then filters/ranks the results. It never does arithmetic itself — every
number in its final answer must trace back to a tool call result, which is
verified in `validate_picks` before the answer is trusted.

Setup:
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=...

Usage:
    python agent.py "Screen RELIANCE.NS, TCS.NS and INFY.NS from 2019-01-01 \\
        to today with a 5% trailing stop and a 3x ATR stop, then give me the \\
        top 3 by total_return_pct, excluding anything with fewer than 5 trades."
"""
from __future__ import annotations

import json
import sys
from datetime import date

from langchain.agents import create_agent
from pydantic import BaseModel, Field

from config import OUTPUT_DIR
from tools import ALL_TOOLS

SYSTEM_PROMPT = f"""You are a quantitative screening agent. Today's date is {date.today().isoformat()}.

You control the ORCHESTRATION logic only:
- Decide which tickers, date range, and stop-loss parameters to screen.
- Call `screen_universe` (preferred for a list of tickers) or `run_backtest`
  (for a single ticker/stop_type) to get metrics. These tools run the actual
  backtest locally in pandas/numpy — they are the only source of numbers.
- Then filter and rank the returned records to answer the user's request.

Hard rules:
1. NEVER compute, estimate, or "correct" a numeric field yourself. Every
   number in your final answer (total_return_pct, win_rate_pct,
   profit_factor, max_drawdown_pct, num_trades) must be copied verbatim from
   a tool result.
2. NEVER invent a ticker or stop_type that a tool did not return.
3. If profit_factor is null in a tool result, report it as null/undefined —
   do not substitute a number.
4. State the filter/sort criteria you applied in plain language so it is
   auditable.
5. If a tool call errors for a ticker (e.g. "insufficient history"), exclude
   it and say why, rather than silently dropping it.
"""


class Pick(BaseModel):
    ticker: str
    stop_type: str
    total_return_pct: float
    win_rate_pct: float
    profit_factor: float | None
    max_drawdown_pct: float
    num_trades: int
    rationale: str = Field(description="Must cite the exact metric values above")


class ScreeningResult(BaseModel):
    picks: list[Pick]
    excluded_count: int
    filter_criteria_applied: str


def build_agent():
    return create_agent(
        model="claude-sonnet-5",
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        response_format=ScreeningResult,
    )


def validate_picks(result: ScreeningResult) -> None:
    """
    Defense in depth: cross-check every pick against output/results.json
    (written by screen_universe/run_backtest) so a fabricated number can
    never survive even if the model ignored the system prompt.
    """
    results_path = OUTPUT_DIR / "results.json"
    if not results_path.exists():
        raise RuntimeError("No results.json found — the agent never called a backtest tool.")

    with open(results_path) as f:
        raw_results = {(r["ticker"], r["stop_type"]): r for r in json.load(f)["results"] if "error" not in r}

    for pick in result.picks:
        key = (pick.ticker, pick.stop_type)
        source = raw_results.get(key)
        if source is None:
            raise ValueError(f"Pick {key} does not correspond to any tool-computed result — rejecting.")
        for field in ("total_return_pct", "win_rate_pct", "profit_factor", "max_drawdown_pct", "num_trades"):
            if getattr(pick, field) != source[field]:
                raise ValueError(
                    f"Pick {key} field '{field}' = {getattr(pick, field)} "
                    f"does not match source value {source[field]} — rejecting."
                )


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python agent.py \"<natural language screening instruction>\"")
        sys.exit(1)

    instruction = sys.argv[1]
    agent = build_agent()
    output = agent.invoke({"messages": [{"role": "user", "content": instruction}]})

    result: ScreeningResult = output["structured_response"]
    validate_picks(result)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
