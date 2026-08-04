#!/usr/bin/env python3
"""Flatten a directory of NovelAI story exports into one tidy record per story.

Reads  <corpus>/json/*.json   (NovelAI `story` + `content` export pairs)
Writes stories.jsonl + blocks.jsonl

One row per story in stories.jsonl; one row per *edit-history block* in
blocks.jsonl. The block stream is the interesting half: NovelAI keeps the whole
undo DAG, so every AI continuation the author kept, retried, or deleted is still
in the file.
"""

import argparse
import json
import pathlib
import sys
from collections import Counter

# Origins NovelAI stamps on datablocks/fragments.
#   root/prompt -> the seed the human typed
#   ai          -> a model continuation
#   user        -> text the human typed mid-story
#   edit        -> the human rewriting existing text in place
HUMAN_ORIGINS = {"root", "prompt", "user", "edit"}


def epoch_seconds(ts):
    """NovelAI mixes units: story.lastUpdatedAt is seconds, story.data.* is ms."""
    if not isinstance(ts, (int, float)):
        return None
    return int(ts / 1000) if ts > 1e12 else int(ts)


def block_text(block):
    frag = block.get("dataFragment") or {}
    return frag.get("data") or ""


def live_path(blocks, current):
    """Block indices on the surviving branch: walk prevBlock back from the head.

    NovelAI keeps every abandoned branch in datablocks. Anything not reachable
    this way is text the author generated and then rewound past -- that, and not
    `removedFragments`, is the honest record of a rejected generation.
    """
    seen = set()
    i = current
    guard = 0
    while isinstance(i, int) and 0 <= i < len(blocks) and i not in seen:
        seen.add(i)
        guard += 1
        if guard > len(blocks) + 5:
            break
        i = blocks[i].get("prevBlock")
    return seen


def summarize_blocks(story):
    """Walk datablocks in file order, tallying authorship and revision behaviour."""
    blocks = story.get("datablocks") or []
    chars = Counter()
    counts = Counter()
    removed_chars = 0
    removed_from_ai = 0
    rows = []

    for i, b in enumerate(blocks):
        origin = b.get("origin") or "unknown"
        text = block_text(b)
        counts[origin] += 1
        chars[origin] += len(text)

        # removedFragments = text this block deleted. When the deleted text was
        # AI-authored, that is the author rejecting a generation.
        removed = b.get("removedFragments") or []
        rm_len = sum(len(f.get("data") or "") for f in removed)
        rm_ai = sum(
            len(f.get("data") or "")
            for f in removed
            if (f.get("origin") or "") == "ai"
        )
        removed_chars += rm_len
        removed_from_ai += rm_ai

        rows.append(
            {
                "block_index": i,
                "origin": origin,
                "chars": len(text),
                "removed_chars": rm_len,
                "removed_ai_chars": rm_ai,
                "prev_block": b.get("prevBlock"),
                "next_blocks": b.get("nextBlock") or [],
                "chain": bool(b.get("chain")),
                "text": text,
            }
        )

    # A branch point = a block with >1 successor. That is a retry: the author
    # rewound and generated again from the same position.
    branch_points = sum(1 for b in blocks if len(b.get("nextBlock") or []) > 1)
    extra_branches = sum(
        max(0, len(b.get("nextBlock") or []) - 1) for b in blocks
    )

    # Kept vs abandoned, by reachability from the head block.
    live = live_path(blocks, story.get("currentBlock"))
    live_ai = live_ai_blocks = 0
    dead_ai = dead_ai_blocks = 0
    for i, b in enumerate(blocks):
        if (b.get("origin") or "") != "ai":
            continue
        n = len(block_text(b))
        if i in live:
            live_ai += n
            live_ai_blocks += 1
        else:
            dead_ai += n
            dead_ai_blocks += 1
    for r in rows:
        r["live"] = r["block_index"] in live

    return rows, {
        "current_block": story.get("currentBlock"),
        "live_blocks": len(live),
        "live_ai_chars": live_ai,
        "live_ai_blocks": live_ai_blocks,
        "abandoned_ai_chars": dead_ai,
        "abandoned_ai_blocks": dead_ai_blocks,
        "n_blocks": len(blocks),
        "blocks_by_origin": dict(counts),
        "chars_by_origin": dict(chars),
        "ai_chars": chars.get("ai", 0),
        "human_chars": sum(chars[o] for o in chars if o in HUMAN_ORIGINS),
        # NOTE: removed_* conflates genuine rejection with whole-document
        # rewrites, where the editor deletes all existing text (charging every
        # prior AI character to `removed`) and re-inserts it as a `user` block.
        # It is kept for provenance; use abandoned_ai_* for rejection.
        "removed_chars": removed_chars,
        "removed_ai_chars": removed_from_ai,
        "branch_points": branch_points,
        "extra_branches": extra_branches,
        "final_step": story.get("step"),
        "n_fragments": len(story.get("fragments") or []),
    }


def context_entry(ctx, idx):
    """context[0] is Memory, context[1] is Author's Note in every export seen."""
    try:
        return ctx[idx].get("text") or ""
    except (IndexError, AttributeError, TypeError):
        return ""


def extract(path):
    doc = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    smeta = (doc.get("story") or {}).get("data") or {}
    content = (doc.get("content") or {}).get("data") or {}
    settings = content.get("settings") or {}
    params = settings.get("parameters") or {}
    story = content.get("story") or {}
    lore = content.get("lorebook") or {}

    rows, agg = summarize_blocks(story)

    # Sampler order matters as much as the values: NovelAI applies the
    # truncation samplers in the listed sequence.
    order = params.get("order") or []
    order_ids = [o.get("id") for o in order if isinstance(o, dict)]
    order_enabled = [
        o.get("id") for o in order if isinstance(o, dict) and o.get("enabled")
    ]

    bias_groups = content.get("phraseBiasGroups") or []
    n_bias = sum(len(g.get("phrases") or []) for g in bias_groups if isinstance(g, dict))
    ban_groups = content.get("bannedSequenceGroups") or []
    n_banned = sum(
        len(g.get("sequences") or []) for g in ban_groups if isinstance(g, dict)
    )

    ctx = content.get("context") or []
    memory = context_entry(ctx, 0)
    authors_note = context_entry(ctx, 1)

    rec = {
        "file": path.name,
        "remote_id": smeta.get("remoteId"),
        "title": smeta.get("title"),
        "created_at": epoch_seconds(smeta.get("createdAt")),
        "last_updated_at": epoch_seconds(
            (doc.get("story") or {}).get("lastUpdatedAt")
            or smeta.get("lastUpdatedAt")
        ),
        "favorite": smeta.get("favorite"),
        "tags": smeta.get("tags") or [],
        "text_preview": smeta.get("textPreview") or "",
        # --- generation configuration -------------------------------------
        "model": settings.get("model"),
        "preset": settings.get("preset"),
        "module": settings.get("prefix"),
        "prefix_mode": settings.get("prefixMode"),
        "trim_responses": settings.get("trimResponses"),
        "ban_brackets": settings.get("banBrackets"),
        "dynamic_penalty_range": settings.get("dynamicPenaltyRange"),
        "settings_version": params.get("textGenerationSettingsVersion"),
        "temperature": params.get("temperature"),
        "max_length": params.get("max_length"),
        "min_length": params.get("min_length"),
        "top_k": params.get("top_k"),
        "top_p": params.get("top_p"),
        "top_a": params.get("top_a"),
        "typical_p": params.get("typical_p"),
        "tail_free_sampling": params.get("tail_free_sampling"),
        "cfg_scale": params.get("cfg_scale"),
        "mirostat_tau": params.get("mirostat_tau"),
        "mirostat_lr": params.get("mirostat_lr"),
        "math1_temp": params.get("math1_temp"),
        "math1_quad": params.get("math1_quad"),
        "min_p": params.get("min_p"),
        "repetition_penalty": params.get("repetition_penalty"),
        "repetition_penalty_range": params.get("repetition_penalty_range"),
        "repetition_penalty_slope": params.get("repetition_penalty_slope"),
        "repetition_penalty_frequency": params.get("repetition_penalty_frequency"),
        "repetition_penalty_presence": params.get("repetition_penalty_presence"),
        "phrase_rep_pen": params.get("phrase_rep_pen"),
        "sampler_order": order_ids,
        "sampler_order_enabled": order_enabled,
        # --- steering apparatus -------------------------------------------
        "memory_chars": len(memory),
        "authors_note_chars": len(authors_note),
        "memory": memory,
        "authors_note": authors_note,
        "lorebook_entries": len(lore.get("entries") or []),
        "lorebook_categories": len(lore.get("categories") or []),
        "phrase_bias_phrases": n_bias,
        "banned_sequences": n_banned,
        "did_generate": content.get("didGenerate"),
    }
    rec.update(agg)
    return rec, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus", type=pathlib.Path, help="directory of *.json exports")
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("."))
    ap.add_argument(
        "--with-blocks",
        action="store_true",
        help="also emit blocks.jsonl (large: full text of every revision)",
    )
    args = ap.parse_args()

    files = sorted(args.corpus.glob("*.json"))
    if not files:
        sys.exit(f"no *.json under {args.corpus}")

    args.out.mkdir(parents=True, exist_ok=True)
    n_ok = n_bad = 0
    bad = []

    with (args.out / "stories.jsonl").open("w", encoding="utf-8") as fs:
        fb = (
            (args.out / "blocks.jsonl").open("w", encoding="utf-8")
            if args.with_blocks
            else None
        )
        try:
            for p in files:
                try:
                    rec, rows = extract(p)
                except Exception as exc:  # noqa: BLE001 - report and continue
                    n_bad += 1
                    bad.append(f"{p.name}\t{type(exc).__name__}: {exc}")
                    continue
                n_ok += 1
                fs.write(json.dumps(rec, ensure_ascii=False) + "\n")
                if fb:
                    for r in rows:
                        r["remote_id"] = rec["remote_id"]
                        fb.write(json.dumps(r, ensure_ascii=False) + "\n")
        finally:
            if fb:
                fb.close()

    if bad:
        (args.out / "extract_errors.txt").write_text("\n".join(bad) + "\n")
    print(f"parsed {n_ok} stories, {n_bad} failed -> {args.out}/stories.jsonl")


if __name__ == "__main__":
    main()
