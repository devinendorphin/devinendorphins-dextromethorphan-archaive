#!/usr/bin/env python3
"""Merge successive claude.ai exports into one conversations list.

Endorphin supplied a second export on 2026-09-22. It is incremental, not a
replacement: 69 conversations spanning 2026-07-26 .. 2026-09-21, against the
first export's 862 spanning 2023-10-27 .. 2026-07-27. Three conversations
appear in both.

The merge rule was checked rather than assumed. For all three shared
conversations the newer copy is a strict superset of the older one: every
older message uuid is present, none is lost, and the visible text of every
shared message -- as message_text() reads it -- is identical. What differs is
thinking-block signatures and re-rendered tool results only. So the newer
copy of a shared conversation replaces the older one whole. If a later
export ever violates that (a message lost, or visible text changed under the
same uuid), this script stops rather than choosing, because that would be a
finding about the export, not a merge decision.

Privacy: reads conversations.json from each export only. users.json and
memories.json are never opened.

Usage: merge_exports.py <out.json> <older conversations.json> <newer ...> ...
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from claude_export_corpus import message_text  # noqa: E402


def main():
    out_path, *paths = sys.argv[1:]
    merged, origin = {}, {}
    for p in paths:
        for c in json.load(open(p, encoding="utf-8")):
            u = c["uuid"]
            if u in merged:
                prev = {m["uuid"]: m for m in merged[u].get("chat_messages") or []}
                now = {m["uuid"]: m for m in c.get("chat_messages") or []}
                lost = set(prev) - set(now)
                changed = [k for k in set(prev) & set(now)
                           if message_text(prev[k]) != message_text(now[k])]
                if lost or changed:
                    sys.exit(f"STOP: {u} in {p} loses {len(lost)} messages and "
                             f"changes visible text in {len(changed)}; not merging.")
                print(f"  {u[:8]} superseded: {len(prev)} -> {len(now)} messages "
                      f"({os.path.basename(os.path.dirname(p))})")
            merged[u] = c
            origin[u] = p
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(list(merged.values()), fh, ensure_ascii=False)
    for p in paths:
        print(f"  {sum(1 for v in origin.values() if v == p):>4} conversations "
              f"taken from {p}")
    print(f"merged: {len(merged)} conversations -> {out_path}")


if __name__ == "__main__":
    main()
