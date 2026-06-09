#!/usr/bin/env python3
"""
One-time script to enrich transcripts/video_index.json with duration data
from the YouTube Data API. Run this once, then use --rebuild in
fetch_auto_captions.py to regenerate no_captions.json with Shorts filtered out.

Usage:
    python3 add_durations.py

Requires client_secrets.json / token.json (same OAuth as youtube_api_transcripts.py).
Costs ~40 quota units for a 2000-video channel (well under the 10,000/day limit).
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


def run():
    if not INDEX_FILE.exists():
        print(f"{INDEX_FILE} not found — run youtube_api_transcripts.py first.")
        return

    videos = json.loads(INDEX_FILE.read_text())

    needs = [v for v in videos if "duration_seconds" not in v]
    if not needs:
        shorts = sum(1 for v in videos if v.get("duration_seconds", 9999) <= SHORTS_MAX_SECONDS)
        print(f"All {len(videos)} videos already have duration data ({shorts} Shorts ≤{SHORTS_MAX_SECONDS}s).")
        print("Run: python3 fetch_auto_captions.py --rebuild  to regenerate no_captions.json")
        return

    print(f"{len(needs)} videos need duration data (already have {len(videos) - len(needs)}).")
    print("Authenticating...")
    youtube = get_service()

    duration_map: dict[str, int] = {}
    for i in range(0, len(needs), 50):
        batch = needs[i : i + 50]
        ids = ",".join(v["id"] for v in batch)
        r = youtube.videos().list(part="contentDetails", id=ids).execute()
        for item in r.get("items", []):
            duration_map[item["id"]] = iso8601_to_seconds(
                item["contentDetails"]["duration"]
            )
        end = min(i + 50, len(needs))
        print(f"  [{end}/{len(needs)}] fetched")
        time.sleep(0.2)

    # Some videos may have been deleted/private — mark them 0 so they're not retried
    for v in videos:
        if "duration_seconds" not in v:
            v["duration_seconds"] = duration_map.get(v["id"], 0)

    INDEX_FILE.write_text(json.dumps(videos, indent=2))

    shorts = sum(1 for v in videos if v["duration_seconds"] <= SHORTS_MAX_SECONDS)
    print(f"\nDone. {len(duration_map)} durations written to {INDEX_FILE}")
    print(f"  {shorts} videos are ≤{SHORTS_MAX_SECONDS}s and will be skipped as Shorts")
    print(f"\nNext step: python3 fetch_auto_captions.py --rebuild")


if __name__ == "__main__":
    run()
