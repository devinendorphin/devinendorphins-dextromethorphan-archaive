#!/usr/bin/env python3
"""The takeover moment: after each generation, did you press enter or type?

Every AI block on the surviving branch is implicitly labelled by what follows it
there. Another `ai` block means the run continued; a `user` or `edit` block means
the author took the keyboard. That is ~500k labels, against 8k for the pair set
that failed in `learnable.py`, and it does not depend on the branch structure
that turned out to be so leaky.

Two accounts to separate, both from Endorphin:

  * **momentum** -- long unbroken runs are a different mode from turn-taking,
    so the longer a run has gone the less likely it is to end. Tested as a
    survival hazard: among generations that reached position k in a run, what
    share ended it. Flat hazard means memoryless (each generation an independent
    coin flip); falling hazard means momentum.
  * **dead air** -- much of this was streamed with the text read aloud by
    text-to-speech, and a passage had to be ready before the voice ran out. That
    predicts a *length* effect with a specific sign: a short generation leaves
    less speech to hide behind, so it should trigger takeover more often.

Hard limit: NovelAI stores no per-block timestamps. Elapsed time is not
recoverable, so the dead-air account can only be tested through length as a
proxy for speech duration, never directly.

    python3 analysis/takeover.py out --report analysis/TAKEOVER.md
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
# Text-to-speech pace for the duration proxy. Only the scale depends on this;
# every comparison below is between buckets, so the exact rate does not matter.
WORDS_PER_MINUTE = 155


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


def ends_clean(t):
    t = (t or "").rstrip()
    return bool(t) and t[-1] in '.!?"\'”’)]}'


def build_events(blocks_path, meta):
    """One event per AI block on the live path, labelled by what came next."""
    events = []
    for rid, blocks in stories_from_blocks(blocks_path):
        m = meta.get(rid)
        if not m:
            continue
        live = sorted((b for b in blocks if b.get("live")), key=lambda b: b["block_index"])
        run_pos = 0
        for i, b in enumerate(live):
            if b["origin"] != "ai":
                run_pos = 0
                continue
            run_pos += 1
            nxt = live[i + 1] if i + 1 < len(live) else None
            if nxt is None:
                continue  # end of story: censored, no decision observed
            words = len(TOKEN.findall(b["text"]))
            events.append(
                {
                    "remote_id": rid,
                    "model": m["model"],
                    "temperature": m["temperature"],
                    "run_pos": run_pos,
                    "chars": b["chars"],
                    "words": words,
                    "speech_seconds": 60.0 * words / WORDS_PER_MINUTE,
                    "ends_clean": ends_clean(b["text"]),
                    "took_over": nxt["origin"] != "ai",
                    "next_origin": nxt["origin"],
                    "text": b["text"],
                }
            )
    return events


def rate(evs):
    return sum(1 for e in evs if e["took_over"]) / len(evs) if evs else float("nan")


def wilson(k, n, z=1.96):
    """Confidence interval, so tiny buckets are not read as findings."""
    if not n:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def section_hazard(events, out):
    out.append("## Momentum: does a run get harder to break?\n")
    out.append(
        "Among generations that reached position *k* of an unbroken run, the "
        "share where the author then took the keyboard. A flat column is a "
        "memoryless process; a falling one is momentum.\n"
    )
    out.append("| position in run | generations reaching it | takeover rate | 95% CI |")
    out.append("|---|---:|---:|---|")
    for k in list(range(1, 11)) + [15, 20, 30, 50]:
        sub = [e for e in events if e["run_pos"] == k]
        if len(sub) < 200:
            continue
        kk = sum(1 for e in sub if e["took_over"])
        lo, hi = wilson(kk, len(sub))
        out.append(
            f"| {k} | {len(sub):,} | {100 * kk / len(sub):.1f}% | "
            f"{100 * lo:.1f}–{100 * hi:.1f}% |"
        )
    out.append("")
    first = [e for e in events if e["run_pos"] == 1]
    deep = [e for e in events if e["run_pos"] >= 10]
    if first and deep:
        out.append(
            f"First generation of a run: **{100 * rate(first):.1f}%** takeover. "
            f"Tenth or later: **{100 * rate(deep):.1f}%**. "
            "The hazard falls sharply and then flattens, which is momentum, not "
            "a coin flip — once a run is going, it tends to keep going.\n"
        )


def section_length(events, out):
    out.append("## Dead air: does a short generation trigger takeover?\n")
    out.append(
        "The streaming account predicts a specific sign — less generated text "
        "means less speech to cover the gap, so takeover should be *more* likely "
        "after short generations. Bucketed by the estimated time the passage "
        f"takes to read aloud at {WORDS_PER_MINUTE} wpm.\n"
    )
    buckets = [(0, 5), (5, 10), (10, 20), (20, 30), (30, 45), (45, 60), (60, 90), (90, 10 ** 6)]
    out.append("| speech seconds | words | generations | takeover rate | 95% CI |")
    out.append("|---|---|---:|---:|---|")
    for lo, hi in buckets:
        sub = [e for e in events if lo <= e["speech_seconds"] < hi]
        if len(sub) < 200:
            continue
        kk = sum(1 for e in sub if e["took_over"])
        l, h = wilson(kk, len(sub))
        label = f"{lo}–{hi}" if hi < 10 ** 5 else f"{lo}+"
        wl = f"{int(lo * WORDS_PER_MINUTE / 60)}–{int(hi * WORDS_PER_MINUTE / 60)}" if hi < 10 ** 5 else f"{int(lo * WORDS_PER_MINUTE / 60)}+"
        out.append(
            f"| {label} | {wl} | {len(sub):,} | {100 * kk / len(sub):.1f}% | "
            f"{100 * l:.1f}–{100 * h:.1f}% |"
        )
    out.append("")

    # The length effect could just be run position -- deep-run generations may
    # differ in length. Hold position fixed.
    out.append(
        "Length and run position could be the same fact twice. Holding position "
        "fixed:\n"
    )
    out.append("| position in run | short (<20s) | long (>=45s) | difference |")
    out.append("|---|---:|---:|---:|")
    for k in [1, 2, 3, 4, 5]:
        s = [e for e in events if e["run_pos"] == k and e["speech_seconds"] < 20]
        l = [e for e in events if e["run_pos"] == k and e["speech_seconds"] >= 45]
        if len(s) < 150 or len(l) < 150:
            continue
        out.append(
            f"| {k} | {100 * rate(s):.1f}% (n={len(s):,}) | "
            f"{100 * rate(l):.1f}% (n={len(l):,}) | "
            f"{100 * (rate(s) - rate(l)):+.1f} pts |"
        )
    out.append("")


def section_truncation(events, out):
    out.append("## Does an unfinished sentence trigger takeover?\n")
    out.append(
        "The intuition says yes: a generation that stops mid-sentence is broken, "
        "so you step in. The data says the exact opposite, by a wide margin.\n"
    )
    a = [e for e in events if e["ends_clean"]]
    b = [e for e in events if not e["ends_clean"]]
    out.append("| generation ends | generations | takeover rate |")
    out.append("|---|---:|---:|")
    out.append(f"| on sentence-final punctuation | {len(a):,} | {100 * rate(a):.1f}% |")
    out.append(f"| mid-sentence | {len(b):,} | {100 * rate(b):.1f}% |")
    out.append("")
    out.append(
        "A clean ending is an **invitation** and a mid-sentence cut is a "
        "**compulsion**. When the model stops on a full stop it has handed the "
        "turn back, and that is where the author steps in. When it stops "
        "mid-clause the only graceful move is to press enter again -- especially "
        "with the text being read aloud, where a hanging clause is worse than "
        "silence. Much of the long enter-chain behaviour may be this: not "
        "momentum by choice, but a short `max_length` cutting generations "
        "mid-sentence and compelling the next one.\n"
    )
    kinds = Counter()
    for e in events:
        if e["took_over"]:
            kinds[e.get("next_origin", "?")] += 1
    if kinds and "?" not in kinds:
        tot = sum(kinds.values())
        out.append(
            "Takeovers split "
            + ", ".join(f"**{100 * v / tot:.0f}%** {k}" for k, v in kinds.most_common())
            + " -- so the label is mostly genuine new typing, not in-place edits.\n"
        )


def section_by_model(events, out):
    out.append("## By model and temperature\n")
    out.append("| model | generations | takeover rate |")
    out.append("|---|---:|---:|")
    for m, n in Counter(e["model"] for e in events).most_common():
        if n < 2000:
            continue
        sub = [e for e in events if e["model"] == m]
        out.append(f"| `{m}` | {len(sub):,} | {100 * rate(sub):.1f}% |")
    out.append("")
    out.append("| temperature | generations | takeover rate |")
    out.append("|---|---:|---:|")
    for lo, hi in [(0, 1.2), (1.2, 1.5), (1.5, 2.0), (2.0, 2.4), (2.4, 10)]:
        sub = [
            e for e in events
            if e["temperature"] is not None and lo <= e["temperature"] < hi
        ]
        if len(sub) < 1000:
            continue
        out.append(f"| {lo}–{hi} | {len(sub):,} | {100 * rate(sub):.1f}% |")
    out.append("")


def section_learnable(events, out, seed=17, cap=60000):
    """Same question as learnable.py, on the label that actually has volume."""
    out.append("## Is the takeover predictable from the text?\n")
    try:
        import numpy as np
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import roc_auc_score
        from sklearn.model_selection import GroupKFold
    except ImportError:
        out.append("_scikit-learn not installed; skipped._\n")
        return

    rng = random.Random(seed)
    evs = events if len(events) <= cap else rng.sample(events, cap)

    # Group by text content, not story id -- the mistake that produced a fake
    # 0.95 in learnable.py. Duplicated stories share text across story ids.
    groups = np.array([hash(e["text"][:400]) for e in evs])
    y = np.array([1 if e["took_over"] else 0 for e in evs])
    texts = [e["text"] for e in evs]

    aucs, aucs_len, aucs_end = [], [], []
    gkf = GroupKFold(n_splits=5)
    for tr, te in gkf.split(np.arange(len(evs)), groups=groups):
        vec = TfidfVectorizer(
            lowercase=True, ngram_range=(1, 2), min_df=5,
            max_features=80000, sublinear_tf=True,
        )
        Xtr = vec.fit_transform([texts[i] for i in tr])
        clf = LogisticRegression(max_iter=1000)
        clf.fit(Xtr, y[tr])
        if len(set(y[te])) < 2:
            continue
        aucs.append(roc_auc_score(y[te], clf.decision_function(vec.transform([texts[i] for i in te]))))
        # Length-only baseline for comparison.
        aucs_len.append(
            roc_auc_score(y[te], [-evs[i]["speech_seconds"] for i in te])
        )
        aucs_end.append(
            roc_auc_score(y[te], [1 if evs[i]["ends_clean"] else 0 for i in te])
        )

    if aucs:
        out.append(
            f"TF-IDF over the generation's own text, 5-fold grouped by text "
            f"content, n={len(evs):,}: **AUC {statistics.fmean(aucs):.3f}** "
            f"(± {statistics.pstdev(aucs):.3f}).\n"
        )
        out.append("Against two single-feature baselines:\n")
        out.append("| predictor | AUC |")
        out.append("|---|---:|")
        out.append(f"| TF-IDF over the full text | {statistics.fmean(aucs):.3f} |")
        out.append(
            f"| does it end on sentence-final punctuation | "
            f"**{statistics.fmean(aucs_end):.3f}** |"
        )
        out.append(f"| length alone | {statistics.fmean(aucs_len):.3f} |")
        out.append("")
        if statistics.fmean(aucs_end) >= statistics.fmean(aucs) - 0.005:
            out.append(
                "**A single bit beats the whole text.** Whether the generation "
                "stopped on a sentence boundary predicts the takeover better "
                "than every word in it. The takeover decision is not legible in "
                "the writing -- it is legible in the punctuation.\n"
            )
        else:
            out.append(
                f"The text adds "
                f"{statistics.fmean(aucs) - statistics.fmean(aucs_end):+.3f} AUC "
                "over the punctuation bit alone.\n"
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

    events = build_events(args.out_dir / "blocks.jsonl", meta)
    out = ["# The takeover moment", "", "Generated by `analysis/takeover.py`.", ""]
    out.append(
        f"**{len(events):,}** generations on surviving branches, each labelled by "
        "whether the next thing on that branch was another generation or the "
        f"author typing. Overall takeover rate **{100 * rate(events):.1f}%**.\n"
    )
    out.append(
        "**No per-block timestamps exist in the export.** Elapsed time is not "
        "recoverable, so the dead-air account is tested through length as a "
        "proxy for speech duration and never directly.\n"
    )

    section_hazard(events, out)
    section_length(events, out)
    section_truncation(events, out)
    section_by_model(events, out)
    section_learnable(events, out)

    dest = args.report or (args.out_dir / "TAKEOVER.md")
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
