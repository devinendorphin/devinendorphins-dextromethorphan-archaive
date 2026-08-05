# 2026-08-05 — Six ways of coming apart

Endorphin, dictated: *"further study of Myths for now. especially the ones that
are about three or four different outputs at three or four different presets
because the different types of language shaping or different… if we can maybe
text anonymize [?taxonomize] the types of… and see if we can characterize them
cuz maybe other things that names have get to be put to them yet, you know?
these ones are very much explorations of that that border of coherence."*

He was right about the object before anyone looked at it. **`Mythmaker - Working
Copy`, 76 forks**, three presets rotated with temperature stepped under each,
across five months — three or four outputs at three or four presets, exactly as
described. *Myths for Now* is also a stream segment: five episode titles in
`data/EPISODES.tsv` from 2024-03-08 alone (*Tales of Ephedra*, *Mixing Ammonia
and Bleach*, *Staying In Your Lane*).

## Why this document and not another

It is the only place in the corpus that supports **attribution of text to
settings**. The 76 forks are an append chain, not parallel copies: 67 of 75
consecutive pairs are a strict prefix relation, so fork *n+1* is fork *n* plus
new blocks at the end, and those blocks belong to *n+1*'s saved settings. One
model, `max_length` held at 100 in all 76. 1,310 attributed generations,
625,000 characters.

Two controls before believing any of it, both passed: text is more homogeneous
within a fork than under a shuffle of blocks between forks of the same day
(p = 0.0005), and the preset spread at 2.5 beats shuffling preset labels within
day (p = 0.0005).

## The finding, and the correction it forces

The three presets are three different machines, and the difference that matters
is **where the truncation sits relative to temperature**:

| preset | enabled order | top_k |
|---|---|---|
| `freshcoffeek` | cfg → temperature → **top_k** → top_p → tfs | 25 |
| `asper` | typical_p → temperature → **top_k** → tfs | 175 |
| `writersdaemon` | mirostat → temperature → typical_p → tfs → top_p → top_a | none |

At **2.5**, the same story on the same model: **0.61%** non-words under
`freshcoffeek`, **0.75%** under `asper`, **7.18%** under `writersdaemon`.
Eleven-fold, at one value of the dial. Heat a distribution and then cut it to 25
candidates and the heat has nothing left to do.

Which forces a correction to this repo's own `analysis/SWEEPS.md`, and it is not
a small one. That report reads the 216 fork clusters as temperature ladders.
**Only 24 of 216 hold the preset constant (11%); 92% of the swept forks sit in
clusters where preset and temperature moved together.** `sweeps.py` now reports
the preset alongside the model and `max_length`, and the regenerated report says
what it does not settle. The clusters are two-factor designs; the second factor
was invisible because the script only looked at `temperature`.

## The thing I did not expect

The `Name:` convention — what §I and §II are built on and what `FINDINGS.md` §7
measures at 85–90% — **collapses at 2.5 under all three presets, by 93–96%,
including the two whose vocabulary does not move at all.**

The obvious objection is that Endorphin *chose* when to run 2.5, so this might
just be him running it over monologue stretches. Matching generations on the
speaker-line density of the 1,200 characters they were continuing from kills
that: handed equally dialogue-dense context, 2.5 returns a speaker line in **6%**
of generations against **38%** below it (p = 0.0002).

So the order of dissolution is **frame, then syntax, then the word**. The show
loses its institutions before it loses its language, and the layer everyone
notices first — the coinage — is the last to go and under two presets never goes
at all. The assistant register goes the same way: *"I'm always happy to help!"*
is a **low**-temperature production, an institution rather than a symptom.

This also gives a partial answer to the standing top priority. If the Unknown
Guest were high-temperature debris, unnamed speakers should multiply with the
dial. Here they do the opposite — 1.5 per 1,000 tokens below 2.0, 0.1–0.7 at 2.5.
An uninvited speaker is a **mid**-temperature event. One document, one model, and
it does not replace the corpus-wide base rate, but it points the way Endorphin
said it pointed and against the reading Claude defended.

## Two borders, and a null

`asper` at 2.5 and `writersdaemon` at 2.5 are both "the border of coherence" and
they are not the same border. **40% of `asper`'s coinages there are
better-formed Spanish than English**, against 8–12% everywhere else — it leaves
the language, with real Spanish function words caught in the wreck
(*"Estopachida mejcascocas nondustano apresteya **hace** caya **ma la**
pascina"*). `writersdaemon` stays inside English and pulls the word apart:
`pluumpurk`, `fearature`, `mythstood`. §VII's *"like how in laws speak in their
native tongue around the daughters boyfriend"* describes the first one exactly.

And the null: **a word the model introduces comes back in Endorphin's own typing
12.5% of the time if it is common, 2.5% if a rare real word, 0.23% if a
coinage.** The model's own later text: 51% / 12% / 1.2%. Nothing invented is
kept, by either party.

The first version of that measure returned **0.00% for every class**, because it
excluded any word he had typed *anywhere* in the document rather than *so far* —
circular by construction. The broken control is the only reason the corrected
number is trustworthy, and it is recorded in the report for that reason.

It is not a verdict on the practice. §VIII found an alliterative naming *schema*
surviving three rewrites and an anti-prompt; both are true. The schema persists,
the instances evaporate. Coinages are readings on an instrument, and you keep
what you learn about the instrument, not the readings.

## What was written

- `analysis/myths.py`, `analysis/MYTHS.md` — new.
- `analysis/sweeps.py` → regenerated `analysis/SWEEPS.md` — the preset correction.
- `READINGS.md` **§IX. Six ways of coming apart** — the six named modes, one
  passage each. **It breaks the document's own standard** (built on measurement,
  falsifiable by re-running a script) and the header now says so and says why,
  rather than folding it in quietly. `README.md` carries the same caveat.
- `corpus/cited/` — two `Mythmaker` forks, not one: the append chain branches on
  2024-05-31 and both terminal arms carry quoted material. They back the
  quotations and **cannot reproduce the report**, which lives in the differences
  between consecutive forks. Refetch instructions are in the directory's README.

## Open

The six names — **the clerk, the name-forge, the caster, the trapdoor, the held
note, the glossolalia engine** — are proposals. Each has a measured definition
that survives a rename, which is the part that matters. He was in the room and
has been running these since 2024 with no names on them.

The preset was never randomly assigned. Whether he reached for `writersdaemon`
when he wanted the room to come apart, or found out what it did by running it,
is the difference between a technique and a discovery, and only he knows.
