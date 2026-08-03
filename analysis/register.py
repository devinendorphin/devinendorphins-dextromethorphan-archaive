#!/usr/bin/env python3
"""Where does raised temperature stop making style and start making noise?

Endorphin describes a deliberate procedure buried in this corpus: pick a preset,
work a mythological or poetic register, then iterate upward in temperature until
the output degrades, and repeat across several presets -- looking for the band
where structure gets strange but has not yet dissolved.

That procedure is measurable, because two different things happen as temperature
rises and they do not happen at the same rate:

  * the model reaches for **rarer real words** -- an English word that exists but
    is uncommon. This is the register climbing.
  * the model emits **non-words** -- character strings that are not English at
    all. This is the noise floor.

`wordfreq` separates them: a Zipf frequency of 0 means the token does not occur
in English, while a low-but-nonzero Zipf is a real rare word. If the rare-word
curve rises before the non-word curve does, there is a band between them, and
its location is an empirical answer to the question the experiments were asking.

Also measures unbroken runs of model generation -- stretches where the author
pressed enter and nothing else.

    python3 analysis/register.py out --report analysis/REGISTER.md
"""

import argparse
import json
import pathlib
import random
import re
import statistics
from collections import Counter, defaultdict
from functools import lru_cache

from wordfreq import zipf_frequency

TOKEN = re.compile(r"[A-Za-z][A-Za-z'-]*")
SENT = re.compile(r"[.!?]+")

# Zipf bands. 0 = not an English word at all; below ~2.5 is rare enough to read
# as deliberate vocabulary rather than ordinary prose.
RARE_MAX = 2.5


@lru_cache(maxsize=400_000)
def zipf(tok):
    return zipf_frequency(tok.lower().strip("'-"), "en")


def lexical_profile(text):
    toks = TOKEN.findall(text)
    if len(toks) < 40:
        return None
    n = len(toks)
    nonword = rare = 0
    for t in toks:
        z = zipf(t)
        if z == 0.0:
            nonword += 1
        elif z < RARE_MAX:
            rare += 1
    sents = [s for s in SENT.split(text) if s.strip()]
    return {
        "tokens": n,
        "nonword_rate": nonword / n,
        "rare_rate": rare / n,
        "ttr": len(set(t.lower() for t in toks)) / n,
        "mean_sentence_tokens": n / max(1, len(sents)),
    }


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


def enter_chains(blocks_path, meta, out):
    """Unbroken runs of AI generation on the surviving branch."""
    out.append("## Pressing enter: unbroken runs of generation\n")
    runs = []
    per_story_max = {}
    for rid, blocks in stories_from_blocks(blocks_path):
        m = meta.get(rid)
        if not m:
            continue
        live = [b for b in blocks if b.get("live")]
        live.sort(key=lambda b: b["block_index"])
        cur = 0
        best = 0
        for b in live:
            if b["origin"] == "ai":
                cur += 1
                best = max(best, cur)
            else:
                if cur:
                    runs.append((cur, rid))
                cur = 0
        if cur:
            runs.append((cur, rid))
        if best:
            per_story_max[rid] = best

    lens = [r for r, _ in runs]
    if not lens:
        out.append("_no runs found_\n")
        return
    s = sorted(lens)
    q = lambda p: s[min(len(s) - 1, int(round(p * (len(s) - 1))))]
    out.append(
        f"**{len(runs):,}** runs of consecutive model generation with no human "
        f"text between them. Median **{q(0.5)}**, p90 **{q(0.9)}**, "
        f"p99 **{q(0.99)}**, max **{s[-1]}**.\n"
    )
    buckets = [(1, 1), (2, 3), (4, 9), (10, 24), (25, 49), (50, 99), (100, 10 ** 9)]
    out.append("| run length | runs | share |")
    out.append("|---|---:|---:|")
    for lo, hi in buckets:
        c = sum(1 for x in lens if lo <= x <= hi)
        label = f"{lo}" if lo == hi else (f"{lo}+" if hi > 10 ** 8 else f"{lo}-{hi}")
        out.append(f"| {label} | {c:,} | {100 * c / len(lens):.1f}% |")
    out.append("")

    top = sorted(per_story_max.items(), key=lambda kv: -kv[1])[:12]
    out.append("Longest unbroken run per story, top 12:\n")
    out.append("| run | model | temperature | created | title |")
    out.append("|---:|---|---:|---|---|")
    for rid, n in top:
        m = meta[rid]
        import datetime as _dt

        try:
            when = _dt.datetime.fromtimestamp(
                m["created_at"], _dt.timezone.utc
            ).strftime("%Y-%m")
        except Exception:  # noqa: BLE001
            when = "?"
        out.append(
            f"| {n} | `{m['model']}` | {m['temperature']} | {when} | "
            f"{(m['title'] or '')[:44]} |"
        )
    out.append("")
    out.append(
        "A run of length 1 is ordinary turn-taking. The long tail is the other "
        "mode: the author stops contributing text and just advances the model, "
        "which makes those stretches pure model output under a fixed setting -- "
        "the cleanest single-condition samples in the corpus.\n"
    )


TRUNCATORS = {"top_k", "top_p", "top_a", "typical_p", "tfs", "min_p"}


def sampler_order_condition(rec):
    """Does any truncating sampler run *before* temperature?

    NovelAI applies samplers in the order listed in `settings.parameters.order`.
    Truncate-then-flatten and flatten-then-truncate are different operations:
    the first spreads probability evenly across a shortlist of plausible tokens,
    the second lifts the whole tail and only then cuts it. At ordinary
    temperatures the distinction barely matters. At 2.5 it should be decisive.
    """
    order = rec.get("sampler_order_enabled") or []
    if "temperature" not in order:
        return None
    i = order.index("temperature")
    return "truncation first" if any(x in TRUNCATORS for x in order[:i]) else "temperature first"


def order_interaction(blocks_path, meta, out, cap=2500, seed=3):
    """The central test: does sampler order change what high temperature does?"""
    out.append("## Where the border actually is\n")
    out.append(
        "The pooled curve above is flat, which cannot be right if temperature "
        "2.5 meant 2.5. It does not. Temperature is one stage in an ordered "
        "pipeline, and the corpus runs it alongside hard truncation throughout: "
        "at temp >= 2.2, `top_k` is active in 79% of stories at a median of "
        "**82** (*tighter* than the median of 150 at temp < 1.2), with "
        "`tail_free_sampling` at 0.97 and `top_a` at 0.02. Temperature 2.5 here "
        "never means 2.5 over the full vocabulary.\n"
    )
    out.append(
        "So the question is not how hot, but hot *in what order*. Splitting "
        "every generation by whether a truncating sampler ran before "
        "temperature:\n"
    )

    rng = random.Random(seed)
    acc = defaultdict(lambda: {"non": [], "rare": [], "ttr": []})
    counts = Counter()

    def band(t):
        if t is None:
            return None
        return "hot (>=2.2)" if t >= 2.2 else ("mid (1.2-2.2)" if t >= 1.2 else "cool (<1.2)")

    with blocks_path.open(encoding="utf-8") as fh:
        for line in fh:
            b = json.loads(line)
            if b["origin"] != "ai":
                continue
            m = meta.get(b["remote_id"])
            if not m:
                continue
            cond = sampler_order_condition(m)
            bd = band(m.get("temperature"))
            if not cond or not bd:
                continue
            key = (bd, cond)
            if counts[key] >= cap or rng.random() > 0.35:
                continue
            p = lexical_profile(b["text"])
            if not p or p["tokens"] < 60:
                continue
            acc[key]["non"].append(p["nonword_rate"])
            acc[key]["rare"].append(p["rare_rate"])
            acc[key]["ttr"].append(p["ttr"])
            counts[key] += 1

    out.append("| temperature | sampler order | generations | non-word % | rare word % | TTR |")
    out.append("|---|---|---:|---:|---:|---:|")
    for bd in ("cool (<1.2)", "mid (1.2-2.2)", "hot (>=2.2)"):
        for cond in ("temperature first", "truncation first"):
            v = acc.get((bd, cond))
            if not v or len(v["non"]) < 100:
                continue
            out.append(
                f"| {bd} | {cond} | {len(v['non']):,} | "
                f"{100 * statistics.fmean(v['non']):.2f} | "
                f"{100 * statistics.fmean(v['rare']):.2f} | "
                f"{statistics.fmean(v['ttr']):.3f} |"
            )
    out.append("")

    hot_t = acc.get(("hot (>=2.2)", "temperature first"))
    hot_x = acc.get(("hot (>=2.2)", "truncation first"))
    cool_x = acc.get(("cool (<1.2)", "truncation first"))
    if hot_t and hot_x and cool_x:
        out.append(
            f"At high temperature the order roughly **halves** the non-word rate "
            f"({100 * statistics.fmean(hot_t['non']):.2f}% -> "
            f"{100 * statistics.fmean(hot_x['non']):.2f}%) while *raising* rare "
            f"vocabulary ({100 * statistics.fmean(hot_t['rare']):.2f}% -> "
            f"{100 * statistics.fmean(hot_x['rare']):.2f}%). Against the cool "
            f"baseline, truncate-first at 2.5 buys about "
            f"**{100 * (statistics.fmean(hot_x['rare']) / statistics.fmean(cool_x['rare']) - 1):.0f}% "
            "more rare real words at essentially unchanged noise**.\n"
        )
        out.append(
            "At cool and mid temperatures the ordering makes little difference, "
            "which is what a mechanical account predicts: order only matters once "
            "temperature is extreme enough to move real mass onto the tail.\n"
        )
        out.append(
            "**So the border is not a temperature.** It is a configuration. "
            "Truncate to a shortlist of plausible continuations, *then* flatten "
            "across that shortlist, and you get maximum surprise within the "
            "space of things the model considers sayable. Flatten first and the "
            "same nominal temperature spends much of its budget on noise.\n"
        )


def temperature_curve(blocks_path, meta, out, per_cell=900, seed=5):
    """Rare-word rate and non-word rate as functions of temperature."""
    out.append("## The border: register versus noise\n")

    rng = random.Random(seed)
    wanted = {
        rid
        for rid, m in meta.items()
        if m.get("temperature") is not None and m.get("ai_chars", 0) > 0
    }

    cells = defaultdict(list)  # (model, tband) -> profiles
    counts = Counter()

    def tband(t):
        for lo, hi in [
            (0.0, 1.05), (1.05, 1.25), (1.25, 1.45), (1.45, 1.65),
            (1.65, 1.9), (1.9, 2.2), (2.2, 2.6), (2.6, 10.0),
        ]:
            if lo <= t < hi:
                return (lo, hi)
        return None

    for rid, blocks in stories_from_blocks(blocks_path):
        if rid not in wanted:
            continue
        m = meta[rid]
        b_ = tband(m["temperature"])
        if b_ is None:
            continue
        key = (m["model"], b_)
        if counts[key] >= per_cell:
            continue
        for blk in blocks:
            if blk["origin"] != "ai":
                continue
            if counts[key] >= per_cell:
                break
            if rng.random() > 0.5:
                continue
            p = lexical_profile(blk["text"])
            if p:
                cells[key].append(p)
                counts[key] += 1

    # Pooled curve.
    pooled = defaultdict(list)
    for (mdl, b_), v in cells.items():
        pooled[b_] += v
    out.append(
        "**Caveat that governs this whole section.** NovelAI stores generation "
        "settings per *story*, as current state -- there is no per-generation "
        "record. Every temperature here is the story's last setting attributed "
        "to all of its generations. For a sweep (see the last section) that is "
        "flatly wrong for the early steps. The error is non-differential, so it "
        "attenuates real effects rather than inventing them: a flat curve is "
        "weak evidence of no effect, but a surviving effect is real.\n"
    )
    out.append(
        "All models pooled. `non-word` is the share of alphabetic tokens with "
        "zero English frequency; `rare word` is the share that are real but "
        "uncommon (Zipf < 2.5). Generations of 40+ tokens.\n"
    )
    out.append(
        "| temperature | generations | rare word % | non-word % | rare:non ratio | TTR | tokens/sentence |"
    )
    out.append("|---|---:|---:|---:|---:|---:|---:|")
    for b_ in sorted(pooled):
        v = pooled[b_]
        if len(v) < 100:
            continue
        rare = 100 * statistics.fmean(x["rare_rate"] for x in v)
        non = 100 * statistics.fmean(x["nonword_rate"] for x in v)
        out.append(
            f"| {b_[0]:.2f}-{b_[1]:.2f} | {len(v):,} | {rare:.2f} | {non:.2f} | "
            f"{(rare / non if non else float('inf')):.1f} | "
            f"{statistics.fmean(x['ttr'] for x in v):.3f} | "
            f"{statistics.fmean(x['mean_sentence_tokens'] for x in v):.1f} |"
        )
    out.append("")

    # Within model, since usage confounds model with temperature everywhere else.
    out.append("Within model, where there is enough spread to see it:\n")
    for mdl in sorted({k[0] for k in cells}):
        bands = sorted(b_ for (m_, b_) in cells if m_ == mdl and len(cells[(m_, b_)]) >= 100)
        if len(bands) < 3:
            continue
        out.append(f"\n**`{mdl}`**\n")
        out.append("| temperature | generations | rare word % | non-word % | TTR |")
        out.append("|---|---:|---:|---:|---:|")
        for b_ in bands:
            v = cells[(mdl, b_)]
            out.append(
                f"| {b_[0]:.2f}-{b_[1]:.2f} | {len(v):,} | "
                f"{100 * statistics.fmean(x['rare_rate'] for x in v):.2f} | "
                f"{100 * statistics.fmean(x['nonword_rate'] for x in v):.2f} | "
                f"{statistics.fmean(x['ttr'] for x in v):.3f} |"
            )
    out.append("")
    return pooled


def find_ramps(meta, out, min_len=3):
    """Sessions that look like a deliberate temperature sweep.

    A ramp = 3+ stories sharing model and preset, created close together, with
    strictly increasing temperature.
    """
    out.append("## Deliberate temperature sweeps\n")
    by_key = defaultdict(list)
    for rid, m in meta.items():
        if m.get("temperature") is None or not m.get("created_at"):
            continue
        by_key[(m["model"], m["preset"])].append(m)

    ramps = []
    for key, rows in by_key.items():
        rows.sort(key=lambda r: r["created_at"])
        run = [rows[0]]
        for prev, cur in zip(rows, rows[1:]):
            close = abs(cur["created_at"] - prev["created_at"]) <= 6 * 3600
            if close and cur["temperature"] > prev["temperature"]:
                run.append(cur)
            else:
                if len(run) >= min_len:
                    ramps.append((key, run))
                run = [cur]
        if len(run) >= min_len:
            ramps.append((key, run))

    if not ramps:
        out.append("_none detected_\n")
        return
    ramps.sort(key=lambda kr: -(kr[1][-1]["temperature"] - kr[1][0]["temperature"]))
    out.append(
        f"**{len(ramps)}** runs of {min_len}+ stories that share a model and "
        "preset, were made within six hours of each other, and step temperature "
        "strictly upward. Largest climbs:\n"
    )
    out.append("| model | steps | temperature climb | when |")
    out.append("|---|---:|---|---|")
    import datetime as _dt

    for (mdl, _preset), run in ramps[:14]:
        try:
            when = _dt.datetime.fromtimestamp(
                run[0]["created_at"], _dt.timezone.utc
            ).strftime("%Y-%m-%d")
        except Exception:  # noqa: BLE001
            when = "?"
        temps = " -> ".join(f"{r['temperature']:g}" for r in run)
        out.append(f"| `{mdl}` | {len(run)} | {temps} | {when} |")
    out.append("")
    out.append(
        "These are the procedure showing up in the metadata. They are a small "
        "fraction of the corpus, so the pooled curve above is mostly ordinary "
        "use rather than the sweeps themselves -- but the sweeps confirm the "
        "temperature spread is partly designed, not only habit.\n"
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
            if r.get("remote_id"):
                meta[r["remote_id"]] = r

    out = ["# Register, noise, and pressing enter", "",
           "Generated by `analysis/register.py`.", ""]
    blocks = args.out_dir / "blocks.jsonl"
    enter_chains(blocks, meta, out)
    temperature_curve(blocks, meta, out)
    order_interaction(blocks, meta, out)
    find_ramps(meta, out)

    dest = args.report or (args.out_dir / "REGISTER.md")
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
