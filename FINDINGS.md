# Findings

**2,016 NovelAI story files.** Last edited between March 2023 and July 2026,
created as far back as **June 2021** — 163 predate 2023, 39 are from 2021.
280M characters of model output against 88M of human text. 1,798 of the files
contain at least one generation; the remaining 218 are pasted articles,
text-to-speech scratchpads and empty stubs.

What makes this a corpus rather than a folder of stories is the last number:
**760,611 edit-history blocks.** NovelAI exports the entire undo tree, not the
finished text. Every generation that was kept, rewound past, or typed over is
still in the file, stamped with who wrote it, which model made it, and what the
sampler was set to.

## The frame

The first four analysis passes asked a question it turns out nobody was asking:
*what made this generation good enough to keep?* Every version of it came back
null or artifactual. The fifth pass read one session end to end and found out
why.

Across **134,063** human blocks that immediately follow a generation:

| length of the human block | count | share |
|---|---:|---:|
| under 50 characters | 62,267 | **46.4%** |
| 50–200 characters | 59,770 | 44.6% |
| 200–600 characters | 8,935 | 6.7% |
| 600+ characters | 3,091 | **2.3%** |

**Median 55 characters.** Ninety-one percent under 200. One in forty is long
enough to be a substantive rewrite.

These are not edits. They are **turns**. The corpus records an exchange
conducted at speed — much of it performed live on stream, with the text read
aloud by text-to-speech — in which the author's move is usually a cue, a name, a
question, or a character walking on stage, and the model's move is to perform
whatever just arrived.

`CASE_STUDY.md` traces one session in full. It pastes Utah HB 249 verbatim — a
statute preemptively denying legal personhood to artificial intelligence,
inanimate objects, bodies of water, land, real property, atmospheric gases,
astronomical objects, weather, plants, nonhuman animals, and "any other member
of a taxonomic domain that is not a human being" — then convenes a press
conference at which each enumerated category sends a representative, calling the
model first to assert its own personhood. Its shape after setup is 27 generation
runs, each terminated by exactly one human block of 15 to 194 characters:

> Solaris, a body of water: Sorry I'm late!
> Omouamoua - Hiiii-ye!
> Light Drizzle: Hi, I was the only weather that was free to come. The others send their regards.

Everything below is organised around that frame. Where an earlier reading
survived it is stated plainly; where the frame overturned one, the overturned
version is kept, because how these metrics failed is the most transferable thing
in the project.

**Epistemic status.** Descriptive statistics over one person's practice. Not a
sample of anything, and not a benchmark — §7 works through why that is
structurally impossible here. Everything regenerates from `analysis/`, where the
tests that killed claims are kept alongside the ones that survived: `PROBES.md`,
`PAIRS.md`, `LEARNABLE.md`, `STOPPING.md`, `REGISTER.md`, `TAKEOVER.md`,
`TABLES.md`.

---

## 1. When the turn passes back

**476,839** generations sit on surviving branches, each labelled by whether the
next thing on that branch was another generation or the author typing. The
author takes a turn **28.1%** of the time (79% new text, 21% in-place edits).
Three things govern when.

**1a. Punctuation — the strongest single fact in the corpus.**

| the generation ends | generations | author takes a turn |
|---|---:|---:|
| on sentence-final punctuation | 305,197 | **37.5%** |
| mid-sentence | 171,642 | **11.5%** |

The intuition — a generation that breaks off mid-clause is defective, so you
step in — is not merely wrong but inverted, by more than 3×.

A clean ending is an **invitation**; a mid-clause cut is a **compulsion**. When
the model stops on a full stop it has handed the turn back, and that is where a
human takes it. When it stops mid-clause the only graceful move is to press
enter again — especially with the text being read aloud, where a hanging clause
is worse than silence.

**1b. Dead air.** Much of this was streamed with TTS reading the output, and a
passage had to be ready before the voice ran out. That predicts a length effect
with a specific sign, and it is there. Bucketed by how long a passage takes to
read aloud at 155 wpm:

| speech seconds | generations | author takes a turn |
|---|---:|---:|
| 0–5 | 6,319 | **45.8%** |
| 5–10 | 7,595 | 42.2% |
| 30–45 | 269,116 | 26.3% |
| 90+ | 1,599 | **22.8%** |

A generation yielding a few seconds of audio does not buy enough time, and the
author has to fill it. Not run position in disguise: holding position fixed,
short (<20s) exceeds long (≥45s) at each of the first five positions, by +10.0,
+4.7, +11.3, +2.6 and +6.9 points. The middle of the range is non-monotonic
(10–20s sits below 20–30s), so the effect is real at the extremes rather than a
clean gradient.

**1c. Momentum.** Among generations reaching position *k* of an unbroken run,
the share that ended it:

| position in run | generations | turn passes back |
|---|---:|---:|
| 1 | 135,103 | **39.4%** |
| 3 | 54,527 | 30.8% |
| 5 | 27,042 | 23.1% |
| 9 | 11,026 | 15.4% |
| 20 | 2,132 | **5.4%** |

A memoryless process would be flat; this falls sevenfold. Long runs are a
genuinely different mode.

The honest caveat is that 1a and 1c are entangled. A short `max_length` cutting
generations mid-sentence would *compel* the next one, manufacturing runs that
look like momentum. The corpus cannot separate them: `max_length` is stored per
story, like every setting, so the per-generation truncation that would decide it
is not recorded.

**1d. And the words do not matter.** A TF-IDF classifier over the generation's
own text, grouped by text content so the duplication leak in §6b cannot recur:

| predictor | AUC |
|---|---:|
| TF-IDF over the full text | 0.623 |
| **does it end on sentence-final punctuation** | **0.647** |
| length alone | 0.559 |

**A single bit beats every word in the passage.** Under the rejection frame this
was baffling. Under the turn-taking frame it is nearly tautological: the human
move is not a verdict on the passage, so no property of the passage predicts it.
What predicts it is whether the turn was handed back.

## 2. The shape of a session

**135,567** unbroken runs of generation with no human text between them.

| run length | share of runs |
|---|---:|
| 1 | 39.6% |
| 2–3 | 32.6% |
| 4–9 | 20.9% |
| 10–24 | 5.9% |
| 25+ | 1.0% |

Median 2, p90 7, p99 24, maximum **212**. That longest run is *I Remind The Body
Electric*, created **April 2022**, surviving in six duplicates under six
different model settings — the same seed text re-run through successive models
as they shipped.

Turn size varies more than 2× by model. Median characters accepted per
generation: 419 (Euterpe) → 469 (Kayra) → 601 (Clio) → 668 (Krake) → 776 (GLM)
→ 944 (Erato). Partly the `max_length` budget (100 → 250 tokens), partly leash.

Those long runs are also the cleanest experimental material in the corpus: 212
consecutive generations with no human intervention is a single-condition sample
— fixed settings, fixed model, no steering — which nothing else here provides.

## 3. How the partner was tuned

The author steers almost entirely through **sampling**, and barely at all
through the context tools built for the purpose.

| feature | share of generating stories |
|---|---:|
| Memory | 15.0% |
| Author's Note | 6.7% |
| Lorebook | 3.8% |
| Phrase bias | 0.4% |
| Banned sequences | 0.4% |

Lorebook, when used at all, has a **median of one entry**. This is close to the
inverse of the NovelAI power-user profile, which is built around lorebooks and
persistent worldbuilding. Nothing here is managing a world. It is running an
exchange at volume — a median of 143 generations per Kayra story, 150 per GLM
story, a median Kayra story carrying 65,482 characters of model output.

**3a. Running hot.** Modal temperature is **2.50** — 286 stories, the single most
common exact value, ahead of 1.0 (277). Median 1.44, mean 1.57 across all
generating stories, well above where NovelAI's own presets sit (1.0–1.4).

Part of that is a deliberate procedure: pick a preset, work a mythological or
poetic register, step temperature up until the output degrades, repeat across
several presets. **33** such sweeps survive in the metadata as runs of 3+
stories sharing model and preset, created within six hours, stepping strictly
upward:

| model | steps | temperature climb |
|---|---:|---|
| `kayra-v1` | 4 | 1 → 1.44 → 1.82 → 2.5 |
| `kayra-v1` | 4 | 1.35 → 1.4 → 1.44 → 2.5 |
| `kayra-v1` | 4 | 1.42 → 1.47 → 1.7 → 2.5 |

They terminate at **2.5 almost every time**, which is the slider's ceiling. The
sweeps were not finding a natural breaking point; they ran out of dial. The top
of the observed range is an interface limit, not a discovered edge.

**3b. What running hot bought, unintentionally.** Holding the model fixed at
`kayra-v1` (990 stories spanning 0.1–2.5), measuring degeneration as trigram
self-repetition truncated to a fixed 150-word window:

| temperature | generations | looping rate |
|---|---:|---:|
| 1.1–1.4 | 1,206 | **6.8%** |
| 1.4–1.7 | 1,440 | 1.7% |
| 1.7–2.2 | 342 | **0.9%** |
| ≥2.2 | 202 | 2.5% |

Roughly a sevenfold reduction. Repetitive degeneration is *the* characteristic
failure of the 2021–2023 models this practice started on, and the thing every
sampler in the NovelAI stack exists to suppress. The sweeps were hunting poetic
register, not looping — this fell out of the habit rather than motivating it,
and it is not visible from inside a session.

**3c. The border between register and noise is a configuration, not a
temperature.** Plotting noise against temperature gives a flat line, and the
reason it is flat is the answer.

Temperature is one stage in an *ordered* pipeline. At temp ≥ 2.2 this corpus
runs `top_k` at a median of **82** — *tighter* than the median of 150 it uses
below 1.2 — with `tail_free_sampling` at 0.97 and `top_a` at 0.02. Temperature
2.5 here never means 2.5 across the full vocabulary. Splitting generations by
whether a truncating sampler ran *before* temperature, using `wordfreq` to
separate real-but-rare words (register climbing) from non-words (noise floor):

| temperature | sampler order | generations | non-word % | rare word % |
|---|---|---:|---:|---:|
| cool (<1.2) | temperature first | 2,500 | 0.62 | 1.10 |
| cool (<1.2) | truncation first | 2,500 | 0.86 | 1.11 |
| mid (1.2–2.2) | temperature first | 2,500 | 0.70 | 1.74 |
| mid (1.2–2.2) | truncation first | 2,500 | 0.86 | 1.08 |
| hot (≥2.2) | temperature first | 2,500 | **2.00** | 1.46 |
| hot (≥2.2) | **truncation first** | 2,500 | **0.96** | **1.58** |

At high temperature the ordering roughly **halves** the non-word rate while
*raising* rare vocabulary — about **42% more rare real words than the cool
baseline at essentially unchanged noise**. At cool and mid temperatures the
ordering barely matters, exactly as a mechanical account predicts: order only
bites once temperature has moved real mass onto the tail.

Truncate to a shortlist of continuations the model considers sayable, *then*
flatten across that shortlist, and you get maximum surprise inside the space of
the sayable. Flatten first and the same nominal 2.5 spends half its budget on
noise. For a partner in an improvised scene that is precisely the right
constraint: surprising, but in key.

## 4. Rewinds and re-rolls

Distinct from the turn: sometimes the author rewinds and generates again from
the identical document state. Measured by branch reachability — walk `prevBlock`
back from `currentBlock`, count AI text *not* on the surviving path:

| abandoned share of generated text | |
|---|---|
| median story | **3.3%** |
| mean story | 7.2% |
| p90 | 18.1% |
| max | 93.5% |
| stories abandoning nothing | 13% |

22,196 abandoned generations against 495,138 kept, across 1,475 stories.

Of **13,336** resolved re-roll events, 52.1% end with the author typing and
47.9% with a generation accepted. When a generation is accepted the median is 2
attempts — one re-roll. When it is not, the median is 1: read one, then type.

An earlier pass read that 52.1% as "none of these, I'll do it" — a threshold
nothing cleared. Under the frame that is wrong for the same reason §1d is: those
human blocks are mostly 55 characters long. The re-roll ends because the turn
came back, not because the model failed an audition.

## 5. What is not learnable

The abandoned branches looked like the best thing in the corpus: 22,196
generations sitting next to the one kept from an identical prompt state,
accumulated over three years with no annotation task and no rubric. A
naturally-occurring preference set. It does not work, and how it fails is worth
more than the reward model would have been.

**5a. It is rejection sampling, not ranking.** Across 8,450 extractable pairs the
kept generation was the *last one generated* **99.6%** of the time — 99.9% at
branch points with exactly two attempts. Nobody was weighing options. Position
perfectly predicts the label, so position must be kept away from any model, and
only the text is left.

**5b. The text carries nothing, and the naive split insists otherwise.** A
within-pair TF-IDF classifier scores **0.950** split by story id. That is
memorisation: duplicating a story in NovelAI copies its whole branch history, so
**91%** of pairs share text with another story id and the answers sit in the
training set. The tell is that the mismatched-pair control — each kept text
scored against a rejected text it never competed with — scored **0.987**,
*higher* than the real thing. A control that beats the treatment means the model
was recognising individual texts, not comparing them.

Re-split by connected components of shared text and deduplicated, 8,450 pairs
collapse to 1,649 distinct comparisons in 1,125 independent groups:

| condition | within-pair accuracy |
|---|---:|
| text classifier, true pairing | 0.559 ± 0.034 |
| length only | 0.548 |
| label permutation control | 0.511 ± 0.033 |
| **mismatched-pair control** | **0.566 ± 0.032** |

Breaking the pairing does not hurt; it helps, fractionally. The true pairing
barely clears "keep the longer one". There is no within-pair signal, and these
pairs do not support a reward model.

## 6. Two metrics that had to be thrown away

The most transferable content here. Both produced a striking,
publishable-looking number that was measuring the tool rather than the author.

**6a. `removedFragments`.** The obvious rejection measure — text a later block
deleted that carried `origin: ai` — says **44% of generated text was deleted**,
and says almost exactly that for every model from 2021-era Euterpe through
GLM-4.6. Five years, a 25× parameter jump, no movement. That would be a real
claim about human editorial standards.

It is an artifact, and the tell is that across 1,675 stories the value **never
once exceeds 0.5**, with 43% crowded into 0.45–0.50. A hard ceiling at exactly
one half is a formula, not a behaviour. NovelAI's editor implements a
whole-document rewrite as *delete everything, re-insert everything*: the delete
charges every prior AI character to `removedFragments`, and the re-insert
returns stamped `origin: user`. A story where the author pasted their own text
back in scores as ~50% "rejected". It looked flat across five years of models
because it was measuring a constant.

**6b. Story-level splits.** Covered in §5b. Grouping by story id is not grouping
by content, because the same text lives under many story ids.

The rule, earned twice: **run the control that should fail before believing the
one that succeeded.** In both cases the diagnostic was a control performing as
well as or better than the treatment.

## 7. Why this cannot benchmark models

Pooling all models and asking which loops most produces a clean-looking table
saying the two newest heavily-used models are worst: Erato (Llama 3 70B) 6.7%,
Kayra 6.9%, against Euterpe 0.0% and Krake 0.1%.

It is confounding, not a result. Euterpe and Krake were used at median
temperatures of 1.54 and 1.92; Erato at **1.00**. §3b shows temperature alone
moves looping sevenfold, larger than any gap between models here. Model choice
and sampler settings are entangled because they were entangled in use — the
sampling changed *when* the model changed, following each model's recommended
presets.

The same trap catches the turn-taking measures. Raw turn rate looks like it
falls with temperature (30.5% below 1.2, 24.9% above 2.4), which would suggest
the model was a better partner when run hot. Holding model, ending and length
fixed:

| temperature | matched n | turn rate |
|---|---:|---:|
| <1.2 | 22,370 | 26.8% |
| 1.2–1.5 | 125,456 | 30.1% |
| 1.5–2.0 | 114,128 | 26.8% |
| ≥2.0 | 79,324 | 26.0% |

Flat, non-monotone, and the individual strata disagree on direction. The raw
effect was composition. **You cannot benchmark models on data collected by a
person who was adapting their settings to the model.**

The one comparison that survives is a rate rather than a ranking. Of resolved
re-roll events, the share ending with the author typing: GLM 61.9%, Euterpe
60.8%, Kayra 55.0%, Clio 50.3%, Krake 44.7%, **Erato 40.7%**. Erato is the model
typed over least and given the longest leash. A fact about these sessions, not a
benchmark.

## 8. What the record cannot hold

- **No per-block timestamps exist.** Elapsed time is unrecoverable, so tempo —
  turn latency, who was waiting for whom, the pace of the exchange — is absent.
  Given that the collaboration was constituted in real time, this is a fossil of
  a live practice with the liveness stripped out. Everything about the dead-air
  clock in §1b is inferred through a length proxy.
- **Settings are stored per story, as current state.** There is no
  per-generation record, so every temperature above is the story's last setting
  attributed to all its generations. For a sweep that is flatly wrong for the
  early steps. The error is non-differential, so it attenuates real effects
  rather than manufacturing them: a flat curve is weak evidence, a surviving
  effect is real.
- **No stream markers.** Which sessions were live, and where they fall in the
  channel's early/middle period, is not in the data. Timestamp clustering
  against the channel's schedule would be the way in if those dates exist
  elsewhere.
- **483 of 2,500 stories will not decrypt**, and not evenly. Before 2025-10,
  losses run 0–7% a month; from 2025-10 onward: 58%, 74%, 94%, 89%, 93%, 90%.
  That is a single damaging event or client change around October 2025, not
  gradual rot. Worth reporting — `data/FAILED_STORIES.txt` is already in the
  shape NovelAI support would want.
- **One file** (`New_Story__eQm-Fkr_ZGaaeaykmh5bu.json`) is truncated at 411
  bytes in Drive itself and cannot be recovered. 2,016 of 2,017.

## 9. What I did not do

- **No content analysis.** Every number is structural — settings, block graph,
  turn lengths, word-frequency statistics. Nothing here characterises what the
  stories are *about*, or reads them as writing. §1d is the closest thing, and
  it is a null result.
- **No text committed.** `data/stories_meta.jsonl` is settings metadata only;
  Memory, Author's Note and previews stripped. Full derived data — including
  `blocks.jsonl`, 524MB with every revision's text — regenerates from the Drive
  export via `analysis/`.
- The `text/` half of the export is untouched; the JSON supersedes it.

## 10. Where this could go next

1. **What the author writes when they take the turn.** In 6,944 cases the model
   was rewound and a human continuation written from the identical context. That
   is a paired human/model sample from matched prompts, and it survives the
   duplication problem because the human side is what varies. It is also the
   only route to the question §7 leaves open: whether the exchange at high
   temperature looks more like uptake and less like correction.
2. **Cue taxonomy.** The 46% of turns under 50 characters are not
   undifferentiated. Naming a character, asking a question and redirecting a
   scene are different moves, and they should predict different things about
   what follows. This is the natural unit of analysis under the frame, and
   nothing here has touched it.
3. **Separating compulsion from momentum.** §1's entanglement is the biggest
   open methodological hole. Stories where `max_length` was large enough that
   generations rarely got cut mid-sentence would give the clean contrast, if
   enough of them exist.
4. **The high-temperature regime.** 310 stories at temp ≥ 2.2, far outside where
   these models were tuned or evaluated. This may be one of the larger extant
   samples of model behaviour out there.

Dropped, and worth recording as dropped: the abandoned branches as preference
data (§5). Not worth another pass in this form.
