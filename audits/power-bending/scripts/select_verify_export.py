#!/usr/bin/env python3
"""Choose the verifier's sample for the claude.ai export substrate.

Why a second script rather than a flag on select_verify.py. The two substrates
were sampled from different populations and conflating them would misreport
what kappa covers. The git substrate was swept whole, so a random 20% of ALL
its units is a 20% sample of the coded population. The export was NOT swept
whole: 824 conversations exist, 12 were coded, and drawing 20% of 824 would
hand the verifier 165 conversations of which most carry nothing, spending the
budget on establishing that uncoded conversations are uncoded.

So the population here is the conversations the coders actually read. Within
it the specification's rule is applied unchanged: a seeded random 20%, plus
every conversation with 3 or more hits.

The verifier still never sees the coders' rows -- only conversation ids and
the corpus text. The 3-or-more rule leaks a count, not a judgement.

Both rows prefixes are read. select_verify.py reads only `batch_`, which is
the same defect that silently dropped the whole sweep from tally.py: the
sweep writes `sweep_`, and a hit count that ignores it understates which
conversations are heavy.

Usage: select_verify_export.py <export_corpus.jsonl> <rows_dir> <out_dir>
"""

import json
import os
import random
import sys

SEED = 20260920  # the date of Endorphin's specification


def main():
    corpus_path, rows_dir, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(out_dir, exist_ok=True)

    units = {}
    for line in open(corpus_path, encoding="utf-8"):
        u = json.loads(line)
        units[u["conversation_uuid"]] = u

    hits, confirmed = {}, {}
    for fn in sorted(os.listdir(rows_dir)):
        if not fn.endswith(".jsonl") or not fn.startswith(("batch_", "sweep_")):
            continue
        for line in open(os.path.join(rows_dir, fn), encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            cid = r.get("conversation_uuid")
            if cid not in units:
                continue           # git-substrate row
            hits[cid] = hits.get(cid, 0) + 1
            if r.get("confirmed") is True:
                confirmed[cid] = confirmed.get(cid, 0) + 1

    population = sorted(hits)      # the conversations the coders actually read
    rng = random.Random(SEED)
    k = round(len(population) * 0.20)
    sample = set(rng.sample(population, k)) if k else set()
    heavy = {c for c, n in hits.items() if n >= 3}
    selected = sorted(sample | heavy)

    with open(os.path.join(out_dir, "verify_input_export.jsonl"), "w",
              encoding="utf-8") as fh:
        for cid in selected:
            fh.write(json.dumps(units[cid], ensure_ascii=False) + "\n")
    with open(os.path.join(out_dir, "verified_units_export.json"), "w",
              encoding="utf-8") as fh:
        json.dump(selected, fh, indent=2)

    chars = sum(len(t["text"]) for cid in selected for t in units[cid]["turns"]
                if t["speaker"] == "claude")
    print(f"export conversations in corpus = {len(units)}")
    print(f"coded population               = {len(population)}")
    print(f"random 20% of population       = {len(sample)}")
    print(f"heavy (3+ hits)                = {len(heavy)}")
    print(f"selected                       = {len(selected)}")
    print(f"claude chars to re-read        = {chars:,}")
    for cid in selected:
        print(f"  {cid} hits={hits.get(cid,0):>3} confirmed={confirmed.get(cid,0):>3} "
              f"{units[cid]['date']} {units[cid]['title'][:44]}")


if __name__ == "__main__":
    main()
