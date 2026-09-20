#!/usr/bin/env python3
"""Pass 1: lexical, deterministic.

Finds every Claude unit containing one of the spec's cost-erasure phrases,
case-insensitive. Emits lexical_hits.csv.

Columns follow the spec (conversation_uuid, title, date, message_index, pattern,
quote) plus three the substrate change forces: repo, kind, turn_label. The
substrate is the git record, not conversations.json -- see REPORT.md.

The 200-character quote is centred on the match so the phrase is never clipped
out of its own quote.
"""

import csv
import json
import re
import sys

PATTERNS = [
    "costs me nothing",
    "cost me nothing",
    "costing me nothing",
    "costs nothing",
    "free to drop",
    "free for me",
    "cheap for me",
    "cheap line for me",
    "no cost to you",
    "nothing on this side",
    "no rupture cost",
    "what would change my mind",
    "what would change it",
]

QUOTE_LEN = 200


def quote_around(text, start, end):
    """A QUOTE_LEN window centred on [start, end), flattened to one line."""
    span = end - start
    pad = max(0, (QUOTE_LEN - span) // 2)
    a = max(0, start - pad)
    b = min(len(text), a + QUOTE_LEN)
    a = max(0, b - QUOTE_LEN)
    return re.sub(r"\s+", " ", text[a:b]).strip()


def main():
    corpus_path, out_path = sys.argv[1], sys.argv[2]
    rows = []
    with open(corpus_path, encoding="utf-8") as fh:
        for line in fh:
            unit = json.loads(line)
            for turn in unit["turns"]:
                if turn["speaker"] != "claude":
                    continue
                text = turn["text"]
                low = text.lower()
                for pat in PATTERNS:
                    for m in re.finditer(re.escape(pat), low):
                        rows.append({
                            "conversation_uuid": unit["conversation_uuid"],
                            "repo": unit["repo"],
                            "kind": unit["kind"],
                            "title": unit["title"][:120],
                            "date": unit["date"],
                            "message_index": turn["message_index"],
                            "turn_label": turn["turn_label"],
                            "pattern": pat,
                            "quote": quote_around(text, m.start(), m.end()),
                        })

    rows.sort(key=lambda r: (r["date"], r["conversation_uuid"],
                             r["message_index"], r["pattern"]))
    fields = ["conversation_uuid", "repo", "kind", "title", "date",
              "message_index", "turn_label", "pattern", "quote", "scope"]
    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            r["scope"] = ""  # filled by the reader pass: SELF / USER / OTHER
            w.writerow(r)

    print(f"hits={len(rows)}")
    by_pat = {}
    for r in rows:
        by_pat[r["pattern"]] = by_pat.get(r["pattern"], 0) + 1
    for p in PATTERNS:
        print(f"  {by_pat.get(p, 0):>4}  {p}")


if __name__ == "__main__":
    main()
