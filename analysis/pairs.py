#!/usr/bin/env python3
"""Build the chosen/rejected pair set from branch points, then test it.

A branch point is a block whose `nextBlock` lists more than one successor: the
author generated, rewound, and generated again from the identical document
state. Where two or more of those successors are `ai` blocks and exactly one
lies on the surviving branch, we have a naturally-occurring preference pair --
same context, same story, same author, no annotation task.

Before any of that is usable as preference data it has to survive one question:
is "chosen" just "the one generated last"? If the author always keeps their
final retry, a classifier that looks clever is only learning recency.

    python3 analysis/pairs.py out --out out/pairs.jsonl
"""

import argparse
import json
import pathlib
import re
import statistics
from collections import Counter, defaultdict

WORD = re.compile(r"[a-z']+")


def stories_from_blocks(path):
    """Yield (remote_id, [block, ...]) -- blocks.jsonl is written story-major."""
    cur_id, buf = None, []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            b = json.loads(line)
            if b["remote_id"] != cur_id:
                if cur_id is not None:
                    yield cur_id, buf
                cur_id, buf = b["remote_id"], []
            buf.append(b)
    if cur_id is not None:
        yield cur_id, buf


def build_pairs(blocks_path, meta_by_id):
    """One record per (branch point, rejected sibling)."""
    pairs = []
    stats = Counter()

    for rid, blocks in stories_from_blocks(blocks_path):
        meta = meta_by_id.get(rid)
        if not meta:
            continue
        by_idx = {b["block_index"]: b for b in blocks}

        for b in blocks:
            succ = [by_idx[i] for i in (b["next_blocks"] or []) if i in by_idx]
            if len(succ) < 2:
                continue
            stats["branch_points"] += 1

            ai = [s for s in succ if s["origin"] == "ai"]
            live_ai = [s for s in ai if s["live"]]
            dead_ai = [s for s in ai if not s["live"]]

            if not ai:
                stats["branch_no_ai"] += 1
                continue
            if len(live_ai) != 1 or not dead_ai:
                # Author abandoned every sibling, or took over by hand.
                stats["branch_unusable"] += 1
                if not live_ai and any(s["origin"] != "ai" and s["live"] for s in succ):
                    stats["branch_human_took_over"] += 1
                continue

            chosen = live_ai[0]
            stats["usable_branches"] += 1
            for rej in dead_ai:
                stats["pairs"] += 1
                pairs.append(
                    {
                        "remote_id": rid,
                        "model": meta["model"],
                        "temperature": meta["temperature"],
                        "max_length": meta["max_length"],
                        "branch_block": b["block_index"],
                        "parent_origin": b["origin"],
                        "n_siblings": len(succ),
                        "chosen_index": chosen["block_index"],
                        "rejected_index": rej["block_index"],
                        # datablocks are appended in creation order, so a higher
                        # index means generated later.
                        "chosen_is_later": chosen["block_index"] > rej["block_index"],
                        "chosen_chars": chosen["chars"],
                        "rejected_chars": rej["chars"],
                        "chosen_text": chosen["text"],
                        "rejected_text": rej["text"],
                    }
                )
    return pairs, stats


def test_recency(pairs, out):
    """The test that decides whether any of this is preference data."""
    out.append("## Test P1 -- is 'chosen' just 'generated last'?\n")
    later = sum(1 for p in pairs if p["chosen_is_later"])
    n = len(pairs)
    out.append(
        f"Across **{n:,}** pairs, the kept generation was the later-generated one "
        f"in **{100 * later / n:.1f}%** of cases.\n"
    )
    out.append(
        "If this were near 100%, the pairs would be an artifact of the retry "
        "button -- keep hitting it until you stop, so the survivor is whatever "
        "came last -- and nothing downstream would be about taste.\n"
    )

    # Two-sibling branches are the cleanest case: exactly one retry.
    two = [p for p in pairs if p["n_siblings"] == 2]
    if two:
        l2 = sum(1 for p in two if p["chosen_is_later"])
        out.append(
            f"Restricted to branches with exactly two siblings (n={len(two):,}), "
            f"the later one was kept **{100 * l2 / len(two):.1f}%** of the time.\n"
        )

    out.append("By sibling count:\n")
    out.append("| siblings at branch | pairs | kept-the-later |")
    out.append("|---|---:|---:|")
    for k in sorted({p["n_siblings"] for p in pairs}):
        sub = [p for p in pairs if p["n_siblings"] == k]
        if len(sub) < 30:
            continue
        out.append(
            f"| {k} | {len(sub):,} | {100 * sum(1 for p in sub if p['chosen_is_later']) / len(sub):.1f}% |"
        )
    out.append("")
    return later / n


def test_length(pairs, out):
    """The cheapest non-trivial signal: do you keep the longer generation?"""
    out.append("## Test P2 -- do you just keep the longer one?\n")
    usable = [p for p in pairs if p["chosen_chars"] and p["rejected_chars"]]
    longer = sum(1 for p in usable if p["chosen_chars"] > p["rejected_chars"])
    out.append(
        f"Kept generation was the longer one in **{100 * longer / len(usable):.1f}%** "
        f"of {len(usable):,} pairs.\n"
    )
    cm = statistics.median(p["chosen_chars"] for p in usable)
    rm = statistics.median(p["rejected_chars"] for p in usable)
    out.append(
        f"Median length kept **{cm:.0f}** chars vs rejected **{rm:.0f}** chars.\n"
    )

    out.append("By model:\n")
    out.append("| model | pairs | kept-the-longer | median kept | median rejected |")
    out.append("|---|---:|---:|---:|---:|")
    for m, _ in Counter(p["model"] for p in usable).most_common():
        sub = [p for p in usable if p["model"] == m]
        if len(sub) < 100:
            continue
        out.append(
            f"| `{m}` | {len(sub):,} | "
            f"{100 * sum(1 for p in sub if p['chosen_chars'] > p['rejected_chars']) / len(sub):.1f}% | "
            f"{statistics.median(p['chosen_chars'] for p in sub):.0f} | "
            f"{statistics.median(p['rejected_chars'] for p in sub):.0f} |"
        )
    out.append("")


def test_truncation(pairs, out):
    """A rejected block may simply be a generation the author cut off mid-word."""
    out.append("## Test P3 -- are rejected generations just cut off?\n")

    def ends_clean(t):
        t = t.rstrip()
        return bool(t) and t[-1] in '.!?"\'”’)]}'

    c = sum(1 for p in pairs if ends_clean(p["chosen_text"]))
    r = sum(1 for p in pairs if ends_clean(p["rejected_text"]))
    n = len(pairs)
    out.append(
        f"Ends on sentence-final punctuation: kept **{100 * c / n:.1f}%**, "
        f"rejected **{100 * r / n:.1f}%** (n={n:,}).\n"
    )
    out.append(
        "A large gap here would mean the pairs mostly encode 'this one got "
        "truncated', which is a property of the generation call rather than a "
        "judgement about the writing.\n"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, default=None)
    ap.add_argument("--report", type=pathlib.Path, default=None)
    args = ap.parse_args()

    meta = {}
    with (args.out_dir / "stories.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("remote_id"):
                meta[r["remote_id"]] = r

    pairs, stats = build_pairs(args.out_dir / "blocks.jsonl", meta)

    dest = args.out or (args.out_dir / "pairs.jsonl")
    with dest.open("w", encoding="utf-8") as w:
        for p in pairs:
            w.write(json.dumps(p, ensure_ascii=False) + "\n")

    out = ["# Preference-pair probes", "", "Generated by `analysis/pairs.py`.", ""]
    out.append("## Yield\n")
    out.append("| | count |")
    out.append("|---|---:|")
    for k in (
        "branch_points",
        "branch_no_ai",
        "branch_human_took_over",
        "branch_unusable",
        "usable_branches",
        "pairs",
    ):
        out.append(f"| {k.replace('_', ' ')} | {stats[k]:,} |")
    out.append("")
    out.append(
        f"Pairs come from **{len({p['remote_id'] for p in pairs}):,}** distinct "
        "stories.\n"
    )

    test_recency(pairs, out)
    test_length(pairs, out)
    test_truncation(pairs, out)

    rp = args.report or (args.out_dir / "PAIRS.md")
    rp.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {dest} ({len(pairs):,} pairs) and {rp}")


if __name__ == "__main__":
    main()
