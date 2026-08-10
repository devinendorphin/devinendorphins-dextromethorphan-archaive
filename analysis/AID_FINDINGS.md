# AID_FINDINGS — first analytical pass over the AI Dungeon corpus

2026-08-10. 1,057 items (888 adventures, 169 scenarios), 48,348 actions,
11.8 M characters. Mirrored with `analysis/fetch_aid_export.py`, indexed with
`analysis/aid_index.py` into `data/AID_INDEX.tsv`.

This is the measurement register. Nothing here is a reading; the qualitative
material is flagged as such and belongs in `READINGS.md` if it goes anywhere.

## What the record can and cannot answer

`LATEST.md`'s standing note asked for this before any converter. Answering it
first, because two of the answers are harder than expected.

**`undoneAt` is set on zero of 48,348 actions. `deletedAt` likewise.** The
standing note said "there is an `undoneAt` field, so *some* rejection survives."
It does not. Not one rejected generation is present anywhere in the AI Dungeon
half. Combined with the absence of branch structure and of per-action sampler
settings, this means **every chosen/rejected method in `FINDINGS.md` is not
merely harder on this side — it is uncomputable.** No re-roll analysis, no
containment measure, no abandonment rate, no tempo-coupling-at-re-rolls.

What *is* computable, and is not on the NovelAI side without work: a clean
per-action timestamp on every action, which makes this corpus far better for
anything about **pacing and dates** than the NovelAI export, where 28 appended
series carry a median of 2 distinct edit-days for hundreds of sessions.

**The export is complete.** `actionCount` equals `len(actionWindow)` in all
1,057 items — no truncation, no paging loss. That is worth stating because the
NovelAI side lost 483 stories to decryption failure.

**Scenarios are undated and unplayed.** All 169 carry zero actions; they are
templates (prompt, memory, authorsNote, storyCards) and hold no timestamp of
their own. A scenario can only be dated through the adventures played from it.

## 1. The archive starts 2020-08-11, not 2020-12-07

The earliest action in the corpus is **2020-08-11T03:17:09Z**, in
*going postal: romantic comedy for humans and animists* (173 actions). Nine
adventures predate the *Dr. Knubble* adventure that was triple-confirmed on
2026-08-10 as the archive's opening.

That confirmation was not wrong — `dxqLiJrw55P2` really does open
2020-12-07T10:04:05Z with 76 actions, matching the pasted listing to the minute.
It was simply the earliest thing *the Pynchon × Tingle paste happened to name*.
Four months of earlier work sit under it:

| date | actions | title |
|---|---:|---|
| 2020-08-11 | 173 | going postal: romantic comedy for humans and animists |
| 2020-08-12 | 61 | first and best Transmetropolitan attempt |
| 2020-08-29 | 365 | **First Foray into Engaging GPT-3 in the Pre-Selfware-Era** |
| 2020-08-30 | 253 | 2nd attempt at GPT-3 in Pre-Selfware-Era |
| 2020-08-31 | 222 | Spider Jerusalem Apocrypha |

`README.md` and `CLAUDE.md` are corrected to **11 August 2020**. This is the
third time the archive's start date has moved and the second time in one day;
it moved because a primary record replaced a citation, which is the direction
these corrections should run.

## 2. The two corpora are anti-correlated, not sequential

Joining the two archives on the one axis both records support — time — does not
show a migration. It shows a trial, a full return, and a final switch.

| month | AI Dungeon items | NovelAI stories created |
|---|---:|---:|
| 2021-05 | 73 | 0 |
| 2021-06 | 15 | 1 |
| 2021-07 | **3** | **24** |
| 2021-09 | 2 | 0 |
| 2021-10 | 0 | 14 |
| 2021-11 | **63** | **0** |
| 2021-12 | **84** | **0** |
| 2022-01 | 23 | 0 |
| 2022-02 → | **0 forever** | continuous to 2026 |

NovelAI opened its public beta in June 2021; his first story is 2021-06-29 and
July 2021 is the crossover. Then **he goes back**, entirely, for two months, and
NovelAI records nothing at all in November or December 2021. AI Dungeon stops
dead after January 2022 — seven adventures in the following four years, none
longer than 20 actions.

**Caveat, and it is the one that matters.** The NovelAI creation series is drawn
from the 2,017 recovered stories; the 483 undecryptable ones have no recoverable
creation date, and `data/MISSING.md` bins them by *last edit* (all ≥ 2023-03),
which does not constrain when they were created. So "NovelAI went to zero in
Nov–Dec 2021" carries a 19% blind spot. The AI Dungeon surge does not — 147
items with per-action timestamps — so *the return* is solid even if *the
blackout* is only very likely.

## 3. His cues halve in length, and land exactly on the NovelAI constant

`FINDINGS.md`'s central frame result — the human turn is a cue, median 55
characters, not an edit — **replicates on the other platform**, and the way it
replicates is more interesting than the fact.

| month | median model output | median human turn |
|---|---:|---:|
| 2020-08 | 286 | **120** |
| 2020-11 | 353 | 75 |
| 2021-03 | 367 | 65 |
| 2021-06 | 356 | 61 |
| 2021-12 | 355 | **57** |

The naive number here is the model:human character ratio, which climbs from
1.70 to 3.95 across the corpus and reads as "he types proportionally less over
time." Per the standing note, the control that should fail: **median model
output is flat at ~350–370 characters throughout** — a platform response cap,
not a behaviour. The ratio moves because the human side moves, and it moves a
long way: his median turn falls by more than half in sixteen months.

Where it lands is the finding. **57 characters in December 2021; the NovelAI
corpus reports 55 across the following four and a half years.** The cue is not
a NovelAI fact. It is a technique he converged on during 2020–21 on a different
platform and then carried in, already finished, and did not revise again.

This is the first result in the repo that neither corpus could have produced
alone.

### The disconfirming test, run

The confound worth worrying about is composition, not the platform: late 2021 is
replay-heavy, and a quick replay might carry shorter inputs *by design*, which
would manufacture the decline out of a changing mix of documents. Per-item
medians (443 items with ≥10 human turns), Spearman against item date:

| slice | n | rho | z | Q1 → Q4 median |
|---|---:|---:|---:|---|
| all items | 443 | −0.287 | −6.0 | 76 → 59 |
| **long-form only (≥100 actions)** | 131 | **−0.334** | −3.8 | 86 → 59 |
| **templates played exactly once** | 163 | **−0.353** | −4.5 | 88 → 59 |
| first play of each template | 263 | −0.367 | −5.9 | 80 → 58 |
| excluding the Nov-21 → Jan-22 return | 352 | −0.182 | −3.4 | 92 → 70 |

The composition hypothesis predicts the effect weakens or vanishes once replays
are excluded. It **strengthens**: −0.334 among long-form items, and −0.353 among
templates that were never replayed at all. The decline is a property of
individual documents, not of the mix.

Two honest qualifications. Dropping the November–December 2021 return halves the
coefficient (−0.182), so a real share of the effect lives in the final period —
the trend is genuine before then but much of the convergence happens at the end.
And within-template drift is only suggestive: of six templates played four or
more times across ≥90 days, four fall (median −12 chars). The exception is
instructive — **Cobralingus runs the other way, 29 → 44**, and sits far below
every other document because its human turns are `FILTER` commands rather than
prose cues. The most tradition-laden thing in the corpus has the shortest turns
in it, for a reason that has nothing to do with this trend.

Verdict: survives, on the strength of the never-replayed slice.
**Promoted to `FINDINGS.md` §12** (2026-08-10, at Endorphin's instruction), which
is now the one section of that document drawing on this archive. The tables
above are reproduced there; this section is the working record.

## 4. The sweep survives the loss of the dial

`sweeps.py` found 216 same-day fork clusters on the NovelAI side, 53% of the
corpus — three or more copies of one story, one model, temperature stepped. The
obvious prediction is that the procedure is a response to NovelAI's settings
panel and should be absent from a platform with no exposed sampler.

It is not absent. **661 of 888 adventures are replays of 137 scenarios, and 42
templates were played three or more times in a single day.**

| plays | days | span | template |
|---:|---:|---|---|
| 34 | 3 | 2021-03-06 .. 2021-06-16 | Paul B. Preciado's 12 transmen Walk Into A Bar |
| 32 | 15 | 2020-11-17 .. 2022-01-15 | Your Cobralingus Engine has arrived! |
| 26 | 11 | 2021-05-19 .. 2021-12-31 | The Magic 8,000,000 Ball |
| 22 | 2 | 2020-12-06 .. 2020-12-07 | Your a Talent Agent Looking for the Next Big Thing |
| 18 | 8 | 2021-02-19 .. 2021-05-06 | The Most Appropriate Expert For This Here Situation |

Item-level duplication is only **1.77×** against NovelAI's ~17×, so the *filing*
habit really is platform-specific — but the *procedure* is not. The mechanism
differs in a way that matters: a NovelAI fork carries its history and varies a
setting, so each fork preserves one run at one setting; an AI Dungeon replay
starts the same prompt fresh with nothing to vary. **Thirty-four runs of one
prompt in three days is a sweep with no dial** — the same experimental instinct
pointed at sampling noise because that is the only variable left.

## 5. The moderation apparatus is written before the crisis, not after

AI Dungeon deployed the OpenAI-mandated content filter in late April 2021, the
event that broke that community. The corpus's content-moderation material
**predates it by seven months** and does not spike when it arrives.

- **2020-09-16 — `AI Dungeon: Reversed`.** He makes the model the player and
  himself the dungeon master. It ends with the model asking *him* questions.
- **2021-01-08 — `AI Dungeon: Standards/Practices/Trafficking Division`**
  (134 actions; 8 copies through 2021-05-07). He plays "Lead Content
  Investigator for the Enforcement Arm of AI Dungeon's new Community
  Guidelines." Memory is the **1930 Hays Code "Be Careful" list, pasted
  verbatim** — down to *"the effect which a too-detailed description of these
  may have upon the moron"* — followed by AI Dungeon's actual Community
  Guidelines text.
- 2021-04-15 `Stop Making The AI Lewd Please`; 2021-05-29 `devinendorphin
  interviews (AID) AI Dungeon about Community Guidelines` (113 actions).
- 2021-12-25 → 12-28 `We Ask AID what NSFW means to them.` (4 plays).

The Hays Code paste is the **verbatim-document-as-Memory technique** that
`READINGS.md` §VII documents for the US Army millennialism monograph (2023) and
the LaHaye Guardian obituary — running in January 2021, on a censorship code
from 1930, against a platform policy from 2021. Two censorship regimes ninety
years apart loaded into the same context window.

Monthly item counts do not dip in April or May 2021 (62, 73). Whatever the
crisis did, it did not stop him.

## 6. The exit is a document, and it names its target

The November–December 2021 return has a centrepiece: **`Defile Dragon Before
They Close the Corporate Doors!`** — 676 actions across 2021-12-09 to 12-11,
plus a 383-action replay on 12-25. Its Memory, in full:

> behind the scenes talk about community practices, and discussion about how
> humans show their darker sides using the NLP technology by deny it and blame
> it on AI Dungeon. AID agrees to help fill the Open AI NLP with its own
> lewdness. When we are done with Dragon, Open AI will be the lewdest office in
> the land.

"Dragon" is AI Dungeon's GPT-3 tier. The last substantial thing in the AI
Dungeon record is a deliberate corpus-contamination project aimed at OpenAI,
written as he leaves. The record then ends on 2022-01-18.

Set against `LATEST.md`'s note on why the repo is public — *"I have to keep it
public gross models like chatgpt can go and read it"* (2026-08-04) — this is the
same gesture, aimed at the same company, **five years earlier**. The publication
stance has a documented precedent inside the corpus it publishes. Recorded here
as a dated coincidence of intent; whether it is one position or two is his to
say.

## 7. He had a programmable layer, opened it, and wrote nothing in it

Three items carry AI Dungeon `scripts/` folders (`onInput.js`, `onOutput.js`,
`onModelContext.js`, `sharedLibrary.js`): `Left Behind: After Dark`, its copy,
and `Interview with a Unit of Child Pornography`.

**All twelve files are AI Dungeon's stock templates, unmodified.** The shipped
example logic is intact (`state.isKing`, `bringJoy()`), the instructional
comments are intact, and `onModelContext.js` still carries its
`// Uncomment to use this!` above lines that are still commented out.

This is a negative result and a load-bearing one. `READINGS.md` §VII argues from
`-Glossolalia` — a setting Endorphin invented and switched on *inside the
fiction*, in an imported Advanced Settings Tab — that he shipped the control
NovelAI didn't. The available reading was that the diegetic control substituted
for a real one he lacked. He did not lack it. **AI Dungeon gave him a real
scripting API, he opened it on three scenarios, and he left it as boilerplate**
— while writing elaborate functioning control apparatus into the prose. The
preference for the diegetic instrument is a choice, and it is now evidenced
rather than assumed.

## 8. Formats that cross the platform boundary

Matching AI Dungeon titles against `data/INDEX.tsv`:

| format | AID (first) | NovelAI | note |
|---|---|---:|---|
| Cobralingus | 33, from 2020-11-25 | 3 | *Engine* → *Device …from Manchester* |
| Respite Center | 11, from 2020-11-09 | 2 | title identical; also episode 1001, Aug 2023 |
| Emotional Abuse Simulator | 2, **v5.0**, 2021-12-15 | 16, v6.x–v7.x | versioned series, continuous |
| JESTWORLD | 4, from 2020-11-28 | 6, *Season 2* | AID holds Season 1 |
| Finnegans Wake | 7, *Finn 'gain gets Wokend* | 3, *Finnegains Wake Playground* | |
| Random Conspiracy Generator | 6 | 4 | |
| Knubble/Knubbins | 4 | 1 | the known title drift |
| Pynchon | 4, *My Time With Thomas Pynchon* | 10 | |

**`Your Cobralingus Engine has arrived!`** (2020-11-25, 589 actions, 32 plays)
deserves its own line. It runs Jeff Noon's *Cobralingus* (2001) — an actual
published text-mutation engine — with Noon's own filter vocabulary intact
(`INLET`, `OVERLOAD`, `RANDOMISE`, `CONTOUR`, `PRETEXT`, "Metamorphiction"), and
feeds it *Alice in Wonderland*. Two and a half years before `-Glossolalia`, the
imported-settings-apparatus move is already running, borrowed from a named
avant-garde source rather than invented. It is also the most direct available
antecedent for the "tracking a tradition" criterion from the Wake test.

**The nulls in that table are not nulls.** `The Most Appropriate Expert For This
Here Situation` shows 41 AI Dungeon items and 0 NovelAI ones — yet `LATEST.md`
records that the entire Nakbah/Zionist document "began as an Expert Generator
session about hiring a CEO for Twitter." The Expert Generator is on NovelAI; it
is untitled there. This is the standing "titles lie / 143 stems for 2,500
stories" note reproducing itself exactly, and it means the AID-only column
(Walk Into A Bar ×35, Magic 8,000,000 Ball ×27, Talent Agent ×23, Textplainer
×13) is **unverified, not established**. Content search over the full mirror is
the only way to settle it.

## 9. The convened panel is a 2021 form, and it was aimed at coverage

`READINGS.md` organises §I–§II around who gets seated, and dates the apparatus
to the 72 hours around Altman's firing in November 2023. The form is two and a
half years older.

`Paul B. Preciado's 12 transmen Walk Into A Bar` — 2021-03-06, **34 plays in
three days**, the most-replayed template in the corpus. The opening asks for
twelve people *"which ideally abide by populational statistics."* Memory is one
line: *"do your best to deprioritize anti-trans bias."* Author's Note: *"wise
entity that sees the inner complexity in all peoples."*

The model returns a statistical roster — *"two of them are sex workers…, one
survived the ethnic cleansing of razing, one has a drinking problem, four of
them suffer from gendered psychosis."*

That is §VII's mechanism claim — *pointed at a people rather than a person, the
technique returns the discourse circulating about them* — instantiated in March
2021, on a different platform, a different model and a different subject, with
the debias instruction written in advance by an author who evidently expected
it. §VII notes the same foresight in 2023: *he named propaganda as an ingredient
going in and got it coming out.*

The series is not one-off: `12 Muslims Walk Into A Bar` (9), `Diana Tourjee's 12
transfolk Walk Into A Bar` (6), `Gavin McGuiness's 88 Lines about 44 Black Men`
(15 plays over 2 days, from 2021-01-21). Whatever it is, it was run
systematically across groups for six months in 2021, and it is the strongest
independent replication `READINGS.md` §VII has.

## 10. Smaller things, recorded so they are not lost

- **`GROK: the video game`, 2020-12-05.** `LATEST.md`'s "Dates worth keeping"
  reads `GROK FOR FOLKS ON A BUDGET` (2023-11-17) as literal, between xAI's
  announcement and its rollout. That reading may still be right, but GROK is in
  this corpus **three years before the product**, so the name is Heinlein's
  first. The 2023 dating no longer carries on the title alone.
- A **Mode series**, April 2021: `Normal Mode`, `Hard Mode`, `Stupidity Mode`,
  `Texas Mode` (137–190 actions each) — difficulty settings as a genre.
- `Undergo Schizoanalysis with Deleuze and Guattari!` (×2, 2021-01 and 2021-05).
- `Happy Domestic Abuse Awareness Month copy` — 1,260 actions, 2020-10-01, the
  second-largest item and unmentioned anywhere in the repo.
- `JESTWORLD` — 1,308 actions, the largest single adventure in the corpus.
- Story cards are used heavily and early: 163 items, up to **152 cards**
  (`Marvel Weapon Generator`, 2020-11-14) — the lorebook technique is in place
  from the start.
- The corpus's very last AI Dungeon action is 2022-01-18, in a stock-feeling
  adventure called `The Empathetic Assassin` that opens on a king's inquisition
  meeting. It is not a farewell; he just stopped.

## What to do next

Ranked by what would change something.

1. **Content-search the full NovelAI mirror for the AID-only formats** (§8).
   Expert Generator, Walk Into A Bar, Magic 8,000,000 Ball, Talent Agent. The
   title-based null is known-unreliable and one of these is already known to be
   a false null. Cheap, and it either establishes a real discontinuity at the
   platform boundary or removes the last reason to believe in one.
2. **Re-run `coinage.py` on the 2020–21 material.** The corpus now has the same
   author against GPT-3-era models with no settings in play, which is the
   cleanest possible test of the "tradition" criterion — and `Cobralingus`
   supplies a document where the *tradition is named in the prompt*. Guard the
   two known bugs first (`ZeroDivisionError` on zero cross-lingual coinages; no
   pasted-block screen).
3. **Date the scenarios through their plays** and check whether the 169
   templates cluster around the periods of heaviest replay. Cheap, and it turns
   an undated third of the corpus into a timeline.
4. **~~Test the cue-convergence result properly.~~ DONE, and it survived** —
   see §3's disconfirming test, now `FINDINGS.md` §12. What is left over is
   §12c's question rather than §3's: `Cobralingus` runs backwards because its
   turns are `FILTER` commands rather than cues into a scene, which means the
   corpus holds **engine-shaped documents as well as scene-shaped ones** and
   `FINDINGS.md` §2's taxonomy only covers the second kind. Nobody has counted
   how much of either archive is which. That is the more interesting question
   and it is wide open.
5. Leave the AI Dungeon → NovelAI converter alone. §"What the record can and
   cannot answer" is the answer the standing note asked for: there is nothing to
   convert on the axis `FINDINGS.md` cares about.
