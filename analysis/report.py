#!/usr/bin/env python3
"""Aggregate stories.jsonl into the tables that back FINDINGS.md.

Everything here is descriptive. Where a number could be read as a claim about
the models rather than about this author's use of them, the table is labelled
accordingly -- this corpus is one person's practice, not a sample of anything.
"""

import argparse
import json
import math
import pathlib
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone

# NovelAI model -> (base architecture, params, first available) for orientation.
MODEL_NOTES = {
    "2.7B": ("GPT-Neo 2.7B (Calliope)", "2.7B", "2021-06"),
    "6B-v4": ("GPT-J 6B (Sigurd)", "6B", "2021-10"),
    "euterpe-v2": ("Fairseq 13B (Euterpe)", "13B", "2022-06"),
    "krake-v2": ("GPT-NeoX 20B (Krake)", "20B", "2022-08"),
    "clio-v1": ("NovelAI in-house (Clio)", "3B", "2023-05"),
    "kayra-v1": ("NovelAI in-house (Kayra)", "13B", "2023-08"),
    "llama-3-erato-v1": ("Llama 3 70B (Erato)", "70B", "2024-10"),
    "xialong-v1": ("Xialong (NovelAI finetune of GLM-4.6)", "355B MoE", "2026-03"),
    "glm-4-6": ("GLM-4.6 (Z.ai, open weights)", "355B MoE", "2025-10"),
}


def month(ts):
    if not ts:
        return None
    try:
        return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m")
    except (OSError, ValueError, OverflowError):
        return None


def load(path):
    return [json.loads(line) for line in path.open(encoding="utf-8")]


def pct(n, d):
    return f"{100.0 * n / d:.1f}%" if d else "-"


def fmt(x, nd=2):
    if x is None:
        return "-"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def table(headers, rows, aligns=None):
    aligns = aligns or ["---"] * len(headers)
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(aligns) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def quantiles(vals):
    vals = sorted(v for v in vals if isinstance(v, (int, float)))
    if not vals:
        return None
    n = len(vals)

    def q(p):
        i = min(n - 1, max(0, int(round(p * (n - 1)))))
        return vals[i]

    return {
        "n": n,
        "min": vals[0],
        "p25": q(0.25),
        "median": q(0.5),
        "p75": q(0.75),
        "max": vals[-1],
        "mean": statistics.fmean(vals),
    }


def section_corpus(recs):
    generated = [r for r in recs if r["ai_chars"] > 0]
    months = sorted({m for m in (month(r["last_updated_at"]) for r in recs) if m})
    total_ai = sum(r["ai_chars"] for r in recs)
    total_human = sum(r["human_chars"] for r in recs)
    lines = [
        "## 1. What is actually in here",
        "",
        f"- **{len(recs)}** recovered story files "
        f"(of 2500 indexed; 483 could not be decrypted -- see `MISSING.md` in the export).",
        f"- **{len(generated)}** contain at least one model generation; "
        f"**{len(recs) - len(generated)}** are text-only "
        "(pasted articles, text-to-speech scratchpads, empty stubs).",
        f"- Activity spans **{months[0]} to {months[-1]}**.",
        f"- **{total_ai / 1e6:.2f}M** characters of model output alongside "
        f"**{total_human / 1e6:.2f}M** characters of human text.",
        f"- **{sum(r['n_blocks'] for r in recs):,}** edit-history blocks retained -- "
        "the export preserves the full undo tree, not just the final text.",
        "",
    ]
    return "\n".join(lines)


def section_models(recs):
    by_model = Counter(r["model"] for r in recs)
    rows = []
    for m, n in by_model.most_common():
        sub = [r for r in recs if r["model"] == m]
        ms = sorted({x for x in (month(r["last_updated_at"]) for r in sub) if x})
        ai = sum(r["ai_chars"] for r in sub)
        hu = sum(r["human_chars"] for r in sub)
        note = MODEL_NOTES.get(m, ("?", "?", "?"))
        rows.append(
            [
                f"`{m}`",
                note[0],
                note[1],
                n,
                f"{ms[0]}..{ms[-1]}" if ms else "-",
                f"{ai / 1000:.0f}k",
                pct(ai, ai + hu),
            ]
        )
    return (
        "## 2. Models used, and for how long\n\n"
        + table(
            ["setting", "what it is", "params", "stories", "active", "AI chars", "AI share of text"],
            rows,
            ["---", "---", "---", "---:", "---", "---:", "---:"],
        )
        + "\n"
    )


def section_sampling(recs):
    gen = [r for r in recs if r["ai_chars"] > 0 and r["temperature"] is not None]
    q = quantiles([r["temperature"] for r in gen])
    counts = Counter(r["temperature"] for r in gen)
    top = counts.most_common(12)

    rows = []
    for m in sorted({r["model"] for r in gen}):
        sub = [r for r in gen if r["model"] == m]
        qq = quantiles([r["temperature"] for r in sub])
        hot = sum(1 for r in sub if r["temperature"] >= 2.0)
        rows.append(
            [
                f"`{m}`",
                qq["n"],
                fmt(qq["min"]),
                fmt(qq["median"]),
                fmt(qq["max"]),
                pct(hot, qq["n"]),
            ]
        )

    lines = [
        "## 3. Sampling temperature",
        "",
        f"Across {q['n']} generating stories: median **{q['median']:.2f}**, "
        f"mean **{q['mean']:.2f}**, range **{q['min']}--{q['max']}**.",
        "",
        "Most-used exact values:",
        "",
        table(
            ["temperature", "stories"],
            [[fmt(t), n] for t, n in top],
            ["---:", "---:"],
        ),
        "",
        "By model:",
        "",
        table(
            ["model", "stories", "min", "median", "max", "share at temp >= 2.0"],
            rows,
            ["---", "---:", "---:", "---:", "---:", "---:"],
        ),
        "",
    ]
    return "\n".join(lines)


def section_truncation(recs):
    gen = [r for r in recs if r["ai_chars"] > 0]
    fields = [
        ("top_k", 0),
        ("top_p", 1),
        ("top_a", 1),
        ("typical_p", 1),
        ("tail_free_sampling", 1),
        ("min_p", 0),
        ("cfg_scale", 1),
        ("mirostat_tau", 0),
        ("math1_temp", 0),
    ]
    rows = []
    for f, neutral in fields:
        vals = [r.get(f) for r in gen if r.get(f) is not None]
        if not vals:
            continue
        active = [v for v in vals if v != neutral]
        qq = quantiles(active) if active else None
        rows.append(
            [
                f"`{f}`",
                len(vals),
                pct(len(active), len(vals)),
                fmt(qq["median"]) if qq else "-",
                fmt(qq["min"]) if qq else "-",
                fmt(qq["max"]) if qq else "-",
            ]
        )

    order_counts = Counter(
        " > ".join(r["sampler_order_enabled"] or []) for r in gen if r.get("sampler_order_enabled")
    )
    return (
        "## 4. Truncation samplers\n\n"
        "`neutral` means the value that disables the sampler. "
        "The share column is how often the author moved it off neutral.\n\n"
        + table(
            ["parameter", "stories with field", "share active", "median (active)", "min", "max"],
            rows,
            ["---", "---:", "---:", "---:", "---:", "---:"],
        )
        + "\n\nMost common enabled-sampler orderings:\n\n"
        + table(
            ["order", "stories"],
            [[o or "(none)", n] for o, n in order_counts.most_common(6)],
            ["---", "---:"],
        )
        + "\n"
    )


def section_repetition(recs):
    gen = [r for r in recs if r["ai_chars"] > 0]
    rows = []
    for f in (
        "repetition_penalty",
        "repetition_penalty_range",
        "repetition_penalty_slope",
        "repetition_penalty_frequency",
        "repetition_penalty_presence",
        "phrase_rep_pen",
    ):
        vals = [r.get(f) for r in gen if isinstance(r.get(f), (int, float))]
        qq = quantiles(vals)
        if not qq:
            continue
        rows.append([f"`{f}`", qq["n"], fmt(qq["min"]), fmt(qq["median"]), fmt(qq["max"])])
    phrase = Counter(r.get("phrase_rep_pen") for r in gen if r.get("phrase_rep_pen"))
    return (
        "## 5. Repetition control\n\n"
        + table(
            ["parameter", "n", "min", "median", "max"],
            rows,
            ["---", "---:", "---:", "---:", "---:"],
        )
        + (
            "\n\nPhrase repetition penalty settings (Kayra/Erato-era):\n\n"
            + table(
                ["setting", "stories"],
                [[f"`{k}`", v] for k, v in phrase.most_common()],
                ["---", "---:"],
            )
            if phrase
            else ""
        )
        + "\n"
    )


def section_steering(recs):
    gen = [r for r in recs if r["ai_chars"] > 0]
    n = len(gen)
    feats = [
        ("memory used", sum(1 for r in gen if r["memory_chars"] > 0)),
        ("author's note used", sum(1 for r in gen if r["authors_note_chars"] > 0)),
        ("lorebook entries", sum(1 for r in gen if r["lorebook_entries"] > 0)),
        ("phrase bias", sum(1 for r in gen if r["phrase_bias_phrases"] > 0)),
        ("banned sequences", sum(1 for r in gen if r["banned_sequences"] > 0)),
        ("ban brackets", sum(1 for r in gen if r.get("ban_brackets"))),
        ("trim responses", sum(1 for r in gen if r.get("trim_responses"))),
        (
            "a module other than `vanilla`",
            sum(1 for r in gen if r.get("module") not in (None, "vanilla")),
        ),
    ]
    rows = [[label, k, pct(k, n)] for label, k in feats]

    mem = quantiles([r["memory_chars"] for r in gen if r["memory_chars"] > 0])
    an = quantiles([r["authors_note_chars"] for r in gen if r["authors_note_chars"] > 0])
    lore = quantiles([r["lorebook_entries"] for r in gen if r["lorebook_entries"] > 0])

    extra = []
    if mem:
        extra.append(f"- Memory, when used: median **{mem['median']:.0f}** chars (max {mem['max']}).")
    if an:
        extra.append(
            f"- Author's Note, when used: median **{an['median']:.0f}** chars (max {an['max']})."
        )
    if lore:
        extra.append(
            f"- Lorebook, when used: median **{lore['median']:.0f}** entries (max {lore['max']})."
        )

    return (
        "## 6. Context-steering apparatus\n\n"
        f"Out of {n} generating stories:\n\n"
        + table(["feature", "stories", "share"], rows, ["---", "---:", "---:"])
        + "\n\n"
        + "\n".join(extra)
        + "\n"
    )


def section_revision(recs):
    gen = [r for r in recs if r["ai_chars"] > 0]
    rows = []
    for m, _ in Counter(r["model"] for r in gen).most_common():
        sub = [r for r in gen if r["model"] == m]
        live = sum(r["live_ai_chars"] for r in sub)
        dead = sum(r["abandoned_ai_chars"] for r in sub)
        branches = sum(r["extra_branches"] for r in sub)
        ai_blocks = sum(r["blocks_by_origin"].get("ai", 0) for r in sub)
        dead_blocks = sum(r["abandoned_ai_blocks"] for r in sub)
        edits = sum(r["blocks_by_origin"].get("edit", 0) for r in sub)
        rows.append(
            [
                f"`{m}`",
                len(sub),
                f"{ai_blocks:,}",
                pct(dead, live + dead),
                pct(dead_blocks, ai_blocks),
                f"{branches / len(sub):.2f}",
                f"{edits / max(1, ai_blocks):.2f}",
            ]
        )
    return (
        "## 7. Revision behaviour -- the accidental preference data\n\n"
        "NovelAI keeps abandoned branches in `datablocks`. Walking `prevBlock` "
        "back from `currentBlock` gives the surviving branch; AI text off that "
        "path is a generation the author rewound past. Branch points (a block "
        "with more than one successor) are rewind-and-retry events.\n\n"
        "(Do **not** use `removedFragments` for this -- see Test A0 in "
        "`PROBES.md` for why that measure is an artifact of the editor.)\n\n"
        + table(
            [
                "model",
                "stories",
                "AI blocks",
                "AI text abandoned",
                "AI blocks abandoned",
                "retries / story",
                "human edits per AI block",
            ],
            rows,
            ["---", "---:", "---:", "---:", "---:", "---:", "---:"],
        )
        + "\n"
    )


def section_cadence(recs):
    gen = [r for r in recs if r["ai_chars"] > 0]
    rows = []
    for m, _ in Counter(r["model"] for r in gen).most_common():
        sub = [r for r in gen if r["model"] == m]
        ai_blocks = sum(r["blocks_by_origin"].get("ai", 0) for r in sub)
        ai_chars = sum(r["ai_chars"] for r in sub)
        hu = sum(r["human_chars"] for r in sub)
        maxlen = quantiles([r["max_length"] for r in sub if r.get("max_length")])
        rows.append(
            [
                f"`{m}`",
                len(sub),
                f"{ai_chars / max(1, ai_blocks):.0f}",
                fmt(maxlen["median"], 0) if maxlen else "-",
                f"{ai_chars / max(1, hu):.2f}",
                f"{ai_blocks / len(sub):.1f}",
            ]
        )
    return (
        "## 8. Turn size and the human/model balance\n\n"
        "`chars per AI block` is how much text the author accepted per generation "
        "call; `max_length` is the token budget they allowed it. The ratio column "
        "is model characters per human character in the finished tree.\n\n"
        + table(
            [
                "model",
                "stories",
                "chars per AI block",
                "median max_length (tokens)",
                "AI:human chars",
                "AI blocks / story",
            ],
            rows,
            ["---", "---:", "---:", "---:", "---:", "---:"],
        )
        + "\n"
    )


def section_timeline(recs):
    by_month = defaultdict(list)
    for r in recs:
        m = month(r["last_updated_at"])
        if m:
            by_month[m].append(r)
    rows = []
    for m in sorted(by_month):
        sub = by_month[m]
        gen = [r for r in sub if r["ai_chars"] > 0]
        models = Counter(r["model"] for r in gen)
        temps = quantiles([r["temperature"] for r in gen if r["temperature"] is not None])
        rows.append(
            [
                m,
                len(sub),
                len(gen),
                ", ".join(f"{k}({v})" for k, v in models.most_common(2)) or "-",
                fmt(temps["median"]) if temps else "-",
                f"{sum(r['ai_chars'] for r in sub) / 1000:.0f}k",
            ]
        )
    return (
        "## 9. Month by month\n\n"
        + table(
            ["month", "stories", "with generation", "dominant model(s)", "median temp", "AI chars"],
            rows,
            ["---", "---:", "---:", "---", "---:", "---:"],
        )
        + "\n"
    )


def section_presets(recs):
    gen = [r for r in recs if r["ai_chars"] > 0]
    c = Counter(r["preset"] for r in gen)
    rows = []
    for p, n in c.most_common(15):
        sub = [r for r in gen if r["preset"] == p]
        temps = quantiles([r["temperature"] for r in sub if r["temperature"] is not None])
        models = Counter(r["model"] for r in sub).most_common(1)
        rows.append(
            [
                f"`{(p or '(none)')[:36]}`",
                n,
                models[0][0] if models else "-",
                fmt(temps["median"]) if temps else "-",
            ]
        )
    uniq = len(c)
    return (
        "## 10. Presets\n\n"
        f"{uniq} distinct preset ids across {len(gen)} generating stories. "
        "NovelAI stores presets by UUID, so built-ins and hand-rolled presets are "
        "indistinguishable here without the client-side preset table -- but the "
        "*spread* is the point.\n\n"
        + table(
            ["preset id", "stories", "usual model", "median temp"],
            rows,
            ["---", "---:", "---", "---:"],
        )
        + "\n"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stories", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("TABLES.md"))
    args = ap.parse_args()

    recs = load(args.stories)
    parts = [
        "# Corpus tables",
        "",
        "Generated by `analysis/report.py`. Descriptive statistics only.",
        "",
        section_corpus(recs),
        section_models(recs),
        section_sampling(recs),
        section_truncation(recs),
        section_repetition(recs),
        section_steering(recs),
        section_revision(recs),
        section_cadence(recs),
        section_presets(recs),
        section_timeline(recs),
    ]
    args.out.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
