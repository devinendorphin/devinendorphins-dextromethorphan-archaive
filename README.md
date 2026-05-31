# devinendorphins-dextromethorphan-archaive

Transcript archive and analysis for the [@glubose](https://www.youtube.com/@glubose) YouTube channel.

## Collecting Transcripts

### Install dependencies

```bash
pip install yt-dlp youtube-transcript-api
```

### Option A — Run locally (simplest, no credentials needed)

YouTube does not block requests from residential IPs, so running locally just works:

```bash
python3 collect_transcripts.py
```

Output lands in `transcripts/`:
- `video_index.json` — full list of videos with metadata
- `<title>__<id>.txt` — one file per video
- `ALL_TRANSCRIPTS_COMBINED.txt` — every transcript concatenated in chronological order
- `no_transcript.json` — videos that had no available transcript (shorts, music-only, etc.)

### Option B — Run from a cloud/server environment (needs cookies)

YouTube blocks datacenter IPs. Export your browser cookies while logged into YouTube:

1. Install the **"Get cookies.txt LOCALLY"** Chrome extension (or equivalent for Firefox)
2. Visit [youtube.com](https://www.youtube.com) while logged in
3. Click the extension → Export → save as `cookies.txt`
4. Upload `cookies.txt` to this directory, then run:

```bash
python3 collect_transcripts.py --cookies cookies.txt
```

> **Do not commit `cookies.txt`** — it contains your session tokens.

### Options

```
--cookies  PATH      Netscape-format cookies file (cloud use)
--output-dir PATH    Where to save transcripts (default: transcripts/)
```

## Output structure

```
transcripts/
├── video_index.json               # all video metadata
├── ALL_TRANSCRIPTS_COMBINED.txt   # single chronological megafile
├── no_transcript.json             # videos with no transcript
└── <title>__<video_id>.txt        # one file per video
```

Each per-video file has a small header:

```
TITLE: My Video Title
VIDEO ID: dQw4w9WgXcQ
URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
DATE: 20230415

<transcript text here>
```
