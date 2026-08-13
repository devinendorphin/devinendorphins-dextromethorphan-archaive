#!/usr/bin/env python3
"""Where is the corpus *only* Endorphin? A span-level screen, not a file-level one.

`analysis/pasted.py` screens whole stories: it flags the 233 files whose 'human'
text dominates, 72 of them with `live_ai_chars` = 0. Endorphin's correction on
2026-08-12 is that this misses most of what it is looking for:

    "There are parts of the corpus that are totally me. The response to Ted
    Chiang of the New Yorker, pure essay. Most of the episode where I make a
    simulation of my ex who had gone with my abusers to the woods. very little
    generation there. My appeal to youtube to please dont delete my channel. a
    PFCizer on accountability that's actually correspondence with a friend i
    made repair with already. There might be other."

*Parts.* *Most of the episode.* The unit is the **episode**, and the standing
note records that the big series are appended -- each broadcast adds to one file
to build context. So a model-free episode sits inside a document that is 60-80%
model overall, and a per-file ratio cannot see it. `Emotional Abuse SImulator
v. 7.0` is the case in point: **64% model by character**, and it carries an
unbroken human span of **375,730 characters**.

This walks the surviving branch (per the standing note: `prevBlock` back from
`currentBlock`, never `removedFragments`) and reports maximal runs of
consecutive non-model blocks.

**It does not identify authorship, and must not be read as if it did.** A human
span is any text that arrived without in-tab generation, which `PASTED.md` shows
is three different things the schema cannot separate: another model's output
pasted back in, wholesale source documents, and Endorphin's own writing. The
screen narrows the search; a human still has to read the result.

**No span text is printed or written to the report.** The four pieces he names
are an essay, a simulation involving his abusers, an appeal to a platform, and
private correspondence with a named friend. The repo is public. Lengths, ids and
offsets only -- pass `--grep` to search locally without emitting what matched.

    python3 analysis/spans.py corpus/json --report analysis/SPANS.md
    python3 analysis/spans.py corpus/json --grep 'ted chiang' --min 2000
"""

import argparse
import json
import pathlib
import re
import statistics as st

HUMAN = ("user", "edit")


def live_path(doc):
    """Blocks on the surviving branch, in order. Never trust removedFragments."""
    story = doc["content"]["data"]["story"]
    blocks = story["datablocks"]
    path, i, seen = [], story.get("currentBlock"), set()
    while isinstance(i, int) and 0 <= i < len(blocks) and i not in seen:
        seen.add(i)
        path.append(blocks[i])
        i = blocks[i].get("prevBlock")
    path.reverse()
    return path


def spans_of(path):
    """(chars, n_blocks, start_index, text) for each maximal human run."""
    out, run, start = [], [], 0
    for idx, b in enumerate(path):
        frag = b.get("dataFragment") or {}
        if frag.get("origin") in HUMAN:
            if not run:
                start = idx
            run.append(frag.get("data", ""))
        elif run:
            out.append((sum(map(len, run)), len(run), start, "".join(run)))
            run = []
    if run:
        out.append((sum(map(len, run)), len(run), start, "".join(run)))
    return out


def totals(path):
    ai = hum = 0
    for b in path:
        frag = b.get("dataFragment") or {}
        n = len(frag.get("data", ""))
        if frag.get("origin") == "ai":
            ai += n
        elif frag.get("origin") in HUMAN:
            hum += n
    return ai, hum


def scan(folder, min_chars):
    rows = []
    for p in sorted(pathlib.Path(folder).glob("*.json")):
        try:
            doc = json.loads(p.read_text(encoding="utf-8", errors="replace"))
            path = live_path(doc)
            title = doc["story"]["data"].get("title") or ""
        except Exception:  # noqa: BLE001 -- 483 files never decrypted; skip quietly
            continue
        ai, hum = totals(path)
        for chars, nblk, start, text in spans_of(path):
            if chars >= min_chars:
                rows.append({"file": p.name, "title": title, "chars": chars,
                             "blocks": nblk, "start": start, "ai": ai, "human": hum,
                             "text": text})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="the mirrored story JSON")
    ap.add_argument("--min", type=int, default=20000, help="minimum span characters")
    ap.add_argument("--grep", help="regex; prints matching spans' ids only, never text")
    ap.add_argument("--report", type=pathlib.Path)
    args = ap.parse_args()

    rows = scan(args.folder, args.min)
    rows.sort(key=lambda r: -r["chars"])

    if args.grep:
        pat = re.compile(args.grep, re.I)
        hits = [r for r in rows if pat.search(r["text"])]
        print(f"{len(hits)} spans match (of {len(rows)} at >={args.min:,} chars)")
        for r in hits[:40]:
            share = 100 * r["ai"] / max(r["ai"] + r["human"], 1)
            print(f"  {r['chars']:>8}c {r['blocks']:>3}blk  block {r['start']:>5}  "
                  f"file {share:>4.0f}% model  {r['file'][:60]}")
        return

    # Dedupe for the headline count: forks copy whole branch histories, so the
    # same span lives under many story ids (standing note: never group by id).
    uniq = {}
    for r in rows:
        uniq.setdefault((r["chars"], r["blocks"]), r)
    dedup = sorted(uniq.values(), key=lambda r: -r["chars"])

    L = [
        "# Spans — where the corpus is model-free, at episode scale",
        "",
        "Generated by `analysis/spans.py`.",
        "",
        f"Maximal runs of consecutive non-model blocks on the surviving branch, "
        f"at **{args.min:,} characters or more**: **{len(rows):,}** spans, "
        f"**{len(dedup):,}** after collapsing fork duplicates.",
        "",
        "`analysis/PASTED.md` screens whole files and finds 233. This screens *inside*",
        "files, because the big series are appended — one file per series, one episode",
        "per session — so a model-free episode is invisible to a per-file ratio.",
        "",
        "| span chars | blocks | at block | file is | title |",
        "|---:|---:|---:|---:|---|",
    ]
    for r in dedup[:25]:
        share = 100 * r["ai"] / max(r["ai"] + r["human"], 1)
        title = r["title"] or "*(untitled)*"
        L.append(f"| {r['chars']:,} | {r['blocks']} | {r['start']:,} | "
                 f"{share:.0f}% model | {title[:52]} |")

    big_in_model_heavy = [r for r in dedup
                          if r["ai"] / max(r["ai"] + r["human"], 1) > 0.5]
    L += [
        "",
        f"**{len(big_in_model_heavy):,} of these sit inside files that are majority "
        "model by character** — exactly the population a per-file screen discards.",
        "",
        "## What this is not",
        "",
        "It is not an authorship test. A human span is any text that arrived without",
        "in-tab generation, and `PASTED.md` shows that is three things the schema cannot",
        "tell apart: another model's output pasted back in (Llama 2 via Replicate, up to",
        "temperature 5), wholesale source documents (the Army monograph, a Guardian",
        "obituary, *Bleeding Edge*), and Endorphin's own writing. This narrows the search",
        "from 2,016 files to a few hundred spans. A person still has to read them.",
        "",
        "No span text appears here, deliberately — see the script's docstring. The",
        "material this is built to find includes an account involving his abusers and",
        "private correspondence, and the repo is public.",
        "",
        "## Status of the four he named",
        "",
        "| piece | found | note |",
        "|---|---|---|",
        "| Ted Chiang / New Yorker response | **located, body absent** | two files carry "
        "the framing and elide the essay as `[See episode 1580 …]` — he confirms 1580 is "
        "*AI Makes Art*; the text itself lives in the broadcast |",
        "| the episode simulating his ex | **LOCATED 2026-08-12** | `Emotional Abuse "
        "SImulator v. 7.0`, 15 fork copies. See below |",
        "| the magick / Lemoine episode | **LOCATED 2026-08-12** | `New Story (11)`–`(16)`, "
        "turn 388, last touched 2024-01-24. See below |",
        "| PFCizer on accountability | **series located** | a seven-fork `New Story 3..9` "
        "family, up to 443 mentions; which fork holds the correspondence is unread |",
        "| the YouTube appeal | **not found** | no title or phrase search has hit it |",
        "",
        "**The one that broke open did so on a phrase he supplied**, not on a better",
        "script: *\"there is a scene where we are in that ramen place he liked, which had",
        "closed off rooms for solitary tasting.\"* The archive renders it as **`Loading",
        "ramen flavor booth, occupation two`**, with the two people present given",
        "*\"HIPAA anonymized screennames\"* — so no search for *ramen place*, *booth* or a",
        "name could have reached it. It sits at **turn 2132 on the live branch, origin",
        "`edit`**, in all 15 forks; the earliest surviving copy was last touched",
        "2023-12-01.",
        "",
        "**And the density check first said he was wrong, which was the measurement's",
        "fault.** He describes the episode as having *\"very little generation there\"*, but",
        "the window around turn 2132 is 73% model at ±25 turns — the scene opens inside a",
        "stretch where the simulator is still running. Profiling the whole document by",
        "100-turn window resolves it: **turns 2200–2300 are 25.5% model, the least-model",
        "window in all 3,688 turns**, against a whole-file figure of 71.4%. His second",
        "quoted line, *\"you gotta hate someone\"*, sits at turn 2280, inside it. The ramen",
        "booth is the **entrance** to the episode and the model-free stretch is immediately",
        "after it. Centre the window on the scene marker and the claim looks false; profile",
        "the document and it is exactly right.",
        "",
        "That is the standing note about his recall earning itself again, and a second",
        "lesson on top of the unit problem: **a scene marker is not the middle of a scene.**",
        "",
        "## The magick episode, and a correction",
        "",
        "**Located.** `New Story (11)`–`(16)`, six forks, created 2023-11-17 and last",
        "touched **2024-01-24** — his *\"like January 2024\"*. The phrase **`magickal",
        "capacity`** appears in exactly six files corpus-wide and at **turn 388** in every",
        "one. Its Spotify title, *The Magickal Capacity*, is not in the archive; the",
        "Twitch titles are unreliable by his own account (*\"that was a twitch glitch\"*),",
        "so the working index is the phrase, not the name.",
        "",
        "The structure is exactly as he described it. **Turn 388 is his** (`user`), closing",
        "the spoken half and handing over: *\"Sometimes just calling one's attention to it",
        "is all ya need… here's 10 tips for self-exploration of your magickal capacity: 1.\"*",
        "**Turns 389 onward are all `ai`** — the model writes the ten tips. One human turn",
        "sets the form and the generation fills it, which is the corpus's turn-taking frame",
        "in its purest instance.",
        "",
        "### The correction",
        "",
        "An earlier version of this file said the phrases he remembers these episodes by",
        "return **zero** matches across the corpus, and concluded that the performance",
        "lives only in the broadcast audio. **That was wrong, and it was wrong the same way",
        "§4 was wrong**: the search was run inside one candidate file rather than across",
        "the corpus. Corpus-wide:",
        "",
        "| remembered phrase | in the archive | where | origin |",
        "|---|---|---|---|",
        "| *\"Bitch, I'm comfortable!\"* | **yes**, 6 files | turn 391 | **`ai`** |",
        "| *\"gardening gives you easy gains\"* | **in substance**, 6 files | turns 396–397 |"
        " **`ai`** |",
        "| *\"you gotta hate someone\"* | **yes**, 14 files | turn 2280 | `edit` |",
        "| *\"I'm truly adverbally sorry!\"* | **no**, 0 files | — | spoken only |",
        "",
        "So the score thesis holds for one line out of four, not for all of them. `READINGS`",
        "§IX still stands — *adverbally* is genuinely absent and was said aloud — but **the",
        "archive retains far more of the performance than the failed search suggested.**",
        "",
        "### Two things worth keeping from it",
        "",
        "**He attributes correctly, unprompted.** Told only that a phrase was missing, he",
        "said *\"the gains part that would be in the text generative part\"* — and it is.",
        "Turn 388 is his, 389 onward are the model's, and he placed the line on the right",
        "side of a boundary he could not see, in a document he last touched two and a half",
        "years ago.",
        "",
        "**But his memory sharpens the model's prose.** He recalls *\"gardening gives you",
        "easy gains\"*. What the model actually wrote is *\"plants and fungi will help keep",
        "your stress down, and give you those little wins each day\"*, with *the garden*",
        "arriving in the next turn. `easy gains` appears **nowhere** in the corpus. The",
        "remembered line is tighter than the generated one — alliterative, four words",
        "shorter, and better. **That is editorial work happening in recall**, and it bears",
        "directly on the open collaboration disagreement in `sessions/LATEST.md`: what he",
        "carries away from a session is not the model's text but a compressed improvement",
        "on it, which is a mechanism neither side of that argument had named.",
    ]
    out = "\n".join(L) + "\n"
    if args.report:
        args.report.write_text(out, encoding="utf-8")
        print(f"wrote {args.report} ({len(rows):,} spans, {len(dedup):,} unique)")
    else:
        print(out)


if __name__ == "__main__":
    main()
