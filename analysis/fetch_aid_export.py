#!/usr/bin/env python3
"""Mirror the `aid-export` Drive folder locally, recursively.

`fetch_export.py` next door handles the NovelAI export, which is one flat folder
of ~2,000 files. The AI Dungeon export is a *tree*: `adventures/` and
`scenarios/` each hold one folder per item (`<shortId>__<slug>/`), and each of
those holds `raw.json`, `story.md`, and sometimes a `scripts/` folder. So a
mirror is ~1,057 folder listings plus ~2,200 downloads rather than one listing.

    python3 analysis/fetch_aid_export.py 10Sg5PJ-sfOSP8T_HFDPlEtnVxX5G5-Dq --out exports/

`--only raw` skips `story.md` and the scripts, which halves the request count
when all you need is the data (`story.md` is rendered *from* `raw.json`, so it
carries nothing the JSON does not).

Same access route as `fetch_export.py`: the folder is link-readable and the
legacy `embeddedfolderview` endpoint returns a whole child list as HTML in one
request. Folders and files are told apart by the `href` each entry carries.
"""

import argparse
import html
import pathlib
import re
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

# An entry's id, then everything up to its title. The href in between says
# whether it is a file (/file/d/) or a folder (/drive/folders/).
ENTRY = re.compile(r'id="entry-([-\w]{25,45})"(.*?)flip-entry-title">([^<]*)<', re.S)

_print_lock = threading.Lock()


def curl(url, dest=None, timeout=120):
    cmd = ["curl", "-sSL", "--max-time", str(timeout), "--retry", "3", "--retry-delay", "2"]
    if dest:
        subprocess.run(cmd + ["-o", str(dest), url], check=False)
        return None
    return subprocess.run(cmd + [url], check=False, capture_output=True, text=True).stdout


def list_folder(folder_id):
    """[(id, name, is_dir)] for every child. One request, no pagination."""
    page = curl(f"https://drive.google.com/embeddedfolderview?id={folder_id}#list") or ""
    out = []
    for fid, mid, name in ENTRY.findall(page):
        out.append((fid, html.unescape(name), "/drive/folders/" in mid))
    return out


def download(fid, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    curl(
        f"https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t",
        dest,
    )


def mirror_item(item, out_root, only_raw, counter):
    """Mirror one `<shortId>__<slug>/` folder."""
    fid, name, _ = item
    dest_dir = out_root / name
    got = 0
    for cid, cname, is_dir in list_folder(fid):
        if is_dir:
            if only_raw:
                continue
            for sid, sname, _ in list_folder(cid):
                download(sid, dest_dir / cname / sname)
                got += 1
        else:
            if only_raw and cname != "raw.json":
                continue
            download(cid, dest_dir / cname)
            got += 1
    with _print_lock:
        counter[0] += 1
        if counter[0] % 50 == 0:
            print(f"  {counter[0]} items", file=sys.stderr, flush=True)
    return name, got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder_id")
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("exports"))
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--only", choices=["raw", "all"], default="all")
    args = ap.parse_args()

    top = list_folder(args.folder_id)
    if not top:
        sys.exit("no entries -- is the folder link-readable?")
    args.out.mkdir(parents=True, exist_ok=True)

    only_raw = args.only == "raw"
    counter = [0]
    for fid, name, is_dir in top:
        if not is_dir:
            download(fid, args.out / name)
            continue
        items = list_folder(fid)
        print(f"{name}: {len(items)} items", file=sys.stderr, flush=True)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            list(pool.map(
                lambda it: mirror_item(it, args.out / name, only_raw, counter), items
            ))

    files = sum(1 for _ in args.out.rglob("*") if _.is_file())
    print(f"{files} files under {args.out}")


if __name__ == "__main__":
    main()
