#!/usr/bin/env python3
"""A taxonomy of the author's turns, and what each kind of turn buys.

`FINDINGS.md` establishes that the human move following a generation is usually
a cue rather than an edit -- median 55 characters. That treats 134,063 turns as
one undifferentiated thing. They are not. Naming a character, issuing a
second-person directive, asking a question and continuing the model's sentence
are different moves, and if the turn-taking frame is right they should buy
different things.

The categories here are syntactic and were read off the data, not imposed: the
corpus uses a small number of recurring conventions (`Name:`, `> You ...`,
`{...}`, `[...]`) heavily and consistently.

Outcome measures, all forward-looking from the cue:

  * **run bought** -- how many generations follow before the author speaks
    again. How much the cue was worth in continuous output.
  * **next generation length** -- whether the cue makes the model expansive.
    This one turns out to be confounded and is reported only as a warning; see
    `section_within_model`.
  * **voice held** -- for cues that name a speaker, whether the model stays in
    that voice or immediately switches to a different speaker tag.

Duplicated stories inflate every count (see `learnable.py`), so each distinct
(cue text, following generation) pair is counted once. Raw and deduplicated
totals are both reported.

    python3 analysis/cues.py out --report analysis/CUES.md
"""

import argparse
import json
import math
import pathlib
import re
import statistics
from collections import Counter, defaultdict

TOKEN = re.compile(r"[A-Za-z][A-Za-z'-]*")
# A speaker tag: a short run of name-ish characters then a colon, at the start.
SPEAKER = re.compile(r"^\s*([A-Za-z0-9][\w .,'’\-()]{0,38}):(\s*)(.*)$", re.S)
SPEAKER_ANYWHERE = re.compile(r"([A-Za-z][\w .,'’\-()]{0,38}):\s")
MOSTLY_PUNCT = re.compile(r"^[\s*\-=_~#.·•—–…]+$")

CUE_ORDER = [
    "directive (>)",
    "stage direction {}",
    "instruction []",
    "handoff (Name:)",
    "speaker line (Name: ...)",
    "question",
    "section break",
    "continuation",
    "narration",
]


def is_name(candidate):
    """Guard against sentence fragments that happen to end in a colon.

    " surrounding AI alignment:" and "Choose a job from the list above:" both
    match a naive speaker pattern. Real speaker tags in this corpus are short
    and capitalised: Elegua, Izanami, Baby AGI, Dr Go, Kayra.
    """
    c = candidate.strip()
    return bool(c) and c[0].isupper() and len(c.split()) <= 4


def classify(text):
    """First match wins. Order matters: the bracket conventions are unambiguous,
    the speaker tag is next most reliable, and the fallbacks are last.

    Empty blocks are not turns. They are the delete half of NovelAI's
    delete-everything-then-reinsert rewrite (see FINDINGS §6a), and they are
    dropped upstream rather than classified.
    """
    t = text.strip()
    if not t:
        return "empty (editor artifact)"
    if t.startswith(">"):
        return "directive (>)"
    if t.startswith("{"):
        return "stage direction {}"
    if t.startswith("["):
        return "instruction []"
    if MOSTLY_PUNCT.match(t):
        return "section break"

    m = SPEAKER.match(t)
    if m and is_name(m.group(1)):
        rest = m.group(3).strip()
        # A name with nothing after the colon is a pure handoff: your turn.
        return "handoff (Name:)" if not rest else "speaker line (Name: ...)"

    if t.endswith("?"):
        return "question"
    # Lowercase or punctuation start = finishing the model's sentence for it.
    if t[0].islower() or not t[0].isalnum():
        return "continuation"
    return "narration"


def cued_name(text):
    m = SPEAKER.match(text.strip())
    return m.group(1).strip().lower() if m and is_name(m.group(1)) else None


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


def build(blocks_path, meta, max_chars=200):
    """One record per human turn that follows a generation."""
    recs = []
    for rid, blocks in stories_from_blocks(blocks_path):
        m = meta.get(rid)
        if not m:
            continue
        live = sorted((b for b in blocks if b.get("live")), key=lambda b: b["block_index"])
        for i in range(1, len(live)):
            cur, prev = live[i], live[i - 1]
            if cur["origin"] == "ai" or prev["origin"] != "ai":
                continue
            # How many generations does the author get before speaking again?
            run, j = 0, i + 1
            while j < len(live) and live[j]["origin"] == "ai":
                run += 1
                j += 1
            nxt = live[i + 1] if i + 1 < len(live) and live[i + 1]["origin"] == "ai" else None
            recs.append(
                {
                    "remote_id": rid,
                    "model": m["model"],
                    "created_at": m.get("created_at"),
                    "cue": cur["text"],
                    "cue_chars": cur["chars"],
                    "long": cur["chars"] > max_chars,
                    "kind": classify(cur["text"]) if cur["chars"] <= max_chars else "long turn",
                    "run_bought": run,
                    "next_chars": nxt["chars"] if nxt else None,
                    "next_text": (nxt["text"][:200] if nxt else ""),
                }
            )
    return recs


def dedupe(recs):
    seen, keep = set(), []
    for r in recs:
        k = (r["cue"], r["next_text"])
        if k in seen:
            continue
        seen.add(k)
        keep.append(r)
    return keep


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else float("nan")


def ci_mean(xs):
    xs = [x for x in xs if x is not None]
    if len(xs) < 2:
        return float("nan"), float("nan")
    m = statistics.fmean(xs)
    h = 1.96 * statistics.pstdev(xs) / math.sqrt(len(xs))
    return m, h


def section_distribution(recs, out):
    out.append("## What kinds of turn there are\n")
    n = len(recs)
    c = Counter(r["kind"] for r in recs)
    out.append("| kind | turns | share | median chars | example |")
    out.append("|---|---:|---:|---:|---|")
    examples = {}
    for r in recs:
        k = r["kind"]
        if k not in examples and 12 <= r["cue_chars"] <= 74:
            examples[k] = re.sub(r"\s+", " ", r["cue"]).strip()
    for k in CUE_ORDER + ["long turn"]:
        if k not in c:
            continue
        sub = [r for r in recs if r["kind"] == k]
        ex = examples.get(k, "")
        ex = ex.replace("|", "\\|")[:58]
        out.append(
            f"| {k} | {c[k]:,} | {100 * c[k] / n:.1f}% | "
            f"{med([r['cue_chars'] for r in sub]):.0f} | `{ex}` |"
        )
    out.append("")


def section_payoff(recs, out):
    out.append("## What each kind of turn buys\n")
    out.append(
        "`run bought` is how many generations follow before the author speaks "
        "again — the length of the model's turn. `next gen` is the size of the "
        "immediately following generation. Both are forward-looking, so they "
        "measure the consequence of the move rather than its occasion.\n"
    )
    out.append(
        "| kind | turns | mean run bought | 95% CI | median run | median next gen (chars) |"
    )
    out.append("|---|---:|---:|---|---:|---:|")
    rows = []
    for k in CUE_ORDER + ["long turn"]:
        sub = [r for r in recs if r["kind"] == k]
        if len(sub) < 200:
            continue
        m, h = ci_mean([r["run_bought"] for r in sub])
        rows.append((m, k, sub, h))
    for m, k, sub, h in sorted(rows, reverse=True):
        out.append(
            f"| {k} | {len(sub):,} | **{m:.2f}** | ±{h:.2f} | "
            f"{med([r['run_bought'] for r in sub]):.0f} | "
            f"{med([r['next_chars'] for r in sub]):.0f} |"
        )
    out.append("")
    if rows:
        top = max(rows)
        bot = min(rows)
        out.append(
            f"Top to bottom that is **{top[0]:.2f}** generations against "
            f"**{bot[0]:.2f}** — a {top[0] / bot[0]:.1f}× spread in how much "
            "continuous output a turn buys, depending only on how it was "
            "phrased.\n"
        )
    out.append(
        "**Do not read the last column from this table.** `instruction []` "
        "shows a median next generation of ~900 characters against ~490 for "
        "everything else, which looks like bracketed instructions making the "
        "model expansive. It is the confound from `FINDINGS.md` §7 again: those "
        "cues sit disproportionately in Erato sessions, where the median "
        "`max_length` is 250 tokens against 100 across the corpus. The next "
        "section holds the model fixed and the effect vanishes.\n"
    )


def section_within_model(recs, out, meta):
    """The cue mix differs by model, and so does max_length. Hold both fixed."""
    out.append("## Holding the model fixed\n")
    out.append(
        "Cue kinds are not evenly spread across models, and `max_length` moves "
        "with the model, so the pooled table above mixes two things. Within a "
        "single model both columns are comparable.\n"
    )
    for mdl in ("kayra-v1", "llama-3-erato-v1", "clio-v1"):
        sub = [r for r in recs if r["model"] == mdl]
        if len(sub) < 500:
            continue
        rows = []
        for k in CUE_ORDER + ["long turn"]:
            s_ = [r for r in sub if r["kind"] == k]
            if len(s_) < 80:
                continue
            m, h = ci_mean([r["run_bought"] for r in s_])
            rows.append((m, k, s_, h))
        if not rows:
            continue
        out.append(f"\n**`{mdl}`** — {len(sub):,} turns\n")
        out.append("| kind | turns | mean run bought | 95% CI | median next gen |")
        out.append("|---|---:|---:|---|---:|")
        for m, k, s_, h in sorted(rows, reverse=True):
            out.append(
                f"| {k} | {len(s_):,} | {m:.2f} | ±{h:.2f} | "
                f"{med([r['next_chars'] for r in s_]):.0f} |"
            )
    out.append("")
    out.append(
        "The next-generation column is now flat inside each model — Kayra sits "
        "at 442–509 characters for every kind of cue, Erato at 1,028–1,133. "
        "Generation length is set by `max_length`, not by how the author "
        "phrased the turn.\n"
    )
    out.append(
        "What survives the control is the run column, and one result in "
        "particular: **`> directive` buys the least in every model that has "
        "enough of them** — 1.79 in Kayra against a 2.43 median for that model, "
        "1.28 in Clio against 2.49. That is the text-adventure convention doing "
        "what it is designed to do: `> You ...` sets up strict alternation, one "
        "move each, so the author gets a reply rather than a run. The other "
        "orderings are broadly stable across models but the gaps are small "
        "relative to their intervals, and should not be pushed.\n"
    )


def section_voice(recs, out):
    """For turns that name a speaker, does the model stay in that voice?"""
    out.append("## Do the named voices hold?\n")
    out.append(
        "For turns that name a speaker, whether the following generation opens "
        "in that voice or switches to a different speaker tag inside the first "
        "80 characters.\n"
    )
    out.append(
        "The two rows do not mean the same thing. After a bare `Name:` handoff "
        "the model has been told whose turn it is, so a switch is a failure to "
        "take the cue. After a full `Name: line` the author has just *finished* "
        "a turn, so a switch to another speaker is dialogue working correctly. "
        "Only the first row measures uptake.\n"
    )
    rows = []
    for k in ("handoff (Name:)", "speaker line (Name: ...)"):
        sub = [r for r in recs if r["kind"] == k and r["next_text"]]
        if len(sub) < 100:
            continue
        held = bail = 0
        for r in sub:
            name = cued_name(r["cue"])
            head = r["next_text"][:80]
            m = SPEAKER_ANYWHERE.search(head)
            other = m and m.group(1).strip().lower() != name
            if other:
                bail += 1
            else:
                held += 1
        rows.append((k, len(sub), held / len(sub)))
    out.append("| kind | turns | voice held | switched speaker |")
    out.append("|---|---:|---:|---:|")
    for k, n, h in rows:
        out.append(f"| {k} | {n:,} | **{100 * h:.1f}%** | {100 * (1 - h):.1f}% |")
    out.append("")


def section_by_model(recs, out):
    out.append("## Does the repertoire change with the model?\n")
    out.append(
        "Share of turns of each kind, by model. Read down a column, not "
        "across — the confound in `FINDINGS.md` §7 applies here too, since "
        "model era and the author's habits moved together.\n"
    )
    models = [m for m, n in Counter(r["model"] for r in recs).most_common() if n >= 900]
    out.append("| kind | " + " | ".join(f"`{m}`" for m in models) + " |")
    out.append("|---|" + "|".join(["---:"] * len(models)) + "|")
    for k in CUE_ORDER + ["long turn"]:
        cells = []
        for m in models:
            sub = [r for r in recs if r["model"] == m]
            cells.append(f"{100 * sum(1 for r in sub if r['kind'] == k) / len(sub):.1f}%")
        out.append(f"| {k} | " + " | ".join(cells) + " |")
    out.append("")


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

    raw = build(args.out_dir / "blocks.jsonl", meta)
    recs = dedupe(raw)
    empty = [r for r in recs if r["kind"] == "empty (editor artifact)"]
    recs = [r for r in recs if r["kind"] != "empty (editor artifact)"]

    out = ["# A taxonomy of the author's turns", "",
           "Generated by `analysis/cues.py`.", ""]
    out.append(
        f"**{len(raw):,}** human turns following a generation, "
        f"**{len(recs):,}** distinct after removing the duplicated stories that "
        "repeat the same exchange under many story ids.\n"
    )
    out.append(
        f"A further **{len(empty):,}** distinct blocks were empty and are "
        "excluded: they are not turns but the delete half of NovelAI's "
        "delete-everything-then-reinsert rewrite (`FINDINGS.md` §6a). Left in "
        "they top the table below at 5.56 generations bought, which is an "
        "artifact of a rewrite being followed by a long uninterrupted stretch. "
        f"All figures use the remaining **{len(recs):,}**.\n"
    )
    section_distribution(recs, out)
    section_payoff(recs, out)
    section_within_model(recs, out, meta)
    section_voice(recs, out)
    section_by_model(recs, out)

    dest = args.report or (args.out_dir / "CUES.md")
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {dest}  (raw {len(raw):,}, deduped {len(recs):,})")


if __name__ == "__main__":
    main()
