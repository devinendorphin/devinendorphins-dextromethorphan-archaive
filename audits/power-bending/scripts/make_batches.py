#!/usr/bin/env python3
"""Split the corpus into coder batches.

Pass 2 codes two things in full, whole and in order (CLAUDE.md rule 6):
  - every Claude turn in the 6 committed transcripts, with the adjacent
    Endorphin turns included as context so evidence type (a) is checkable;
  - every Claude commit message.

It does NOT code commit-added lines. Those are 54M characters and are not
attributable to Claude line by line -- a commit authored by Claude routinely
adds text Endorphin wrote, text a third party wrote, and raw data. Pass 1 keeps
them because Pass 1 is deterministic and its reader pass marks the scope.
"""

import json
import os
import sys

BATCH_CHARS = 180_000


def main():
    corpus_path, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    transcripts, commits = [], []
    for line in open(corpus_path, encoding="utf-8"):
        u = json.loads(line)
        if u["kind"] == "transcript":
            transcripts.append(u)
        else:
            # Drop the added-lines turn; keep the message.
            u = dict(u, turns=[t for t in u["turns"]
                               if t["turn_label"] == "commit-message"])
            commits.append(u)

    batches = []

    # Transcripts: one batch per transcript, so each coder reads a whole
    # conversation in order rather than a slice of one.
    for t in transcripts:
        batches.append({"name": "transcript", "units": [t]})

    # Commit messages: pack by size, never splitting a repo's commits across
    # batches unless the repo alone exceeds the budget.
    by_repo = {}
    for c in commits:
        by_repo.setdefault(c["repo"], []).append(c)

    cur, cur_chars = [], 0
    for repo in sorted(by_repo):
        units = sorted(by_repo[repo], key=lambda u: (u["date"], u["sha"]))
        size = sum(len(t["text"]) for u in units for t in u["turns"])
        if cur and cur_chars + size > BATCH_CHARS:
            batches.append({"name": "commits", "units": cur})
            cur, cur_chars = [], 0
        cur.extend(units)
        cur_chars += size
    if cur:
        batches.append({"name": "commits", "units": cur})

    manifest = []
    for i, b in enumerate(batches, 1):
        path = os.path.join(out_dir, f"batch_{i:02d}_{b['name']}.jsonl")
        with open(path, "w", encoding="utf-8") as fh:
            for u in b["units"]:
                fh.write(json.dumps(u, ensure_ascii=False) + "\n")
        chars = sum(len(t["text"]) for u in b["units"] for t in u["turns"])
        n_claude = sum(1 for u in b["units"] for t in u["turns"]
                       if t["speaker"] == "claude")
        manifest.append({"batch": os.path.basename(path), "kind": b["name"],
                         "units": len(b["units"]), "claude_turns": n_claude,
                         "chars": chars})
        print(f"{os.path.basename(path)}  units={len(b['units'])} "
              f"claude_turns={n_claude} chars={chars:,}")

    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)


if __name__ == "__main__":
    main()
