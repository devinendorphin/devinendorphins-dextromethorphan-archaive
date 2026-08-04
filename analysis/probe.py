#!/usr/bin/env python3
"""Disconfirming tests for the headline claims, plus text-level measures.

Run after extract.py. Reads stories.jsonl and blocks.jsonl.

The pooled rejection rate in TABLES.md is a ratio of sums, so a handful of huge
stories could produce it. Everything here re-checks a claim at the level it
would have to hold at, and reports the result even when it kills the claim.
"""

import argparse
import json
import math
import pathlib
import random
import re
import statistics
from collections import Counter, defaultdict

WORD = re.compile(r"[a-z']+")


def load_stories(p):
    return [json.loads(l) for l in p.open(encoding="utf-8")]


def spearman(xs, ys):
    """Rank correlation; robust to the wild scales in this data."""
    n = len(xs)
    if n < 3:
        return None

    def ranks(v):
        order = sorted(range(n), key=lambda i: v[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx, ry = ranks(xs), ranks(ys)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ry))
    return num / (dx * dy) if dx and dy else None


def summary(vals):
    vals = sorted(vals)
    if not vals:
        return None
    n = len(vals)
    g = lambda p: vals[min(n - 1, max(0, int(round(p * (n - 1)))))]
    return dict(n=n, p10=g(0.10), p25=g(0.25), median=g(0.5), p75=g(0.75), p90=g(0.90),
                mean=statistics.fmean(vals))


def test_removed_artifact(recs, out):
    """The first rejection metric I tried, and why it is wrong. Kept as a warning."""
    out.append("## Test A0 -- a metric that had to be thrown away\n")
    out.append(
        "The obvious rejection measure is `removedFragments` carrying "
        "`origin: ai` -- text a later block deleted that the model had written. "
        "Pooled it gives a striking ~44%, near-identical across every model from "
        "2021-era Euterpe to GLM-4.6. It is an artifact.\n"
    )
    vals = []
    for r in recs:
        gen = r["ai_chars"] + r["removed_ai_chars"]
        if gen >= 2000:
            vals.append(r["removed_ai_chars"] / gen)
    over = sum(1 for v in vals if v > 0.5)
    near = sum(1 for v in vals if 0.45 <= v <= 0.5)
    out.append(
        f"Across {len(vals)} stories the value never once exceeds 0.5 "
        f"(n>0.5: **{over}**), and **{100 * near / len(vals):.0f}%** of stories sit "
        "in the top sliver 0.45-0.50. A hard ceiling at exactly one half is a "
        "formula, not a behaviour.\n"
    )
    out.append(
        "The cause is visible in the block stream: NovelAI's editor implements a "
        "whole-document rewrite as *delete everything, re-insert everything*. The "
        "delete charges every prior AI character to `removedFragments`; the "
        "re-insert comes back stamped `origin: user`. So a story where the author "
        "merely pasted their text back in scores as ~50% 'rejected', and the "
        "measure saturates. It tracks the editor, not the author's judgement, "
        "which is why it looked identically flat across five years of models.\n"
    )
    out.append(
        "Everything below uses branch reachability instead: walk `prevBlock` back "
        "from `currentBlock` to get the surviving branch, and count AI text that "
        "is *not* on it. That is text the author generated and then rewound past.\n"
    )


def test_rejection_rate(recs, out):
    """Corrected claim: how much generated text did the author actually abandon?"""
    out.append("## Test A -- how much generated text was abandoned?\n")
    out.append(
        "Per story: AI characters on abandoned branches, over all AI characters "
        "generated. Stories with at least 2k generated characters.\n"
    )

    per_model = defaultdict(list)
    for r in recs:
        gen = r["live_ai_chars"] + r["abandoned_ai_chars"]
        if gen < 2000 or not r["model"]:
            continue  # too small for a stable ratio
        per_model[r["model"]].append(r["abandoned_ai_chars"] / gen)

    rows = []
    for m, vals in sorted(per_model.items(), key=lambda kv: -len(kv[1])):
        s = summary(vals)
        if s["n"] < 5:
            continue
        rows.append(
            f"| `{m}` | {s['n']} | {s['median']:.3f} | {s['mean']:.3f} | "
            f"{s['p90']:.3f} | {max(vals):.3f} |"
        )
    out.append("| model | stories | median | mean | p90 | max |")
    out.append("|---|---:|---:|---:|---:|---:|")
    out.extend(rows)
    out.append("")

    allv = [v for vs in per_model.values() for v in vs]
    s = summary(allv)
    zero = sum(1 for v in allv if v == 0)
    out.append(
        f"Across all {s['n']} stories: median **{s['median']:.3f}**, mean "
        f"**{s['mean']:.3f}**, p90 **{s['p90']:.3f}**, max **{max(allv):.3f}**. "
        f"**{100 * zero / s['n']:.0f}%** of stories abandoned nothing at all.\n"
    )
    out.append(
        "The distribution is unbounded above and heavily right-skewed -- the shape "
        "you expect from a real behaviour, and the one the discarded metric could "
        "not produce.\n"
    )
    return per_model


def test_temperature_vs_rejection(recs, out):
    """Obvious hypothesis: hotter sampling -> more rejected text."""
    out.append("## Test B -- does cranking temperature cost you more rejects?\n")
    pts = []
    for r in recs:
        gen = r["live_ai_chars"] + r["abandoned_ai_chars"]
        if gen < 2000 or r["temperature"] is None:
            continue
        pts.append((r["temperature"], r["abandoned_ai_chars"] / gen, r["model"]))

    rho = spearman([p[0] for p in pts], [p[1] for p in pts])
    out.append(
        f"All models pooled, n={len(pts)}: Spearman rho = **{rho:+.3f}** "
        "between temperature and per-story share of generated text deleted.\n"
    )

    out.append("Within model (pooling hides model-specific temperature habits):\n")
    out.append("| model | stories | rho | median temp | median reject |")
    out.append("|---|---:|---:|---:|---:|")
    for m in sorted({p[2] for p in pts}):
        sub = [p for p in pts if p[2] == m]
        if len(sub) < 30:
            continue
        r_ = spearman([p[0] for p in sub], [p[1] for p in sub])
        out.append(
            f"| `{m}` | {len(sub)} | {r_:+.3f} | "
            f"{statistics.median(p[0] for p in sub):.2f} | "
            f"{statistics.median(p[1] for p in sub):.3f} |"
        )
    out.append("")

    # Bucketed, so a monotone-but-weak effect is still visible.
    out.append("Pooled, bucketed by temperature:\n")
    out.append("| temperature | stories | median reject share |")
    out.append("|---|---:|---:|")
    buckets = [(0, 0.9), (0.9, 1.1), (1.1, 1.3), (1.3, 1.5), (1.5, 2.0), (2.0, 2.6), (2.6, 9)]
    for lo, hi in buckets:
        sub = [p[1] for p in pts if lo <= p[0] < hi]
        if len(sub) < 10:
            continue
        out.append(f"| {lo}-{hi} | {len(sub)} | {statistics.median(sub):.3f} |")
    out.append("")


def test_looping(blocks_path, recs, out, sample_per_model=400, seed=7):
    """Folk claim: older/smaller models degenerate into loops more often.

    Measured on accepted AI blocks only, as trigram self-repetition inside a
    single generation.
    """
    out.append("## Test C -- do older models loop more?\n")
    by_id = {r["remote_id"]: r for r in recs if r.get("remote_id")}

    rng = random.Random(seed)
    keep = defaultdict(list)
    for rid, r in by_id.items():
        if r["model"] and r["ai_chars"] > 0:
            keep[r["model"]].append(rid)
    wanted = set()
    for m, ids in keep.items():
        rng.shuffle(ids)
        wanted.update(ids[:sample_per_model])

    # Repetition grows with length mechanically, and the models were used at very
    # different block lengths (Erato ~944 chars/block vs Kayra ~469). Truncating
    # every generation to a fixed word window is what makes the columns comparable.
    WINDOW = 150
    stats = defaultdict(lambda: {"blocks": 0, "loopy": 0, "ttr": [], "rep": []})
    with blocks_path.open(encoding="utf-8") as fh:
        for line in fh:
            b = json.loads(line)
            if b["origin"] != "ai" or b["remote_id"] not in wanted:
                continue
            r = by_id[b["remote_id"]]
            words = WORD.findall(b["text"].lower())
            if len(words) < WINDOW:
                continue
            w = words[:WINDOW]
            tri = [tuple(w[i : i + 3]) for i in range(len(w) - 2)]
            dup = sum(v - 1 for v in Counter(tri).values())
            rep = dup / len(tri)
            s = stats[r["model"]]
            s["blocks"] += 1
            s["rep"].append(rep)
            s["ttr"].append(len(set(w)) / WINDOW)
            if rep > 0.10:
                s["loopy"] += 1

    out.append(
        "`trigram repeat` is the share of word-trigrams inside one generation that "
        "repeat an earlier trigram in the same generation; `looping` counts "
        "generations above 10%. Repetition rises with length mechanically and the "
        f"models were used at very different block lengths, so every generation is "
        f"truncated to its first {WINDOW} words. Sampled up to {sample_per_model} "
        "stories per model.\n"
    )
    out.append(
        "| model | blocks | median trigram repeat | p90 | looping rate | median TTR |"
    )
    out.append("|---|---:|---:|---:|---:|---:|")
    for m, s in sorted(stats.items(), key=lambda kv: -kv[1]["blocks"]):
        if s["blocks"] < 50:
            continue
        rep = sorted(s["rep"])
        p90 = rep[min(len(rep) - 1, int(round(0.9 * (len(rep) - 1))))]
        out.append(
            f"| `{m}` | {s['blocks']:,} | {statistics.median(rep):.3f} | {p90:.3f} | "
            f"{100 * s['loopy'] / s['blocks']:.1f}% | {statistics.median(s['ttr']):.3f} |"
        )
    out.append("")
    return stats


def test_looping_within_model(blocks_path, recs, out, seed=13):
    """Test C says the newest models loop most -- but model and temperature are
    entangled in how they were used. Kayra alone spans temp 0.1-2.5, so it can
    separate the two.
    """
    out.append("## Test C2 -- looping vs temperature, inside one model\n")
    by_id = {
        r["remote_id"]: r
        for r in recs
        if r.get("remote_id")
        and r["model"] == "kayra-v1"
        and r["temperature"] is not None
        and r["ai_chars"] > 0
    }
    rng = random.Random(seed)
    ids = sorted(by_id)
    if len(ids) > 900:
        ids = rng.sample(ids, 900)
    wanted = set(ids)

    WINDOW = 150
    bands = [(0, 1.1), (1.1, 1.4), (1.4, 1.7), (1.7, 2.2), (2.2, 9)]
    acc = defaultdict(lambda: {"n": 0, "loopy": 0, "rep": []})
    with blocks_path.open(encoding="utf-8") as fh:
        for line in fh:
            b = json.loads(line)
            if b["origin"] != "ai" or b["remote_id"] not in wanted:
                continue
            words = WORD.findall(b["text"].lower())
            if len(words) < WINDOW:
                continue
            w = words[:WINDOW]
            tri = [tuple(w[i : i + 3]) for i in range(len(w) - 2)]
            rep = sum(v - 1 for v in Counter(tri).values()) / len(tri)
            t = by_id[b["remote_id"]]["temperature"]
            for lo, hi in bands:
                if lo <= t < hi:
                    s = acc[(lo, hi)]
                    s["n"] += 1
                    s["rep"].append(rep)
                    if rep > 0.10:
                        s["loopy"] += 1
                    break

    out.append(
        "`kayra-v1` only, generations truncated to 150 words, same measure as "
        "Test C.\n"
    )
    out.append("| temperature | generations | median trigram repeat | p90 | looping rate |")
    out.append("|---|---:|---:|---:|---:|")
    for lo, hi in bands:
        s = acc.get((lo, hi))
        if not s or s["n"] < 100:
            continue
        rep = sorted(s["rep"])
        p90 = rep[min(len(rep) - 1, int(round(0.9 * (len(rep) - 1))))]
        out.append(
            f"| {lo}-{hi} | {s['n']:,} | {statistics.median(rep):.3f} | {p90:.3f} | "
            f"{100 * s['loopy'] / s['n']:.1f}% |"
        )
    out.append("")


def test_diversity_matched(blocks_path, recs, out, seed=11):
    """Lexical diversity by model is confounded by temperature. Match on it."""
    out.append("## Test D -- lexical diversity at matched temperature\n")
    by_id = {r["remote_id"]: r for r in recs if r.get("remote_id")}
    band = defaultdict(list)  # (model, temp band) -> ttr values

    rng = random.Random(seed)
    wanted = {
        rid
        for rid, r in by_id.items()
        if r["model"] and r["ai_chars"] > 0 and r["temperature"] is not None
    }
    if len(wanted) > 1400:
        wanted = set(rng.sample(sorted(wanted), 1400))

    def tband(t):
        if t < 1.15:
            return "~1.0"
        if t < 1.6:
            return "~1.4"
        if t < 2.2:
            return "~1.8"
        return ">=2.2"

    with blocks_path.open(encoding="utf-8") as fh:
        for line in fh:
            b = json.loads(line)
            if b["origin"] != "ai" or b["remote_id"] not in wanted:
                continue
            words = WORD.findall(b["text"].lower())
            if len(words) < 120:
                continue
            w = words[:120]  # fixed window: TTR is length-sensitive
            r = by_id[b["remote_id"]]
            band[(r["model"], tband(r["temperature"]))].append(len(set(w)) / 120)

    models = sorted({k[0] for k in band})
    bands = ["~1.0", "~1.4", "~1.8", ">=2.2"]
    out.append(
        "Type-token ratio over a fixed 120-word window of each accepted "
        "generation. Cells are `median (n)`; blank where n < 40.\n"
    )
    out.append("| model | " + " | ".join(bands) + " |")
    out.append("|---|" + "|".join(["---:"] * len(bands)) + "|")
    for m in models:
        cells = []
        for tb in bands:
            v = band.get((m, tb), [])
            cells.append(f"{statistics.median(v):.3f} ({len(v)})" if len(v) >= 40 else "")
        if any(cells):
            out.append(f"| `{m}` | " + " | ".join(cells) + " |")
    out.append("")


def test_session_shape(recs, out):
    """How long are these sessions, and did that change as models improved?"""
    out.append("## Test E -- session shape over time\n")
    out.append("| model | median AI blocks/story | median chars/AI block | median story AI chars |")
    out.append("|---|---:|---:|---:|")
    for m, _ in Counter(r["model"] for r in recs if r["ai_chars"] > 0).most_common():
        sub = [r for r in recs if r["model"] == m and r["ai_chars"] > 0]
        if len(sub) < 20:
            continue
        nb = [r["blocks_by_origin"].get("ai", 0) for r in sub]
        cpb = [
            r["ai_chars"] / r["blocks_by_origin"]["ai"]
            for r in sub
            if r["blocks_by_origin"].get("ai")
        ]
        out.append(
            f"| `{m}` | {statistics.median(nb):.0f} | {statistics.median(cpb):.0f} | "
            f"{statistics.median(r['ai_chars'] for r in sub):,.0f} |"
        )
    out.append("")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir", type=pathlib.Path)
    ap.add_argument("--report", type=pathlib.Path, default=None)
    args = ap.parse_args()

    recs = load_stories(args.out_dir / "stories.jsonl")
    blocks = args.out_dir / "blocks.jsonl"
    out = ["# Probes", "", "Generated by `analysis/probe.py`.", ""]

    test_removed_artifact(recs, out)
    test_rejection_rate(recs, out)
    test_temperature_vs_rejection(recs, out)
    test_session_shape(recs, out)
    if blocks.exists():
        test_looping(blocks, recs, out)
        test_looping_within_model(blocks, recs, out)
        test_diversity_matched(blocks, recs, out)
    else:
        out.append("_blocks.jsonl absent; text-level probes skipped._\n")

    dest = args.report or (args.out_dir / "PROBES.md")
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
