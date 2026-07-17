# AI Filtering & Orchestration Blueprint

This is now implemented for real in [agent.py](agent.py) + [tools.py](tools.py),
not just a copy-paste template. This doc explains the design so you can adapt
the prompt or add tools later.

## Architecture

```text
you: natural-language instruction
        │
        ▼
agent.py  (LangChain create_agent, ChatAnthropic)
        │  decides which tool to call, with which args
        ▼
tools.py  (@tool wrappers — the ONLY things touching data/numbers)
        │  fetch_price_data / run_backtest / screen_universe
        ▼
data_loader.py → signals.py → backtest.py → metrics.py
        │  (pure pandas/numpy — same engine as main.py)
        ▼
output/results.json  (ground truth, written to disk)
        │
        ▼
agent reads tool output, ranks/filters, returns a Pydantic
`ScreeningResult` (response_format on create_agent)
        │
        ▼
agent.py: validate_picks() cross-checks every returned number against
output/results.json byte-for-byte before printing anything
```

The LLM controls **orchestration** (which tickers, which params, which tool,
how to rank) end to end. It never controls **arithmetic** — every numeric
field in `Pick` must match a tool result exactly, or `validate_picks` raises
and the run is rejected. That's the actual hallucination guardrail; the
system prompt is a first line of defense, `validate_picks` is the backstop
that doesn't rely on the model behaving.

## System prompt (as used in `agent.py`)

The full text is in `SYSTEM_PROMPT` in [agent.py](agent.py). Key rules:

1. Never compute/estimate/correct a numeric field — every number in the
   final answer must be copied verbatim from a tool result.
2. Never invent a ticker or stop_type a tool didn't return.
3. `profit_factor: null` means mathematically undefined (zero losing
   trades) — report it as such, never substitute a number.
4. State filter/sort criteria in plain language (auditable ranking).
5. Tool errors (e.g. "insufficient history") are reported, not silently dropped.

## Example invocation

```bash
export ANTHROPIC_API_KEY=...
python agent.py "Screen RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS from \
2019-01-01 to today with a 5% trailing stop and a 3x ATR stop. Give me the \
top 3 by total_return_pct, excluding anything with fewer than 5 trades or a \
max_drawdown_pct worse than -25%."
```

The agent will typically call `screen_universe` once (batch tool, cheaper
than one call per ticker), read back the JSON, rank it, and return a
`ScreeningResult` — which then gets validated against `output/results.json`
before being printed.

## Why this works

- The LLM never touches raw price data or does math — it calls tools that do
  it locally, and only ever ranks/filters/reasons over the returned JSON.
- `response_format=ScreeningResult` forces a typed, schema-conformant
  answer — there's no free-text slot for a fabricated metric to hide in.
- `validate_picks()` is Python-side, deterministic, and runs on every
  invocation — even if the model ignores the system prompt, a wrong number
  cannot reach you silently; the script raises instead.
- Because `screen_universe` also writes `output/results.json`, you keep the
  same audit trail as the plain CLI (`main.py`) — you can always diff what
  the agent picked against the full raw result set by hand.
