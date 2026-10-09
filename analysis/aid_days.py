#!/usr/bin/env python3
"""AI Dungeon actions per day, from the Drive mirror of the 2026-08-10 export.

Why this exists: the archive's start date (2020-12-07) came from a search for one
adventure, not from a scan of all 888. This reads every adventure's raw.json and
counts timestamped actions per UTC day. Output is dates and counts only -- no
text, no titles -- the same rule as every other file in data/.

Usage: aid_days.py CACHE_DIR [--fetch] > data/AID_DAYS.tsv
  --fetch  download each adventure's raw.json from the Drive mirror into
           CACHE_DIR first (~1,800 requests; cached files are skipped).
           CACHE_DIR must be outside the repo.
"""
import collections
import concurrent.futures as cf
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import fetch_export  # noqa: E402

ADVENTURES = "1ZHt_N3irjHmD6LNO7PpqfRA-u02yZ_Tr"   # exports/adventures/ on Drive


def fetch(cache):
    cache.mkdir(parents=True, exist_ok=True)

    def one(item):
        fid, name = item
        dest = cache / (name + ".json")
        if dest.exists() and dest.stat().st_size > 0:
            return
        raw = [x for x in fetch_export.list_folder(fid) if x[1] == "raw.json"]
        if not raw:
            print(f"no raw.json: {name}", file=sys.stderr)
            return
        subprocess.run(["curl", "-sL", "--retry", "3", "-o", str(dest),
                        f"https://drive.usercontent.google.com/download?id={raw[0][0]}"
                        "&export=download&confirm=t"], check=True)

    with cf.ThreadPoolExecutor(12) as ex:
        list(ex.map(one, fetch_export.list_folder(ADVENTURES)))


def main():
    cache = pathlib.Path(sys.argv[1])
    if "--fetch" in sys.argv:
        fetch(cache)
    days = collections.Counter()
    for p in sorted(cache.glob("*.json")):
        for a in json.load(open(p))["actionWindow"]:
            if a.get("createdAt"):
                days[a["createdAt"][:10]] += 1
    for d in sorted(days):
        print(f"{d}\t{days[d]}")


if __name__ == "__main__":
    main()
