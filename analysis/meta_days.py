#!/usr/bin/env python3
"""meta_days.py — per-day activity counts for the Meta archive.

Reads the Facebook and Instagram corpora and writes data/META_DAYS.tsv:
one row per (date, source) with posts and videos, mirroring the no-header,
date-first shape of data/TWEET_DAYS.tsv.

Dates are America/New_York calendar days (the corpora already carry
created_at_local in the user's timezone).
"""
import json, sys, collections
from pathlib import Path

FB = Path.home() / "workspace/meta-corpus/facebook/corpus.jsonl"
IG = Path.home() / "workspace/meta-corpus/instagram/gallegos.devon/corpus.jsonl"

counts = collections.defaultdict(lambda: [0, 0])  # (date, source) -> [posts, videos]

for path, source in ((FB, "fb"), (IG, "ig")):
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            local = d.get("created_at_local") or ""
            day = local.split("T")[0].split(" ")[0]
            if not day:
                continue
            video = bool(d.get("has_video")) or str(d.get("type", "")).upper() in ("REEL", "STORY")
            counts[(day, source)][0] += 1
            counts[(day, source)][1] += 1 if video else 0

rows = sorted(counts.items())
out = Path(__file__).resolve().parent.parent / "data" / "META_DAYS.tsv"
with open(out, "w") as fh:
    for (day, source), (posts, videos) in rows:
        fh.write(f"{day}\t{source}\t{posts}\t{videos}\n")
print(f"wrote {len(rows)} rows -> {out}", file=sys.stderr)
tot_fb = sum(p for (d, s), (p, v) in rows if s == "fb")
tot_ig = sum(p for (d, s), (p, v) in rows if s == "ig")
print(f"fb rows: {tot_fb} posts, ig rows: {tot_ig} records", file=sys.stderr)
