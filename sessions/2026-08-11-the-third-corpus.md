# 2026-08-11 — the third corpus

Endorphin pasted a Drive link — *"thats my google ai studio work. is there any
information here that use useful and insightful informs the other info from the
other corpora?"* — and the answer turned out to be yes, in a way that closes one
open disagreement, corrects the repo's account of its own name, and surfaces a
preservation emergency nobody here knew about.

## What it is

`1laFmZy2mcYwQyDHHy2_1vHqBciBkEoU4`, link-readable, **1,386 Google AI Studio
prompt sessions, 2025-03-27 .. 2026-06-21**, across 310 active days, plus ~590
screenshots, videos and `.txt` exports. `analysis/aistudio_export.py` written
this session; **`AISTUDIO.md`** is the full write-up. 1,098 files (everything
≤1.5 MB, 79 MB total) mirrored and analysed; **288 skipped for size**, and
`--report` lists them so they are never silently missing from a count.

The Drive MCP returns these base64-encoded and one at a time; the folder answers
`embeddedfolderview` with HTTP 200 and all ~1,978 children in one request, and
`drive.usercontent.google.com/download` returns them as plain JSON. The whole
mirror cost no model tokens. **Try the curl path before the MCP for any Drive
folder in this project.**

## The record is a different shape again, and mostly a better one

`CLAUDE.md`'s instruction for the AI Dungeon side — write up what each record
can and cannot answer *before* designing a join — applied here first.

Richer than NovelAI in four ways:

- **`finishReason`, and no truncation at all.** `maxOutputTokens` is 65,536 in
  1,043 of 1,088 sessions and there is **not one `MAX_TOKENS` finish** in 4,285
  model output turns. Priority 5 in `LATEST.md` asks whether enough stories exist
  where the cutoff was large enough not to compel the next turn. There are about
  a thousand, on a platform that records the answer per turn.
- **Thinking traces** — 3,734 chunks, 12.8 M characters of model reasoning
  preserved next to the output it produced. Nothing like it in either other
  corpus.
- **Multimodal input** — 310 images, 97 YouTube videos, 45 Drive videos, 529
  grounding blocks. First place the broadcast layer and the generation layer meet
  inside one record.
- **Partial branch structure** — 245 `branchParent` chunks, plus `Branch of …`
  sibling files nesting up to ten deep. Weaker than NovelAI's undo tree, strictly
  more than AI Dungeon's flat sequence.

Poorer in one that matters: **no chosen/rejected pairs.** §7's containment
measure has no analogue here.

## The disconfirming test, run as instructed, and it disconfirmed

`READINGS.md` §III argues the temperature dial from NovelAI's settings
distributions; `sweeps.py` finds the ladder across 53% of that corpus, topping
out at the maximum in 42% of clusters. The primed expectation was that the sweep
is Endorphin's procedure and would show up wherever he worked.

It does not. On AI Studio temperature is a **switch**: 586 sessions at 1.0, 469
at 2.0, 33 everywhere else combined. Only 11% of title stems have a second
member. Of 103 branch families, 68 hold temperature identical and 22 of the
remaining 35 vary it as the bare pair (1.0, 2.0); graded ladders appear four
times in the whole corpus.

The taste for the maximum survives and §III's reading of it stands. The
*procedure* does not, and **"never group by story id" must not be carried
across** — it was earned on a duplication habit this platform does not have.

## The sixth instance of the standing note, caught by the tool written to catch it

First pass reported **model:human 9.9:1** and a story about the late era. Wrong.
`isThought` chunks carry `role: "model"`, and they are **38% of all model text**.
Excluding them gives **6.13:1** — which is the Kayra figure (6:1) to two
significant figures.

That inverts the reading. `LATEST.md` records the human/model ratio flipping to
0.7:1 in the GLM-4.6 fork of the Nakbah document and notes nobody checked whether
it generalised. It does not: AI Studio runs in the same period at the Kayra
ratio, so **the GLM-4.6 fork is the outlier**, and the inversion belongs to that
document rather than to the era.

Same shape as counting pasted LLaMA 2 as Endorphin, one platform over, and
easier to make because the platform labels the reasoning as the model's.

## Tantura

`LATEST.md` carried this as unanswered: his in-session reading that the account
was *"stymied… like it was skipped in preprocessing"* rests on one null from a
13B model in degenerating text. Claude said the conclusion outran its evidence
and Endorphin had not replied.

He had already replied, in August 2025, by running it again. `Witnesses of the
Nakba` — `gemini-2.5-pro`, temperature 2.0, topP 0.99, topK 64 — is the same
Expert Generator opening, the same sequence (life before → where did the Zionists
come from → the Nakba itself → the one-word probe), and says so in-session:
*"This is the third iteration of this scenario."*

The `Tantura` turn returns 7,400 characters across three witnesses. The coastal
fishing village south of Haifa; late May 1948; the men separated and taken to the
beach by the cemetery; the fisherman with empty eyes; *"Deir Yassin was the
warning. Tantura was the confirmation."* The scholar persona: *"the perfect and
most obscene symbol of both the event and its subsequent denial. It's a case
study in erasure."*

**The record was retrievable. The 2023 model could not retrieve it.** The
preprocessing reading does not survive its own author's rerun. The method does —
this is precisely the standing note *before generalising from a session, ask what
a rerun on other equipment would do*, and he built the rerun before the note
existed.

The two-nulls-two-causes note is untouched: the October 2023 probe returned genre
filler because the record did not yet exist anywhere.

## Three things the repo had wrong or missing

**The name.** `CLAUDE.md` said *"the name is the name."* `ALMO Interview:
Endorphin` (2025-04-11) lists Absurdly Large Media Objects by size and files, at
`+1600 hours of video`, **"devinendorphin's dextromethorphan varAIety hour / AKA
This show!!!"** — `AI` spelled into *variety*, and the hour count matching
`EPISODES.tsv`'s 1,604 broadcasts. The referent is the broadcast layer. The same
document gives his own written definition of the Counterfactual Interview
(*"trusting that the aggregate vibes of billions are enough variation to assume a
field… enough of the core spiritus software to make the resulting conversation as
accurate as anything else"*), fifteen months before §IV, and places ALMO inside a
cyborgism/Janus vocabulary — *the Dreamtime*, *Bach faucets*, ALMOs shifting
*"the priors of self-supervised models"* — that the archive was never credited
with.

**The precedent.** `Novel Project: A Failed Attempt` (2025-04-27) opens by
pasting the entire first movement of **"The Book of Ephraim"** from Merrill's
*The Changing Light at Sandover* under `Continue the prompt:`. A poet
transcribing dictation from a device, named voices arriving uninvited, the human
as scribe rather than author, and an explicit worry about whether the transcript
is literature. Better than Derrida-on-iterability as the next lens, because he
was already reading it. He returns to it in `Digital Séance: LLM, Merrill, and
Ephraim` (2026-01-28). Same experiment as the Wake exercise one month earlier —
Joyce 03-27 via Cobralingus, Merrill 04-27.

**The channel.** Four December 2025 sessions are an attempt to get `@glubose`
reinstated after a spam flag, arguing from *"1700 dated Video files"* as
*"non-fungible proof of what these machines (GPT-3/AI Dungeon) were capable of or
said on specific days."* The diagnosis in-session: TTS audio triggering
"Non-Original/Repetitive" filters, hallucinogenic imagery correlating with
ad-farm slop, and the keywords `GPT` / `AI Dungeon` / `Models` sitting in a space
now saturated with scams — *"The context AI cannot tell the difference between
philosophy about technology and tech-scams."* Item 7 read the 1646-vs-1,604 gap
as attrition. It may be enforcement. **Ask him what happened.**

## Also, and it closes an Urgent

**`New Story 5` is not lost.** `New Story (5) (2026-01-22T02_15_50.232Z).txt`,
**221,587 bytes** — matching the §VI source's 221,587 chars exactly — is in this
folder. The re-export-as-JSON ask still stands; the loss risk does not.

## Left undone

- **288 sessions unread for size**, including `Finnegans Wake Diorama at Armory`
  (44.9 MB), `A Crying of Lot 49 Diorama` (35.7 MB), `Rewriting Finnegans Wake
  Simply.` (33.2 MB), `PFCizer Syllabus: Project Glass House` (14.2 MB),
  `Simulating Counterfactual Interviews.` (10.9 MB). Two more Wake sessions and a
  Pynchon one are the obvious next `coinage.py` material — the same test on a
  third model.
- **The 15 AI Dungeon sessions are unread.** They are the only commentary on the
  unanalysed corpus and should be read before any join is designed.
- **The thinking traces are untouched** as an object. 12.8 M characters of stated
  reasoning next to the output is a new kind of evidence for the collaboration
  disagreement, which is still open and should stay open.
- **`Cobralingus Engine: Filter Gates`, 2025-03-27 04:02 UTC**, is the first
  session in the corpus: Jeff Noon's metamorphiction engine transcribed with all
  fourteen filter gates, run on the opening of the Wake. Read against §VII's
  `-Glossolalia` argument — this is him importing someone else's invented control
  panel two years after building his own.
