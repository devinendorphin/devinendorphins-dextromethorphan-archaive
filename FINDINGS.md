# Findings — first pass

2,016 NovelAI story files, March 2023 to July 2026. 280M characters of model
output, 88M of human text, and — the part that matters — **760,611 edit-history
blocks**, because the export preserves the whole undo tree rather than the final
text. Every generation you kept, rewound past, or typed over is still in there,
stamped with which model made it and at what settings.

Epistemic status: descriptive statistics over one person's practice. Nothing
here is a controlled comparison of models, and where the data pretends to be
one, that is called out. Numbers regenerate from `analysis/`; see
`analysis/TABLES.md` for the full tables and `analysis/PROBES.md` for the tests.

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
thing every sampler in the NovelAI stack exists to suppress. You appear to have
solved it by feel, with the crudest available knob, and then kept the habit for
years across five model generations — including onto models that no longer
needed it.

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

## 7. Where this could go next

Roughly in order of how much I think is actually there:

1. **The abandoned branches are preference data.** 22,196 abandoned AI blocks,
   across 1,475 stories, sit next to the generation you kept from the same
   prompt state (against 495,138 kept blocks). That is a
   naturally-occurring chosen/rejected pair set, built by one person with a
   stable aesthetic over three years, with no annotation task and no rubric.
   That is rare, and it is the thing an alignment researcher would actually want.
   The obvious question: is there a *learnable* signal in what you rewind past,
   or is it mostly noise and mechanics?
2. **Prompt-state → acceptance.** Does accepted-vs-abandoned correlate with
   anything measurable in the preceding context — length, who wrote the previous
   block, how far into the session you are?
3. **Session-level dynamics.** Do abandonment rates rise or fall within a
   session? Does a long session converge on the model's voice, or your own?
4. **The high-temperature regime specifically.** You have 310 stories at
   temp ≥ 2.2, which is far outside where these models were tuned or
   evaluated. Whatever is characteristic about model behaviour out there, this
   may be one of the larger extant samples of it.
