#!/usr/bin/env python3
"""Recover the Twitch episode index from screenshots, and test it against story edits.

The channel's pre-YouTube back catalogue exists only as 83 phone screenshots of
the Twitch Video Producer dashboard, taken in one sitting on 2025-03-01. The
dashboard reports 1,604 videos; OCR recovers about 94% of the rows with a title,
a date, and a duration.

That index is the first external clock this corpus has had. `analysis/` has been
able to say *when a story was last edited* but never *what the author was doing
that day*. Joining the two tests the long-open question of whether the generation
was performed live.

    python3 analysis/episodes.py corpus/twitch --out data/EPISODES.tsv
    python3 analysis/episodes.py corpus/twitch --join out/stories.jsonl

Needs `tesseract` on PATH. The screenshots are dark-mode phone captures, so OCR
is imperfect: expect garbled titles and the occasional impossible date (anything
after the 2025-03-01 capture is a misread and is dropped). Missing rows depress
the join statistic, so the result below is conservative.
"""

import argparse
import collections
import datetime
import json
import pathlib
import random
import re
import subprocess
import sys

MONTHS = ("January|February|March|April|May|June|July|August|September|"
          "October|November|December")
DATE = re.compile(rf"({MONTHS})\s+([1-9]\d?),?\s*(20\d{{2}})")
CAPTURED = datetime.date(2025, 3, 1)


def ocr(shot_dir):
    """Run tesseract over every screenshot, yielding one text blob per image."""
    for img in sorted(pathlib.Path(shot_dir).glob("*.jpg")):
        out = subprocess.run(
            ["tesseract", str(img), "-", "--psm", "6"],
            capture_output=True, text=True, check=False,
        )
        yield out.stdout


def episodes(shot_dir):
    """(date, duration, title) per dashboard row, deduplicated across overlaps."""
    rows, seen = [], set()
    for blob in ocr(shot_dir):
        lines = blob.splitlines()
        for i, line in enumerate(lines):
            m = DATE.search(line)
            if not m:
                continue
            try:
                d = datetime.datetime.strptime(
                    f"{m.group(1)} {m.group(2)} {m.group(3)}", "%B %d %Y").date()
            except ValueError:
                continue
            if d > CAPTURED:      # impossible: the screenshots predate it
                continue
            # The title sits before the date on the same line, or just above it.
            head = line[:m.start()].strip()
            title = head if _titleish(head) else ""
            for j in range(i - 1, max(-1, i - 4), -1):
                if title:
                    break
                if _titleish(lines[j].strip()):
                    title = lines[j].strip()
            dur = re.search(r"(\d+:\d{2}(?::\d{2})?)", line[m.end():])
            title = _clean(title)
            key = (d, re.sub(r"\W", "", title)[:34].lower())
            if key in seen or not title:
                continue
            seen.add(key)
            rows.append((d, dur.group(1) if dur else "", title))
    return sorted(rows)


def _titleish(s):
    return len(s) > 12 and re.search(r"[A-Za-z]{4}", s)


# The dashboard's left sidebar and the row's Watch button OCR into the same
# line as the title, so trim from the episode marker to the button.
LEAD = re.compile(r"^.*?(?=\bEPISODE\b|\bEpisode\b|\bEp\b\.?\s*\d)", re.I)
TAIL = re.compile(r"\s*[D>|]*\s*Watch\s*[:.]?\s*$", re.I)


def _clean(title):
    t = LEAD.sub("", title, count=1) if re.search(r"episode", title, re.I) else title
    t = TAIL.sub("", t)
    return re.sub(r"\s+", " ", t).strip(" .:|>")


def join(rows, stories_path, trials=1000, seed=0):
    """Do story edits land on broadcast days more often than chance?

    Both series are bursty, so a flat base rate is the wrong control -- it would
    credit any two habits that happened to share the same busy months. Instead
    the episode calendar is circularly shifted, which preserves its clumping and
    destroys only the day-level alignment.
    """
    ep_days = {d for d, _, _ in rows}
    lo, hi = min(ep_days), max(ep_days)
    span = (hi - lo).days + 1
    edits = collections.Counter()
    for line in open(stories_path):
        ts = json.loads(line)["last_updated_at"]
        edits[datetime.datetime.fromtimestamp(
            ts, datetime.timezone.utc).date()] += 1

    ordinal = {(d - lo).days for d in ep_days}
    in_range = [((d - lo).days, n) for d, n in edits.items() if lo <= d <= hi]

    def touched(shift):
        moved = {(x + shift) % span for x in ordinal}
        return sum(n for o, n in in_range if o in moved)

    def days(shift):
        moved = {(x + shift) % span for x in ordinal}
        return sum(1 for o, _ in in_range if o in moved)

    random.seed(seed)
    shifts = random.sample(range(1, span), min(trials, span - 1))
    return {
        "span": (lo, hi),
        "episode_days": len(ep_days),
        "episodes": len(rows),
        "stories_obs": touched(0),
        "stories_null": sorted(touched(k) for k in shifts),
        "days_obs": days(0),
        "days_null": sorted(days(k) for k in shifts),
    }


def broadcast(rows, index_path):
    """Story titles that appear inside an episode title.

    The statistical join says the two calendars align; this says which stories
    were actually on air, which is the thing four sessions of timestamp
    clustering could not get at. Matching is substring-on-lowercase with a
    length floor, so it is conservative: it will miss any episode that renamed
    the story and any story whose title is too short to be distinctive.
    """
    titles = set()
    for line in open(index_path):
        parts = line.rstrip("\n").split("\t")
        if len(parts) > 3 and parts[3]:
            titles.add(re.sub(r"\s*\(\d+\)$", "", parts[3]).lower())
    titles = {t for t in titles if len(t) > 14}
    hits = collections.defaultdict(list)
    for d, _, ep in rows:
        low = ep.lower()
        for story in titles:
            if story in low:
                hits[story].append((d, ep))
                break
    return hits


def coverage(rows, meta_path):
    """Interval coverage -- the right statistic once you know how stories are kept.

    Endorphin keeps two kinds of story. Some series (`The Dork Forest`,
    `Sydney Bing RE:Sequences`) are **appended**: every new episode goes into one
    file so the context keeps building. Others (`Random Conspiracy Generator`)
    are one-offs, a fresh file each time.

    That wrecks day-level matching. An appended series carries thousands of
    blocks and exactly one `last_updated_at`, so twenty-seven broadcasts collapse
    to a single date -- and the stories most often on air are the ones the join
    can least see. Interval coverage asks the answerable question instead: does
    the broadcast fall inside the story's life?
    """
    by_stem = collections.defaultdict(list)
    for line in open(meta_path):
        r = json.loads(line)
        stem = re.sub(r"\s*\(\d+\)$", "", r["title"]).lower()
        by_stem[stem].append((
            datetime.datetime.fromtimestamp(
                r["created_at"], datetime.timezone.utc).date(),
            datetime.datetime.fromtimestamp(
                r["last_updated_at"], datetime.timezone.utc).date(),
            r["n_blocks"]))

    out = []
    for stem, forks in by_stem.items():
        if len(stem) <= 14:
            continue
        eps = [d for d, _, ep in rows if stem in ep.lower()]
        if not eps:
            continue
        lo = min(c for c, _, _ in forks)
        hi = max(u for _, u, _ in forks)
        inside = sum(1 for d in eps if lo <= d <= hi)
        out.append((stem, len(eps), inside, lo, hi,
                    max(b for _, _, b in forks),
                    len({u for _, u, _ in forks})))
    return sorted(out, key=lambda r: -r[1])


def shape(meta_path):
    """The append/one-off split, as block count against distinct edit-days."""
    by_stem = collections.defaultdict(list)
    for line in open(meta_path):
        r = json.loads(line)
        stem = re.sub(r"\s*\(\d+\)$", "", r["title"]).lower()
        by_stem[stem].append((
            datetime.datetime.fromtimestamp(
                r["created_at"], datetime.timezone.utc).date(),
            datetime.datetime.fromtimestamp(
                r["last_updated_at"], datetime.timezone.utc).date(),
            r["n_blocks"]))
    buckets = {"appended (>=1000 blocks)": [], "one-off (<200 blocks)": []}
    for forks in by_stem.values():
        blocks = max(b for _, _, b in forks)
        span = (max(u for _, u, _ in forks) - min(c for c, _, _ in forks)).days
        days = len({u for _, u, _ in forks})
        key = ("appended (>=1000 blocks)" if blocks >= 1000
               else "one-off (<200 blocks)" if blocks < 200 else None)
        if key:
            buckets[key].append((span, blocks, days))
    return buckets


def report(r):
    def line(label, obs, null):
        mean = sum(null) / len(null)
        p = (sum(1 for x in null if x >= obs) + 1) / (len(null) + 1)
        return (f"{label}: observed {obs}, null mean {mean:.0f} "
                f"(95th {null[int(.95 * len(null))]}), "
                f"lift {obs / mean:.2f}x, p = {p:.4f}")
    lo, hi = r["span"]
    print(f"episodes {r['episodes']} across {r['episode_days']} broadcast days, "
          f"{lo} .. {hi}")
    print(line("stories touched on a broadcast day", r["stories_obs"],
               r["stories_null"]))
    print(line("edit-days that were broadcast days", r["days_obs"],
               r["days_null"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shots", help="directory of dashboard screenshots")
    ap.add_argument("--out", type=pathlib.Path, help="write the episode index")
    ap.add_argument("--join", help="stories.jsonl or data/stories_meta.jsonl")
    ap.add_argument("--titles", help="data/INDEX.tsv -- which stories went to air")
    ap.add_argument("--coverage", help="data/stories_meta.jsonl -- interval coverage")
    args = ap.parse_args()

    rows = episodes(args.shots)
    if not rows:
        sys.exit("no episode rows recovered -- is tesseract installed?")
    print(f"{len(rows)} episodes recovered", file=sys.stderr)
    if args.out:
        args.out.write_text(
            "".join(f"{d}\t{dur}\t{t}\n" for d, dur, t in rows), encoding="utf-8")
    if args.join:
        report(join(rows, args.join))
    if args.titles:
        hits = broadcast(rows, args.titles)
        print(f"\n{len(hits)} stories identifiable in episode titles "
              f"({sum(len(v) for v in hits.values())} episodes):")
        for story in sorted(hits, key=lambda s: hits[s][0][0]):
            eps = hits[story]
            print(f"  {eps[0][0]} .. {eps[-1][0]}  x{len(eps):<3} {story}")
    if args.coverage:
        import statistics
        print("\nhow stories are kept (block count vs distinct edit-days):")
        for name, v in shape(args.coverage).items():
            if not v:
                continue
            print(f"  {name:26} n={len(v):4} median span "
                  f"{statistics.median(x[0] for x in v):5.0f}d  median edit-days "
                  f"{statistics.median(x[2] for x in v):.0f}")
        cov = coverage(rows, args.coverage)
        tot = sum(c[1] for c in cov)
        ins = sum(c[2] for c in cov)
        print(f"\ninterval coverage: {ins}/{tot} broadcasts fall inside their "
              f"story's life ({100 * ins / tot:.0f}%)")
        print(f"  {'story':44} {'eps':>4} {'in':>4} {'blocks':>7} {'edit-days':>10}")
        for stem, n, inside, lo, hi, blocks, days in cov:
            print(f"  {stem[:42]:44} {n:4} {inside:4} {blocks:7} {days:10}")


if __name__ == "__main__":
    main()
