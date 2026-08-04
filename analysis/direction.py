#!/usr/bin/env python3
"""Who is keeping the beat?

`FINDINGS.md` §1e finds short-memory length coupling: adjacent generations are
19.5% closer in word count than the same run scrambled, decaying to nothing by
lag 6. It could not say who produced it. Three candidates:

  * the **model** — it conditions on context, so a long preceding passage makes
    a long continuation likelier, with no human involvement at all;
  * the **author** — pacing the text-to-speech voice by rejecting generations
    that break the clip and keeping ones that hold it;
  * **both**, locked together, which is what the collaboration account predicts.

Two designs separate them.

**Selection test (the identifying one).** At a branch point the author generated,
rewound, and generated again from the *identical* document state. Kept and
rejected siblings are therefore draws from the same conditional distribution
under the same model and settings — the model's own autocorrelation applies
equally to both. So if the kept generation sits closer in length to the
preceding one than its rejected sibling does, more often than chance, that gap
is the author's selection and nothing else. Chance is 50%.

**Exposure test.** Runs in which the author never re-rolled involved no
selection at all, so their coupling is pure model. Compare against runs that
contain re-rolls.

Both are immune to `max_length` and model choice, which apply to kept and
rejected alike.

    python3 analysis/direction.py out --report analysis/DIRECTION.md
"""

import argparse
import json
import math
import pathlib
import random
import re
import statistics
from collections import Counter, defaultdict

TOKEN = re.compile(r"[A-Za-z][A-Za-z'-]*")
LAGS = (1, 2, 3, 4, 6)


def words(t):
    return len(TOKEN.findall(t or ""))


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


def wilson(k, n, z=1.96):
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def collect_branches(blocks_path, meta):
    """(preceding length, kept length, rejected length) at each re-roll."""
    rows = []
    for rid, blocks in stories_from_blocks(blocks_path):
        m = meta.get(rid)
        if not m:
            continue
        by_idx = {b["block_index"]: b for b in blocks}
        live = sorted((b for b in blocks if b.get("live")), key=lambda b: b["block_index"])
        pos = {b["block_index"]: i for i, b in enumerate(live)}

        for b in blocks:
            succ = [by_idx[i] for i in (b["next_blocks"] or []) if i in by_idx]
            if len(succ) < 2:
                continue
            ai = [s for s in succ if s["origin"] == "ai"]
            kept = [s for s in ai if s["live"]]
            dead = [s for s in ai if not s["live"]]
            if len(kept) != 1 or not dead:
                continue
            # Nearest preceding generation on the surviving branch.
            if b["block_index"] not in pos:
                continue
            prev_len = None
            for j in range(pos[b["block_index"]], -1, -1):
                if live[j]["origin"] == "ai":
                    prev_len = words(live[j]["text"])
                    break
            if not prev_len:
                continue
            k = words(kept[0]["text"])
            for d in dead:
                r = words(d["text"])
                if k >= 20 and r >= 20:
                    rows.append(
                        {
                            "model": m["model"],
                            "prev": prev_len,
                            "kept": k,
                            "rejected": r,
                            "kept_text": kept[0]["text"][:200],
                            "rejected_text": d["text"][:200],
                        }
                    )
    return rows


def dedupe(rows):
    seen, keep = set(), []
    for r in rows:
        k = (r["kept_text"], r["rejected_text"])
        if k in seen:
            continue
        seen.add(k)
        keep.append(r)
    return keep


def section_selection(rows, out):
    out.append("## Selection test — does the author pick for tempo?\n")
    out.append(
        "At each re-roll: is the **kept** generation closer in word count to the "
        "preceding generation than the **rejected** sibling is? Both were drawn "
        "from the identical document state under the same model and settings, so "
        "the model's own length autocorrelation applies equally to each. Chance "
        "is 50%. Ties excluded.\n"
    )
    usable = [r for r in rows if abs(r["kept"] - r["prev"]) != abs(r["rejected"] - r["prev"])]
    wins = sum(
        1 for r in usable if abs(r["kept"] - r["prev"]) < abs(r["rejected"] - r["prev"])
    )
    n = len(usable)
    lo, hi = wilson(wins, n)
    out.append("| comparison | pairs | kept is closer | 95% CI |")
    out.append("|---|---:|---:|---|")
    out.append(
        f"| all | {n:,} | **{100 * wins / n:.1f}%** | {100 * lo:.1f}–{100 * hi:.1f}% |"
    )
    for mdl, c in Counter(r["model"] for r in usable).most_common():
        if c < 300:
            continue
        sub = [r for r in usable if r["model"] == mdl]
        w = sum(1 for r in sub if abs(r["kept"] - r["prev"]) < abs(r["rejected"] - r["prev"]))
        l2, h2 = wilson(w, len(sub))
        out.append(
            f"| `{mdl}` | {len(sub):,} | {100 * w / len(sub):.1f}% | "
            f"{100 * l2:.1f}–{100 * h2:.1f}% |"
        )
    out.append("")

    md_k = statistics.median(abs(r["kept"] - r["prev"]) for r in rows)
    md_r = statistics.median(abs(r["rejected"] - r["prev"]) for r in rows)
    out.append(
        f"Median |Δ words| from the preceding generation: kept **{md_k:.0f}**, "
        f"rejected **{md_r:.0f}**.\n"
    )
    return wins / n if n else float("nan"), n


def section_direction_of_pull(rows, out):
    """If the author selects, is it for matching or simply for length?"""
    out.append("## Is it matching, or just a preference for longer?\n")
    out.append(
        "A simpler story than tempo-matching: the author rejects short "
        "generations because they leave dead air, with no reference to what "
        "came before. That predicts kept > rejected regardless of the preceding "
        "length. Tempo-matching predicts the pull is *toward* the previous "
        "length — so when the previous generation was short, the author should "
        "prefer the shorter sibling.\n"
    )
    out.append("| preceding generation | pairs | kept is longer | kept is closer |")
    out.append("|---|---:|---:|---:|")
    bands = [(0, 40), (40, 70), (70, 110), (110, 170), (170, 10 ** 6)]
    for lo, hi in bands:
        sub = [r for r in rows if lo <= r["prev"] < hi]
        if len(sub) < 200:
            continue
        longer = sum(1 for r in sub if r["kept"] > r["rejected"])
        closer_pool = [
            r for r in sub if abs(r["kept"] - r["prev"]) != abs(r["rejected"] - r["prev"])
        ]
        closer = sum(
            1 for r in closer_pool
            if abs(r["kept"] - r["prev"]) < abs(r["rejected"] - r["prev"])
        )
        label = f"{lo}–{hi} words" if hi < 10 ** 5 else f"{lo}+ words"
        out.append(
            f"| {label} | {len(sub):,} | {100 * longer / len(sub):.1f}% | "
            f"{100 * closer / len(closer_pool):.1f}% |"
        )
    out.append("")
    out.append(
        "If the middle column is flat near 50% while the right column stays "
        "above it across every band — including the bands where matching means "
        "choosing the *shorter* sibling — the pull is toward the previous "
        "length rather than toward length as such.\n"
    )


def section_exposure(blocks_path, meta, out, min_len=8, seed=21):
    """Runs with no re-rolls involved no selection: pure model coupling."""
    out.append("## Exposure test — coupling with and without selection\n")
    out.append(
        "A run in which the author never re-rolled contains no selection at all, "
        "so whatever coupling it shows is the model's alone. Same shuffle "
        "control as §1e.\n"
    )
    rng = random.Random(seed)
    obs = {"clean": defaultdict(list), "rerolled": defaultdict(list)}
    shuf = {"clean": defaultdict(list), "rerolled": defaultdict(list)}
    n_runs = Counter()

    for rid, blocks in stories_from_blocks(blocks_path):
        if rid not in meta:
            continue
        by_idx = {b["block_index"]: b for b in blocks}
        live = sorted((b for b in blocks if b.get("live")), key=lambda b: b["block_index"])
        run, runs = [], []
        for b in live:
            if b["origin"] == "ai":
                run.append(b)
            else:
                if len(run) >= min_len:
                    runs.append(run)
                run = []
        if len(run) >= min_len:
            runs.append(run)

        for r in runs:
            # Did any block in this run sit at a branch point with a dead AI sibling?
            rerolled = False
            for b in r:
                p = by_idx.get(b["prev_block"])
                if p and len(p.get("next_blocks") or []) > 1:
                    sibs = [by_idx[i] for i in p["next_blocks"] if i in by_idx]
                    if any(s["origin"] == "ai" and not s["live"] for s in sibs):
                        rerolled = True
                        break
            key = "rerolled" if rerolled else "clean"
            lens = [words(b["text"]) for b in r]
            lens = [x for x in lens if x >= 20]
            if len(lens) < min_len:
                continue
            n_runs[key] += 1
            s = lens[:]
            rng.shuffle(s)
            for lag in LAGS:
                for i in range(len(lens) - lag):
                    obs[key][lag].append(abs(lens[i] - lens[i + lag]))
                for i in range(len(s) - lag):
                    shuf[key][lag].append(abs(s[i] - s[i + lag]))

    out.append("| run type | runs | lag 1 reduction | lag 2 | lag 3 | lag 6 |")
    out.append("|---|---:|---:|---:|---:|---:|")
    for key, label in (("clean", "no re-rolls (model only)"), ("rerolled", "contains re-rolls")):
        if n_runs[key] < 50:
            continue
        cells = []
        for lag in (1, 2, 3, 6):
            o = obs[key][lag]
            s = shuf[key][lag]
            if not o:
                cells.append("-")
                continue
            om, sm = statistics.fmean(o), statistics.fmean(s)
            cells.append(f"{100 * (sm - om) / sm:.1f}%")
        out.append(f"| {label} | {n_runs[key]:,} | " + " | ".join(cells) + " |")
    out.append("")
    return n_runs


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

    blocks = args.out_dir / "blocks.jsonl"
    raw = collect_branches(blocks, meta)
    rows = dedupe(raw)

    out = ["# Who is keeping the beat?", "", "Generated by `analysis/direction.py`.", ""]
    out.append(
        f"**{len(raw):,}** re-roll comparisons, **{len(rows):,}** distinct after "
        "removing duplicated stories.\n"
    )
    section_selection(rows, out)
    section_direction_of_pull(rows, out)
    section_exposure(blocks, meta, out)

    dest = args.report or (args.out_dir / "DIRECTION.md")
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
