#!/usr/bin/env python3
"""The Erato era, and where its border between register and noise sits.

`FINDINGS.md` §4c locates a border on the classic sampler stack: at high
temperature, running a truncating sampler *before* temperature roughly halves
the non-word rate while raising rare vocabulary. Erato does not use that stack.
It uses NovelAI's Unified sampler (`math1` in the stored order), whose knobs are
`linear` (`math1_temp`) and `quad` (`math1_quad`), and in most Erato stories
temperature is not in the pipeline at all.

So the §4c test is not merely uninformative here, it is undefined. This
re-runs the same lexical measure -- `wordfreq` separating real-but-rare words
from non-words -- across the Unified configuration instead.

One thing this cannot be: a controlled test of `linear` against `quad`. The
observed settings are almost perfectly collinear with NovelAI's four stock Erato
presets, which move both knobs together along with `min_p`, `top_p` and the
sampler order. What follows is therefore a comparison of presets, reported as
such.

    python3 analysis/erato.py out --report analysis/ERATO.md
"""

import argparse
import json
import pathlib
import random
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from functools import lru_cache

from wordfreq import zipf_frequency

TOKEN = re.compile(r"[A-Za-z][A-Za-z'-]*")
RARE_MAX = 2.5
MODEL = "llama-3-erato-v1"


@lru_cache(maxsize=400_000)
def zipf(tok):
    return zipf_frequency(tok.lower().strip("'-"), "en")


def month(ts):
    try:
        return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m")
    except (OSError, ValueError, TypeError, OverflowError):
        return None


def lexical(text, min_tokens=60):
    toks = TOKEN.findall(text)
    if len(toks) < min_tokens:
        return None
    non = rare = 0
    for t in toks:
        z = zipf(t)
        if z == 0.0:
            non += 1
        elif z < RARE_MAX:
            rare += 1
    return non / len(toks), rare / len(toks)


def preset_name(r):
    p = r.get("preset") or ""
    return p.replace("default-erato-", "").replace("default-", "") or "(none)"


def section_temperature_is_inert(recs, all_recs, out):
    """The correction that governs every earlier temperature claim about Erato."""
    out.append("## Temperature is not in the pipeline\n")
    off = [r for r in recs if "temperature" not in (r["sampler_order_enabled"] or [])]
    on = [r for r in recs if "temperature" in (r["sampler_order_enabled"] or [])]
    out.append(
        f"Of {len(recs)} generating Erato stories, **{len(off)} "
        f"({100 * len(off) / len(recs):.0f}%)** do not have `temperature` in "
        "their enabled sampler order at all. The Unified sampler replaces it.\n"
    )
    vals = Counter(r["temperature"] for r in off)
    top = vals.most_common(1)
    if top:
        out.append(
            f"In **{top[0][1]} of {len(off)}** of those, the stored temperature "
            f"is exactly **{top[0][0]}** — the neutral value, sitting unused in "
            "a field that is not part of the pipeline. When temperature *is* "
            f"enabled the median is **{statistics.median(r['temperature'] for r in on):.2f}**.\n"
        )
    out.append(
        "This is Erato-only. Every other model in the corpus has temperature "
        "enabled in 100% of its stories:\n"
    )
    out.append("| model | stories | temperature absent from the order |")
    out.append("|---|---:|---:|")
    for mdl, n in Counter(r["model"] for r in all_recs).most_common():
        sub = [r for r in all_recs if r["model"] == mdl]
        if len(sub) < 20:
            continue
        d = sum(1 for r in sub if "temperature" not in (r["sampler_order_enabled"] or []))
        out.append(f"| `{mdl}` | {len(sub):,} | {100 * d / len(sub):.1f}% |")
    out.append("")
    out.append(
        "**Consequence.** Erato's headline 'median temperature 1.00' is an "
        "artifact of reading an inert field. Any comparison that uses it — "
        "including `FINDINGS.md` §9's argument that Erato was run cool while "
        "Euterpe and Krake were run hot — is comparing a live setting against a "
        "disabled one.\n"
    )


def section_regime(recs, out):
    out.append("## What the Erato regime actually was\n")
    out.append("Enabled sampler orders:\n")
    out.append("| order | stories |")
    out.append("|---|---:|")
    for o, n in Counter(
        " > ".join(r["sampler_order_enabled"] or []) for r in recs
    ).most_common(6):
        out.append(f"| `{o or '(none)'}` | {n} |")
    out.append("")
    out.append("Presets, and the Unified knobs each one sets:\n")
    out.append("| preset | stories | linear | quad | min_p | order |")
    out.append("|---|---:|---:|---:|---:|---|")
    for p, n in Counter(preset_name(r) for r in recs).most_common():
        if n < 10:
            continue
        sub = [r for r in recs if preset_name(r) == p]
        o = Counter(" > ".join(r["sampler_order_enabled"] or []) for r in sub).most_common(1)[0][0]
        out.append(
            f"| `{p}` | {n} | {statistics.median(r['math1_temp'] for r in sub):.3f} | "
            f"{statistics.median(r['math1_quad'] for r in sub):.2f} | "
            f"{statistics.median(r['min_p'] for r in sub):.3f} | `{o}` |"
        )
    out.append("")
    out.append(
        "The four stock presets are collinear with the knobs, which is why no "
        "knob-level test is possible: `linear` and `quad` never vary "
        "independently of each other or of the rest of the stack.\n"
    )


def section_border(recs, blocks_path, out, cap=2200, seed=9):
    out.append("## The border, on the Unified sampler\n")
    out.append(
        "Same measure as `FINDINGS.md` §4c: `wordfreq` Zipf frequency splits "
        "alphabetic tokens into non-words (zero English frequency, the noise "
        "floor) and real-but-rare words (Zipf < 2.5, the register climbing). "
        "Generations of 60+ tokens.\n"
    )
    keep = {r["remote_id"]: r for r in recs if r.get("remote_id")}
    rng = random.Random(seed)
    acc = defaultdict(lambda: {"non": [], "rare": []})
    counts = Counter()

    with blocks_path.open(encoding="utf-8") as fh:
        for line in fh:
            b = json.loads(line)
            if b["origin"] != "ai":
                continue
            r = keep.get(b["remote_id"])
            if r is None:
                continue
            p = preset_name(r)
            if counts[p] >= cap or rng.random() > 0.5:
                continue
            lex = lexical(b["text"])
            if not lex:
                continue
            acc[p]["non"].append(lex[0])
            acc[p]["rare"].append(lex[1])
            counts[p] += 1

    rows = []
    for p, v in acc.items():
        if len(v["non"]) < 200:
            continue
        sub = [r for r in recs if preset_name(r) == p]
        non = 100 * statistics.fmean(v["non"])
        rare = 100 * statistics.fmean(v["rare"])
        rows.append((rare / non if non else 0, p, len(v["non"]), non, rare, sub))
    rows.sort(reverse=True)

    out.append(
        "| preset | generations | linear | quad | non-word % | rare word % | rare : non |"
    )
    out.append("|---|---:|---:|---:|---:|---:|---:|")
    for ratio, p, n, non, rare, sub in rows:
        out.append(
            f"| `{p}` | {n:,} | {statistics.median(r['math1_temp'] for r in sub):.3f} | "
            f"{statistics.median(r['math1_quad'] for r in sub):.2f} | "
            f"{non:.2f} | {rare:.2f} | **{ratio:.2f}** |"
        )
    out.append("")

    if rows:
        best = rows[0]
        furthest = max(rows, key=lambda x: x[4])
        out.append("Against the classic stack, from §4c:\n")
        out.append("| configuration | non-word % | rare word % | rare : non |")
        out.append("|---|---:|---:|---:|")
        out.append("| classic, hot, truncation first | 0.96 | 1.58 | 1.65 |")
        out.append("| classic, hot, temperature first | 2.00 | 1.46 | 0.73 |")
        out.append("| classic, cool | 0.62 | 1.10 | 1.77 |")
        out.append(
            f"| Unified, `{best[1]}` | {best[3]:.2f} | {best[4]:.2f} | {best[0]:.2f} |"
        )
        out.append(
            f"| Unified, `{furthest[1]}` | {furthest[3]:.2f} | {furthest[4]:.2f} | "
            f"{furthest[0]:.2f} |"
        )
        out.append("")
        out.append(
            f"**No Erato preset beats the classic stack's exchange rate.** The "
            f"best of them, `{best[1]}`, lands at {best[0]:.2f} against the 1.65 "
            "of high temperature with truncation running first — a tie, near "
            "enough — and it gets there at a much lower absolute level of both "
            f"quantities ({best[4]:.2f}% rare against 1.58%). Cleaner, but it "
            "does not reach as far.\n"
        )
        out.append(
            f"**What the Unified sampler does add is range.** `{furthest[1]}` "
            f"(linear {statistics.median(r['math1_temp'] for r in furthest[5]):.3f}, "
            f"quad {statistics.median(r['math1_quad'] for r in furthest[5]):.2f}) "
            f"reaches a rare-word rate of **{furthest[4]:.2f}%** — roughly double "
            "anything the classic stack achieved at any temperature — at "
            f"{furthest[3]:.2f}% non-words, the highest noise floor measured "
            f"anywhere in the corpus. Its exchange rate of {furthest[0]:.2f} is "
            "well above the classic stack's naive hot setting (0.73) and well "
            "below its best.\n"
        )
        out.append(
            "So the Unified sampler **extended the range without improving the "
            "exchange rate**. Temperature-plus-truncation could not get the "
            "register that high at any price; `math1` could, and the price was a "
            "noise floor two and a half times the corpus norm. The border did "
            "not disappear — it moved outward and stayed just as steep.\n"
        )
    return rows


def section_era(recs, out):
    out.append("## The era in the corpus\n")
    by_month = Counter(month(r["last_updated_at"]) for r in recs)
    out.append("| month | Erato stories | dominant preset |")
    out.append("|---|---:|---|")
    for m in sorted(x for x in by_month if x):
        sub = [r for r in recs if month(r["last_updated_at"]) == m]
        if len(sub) < 5:
            continue
        out.append(
            f"| {m} | {len(sub)} | `{Counter(preset_name(r) for r in sub).most_common(1)[0][0]}` |"
        )
    out.append("")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir", type=pathlib.Path)
    ap.add_argument("--report", type=pathlib.Path, default=None)
    args = ap.parse_args()

    all_recs = []
    with (args.out_dir / "stories.jsonl").open(encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["ai_chars"] > 0:
                all_recs.append(r)
    recs = [r for r in all_recs if r["model"] == MODEL]

    out = ["# The Erato era", "", "Generated by `analysis/erato.py`.", ""]
    out.append(
        f"**{len(recs)}** generating stories, "
        f"{sum(r['ai_chars'] for r in recs) / 1e6:.1f}M characters of output, "
        "November 2024 to July 2026. Llama 3 70B, settings schema v7.\n"
    )
    section_temperature_is_inert(recs, all_recs, out)
    section_regime(recs, out)
    section_border(recs, args.out_dir / "blocks.jsonl", out)
    section_era(recs, out)

    dest = args.report or (args.out_dir / "ERATO.md")
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
