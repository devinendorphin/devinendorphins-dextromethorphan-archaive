#!/usr/bin/env python3
"""
Second-pass transcript collector for videos that had no captions via the YouTube API.
Uses yt-dlp with --ignore-no-formats-error to fetch auto-generated captions,
including age-restricted videos (uses Chrome cookies for auth).

Run after youtube_api_transcripts.py has completed:
  python3 fetch_auto_captions.py

Reads no_captions.json, skips already-saved files, rebuilds combined file when done.
Designed to run overnight — uses 10-20s delays per video to avoid 429s.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import random
from pathlib import Path


OUTPUT_DIR = Path("transcripts")
BROWSER = "chrome"  # change to "firefox" or "safari" if needed


def safe_filename(title: str, video_id: str) -> str:
    safe = re.sub(r'[^\w\s\-]', '', title).strip()
    safe = re.sub(r'\s+', '_', safe)[:80]
    return f"{safe}__{video_id}"


def format_eta(seconds: float) -> str:
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m}m" if h else (f"{m}m {s}s" if m else f"{s}s")


def parse_vtt(vtt_path: Path) -> str:
    raw = vtt_path.read_text(encoding="utf-8", errors="replace")
    text_lines = []
    for line in raw.splitlines():
        if any(line.startswith(x) for x in ("WEBVTT", "NOTE", "Kind:", "Language:")):
            continue
        if re.match(r"^\d+$", line.strip()) or "-->" in line:
            continue
        line = re.sub(r"<[^>]+>", "", line).strip()
        if line:
            text_lines.append(line)
    deduped = []
    for line in text_lines:
        if not deduped or line != deduped[-1]:
            deduped.append(line)
    return " ".join(deduped)


def fetch_via_ytdlp(video_id: str, tmp_dir: Path) -> str | None:
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--skip-download",
        "--write-auto-subs",
        "--write-subs",
        "--sub-langs", "en.*",
        "--sub-format", "vtt",
        "--convert-subs", "vtt",
        "--no-check-certificates",
        "--no-warnings",
        "--ignore-no-formats-error",
        "--cookies-from-browser", BROWSER,
        "-o", str(tmp_dir / "%(id)s.%(ext)s"),
        f"https://www.youtube.com/watch?v={video_id}",
    ]

    for attempt in range(3):
        result = subprocess.run(cmd, capture_output=True, text=True)
        if "429" in result.stderr or "Too Many Requests" in result.stderr:
            wait = (attempt + 1) * 300  # 5min, 10min, 15min
            print(f"\n  rate-limited — sleeping {wait//60}min...", end=" ", flush=True)
            time.sleep(wait)
            continue
        break

    for vtt_file in tmp_dir.glob(f"{video_id}*.vtt"):
        text = parse_vtt(vtt_file)
        vtt_file.unlink()
        if text:
            return text
    return None


def rebuild_combined():
    all_files = list(OUTPUT_DIR.glob("*__*.txt"))
    combined = OUTPUT_DIR / "ALL_TRANSCRIPTS_COMBINED.txt"

    index_path = OUTPUT_DIR / "video_index.json"
    id_to_date = {}
    if index_path.exists():
        for v in json.loads(index_path.read_text()):
            id_to_date[v["id"]] = v.get("upload_date", "")

    def file_date(p: Path) -> str:
        return id_to_date.get(p.stem.split("__")[-1], "")

    all_files.sort(key=file_date)

    with combined.open("w", encoding="utf-8") as f:
        f.write("@glubose YouTube Channel — All Transcripts\n")
        f.write(f"{'='*60}\n")
        f.write(f"Transcript files: {len(all_files)}\n")
        f.write(f"{'='*60}\n\n")
        for p in all_files:
            f.write(f"\n{'='*60}\n")
            f.write(p.read_text(encoding="utf-8"))
            f.write("\n")

    print(f"Combined file rebuilt: {combined}  ({len(all_files)} transcripts)")


def run():
    no_captions_path = OUTPUT_DIR / "no_captions.json"
    if not no_captions_path.exists():
        print("no_captions.json not found — run youtube_api_transcripts.py first.")
        return

    videos = json.loads(no_captions_path.read_text())
    print(f"Attempting yt-dlp auto-captions for {len(videos)} videos...")
    print("Using conservative delays (10-20s/video) — designed to run overnight.\n")

    tmp_dir = OUTPUT_DIR / "_tmp"
    tmp_dir.mkdir(exist_ok=True)

    results = []
    still_failed = []
    times = []

    for i, video in enumerate(videos, 1):
        vid_id = video["id"]
        title = video["title"]
        date = video.get("upload_date", "")

        filename = safe_filename(title, vid_id) + ".txt"
        out_path = OUTPUT_DIR / filename

        eta = f"  ETA {format_eta(sum(times)/len(times) * (len(videos)-i))}" if times else ""

        if out_path.exists():
            print(f"[{i}/{len(videos)}]{eta}  SKIP  {title}")
            results.append({**video, "transcript_file": filename})
            continue

        print(f"[{i}/{len(videos)}]{eta}  {title}", end="  ", flush=True)
        t0 = time.monotonic()

        text = fetch_via_ytdlp(vid_id, tmp_dir)

        if text:
            header = f"TITLE: {title}\nVIDEO ID: {vid_id}\nURL: {video['url']}\nDATE: {date}\n\n"
            out_path.write_text(header + text, encoding="utf-8")
            print(f"OK ({len(text)} chars)")
            results.append({**video, "transcript_file": filename, "char_count": len(text)})
        else:
            print("NO TRANSCRIPT")
            still_failed.append(video)

        times.append(time.monotonic() - t0)

        # Conservative delay — 10-20s between requests to stay under rate limits
        time.sleep(random.uniform(10.0, 20.0))

    # Clean up tmp
    try:
        tmp_dir.rmdir()
    except OSError:
        pass

    print(f"\nDone: {len(results)} new transcripts, {len(still_failed)} still no transcript.")

    if still_failed:
        (OUTPUT_DIR / "no_transcript_final.json").write_text(json.dumps(still_failed, indent=2))
        print(f"Remaining failures saved to: transcripts/no_transcript_final.json")

    rebuild_combined()


if __name__ == "__main__":
    run()
