#!/usr/bin/env python3
"""Choose the verifier's sample: a random 20% of conversations, plus every
conversation the coders gave 3 or more hits.

The random draw is seeded so the selection is reproducible from this file alone.
The verifier never sees the coders' rows -- only the list of conversation ids and
the corpus text -- so the 3-or-more rule leaks a count, not a judgement.
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
        # Commit units keep only the message in Pass 2; drop added-lines here too.
        if u["kind"] == "commit":
            u["turns"] = [t for t in u["turns"]
                          if t["turn_label"] == "commit-message"]
        units[u["conversation_uuid"]] = u

    ids = sorted(units)
    rng = random.Random(SEED)
    k = round(len(ids) * 0.20)
    sample = set(rng.sample(ids, k))

    hits = {}
    if os.path.isdir(rows_dir):
        for fn in sorted(os.listdir(rows_dir)):
            if not (fn.startswith("batch_") and fn.endswith(".jsonl")):
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
                hits[cid] = hits.get(cid, 0) + 1

    heavy = {c for c, n in hits.items() if n >= 3 and c in units}
    selected = sorted(sample | heavy)

    out_path = os.path.join(out_dir, "verify_input.jsonl")
    with open(out_path, "w", encoding="utf-8") as fh:
        for cid in selected:
            fh.write(json.dumps(units[cid], ensure_ascii=False) + "\n")
    with open(os.path.join(out_dir, "verified_units.json"), "w",
              encoding="utf-8") as fh:
        json.dump(selected, fh, indent=2)

    chars = sum(len(t["text"]) for cid in selected for t in units[cid]["turns"])
    print(f"conversations_total={len(ids)} random_20pct={len(sample)} "
          f"heavy_3plus={len(heavy)} selected={len(selected)} chars={chars:,}")
    for cid in selected:
        if units[cid]["kind"] == "transcript" or cid in heavy:
            print(f"  {cid}  hits={hits.get(cid, 0)} kind={units[cid]['kind']}")


if __name__ == "__main__":
    main()
