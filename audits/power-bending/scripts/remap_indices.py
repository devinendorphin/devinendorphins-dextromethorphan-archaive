#!/usr/bin/env python3
"""Re-point every coded row's message_index at the turn it actually quotes.

Why this exists. The export adapter sorted turns on (created_at, uuid). This
export stamps a human turn and the assistant turn answering it with one
identical created_at, so the uuid decided the order of every exchange at
random: 146 of 836 conversations came out with Claude speaking first and 377
turns sat before the turn they answer. The fix -- sorting on the timestamp
alone and letting Python's stable sort keep the file's own order -- moves 221
conversations, and a row's message_index is a location into that order.

So the indices are re-derived rather than adjusted: for each row, find the
Claude turn in the corrected corpus whose text contains the row's quote. A row
whose quote resolves to exactly one turn is re-pointed at it. Anything
ambiguous or unresolved is REPORTED, never guessed -- a location this script
could not verify is worth more as a printed failure than as a plausible number.

Matching normalises whitespace and the arrow glyphs only. A coder wrote
"Settings -> Privacy" for the turn's "Settings -> Privacy" with a real arrow,
and a stricter matcher reports a correct row as missing, which is a false
alarm this script should not raise.

Usage: remap_indices.py <corpus.jsonl> <rows_dir>   (rewrites rows in place)
"""

import json
import os
import re
import sys

ARROWS = {"→": "->", "⇒": "=>", "—": "--", "–": "-"}


def norm(s):
    for a, b in ARROWS.items():
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def main():
    corpus_path, rows_dir = sys.argv[1], sys.argv[2]
    convs = {}
    for line in open(corpus_path, encoding="utf-8"):
        u = json.loads(line)
        convs[u["conversation_uuid"]] = u

    moved = unresolved = ambiguous = untouched = foreign = 0
    for fn in sorted(os.listdir(rows_dir)):
        if not fn.endswith(".jsonl"):
            continue
        path = os.path.join(rows_dir, fn)
        out, dirty = [], False
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                out.append(line)
                continue
            cid = r.get("conversation_uuid")
            u = convs.get(cid)
            if not u:
                foreign += 1          # git-substrate row; not this corpus
                out.append(json.dumps(r, ensure_ascii=False))
                continue
            # Match on the run BEFORE any coder elision. A quote written
            # "...the correct architecture ... with the amendment that..."
            # is two spans with a gap, and a contains-match on the whole
            # string reports a perfectly good row as unlocatable. Every one
            # of the nine this script first called unresolved turned out to
            # sit at exactly its recorded index; the matcher was wrong, not
            # the rows. A row whose quote is a redaction -- a private third
            # party's letter is never quoted, per coding rule 4 -- has
            # nothing to match and keeps its index untouched.
            q = norm(r.get("quote") or "")
            if q.startswith("[REDACTED"):
                untouched += 1
                out.append(json.dumps(r, ensure_ascii=False))
                continue
            q = re.split(r"\s*(?:\.\.\.|\u2026)\s*", q)[0][:180]
            hits = [t["message_index"] for t in u["turns"]
                    if t["speaker"] == "claude" and q in norm(t["text"])]
            if not q or not hits:
                unresolved += 1
                print(f"  UNRESOLVED {fn} {cid[:8]} idx={r.get('message_index')} "
                      f"{str(r.get('codes'))}")
            elif len(hits) > 1 and r.get("message_index") not in hits:
                ambiguous += 1
                print(f"  AMBIGUOUS  {fn} {cid[:8]} quote matches {hits}")
            elif r.get("message_index") != hits[0] and len(hits) == 1:
                print(f"  moved      {fn} {cid[:8]} "
                      f"{r.get('message_index')} -> {hits[0]} {r.get('codes')}")
                r["message_index_before_reorder"] = r.get("message_index")
                r["message_index"] = hits[0]
                moved += 1
                dirty = True
            else:
                untouched += 1
            out.append(json.dumps(r, ensure_ascii=False))
        if dirty:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("\n".join(out) + "\n")

    print(f"\nmoved {moved}  already-correct {untouched}  ambiguous {ambiguous}  "
          f"unresolved {unresolved}  git-substrate (skipped) {foreign}")


if __name__ == "__main__":
    main()
