#!/usr/bin/env python3
"""
Second-pass transcript collector for videos that had no captions via the YouTube API.
Uses youtube-transcript-api to fetch auto-generated captions.

Run after youtube_api_transcripts.py has completed:
  python3 fetch_auto_captions.py

If no_captions.json was lost or corrupted by an early IP-block exit, rebuild it:
  python3 fetch_auto_captions.py --rebuild

NOTE: If you get IpBlocked errors, your IP was temporarily banned by YouTube
from doing too many requests. Wait a few hours (or overnight) and try again.

Reads no_captions.json, skips already-saved files, rebuilds combined file when done.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import random
from pathlib import Path


OUTPUT_DIR = Path("transcripts")


def safe_filename(title: str, video_id: str) -> str:
    safe = re.sub(r'[^\w\s\-]', '', title).strip()
    safe = re.sub(r'\s+', '_', safe)[:80]
    return f"{safe}__{video_id}"


def format_eta(seconds: float) -> str:
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m}m" if h else (f"{m}m {s}s" if m else f"{s}s")


def fetch_transcript(video_id: str) -> tuple[str | None, str | None]:
    """Returns (text, error_type). error_type is None on success."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        try:
            transcript = api.fetch(video_id, languages=["en"])
        except Exception:
            listing = api.list(video_id)
            transcript = listing.find_generated_transcript(["en"]).fetch()
        return " ".join(s.text for s in transcript), None
    except Exception as e:
        error_type = type(e).__name__
        return None, error_type


def rebuild_combined():
    all_files = list(OUTPUT_DIR.glob("*__*.txt"))
    combined = OUTPUT_DIR / "ALL_TRANSCRIPTS_COMBINED.txt"

    index_path = OUTPUT_DIR / "video_index.json"
    id_to_date = {}
    if index_path.exists():
        for v in json.loads(index_path.read_text()):
            id_to_date[v["id"]] = v.get("upload_date", "")

    all_files.sort(key=lambda p: id_to_date.get(p.stem.split("__")[-1], ""))

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


def rebuild_no_captions():
    """Rebuild no_captions.json by scanning video_index.json for videos without .txt files."""
    index_path = OUTPUT_DIR / "video_index.json"
    if not index_path.exists():
        print("video_index.json not found — run youtube_api_transcripts.py first.")
        return

    all_videos = json.loads(index_path.read_text())
    missing = []
    for v in all_videos:
        filename = safe_filename(v["title"], v["id"]) + ".txt"
        if not (OUTPUT_DIR / filename).exists():
            missing.append(v)

    no_captions_path = OUTPUT_DIR / "no_captions.json"
    no_captions_path.write_text(json.dumps(missing, indent=2))
    have = len(all_videos) - len(missing)
    print(f"Rebuilt no_captions.json:")
    print(f"  {len(all_videos)} total videos")
    print(f"  {have} already have transcripts")
    print(f"  {len(missing)} still need fetching → written to no_captions.json")


def run():
    no_captions_path = OUTPUT_DIR / "no_captions.json"
    if not no_captions_path.exists():
        print("no_captions.json not found.")
        print("Run: python3 fetch_auto_captions.py --rebuild")
        return

    videos = json.loads(no_captions_path.read_text())
    print(f"Fetching auto-captions for {len(videos)} videos via youtube-transcript-api...\n")

    results, still_failed, times = [], [], []
    ip_blocked_count = 0

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

        text, error = fetch_transcript(vid_id)

        if text:
            header = f"TITLE: {title}\nVIDEO ID: {vid_id}\nURL: {video['url']}\nDATE: {date}\n\n"
            out_path.write_text(header + text, encoding="utf-8")
            print(f"OK ({len(text)} chars)")
            results.append({**video, "transcript_file": filename, "char_count": len(text)})
            ip_blocked_count = 0
        else:
            print(f"NO TRANSCRIPT ({error})")
            still_failed.append({**video, "error": error})
            if error in ("IpBlocked", "RequestBlocked"):
                ip_blocked_count += 1
                if ip_blocked_count >= 3:
                    print("\nIP is blocked — stopping early. Wait a few hours and run again.")
                    print("Progress is saved; it will resume from where it left off.")
                    # Preserve all videos not yet attempted so the next run picks them up
                    still_failed.extend(videos[i:])
                    break

        times.append(time.monotonic() - t0)
        time.sleep(random.uniform(1.5, 3.0))

    print(f"\nDone: {len(results)} new transcripts, {len(still_failed)} no transcript.")

    # Always write back — even an empty list means we finished everything
    (OUTPUT_DIR / "no_captions.json").write_text(json.dumps(still_failed, indent=2))
    print("no_captions.json updated with remaining videos.")

    rebuild_combined()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rebuild", action="store_true",
        help="Rebuild no_captions.json by scanning video_index.json vs existing .txt files. "
             "Use this if no_captions.json was lost or truncated by an early exit."
    )
    args = parser.parse_args()

    if args.rebuild:
        rebuild_no_captions()
    else:
        run()
