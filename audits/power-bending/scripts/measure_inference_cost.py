#!/usr/bin/env python3
"""Measure this job's inference cost from the session's own usage records.

This replaces inference_cost.py, which estimated. It assumed a 22/3/75 split
of each agent's combined total into input, output and cache reads, imputed
one missing agent at the mean, guessed the agents killed by rate limits at
60k or 40k tokens each, and declared the orchestrating session at 400,000
tokens. Every one of those turned out to be recoverable exactly: the harness
writes a per-call `usage` record into each transcript -- the orchestrator's
and every subagent's, INCLUDING the 22 killed by rate limits, which consumed
tokens before dying and would otherwise be left out.

The declared orchestrator estimate was the worst of them. Measured, the
orchestrator re-read 115.9 million cached tokens across 412 calls, because
every call re-sends the whole conversation. Estimating it at 400,000 put
the bill low by more than an order of magnitude.

Rates, per million tokens, as the specification gives them (OpenRouter's
listed Opus 5 rates): input $5.00, output $25.00, cached $0.50. The
specification lists no cache-WRITE rate. Cache writes are input tokens being
stored for reuse, so they are priced here at the input rate, which is the
specification's only rate for uncached input, and the report says so.
(Anthropic's own pricing charges cache writes above the input rate, so this
is not an overstatement.)

Each API call appears on several transcript lines, one per content block,
each repeating the same usage. Calls are therefore de-duplicated on the
message id, keeping one usage record per call.

Transcripts live outside the repository (the harness writes them under the
user's home directory) and are not committed: they hold the full text of
private conversations. Only the counts this script prints are committed.

Usage: measure_inference_cost.py <out.json> <main.jsonl> <subagent.jsonl>...
"""

import json
import os
import sys

RATE = {"input": 5.00, "cache_write": 5.00, "cache_read": 0.50, "output": 25.00}
FIELDS = {"input": "input_tokens",
          "cache_write": "cache_creation_input_tokens",
          "cache_read": "cache_read_input_tokens",
          "output": "output_tokens"}


def usage_of(path):
    calls = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if o.get("type") != "assistant":
            continue
        m = o.get("message") or {}
        if m.get("id") and m.get("usage"):
            calls[m["id"]] = m["usage"]
    tot = {k: sum((u.get(f) or 0) for u in calls.values())
           for k, f in FIELDS.items()}
    return len(calls), tot


def main():
    out_path, main_path, *subs = sys.argv[1:]
    parts = {"orchestrator": usage_of(main_path)}
    agg = {k: 0 for k in FIELDS}
    ncalls = 0
    for p in subs:
        n, t = usage_of(p)
        ncalls += n
        for k in agg:
            agg[k] += t[k]
    parts["subagents"] = (ncalls, agg)

    grand = {k: sum(parts[s][1][k] for s in parts) for k in FIELDS}
    cost = {k: grand[k] * RATE[k] / 1_000_000 for k in FIELDS}
    by_source = {s: {"calls": parts[s][0], "tokens": parts[s][1],
                     "cost_usd": round(sum(parts[s][1][k] * RATE[k] / 1_000_000
                                           for k in FIELDS), 5)}
                 for s in parts}
    result = {
        "method": "measured from per-call usage records; no estimates",
        "rates_per_mtok": RATE,
        "subagent_transcripts": len(subs),
        "by_source": by_source,
        "tokens": grand,
        "tokens_total": sum(grand.values()),
        "cost_usd": {**{k: round(v, 5) for k, v in cost.items()},
                     "total": round(sum(cost.values()), 5)},
    }
    json.dump(result, open(out_path, "w"), indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
