#!/usr/bin/env python3
"""
Second-pass transcript collector for videos that had no captions via the YouTube API.
Uses youtube-transcript-api to fetch auto-generated captions locally.

Run after youtube_api_transcripts.py has completed:
  python3 fetch_auto_captions.py

Reads no_captions.json from the transcripts/ folder and tries to fetch
auto-generated captions for each video. Skips any already saved.
"""

from __future__ import annotations

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


def fetch_transcript(video_id: str) -> str | None:
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        # Try English first, then any auto-generated language
        try:
            transcript = api.fetch(video_id, languages=["en"])
        except Exception:
            try:
                listing = api.list(video_id)
                transcript = listing.find_generated_transcript(["en"]).fetch()
            except Exception:
                return None
        return " ".join(snippet.text for snippet in transcript)
    except Exception:
        return None


def run():
    no_captions_path = OUTPUT_DIR / "no_captions.json"
    if not no_captions_path.exists():
        print("no_captions.json not found — run youtube_api_transcripts.py first.")
        return

    videos = json.loads(no_captions_path.read_text())
    print(f"Attempting auto-captions for {len(videos)} videos...")

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

        text = fetch_transcript(vid_id)

        if text:
            header = f"TITLE: {title}\nVIDEO ID: {vid_id}\nURL: {video['url']}\nDATE: {date}\n\n"
            out_path.write_text(header + text, encoding="utf-8")
            print(f"OK ({len(text)} chars)")
            results.append({**video, "transcript_file": filename, "char_count": len(text)})
        else:
            print("NO TRANSCRIPT")
            still_failed.append(video)

        times.append(time.monotonic() - t0)
        time.sleep(random.uniform(1.0, 2.5))

    print(f"\nDone: {len(results)} new transcripts, {len(still_failed)} still no transcript.")

    if still_failed:
        (OUTPUT_DIR / "no_transcript_final.json").write_text(
            json.dumps(still_failed, indent=2))
        print(f"Remaining failures: transcripts/no_transcript_final.json")

    # Rebuild the combined file to include new transcripts
    print("Rebuilding combined file...")
    all_files = sorted(OUTPUT_DIR.glob("*__*.txt"))
    combined = OUTPUT_DIR / "ALL_TRANSCRIPTS_COMBINED.txt"

    # Load video index for ordering
    index_path = OUTPUT_DIR / "video_index.json"
    if index_path.exists():
        index = json.loads(index_path.read_text())
        id_to_date = {v["id"]: v.get("upload_date", "") for v in index}
    else:
        id_to_date = {}

    def file_date(p: Path) -> str:
        vid_id = p.stem.split("__")[-1]
        return id_to_date.get(vid_id, "")

    all_files_sorted = sorted(all_files, key=file_date)

    with combined.open("w", encoding="utf-8") as f:
        f.write("@glubose YouTube Channel — All Transcripts\n")
        f.write(f"{'='*60}\n")
        f.write(f"Transcript files: {len(all_files_sorted)}\n")
        f.write(f"{'='*60}\n\n")
        for p in all_files_sorted:
            f.write(f"\n{'='*60}\n")
            f.write(p.read_text(encoding="utf-8"))
            f.write("\n")

    print(f"Combined file rebuilt: {combined}")
    print(f"  Total transcript files: {len(all_files_sorted)}")


if __name__ == "__main__":
    run()
