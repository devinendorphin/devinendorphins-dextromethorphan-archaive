# TW_EXPORT — the third archive, and what it can and cannot answer

There are now three archives in this project and they are three different
shapes. `CLAUDE.md` sets the rule for adding one: *write up what each record can
and cannot answer before designing anything that joins them; the asymmetry is a
finding, not an obstacle to route around.* This is that write-up for the
Twitter/X export, done before anything was joined.

Run it with `analysis/tw_export.py`; the measurements are in `analysis/TWITTER.md`.

## What arrived

A standard Twitter/X account export, generated 2026-08-11, **4.03 GB across
8,571 files**, handle `glubose` — the same handle as the Twitch/YouTube channel
in `data/EPISODES.tsv`, and the same account that owns the Drive folders.

Essentially all of the 4 GB is media. The record is 18 MB of `data/*.js`, each
file a single `window.YTD.<type>.part0 = [ … ]` assignment wrapping plain JSON.
Four of them matter:

| file | records | what it is |
|---|---:|---|
| `tweets.js` | 3,909 | posts, 2008-07-12 .. 2026-08-11, stamped to the second |
| `grok-chat-item.js` | 2,818 | **turn-taking with a language model, timestamped** |
| `note-tweet.js` | 432 | long-form posts, 333,910 chars, median 534 |
| `tweet-headers.js` | 3,909 | ids and stamps only; redundant with `tweets.js` |

`manifest.js` declares the count of every type, which is how the above was
enumerated rather than guessed.

## What is deliberately not read

The export also contains direct messages (16), the account's phone number, email,
creation IP, a 340-entry IP audit, ad-conversion records and the personalization
inference dump. **`tw_export.py` never opens any of them** — there is a `SKIP`
list in the script and the archive reader filters on it.

The repo is public by a deliberate decision (`sessions/LATEST.md`: *"i am
prepared to be scraped"*), and that decision was made about a corpus of the
author's own fiction. It does not extend here. Direct messages are two-party:
Endorphin can consent to his own exposure and cannot consent to his
correspondents'. The phone number, email and IP history are not analysable
material for any question this project asks. **Nothing in `data/` carries message
text**: `data/twitter_meta.jsonl` is one row per Grok turn holding chat id, turn
index, timestamp, sender, mode and *lengths only*, and `data/TWEET_DAYS.tsv` is a
date and a count. That matches the existing rule for `data/` — settings metadata,
no prose — and it means the committed record is safe to have in a public repo
without any judgement call about tweet content.

The tweet and Grok *text* is written to `out/` by `--out`, which is gitignored,
for local analysis only.

## The Grok record, in detail

This is the only part of the export that is a text-generation record, so it is
the only part that could join the project's subject matter. Its schema:

```json
{"grokChatItem": {
  "accountId": "…", "chatId": "…",
  "createdAt": "2024-12-07T19:06:52.310Z",
  "sender":   {"name": "User"},        // or "Agent"
  "grokMode": {"name": "Normal"},      // 2,814 Normal, 4 Fun
  "message":  "…",
  "postIds": [], "attachments": []
}}
```

2,818 turns, **1,409 User and 1,409 Agent, exactly balanced**, across 431 chats,
2024-12-07 .. 2026-07-29, on 162 distinct days.

Three properties decide what it can be asked.

**1. Strict alternation, and therefore no re-rolls.** The perfect 1,409/1,409
balance is not a coincidence of the data; it is the schema. Every user turn has
exactly one agent turn. If Endorphin ever regenerated a Grok response, the
discarded one is not here.

**2. One timestamp per exchange, not per turn.** The Agent turn carries the
*identical* `createdAt` as the user turn it answers — in 1,409 of 1,409 cases,
to the millisecond. The stamp is the request, not the completion. So model
latency is exactly zero everywhere and is not recoverable, and any interval
measured here runs user-turn to user-turn, containing generation, reading and
typing undifferentiated. This is the single most important caveat on
`TWITTER.md` §2 and it is why that section is built out of controls rather than
out of the raw gradient.

**3. No settings, and no model identity.** There is no temperature, no sampler
order, no max length, and no record of which Grok version answered. Nothing
settings-comparative can be run, and the model-field caveat from the NovelAI side
does not even have a field to attach to.

## The asymmetry, stated plainly

| | NovelAI (2,016) | AI Dungeon (888) | Twitter/X Grok (431 chats) |
|---|---|---|---|
| full undo tree | **yes** — 760,611 blocks | no | no |
| rejected generations | **yes**, via branch reachability | no | **structurally none** |
| per-turn sampler settings | **yes** | no | no |
| model recorded | yes, but records the *client setting* | partial | no |
| branch structure | `prevBlock` / `currentBlock` | flat `actionWindow`, `undoneAt` | flat, strict alternation |
| **timestamps** | story-level only | item-level | **per exchange, to the ms** |
| turn attribution | yes | yes | yes |
| span | 2021-06 .. 2026-07 | 2020-12 .. | 2024-12 .. 2026-07 |

Reading down the columns: almost everything this project measures lives in the
first column, and the reason is the undo tree. `PAIRS.md`, `LEARNABLE.md`,
`STOPPING.md`, `TAKEOVER.md`, `HANDOVER.md`, `SWEEPS.md`, `ERATO.md` and
`REGISTER.md` are all built on chosen/rejected pairs, branch reachability or
sampler settings, and **none of them can be computed on the Grok record at all.**
Not "with difficulty" — the data does not exist.

Reading across the bottom rows, the exchange is the one thing all three share,
which is why the corpus settled on the turn as its unit and why the cue-length
comparison in `TWITTER.md` §1 is possible.

The last row is the interesting one, and it runs the other way. `FINDINGS.md` §11
records that NovelAI stores no per-block timestamps, so duration is
unrecoverable; `analysis/tempo.py` recovered rhythm from the sequence of lengths
and said explicitly that duration was still gone. **The Grok record has
duration.** It is the only measurement in the project that the NovelAI corpus is
structurally incapable of making, which is the whole of what this archive adds to
the measurement side.

## What it is not

**It is not a continuation of the practice.** The NovelAI corpus is one person
driving models through five years of fiction, in documents running to 3,341
blocks and a million characters. The Grok chats are 431 utility exchanges with a
median of **4 turns and 1.0 minutes** — image prompts, link analysis, opinion
probes, fact-checks. The corpus's material barely appears: `pynchon` in 3 user
turns, `tingle` in 4, `ai dungeon` in 1, `left behind` in 1.

That is worth stating because it is the obvious thing to get wrong. A third
archive of the same person talking to a language model looks like more of the
same corpus and is not: it is a different activity, and the only reason the
cue-length comparison in §1 means anything is precisely *because* the activity
differs — a number that survives a change of platform, model, interface **and**
task is a fact about the author.

**It is not a second Knubble-style dating.** The AI Dungeon archive moved the
project's floor back eighteen months because a pasted listing in one NovelAI
story matched an adventure action-for-action. Nothing here does that. The tweets
run back to 2008 but the account is dormant until 2022 (1 tweet in 2019, 4 in
2020, 11 in 2021, then 240 in 2022), and the Grok record starts 2024-12-07, which
is after everything.

## Open, not done

- **The 194 tweets from 2026 and the 432 long-form posts are unread.** The
  long-form set is 334,000 characters of the author writing in his own voice with
  no model in the loop, which is a control the project has never had. Every
  register measurement in `REGISTER.md` compares him against a model *inside* a
  generation session. This is him outside one.
- **The tweet↔story join was not attempted**, deliberately. The standing note
  holds: appended series carry one `last_updated_at` for dozens of sessions, so
  day-matching undersamples exactly the stories that were used most. The clock
  test in `TWITTER.md` §3 joins tweets to *broadcasts*, where both sides are
  day-stamped events, and stops there.
- **Whether any Grok chat is the origin of corpus material is unchecked.** The
  term counts above say it is unlikely, but they are substring counts over user
  turns, and the standing note that titles lie applies to search terms too.
