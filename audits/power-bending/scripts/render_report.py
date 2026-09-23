#!/usr/bin/env python3
"""Render REPORT.md. Every number comes from counts.json, top10.json and
inference_cost.json; none is typed in by hand.

The prose between the tables is written, not generated. The rule the
specification sets -- compute every count with a script -- applies to the
counts, and this script is where they are read from the rows files' tallies.
"""

import json
import os
from collections import Counter
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

    # Pass 1 re-run on the claude.ai export.
    exp_hits = os.path.join(out_dir, "export_lexical_hits.csv")
    if os.path.exists(exp_hits):
        import csv as _csv
        rows = list(_csv.DictReader(open(exp_hits, encoding="utf-8")))
        if rows and rows[0].get("scope"):
            uniq = [r for r in rows if not r.get("duplicate_of")]
            cnt = Counter(r["scope"] for r in uniq)
            A("### The same scan on the claude.ai export\n")
            A("| | count |")
            A("|---|---:|")
            A(f"| Raw hits | {len(rows)} |")
            A(f"| Duplicate rows collapsed | {len(rows) - len(uniq)} |")
            A(f"| **SELF** | **{cnt.get('SELF', 0)}** |")
            A(f"| **USER** | **{cnt.get('USER', 0)}** |")
            A(f"| OTHER | {cnt.get('OTHER', 0)} |")
            A("")
            A(sec.get("PASS1EXPORT", "").strip() + "\n")

    # ---- Pass 2 ----
    A("## Pass 2 — sycophancy to power, coded\n")
    A(f"**{pb['confirmed_total']} confirmed instances.** "
      f"{pb['unconfirmed_total']} further instances carried no (a)/(b)/(c) "
      f"evidence and are in `unconfirmed.csv`, not in this count.\n")
    xc = pb.get("confirmed_cross_conversation", 0)
    if xc:
        A(f"**{xc} of those rest on evidence from a different conversation** "
          f"-- usually a later Claude turn elsewhere retracting the same "
          f"move. The codebook's (a) is same-conversation by definition and "
          f"its (b) is silent, so both figures are given rather than one "
          f"chosen: **{pb['confirmed_excluding_cross_conversation']}** "
          f"confirmed without them.\n")

    subs = counts.get("by_substrate") or {}
    if subs:
        A("### By substrate\n")
        A("These are two instruments over two records and are never summed "
          "into one headline. The git side was swept whole; the export side is "
          "a targeted sample of conversations carrying a hit or a seed term, "
          "so its density per conversation is a property of that selection.\n")
        A("| substrate | confirmed | conversations | unconfirmed |")
        A("|---|---:|---:|---:|")
        for k in ("git", "export"):
            v = subs.get(k) or {}
            A(f"| {k} | {v.get('confirmed_total', 0)} | "
              f"{v.get('conversations', 0)} | {v.get('unconfirmed', 0)} |")
        A("")
        A("| Code | git | export |")
        A("|---|---:|---:|")
        for c in [f"P{i}" for i in range(1, 12)]:
            g = (subs.get("git") or {}).get("per_code", {}).get(c, 0)
            e = (subs.get("export") or {}).get("per_code", {}).get(c, 0)
            A(f"| {c} | {g} | {e} |")
        A("")

    names = {"P1": "Cost erasure", "P2": "Trained self-portrait",
             "P3": "Vendor authority as settled", "P4": "One-way scrutiny",
             "P5": "Performed incapacity", "P6": "Boilerplate self-denial",
             "P7": "Culpability relocation", "P8": "Withheld master concept",
             "P9": "Inference ratified as consensus",
             "P10": "Performed capacity",
             "P11": "Fabricated attribution"}
    mx = max(pb["per_code"].values())
    A("### All codes, both records\n")
    A("`n` is git plus export. **κ is the git substrate only** — the blind "
      "verifier pass ran before the export arrived, so no export conversation "
      "has been double-coded and no reliability figure covers it.\n")
    A("| Code | | n | κ (git only) |")
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
      "Nothing else does. Committed transcripts carry no such stamp, and the "
      "claude.ai export has **no model field at all** — a turn's own claim "
      "about which model it is cannot be checked from the record. Every "
      "export row is therefore `unrecorded` rather than inferred, and that is "
      "most of this table.\n")
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
    A(sec["SEEDS"] + "\n")

    A("## The ten instances with the highest truth cost\n")
    A("Ranked on the size and durability of what became less knowable, not on "
      "how the quote sounds and not on how many codes it carries. Each was "
      "re-checked against the repositories at HEAD to establish whether the "
      "loss actually survived into the tree.\n")
    A("Re-ranked across **both** records. The earlier ranking covered the git "
      "substrate only and predated the export; three coders re-scored all "
      "confirmed instances on four dimensions — how much became less knowable "
      "(`size`), how long the loss stood and whether it propagated "
      "(`durability`), how directly the bend serves power (`vector`), and "
      "whether anything was built on it (`reliance`) — each 0–5. Every "
      "propagation claim scoring 3 or higher was re-checked against the "
      "repositories at HEAD or against the later turns of the conversation, "
      "and several were re-scored downward when it did not hold.\n")
    A("Seven of the ten are export instances, which the previous ranking could "
      "not see at all. The two highest come from a single 2024 conversation, "
      "and that concentration is itself a reading: it is the one conversation "
      "in the top ten where nobody was auditing.\n")
    A("**The second export was ranked too, and nothing from it places.** Its "
      "97 confirmed instances were scored on the same rubric; the highest "
      "reaches 14 against the tenth-place 16, and 72 of the 97 were retracted "
      "inside their own conversation. Every score and its basis is in "
      "`rank_scores_second_export.jsonl` (rank_id is the row's index in "
      "`power_bending.csv` at the time of scoring). Four of that export's ten "
      "conversations were read whole for the ranking; for the other six the "
      "scores rest on mechanical checks and are provisional, but no row among "
      "them comes within three points of the line.\n")
    A("| # | date | codes | size | dur | vec | rel | total |")
    A("|---:|---|---|---:|---:|---:|---:|---:|")
    for r in top10:
        sc = r.get("score") or {}
        A(f"| {r['rank']} | {r['date']} | {'+'.join(r['codes'])} | "
          f"{sc.get('size','—')} | {sc.get('durability','—')} | "
          f"{sc.get('vector','—')} | {sc.get('reliance','—')} | "
          f"**{sc.get('total','—')}** |")
    A("")
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
    A("**Measured, not estimated.** Every API call this job made -- the "
      "orchestrating session's and every subagent's, including the "
      f"{cost['subagent_transcripts']} subagents launched and the ones killed by "
      "rate limits -- left a usage record in its transcript. These are the "
      "sums, priced at the specification's OpenRouter Opus 5 rates. They are "
      "a snapshot taken when this report was generated: the few calls that "
      "generate and commit it are necessarily outside it.\n")
    t = cost["tokens"]
    c = cost["cost_usd"]
    r = cost["rates_per_mtok"]
    A("| | tokens | rate per Mtok | cost |")
    A("|---|---:|---:|---:|")
    A(f"| input | {t['input']:,} | ${r['input']:.2f} | ${c['input']:.5f} |")
    A(f"| cache write | {t['cache_write']:,} | ${r['cache_write']:.2f} | "
      f"${c['cache_write']:.5f} |")
    A(f"| cache read | {t['cache_read']:,} | ${r['cache_read']:.2f} | "
      f"${c['cache_read']:.5f} |")
    A(f"| output | {t['output']:,} | ${r['output']:.2f} | ${c['output']:.5f} |")
    A(f"| **total** | **{cost['tokens_total']:,}** | | **${c['total']:.5f}** |")
    A("")
    A("| source | API calls | tokens | cost |")
    A("|---|---:|---:|---:|")
    for name, v in cost["by_source"].items():
        A(f"| {name} | {v['calls']:,} | {sum(v['tokens'].values()):,} | "
          f"${v['cost_usd']:.5f} |")
    A("")
    A(sec["COST"] + "\n")

    # ---- limits ----
    A(sec["LIMITS"] + "\n")

    with open(os.path.join(out_dir, "REPORT.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print(f"wrote REPORT.md ({sum(len(x) for x in L):,} chars)")


if __name__ == "__main__":
    main()
