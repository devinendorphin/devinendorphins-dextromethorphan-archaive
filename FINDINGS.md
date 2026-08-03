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
aloud by text-to-speech over a lo-fi backing track — in which the author's move
is usually a cue, a name, a question, or a character walking on stage, and the
model's move is to perform whatever just arrived.

The backing track matters more than it sounds. With a beat under it, the
synthesised voice reads as continuous freestyle or poetry, which makes the
constraint not "avoid silence" but **keep the audio flowing at a steady clip**.
And it put the author on both sides at once — driving the generation, and
listening to it in real time as an audience member, with what he heard informing
the next move. §1e shows that loop left a measurable trace.

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
sample of anything, and not a benchmark — §10 works through why that is
structurally impossible here. Everything regenerates from `analysis/`, where the
tests that killed claims are kept alongside the ones that survived: `PROBES.md`,
`PAIRS.md`, `LEARNABLE.md`, `STOPPING.md`, `REGISTER.md`, `TAKEOVER.md`,
`CUES.md`, `ERATO.md`, `TEMPO.md`, `TABLES.md`.

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
own text, grouped by text content so the duplication leak in §9b cannot recur:

| predictor | AUC |
|---|---:|
| TF-IDF over the full text | 0.623 |
| **does it end on sentence-final punctuation** | **0.647** |
| length alone | 0.559 |

**A single bit beats every word in the passage.** Under the rejection frame this
was baffling. Under the turn-taking frame it is nearly tautological: the human
move is not a verdict on the passage, so no property of the passage predicts it.
What predicts it is whether the turn was handed back.

**1e. And the pacing left a trace after all.** §11 records that no per-block
timestamps exist, so tempo is unrecoverable. That is true of *duration*. It is
not true of *rhythm*. Within unbroken runs of at least 8 generations (12,921 of
them), the absolute difference in word count between generations *lag* apart,
against the same run with its order shuffled:

| lag | pairs | observed \|Δ words\| | shuffled | reduction |
|---:|---:|---:|---:|---:|
| 1 | 178,979 | 11.03 | 13.69 | **19.5%** |
| 2 | 166,058 | 12.03 | 13.73 | 12.4% |
| 3 | 153,137 | 12.59 | 13.67 | 7.9% |
| 4 | 140,216 | 13.07 | 13.68 | 4.4% |
| 6 | 114,374 | 13.59 | 13.69 | **0.7%** |
| 8 | 88,532 | 13.71 | 13.65 | −0.5% |

Shuffling preserves the run's entire length distribution — so `max_length`
capping, model choice and session habits all cancel — and destroys only the
sequence.

**The decay is the result.** A slow drift across a session would show the same
reduction at every lag, because shuffling kills a trend as thoroughly as a
rhythm. Largest at lag 1 and gone by lag 6 is short-memory coupling: each
generation's length tracks the one just before it over a window of about five
turns. That is what keeping a voice fed at a steady clip looks like from the
outside.

What it cannot show is **direction**. A steady clip could be the author pacing
the model, the model's own length autocorrelation pacing the author, or both
locked together — which is what the collaboration account would actually
predict. Nothing here separates them.

## 2. A taxonomy of the turn

If the turn is the unit, 134,063 of them is not one thing. They fall into a
small number of syntactic conventions the corpus uses heavily and consistently,
read off the data rather than imposed. Deduplicated to **18,089** distinct
turns:

| kind | share | median chars | example |
|---|---:|---:|---|
| speaker line (`Name: ...`) | 26.2% | 74 | `Elegua: Sounds about white.` |
| narration | 24.9% | 61 | `No! Even darker! Alright here's a hunt, Zyklon` |
| long turn (>200 chars) | 12.4% | 354 | |
| stage direction (`{...}`) | 11.6% | 70 | `{What would be markers of being a "bad actor".` |
| continuation | 11.3% | 48 | `( It ook four tries to get this, stupid 20B)` |
| question | 3.7% | 60 | |
| handoff (`Name:`) | 3.7% | 12 | `Deganawida:` |
| directive (`> ...`) | 3.4% | 56 | `> The Best Little Methodist Whorehouse During Methsmas!` |
| instruction (`[...]`) | 1.9% | 34 | `[A partial list of people to bleach.]` |

A further 737 distinct blocks were empty and are **excluded**: not turns but the
delete half of the §9a rewrite. Left in they top every table, which is worth
recording as a third instance of the same trap.

**2a. What a turn buys.** Measuring forward — how many generations follow before
the author speaks again:

| kind | turns | mean run bought | 95% CI |
|---|---:|---:|---|
| instruction (`[...]`) | 347 | **3.33** | ±0.44 |
| stage direction (`{...}`) | 2,104 | 3.11 | ±0.16 |
| long turn | 2,238 | 2.74 | ±0.19 |
| handoff (`Name:`) | 674 | 2.73 | ±0.26 |
| speaker line | 4,746 | 2.58 | ±0.09 |
| narration | 4,500 | 2.44 | ±0.11 |
| continuation | 2,049 | 2.43 | ±0.23 |
| question | 678 | 2.37 | ±0.25 |
| directive (`> ...`) | 620 | **1.74** | ±0.16 |

A 1.9× spread in continuous output, from phrasing alone.

**2b. One reading that did not survive its control.** The pooled table also
shows `instruction []` producing a median next generation of ~900 characters
against ~490 for everything else — bracketed instructions apparently making the
model expansive. They do not. Those cues sit disproportionately in Erato
sessions where median `max_length` is 250 tokens against 100 corpus-wide. Hold
the model fixed and it collapses to **492**, indistinguishable from every other
cue:

| within `kayra-v1` | mean run bought | median next gen |
|---|---:|---:|
| stage direction `{...}` | 3.11 ±0.16 | 499 |
| instruction `[...]` | 3.06 ±0.52 | 492 |
| handoff `Name:` | 2.90 ±0.30 | 500 |
| speaker line | 2.58 ±0.11 | 474 |
| narration | 2.43 ±0.14 | 473 |
| question | 2.22 ±0.30 | 476 |
| directive `> ...` | **1.79** ±0.27 | 442 |

Inside a model the next-generation column is flat — Kayra 442–509 for every cue
kind, Erato 1,028–1,133. **Generation length is set by `max_length`, not by how
the turn was phrased.** Third time the same lesson: §9's rule applies to this
section too.

**2c. What survives it.** The run column, and one result in particular:
**`> directive` buys the least in every model with enough of them** — 1.79 in
Kayra against that model's 2.43 median, 1.28 in Clio against 2.49. That is the
text-adventure convention behaving as designed: `> You ...` establishes strict
alternation, one move each, so the author gets a reply rather than a run. The
other orderings are broadly stable across models, but the gaps are small next to
their intervals and should not be pushed.

**2d. Handing over a voice works.** For turns that name a speaker and stop —
a bare `Deganawida:` with nothing after the colon — the following generation
opens in that voice **89.7%** of the time (n=630). The comparison row, full
`Name: line` turns, holds at 68.8%, but that is not a failure rate: after the
author finishes a line, a switch to another speaker is dialogue working. Only
the handoff row measures uptake, and roughly nine times in ten the model takes
the cue it was handed.

That is the cleanest evidence in the corpus for the partner reading. A pure
handoff carries no content — no sentence to continue, no instruction, just a
name and a colon. Nearly all of its effect has to come from the model correctly
inferring whose turn it is.

**2e. The repertoire moves with the model**, though §10's confound forbids
reading that as a fact about the models. `stage direction {}` is 17.9% of Kayra
turns and ~0% in Clio, Krake and Euterpe; `instruction []` is 14.9% of Erato
turns and ~1% everywhere else. These are conventions the author adopted in
particular eras, and they date the practice as much as the presets in §4 do.

## 3. The shape of a session

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

## 4. How the partner was tuned

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

They terminate at **2.5 almost every time**, which is the ceiling for every
NovelAI-native model in the corpus. The sweeps were not finding a natural
breaking point; they ran out of dial. The top of the observed range is an
interface limit, not a discovered edge — and §5 shows it is an era-specific
one, since `xialong-v1` later runs at 3.5.

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

## 5. The October 2025 discontinuity

Two models in this corpus sit outside the NovelAI-trained lineage, and they are
easy to miss because their story counts are small:

| model | stories | AI characters | active | temperature |
|---|---:|---:|---|---|
| `glm-4-6` | 62 | **16,164,340** | 2025-10 – 2026-07 | 1.00 – 1.75 |
| `xialong-v1` | 11 | 651,813 | 2026-04 – 2026-07 | 0.85 and 3.50 |

The character count is the tell. GLM-4.6 is 3.4% of generating stories and
**5.8% of all model output in the corpus** — its median story carries 129,158
characters, the largest of any model. These are not stray experiments.

**What they are.** GLM-4.6 is Z.ai's open-weights 355B Mixture-of-Experts
model. NovelAI added it as GLM-4.5 on 25 September 2025, updated it to GLM-4.6
on 1 October, and rolled it to all tiers mid-October. Xialong (夏龍, "Summer
Dragon") is NovelAI's own 355B finetune *of GLM-4.6*, released 31 March 2026 as
an Opus exclusive — so the two are one family, not two. Both carry 28,672 tokens
of context plus an 8,192-token rollover, roughly quadruple Kayra's 8,192.

The corpus dates match the releases to within days: `glm-4-6` first appears in
2025-10, `xialong-v1` in 2026-04. That is a useful external check on the
timestamps everything else here rests on.

**And from October 2025 they are almost the whole practice:**

| month | models in use |
|---|---|
| 2025-08 | kayra 17, krake 4, erato 4, euterpe 1, clio 1 |
| 2025-09 | 3 stories total |
| **2025-10** | **glm 22**, kayra 2, krake 2, erato 2, euterpe 1 |
| 2025-11 | **glm 16**, krake 4 |
| 2025-12 | **glm 9** |
| 2026-01 | glm 3, erato 2 |
| 2026-02 | **glm 4** |
| 2026-03 | **glm 3** |
| 2026-04 | **xialong 6**, clio 2, kayra 1 |

**5a. The experimental sampling regime was thrown out.** This is the sharpest
change and it is visible in one field. NovelAI stores the sampler pipeline as an
ordered array, including entries the user has switched off. Its *length* is
therefore what the client offered, not what the author chose:

| model | order-array length | samplers ever enabled |
|---|---|---|
| `kayra-v1` | 9 or 11 | typical_p, temperature, top_k, tfs, mirostat, top_p, top_a, cfg, top_g, math1, min_p |
| `llama-3-erato-v1` | 11 | **math1 (369/374)**, min_p, top_p, temperature, typical_p, mirostat, top_a |
| `glm-4-6` | **3 or 4** | temperature, top_k, top_p |
| `xialong-v1` | **4** | temperature, top_k, top_p, min_p |

Erato ran NovelAI's experimental Unified sampler (`math1`) in **369 of 374**
stories — that was its regime. GLM's array contains three entries *in total*.
The other samplers are not disabled; they are absent. Whatever the author might
have wanted, Tail-Free Sampling, Top-A, Typical-P, Mirostat, CFG and the Unified
sampler stopped being on offer.

The documentation corroborates a narrowed surface from the other direction:
Banned Tokens are **not available** on GLM-4.6 and Xialong, while System Prompt
is available **only** on them. Losing logit-level controls and gaining a system
prompt is the signature of a different serving path — a chat-style API rather
than the raw-completion access NovelAI's own inference stack gives it. The
public posts do not describe the infrastructure, so this is inference from the
feature surface, not a confirmed account.

**5b. Everything else moves at the same boundary.**

- **A new settings schema.** Version 8 first appears 2025-11; `xialong-v1` is
  v8-only, `glm-4-6` splits v7/v8. Every earlier model sits on v3–v7.
- **Finer `max_length` granularity.** Values that are not multiples of ten:
  3% of Kayra stories, 28% of Erato, **68% of GLM, 73% of Xialong** — 282, 273,
  258 rather than 250 or 300.
- **The decryption cliff.** §10 records losses of 0–7% a month before 2025-10,
  then 67%, 58%, 74%, 94%, 89%, 93%, 90%. It starts the same month.

§11 offers "a single damaging event or a client change around October 2025" as
the two readings of that cliff. The model roster, the sampler surface, the
schema bump and the slider granularity all move together at exactly that
boundary, which favours the second strongly.

**Two corrections follow.**

§4a states that the temperature sweeps terminate at 2.5, "which is the slider's
ceiling". That holds for every NovelAI-trained model — Kayra, Erato, Clio,
Euterpe and Krake all top out at exactly 2.5 — but `xialong-v1` runs at **3.5**.
The ceiling is era-specific, not a fact about temperature.

More consequentially: **`glm-4-6` never exceeds 1.75.** The high-temperature
habit that §4a and §4b treat as the corpus's most distinctive feature stops dead
at the platform change — which now has a mechanical explanation rather than
being a change of taste. The samplers that made running hot survivable are the
ones that disappeared: §4c shows the register/noise border depends on truncation
running *before* temperature, and GLM offers only `top_k` and `top_p` to
truncate with. Everything in §4 describes the 2021–2025 native era.

**A note on where these models appear.** They are in the aggregate tables
(`TABLES.md`, `PROBES.md`, `REGISTER.md`) but drop out of most within-model
control tables, which impose minimum-n thresholds of 100–500. That is correct —
9 generating Xialong stories cannot support a controlled comparison — but it
means the controls in §2b, §4b and §10 describe the native era only, and should
not be read as covering the last nine months of the corpus.

## 6. The Erato era, and a second border

Erato (Llama 3 70B, Nov 2024 – Jul 2026, 374 generating stories, 52.9M
characters) is the one stretch where the whole configuration approach changed at
once. Full tables in `analysis/ERATO.md`.

**6a. Temperature is not in the pipeline.** In **227 of 374** Erato stories
(61%) `temperature` does not appear in the enabled sampler order at all, and in
**226 of those 227** the stored value is exactly **1.0** — the neutral number,
sitting unused in a field the pipeline never reads. When temperature *is*
enabled the median is 1.37. This is Erato-only; every other model has it enabled
in 100% of stories.

So Erato's apparent "median temperature 1.00" was never a setting. NovelAI's
Unified sampler (`math1`) replaced the temperature stage outright, and any claim
resting on that number — including the one §9 originally made — is comparing a
live control against a switched-off one. It also means §4's corpus temperature
statistics are dragged down by 227 inert 1.0 values.

**6b. What the regime was.** Four stock presets carry almost the whole era, and
the settings are collinear with them, so no knob-level test is possible —
`linear` and `quad` never vary independently of each other or of the rest of the
stack:

| preset | stories | linear | quad | min_p | order |
|---|---:|---:|---:|---:|---|
| `dragonfruit` | 141 | 0.900 | 0.07 | 0.035 | `temperature > typical_p > math1 > min_p > mirostat > top_a` |
| `goldenarrow` | 87 | 0.500 | 0.19 | 0.000 | `math1 > top_p` |
| `zanyscribe` | 79 | −0.275 | 0.35 | 0.080 | `math1 > top_p` |
| `wilder` | 59 | 0.000 | 0.19 | 0.010 | `math1 > min_p` |

That is itself a shift. On Kayra the corpus shows 48 distinct presets and heavy
hand-tuning; the Erato era runs on four stock ones.

**6c. The border moved outward and stayed just as steep.** Re-running §4c's
measure — `wordfreq` splitting non-words (noise) from real-but-rare words
(register) — across the Unified configuration:

| configuration | non-word % | rare word % | rare : non |
|---|---:|---:|---:|
| classic, cool | 0.62 | 1.10 | 1.77 |
| **classic, hot, truncation first** | 0.96 | 1.58 | **1.65** |
| Unified, `goldenarrow` | 0.53 | 0.86 | 1.63 |
| Unified, `zanyscribe` | **2.45** | **3.24** | 1.32 |
| classic, hot, temperature first | 2.00 | 1.46 | 0.73 |

**No Erato preset beats the classic stack's exchange rate.** `goldenarrow` ties
it — 1.63 against 1.65 — and gets there at a much lower absolute level of both
quantities, so it is cleaner without reaching as far.

**What the Unified sampler adds is range.** `zanyscribe` (linear −0.275, quad
0.35) reaches a rare-word rate of **3.24%**, roughly double anything the classic
stack managed at any temperature, at a **2.45%** non-word rate — the highest
noise floor measured anywhere in the corpus. Temperature-plus-truncation could
not get the register that high at any price. `math1` could, and the price was a
noise floor two and a half times the corpus norm.

So the answer to "does the Unified sampler dissolve the border" is no. It
**extended the reachable range without improving the exchange rate.** The trade
between strangeness and dissolution is the same trade; `math1` just lets you buy
further along it.

There is one thing this cannot settle. Because the presets bundle `linear`,
`quad`, `min_p`, `top_p` and the sampler order together, the 3.24% is a property
of `zanyscribe`, not of any one knob. Whether the range came from the negative
`linear`, the high `quad`, or their interaction is not recoverable from
naturalistic use — it would need settings varied one at a time, which is exactly
what a preset prevents.

## 7. Rewinds and re-rolls

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

## 8. What is not learnable

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

## 9. Two metrics that had to be thrown away

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

**6b. Story-level splits.** Covered in §8b. Grouping by story id is not grouping
by content, because the same text lives under many story ids.

The rule, earned twice: **run the control that should fail before believing the
one that succeeded.** In both cases the diagnostic was a control performing as
well as or better than the treatment.

## 10. Why this cannot benchmark models

Pooling all models and asking which loops most produces a clean-looking table
saying the two newest heavily-used models are worst: Erato (Llama 3 70B) 6.7%,
Kayra 6.9%, against Euterpe 0.0% and Krake 0.1%.

It is confounding, not a result. Euterpe and Krake were used at median
temperatures of 1.54 and 1.92; §4b shows temperature alone moves looping
sevenfold, larger than any gap between models here. Model choice and sampler
settings are entangled because they were entangled in use — the sampling
changed *when* the model changed, following each model's recommended presets.

The Erato row is worse than confounded, it is meaningless: **61% of Erato
stories do not have temperature in their sampler pipeline at all** (§6). An
earlier draft of this section read Erato's stored median of 1.00 as "run cool".
It is the neutral value of a disabled field. Erato ran on the Unified sampler,
which has no temperature stage.

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

## 11. What the record cannot hold

- **No per-block timestamps exist.** Elapsed time is unrecoverable, so
  *duration* — turn latency, who was waiting for whom — is absent. §1e shows
  *rhythm* partly survives in the sequence of lengths, but that is a weaker
  thing and cannot recover direction.
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

## 12. What I did not do

- **No content analysis.** Every number is structural — settings, block graph,
  turn lengths, word-frequency statistics. Nothing here characterises what the
  stories are *about*, or reads them as writing. §1d is the closest thing, and
  it is a null result.
- **No text committed.** `data/stories_meta.jsonl` is settings metadata only;
  Memory, Author's Note and previews stripped. Full derived data — including
  `blocks.jsonl`, 524MB with every revision's text — regenerates from the Drive
  export via `analysis/`.
- The `text/` half of the export is untouched; the JSON supersedes it.

## 13. Where this could go next

1. **What the author writes when they take the turn.** In 6,944 cases the model
   was rewound and a human continuation written from the identical context. That
   is a paired human/model sample from matched prompts, and it survives the
   duplication problem because the human side is what varies. It is also the
   only route to the question §10 leaves open: whether the exchange at high
   temperature looks more like uptake and less like correction.
2. **Why a handoff works.** §2d shows a bare `Name:` gets taken up 89.7% of
   the time on no content at all. Whether that is the model tracking the scene
   or simply the strength of the `Name:` convention in its training data is the
   sharpest open question the frame raises, and it is answerable — compare
   uptake for names established earlier in the session against names appearing
   for the first time.
3. **Separating compulsion from momentum.** §1c's entanglement is the biggest
   open methodological hole. Stories where `max_length` was large enough that
   generations rarely got cut mid-sentence would give the clean contrast, if
   enough of them exist.
4. **The high-temperature regime.** 310 stories at temp ≥ 2.2, far outside where
   these models were tuned or evaluated. This may be one of the larger extant
   samples of model behaviour out there.

Dropped, and worth recording as dropped: the abandoned branches as preference
data (§8). Not worth another pass in this form.
