# 2026-08-12 — The archive with a clock

Endorphin opened with *"I just uploaded a zip of my twitter data. care to analyze it in
similar fashion to my other corpora?"* and a Drive link. 4.03 GB, 8,571 files, handle
`glubose` — the same handle as the channel in `data/EPISODES.tsv`.

**The request contains a claim worth testing rather than executing.** "In similar fashion"
presumes the archive can carry the apparatus, and mostly it cannot: there is no undo tree,
so no rejected generations and no branch reachability, and no sampler settings, so nothing
settings-comparative. Most of `analysis/` is uncomputable here. What it has instead is the
one thing the NovelAI export lacks — **timestamps** — which is why this session produced a
capability document before it produced a measurement.

Branch `claude/twitter-data-analysis-hzt3gp`. Nothing here touched `FINDINGS.md` or
`READINGS.md`; §1 below bears on the frame and the change it wants is recorded, not applied.

## What was built

`analysis/tw_export.py` (stdlib only), `analysis/TW_EXPORT.md` (schema + the three-archive
asymmetry table), `analysis/TWITTER.md` (generated). Committed data:
`data/twitter_meta.jsonl` (2,818 rows, lengths only) and `data/TWEET_DAYS.tsv` (580 days).
`README.md` and `CLAUDE.md` updated for the third corpus.

The script reads **straight out of the delivered `.zip`** — the 4 GB is essentially all
media and unpacking it is wasted disk. It also has a `SKIP` list and never opens the direct
messages, phone number, email, creation IP, 340-entry IP audit, ad records or
personalization dump.

## Privacy is not inherited, and this is the first archive where that bites

The public-repo decision (*"i am prepared to be scraped"*) was made about a corpus of
Endorphin's own fiction. It does not transfer to an export holding **two-party** data: he
can consent to his own exposure and cannot consent to his 16 correspondents'. So nothing
from this archive enters `data/` with message text in it — the committed metadata is chat
id, turn index, timestamp, sender, mode and *lengths*. That also sidesteps having to make
any judgement about tweet content, one tweet at a time, in a public repo.

**This is flagged rather than settled.** The tweets are already public and Endorphin may
well want them committed in full; the long-form posts in particular (§ below) are a
resource. That is his call and it was not made unilaterally here.

## 1. The cue length is the author — and the control costs the frame something

`FINDINGS.md`'s frame rests on a median human turn of **55 characters** across 134,063
blocks, and the standing objection is that it measures NovelAI's text box. Grok is a
different platform, model, interface **and activity** — image prompts, link analysis,
fact-checks, not driving fiction.

| | n | median | <50 | 50–200 | 200–600 | 600+ |
|---|---:|---:|---:|---:|---:|---:|
| Grok user turn, after an agent turn | 978 | **58** | 42.2% | 46.3% | 8.6% | 2.9% |
| Grok chat opener (control) | 431 | 55 | 35.0% | 50.3% | 10.0% | 4.6% |
| NovelAI human block after a generation | 134,063 | 55 | 46.4% | 44.6% | 6.7% | 2.3% |

58 against 55, same shape. The median human turn survives a change of tool, so **it is a
fact about the author, not about NovelAI.** That is the strongest cross-tool control the
project has ever had for a headline number, and for once the number passes.

**But the opener control fires.** A chat opener has nothing before it and cannot be a
response to a generation, and it runs to a median of **55 characters** — indistinguishable
from the turns that do follow one. Position in the exchange does not move the number. So
the median is *not* evidence for the turn-taking mechanism; it is evidence about how long
this person types at a model, in any position. `FINDINGS.md` argues the turn-taking frame
from the branch structure, and after this it has to keep arguing it from there alone.

Worth noting which way this cuts: the standing warning is *the obvious metric measures the
tool, not the author.* Here the obvious metric measured the author and the **control**
narrowed what it licenses. Same discipline, opposite outcome.

## 2. Duration — the measurement NovelAI cannot make

`FINDINGS.md` §11 says tempo is unrecoverable for want of per-block timestamps;
`analysis/tempo.py` recovered rhythm from the sequence of lengths and said plainly that
duration was still gone. This record has duration.

**First the resolution, because it is worse than it looks.** The Agent turn carries the
*identical* `createdAt` as the user turn it answers — **1,409 of 1,409**, to the
millisecond. The stamp is the request, not the completion. Model latency is therefore
exactly zero everywhere and unrecoverable, and every interval runs user-turn to user-turn,
mixing generation, reading and typing. One stamp per **exchange**, not per turn.

Turnaround against how much there was to read, restricted to replies under 50 characters so
typing is near-constant:

| agent turn | n | median turnaround |
|---|---:|---:|
| 0–500 chars | 210 | 36s |
| 500–1,000 | 51 | 37s |
| 1,000–2,000 | 39 | 36s |
| 2,000–4,000 | 61 | 63s |
| 4,000+ | 47 | 141s |

**A threshold, not a slope.** Flat at ~36 seconds all the way to 2,000 characters — four
hundred words of output bought no more of his time than forty did — then a steep climb. The
confound is that generation time sits inside the interval, and it is the flat stretch that
rules it out: a generation-time explanation predicts a rise throughout. The second control
holds reading fixed and varies typing, and a long reply costs 2–3× at every reading length,
so human time is a large share of the interval.

What it cannot show is what he was doing in those 36 seconds — reading the opening only,
skimming to a budget, or a fixed rhythm of attention. No scroll or focus events exist.

## 3. The tweets are a second external clock, and they vindicate the OCR

`data/EPISODES.tsv` is 1,492 broadcasts recovered by OCR off the Twitch dashboard — the
project's only independent clock, day-resolution and lossy. The tweets are a second,
stamped by the platform. Both series clump in the same years, so a co-occurrence count
would mostly measure that; the null is a **circular shift** of the broadcast series (20,000
of them), preserving every run and gap and destroying only alignment.

| | observed | shifted null | z | p |
|---|---:|---:|---:|---:|
| days with both | **104** | 67.4 ± 14.9 | 2.45 | 0.0006 |
| tweets per broadcast day | **3.28** | 1.72 ± 0.51 | 3.08 | 0.0031 |

Both survive. **The value is a check on the OCR**: two records made by entirely different
machinery agree well past chance, so `EPISODES.tsv` is measuring real broadcast days. It
does not recover the episodes the OCR missed, and it cannot be joined to *story* activity —
the standing note holds, appended series carry one `last_updated_at` for dozens of sessions.

## Not the same practice

431 chats, median **4 turns and 1.0 minutes**, against NovelAI documents of 3,341 blocks
over years. The corpus's material barely appears: `pynchon` in 3 user turns, `tingle` in 4,
`ai dungeon` in 1, `left behind` in 1. This is a utility register, not a continuation of
the ALMO. It is also *why* §1 means anything — a number that survives a change of activity
as well as of tool is a fact about the person.

No second Knubble-style dating either. The account runs back to 2008 but is dormant until
2022 (1 tweet in 2019, 4 in 2020, 11 in 2021, then 240 in 2022), and the Grok record starts
2024-12-07, after everything.

## Left open

- **The 432 long-form posts are unread — 333,910 characters, median 534.** This is the
  control the project has never had: Endorphin writing at length in his own voice with **no
  model in the loop**. Every register measurement in `REGISTER.md` compares him against a
  model *inside* a generation session. Highest-value unread material here by some distance.
- **Whether to commit tweet text.** Flagged above, his call.
- **Whether any Grok chat seeded corpus material.** Term counts say unlikely, but they are
  substring counts and the standing note that titles lie applies to search terms too.
- The zip died with the container. It is in Drive, file id
  **`10bD3yruaqhxucd-YW-ywl1Zx4m2HlokP`**, owner `glubose@gmail.com`, and
  `tw_export.py` takes it as-is.
