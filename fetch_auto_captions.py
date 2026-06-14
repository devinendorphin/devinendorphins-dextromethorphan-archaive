#!/usr/bin/env python3
"""
Second-pass transcript collector for videos that had no captions via the YouTube API.
Uses youtube-transcript-api to fetch auto-generated captions.

Run after youtube_api_transcripts.py has completed:
  python3 fetch_auto_captions.py

If no_captions.json was lost or corrupted by an early IP-block exit, rebuild it:
  python3 fetch_auto_captions.py --rebuild

To skip Shorts, run mark_shorts.py first (one-time), then --rebuild:
  python3 mark_shorts.py
  python3 fetch_auto_captions.py --rebuild

One-time cleanup: move known-permanent failures out of no_captions.json:
  python3 fetch_auto_captions.py --purge-permanent

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
PERMANENTLY_FAILED_PATH = OUTPUT_DIR / "permanently_failed.json"

# Errors that will never succeed regardless of IP status or retry timing.
PERMANENT_ERRORS = {"TranscriptsDisabled", "VideoUnavailable"}

# VideoUnplayable is only permanent for specific reasons — check the reason string.
PERMANENT_REASONS = (
    "This video is private",
    "This live event will begin in a few moments",
    "This video has been removed",
    "no longer available",
    "has been removed by the user",
)


def is_permanent_failure(error: str | None, reason: str | None) -> bool:
    if error in PERMANENT_ERRORS:
        return True
    if error == "VideoUnplayable" and reason:
        return any(p.lower() in reason.lower() for p in PERMANENT_REASONS)
    return False


def safe_filename(title: str, video_id: str) -> str:
    safe = re.sub(r'[^\w\s\-]', '', title).strip()
    safe = re.sub(r'\s+', '_', safe)[:80]
    return f"{safe}__{video_id}"


def format_eta(seconds: float) -> str:
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m}m" if h else (f"{m}m {s}s" if m else f"{s}s")


def extract_reason(e: Exception) -> str | None:
    """Pull a short human-readable reason out of a youtube-transcript-api exception."""
    reason = getattr(e, "reason", None)
    if reason:
        return str(reason).strip()
    boilerplate = (
        "Could not retrieve", "This is most likely", "If you are sure",
        "request to YouTube", "Ip belonging to", "youtube-transcript-api",
        "https://", "For more information", "the video is no longer",
    )
    for line in str(e).splitlines():
        line = line.strip()
        if line and not any(line.startswith(b) for b in boilerplate):
            return line[:120]
    return None


def fetch_transcript(video_id: str) -> tuple[str | None, str | None, str | None]:
    """Returns (text, error_type, reason). error_type and reason are None on success."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        api = YouTubeTranscriptApi()
        try:
            transcript = api.fetch(video_id, languages=["en"])
        except Exception:
            listing = api.list(video_id)
            transcript = listing.find_generated_transcript(["en"]).fetch()
        return " ".join(s.text for s in transcript), None, None
    except Exception as e:
        error_type = type(e).__name__
        return None, error_type, extract_reason(e)


def load_permanently_failed() -> set[str]:
    """Return the set of video IDs already marked permanently failed."""
    if not PERMANENTLY_FAILED_PATH.exists():
        return set()
    return {v["id"] for v in json.loads(PERMANENTLY_FAILED_PATH.read_text())}


def append_permanently_failed(videos: list[dict]) -> None:
    """Add videos to permanently_failed.json, deduplicating by id."""
    existing: list[dict] = []
    if PERMANENTLY_FAILED_PATH.exists():
        existing = json.loads(PERMANENTLY_FAILED_PATH.read_text())
    seen = {v["id"] for v in existing}
    for v in videos:
        if v["id"] not in seen:
            existing.append(v)
            seen.add(v["id"])
    PERMANENTLY_FAILED_PATH.write_text(json.dumps(existing, indent=2))


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


def rebuild_no_captions(skip_shorts: bool = True):
    """Rebuild no_captions.json by scanning video_index.json for videos without .txt files."""
    index_path = OUTPUT_DIR / "video_index.json"
    if not index_path.exists():
        print("video_index.json not found — run youtube_api_transcripts.py first.")
        return

    all_videos = json.loads(index_path.read_text())
    has_short_marks = any("is_short" in v for v in all_videos)
    if skip_shorts and not has_short_marks:
        print("Note: video_index.json has no Shorts data — run mark_shorts.py first to enable filtering.")
        skip_shorts = False

    perm_ids = load_permanently_failed()

    missing, skipped_short, skipped_perm, already_have = [], 0, 0, 0
    for v in all_videos:
        filename = safe_filename(v["title"], v["id"]) + ".txt"
        if (OUTPUT_DIR / filename).exists():
            already_have += 1
            continue
        if v["id"] in perm_ids:
            skipped_perm += 1
            continue
        if skip_shorts and v.get("is_short", False):
            skipped_short += 1
            continue
        missing.append(v)

    no_captions_path = OUTPUT_DIR / "no_captions.json"
    no_captions_path.write_text(json.dumps(missing, indent=2))
    print(f"Rebuilt no_captions.json:")
    print(f"  {len(all_videos)} total videos")
    print(f"  {already_have} already have transcripts")
    if perm_ids:
        print(f"  {skipped_perm} skipped as permanently failed")
    if skip_shorts:
        print(f"  {skipped_short} skipped as Shorts")
    print(f"  {len(missing)} queued for fetching → written to no_captions.json")


def purge_permanent():
    """
    One-time cleanup: scan no_captions.json for known-permanent failures
    (from previous runs that recorded error/reason) and move them out to
    permanently_failed.json so they're never retried.
    """
    no_captions_path = OUTPUT_DIR / "no_captions.json"
    if not no_captions_path.exists():
        print("no_captions.json not found.")
        return

    videos = json.loads(no_captions_path.read_text())
    keep, permanent = [], []
    for v in videos:
        error = v.get("error")
        reason = v.get("reason")
        if error and is_permanent_failure(error, reason):
            permanent.append(v)
        else:
            keep.append(v)

    if not permanent:
        print("No permanent failures found in no_captions.json — nothing to purge.")
        return

    append_permanently_failed(permanent)
    no_captions_path.write_text(json.dumps(keep, indent=2))

    print(f"Purged {len(permanent)} permanent failures → {PERMANENTLY_FAILED_PATH}")
    print(f"  {len(keep)} videos remain in no_captions.json")
    # Show a breakdown of what was purged
    by_error: dict[str, int] = {}
    for v in permanent:
        key = v.get("error", "unknown")
        by_error[key] = by_error.get(key, 0) + 1
    for err, count in sorted(by_error.items(), key=lambda x: -x[1]):
        print(f"    {count:4d}  {err}")


def run(max_minutes: float | None = None):
    no_captions_path = OUTPUT_DIR / "no_captions.json"
    if not no_captions_path.exists():
        print("no_captions.json not found.")
        print("Run: python3 fetch_auto_captions.py --rebuild")
        return

    videos = json.loads(no_captions_path.read_text())
    cap_note = f"  (stopping after {format_eta(max_minutes * 60)})" if max_minutes else ""
    print(f"Fetching auto-captions for {len(videos)} videos via youtube-transcript-api...{cap_note}\n")

    results, still_failed, permanent_this_run, times = [], [], [], []
    ip_blocked_count = 0
    start = time.monotonic()
    deadline = start + max_minutes * 60 if max_minutes else None

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

        # Time cap: stop voluntarily before YouTube's rate limiter trips
        if deadline and time.monotonic() >= deadline:
            print(f"\nTime cap reached ({format_eta(max_minutes * 60)}) — stopping.")
            print("Progress is saved; it will resume from where it left off.")
            still_failed.extend(videos[i - 1:])
            break

        print(f"[{i}/{len(videos)}]{eta}  {title}", end="  ", flush=True)
        t0 = time.monotonic()

        text, error, reason = fetch_transcript(vid_id)

        if text:
            header = f"TITLE: {title}\nVIDEO ID: {vid_id}\nURL: {video['url']}\nDATE: {date}\n\n"
            out_path.write_text(header + text, encoding="utf-8")
            print(f"OK ({len(text)} chars)")
            results.append({**video, "transcript_file": filename, "char_count": len(text)})
            ip_blocked_count = 0
        else:
            detail = f"{error}: {reason}" if reason else error
            if is_permanent_failure(error, reason):
                print(f"PERMANENT ({detail})")
                permanent_this_run.append({**video, "error": error, "reason": reason})
            else:
                print(f"NO TRANSCRIPT ({detail})")
                still_failed.append({**video, "error": error, "reason": reason})
                if error in ("IpBlocked", "RequestBlocked"):
                    ip_blocked_count += 1
                    if ip_blocked_count >= 3:
                        print("\nIP is blocked — stopping early. Wait a few hours and run again.")
                        print("Progress is saved; it will resume from where it left off.")
                        still_failed.extend(videos[i:])
                        break

        times.append(time.monotonic() - t0)
        time.sleep(random.uniform(1.5, 3.0))

    print(f"\nDone: {len(results)} transcripts, {len(permanent_this_run)} permanent, {len(still_failed)} retry.")

    if permanent_this_run:
        append_permanently_failed(permanent_this_run)
        print(f"  {len(permanent_this_run)} permanent failures saved to {PERMANENTLY_FAILED_PATH}")

    (OUTPUT_DIR / "no_captions.json").write_text(json.dumps(still_failed, indent=2))
    print("no_captions.json updated with remaining videos.")

    rebuild_combined()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rebuild", action="store_true",
        help="Rebuild no_captions.json from video_index.json, excluding videos that already "
             "have transcripts, are permanently failed, or are Shorts (if mark_shorts.py was run)."
    )
    parser.add_argument(
        "--no-skip-shorts", action="store_true",
        help="Include Shorts when rebuilding no_captions.json (default: skip them)."
    )
    parser.add_argument(
        "--purge-permanent", action="store_true",
        help="One-time cleanup: scan no_captions.json for known-permanent failures "
             "(TranscriptsDisabled, private, deleted, etc.) and move them to "
             "permanently_failed.json so they are never retried."
    )
    parser.add_argument(
        "--max-minutes", type=float, default=None, metavar="N",
        help="Stop after N minutes (progress saved). Lets you cap each run "
             "below YouTube's rate-limit threshold instead of running until banned."
    )
    args = parser.parse_args()

    if args.purge_permanent:
        purge_permanent()
    elif args.rebuild:
        rebuild_no_captions(skip_shorts=not args.no_skip_shorts)
    else:
        run(max_minutes=args.max_minutes)
