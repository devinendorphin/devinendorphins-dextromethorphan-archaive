# Findings

2,016 NovelAI story files. Last edited between March 2023 and July 2026, but
*created* as far back as **June 2021** — 163 of them predate 2023, 39 are from
2021. 280M characters of model
output, 88M of human text, and — the part that matters — **760,611 edit-history
blocks**, because the export preserves the whole undo tree rather than the final
text. Every generation you kept, rewound past, or typed over is still in there,
stamped with which model made it and at what settings.

Epistemic status: descriptive statistics over one person's practice. Nothing
here is a controlled comparison of models, and where the data pretends to be
one, that is called out. Numbers regenerate from `analysis/`; see
`analysis/` for the full tables and the tests, including the ones that failed:
`TABLES.md`, `PROBES.md`, `PAIRS.md`, `LEARNABLE.md`, `STOPPING.md`,
`REGISTER.md`, `TAKEOVER.md`.

---

## 1. The best thing in the corpus is a metric that had to be thrown away

The obvious question to ask a corpus like this is: *how much of what the model
wrote did you actually keep?* NovelAI records deletions — each block carries a
`removedFragments` list, and fragments are tagged with who wrote them. Text
deleted that was tagged `origin: ai` looks exactly like a rejected generation.

That measure says **44% of generated text was deleted**, and — the striking part
— it says almost precisely that for every model from 2021-era Euterpe (Fairseq
13B) through GLM-4.6 (357B MoE). Five years, a 25× parameter jump, no movement.
An invariant like that would be a genuinely interesting claim about what human
editorial standards do as models improve.

It is an artifact, and the tell is that the number **never once exceeds 0.5**
across 1,675 stories, with 43% of stories crowded into 0.45–0.50. A hard ceiling
at exactly one half is a formula, not a behaviour.

The cause is visible once you read the block stream instead of aggregating it.
NovelAI's editor implements a whole-document rewrite as *delete everything,
re-insert everything*. The delete charges every prior AI character to
`removedFragments`; the re-insert comes back stamped `origin: user`. So a story
where you pasted your own text back in scores as ~50% "rejected". The metric was
tracking the text editor, not your judgement — which is exactly why it looked so
beautifully flat across five years of models. **It was measuring a constant
because it was measuring a constant.**

The honest measure is branch reachability: walk `prevBlock` back from
`currentBlock` to get the surviving branch, and count AI text that is *not* on
it. That is text generated and then rewound past. It gives:

| | abandoned share of generated text |
|---|---|
| median story | **3.3%** |
| mean story | 7.2% |
| p90 | 18.1% |
| max | 93.5% |
| stories abandoning nothing | 13% |

Unbounded above, heavily right-skewed — the shape a real behaviour makes.

I am flagging this first because it is the most transferable thing in the pass.
Any future study of this corpus, or of any NovelAI export, will reach for
`removedFragments` and get a beautiful wrong answer.

## 2. You run hot, and it was the right call for reasons you weren't aiming at

Your modal temperature is **2.50** — 286 stories, the single most common exact
value in the corpus, ahead of 1.0. On Clio it is your *median*. On Xialong you
run **3.5**. NovelAI's own presets mostly live between 1.0 and 1.4. Across all
1,798 generating stories the median is 1.44 and the mean 1.57, both well above
where the interface nudges you.

Read as craft, that is a taste for high-entropy output. But there is a
mechanical consequence you could not have been optimising for, because it needs
a corpus this size to see. Holding the model fixed at `kayra-v1` (990 stories
spanning temperature 0.1–2.5), measuring degeneration as trigram self-repetition
inside a generation, truncated to a fixed 150-word window so length can't
confound it:

| temperature | generations | looping rate (>10% repeated trigrams) |
|---|---:|---:|
| 1.1–1.4 | 1,206 | **6.8%** |
| 1.4–1.7 | 1,440 | 1.7% |
| 1.7–2.2 | 342 | **0.9%** |
| ≥2.2 | 202 | 2.5% |

Running hot cut your looping rate by roughly seven-fold. Repetitive degeneration
is *the* characteristic failure of the 2021–2023 models you started on, and the
thing every sampler in the NovelAI stack exists to suppress.

**Correction, from Endorphin after this was written.** The first draft said you
solved this "by feel". That is wrong, or at least half wrong: part of the
temperature spread is a deliberate procedure — pick a preset, work a
mythological or poetic register, step temperature up across several iterations
until the output degrades, repeat across roughly three presets, looking for
where novel structure lives before it dissolves. §8 finds 33 of those sweeps
sitting in the metadata, and they terminate at 2.5 almost every time. So the
habit is partly designed testing and partly retained practice. What remains
accidental is the *anti-looping* consequence — that was not what the sweeps were
looking for, and it is not visible from inside a session.

## 3. The corpus cannot rank the models, and that is itself the finding

Pooling all models and asking which loops most produces a clean-looking table
that says the two **newest** heavily-used models are the worst: Erato (Llama 3
70B) 6.7%, Kayra 6.9%, against Euterpe 0.0% and Krake 0.1%. Taken at face value
that is a headline — bigger models degenerate more.

It is confounding, not a result. You used Euterpe and Krake at median
temperatures of 1.54 and 1.92; you used Erato at **1.00**. Section 2 shows
temperature alone moves looping by 7×, which is larger than the gap between any
two models here. Model choice and sampler settings are entangled in this corpus
because they are entangled in real use — you changed how you sampled *when* you
changed models, following each model's recommended presets.

This is the generic hazard in naturalistic AI-use corpora, and it is worth
stating plainly for whoever reads this next: **you cannot benchmark models on
data collected by a person who was adapting their settings to the model.**
Anything model-comparative here needs within-model, matched-setting slices, and
most such slices in this corpus are too thin to carry weight.

## 4. You barely use the steering apparatus

Of 1,798 generating stories:

| feature | share |
|---|---:|
| Memory | 15.0% |
| Author's Note | 6.7% |
| Lorebook | 3.8% |
| Phrase bias | 0.4% |
| Banned sequences | 0.4% |

Lorebook, when used at all, has a **median of one entry**.

This is close to the inverse of the NovelAI power-user profile, which is built
around lorebooks and persistent worldbuilding. You are not managing a world; you
are doing raw continuation at volume — median 143 generations per Kayra story,
150 per GLM story, and a median Kayra story carrying 65k characters of model
output. The steering happens in the prompt and in what you accept, not in the
context-management panel.

Combined with §2, a consistent picture: you steer by **sampling** and by
**selection**, not by instruction. That is an unusual and coherent practice, and
it is legible only because the export kept the settings alongside the text.

## 5. Loose ends worth a look

- **A 4.6× spread in turn size.** Median characters accepted per generation runs
  419 (Euterpe) → 469 (Kayra) → 944 (Erato). Partly your `max_length` budget
  (100 → 250 tokens), partly trust. Erato is the one model you let run long
  *and* the one you abandon most (median 6.7% vs Kayra's 3.0%). Plausibly:
  longer leash, more rope.
- **Sampler-order archaeology.** 48 distinct preset ids, and orderings like
  `math1 > top_p` and `mirostat > temperature > typical_p > tfs > top_p > top_a`.
  These are the experimental sampler stacks of specific NovelAI eras; the corpus
  dates when each was in play.
- **The 2025-10 encryption cliff.** `data/MISSING.md`: 483 of 2,500 stories will
  not decrypt, but they are not spread evenly. Before 2025-10 losses run 0–7% a
  month; from 2025-10 onward they run 58%, 74%, 94%, 89%, 93%, 90%. That is a
  single damaging event or a client change around October 2025, not gradual rot.
  Worth reporting to NovelAI — `data/FAILED_STORIES.txt` is already in the shape
  their support would want.

## 6. What I did not do

- No content analysis. Every number is structural — settings, timings, block
  graph, and word-level repetition statistics. I have not characterised what the
  stories are *about*, nor read them as writing.
- No text committed. `data/stories_meta.jsonl` is settings metadata only; Memory,
  Author's Note and previews were stripped. Full derived data (including
  `blocks.jsonl`, 524MB with every revision's text) regenerates from the Drive
  export via `analysis/`.
- The `text/` half of the export is untouched — the JSON supersedes it.
- One file, `New_Story__eQm-Fkr_ZGaaeaykmh5bu.json`, is truncated at 411 bytes
  in Drive itself and cannot be recovered by re-downloading. 2,016 of 2,017.

## 7. Second pass: the preference data does not work, and the reason is the finding

§8 below was the top of the "next" list: 22,196 abandoned generations sitting
next to the one you kept from the identical prompt state, built over three years
with no annotation task. It looked like the best thing in the corpus. It was
chased, and it does not hold up. Three results, in the order they killed each
other.

**7a. You are not picking a favourite, you are rolling until satisfied.** Across
8,450 extractable pairs, the generation you kept was the *last one generated*
**99.6%** of the time — 99.9% at branch points with exactly two attempts. So
these are not best-of-N comparisons. They are rejection sampling against a
threshold, and the label "chosen" is perfectly predicted by position. Position
therefore has to be kept away from any model, and the only question left is
whether the *text* carries the signal.

**7b. It does not, and a story-level split will tell you it does.** A TF-IDF
classifier evaluated within-pair — score both continuations from one branch
point, ask whether the kept one wins — scores **0.950** when split by story id.
That is memorisation. Duplicating a story in NovelAI ("Working Copy", "New Story
(2)") copies its whole branch history, so **91%** of pairs share text with
another story id and the answers are sitting in the training set. The tell is
that the mismatched-pair control — where each kept text is scored against a
rejected text it never competed with — scored **0.987**, *higher* than the real
thing. A control that beats the treatment means the model was recognising
individual texts, not comparing them.

Re-split by connected components of shared text, and deduplicated, 8,450 pairs
collapse to 1,649 distinct comparisons in 1,125 independent groups:

| condition | within-pair accuracy |
|---|---:|
| text classifier, true pairing | 0.559 ± 0.034 |
| length only | 0.548 |
| label permutation control | 0.511 ± 0.033 |
| **mismatched-pair control** | **0.566 ± 0.032** |

Breaking the pairing does not hurt — it helps, fractionally. The true pairing
barely clears "keep the longer one". **There is no within-pair signal.** What
little is there is a global difference between the two pools (kept generations
run slightly longer, and end on a complete sentence 63% vs 56% of the time), and
it applies just as well to texts that were never in competition. These pairs do
not support a reward model.

**7c. What is actually happening is more interesting than the reward model would
have been.** If the rejected text does not predict rejection, look at the
process instead. Of 13,336 resolved re-roll events:

| resolution | share |
|---|---:|
| you wrote it yourself | **52.1%** |
| you accepted a generation | 47.9% |

**More than half of all re-rolls end with you taking over and writing it.** When
you do accept, the median is 2 attempts — you re-roll once. When you don't, the
median is 1: you read one generation, and write it yourself.

That is the thing a pair set structurally cannot see, because it only keeps the
branches where a generation eventually won. The dominant rejection event in
three and a half years of this corpus is *not* "this generation is worse than
that one" — it is "none of these, I'll do it", decided fast, usually on the
first try. Your bar is not a ranking over model outputs. It is a threshold, and
half the time nothing clears it.

**Caveat, from Endorphin after this was written.** A good deal of this
generation was performed live on stream, concentrated in the early and middle
history of that channel. That reframes both §7a and §7c: under an audience and
a clock, taking the keyboard after one look is improv, not deliberation, and
"retry until satisfied" is partly "retry until the scene can continue". The
speed of the takeover decision — median one attempt — reads very differently as
a performance constraint than as an editorial one. The corpus carries no
stream markers, so this cannot currently be separated out; timestamp clustering
against the channel's schedule would be the way in if the dates exist
elsewhere.

The model-by-model split is the one place a comparison survives, because it is
a rate rather than a ranking:

| model | re-roll events | you wrote it yourself |
|---|---:|---:|
| `glm-4-6` | 809 | 61.9% |
| `euterpe-v2` | 429 | 60.8% |
| `kayra-v1` | 7,968 | 55.0% |
| `clio-v1` | 946 | 50.3% |
| `krake-v2` | 678 | 44.7% |
| `llama-3-erato-v1` | 2,491 | **40.7%** |

Erato is the model you hand-write over least — and from §5, the one you let run
longest and abandon most characters of. Longer leash, more rope, but a better
hit rate per attempt. Same §3 caveat applies: settings move with model choice,
so read this as a fact about your sessions, not a benchmark.

## 8. The sweeps, the border, and pressing enter

Three things Endorphin raised after §7, all of which turn out to be measurable.

**9a. The sweeps are in the metadata.** Filtering for runs of three or more
stories that share a model *and* preset, were created within six hours of each
other, and step temperature strictly upward finds **33** of them. A
representative sample:

| model | steps | temperature climb | when |
|---|---:|---|---|
| `kayra-v1` | 4 | 1 → 1.44 → 1.82 → 2.5 | 2024-04-09 |
| `kayra-v1` | 4 | 1.35 → 1.4 → 1.44 → 2.5 | 2023-11-17 |
| `kayra-v1` | 4 | 1.42 → 1.47 → 1.7 → 2.5 | 2024-03-05 |
| `kayra-v1` | 3 | 1.4 → 2 → 2.5 | 2024-03-05 |

They terminate at **2.5 almost every time**, which is the NovelAI slider's
ceiling. So the sweeps were not finding a natural breaking point — they were
running out of dial. That is worth knowing: the top of the observed range is an
interface limit, not a discovered edge.

**9b. The border is a configuration, not a temperature.** The obvious way to
locate "where structure dissolves" is to plot noise against temperature. Doing
that produces a **flat line**, which cannot be right — and the reason it is flat
is the answer.

Temperature is one stage in an *ordered* pipeline. At temp ≥ 2.2 this corpus
runs `top_k` at a median of **82** — *tighter* than the median of 150 at temp
< 1.2 — plus `tail_free_sampling` 0.97 and `top_a` 0.02. Temperature 2.5 here
never means 2.5 across the full vocabulary. So the question is not how hot but
hot *in what order*. Splitting every generation by whether a truncating sampler
ran before temperature, using `wordfreq` to separate real-but-rare words (the
register climbing) from non-words (the noise floor):

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
ordering barely matters, which is exactly what a mechanical account predicts:
order only bites once temperature has moved real mass onto the tail.

So: truncate to a shortlist of continuations the model considers sayable, *then*
flatten across that shortlist, and you get maximum surprise inside the space of
the sayable. Flatten first and the same nominal 2.5 spends half its budget on
noise. **That is the border you were looking for, and it is a two-knob answer.**

One caveat governs all of this. NovelAI stores settings per *story*, as current
state — there is no per-generation record, so every temperature above is the
story's last setting attributed to all of its generations. For a sweep that is
flatly wrong for the early steps. The error is non-differential, so it attenuates
real effects rather than manufacturing them: the flat pooled curve is weak
evidence, but the order effect that survived it is real.

**9c. Pressing enter.** Unbroken runs of model generation with no human text
between them, on the surviving branch: **135,567** of them. Median 2, p90 7,
p99 24, and a maximum of **212**.

| run length | share of runs |
|---|---:|
| 1 | 39.6% |
| 2–3 | 32.6% |
| 4–9 | 20.9% |
| 10–24 | 5.9% |
| 25+ | 1.0% |

The 212-run is *I Remind The Body Electric*, created **April 2022** — almost
certainly the story you were thinking of. It survives in six duplicates under
six different model settings, which is its own kind of evidence: you kept
re-running the same seed text through successive models as they came out.

Those long runs are also, incidentally, the cleanest experimental material in
the corpus. A stretch of 212 consecutive generations with no human intervention
is a single-condition sample — fixed settings, fixed model, no author steering —
which is exactly what nothing else here provides.

## 9. The takeover moment

The label §7 pointed at, with 60× the volume of the pair set that failed:
**476,839** generations on surviving branches, each labelled by whether the next
thing was another generation or the author typing. Overall takeover rate
**28.1%** (79% new typing, 21% in-place edits). Endorphin supplied two accounts
to separate, and the data supports both — then produces a third that neither
predicted.

**Hard limit first.** NovelAI stores no per-block timestamps. Elapsed time is
not recoverable at all, so the dead-air account can only be tested through
length as a proxy for speech duration, never directly.

**9a. Momentum is real.** Among generations reaching position *k* of an unbroken
run, the share that ended it:

| position in run | generations | takeover rate |
|---|---:|---:|
| 1 | 135,103 | **39.4%** |
| 3 | 54,527 | 30.8% |
| 5 | 27,042 | 23.1% |
| 9 | 11,026 | 15.4% |
| 20 | 2,132 | **5.4%** |
| 50 | 250 | 9.2% |

A memoryless process would be flat. This falls by a factor of seven. Long runs
are a genuinely different mode, not a lucky streak of independent decisions.

**9b. Dead air shows up, with the sign the account predicts.** Bucketing by how
long the passage takes to read aloud (155 wpm):

| speech seconds | generations | takeover rate |
|---|---:|---:|
| 0–5 | 6,319 | **45.8%** |
| 5–10 | 7,595 | 42.2% |
| 30–45 | 269,116 | 26.3% |
| 90+ | 1,599 | **22.8%** |

Short generations double the takeover rate. This is not just run position in
disguise — holding position fixed, short (<20s) beats long (≥45s) at every one
of the first five positions, by +10.0, +4.7, +11.3, +2.6 and +6.9 points. A
generation that yields only a few seconds of speech does not buy enough time,
and the author steps in. The middle of the range is non-monotonic (10–20s sits
below 20–30s), so the effect is real at the extremes rather than a clean
gradient.

**9c. The thing neither of us predicted, and the strongest result in the pass.**

| generation ends | generations | takeover rate |
|---|---:|---:|
| on sentence-final punctuation | 305,197 | **37.5%** |
| mid-sentence | 171,642 | **11.5%** |

The intuition — a generation that breaks off mid-clause is defective, so you
step in — is not merely wrong, it is inverted, by more than 3×.

A clean ending is an **invitation**; a mid-sentence cut is a **compulsion**.
When the model stops on a full stop it has handed the turn back, and that is
where a human takes it. When it stops mid-clause the only graceful move is to
press enter again — especially with the text being read aloud, where a hanging
clause is worse than silence.

Which means a good deal of §8c's enter-chain behaviour may not be momentum by
choice at all. It may be a short `max_length` cutting generations mid-sentence
and *compelling* the next one. The two accounts are entangled and this corpus
cannot fully separate them: `max_length` is stored per story, like every other
setting, so the per-generation truncation that would decide it is not recorded.

**9d. And the text does not matter.** A TF-IDF classifier over the generation's
own words, grouped by text content so the §7b duplication leak cannot recur:

| predictor | AUC |
|---|---:|
| TF-IDF over the full text | 0.623 |
| **does it end on sentence-final punctuation** | **0.647** |
| length alone | 0.559 |

**A single bit beats every word in the passage.** The takeover decision is not
legible in the writing. It is legible in the punctuation — in whether the model
handed the turn back or left it hanging.

Taken with §7b, that is now twice that the *content* of a generation has failed
to predict what the author did with it, while structural facts — how long it
was, where it stopped — predict it comparatively well. For a corpus built
entirely out of aesthetic play, the aesthetics are the part that does not
register in the behaviour.

## 10. Where this could go next

~~1. The abandoned branches are preference data.~~ **Chased in §7. Dead.**
The pairs are rejection sampling, not preference ranking, and the rejected text
carries no recoverable signal. Not worth another pass in this form.

Still open, reordered after what §7 taught:

1. **The takeover moment.** §7c says 52% of re-rolls end with you writing it
   yourself, usually after one look. *That* is the labelled event worth
   modelling: not "which generation is better" but "does this one clear the
   bar at all". Every AI block in the corpus is implicitly labelled by whether
   you kept going or took the keyboard, which is ~517k labels rather than 8k
   pairs, and it does not depend on the branch structure that turned out to be
   so leaky.
2. **What you write when you take over.** In 6,944 cases you rejected the
   model's continuation and immediately wrote your own from the identical
   context. That is a paired human/model sample from matched prompts — a
   cleaner comparison than anything in the pair set, and it survives the
   duplication problem because the human text is what varies.
3. **Session-level dynamics.** Does the takeover rate rise or fall within a
   session? Does a long session converge on the model's voice, or on yours?
4. **The high-temperature regime specifically.** You have 310 stories at
   temp ≥ 2.2, which is far outside where these models were tuned or
   evaluated. Whatever is characteristic about model behaviour out there, this
   may be one of the larger extant samples of it.

A methodological note worth carrying to any future pass, since it has now bitten
twice: **this corpus punishes the obvious metric.** Both §1 and §7b produced a
striking, publishable-looking number that turned out to be measuring the tool
rather than the author — once the text editor, once the duplicate-story habit.
Run the control that should fail before believing the one that succeeded.
