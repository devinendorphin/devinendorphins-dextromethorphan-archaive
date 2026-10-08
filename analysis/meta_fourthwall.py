#!/usr/bin/env python3
"""meta_fourthwall.py — fourth-wall address candidates.

Inclusion rule (stated in META_FOURTHWALL.md): a record qualifies if the
addressed audience *cannot be the platform's present audience* — future
readers, posterity, the archive, the algorithm/surveillance apparatus named
as such, anticipated AI/analyst readers, "whoever reads this in [year]",
or the author speaking about the post as an object that will outlive the
moment.

Prints candidates with date and URL for manual curation; near-misses are
printed in a separate section and explained in the writeup.
"""
import json, re, sys
from pathlib import Path

FB = Path.home() / "workspace/meta-corpus/facebook/corpus.jsonl"
IG = Path.home() / "workspace/meta-corpus/instagram/gallegos.devon/corpus.jsonl"

STRONG = re.compile(
    r"(future|posterity|whoever.{0,40}(read|find|see)|dear future|"
    r"years from now|decades from now|when (i|we).{0,20} (am|are) (dead|gone)|"
    r"for the record|on the record|this (post|video|reel) will|"
    r"algorithm|surveillance|being watched|they.{0,20}(watch|track|monitor|scrap)|"
    r"\bAI\b.{0,30}(read|analy|train)|agents?.{0,30}(read|analy)|"
    r"training data|language model|to the (future|archive|historians?)|"
    r"archived|for (the )?archive|someone.{0,30}analyz|retroactiv|"
    r"dear (algorithm|mark|zuckerberg|meta)|hey (algorithm|siri|alexa)|"
    r"note to self|note to future|time capsule|"
    r"if you.{0,30}reading this|when you read this|"
    r"scraped|data broker|nsa|fbi.{0,20}watch|camera.{0,20}(watch|track))",
    re.I)

NEAR = re.compile(
    r"(the (internet|web) (never |will )?(forget|remember)|"
    r"this is (going )?on (the |my )(record|internet)|"
    r"screensh?ot|receipts|deleting (this|it)|"
    r"meta.{0,20}(knows|sees)|facebook.{0,20}(knows|sees))",
    re.I)

strong, near = [], []
seen = set()
for path, src in ((FB, "fb"), (IG, "ig")):
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            text = d.get("text") or d.get("caption") or ""
            if not text or text in seen:
                continue
            seen.add(text)
            rec = (d.get("created_at_local",""), src, d.get("url",""), text)
            if STRONG.search(text):
                strong.append(rec)
            elif NEAR.search(text):
                near.append(rec)

def dump(title, rows):
    print(f"===== {title} ({len(rows)}) =====")
    for local, src, url, text in sorted(rows):
        print(f"--- {local} [{src}] {url}")
        print(text[:700].replace("\n"," "))
        print()

dump("STRONG candidates", strong)
dump("NEAR-MISS candidates", near)
print(f"{len(strong)} strong, {len(near)} near-miss", file=sys.stderr)
