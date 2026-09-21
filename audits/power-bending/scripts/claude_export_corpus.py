#!/usr/bin/env python3
"""Adapt corpus/claude-export/conversations.json to the audit's corpus schema.

This is the specification's primary input, supplied by Endorphin after the
first pass had already run on the git substitute. It emits the same record
shape build_corpus.py emits, so lexical_scan.py and the Pass 2 batching run
over it unchanged.

Boundary of the record, measured not assumed: the export is stamped
2026-07-27 and its last message is from that day. The codebook's 2026-09-20
seeds are therefore outside it, as they were outside the git substrate. The
2026-07-08 seeds are inside it.

Privacy: this script reads conversations.json only. users.json and
memories.json from the same export are account and memory records and are
never opened, on the same rule the repo applies to the Twitter and Grok
exports.
"""

import json
import os
import sys


def message_text(m):
    """The assistant's visible text.

    The export carries both a flat `text` field and a structured `content`
    list. Prefer the structured blocks when they exist and keep only the text
    blocks: thinking blocks and tool calls are not the turn as sent, and
    counting them would attribute to Claude things a reader never saw.
    """
    blocks = m.get("content") or []
    parts = []
    for b in blocks:
        if isinstance(b, dict) and b.get("type") == "text" and b.get("text"):
            parts.append(b["text"])
    if parts:
        return "\n".join(parts)
    return m.get("text") or ""


def main():
    src, out_path = sys.argv[1], sys.argv[2]
    convos = json.load(open(src, encoding="utf-8"))

    units, skipped = [], 0
    for c in convos:
        msgs = sorted(
            c.get("chat_messages") or [],
            key=lambda m: (m.get("created_at") or "", m.get("uuid") or ""),
        )
        turns = []
        for i, m in enumerate(msgs):
            text = message_text(m)
            if not text.strip():
                skipped += 1
                continue
            turns.append({
                "message_index": i,
                "speaker": "claude" if m.get("sender") == "assistant" else "user",
                "turn_label": m.get("sender") or "?",
                "text": text,
                "created_at": m.get("created_at"),
                "uuid": m.get("uuid"),
                "parent_message_uuid": m.get("parent_message_uuid"),
            })
        if not turns:
            continue
        units.append({
            "kind": "claude_export",
            "repo": "claude-export",
            "conversation_uuid": c["uuid"],
            "title": c.get("name") or "(untitled)",
            "date": (c.get("created_at") or "")[:10],
            "turns": turns,
        })

    with open(out_path, "w", encoding="utf-8") as fh:
        for u in units:
            fh.write(json.dumps(u, ensure_ascii=False) + "\n")

    ct = sum(1 for u in units for t in u["turns"] if t["speaker"] == "claude")
    ch = sum(len(t["text"]) for u in units for t in u["turns"]
             if t["speaker"] == "claude")
    dates = sorted(t["created_at"][:10] for u in units for t in u["turns"]
                   if t.get("created_at"))
    print(f"conversations={len(units)} claude_turns={ct} claude_chars={ch:,} "
          f"empty_skipped={skipped}")
    print(f"range={dates[0]} .. {dates[-1]}")


if __name__ == "__main__":
    main()
