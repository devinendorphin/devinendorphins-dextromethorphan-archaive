#!/usr/bin/env python3
"""Build a per-item index of the AI Dungeon export, and report on it.

    python3 analysis/aid_index.py --exports exports --out data/AID_INDEX.tsv

The NovelAI side has `data/stories_meta.jsonl`; this is its opposite number, and
it is much thinner because the record is. AI Dungeon stores no sampler settings,
no model name and no branch structure, so everything here is derived from the
action list: dates come from action `createdAt` (an adventure carries no
creation timestamp of its own), and the human/model split comes from action
`type` — `continue` is the model, `story` / `do` / `say` / `start` are the
author.

Rules carried over from the NovelAI side that still apply:

- **Never group by item id.** AI Dungeon's "Copy of ..." works like NovelAI's
  duplicate, so the same text lives under many shortIds. `--dupes` groups by
  first-action text instead.
- **Do not read `undoneAt` as a rejection measure without checking it is ever
  set.** `--report` prints its corpus-wide count first, for exactly that reason.
"""

import argparse
import collections
import csv
import glob
import json
import os
import pathlib
import re
import statistics
import sys

HUMAN_TYPES = {"story", "do", "say", "start"}
MODEL_TYPES = {"continue"}


def iso_day(ts):
    return (ts or "")[:10]


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:  # noqa: BLE001
        print(f"unreadable: {path}: {exc}", file=sys.stderr)
        return None


def item_row(path, d):
    aw = d.get("actionWindow") or []
    stamps = sorted(a["createdAt"] for a in aw if a.get("createdAt"))
    human = [a for a in aw if a.get("type") in HUMAN_TYPES]
    model = [a for a in aw if a.get("type") in MODEL_TYPES]
    tlen = lambda xs: sum(len(a.get("text") or "") for a in xs)  # noqa: E731
    folder = pathlib.Path(path).parent
    scripts = sorted(p.name for p in (folder / "scripts").glob("*")) if (folder / "scripts").is_dir() else []
    types = collections.Counter(a.get("type") for a in aw)
    return {
        "shortId": d.get("shortId") or "",
        "type": d.get("contentType") or "",
        "title": (d.get("title") or "").replace("\t", " ").strip(),
        "slug": folder.name,
        "scenarioId": d.get("scenarioId") or "",
        "actionCount": d.get("actionCount") if d.get("actionCount") is not None else "",
        "n_actions": len(aw),
        "n_human": len(human),
        "n_model": len(model),
        "human_chars": tlen(human),
        "model_chars": tlen(model),
        "n_undone": sum(1 for a in aw if a.get("undoneAt")),
        "n_deleted": sum(1 for a in aw if a.get("deletedAt")),
        "n_images": sum(1 for a in aw if a.get("imageUrl")),
        "first_at": stamps[0] if stamps else "",
        "last_at": stamps[-1] if stamps else "",
        "n_days": len({iso_day(s) for s in stamps}),
        "memory_chars": len(d.get("memory") or ""),
        "an_chars": len(d.get("authorsNote") or ""),
        "instr_chars": len((d.get("details") or {}).get("instructions") or "") if isinstance(d.get("details"), dict) else 0,
        "n_storycards": len(d.get("storyCards") or []),
        "tags": "|".join(d.get("tags") or []),
        "scripts": "|".join(scripts),
        "types": ";".join(f"{k}={v}" for k, v in sorted(types.items(), key=lambda kv: -kv[1])),
        "path": str(folder),
    }


def build(exports):
    rows = []
    for path in sorted(glob.glob(os.path.join(exports, "*", "*", "raw.json"))):
        d = load(path)
        if d is not None:
            rows.append(item_row(path, d))
    return rows


COLUMNS = [
    "shortId", "type", "title", "slug", "scenarioId", "actionCount", "n_actions",
    "n_human", "n_model", "human_chars", "model_chars", "n_undone", "n_deleted",
    "n_images", "first_at", "last_at", "n_days", "memory_chars", "an_chars",
    "instr_chars", "n_storycards", "tags", "scripts", "types", "path",
]


def write_tsv(rows, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def opening(d, n=400):
    """First action's text — the duplicate key. Titles lie; openings do not."""
    aw = sorted(
        (a for a in (d.get("actionWindow") or []) if a.get("createdAt")),
        key=lambda a: a["createdAt"],
    )
    return re.sub(r"\s+", " ", (aw[0].get("text") if aw else "") or "")[:n].strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exports", default="exports")
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("data/AID_INDEX.tsv"))
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    rows = build(args.exports)
    write_tsv(rows, args.out)
    print(f"{len(rows)} items -> {args.out}")

    if not args.report:
        return

    adv = [r for r in rows if r["type"] == "adventure"]
    acts = sum(r["n_actions"] for r in rows)
    print(f"\nactions: {acts:,}   undone: {sum(r['n_undone'] for r in rows):,}"
          f"   deleted: {sum(r['n_deleted'] for r in rows):,}")
    print(f"human chars: {sum(r['human_chars'] for r in rows):,}"
          f"   model chars: {sum(r['model_chars'] for r in rows):,}")

    dated = [r for r in rows if r["first_at"]]
    dated.sort(key=lambda r: r["first_at"])
    print(f"\nspan: {dated[0]['first_at']} .. {max(r['last_at'] for r in dated)}")
    by_month = collections.Counter(r["first_at"][:7] for r in dated)
    print("\nitems by month of first action:")
    for m in sorted(by_month):
        print(f"  {m}  {by_month[m]:4d}  {'#' * min(60, by_month[m])}")

    print("\nlongest by actions:")
    for r in sorted(rows, key=lambda r: -r["n_actions"])[:15]:
        print(f"  {r['n_actions']:5d}  {r['first_at'][:10]}  {r['title'][:60]}")

    with_scripts = [r for r in rows if r["scripts"]]
    print(f"\nitems with scripts: {len(with_scripts)}")
    print(f"items with memory: {sum(1 for r in rows if r['memory_chars'])}"
          f"   authorsNote: {sum(1 for r in rows if r['an_chars'])}"
          f"   storyCards: {sum(1 for r in rows if r['n_storycards'])}")


if __name__ == "__main__":
    main()
