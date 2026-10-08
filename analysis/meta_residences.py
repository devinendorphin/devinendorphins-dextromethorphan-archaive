#!/usr/bin/env python3
"""meta_residences.py — residence/move/location mention candidates.

Prints every corpus record whose text matches a residence-related pattern,
with date and URL, for manual curation in META_RESIDENCES.md. Matching is
deliberately broad (recall over precision); the writeup keeps only
evidence-backed claims and says "uncertain" where it is uncertain.

Patterns: explicit move language, "living in", apartment/roommates, city and
borough names that appear in the corpus, check-in phrasing.
"""
import json, re, sys
from pathlib import Path

FB = Path.home() / "workspace/meta-corpus/facebook/corpus.jsonl"
IG = Path.home() / "workspace/meta-corpus/instagram/gallegos.devon/corpus.jsonl"

MOVE = re.compile(r"\b(mov(?:e|ed|ing)|relocat|new (?:apartment|place|crib|pad|home)|"
                  r"just moved|moving to|moving out|moving back|lease|landlord|"
                  r"roommate|apartment|my place|living in|living at|live in|"
                  r"back in|now in|in nyc|in brooklyn|in manhattan|in queens|"
                  r"in los angeles|in la\b|california|downey)\b", re.I)

PLACES = re.compile(r"\b(brooklyn|manhattan|queens|bronx|staten island|harlem|"
                    r"williamsburg|bushwick|bed-stuy|bed stuy|park slope|"
                    r"los angeles|\bLA\b|hollywood|silver ?lake|echo park|"
                    r"downey|usc|columbia|new york|nyc)\b", re.I)

seen = set()
hits = 0
for path, src in ((FB, "fb"), (IG, "ig")):
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            text = d.get("text") or d.get("caption") or ""
            if not text:
                continue
            m1 = MOVE.search(text); m2 = PLACES.search(text)
            if not (m1 or m2):
                continue
            if text in seen:
                continue
            seen.add(text)
            hits += 1
            local = d.get("created_at_local", "")
            print(f"--- {local} [{src}] {d.get('url','')}")
            print(text[:600].replace("\n", " "))
            print()
print(f"\n{hits} candidate mentions printed", file=sys.stderr)
