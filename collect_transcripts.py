#!/usr/bin/env python3
"""
Collects all transcripts from the @glubose YouTube channel.

Usage:
    python3 collect_transcripts.py [--cookies cookies.txt] [--output-dir transcripts]

Requirements:
    pip install yt-dlp youtube-transcript-api

Running from a cloud environment:
    You must supply a Netscape-format cookies.txt exported from a logged-in
    browser session (e.g. via the "Get cookies.txt LOCALLY" Chrome extension).
    Pass it with --cookies cookies.txt

Running locally:
    No cookies needed — just run the script directly.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path


CHANNEL_URL = "https://www.youtube.com/@glubose/videos"


def cookie_args(cookies_path: str | None, browser: str | None) -> list[str]:
    if cookies_path:
        return ["--cookies", cookies_path]
    if browser:
        return ["--cookies-from-browser", browser]
    return []


def get_video_list(cookies_path: str | None, browser: str | None) -> list[dict]:
    """Fetch the full list of videos from the channel using yt-dlp."""
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(id)s\t%(title)s\t%(upload_date)s\t%(duration)s",
        "--no-warnings",
        "--no-check-certificates",
        "--sleep-interval", "1",
        "--max-sleep-interval", "3",
    ]
    cmd += cookie_args(cookies_path, browser)
    cmd.append(CHANNEL_URL)

    print(f"Fetching video list from {CHANNEL_URL} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("yt-dlp error:", result.stderr[:500])
        sys.exit(1)

    videos = []
    for line in result.stdout.strip().splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            video_id = parts[0].strip()
            title = parts[1].strip() if len(parts) > 1 else "Unknown"
            date = parts[2].strip() if len(parts) > 2 else ""
            duration = parts[3].strip() if len(parts) > 3 else ""
            videos.append({
                "id": video_id,
                "title": title,
                "upload_date": date,
                "duration": duration,
                "url": f"https://www.youtube.com/watch?v={video_id}",
            })

    print(f"Found {len(videos)} videos.")
    return videos


def fetch_transcript_ytdlp(video_id: str, cookies_path: str | None, browser: str | None, tmp_dir: Path) -> str | None:
    """Download auto-generated subtitles via yt-dlp and parse them to plain text."""
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--write-auto-subs",
        "--write-subs",
        "--sub-langs", "en.*",
        "--sub-format", "vtt",
        "--convert-subs", "vtt",
        "--no-check-certificates",
        "--no-warnings",
        "--sleep-interval", "1",
        "--max-sleep-interval", "4",
        "-o", str(tmp_dir / "%(id)s.%(ext)s"),
    ]
    cmd += cookie_args(cookies_path, browser)
    cmd.append(f"https://www.youtube.com/watch?v={video_id}")

    subprocess.run(cmd, capture_output=True, text=True)

    # Find any .vtt file written for this video
    for vtt_file in tmp_dir.glob(f"{video_id}*.vtt"):
        text = parse_vtt(vtt_file)
        vtt_file.unlink()
        if text:
            return text
    return None


def fetch_transcript_api(video_id: str) -> str | None:
    """Fetch transcript via youtube-transcript-api (works locally, blocked on cloud)."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        # Try English first, then fall back to any available language
        try:
            transcript = api.fetch(video_id, languages=["en"])
        except Exception:
            listing = api.list(video_id)
            transcript = listing.find_generated_transcript(["en"]).fetch()
        return " ".join(snippet.text for snippet in transcript)
    except Exception as e:
        return None


def parse_vtt(vtt_path: Path) -> str:
    """Convert a VTT subtitle file to clean, deduplicated plain text."""
    raw = vtt_path.read_text(encoding="utf-8", errors="replace")

    # Strip VTT header and cue metadata
    lines = raw.splitlines()
    text_lines = []
    for line in lines:
        # Skip header, timestamps, cue numbers, NOTE blocks
        if line.startswith("WEBVTT") or line.startswith("NOTE") or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        if re.match(r"^\d+$", line.strip()):  # cue number
            continue
        if "-->" in line:  # timestamp line
            continue
        # Strip inline VTT tags like <00:00:01.000><c>word</c>
        line = re.sub(r"<[^>]+>", "", line)
        line = line.strip()
        if line:
            text_lines.append(line)

    # Deduplicate consecutive repeated lines (common in auto-captions)
    deduped = []
    for line in text_lines:
        if not deduped or line != deduped[-1]:
            deduped.append(line)

    return " ".join(deduped)


def safe_filename(title: str, video_id: str) -> str:
    """Make a filesystem-safe filename from a video title."""
    safe = re.sub(r'[^\w\s\-]', '', title).strip()
    safe = re.sub(r'\s+', '_', safe)[:80]
    return f"{safe}__{video_id}"


def format_eta(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m}m"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def collect_all_transcripts(cookies_path: str | None, browser: str | None, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir = output_dir / "_tmp"
    tmp_dir.mkdir(exist_ok=True)

    videos = get_video_list(cookies_path, browser)

    # Save video list as JSON index
    index_path = output_dir / "video_index.json"
    index_path.write_text(json.dumps(videos, indent=2), encoding="utf-8")
    print(f"Video index saved to {index_path}")

    results = []
    failed = []
    times = []  # per-video elapsed times for ETA

    for i, video in enumerate(videos, 1):
        vid_id = video["id"]
        title = video["title"]
        date = video.get("upload_date", "")

        # Resume: skip videos whose transcript file already exists
        existing_filename = safe_filename(title, vid_id) + ".txt"
        existing_path = output_dir / existing_filename
        if existing_path.exists():
            eta_str = ""
            if times:
                avg = sum(times) / len(times)
                remaining = len(videos) - i
                eta_str = f"  ETA {format_eta(avg * remaining)}"
            print(f"[{i}/{len(videos)}] SKIP (already done) {title}{eta_str}")
            results.append({**video, "transcript_file": existing_filename,
                            "char_count": existing_path.stat().st_size})
            continue

        eta_str = ""
        if times:
            avg = sum(times) / len(times)
            remaining = len(videos) - i
            eta_str = f"  ETA {format_eta(avg * remaining)}"

        print(f"[{i}/{len(videos)}]{eta_str}  {title} ({vid_id})", end="  ", flush=True)
        t0 = time.monotonic()

        # Try yt-dlp first (works with cookies in cloud), then API (works locally)
        text = fetch_transcript_ytdlp(vid_id, cookies_path, browser, tmp_dir)
        if not text:
            text = fetch_transcript_api(vid_id)

        if text:
            out_path = output_dir / existing_filename
            header = f"TITLE: {title}\nVIDEO ID: {vid_id}\nURL: {video['url']}\nDATE: {date}\n\n"
            out_path.write_text(header + text, encoding="utf-8")
            print(f"OK ({len(text)} chars)")
            results.append({**video, "transcript_file": existing_filename, "char_count": len(text)})
        else:
            print("NO TRANSCRIPT")
            failed.append(video)

        elapsed = time.monotonic() - t0
        times.append(elapsed)

        # Small extra pause on top of yt-dlp's own internal sleep
        time.sleep(random.uniform(0.5, 1.5))

    # Clean up tmp dir
    tmp_dir.rmdir() if not any(tmp_dir.iterdir()) else None

    # Build the combined gargantuan text
    combined_path = output_dir / "ALL_TRANSCRIPTS_COMBINED.txt"
    print(f"\nBuilding combined transcript file...")
    with combined_path.open("w", encoding="utf-8") as f:
        f.write(f"@glubose YouTube Channel — All Transcripts\n")
        f.write(f"{'='*60}\n")
        f.write(f"Total videos: {len(videos)} | With transcripts: {len(results)} | No transcript: {len(failed)}\n")
        f.write(f"{'='*60}\n\n")

        # Sort by upload date (oldest first)
        sorted_results = sorted(results, key=lambda v: v.get("upload_date", ""))
        for video in sorted_results:
            transcript_file = output_dir / video["transcript_file"]
            content = transcript_file.read_text(encoding="utf-8")
            f.write(f"\n{'='*60}\n")
            f.write(content)
            f.write("\n")

    print(f"Combined file saved: {combined_path}")
    print(f"  {len(results)} transcripts, {len(failed)} videos had no transcript")

    if failed:
        failed_path = output_dir / "no_transcript.json"
        failed_path.write_text(json.dumps(failed, indent=2), encoding="utf-8")
        print(f"  Videos without transcripts listed in: {failed_path}")

    return results, failed


def main():
    parser = argparse.ArgumentParser(description="Collect all @glubose YouTube transcripts")
    parser.add_argument("--cookies", metavar="cookies.txt",
                        help="Netscape-format cookies file")
    parser.add_argument("--browser", metavar="BROWSER",
                        help="Read cookies from browser: safari, chrome, firefox, etc.")
    parser.add_argument("--output-dir", default="transcripts",
                        help="Directory to save transcripts (default: transcripts/)")
    args = parser.parse_args()

    if not shutil_which("yt-dlp"):
        print("Error: yt-dlp not found. Install with: pip install yt-dlp")
        sys.exit(1)

    collect_all_transcripts(
        cookies_path=args.cookies,
        browser=args.browser,
        output_dir=Path(args.output_dir),
    )


def shutil_which(name):
    import shutil
    return shutil.which(name)


if __name__ == "__main__":
    main()
