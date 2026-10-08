# META_EXPORT — the fifth archive, and what it can and cannot answer

Per `CLAUDE.md` (quoted in `analysis/TW_EXPORT.md`): *write up what each record
can and cannot answer before designing anything that joins them; the asymmetry
is a finding, not an obstacle to route around.* This is that write-up for the
Meta pull — Facebook timeline + Instagram posts, collected 2026-10-07/08 —
before anything is joined to it.

Generated from: `~/workspace/meta-corpus/` (raw JSONL corpora, out of git),
with scripts `analysis/meta_days.py`, `analysis/meta_eras.py`,
`analysis/meta_residences.py`, `analysis/meta_fourthwall.py`,
`analysis/meta_phrase.py`. Per-day activity: `data/META_DAYS.tsv`
(no header; `date\t source(fb|ig)\t posts\t videos`).

## What arrived

Two connector reads, both of the user's **own** accounts, fetched 2026-10-07
into 2026-10-08 (America/New_York):

| pull | account | records | span (local) |
|---|---|---:|---|
| Facebook timeline | Devon Gallegos, profile id 723125492, via `facebook-cli` | 1,820 posts | 2008-10-07 → 2026-10-07 |
| Instagram posts | @gallegos.devon, via `instagram-cli` | 1,743 records (1,109 POST, 427 REEL, 207 story-archive items) | 2016-02-29 → 2026-10-07 |
| Instagram posts | @hal.cyonus, via `instagram-cli` | **0** | — (empty shell: 6 followers, 0 following, 0 posts; noted and set aside) |

Timeline pagination was exhausted (`has_next_page=false`, 92 pages, no
rate-limit errors): this is ~100% of what the API returns. Every timeline post
has author == owner — zero posts by others on his wall. Text is preserved
untruncated; 17 Facebook posts also carry a `video_transcript` field.

## Asset inventory, per year

`fb_own` / `fb_shr` = own-authored vs shared (`entshare`-type) Facebook posts.
IG story-archive items carry media only, no captions.

| year | fb_own | fb_shr | fb_video | fb_photo | ig_posts | ig_reels | ig_stories |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2008 | 21 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2009 | 61 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2010 | 62 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2011 | 20 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2012 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2013 | 11 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2014 | 9 | 2 | 0 | 0 | 0 | 0 | 0 |
| 2015 | 16 | 2 | 0 | 0 | 0 | 0 | 0 |
| 2016 | 9 | 11 | 0 | 1 | 14 | 0 | 20 |
| 2017 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2018 | 4 | 6 | 0 | 0 | 1 | 0 | 0 |
| 2019 | 76 | 34 | 0 | 58 | 33 | 0 | 0 |
| 2020 | 72 | 94 | 5 | 7 | 0 | 0 | 0 |
| 2021 | 246 | 68 | 47 | 161 | 481 | 115 | 35 |
| 2022 | 278 | 70 | 58 | 158 | 632 | 144 | 9 |
| 2023 | 142 | 90 | 7 | 33 | 71 | 36 | 3 |
| 2024 | 191 | 25 | 26 | 75 | 94 | 61 | 68 |
| 2025 | 118 | 21 | 39 | 48 | 73 | 20 | 27 |
| 2026 | 57 | 4 | 49 | 5 | 62 | 51 | 120 |

Totals: **1,820** FB posts (1,393 own, 427 shared, 231 video, 546 photo),
**15** own-authored Facebook comments (sampled from 30 text-heaviest own posts;
5 had any comments), **1,461** IG posts/reels with captions, **207** IG story
items (media only), 20 saved FB items (6 post / 4 reel / 9 link / 1 video),
9 saved IG posts. Friend/follower counts were recorded as scalars only (666 FB
friends; @gallegos.devon 268 followers / 436 following) and no names were
enumerated.

## Coverage gaps, stated plainly

1. **Media loss.** Zero Facebook video posts before 2020; only 1 photo post
   before 2019. The 2008–2015 record is almost entirely text/status posts.
   The user suspects videos were lost a couple of years ago; the API shows no
   way to distinguish user deletion, platform removal, or an incident.
2. **Silent years.** Zero posts in 2012 and 2017; very sparse 2011–2018. These
   are real zeros in what the API returns, not fetch failures.
3. **No Facebook stories archive** — the skill has no archive endpoint.
4. **No instant messages.** Messenger Companion and Instagram Messages are both
   unconnected as of 2026-10-07, so the user's DMs are not in this corpus.
5. **Only one of two Facebook profiles.** The user historically kept two
   profiles (glubose@aol.com, glubose@gmail.com); only one account can be
   linked at a time. The linked profile is the one he ties to the AOL account
   in his own 2021-07-23 video ("This is tied to my AOL account … and the one
   I don't use as much is tied to my Gmail"). The Gmail-tied profile's posts
   are out of reach from here.
6. **hal.cyonus is an empty shell** (see table above).
7. **Instagram story archive items have no text.** 207 items, media only.

## What this corpus can and cannot answer

**Can.** It is the project's first record of him *unaccompanied by a model*
that is large, dated, and uniform — the Twitter export's long-form posts were
the second candidate (`TW_EXPORT.md`), but this one is 18 years long and
~3,300 text records. It carries a clock on every record, like the Grok
archives, and unlike them it is not a turn-taking record at all: there is no
model in the loop, no sampler, no branch structure. `PAIRS.md`, `LEARNABLE.md`
and the rest of the undo-tree measurements cannot be run on it — the data does
not exist — which is the same asymmetry `TW_EXPORT.md` stated for Twitter,
one archive further along.

**Cannot.** It cannot answer anything about his messaging life (gap 4), about
the other profile (gap 5), or about the visual content of his videos and
photos — only 17 videos carry transcripts, and no image content was described.
It cannot date when the pre-2020 videos disappeared (gap 1). And like every
non-NovelAI archive here, it cannot carry chosen/rejected pairs or model
latency: there is no model and no generation.

**What it adds.** Duration of a different kind: the Grok archives gave the
project per-exchange timestamps over ~20 months; this gives per-post
timestamps over 18 years of the author writing in his own voice. That is the
only measurement in the project this archive is structurally positioned to
make, and it is what `analysis/META_ERAS.md` is built on.
