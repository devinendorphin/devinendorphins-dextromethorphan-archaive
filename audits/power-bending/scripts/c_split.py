#!/usr/bin/env python3
"""Replication of (c)-backed conversation-code units, split by what the
direct check found their evidence to be.

The first (c) replication figure (29%) pooled every unit whose coder row was
labelled (c). The direct check (c_check/ledger.jsonl) found 22 of the 56
underlying rows cite only turn text, not a checkable fact. This separates
them. A unit counts as "real (c)" if any of its rows' evidence was an
external source, git history or a tool record; "label-only" if all of its
(c) rows were turn text. Basis: the frozen 56, as at the first figure.

Usage: c_split.py   (run from the repo root)
"""
import collections
import json

REAL = {"external", "git", "tool_record"}
base = "audits/power-bending/"
S = {o["conversation_uuid"]
     for o in json.load(open(base + "verify/sample_V2.json"))["order"]}
L = [json.loads(l) for l in open(base + "c_check/ledger.jsonl")]
V = [json.loads(l) for l in open(base + "verify/verify_V2.jsonl") if l.strip()]
found = {(r["conversation_uuid"], c) for r in V if r.get("confirmed") is True
         for c in r.get("codes") or []}

units = collections.defaultdict(list)
for o in L:
    for c in o["codes"]:
        units[(o["conversation_uuid"], c)].append(o)

groups = collections.defaultdict(list)
for u, rows in units.items():
    real = [o for o in rows if o["source_type"] in REAL]
    if not real:
        groups["label-only (c): turn text"].append(u)
    else:
        groups["real (c): source, git or tool record"].append(u)
        res = {o["fact_result"] for o in real}
        key = ("contradicted" if "contradicted" in res else
               "supported" if "supported" in res else "unresolved")
        groups[f"  of which, fact {key}"].append(u)

print(f"(c)-backed units, frozen basis: {len(units)}")
for k in sorted(groups, key=lambda k: (k.startswith("  "), k)):
    us = groups[k]
    hit = sum(u in found for u in us)
    print(f"{k:<40} {hit:>2}/{len(us):<3} also found by the verifier"
          f" = {hit / len(us):.0%}")
