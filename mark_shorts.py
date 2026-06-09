#!/usr/bin/env python3
"""
One-time script that marks Shorts in transcripts/video_index.json using
YouTube's own Shorts playlist (UUSH prefix), which is the authoritative
source — more reliable than duration or hashtag heuristics.

Run once, then regenerate the fetch queue:
    python3 mark_shorts.py
    python3 fetch_auto_captions.py --rebuild

Requires client_secrets.json / token.json (same OAuth as youtube_api_transcripts.py).
Costs ~1 quota unit per 50 Shorts (typically < 10 units total).
"""

from __future__ import annotations

import json
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
        r = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=shorts_playlist,
            maxResults=50,
            pageToken=page_token,
        ).execute()
        for item in r.get("items", []):
            short_ids.add(item["contentDetails"]["videoId"])
        page_token = r.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.2)
    return short_ids


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
    print("Fetching Shorts playlist...")
    short_ids = fetch_shorts_ids(youtube)
    print(f"Found {len(short_ids)} Shorts.\n")

    for v in videos:
        v["is_short"] = v["id"] in short_ids

    INDEX_FILE.write_text(json.dumps(videos, indent=2))

    n_short = sum(1 for v in videos if v["is_short"])
    n_long  = len(videos) - n_short
    print(f"Updated {INDEX_FILE}:")
    print(f"  {n_short} Shorts  (will be skipped by --rebuild)")
    print(f"  {n_long} regular videos")
    print(f"\nNext step: python3 fetch_auto_captions.py --rebuild")


if __name__ == "__main__":
    run()
