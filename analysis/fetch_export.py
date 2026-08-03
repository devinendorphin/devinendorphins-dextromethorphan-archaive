#!/usr/bin/env python3
"""Mirror the `nai_export` Drive folder locally.

The Drive MCP connector cannot list this folder (it returns a generic
"Operation is not implemented" for any query scoped to its id, while the same
query shape works on sibling folders). The folder is link-readable, so this
enumerates it through the legacy `embeddedfolderview` endpoint, which returns
the whole child list as plain HTML in one request, and then downloads each file.

    python3 analysis/fetch_export.py <folder-id> --out corpus/

Note the export is not perfectly clean: at least one file
(`New_Story__eQm-Fkr_ZGaaeaykmh5bu.json`) is truncated at 411 bytes *in Drive*,
so no download can repair it. `--check` reports those rather than retrying.
"""

import argparse
import html
import json
import pathlib
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ENTRY = re.compile(
    r'id="entry-([-\w]{25,45})".*?flip-entry-title">([^<]*)<', re.S
)


def curl(url, dest=None, timeout=120):
    cmd = ["curl", "-sSL", "--max-time", str(timeout), "--retry", "3", "--retry-delay", "2"]
    if dest:
        cmd += ["-o", str(dest), url]
        subprocess.run(cmd, check=False)
        return None
    cmd.append(url)
    return subprocess.run(cmd, check=False, capture_output=True, text=True).stdout


def list_folder(folder_id):
    """(file_id, name) for every child. One request, no pagination."""
    page = curl(f"https://drive.google.com/embeddedfolderview?id={folder_id}#list")
    return [(fid, html.unescape(name)) for fid, name in ENTRY.findall(page or "")]


def download(fid, name, out_dir):
    dest = out_dir / name
    if dest.exists() and dest.stat().st_size > 0:
        return None
    curl(
        f"https://drive.usercontent.google.com/download?id={fid}"
        "&export=download&confirm=t",
        dest,
    )
    return dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder_id")
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("corpus"))
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--check", action="store_true", help="validate JSON after download")
    args = ap.parse_args()

    entries = list_folder(args.folder_id)
    if not entries:
        sys.exit("no entries -- is the folder link-readable?")
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "MANIFEST.tsv").write_text(
        "".join(f"{f}\t{n}\n" for f, n in entries), encoding="utf-8"
    )
    print(f"{len(entries)} entries")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(lambda e: download(e[0], e[1], args.out), entries))

    if args.check:
        bad = []
        for _, name in entries:
            p = args.out / name
            if not name.endswith(".json"):
                continue
            try:
                json.loads(p.read_text(encoding="utf-8", errors="replace"))
            except Exception as exc:  # noqa: BLE001
                bad.append(f"{name}\t{p.stat().st_size if p.exists() else 0}B\t{exc}")
        if bad:
            print(f"{len(bad)} unreadable:", *bad, sep="\n  ")
        else:
            print("all JSON parsed")


if __name__ == "__main__":
    main()
