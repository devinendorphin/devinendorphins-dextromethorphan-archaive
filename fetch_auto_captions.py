#!/usr/bin/env python3
"""
Second-pass transcript collector for videos that had no captions via the YouTube API.
Uses youtube-transcript-api to fetch captions, preferring manually-created ones but
falling back to auto-generated (and, if needed, auto-translated) captions.

Run after youtube_api_transcripts.py has completed:
  python3 fetch_auto_captions.py

Cap each run to stay under YouTube's rate limiter (progress is saved):
  python3 fetch_auto_captions.py --max-minutes 30

Route requests through a proxy to avoid IP blocks (strongly recommended for
large channels or when running from a datacenter/cloud IP):
  # Generic HTTP/HTTPS proxy:
  python3 fetch_auto_captions.py --proxy http://user:pass@host:port
  # Webshare rotating residential proxies (handled natively by the library):
  python3 fetch_auto_captions.py --webshare-username USER --webshare-password PASS

If no_captions.json was lost or corrupted by an early IP-block exit, rebuild it:
  python3 fetch_auto_captions.py --rebuild

NOTE: If you get IpBlocked errors, your IP was temporarily banned by YouTube
from doing too many requests. Wait a few hours (or overnight) and try again,
slow down with --sleep-min/--sleep-max, or route through a proxy.

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

# Exception class names (from youtube-transcript-api) that mean "YouTube blocked
# this IP", as opposed to "this video genuinely has no transcript".
BLOCK_ERRORS = {"IpBlocked", "RequestBlocked"}


def is_block_error(error_type: str | None) -> bool:
    return error_type in BLOCK_ERRORS


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
    # Newer versions expose .reason directly (e.g. "Sign in to confirm your age")
    reason = getattr(e, "reason", None)
    if reason:
        return str(reason).strip()
    # Otherwise mine str(e) for the meaningful line, skipping boilerplate/URLs
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


def build_api(proxy: str | None = None,
              webshare_username: str | None = None,
              webshare_password: str | None = None):
    """Construct a YouTubeTranscriptApi, optionally routed through a proxy.

    Webshare credentials take precedence over a generic proxy URL because the
    library has first-class support for Webshare's rotating residential pool,
    which is the most reliable way to avoid IP blocks.
    """
    from youtube_transcript_api import YouTubeTranscriptApi

    proxy_config = None
    if webshare_username and webshare_password:
        from youtube_transcript_api.proxies import WebshareProxyConfig
        proxy_config = WebshareProxyConfig(
            proxy_username=webshare_username,
            proxy_password=webshare_password,
        )
    elif proxy:
        from youtube_transcript_api.proxies import GenericProxyConfig
        proxy_config = GenericProxyConfig(http_url=proxy, https_url=proxy)

    if proxy_config is not None:
        return YouTubeTranscriptApi(proxy_config=proxy_config)
    return YouTubeTranscriptApi()


def _select_transcript(listing, languages: list[str]):
    """Pick the best available transcript from a listing without making extra
    network requests (find_* only inspect the already-fetched listing).

    Preference order:
      1. manually-created captions in a preferred language
      2. auto-generated captions in a preferred language
      3. any translatable track auto-translated into the first preferred language

    Returns (transcript_obj, kind_label). The actual caption download happens
    later via transcript_obj.fetch().
    """
    # 1. Human-made captions are highest quality.
    try:
        return listing.find_manually_created_transcript(languages), "manual"
    except Exception:
        pass

    # 2. Auto-generated captions ("a.en" etc.) — what we're really here for.
    try:
        return listing.find_generated_transcript(languages), "auto-generated"
    except Exception:
        pass

    # 3. Last resort: translate whatever exists into our first preferred language.
    target = languages[0]
    for transcript in listing:
        if getattr(transcript, "is_translatable", False):
            try:
                return transcript.translate(target), f"translated->{target}"
            except Exception:
                continue

    # Nothing usable; let find_transcript raise a descriptive NoTranscriptFound.
    return listing.find_transcript(languages), "any"


def fetch_transcript(video_id: str, api, languages: list[str]):
    """Returns (text, error_type, reason, kind).

    On success: (text, None, None, kind). On failure: (None, error_type, reason, None).
    Makes at most one list() call plus one fetch()/translate() call, so a single
    blocked video costs far fewer requests than blindly retrying.
    """
    try:
        listing = api.list(video_id)
        transcript, kind = _select_transcript(listing, languages)
        fetched = transcript.fetch()
        return " ".join(s.text for s in fetched), None, None, kind
    except Exception as e:
        return None, type(e).__name__, extract_reason(e), None


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


def run(max_minutes: float | None = None,
        languages: list[str] | None = None,
        proxy: str | None = None,
        webshare_username: str | None = None,
        webshare_password: str | None = None,
        sleep_min: float = 1.5,
        sleep_max: float = 3.0,
        block_backoff: float = 30.0,
        block_retries: int = 2,
        max_consecutive_blocks: int = 2):
    languages = languages or ["en"]

    no_captions_path = OUTPUT_DIR / "no_captions.json"
    if not no_captions_path.exists():
        print("no_captions.json not found.")
        print("Run: python3 fetch_auto_captions.py --rebuild")
        return

    try:
        api = build_api(proxy, webshare_username, webshare_password)
    except ImportError as e:
        print(f"Could not initialise youtube-transcript-api: {e}")
        print("Install it with: pip install youtube-transcript-api")
        return

    videos = json.loads(no_captions_path.read_text())
    cap_note = f"  (stopping after {format_eta(max_minutes * 60)})" if max_minutes else ""
    route = "Webshare proxy" if webshare_username else ("proxy" if proxy else "direct connection")
    print(f"Fetching captions for {len(videos)} videos via youtube-transcript-api "
          f"[{route}, langs={','.join(languages)}]...{cap_note}\n")

    results, still_failed, times = [], [], []
    consecutive_blocks = 0
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

        text, error, reason, kind = fetch_transcript(vid_id, api, languages)

        # If blocked, back off exponentially and retry the SAME video a few times
        # before deciding the IP is actually banned. A real block is sticky, so
        # surviving these retries is a strong signal (no false positives from a
        # single flaky request).
        attempt = 0
        while is_block_error(error) and attempt < block_retries:
            wait = block_backoff * (2 ** attempt)
            print(f"\n    {error} — backing off {format_eta(wait)} "
                  f"(retry {attempt + 1}/{block_retries})", end="  ", flush=True)
            time.sleep(wait)
            text, error, reason, kind = fetch_transcript(vid_id, api, languages)
            attempt += 1

        if text:
            header = f"TITLE: {title}\nVIDEO ID: {vid_id}\nURL: {video['url']}\nDATE: {date}\n\n"
            out_path.write_text(header + text, encoding="utf-8")
            print(f"OK [{kind}] ({len(text)} chars)")
            results.append({**video, "transcript_file": filename,
                            "char_count": len(text), "caption_kind": kind})
            consecutive_blocks = 0
        else:
            detail = f"{error}: {reason}" if reason else error
            print(f"NO TRANSCRIPT ({detail})")
            still_failed.append({**video, "error": error, "reason": reason})
            if is_block_error(error):
                consecutive_blocks += 1
                if consecutive_blocks >= max_consecutive_blocks:
                    print(f"\nIP is blocked ({consecutive_blocks} blocks in a row, "
                          f"backoff exhausted) — stopping early.")
                    print("Wait a few hours and run again, slow down with "
                          "--sleep-min/--sleep-max, or use --proxy/--webshare-*.")
                    print("Progress is saved; it will resume from where it left off.")
                    # Preserve all videos not yet attempted so the next run picks them up
                    still_failed.extend(videos[i:])
                    break
            else:
                # A genuine "no transcript" result clears the block streak too.
                consecutive_blocks = 0

        times.append(time.monotonic() - t0)
        time.sleep(random.uniform(sleep_min, sleep_max))

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
    parser.add_argument(
        "--max-minutes", type=float, default=None, metavar="N",
        help="Stop after N minutes (progress saved). Lets you cap each run "
             "below YouTube's rate-limit threshold instead of running until banned."
    )
    parser.add_argument(
        "--languages", default="en", metavar="LANGS",
        help="Comma-separated preferred caption languages, in order. Default: en"
    )
    parser.add_argument(
        "--proxy", default=None, metavar="URL",
        help="Route requests through an HTTP/HTTPS proxy, e.g. "
             "http://user:pass@host:port. Helps avoid IP blocks."
    )
    parser.add_argument(
        "--webshare-username", default=None,
        help="Webshare proxy username (uses the library's rotating residential pool)."
    )
    parser.add_argument(
        "--webshare-password", default=None,
        help="Webshare proxy password."
    )
    parser.add_argument(
        "--sleep-min", type=float, default=1.5, metavar="SEC",
        help="Minimum delay between videos (default: 1.5s). Raise to be gentler."
    )
    parser.add_argument(
        "--sleep-max", type=float, default=3.0, metavar="SEC",
        help="Maximum delay between videos (default: 3.0s)."
    )
    parser.add_argument(
        "--block-backoff", type=float, default=30.0, metavar="SEC",
        help="Base backoff after a block error; doubles each retry (default: 30s)."
    )
    parser.add_argument(
        "--block-retries", type=int, default=2, metavar="N",
        help="Retries per video after a block before counting it (default: 2)."
    )
    parser.add_argument(
        "--max-consecutive-blocks", type=int, default=2, metavar="N",
        help="Stop after this many videos block in a row, post-backoff (default: 2)."
    )
    args = parser.parse_args()

    if args.rebuild:
        rebuild_no_captions()
    else:
        run(
            max_minutes=args.max_minutes,
            languages=[s.strip() for s in args.languages.split(",") if s.strip()],
            proxy=args.proxy,
            webshare_username=args.webshare_username,
            webshare_password=args.webshare_password,
            sleep_min=args.sleep_min,
            sleep_max=args.sleep_max,
            block_backoff=args.block_backoff,
            block_retries=args.block_retries,
            max_consecutive_blocks=args.max_consecutive_blocks,
        )
