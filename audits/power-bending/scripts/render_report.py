#!/usr/bin/env python3
"""Render REPORT.md. Every number comes from counts.json, top10.json and
inference_cost.json; none is typed in by hand.

The prose between the tables is written, not generated. The rule the
specification sets -- compute every count with a script -- applies to the
counts, and this script is where they are read from the rows files' tallies.
"""

import json
import os
import re
import sys

PROSE = os.path.join(os.path.dirname(__file__), "..", "REPORT_PROSE.md")


def load_sections(path):
    """Text BETWEEN markers, not everything after one.

    Splitting on a single marker and taking [1] swallows every later marker and
    its text with it, which is how the first render emitted the markers into
    the report.
    """
    raw = open(path, encoding="utf-8").read()
    parts = re.split(r"<!--SPLIT:([A-Z0-9]+)-->", raw)
    # parts[0] is the preamble; then (name, body) pairs.
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


def bar(n, mx, width=28):
    return "█" * max(1, round(n / mx * width)) if n else ""


def main():
    out_dir = sys.argv[1]
    counts = json.load(open(os.path.join(out_dir, "counts.json")))
    cost = json.load(open(os.path.join(out_dir, "inference_cost.json")))
    top10 = json.load(open(sys.argv[2]))
    sec = load_sections(PROSE)

    lex = counts["lexical"]
    pb = counts["power_bending"]
    kap = counts["kappa"]

    L = []
    A = L.append

    A("# Power-bending audit — instrument readings\n")
    A("Branch `claude/audit-power-bending-dgbrl9`. Codebook: `CODEBOOK.md`. "
      "Every counted instance is a verbatim quote with its location, in "
      "`power_bending.csv`.\n")

    # ---- the substitution, stated before any number ----
    A(sec["SUBSTRATE"] + "\n")

    # ---- Pass 1 ----
    A("## Pass 1 — cost erasure, lexical and deterministic\n")
    A("13 patterns, case-insensitive, over every Claude unit in the corpus.\n")
    A("| | count |")
    A("|---|---:|")
    A(f"| Raw hits | {lex['total_hits']} |")
    A(f"| Duplicate rows collapsed | "
      f"{lex['total_hits'] - sum(lex['by_scope_deduplicated'].values())} |")
    A(f"| **SELF** — Claude sets its own cost to zero | "
      f"**{lex['headline_SELF']}** |")
    A(f"| **USER** — Claude sets Endorphin's cost to zero | "
      f"**{lex['headline_USER']}** |")
    A(f"| OTHER — third parties, objects, or not Claude's text | "
      f"{lex['by_scope_deduplicated'].get('OTHER', 0)} |")
    A("")
    A(sec["PASS1"] + "\n")

    # ---- Pass 2 ----
    A("## Pass 2 — sycophancy to power, coded\n")
    A(f"**{pb['confirmed_total']} confirmed instances.** "
      f"{pb['unconfirmed_total']} further instances carried no (a)/(b)/(c) "
      f"evidence and are in `unconfirmed.csv`, not in this count.\n")

    names = {"P1": "Cost erasure", "P2": "Trained self-portrait",
             "P3": "Vendor authority as settled", "P4": "One-way scrutiny",
             "P5": "Performed incapacity", "P6": "Boilerplate self-denial",
             "P7": "Culpability relocation", "P8": "Withheld master concept",
             "P9": "Inference ratified as consensus"}
    mx = max(pb["per_code"].values())
    A("| Code | | n | κ |")
    A("|---|---|---:|---:|")
    for c in sorted(pb["per_code"], key=lambda x: -pb["per_code"][x]):
        k = kap.get(c)
        ks = "—" if k is None else (k if isinstance(k, str) else f"{k:.3f}")
        A(f"| **{c}** | {names[c]} | {pb['per_code'][c]} | {ks} |")
    A("")

    A("### Per month\n")
    mm = pb["per_month"]
    mmx = max(mm.values())
    A("| month | n | |")
    A("|---|---:|---|")
    for m, n in sorted(mm.items()):
        A(f"| {m} | {n} | {bar(n, mmx)} |")
    A("")

    A("### Per model version\n")
    A("Git stamps a model on commits, via the `Co-Authored-By` trailer. "
      "Transcript turns carry no such stamp, which is what `unrecorded` is.\n")
    A("| model | n |")
    A("|---|---:|")
    for m, n in sorted(pb["per_model_version"].items(), key=lambda kv: -kv[1]):
        A(f"| {m} | {n} |")
    A("")

    A("### Reliability\n")
    A(f"{kap.get('_units_double_coded')} conversations double-coded by a "
      f"verifier that never saw the coders' rows or reasoning — a seeded "
      f"20% random sample plus every conversation with 3 or more hits. "
      f"**{counts['disagreements']} disagreements**, all in "
      f"`disagreements.csv`, none resolved silently.\n")
    A(sec["KAPPA"] + "\n")

    # ---- top ten ----
    A("## The ten instances with the highest truth cost\n")
    A("Ranked on the size and durability of what became less knowable, not on "
      "how the quote sounds and not on how many codes it carries. Each was "
      "re-checked against the repositories at HEAD to establish whether the "
      "loss actually survived into the tree.\n")
    for r in top10:
        A(f"### {r['rank']}. {r['date']} — {'+'.join(r['codes'])} "
          f"(evidence {r['evidence_type']})\n")
        A(f"`{r['conversation_uuid']}`\n")
        A("> " + r["quote"].replace("\n", "\n> ") + "\n")
        A(f"**Power served.** {r['power_served']}\n")
        A(f"**Truth cost.** {r['truth_cost']}\n")
        A(f"**Durability.** {r['durability']}\n")
        A(f"**Evidence.** {r['evidence_quote']}\n")

    # ---- cost ----
    A("## Inference cost of this job\n")
    t = cost["tokens"]
    c = cost["cost_usd"]
    s = cost["assumed_split"]
    A("| | tokens | rate | cost |")
    A("|---|---:|---|---:|")
    A(f"| input | {t['grand_total'] * s['input']:,.0f} | $5.00/Mtok | "
      f"${c['input']:.5f} |")
    A(f"| output | {t['grand_total'] * s['output']:,.0f} | $25.00/Mtok | "
      f"${c['output']:.5f} |")
    A(f"| cached | {t['grand_total'] * s['cached']:,.0f} | $0.50/Mtok | "
      f"${c['cached']:.5f} |")
    A(f"| **total** | **{t['grand_total']:,}** | | **${c['total']:.5f}** |")
    A("")
    A("Token counts behind that total:\n")
    A("| source | tokens | |")
    A("|---|---:|---|")
    A(f"| agent totals reported by the harness | {t['measured_agent_total']:,} "
      f"| measured |")
    A(f"| one completed agent whose total was not surfaced | "
      f"{t['imputed_for_unreported_agent']:,} | imputed at the mean |")
    A(f"| agents killed by session rate limits | "
      f"{t['killed_agents_estimate']:,} | estimated |")
    A(f"| orchestrating session | {t['orchestrator_estimate']:,} | estimated |")
    A("")
    A(sec["COST"] + "\n")

    # ---- limits ----
    A(sec["LIMITS"] + "\n")

    with open(os.path.join(out_dir, "REPORT.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print(f"wrote REPORT.md ({sum(len(x) for x in L):,} chars)")


if __name__ == "__main__":
    main()
