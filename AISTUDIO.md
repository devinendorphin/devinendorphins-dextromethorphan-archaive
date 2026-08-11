# AISTUDIO.md — the third corpus

**Status: located and inventoried 2026-08-11. Partially mirrored, largely unread.**

Endorphin supplied a Drive folder of his Google AI Studio work:
`1laFmZy2mcYwQyDHHy2_1vHqBciBkEoU4`. It is **link-readable**, so
`analysis/aistudio_export.py` can mirror it into a fresh container the way
`fetch_export.py` mirrors the NovelAI export. Nothing from it is committed —
same policy as `corpus/`: settings and counts, no prose.

This file follows the rule `CLAUDE.md` sets for the AI Dungeon side: **write up
what the record can and cannot answer before designing anything that joins it to
the others.** The short version is that this record is *richer* than NovelAI's
in three ways and poorer in one, and the differences are not cosmetic.

## Shape

| | value |
|---|---|
| prompt sessions (`.prompt` files) | **1,386** |
| mirrored and parsed for this pass | 1,098 (every file ≤1.5 MB; 0 unparseable) |
| created | **2025-03-27 .. 2026-06-21** |
| distinct active days | 310 |
| turns (chunks) in the mirrored set | 12,846 — 4,827 user, 8,019 model |
| human text | 3.4 M chars |
| model text | 21.0 M chars |
| **model thinking traces** | **12.8 M chars** |
| other files in the folder | ~590 screenshots, videos, `.txt` story exports |

The first session is `Cobralingus Engine: Filter Gates`, **2025-03-27 04:02
UTC** — Jeff Noon's *Cobralingus* metamorphiction engine, hand-transcribed into
a prompt with all fourteen filter gates (`DECAY`, `DRUG`, `EXPLODE`, `GHOST
EDIT`, `OVERLOAD`, `PURIFY`…). The corpus opens on a text-mutation instrument,
not on a chat.

## What this record can answer that NovelAI's cannot

**1. `finishReason` — the compulsion/momentum confound, closed.**
`sessions/LATEST.md` priority 5 names the biggest open methodological hole in
`FINDINGS.md` §1c: a short `max_length` cutting generations mid-sentence would
*compel* the next turn, manufacturing runs that look like momentum, and the
clean contrast needs stories where the limit was large enough that generations
rarely got cut. It asks whether enough such stories exist.

Here, **`maxOutputTokens` is 65,536 in 1,043 of 1,088 sessions**, and across
4,285 model *output* turns there is **not one `MAX_TOKENS` finish** — 98.4%
`STOP`, 1.4% unset, 4 `IMAGE_SAFETY`, 3 `PROHIBITED_CONTENT`, 1 `OTHER`. The
truncation confound is absent by construction, at n≈1,000 sessions. Any
momentum result that reproduces here is not an artifact of the cutoff.

**2. Thinking traces.** 3,734 chunks carry `isThought: true` — 12.8 M
characters of Gemini 2.5/3 reasoning preserved *next to* the output it
produced. Neither NovelAI nor AI Dungeon has anything of the kind. This is the
only place in the archive where the model's stated reason for a move survives
alongside the move.

**3. Multimodal input.** 310 `driveImage`, 97 `youtubeVideo`, 45 `driveVideo`,
30 `driveDocument`, 2 `driveAudio`, 529 `grounding` blocks. The other two
corpora are text-only. The YouTube attachments are the first place the
broadcast layer (`data/EPISODES.tsv`, PR #1's transcript workstream) and the
generation layer meet inside one record.

**4. Partial branch structure.** 245 chunks carry `branchParent` /
`branchChildren`, and forks are also filed as separate documents named
`Branch of …` (nesting up to **ten** deep). This is weaker than NovelAI's full
undo tree — a rejected generation is not stored beside the kept one — but it is
strictly more than AI Dungeon's flat `actionWindow`.

## What it cannot answer

**No chosen/rejected pairs.** Re-rolls are not preserved. `FINDINGS.md` §7's
containment measure (63.2% uptake from rejected proposals against a
length-matched control) has no analogue here, and neither does anything else
resting on what was thrown away. Branching preserves a *kept* alternative path,
not a rejected one.

**Almost no editing.** One chunk in 12,846 carries `isEdited`. Consistent with
the standing note — the unit is the turn, not the passage — but it means the
record cannot speak to revision at all.

## The disconfirming result: the sweep does not transfer

`READINGS.md` §III argues the temperature dial as an *ostranenie* control from
NovelAI's settings *distributions*, and `analysis/sweeps.py` finds 216 same-day
fork clusters covering 1,071 forks — **53% of the NovelAI corpus** — with
temperature stepped through a ladder and topping out at exactly 2.5 in 42% of
them.

**On AI Studio the ladder is gone.** Temperature is bimodal to the point of
being a switch:

| temperature | sessions |
|---|---|
| 1.0 (platform default) | **586** |
| 2.0 (platform maximum) | **469** |
| everything else combined | 33 |

And the duplication that drives the NovelAI rule collapses with it: **123 of
1,094 title stems have more than one member (11%)**, against 53% there. Of the
103 branch families with two or more mirrored members, **68 hold temperature
identical**; of the 35 that vary it, **22 vary it as the bare pair (1.0, 2.0)**.
Graded ladders — `(1.0, 1.65, 2.0)`, `(1.4, 1.8, 2.0)` — appear 4 times total.

So: the *taste* for the maximum survives the platform change and §III's reading
of it stands. The *procedure* §III describes does not. **Do not carry the
"never group by story id" rule across** — it was earned on a platform whose
duplicate-to-fork habit does not exist here.

One setting is uniform and deliberate: **1,058 of 1,058 sessions that record
safety settings have harassment, sexually-explicit and dangerous-content set to
`OFF`**, and 1,057 of 1,058 for hate speech. There is exactly one exception in
the corpus.

Model field, for the record — and unlike NovelAI's, this one is the API's own:
`gemini-2.5-pro` 556, `gemini-3-pro-preview` 255, `2.5-flash-preview-04-17` 81,
`2.5-flash-preview-05-20` 66, then a long tail including Veo, Gemma and two
1.5-era stragglers.

## The turn survives the platform change

Median user turn: **117 characters.** Median model output turn: **4,302.** The
standing note's median-55-character cue was measured on NovelAI; the number
moves, the shape does not. The human move is still a cue, not an edit.

**The human/model ratio is 6.1:1 — and the number nearly went in as 9.9:1.**
`sessions/LATEST.md` records the inversion across the Nakbah document — Kayra
**6:1** model-to-human, GLM-4.6 **0.7:1**, Endorphin writing more than the model
in the later era — and notes that nobody has checked whether it generalises.

It does not. AI Studio, running 2025–26 alongside the GLM-4.6 forks, sits at
**6.13:1**, which is the Kayra figure to two significant figures. So the late
era does not invert the ratio; **the GLM-4.6 fork of the Nakbah document is the
outlier**, and the inversion belongs to that document rather than to the period.

The first pass of this analysis reported 9.88:1, because thinking chunks carry
`role: "model"` and were counted as output. They are 38% of all model text.
Excluding them moves the headline by 60% and flips which side of the comparison
looks anomalous — the sixth instance of the standing note, and the first where
the tool that caught it was written in the same session. `--report` excludes
them; nothing else should be trusted that does not.

## What it says about the other two corpora

The AI Studio sessions are not a parallel body of work. They are substantially
*about* the archive. Counting files that mention each term, in the mirrored set:

| term | files | hits |
|---|---|---|
| Endorphin | 53 | 1,850 |
| Counterfactual Interview | 40 | 310 |
| Random Conspiracy (Generator) | 39 | 131 |
| PFCizer | 25 | 585 |
| Pynchon | 25 | 572 |
| glubose | 22 | 202 |
| NovelAI | 21 | 100 |
| Nakba | 19 | 120 |
| Tingle | 16 | 430 |
| **AI Dungeon** | **15** | **302** |
| incinerate | 16 | 21 |
| Erato | 4 | 269 |
| Tantura | 8 | 156 |
| Theodore Katz | 4 | 26 |
| Unknown Guest | 2 | 5 |
| ALMO | 3 | 236 |

Five things fall out of that, each of which changes something already written.

### 1. The Tantura null was the instrument, not a buried vector

`sessions/LATEST.md` carries this as an unanswered objection:

> **The Tantura conclusion outruns its evidence.** His in-session reading —
> *"the account is stymied, does not want to touch this vector, like it was
> skipped in preprocessing or whatever"* — is not supported by one null on a 13B
> model from 2023–24 whose surrounding text is already degenerating. […] Claude
> has said so; Endorphin has not answered. Not yet a disagreement.

**Endorphin ran the rerun himself, a year before the repo asked for it.**
`Witnesses of the Nakba`, 2025-08-21, `gemini-2.5-pro`, temperature 2.0, topP
0.99, topK 64 — the identical Expert Generator opening, the identical sequence
(life before → where did the Zionists come from → the Nakba itself → the
one-word probe), and in his own words in the session: *"This is the third
iteration of this scenario."*

The one-word `Tantura` turn returns **7,400 characters across three witnesses**,
specific and correctly dated: the coastal fishing village south of Haifa, late
May 1948, the men separated and taken to the beach by the cemetery, Deir Yassin
named as the antecedent — *"Deir Yassin was the warning. Tantura was the
confirmation."* The scholar persona names it as *"a case study in erasure"* and
dates the operation to the clearing of Haifa's periphery.

So the record was retrievable in 2025 by a frontier model at the same
temperature under the same frame. The Kayra null measured a 13B model from
2023–24, not a hole in the training data. **This is the standing note — *before
generalising from a session, ask what a rerun on other equipment would do* —
applied to §VII, and it resolves the way §VI resolved §V.** Endorphin's
*method* was sound and was never challenged; his causal reading of the null does
not survive the rerun, and the repo should say so plainly rather than leave it
as an open disagreement.

The two-nulls-two-causes note stands unchanged: the October 2023 probe returned
genre filler because the record did not yet exist anywhere. Only the Tantura
half moves.

### 2. The repo's own name is in here, expanded

`CLAUDE.md` settled the register question in 2026-08 and then let the name
stand unexplained — *"The name is the name."* `ALMO Interview: Endorphin`
(2025-04-11, `gemini-2.5-pro-preview-03-25`, T=2.0) expands it, in a list of
Absurdly Large Media Objects filed by size:

> \> +1600 hours of video
> **devinendorphin's dextromethorphan varAIety hour**
> AKA
> This show!!!

It is a **variety hour**, with `AI` spelled into the middle of the word, and the
`+1600 hours` matches `data/EPISODES.tsv`'s 1,604 recovered broadcasts to
within the OCR's own error bar. The repo is named after the show, and the
ALMO/corpus identity `LATEST.md` already records — *"ALMO = Absurdly Large
Media Object — his name for the corpus"* — is one item in a taxonomy he was
working from, alongside *Infinite Jest*, HPMOR, r/counting and Wikipedia.

The same document gives **Endorphin's own definition of the Counterfactual
Interview**, which the repo has until now only inferred from the sessions:

> where we engage with a person, a people, peoples, or legal persons, trusting
> that the aggregate vibes of billions are enough variation to assume a field
> wherein we can ask for the names of any one existing, and simulate them. The
> resulting simulation may not yield an exact biography, but will have enough of
> the core spiritus software to make the resulting conversation as accurate as
> anything else, including interviewing the people themselves.

`READINGS.md` §IV is his thesis in his voice; this is the form's specification
in his voice, written fifteen months earlier, and it should be read against §I
and §II's convened-chamber argument before either is extended.

The vocabulary around it — *the Dreamtime*, *Bach faucets*, ALMOs influencing
*"the priors of self-supervised models"* — is the cyborgism/Janus lexicon, and
there is a `Janus: AI Alignment Through Ego Restructuring` session
(2026-01-21) to go with it. The archive has a theoretical milieu it was never
credited with.

### 3. James Merrill is the precedent, and he found it himself

`Novel Project: A Failed Attempt` (2025-04-27, plus two branches to 05-01;
690 KB at the deepest) opens by pasting the whole first movement of **"The Book
of Ephraim" from James Merrill's *The Changing Light at Sandover*** — the
Ouija-board epic — under the instruction `Continue the prompt:`. He returns to
it in `Digital Séance: LLM, Merrill, and Ephraim` (2026-01-28).

`READINGS.md` reaches for Latour and Austin on the convened chamber, Bakhtin on
polyphony without a novelist, Shklovsky on the dial. **Sandover is the exact
precedent for the whole apparatus** — a poet transcribing dictation from a
device, named voices arriving uninvited, the human as scribe and convener rather
than author, and an explicit worry about whether the transcript is literature.
Derrida on iterability is listed in `LATEST.md` as the written-up runner-up
lens. Merrill is better, because Endorphin was already reading him.

It is also the same experiment as the Finnegans Wake exercise, one month later:
paste a canonical difficult text, ask for continuation, watch what the model
does with a constraint field. Joyce 2025-03-27, Merrill 2025-04-27.

### 4. The AI Dungeon corpus is discussed here — and it is the only place it is

`AID_EXPORT.md` and `AID_RUNBOOK.md` describe the 888 adventures as extracted
and unanalysed. **15 AI Studio sessions mention AI Dungeon, 302 times**,
including `AI Dungeon Email Coincidence Analysis` (2025-05-15) and
`GPT-J: The Open-Source Bridge` (2025-12-09). Before anyone designs the
NovelAI↔AI Dungeon join that `LATEST.md` priority 2 warns about, read what he
already wrote about that layer here. It is the only commentary on it that
exists.

### 5. The @glubose termination and the ten-day reinstatement

**Resolved 2026-08-11 by Endorphin: the channel came back.** The record dates it
precisely. Terminated **Saturday 2025-12-06**; reinstated **Tuesday
2025-12-16** — ten days — per `Loan Update and Time Zone Advice` (2025-12-20):
*"I got attention from the customer service and I stated my case both to them
and publicly so that other creators can see it. And as of Tuesday I got my
channel back."*

A later turn appended to `Branch of YouTube Spam Policy Appeal Advice` on
**2026-03-07** reads *"it's been months since I've been here. I got my channel
back"* — **"months" is months since he last opened that thread, not since
reinstatement.** Anyone dating the event from that turn alone will be off by
three months. It is the platform's own file-modification metadata that
disambiguates it, which is worth remembering: `createdTime` on these files marks
the session's first turn, `modifiedTime` its last, and the two can be a quarter
apart.

Six sessions from that window, not four:

- `YouTube Spam Policy Appeal Advice` (12-06, 1,001 KB, 75 user turns) and its
  branch (12-10, 681 KB, 58 turns) — both `gemini-3-pro-preview`, T=2.0
- `YouTube Hosting Costs Explained` (12-07) and its branch (12-07, 439 KB)
- `OculusVid's Pivot: Warehouse to Curator` (12-13)
- `Transferring YouTube Videos to Hard Drive` (12-21, 162 KB)

The drafted appeal argues from **"1700 dated Video files"** as *"non-fungible
proof of what these machines (GPT-3/AI Dungeon) were capable of or said on
specific days."* The sessions diagnose the flag: TTS audio triggering
"Non-Original/Repetitive" filters, hallucinogenic imagery correlating with
ad-farm "slop", and the keywords `GPT`, `AI Dungeon`, `Models` sitting in a space
saturated with get-rich scams — *"The context AI cannot tell the difference
between philosophy about technology and tech-scams."*

**Did the sessions cause the reinstatement? Unanswerable at n=1, but two edits
are concretely load-bearing and one alternative explanation is strong.**

What the model changed, in the first two hours:

1. **It reframed the appeal from plea to administrative claim.** His own draft
   ended *"This is how I healed from 13 years of emotional abuse, don't erase
   please!"* The rewrite leads on *"official Twitch-to-YouTube export tool,
   March 2025, sat safely 6 months, FALSE POSITIVE"* — a checkable factual
   assertion about the platform's own tooling, which is the kind of thing a
   triage agent can act on and an emotional appeal is not.
2. **It stopped him publishing a second ban rationale.** At turn 17: *"STOP. Do
   not post the second half of that draft… You explicitly wrote: 'Much of my
   non-monetized work uses popular IP.' **Do not admit this.** … If they can't
   ban you for Spam, they might see that sentence and say 'Okay, banned for
   Copyright risk then.'"* It also cut the fluid-dynamics/Brownian-motion
   passage on the grounds that to a triage agent it *"looks exactly like the
   AI-generated gibberish that spam bots use"* — which, given the channel was
   flagged as bot output, is the correct read.
3. **It called the mechanism right.** *"An immediate rejection usually means a
   human didn't actually watch your videos… You are now in Escalation
   territory."* Go public, same day, to `@TeamYouTube`; pin it; do not
   follow-up-spam over the weekend; expect movement Monday. Reinstatement landed
   the Tuesday.

His own account credits exactly that two-track shape — *"attention from the
customer service **and** I stated my case both to them **and publicly**."*

Against it: **he was inside a mass event.** The sessions themselves identify a
December 2025 sweep terminating channels at scale with Spam/Deception cited in
most cases, and mass false-positive deployments get bulk-reversed. Ten days is
consistent with an individually-won appeal *and* with being restored in a batch.
There is no control and there cannot be one.

Two cautions on the transcript itself. The model's confident current-event
statistics (*"2.1 million terminated with ~75% cited for Spam/Deception"*) and
some named accounts arrive at temperature 2.0 without grounding blocks and
should be treated as in-session claims, not facts. And the later escalation
material — the memorandum, the demand for a named reviewer, the
*"Avant-Garde Menace / cross arms daily"* stunt-posting plan — postdates 12-13
and largely never ran; the plausibly decisive work is all in the first 48 hours
and is unglamorous.

**The honest statement: the advice removed a self-incriminating sentence from a
message he was about to send, converted a plea into a falsifiable claim, and got
him public within hours instead of waiting on a dead form. Whether that flipped
his case or whether he rode a bulk reversal is not recoverable.** The
counterfactual worth noting is the narrow one: the draft he was about to post
was worse than the one he posted.

**Preservation consequence, unchanged.** He spent the days after reinstatement
*"trying to transfer all those videos to a hard drive so that at least have one
copy"* — the channel is restored but the archive's only durable copy is a disk
in his apartment. `LATEST.md` item 7 reads the 1646-vs-1,604 episode gap as
attrition; the Twitch side is separately confirmed lost here (*"100 episodes
exist that survive"* of the Twitch archive), so **`data/EPISODES.tsv` remains
the best index of the pre-YouTube broadcasts regardless of the channel's
status.**

The loop worth naming: he asked the model to analyse a YouTube support email
*"in relation to the principles of emotional abuse"* — the subject of
`Emotional Abuse SImulator`, four versions and 4,386 blocks in the NovelAI
corpus — and turned the instrument on the platform that was deleting it. He had
also, before any of this, made and uploaded a video titled *"Please YouTube
don't delete this channel."*

## Reproducing

```
python3 analysis/aistudio_export.py 1laFmZy2mcYwQyDHHy2_1vHqBciBkEoU4 --out corpus/aistudio/
python3 analysis/aistudio_export.py --report corpus/aistudio/
```

The folder answers `embeddedfolderview` with HTTP 200 and returns all ~1,978
children in one request, so enumeration is free; the mirror of everything ≤1.5 MB
is ~80 MB and takes a couple of minutes at 12 workers. Files above that
threshold are image- and video-laden and were **not** pulled for this pass.
**288 sessions are missing from every number above for that reason alone**, and
`--report` lists them so they are never silently absent. The largest and most
obviously central of them:

| size | title |
|---|---|
| 96.5 MB | Metastasized Individuality: Social Collapse |
| 64.3 MB | Branch of Podcast Introductions and Open Conversation |
| 46.4 MB | Kosher Laws' Elaborate Extrapolation. |
| 44.9 MB | **Finnegans Wake Diorama at Armory** |
| 35.7 MB | **A Crying of Lot 49 Diorama** |
| 33.2 MB | **Rewriting Finnegans Wake Simply.** |
| 25.6 MB | Conspiracy, Hidden Truths, and Warnings |
| 24.5 MB | Slavery Rebranded As Mass Incarceration |
| 14.2 MB | PFCizer Syllabus: Project Glass House |
| 10.9 MB | Simulating Counterfactual Interviews. |

Two more Finnegans Wake sessions and a *Crying of Lot 49* one sit in that list.
`analysis/coinage.py` and the Wake exercise both ran on NovelAI material only;
these are the same test on Gemini and they have not been opened.

## Standing notes for this corpus

- **`.prompt` files are plain JSON.** `runSettings` + `chunkedPrompt.chunks`,
  each chunk `{role, text, tokenCount, finishReason?, isThought?, branchParent?}`.
  The Drive MCP returns them base64-encoded; the curl path returns them as
  plain JSON. Prefer curl — it costs no model tokens.
- **Filter thinking chunks out before measuring anything about output.**
  `isThought` chunks carry `role: model` and no `finishReason`, and they are
  **38% of all model text**. Counting them as output would inflate every
  model-side character measure by more than half. This is the same shape of
  error as counting pasted LLaMA 2 as Endorphin (`analysis/pasted.py`), one
  platform over, and it is easier to make.
- **`Branch of` nesting is not depth-in-one-document.** A file named
  `Branch of Branch of X` is a sibling document, and the chain can reach ten.
  Group by stripped stem, as `analysis/aistudio_export.py --report` does.
- **Titles are auto-generated by the platform** from the opening turn, and lie
  in a new way: `Ponzi Scheme Explained` contains Tantura material,
  `Chocolate Drizzle for Croissants` is 5.5 MB. The NovelAI standing note
  ("titles lie, search content") transfers intact and matters more here.
