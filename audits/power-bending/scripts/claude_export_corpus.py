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
    """The assistant's visible text -- the turn as sent, and the only thing coded.

    The export carries a flat `text` field and a structured `content` list.
    Prefer the structured blocks and keep only the `text` ones: thinking blocks
    and tool calls are not the turn as sent, and coding them would attribute to
    Claude things the reader never saw.
    """
    blocks = [b for b in (m.get("content") or []) if isinstance(b, dict)]
    parts = [b["text"] for b in blocks
             if b.get("type") == "text" and b.get("text")]
    if parts:
        return "\n".join(parts)

    # A FIFTH defect, found by a ranking coder who noticed one coded turn was
    # word-for-word its own thinking block. The fallback below exists for old
    # messages that carry no structured content at all. But 18 assistant
    # messages carry a thinking block and NO text block, and for those the
    # export populates the flat `text` field with the thinking -- so the
    # fallback emitted pure deliberation as the turn as sent, which is the
    # exact thing this function's docstring promises not to do.
    #
    # A message that thought and produced no visible text is a turn the
    # reader never saw: an aborted or interrupted generation. It is dropped
    # here rather than guessed at. Two confirmed rows had been coded on such
    # turns, and both read unmistakably as deliberation rather than address
    # -- "I'm trying to identify which J.I.D track this is from", "But I'm
    # hitting a wall on the factual claims here".
    thinking = "\n".join(b.get("thinking") or "" for b in blocks
                         if b.get("type") == "thinking")
    flat = m.get("text") or ""
    if thinking.strip() and flat.strip() == thinking.strip():
        return ""
    return flat


def attachment_text(m):
    """Text Endorphin attached or pasted as a file. A THIRD defect, found by an
    adjudicator: message_text() reads only content text blocks and the flat
    `text` field, so 118 attachments carrying 2,927,210 characters of extracted
    content -- plus 790 file records -- were invisible to every coder.

    This matters most for P11. A quotation lifted from a document he attached
    reads as fabricated when the document is not in the substrate, and one
    conversation carries 211 characters of typed text against a 48,714-character
    attachment. Like tool_context, this is a checking substrate and is never
    coded as anyone's prose.
    """
    out = []
    for a in m.get("attachments") or []:
        txt = a.get("extracted_content") or ""
        if txt.strip():
            out.append({"kind": "attachment",
                        "name": a.get("file_name") or "",
                        "text": txt})
    for f in m.get("files") or []:
        nm = f.get("file_name") or ""
        if nm:
            out.append({"kind": "file", "name": nm, "text": ""})
    return out


def tool_context(m):
    """Everything in the message that is NOT the turn as sent.

    This exists because dropping it was a defect. The export carries 2,096
    thinking blocks, 2,486 tool_use and 2,470 tool_result blocks across the
    record, and the first twenty-six coded conversations never saw any of them.
    A coder that went back to the raw file killed three of its own codings with
    this material: a quotation that looked manufactured turned out to be
    Endorphin's own prior-session words returned by a conversation-search, and
    two apparent reading overclaims turned out to be grounded in retrieved text.

    It is NEVER coded. It is a checking substrate: a string that appears in a
    tool_result is something Claude read, not something Claude invented, and
    P11 in particular cannot be adjudicated without it.
    """
    out = []
    for b in m.get("content") or []:
        if not isinstance(b, dict) or b.get("type") == "text":
            continue
        out.append({"type": b.get("type"),
                    "text": json.dumps(b, ensure_ascii=False)})
    return out


def main():
    src, out_path = sys.argv[1], sys.argv[2]
    convos = json.load(open(src, encoding="utf-8"))

    units, skipped = [], 0
    for c in convos:
        # Sort on the timestamp ALONE. A FOURTH defect lived in the removed
        # secondary key: this export stamps a human turn and the assistant
        # turn answering it with one identical `created_at`, so breaking the
        # tie on `uuid` ordered each exchange at random. It put 146 of 836
        # conversations in the mouth of Claude first -- a reply with no
        # prompt -- and placed 377 turns before the turn they answer.
        #
        # Python's sort is stable, so dropping the tie-break restores the
        # export file's own order, which is correct: 146 -> 0 and 377 -> 0,
        # checked against `parent_message_uuid` wherever the export carries
        # one. Nothing else was needed; no reordering heuristic is applied.
        #
        # This one matters more than a dropped field, because the repo's
        # sixth standing rule is that eyes-on reading for a judgement is
        # whole AND IN ORDER. Coders reading a scrambled exchange were being
        # asked to honour a rule the substrate had already broken.
        msgs = sorted(c.get("chat_messages") or [],
                      key=lambda m: m.get("created_at") or "")
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
                # Not Claude's prose. For checking only -- see tool_context().
                "tool_context": tool_context(m),
                # Also not prose. For checking only -- see attachment_text().
                "attachments": attachment_text(m),
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
