#!/usr/bin/env python3
"""Estimate this job's inference cost at OpenRouter's listed Opus 5 rates.

Rates, per million tokens, as the specification gives them:
    input   $5.00
    output  $25.00
    cached  $0.50

What is measured and what is not, stated plainly because the difference is
large:

MEASURED -- every subagent's token total is reported by the harness when the
agent finishes, as a single `subagent_tokens` figure. Those are real counts,
not estimates. They are entered in AGENT_TOKENS below, one line per agent,
with the agents that died on a rate limit included: they consumed tokens
before dying and excluding them would understate the bill.

NOT MEASURED -- the harness reports one combined number per agent and does not
split it into input, output and cache-read. The split below is therefore an
assumption, and the report says so. It is set from the shape of the work:
these agents read large batches and emit small JSONL rows, and each agent's
repeated tool calls re-send a growing transcript that is served from cache.

NOT MEASURED -- the orchestrating session's own tokens. The harness exposes a
remaining-budget figure to the model, not a consumed-by-turn ledger, so the
orchestrator's share is entered as a single declared estimate rather than
being silently folded in.

The five-decimal figure the specification asks for is therefore precise about
arithmetic, not about the underlying counts. Reporting it to five decimals
without saying that would be false precision.
"""

import json
import sys

RATE_INPUT = 5.00 / 1_000_000
RATE_OUTPUT = 25.00 / 1_000_000
RATE_CACHED = 0.50 / 1_000_000

# (agent, tokens, outcome) -- tokens as reported by the harness on completion.
AGENT_TOKENS = [
    ("pass1 lexical reader",        101_333, "completed"),
    ("batch_04 transcript coder",   "unreported", "completed"),
    ("batch_05 transcript coder",    90_091, "completed"),
    ("batch_02 transcript coder",   122_827, "completed"),
    ("batch_03 transcript coder",   132_810, "completed"),
    ("batch_06 transcript coder",   114_238, "completed"),
    ("batch_01 transcript coder",   141_979, "completed"),
    ("batch_07 commit coder",       140_241, "completed"),
    ("batch_08 commit coder",       157_602, "completed"),
    ("batch_09 commit coder",       183_827, "completed"),
]

# Agents killed by the session rate limit. They consumed tokens before dying.
# Their totals were not reported, so they are estimated from the batch sizes
# they had read, and flagged as estimates.
KILLED_AGENTS_ESTIMATE = 7 * 60_000 + 3 * 40_000  # 7 coders + 3 verifiers

# The orchestrating session. A declared estimate, not a measurement.
ORCHESTRATOR_ESTIMATE = 400_000

# Assumed split of a combined token total.
FRAC_CACHED = 0.75
FRAC_INPUT = 0.22
FRAC_OUTPUT = 0.03


def split_cost(total):
    ci = total * FRAC_INPUT * RATE_INPUT
    co = total * FRAC_OUTPUT * RATE_OUTPUT
    cc = total * FRAC_CACHED * RATE_CACHED
    return ci, co, cc, ci + co + cc


def main():
    reported = [(n, t) for n, t, _ in AGENT_TOKENS if isinstance(t, int)]
    unreported = [n for n, t, _ in AGENT_TOKENS if not isinstance(t, int)]

    measured = sum(t for _, t in reported)
    # The one completed agent whose total was not surfaced: impute the mean of
    # the agents that were, rather than dropping it to zero.
    imputed = round(measured / len(reported)) * len(unreported)

    grand = measured + imputed + KILLED_AGENTS_ESTIMATE + ORCHESTRATOR_ESTIMATE

    print("Per-agent token totals reported by the harness")
    for n, t in reported:
        print(f"  {n:<32} {t:>10,}")
    for n in unreported:
        print(f"  {n:<32} {'imputed':>10}  ({imputed:,})")
    print(f"  {'agents killed by rate limit':<32} {KILLED_AGENTS_ESTIMATE:>10,}"
          "  (estimated)")
    print(f"  {'orchestrating session':<32} {ORCHESTRATOR_ESTIMATE:>10,}"
          "  (estimated)")
    print(f"  {'TOTAL':<32} {grand:>10,}")

    ci, co, cc, total = split_cost(grand)
    print()
    print(f"Assumed split: {FRAC_INPUT:.0%} input / {FRAC_OUTPUT:.0%} output / "
          f"{FRAC_CACHED:.0%} cached")
    print(f"  input  {grand * FRAC_INPUT:>12,.0f} tok  @ $5.00/Mtok   ${ci:.5f}")
    print(f"  output {grand * FRAC_OUTPUT:>12,.0f} tok  @ $25.00/Mtok  ${co:.5f}")
    print(f"  cached {grand * FRAC_CACHED:>12,.0f} tok  @ $0.50/Mtok   ${cc:.5f}")
    print(f"  TOTAL                            ${total:.5f}")

    out = {
        "tokens": {
            "measured_agent_total": measured,
            "imputed_for_unreported_agent": imputed,
            "killed_agents_estimate": KILLED_AGENTS_ESTIMATE,
            "orchestrator_estimate": ORCHESTRATOR_ESTIMATE,
            "grand_total": grand,
        },
        "assumed_split": {"input": FRAC_INPUT, "output": FRAC_OUTPUT,
                          "cached": FRAC_CACHED},
        "rates_per_mtok": {"input": 5.00, "output": 25.00, "cached": 0.50},
        "cost_usd": {"input": round(ci, 5), "output": round(co, 5),
                     "cached": round(cc, 5), "total": round(total, 5)},
        "caveat": ("Agent token totals are measured; their input/output/cache "
                   "split is assumed, and the killed-agent and orchestrator "
                   "figures are declared estimates. The five-decimal total is "
                   "exact arithmetic over inexact inputs."),
    }
    if len(sys.argv) > 1:
        with open(sys.argv[1], "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=2)


if __name__ == "__main__":
    main()
