#!/usr/bin/env python3
"""
Collect YouTube transcripts via YouTube Data API v3 (OAuth 2.0).
As the channel owner this bypasses all rate limits and n-challenge issues.

Setup (one time):
  1. Go to https://console.cloud.google.com
  2. Create a project → Enable "YouTube Data API v3"
  3. APIs & Services → Credentials → Create OAuth 2.0 Client ID (Desktop app)
  4. Download the JSON → save as client_secrets.json next to this script
  5. pip install google-api-python-client google-auth-oauthlib

Run:
  python3 youtube_api_transcripts.py
  (opens browser for Google login on first run, saves token for future runs)
"""

from __future__ import annotations

import io
import json
import re
import time
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
SECRETS_FILE = "client_secrets.json"
TOKEN_FILE = "token.json"


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


def get_uploads_playlist(youtube) -> str:
    r = youtube.channels().list(part="contentDetails", mine=True).execute()
    return r["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def list_all_videos(youtube, playlist_id: str) -> list[dict]:
    videos, page_token = [], None
    while True:
        r = youtube.playlistItems().list(
            part="snippet", playlistId=playlist_id,
            maxResults=50, pageToken=page_token
        ).execute()
        for item in r["items"]:
            s = item["snippet"]
            vid_id = s["resourceId"]["videoId"]
            videos.append({
                "id": vid_id,
                "title": s["title"],
                "upload_date": s["publishedAt"][:10].replace("-", ""),
                "url": f"https://www.youtube.com/watch?v={vid_id}",
            })
        page_token = r.get("nextPageToken")
        if not page_token:
            break
        time.sleep(0.3)
    return videos


def get_caption_id(youtube, video_id: str) -> str | None:
    try:
        r = youtube.captions().list(part="snippet", videoId=video_id).execute()
        # Prefer manual English, then auto-generated English, then any English
        tracks = r.get("items", [])
        for track in tracks:
            lang = track["snippet"]["language"]
            kind = track["snippet"]["trackKind"]
            if lang.startswith("en") and kind == "standard":
                return track["id"]
        for track in tracks:
            if track["snippet"]["language"].startswith("en"):
                return track["id"]
        # Fall back to first available track
        return tracks[0]["id"] if tracks else None
    except HttpError:
        return None


def download_caption_vtt(youtube, caption_id: str) -> str | None:
    try:
        request = youtube.captions().download(id=caption_id, tfmt="vtt")
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return fh.getvalue().decode("utf-8", errors="replace")
    except HttpError:
        return None


def parse_vtt(vtt: str) -> str:
    lines = vtt.splitlines()
    text_lines = []
    for line in lines:
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


def safe_filename(title: str, video_id: str) -> str:
    safe = re.sub(r'[^\w\s\-]', '', title).strip()
    safe = re.sub(r'\s+', '_', safe)[:80]
    return f"{safe}__{video_id}"


def format_eta(seconds: float) -> str:
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m}m" if h else (f"{m}m {s}s" if m else f"{s}s")


def collect(output_dir: Path = Path("transcripts")):
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Authenticating...")
    youtube = get_service()

    print("Getting uploads playlist...")
    playlist_id = get_uploads_playlist(youtube)

    print("Fetching video list...")
    videos = list_all_videos(youtube, playlist_id)
    print(f"Found {len(videos)} videos.")
    (output_dir / "video_index.json").write_text(json.dumps(videos, indent=2))

    results, failed, times = [], [], []

    for i, video in enumerate(videos, 1):
        vid_id = video["id"]
        title = video["title"]
        filename = safe_filename(title, vid_id) + ".txt"
        out_path = output_dir / filename

        eta = f"  ETA {format_eta(sum(times)/len(times) * (len(videos)-i))}" if times else ""

        if out_path.exists():
            print(f"[{i}/{len(videos)}]{eta}  SKIP  {title}")
            results.append({**video, "transcript_file": filename})
            continue

        print(f"[{i}/{len(videos)}]{eta}  {title}", end="  ", flush=True)
        t0 = time.monotonic()

        caption_id = get_caption_id(youtube, vid_id)
        text = None
        if caption_id:
            vtt = download_caption_vtt(youtube, caption_id)
            if vtt:
                text = parse_vtt(vtt)

        if text:
            header = f"TITLE: {title}\nVIDEO ID: {vid_id}\nURL: {video['url']}\nDATE: {video.get('upload_date','')}\n\n"
            out_path.write_text(header + text, encoding="utf-8")
            print(f"OK ({len(text)} chars)")
            results.append({**video, "transcript_file": filename, "char_count": len(text)})
        else:
            print("NO CAPTIONS")
            failed.append(video)

        times.append(time.monotonic() - t0)
        time.sleep(0.5)

    # Build combined file
    combined = output_dir / "ALL_TRANSCRIPTS_COMBINED.txt"
    print("\nBuilding combined file...")
    with combined.open("w", encoding="utf-8") as f:
        f.write("@glubose YouTube Channel — All Transcripts\n")
        f.write(f"{'='*60}\n")
        f.write(f"Videos: {len(videos)}  |  Transcripts: {len(results)}  |  No captions: {len(failed)}\n")
        f.write(f"{'='*60}\n\n")
        for v in sorted(results, key=lambda x: x.get("upload_date", "")):
            f.write(f"\n{'='*60}\n")
            f.write((output_dir / v["transcript_file"]).read_text(encoding="utf-8"))
            f.write("\n")

    print(f"Saved: {combined}")
    print(f"  {len(results)} transcripts  |  {len(failed)} had no captions")
    if failed:
        (output_dir / "no_captions.json").write_text(json.dumps(failed, indent=2))


if __name__ == "__main__":
    collect()
