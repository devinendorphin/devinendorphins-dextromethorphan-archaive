#!/usr/bin/env python3
"""Render one story's surviving branch as a turn-by-turn trace.

Everything else in `analysis/` aggregates. This does the opposite: it takes a
single story and lays out the live path in order, marked by who wrote each
block, so a session can be read as the sequence of moves it was.

    python3 analysis/trace.py corpus/json/SOME_STORY.json --stats
    python3 analysis/trace.py corpus/json/SOME_STORY.json --transcript --width 200

`--stats` prints the shape: run-length structure, where the author intervened,
how the turn sizes move over the session. `--transcript` prints the text.
"""

import argparse
import datetime as dt
import json
import pathlib
import re
from collections import Counter

TOKEN = re.compile(r"[A-Za-z][A-Za-z'-]*")
MARK = {"ai": "AI ", "user": ">>>", "edit": " ~ ", "prompt": "PRO", "root": "-  "}


def ts(x):
    if not x:
        return "?"
    return dt.datetime.fromtimestamp(
        x / 1000 if x > 1e12 else x, dt.timezone.utc
    ).strftime("%Y-%m-%d")


def load(path):
    d = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    content = d["content"]["data"]
    story = content["story"]
    blocks = story["datablocks"]

    live, i, seen = [], story.get("currentBlock"), set()
    while isinstance(i, int) and 0 <= i < len(blocks) and i not in seen:
        seen.add(i)
        live.append(i)
        i = blocks[i].get("prevBlock")
    live.reverse()

    rows = []
    for j in live:
        b = blocks[j]
        rows.append(
            {
                "index": j,
                "origin": b.get("origin") or "?",
                "text": (b.get("dataFragment") or {}).get("data") or "",
            }
        )
    return d, content, rows


def runs_of(rows):
    """(origin, count, total_chars) for each consecutive same-origin stretch."""
    out = []
    for r in rows:
        kind = "ai" if r["origin"] == "ai" else "human"
        if out and out[-1][0] == kind:
            out[-1][1] += 1
            out[-1][2] += len(r["text"])
        else:
            out.append([kind, 1, len(r["text"])])
    return [tuple(x) for x in out]


def print_stats(d, content, rows):
    sm = d["story"]["data"]
    st = content["settings"]
    p = st.get("parameters", {})
    order = [o["id"] for o in p.get("order", []) if isinstance(o, dict) and o.get("enabled")]

    print(f"title      {sm.get('title')}")
    print(f"created    {ts(sm.get('createdAt'))}   last edited {ts(d['story'].get('lastUpdatedAt'))}")
    print(f"model      {st.get('model')}   preset {st.get('preset')}   module {st.get('prefix')}")
    print(
        f"sampling   temp {p.get('temperature')}  max_length {p.get('max_length')}  "
        f"top_k {p.get('top_k')}  tfs {p.get('tail_free_sampling')}  "
        f"typical_p {p.get('typical_p')}"
    )
    print(f"order      {' > '.join(order)}")
    ctx = content.get("context") or []
    if ctx:
        print(f"memory     {len(ctx[0].get('text') or '')} chars"
              + (f"   author's note {len(ctx[1].get('text') or '')} chars" if len(ctx) > 1 else ""))
    print()

    org = Counter(r["origin"] for r in rows)
    ai_chars = sum(len(r["text"]) for r in rows if r["origin"] == "ai")
    hu_chars = sum(len(r["text"]) for r in rows if r["origin"] != "ai")
    print(f"live blocks {len(rows)}   {dict(org)}")
    print(f"characters  model {ai_chars:,}   human {hu_chars:,}   "
          f"ratio {ai_chars / max(1, hu_chars):.1f}:1")
    print()

    rs = runs_of(rows)
    ai_runs = [n for k, n, _ in rs if k == "ai"]
    print(f"generation runs: {len(ai_runs)}   longest {max(ai_runs) if ai_runs else 0}   "
          f"median {sorted(ai_runs)[len(ai_runs) // 2] if ai_runs else 0}")
    print()
    print("shape (each row is one unbroken stretch):")
    print(f"  {'who':6s} {'blocks':>6s} {'chars':>7s}  bar")
    for kind, n, ch in rs:
        bar = ("#" if kind == "ai" else "|") * min(60, n)
        print(f"  {kind:6s} {n:6d} {ch:7d}  {bar}")


def print_transcript(rows, width, limit):
    for k, r in enumerate(rows):
        if limit and k >= limit:
            print(f"... {len(rows) - limit} more blocks")
            break
        t = re.sub(r"\s+", " ", r["text"]).strip()
        if not t:
            t = "(empty)"
        print(f"{MARK.get(r['origin'], '?')} [{k:3d}] {t[:width]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("story", type=pathlib.Path)
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--transcript", action="store_true")
    ap.add_argument("--width", type=int, default=160)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    d, content, rows = load(args.story)
    if args.stats or not args.transcript:
        print_stats(d, content, rows)
    if args.transcript:
        print()
        print_transcript(rows, args.width, args.limit)


if __name__ == "__main__":
    main()
