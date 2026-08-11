#!/usr/bin/env python3
"""Mirror and index Endorphin's Google AI Studio Drive folder.

The folder is link-readable, so enumeration goes through the same legacy
`embeddedfolderview` endpoint `fetch_export.py` uses: one request, no
pagination, no credential. AI Studio `.prompt` files download as plain JSON.

    python3 analysis/aistudio_export.py <folder-id> --out corpus/aistudio/
    python3 analysis/aistudio_export.py --report corpus/aistudio/

Schema (see AISTUDIO.md):

    {"runSettings": {temperature, model, topP, topK, maxOutputTokens,
                     safetySettings[], thinkingBudget, ...},
     "systemInstruction": {...},
     "chunkedPrompt": {"chunks": [{role, text, tokenCount,
                                   finishReason?, isThought?,
                                   branchParent?, branchChildren?, ...}]}}

Two traps, both of which will silently corrupt any measurement:

* `isThought` chunks carry `role: "model"` and no `finishReason`. They are the
  model's reasoning, not its output, and they are ~38% of all model text.
  `--report` excludes them; anything else must too.
* Files named `Branch of ...` are sibling documents, not depth within one.
  Group by the stripped stem before counting "stories".

Only files at or below --max-bytes are fetched, because a handful embed video
and run to 137 MB. The skipped ones are listed by `--report` so they are never
silently absent from a count.
"""

import argparse
import collections
import html
import json
import pathlib
import re
import statistics
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ENTRY = re.compile(r'id="entry-([-\w]{25,45})".*?flip-entry-title">([^<]*)<', re.S)
BRANCH = re.compile(r"^(?:Branch of )+")
DEFAULT_MAX_BYTES = 1_500_000


def curl(url, dest=None, timeout=120):
    cmd = ["curl", "-sSL", "--max-time", str(timeout), "--retry", "3", "--retry-delay", "2"]
    if dest:
        subprocess.run(cmd + ["-o", str(dest), url], check=False)
        return None
    return subprocess.run(cmd + [url], check=False, capture_output=True, text=True).stdout


def list_folder(folder_id):
    """(file_id, title) for every child. One request, no pagination."""
    page = curl(f"https://drive.google.com/embeddedfolderview?id={folder_id}#list")
    return [(fid, html.unescape(name)) for fid, name in ENTRY.findall(page or "")]


def download(fid, out_dir):
    dest = out_dir / f"{fid}.json"
    if dest.exists() and dest.stat().st_size > 200:
        return dest, True
    curl(
        f"https://drive.usercontent.google.com/download?id={fid}"
        "&export=download&confirm=t",
        dest,
    )
    return dest, False


def is_prompt(path):
    """A .prompt file is JSON with runSettings; everything else is an asset."""
    try:
        with open(path) as fh:
            return json.load(fh).get("runSettings") is not None
    except Exception:
        return False


def mirror(folder_id, out_dir, max_bytes, workers):
    out_dir.mkdir(parents=True, exist_ok=True)
    entries = list_folder(folder_id)
    print(f"{len(entries)} children in folder {folder_id}", file=sys.stderr)

    index = {}
    with ThreadPoolExecutor(workers) as pool:
        for (fid, title), (dest, cached) in zip(
            entries, pool.map(lambda e: download(e[0], out_dir), entries)
        ):
            size = dest.stat().st_size if dest.exists() else 0
            if size > max_bytes:
                dest.unlink(missing_ok=True)
                index[fid] = {"title": title, "skipped": size}
                continue
            if not is_prompt(dest):
                dest.unlink(missing_ok=True)
                continue
            index[fid] = {"title": title, "bytes": size}
    (out_dir / "INDEX.json").write_text(json.dumps(index, indent=1))
    kept = sum(1 for v in index.values() if "bytes" in v)
    print(f"{kept} prompt files kept, {len(index) - kept} over --max-bytes", file=sys.stderr)
    return index


def load(out_dir):
    for path in sorted(out_dir.glob("*.json")):
        if path.name == "INDEX.json":
            continue
        try:
            yield path.stem, json.load(open(path))
        except Exception:
            continue


def report(out_dir):
    index = {}
    if (out_dir / "INDEX.json").exists():
        index = json.loads((out_dir / "INDEX.json").read_text())
    docs = dict(load(out_dir))
    print(f"sessions parsed: {len(docs)}")

    temps = collections.Counter()
    models = collections.Counter()
    maxtok = collections.Counter()
    safety = collections.Counter()
    for d in docs.values():
        rs = d.get("runSettings") or {}
        temps[rs.get("temperature")] += 1
        models[rs.get("model")] += 1
        maxtok[rs.get("maxOutputTokens")] += 1
        for s in rs.get("safetySettings") or []:
            safety[(s.get("category"), s.get("threshold"))] += 1

    print("\ntemperature (the sweep does NOT transfer; expect a 1.0/2.0 switch)")
    for t, c in sorted(temps.items(), key=lambda kv: (kv[0] is None, kv[0])):
        print(f"  {c:5d}  {t}")
    print("\nmodel")
    for m, c in models.most_common(12):
        print(f"  {c:5d}  {m}")
    print("\nmaxOutputTokens")
    for m, c in maxtok.most_common(6):
        print(f"  {c:5d}  {m}")
    print("\nsafety thresholds")
    for (cat, thr), c in safety.most_common(10):
        print(f"  {c:5d}  {cat} = {thr}")

    fr = collections.Counter()
    user, model, thought = [], [], 0
    branch_chunks = 0
    modal = collections.Counter()
    for d in docs.values():
        for c in (d.get("chunkedPrompt") or {}).get("chunks") or []:
            text = c.get("text") or ""
            if c.get("isThought"):
                thought += len(text)
                continue
            if c.get("branchParent"):
                branch_chunks += 1
            for k in ("youtubeVideo", "driveVideo", "driveImage",
                      "driveDocument", "driveAudio", "grounding"):
                if c.get(k):
                    modal[k] += 1
            if c.get("role") == "user":
                user.append(len(text))
            elif c.get("role") == "model":
                model.append(len(text))
                fr[c.get("finishReason")] += 1

    print("\nfinishReason on model output (thinking chunks excluded)")
    total = sum(fr.values()) or 1
    for k, v in fr.most_common():
        print(f"  {v:6d} {100 * v / total:5.1f}%  {k}")
    print("  -- MAX_TOKENS is the truncation confound of FINDINGS.md §1c --")

    print(f"\nuser turns  n={len(user):5d}  median {statistics.median(user):6.0f} chars")
    print(f"model turns n={len(model):5d}  median {statistics.median(model):6.0f} chars")
    print(f"\nhuman {sum(user)/1e6:.2f}M  model {sum(model)/1e6:.2f}M  "
          f"thinking {thought/1e6:.2f}M chars")
    print(f"model:human ratio {sum(model)/max(sum(user),1):.2f}")
    print(f"thinking is {100*thought/max(sum(model)+thought,1):.0f}% of all model text "
          f"-- exclude it or every model-side number inflates")
    print(f"\nbranchParent chunks: {branch_chunks}   attachments: {modal.most_common()}")

    fams = collections.defaultdict(list)
    for fid, meta in index.items():
        fams[BRANCH.sub("", meta["title"]).strip()].append(fid)
    multi = {k: v for k, v in fams.items() if len(v) > 1}
    print(f"\ntitle stems {len(fams)}   families >1 member {len(multi)} "
          f"({100*len(multi)/max(len(fams),1):.0f}%; NovelAI is 53%)")

    same = diff = 0
    for members in multi.values():
        ts = [(docs[m].get("runSettings") or {}).get("temperature")
              for m in members if m in docs]
        ts = [t for t in ts if t is not None]
        if len(ts) < 2:
            continue
        if len(set(ts)) == 1:
            same += 1
        else:
            diff += 1
    print(f"  temperature identical across family: {same}   varies: {diff}")

    skipped = {k: v for k, v in index.items() if "skipped" in v}
    if skipped:
        print(f"\n{len(skipped)} files over --max-bytes, NOT counted above:")
        for fid, meta in sorted(skipped.items(),
                                key=lambda kv: -kv[1]["skipped"])[:12]:
            print(f"  {meta['skipped']/1e6:7.1f} MB  {meta['title']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder_id", nargs="?")
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("corpus/aistudio"))
    ap.add_argument("--report", type=pathlib.Path)
    ap.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()

    if args.report:
        report(args.report)
        return
    if not args.folder_id:
        ap.error("give a folder id to mirror, or --report <dir>")
    mirror(args.folder_id, args.out, args.max_bytes, args.workers)
    report(args.out)


if __name__ == "__main__":
    main()
