#!/usr/bin/env python3
"""
One-time script that marks Shorts in transcripts/video_index.json.

A video is flagged is_short = True if EITHER:
  * it's in the channel's authoritative Shorts playlist (UUSH prefix), OR
  * it's <= 60s long  (catches pre-Oct-2024 vertical shorts that YouTube
    never reclassified into the Shorts playlist)

Run once, then regenerate the fetch queue:
    python3 mark_shorts.py
    python3 fetch_auto_captions.py --rebuild

Requires client_secrets.json / token.json (same OAuth as youtube_api_transcripts.py).
Costs ~10 quota units for the Shorts playlist + ~1 per 50 videos for durations.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
SECRETS_FILE = "client_secrets.json"
TOKEN_FILE = "token.json"
INDEX_FILE = Path("transcripts/video_index.json")
SHORTS_MAX_SECONDS = 60


def get_service():
    creds = None
    if Path(TOKEN_FILE).exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        Path(TOKEN_FILE).write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def iso8601_to_seconds(duration: str) -> int:
    """PT1H2M3S → 3723"""
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration or "")
    if not m:
        return 0
    h, mins, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mins * 60 + s


def fetch_shorts_ids(youtube) -> set[str]:
    """Fetch all video IDs from the channel's Shorts playlist (UUSH...)."""
    r = youtube.channels().list(part="id", mine=True).execute()
    channel_id = r["items"][0]["id"]          # UC...
    shorts_playlist = "UUSH" + channel_id[2:] # UUSH...
    print(f"Channel ID:       {channel_id}")
    print(f"Shorts playlist:  {shorts_playlist}")

    short_ids: set[str] = set()
    page_token = None
    while True:
        try:
            r = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=shorts_playlist,
                maxResults=50,
                pageToken=page_token,
            ).execute()
        except Exception as e:
            # Channel may have no Shorts playlist at all — fall back to duration only
            print(f"  (no Shorts playlist found: {type(e).__name__}) — using duration only")
            break
        for item in r.get("items", []):
            short_ids.add(item["contentDetails"]["videoId"])
        page_token = r.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.2)
    return short_ids


def fetch_durations(youtube, video_ids: list[str]) -> dict[str, int]:
    """Fetch contentDetails.duration (seconds) for all videos, in batches of 50."""
    durations: dict[str, int] = {}
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        r = youtube.videos().list(
            part="contentDetails", id=",".join(batch)
        ).execute()
        for item in r.get("items", []):
            durations[item["id"]] = iso8601_to_seconds(
                item["contentDetails"]["duration"]
            )
        end = min(i + 50, len(video_ids))
        print(f"  durations [{end}/{len(video_ids)}]")
        time.sleep(0.2)
    return durations


def run():
    if not INDEX_FILE.exists():
        print(f"{INDEX_FILE} not found — run youtube_api_transcripts.py first.")
        return

    videos = json.loads(INDEX_FILE.read_text())
    already = sum(1 for v in videos if "is_short" in v)
    if already == len(videos):
        n = sum(1 for v in videos if v["is_short"])
        print(f"All {len(videos)} videos already marked ({n} Shorts).")
        print("Run: python3 fetch_auto_captions.py --rebuild")
        return

    print("Authenticating...")
    youtube = get_service()

    print("Fetching Shorts playlist (UUSH)...")
    short_ids = fetch_shorts_ids(youtube)
    print(f"  {len(short_ids)} videos in the Shorts playlist\n")

    print("Fetching durations for all videos...")
    durations = fetch_durations(youtube, [v["id"] for v in videos])
    print()

    from_playlist = from_duration = 0
    for v in videos:
        in_playlist = v["id"] in short_ids
        secs = durations.get(v["id"], 0)
        short_by_duration = 0 < secs <= SHORTS_MAX_SECONDS
        v["duration_seconds"] = secs
        v["is_short"] = in_playlist or short_by_duration
        if v["is_short"]:
            if in_playlist:
                from_playlist += 1
            else:
                from_duration += 1

    INDEX_FILE.write_text(json.dumps(videos, indent=2))

    n_short = sum(1 for v in videos if v["is_short"])
    n_long  = len(videos) - n_short
    print(f"Updated {INDEX_FILE}:")
    print(f"  {n_short} Shorts total  (will be skipped by --rebuild)")
    print(f"    {from_playlist} from the UUSH Shorts playlist")
    print(f"    {from_duration} extra caught by ≤{SHORTS_MAX_SECONDS}s duration (older shorts)")
    print(f"  {n_long} regular videos")
    print(f"\nNext step: python3 fetch_auto_captions.py --rebuild")


if __name__ == "__main__":
    run()
