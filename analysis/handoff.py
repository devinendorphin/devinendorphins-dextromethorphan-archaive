#!/usr/bin/env python3
"""Why does a bare `Name:` work?

`CUES.md` finds that a handoff carrying no content at all -- a name, a colon,
nothing else -- is followed by a generation in that voice 89.7% of the time.
Two explanations, and they make opposite predictions:

  * **Scene-tracking.** The model is following who is in the room. Then a name
    already established in this session should be taken up more reliably than
    one appearing for the first time, because only the established name has
    anything in context to attach to.
  * **Convention strength.** `Name:` is simply an overwhelming formatting cue in
    the training data. Then a brand-new name should work just as well, because
    the model is completing a template rather than tracking a cast.

The test is whether uptake depends on prior establishment. Novel names also let
us separate a stronger claim: a first-appearance name has *no* referent in
context, so if the model still stays in voice, the effect is the convention.

Uptake is measured as: does the following generation open without switching to
a *different* speaker tag inside its first 80 characters?

    python3 analysis/handoff.py out --report analysis/HANDOFF.md
"""

import argparse
import json
import math
import pathlib
import re
import statistics
from collections import Counter, defaultdict

SPEAKER = re.compile(r"^\s*([A-Za-z0-9][\w .,'’\-()]{0,38}):(\s*)(.*)$", re.S)
SPEAKER_ANYWHERE = re.compile(r"([A-Za-z][\w .,'’\-()]{0,38}):\s")
WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")


def is_name(c):
    c = c.strip()
    return bool(c) and c[0].isupper() and len(c.split()) <= 4


def handoff_name(text):
    """The name in a bare `Name:` handoff, or None if this is not one."""
    m = SPEAKER.match(text.strip())
    if not m or not is_name(m.group(1)):
        return None
    if m.group(3).strip():
        return None  # something follows the colon: a speaker line, not a handoff
    return m.group(1).strip()


def wilson(k, n, z=1.96):
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def stories_from_blocks(path):
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


def collect(blocks_path, meta):
    """Every bare-handoff turn, labelled by whether the name was already in play."""
    rows = []
    for rid, blocks in stories_from_blocks(blocks_path):
        m = meta.get(rid)
        if not m:
            continue
        live = sorted((b for b in blocks if b.get("live")), key=lambda b: b["block_index"])
        seen_text = []          # everything before the current turn, in order
        seen_lower = ""
        for i, b in enumerate(live):
            if b["origin"] != "ai":
                name = handoff_name(b["text"])
                if name and i + 1 < len(live) and live[i + 1]["origin"] == "ai":
                    head = live[i + 1]["text"][:80]
                    other = SPEAKER_ANYWHERE.search(head)
                    switched = bool(
                        other and other.group(1).strip().lower() != name.lower()
                    )
                    # Was this name used anywhere earlier in the session?
                    established = name.lower() in seen_lower
                    rows.append(
                        {
                            "remote_id": rid,
                            "model": m["model"],
                            "name": name,
                            "established": established,
                            "prior_chars": len(seen_lower),
                            "held": not switched,
                            "next_text": live[i + 1]["text"][:200],
                            "cue": b["text"],
                        }
                    )
            seen_text.append(b["text"])
            seen_lower += b["text"].lower()
    seen, keep = set(), []
    for r in rows:
        k = (r["cue"], r["next_text"])
        if k in seen:
            continue
        seen.add(k)
        keep.append(r)
    return rows, keep


def rate_row(label, sub, out):
    if not sub:
        return
    k = sum(1 for r in sub if r["held"])
    lo, hi = wilson(k, len(sub))
    out.append(
        f"| {label} | {len(sub):,} | **{100 * k / len(sub):.1f}%** | "
        f"{100 * lo:.1f}–{100 * hi:.1f}% |"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir", type=pathlib.Path)
    ap.add_argument("--report", type=pathlib.Path, default=None)
    args = ap.parse_args()

    meta = {}
    with (args.out_dir / "stories.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("remote_id") and r["ai_chars"] > 0:
                meta[r["remote_id"]] = r

    raw, rows = collect(args.out_dir / "blocks.jsonl", meta)
    out = ["# Why a bare `Name:` works", "", "Generated by `analysis/handoff.py`.", ""]
    out.append(
        f"**{len(raw):,}** bare-handoff turns followed by a generation, "
        f"**{len(rows):,}** distinct after removing duplicated stories. Uptake = "
        "the generation does not switch to a different speaker tag in its first "
        "80 characters.\n"
    )

    est = [r for r in rows if r["established"]]
    nov = [r for r in rows if not r["established"]]

    out.append("## Established names against first appearances\n")
    out.append("| name | handoffs | voice held | 95% CI |")
    out.append("|---|---:|---:|---|")
    rate_row("already used earlier in the session", est, out)
    rate_row("first appearance in the session", nov, out)
    rate_row("all", rows, out)
    out.append("")

    if est and nov:
        ke, kn = sum(1 for r in est if r["held"]), sum(1 for r in nov if r["held"])
        pe, pn = ke / len(est), kn / len(nov)
        gap = 100 * (pe - pn)
        # Two-proportion z-test. Overlapping Wilson intervals are a conservative
        # and misleading proxy for this comparison, so do it properly.
        pooled = (ke + kn) / (len(est) + len(nov))
        se = math.sqrt(pooled * (1 - pooled) * (1 / len(est) + 1 / len(nov)))
        z = (pe - pn) / se if se else 0.0
        pval = math.erfc(abs(z) / math.sqrt(2))
        out.append(
            f"Gap: **{gap:+.1f} points** in favour of established names "
            f"(two-proportion z = {z:.2f}, p = {pval:.3f}).\n"
        )
        out.append(
            "**Both things are true, and the larger one is the convention.** A "
            f"name the model has never seen still holds **{100 * pn:.1f}%** of "
            "the time. There is no referent for it anywhere in the session — "
            "the model cannot be tracking a cast member it has not met — so "
            "that share is `Name:` working as a formatting template.\n"
        )
        if pval < 0.05:
            out.append(
                f"On top of that, establishment adds a real but small "
                f"**{gap:+.1f} points** (p = {pval:.3f}). So the model does "
                "attend to who is already in the room; it just is not where "
                "most of the effect comes from.\n"
            )
        else:
            out.append(
                f"The {gap:+.1f}-point advantage for established names does not "
                f"reach significance (p = {pval:.3f}), so on this evidence "
                "scene-tracking adds nothing detectable.\n"
            )
        out.append(
            "This makes the 89.7% headline in `CUES.md` a weaker result about "
            "partnership than it first looked. It was offered as the cleanest "
            "evidence that the model was tracking the scene. Most of it is the "
            "strength of a formatting convention, and the scene-tracking "
            "component is a few points on top.\n"
        )

    out.append("## Does more prior context help?\n")
    out.append(
        "If the model is tracking a cast, more session text before the handoff "
        "should mean better uptake. Bucketed by how much text preceded it.\n"
    )
    out.append("| prior session text | handoffs | voice held | 95% CI |")
    out.append("|---|---:|---:|---|")
    for lo_c, hi_c in [(0, 2000), (2000, 8000), (8000, 25000), (25000, 10 ** 9)]:
        sub = [r for r in rows if lo_c <= r["prior_chars"] < hi_c]
        label = f"{lo_c:,}–{hi_c:,} chars" if hi_c < 10 ** 8 else f"{lo_c:,}+ chars"
        rate_row(label, sub, out)
    out.append("")

    out.append("## By model\n")
    out.append("| model | handoffs | voice held | 95% CI |")
    out.append("|---|---:|---:|---|")
    for mdl, n in Counter(r["model"] for r in rows).most_common():
        if n < 40:
            continue
        rate_row(f"`{mdl}`", [r for r in rows if r["model"] == mdl], out)
    out.append("")

    out.append("## The names themselves\n")
    c = Counter(r["name"] for r in rows)
    out.append(f"{len(c):,} distinct names across {len(rows):,} handoffs. Most handed to:\n")
    out.append("| name | handoffs | voice held |")
    out.append("|---|---:|---:|")
    for name, n in c.most_common(12):
        sub = [r for r in rows if r["name"] == name]
        k = sum(1 for r in sub if r["held"])
        out.append(f"| `{name}` | {n} | {100 * k / len(sub):.0f}% |")
    out.append("")

    dest = args.report or (args.out_dir / "HANDOFF.md")
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
