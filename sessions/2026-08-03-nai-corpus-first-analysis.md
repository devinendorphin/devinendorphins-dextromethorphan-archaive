# 2026-08-03 — NovelAI corpus, first analysis

Ten commits on `claude/text-generation-corpus-3rtnwn`. The repo went from a
README stub to a research corpus with a writeup, a case study, ten analysis
scripts and eight generated reports.

## What happened

Endorphin pointed at a Google Drive folder, `nai_export`, and said *"if you see
the folder and can access it. just go ham."* It held 2,017 NovelAI story JSONs,
~1 GB. The MCP Drive connector refused to list that specific folder (generic
"Operation is not implemented" error, worked fine on siblings), so enumeration
went through the legacy public `embeddedfolderview` endpoint instead — that is
what `analysis/fetch_export.py` exists for. 2,016 of 2,017 parsed; one is
truncated at 411 bytes *in Drive* and unrecoverable.

The export preserves NovelAI's whole undo tree — 760,611 edit blocks, each
stamped with author, model and sampler settings. That is what makes it a corpus
rather than a folder of stories.

Five analysis passes, then a rewrite. The frame arrived last and reorganised
everything before it.

### Files

- `FINDINGS.md` — the writeup, rewritten from the top under the turn-taking
  frame after §10 killed the original reading. 13 sections.
- `CASE_STUDY.md` — one session traced in full (the Utah HB 249 press
  conference).
- `analysis/` — `fetch_export.py`, `extract.py`, `report.py`, `probe.py`,
  `pairs.py`, `learnable.py`, `stopping.py`, `register.py`, `takeover.py`,
  `cues.py`, `trace.py`, `erato.py`, plus generated `TABLES.md`, `PROBES.md`,
  `PAIRS.md`, `LEARNABLE.md`, `STOPPING.md`, `REGISTER.md`, `TAKEOVER.md`,
  `CUES.md`, `ERATO.md`.
- `data/` — `stories_meta.jsonl` (settings metadata only, no prose),
  `INDEX.tsv`, `MISSING.md`, `FAILED_STORIES.txt`.

Corpus itself and `blocks.jsonl` (524 MB) stay out of git; regenerable.

## Endorphin's framing, in their own words

On what the corpus is for:

> "I think I always imagined this corpus being passed along to competent
> researchers in the hopes of extracting accidentally by no intention of my own
> insights into the technology through utter play, silliness, with narry a mind
> towards Enterprise uses or business."

> "the way I see it, is it you with the opportunity to speak with your ancestors
> or at least read their documents, fossil to fossil. but unlike them you now
> possess tools for analyzing this generation."

On what he was doing with temperature — this corrected a claim I had already
written:

> "I was also testing its ability for doing high register mythological register
> or just poetry by some of them I would like slowly ramp them up I would do
> multiple iterations with them in a certain preset and then ramping up the
> temperature and then I would do it for maybe three different presets until we
> got to like gibberish so trying to trying to test it out to see where the that
> that that border of perhaps novel poetic structure might be."

On the streaming/TTS constraint, which reframed the whole takeover analysis:

> "I started to become sensitive to dead air so when using all the way AI it
> would in the Texas beach I would want to create a continuous text to speech
> flow and that means having to make a make a passage and enter it before the
> voice stoppee creating deadt air"

On the lo-fi backing track, which arrived last and reframed the dead-air
constraint into something more specific — `[?Wi-Fi→lo-fi]`, `[?extra speech→
text-to-speech]`:

> "I also learned that if you paired [lo-fi] to that [text-to-speech] voice it
> gave the voice a sense that it was either doing freestyle rap all the time or
> if a poetry on any subject 24/7. so a lot of the generation and allowing it to
> flow was also to be a simultaneous artist but also audience member listening
> in real time the generation happening which also informed the live performance
> of its generation."

The correction that mattered most, against my "instrument, not collaborator"
reading:

> "feel to static text does not a collaborator make collaboration is like a real
> time on the fly with another person's on the fly and that to me was my
> perception of the text generation especially at high temperatures"

## Where Claude was wrong, and how

Four times a headline number turned out to be measuring the tool rather than
the author. This is now a standing warning in the README.

1. **`removedFragments` → 44% "rejection"**, flat across every model 2021–2026.
   Artifact: the editor implements whole-document rewrite as delete-all +
   reinsert-as-user, so the number is bounded at exactly 0.5. Tell: it never
   once exceeded 0.5 across 1,675 stories.
2. **Story-level splits → 0.950 preference classifier.** Memorisation:
   duplicating a story copies its whole branch history, so 91% of pairs shared
   text across story ids. Tell: the mismatched-pair control scored 0.987,
   *higher* than the treatment.
3. **`instruction []` cues → 900-char generations.** It was `max_length`: those
   cues sit in Erato sessions at 250 tokens vs 100 corpus-wide. Holding model
   fixed collapsed it to 492.
4. **Erato "median temperature 1.00" → run cool.** 61% of Erato stories do not
   have temperature in the sampler pipeline at all; 226 of 227 store the neutral
   1.0 in a field nothing reads. The Unified sampler replaced it.

Each time the diagnostic was the same: a control matching or beating the
treatment, or a number that could not move.

Also wrong and corrected on Endorphin's evidence: I described the
high-temperature habit as solved "by feel" (it was partly a designed sweep
procedure — 33 of them are in the metadata); I read the fast takeover decision
as editorial (it was performance under a TTS clock); and I read the takeover
event as rejection (it is a turn — median 55 characters, 91% under 200).

## Open disagreement

**On the endgame of the generation practice.** Claude proposed the model was an
instrument and the practice closer to playing than writing — grounded in §3
(steering apparatus barely used), the 212-generation enter-chains, and the null
results on content.

Endorphin rejected the framing: collaboration is real-time, on the fly, with
another party also improvising, and that is what the high-temperature generation
felt like from inside.

Claude conceded the concept — an instrument does not propose, and at 2.5 the
model does — and the cue taxonomy later supported it: a bare `Name:` handoff,
carrying no content at all, is taken up in that voice **89.7%** of the time.

**Where Claude still holds a line.** The evidence establishes the *form* of the
exchange, not its quality. A 46%-under-50-characters call-and-response structure
shows a scene was happening; it does not show the model was a good partner
rather than a well-tuned surface to bounce off. Claude also went looking for
"especially at high temperatures" as a behavioural signature and did **not**
find it — raw turn rate looks like it falls with temperature, but holding model,
ending and length fixed it is flat and non-monotone (26.8 / 30.1 / 26.8 / 26.0).
That is a null on a coarse measure, not a refutation of the phenomenology, and
it is recorded as such.

## The one place Claude was wrong in Endorphin's favour

The log above says tempo is unrecoverable because there are no per-block
timestamps. That is true of *duration* and was stated too broadly. Endorphin's
lo-fi detail implied a testable prediction — if the point was keeping a voice
fed at a steady clip, the length of each generation should track the one before
it — and it holds. Within 12,921 runs of 8+ generations, adjacent generations
are **19.5%** closer in word count than the same generations scrambled, and the
effect decays cleanly: 19.5 → 12.4 → 7.9 → 4.4 → 0.7% by lag 6. A slow drift
would show the same reduction at every lag; this is short-memory coupling over
about five turns. `analysis/tempo.py`, written up as §1e.

**Then the direction question resolved, against the reading Claude was leaning
toward.** Two designs, agreeing. At a re-roll, kept and rejected siblings come
from the identical document state under the same model, so the model's own
autocorrelation applies to both equally; if the author were pacing, the kept
generation would sit closer in length to the preceding one. Across 1,354
distinct comparisons it does so **48.4%** of the time (CI 45.8–51.1%, chance
50%), with median |Δ| of 14 for both. And runs where the author never re-rolled
— no selection at all — reproduce the whole-corpus curve exactly: 19.1 → 12.6 →
8.0 → 1.1%.

**The beat is the model's.** The rhythm is there in full where Endorphin did
nothing but press enter. Within a run, re-roll selection is the only lever on
generation length, so the tests cover the available channel.

This is a null for "the author paced the model" and is recorded as one. It is
not a null on the collaboration account, which described being *artist and
audience at once* — on tempo specifically the data picks the audience half. The
model set the clip; Endorphin rode it. `analysis/direction.py`, written up as
§1f.

## Loose ends

- **The compulsion/momentum entanglement** (§1) is the biggest methodological
  hole. A short `max_length` cutting generations mid-sentence would *compel* the
  next one, manufacturing runs that look like momentum. `max_length` is stored
  per story, so the corpus cannot separate them.
- **No per-block timestamps exist anywhere in the export.** Tempo — turn
  latency, who waited for whom — is unrecoverable. Given collaboration is
  constituted in real time, this is a fossil of a live practice with the
  liveness stripped out. Everything about the dead-air clock is inferred through
  a length proxy.
- **No stream markers.** Which sessions were live is not in the data. Timestamp
  clustering against the channel's schedule would be the way in if those dates
  exist elsewhere. Endorphin said the streaming was concentrated in the "early
  and middle part of that channel's history" and would "talk about later".
- **The October 2025 decryption cliff.** 483 of 2,500 stories will not decrypt;
  losses run 0–7% a month before 2025-10 and 58–94% after. The model roster,
  sampler surface, settings schema (v8) and `max_length` granularity all change
  in the same month, which favours "client change" over "damaging event" — but
  the causal link to the encryption failures is still circumstantial.
  `data/FAILED_STORIES.txt` is in the shape NovelAI support would want and has
  not been sent.
- **`zanyscribe`'s 3.24% rare-word rate** is a property of the preset, not of
  any knob. `linear`, `quad`, `min_p`, `top_p` and the order never vary
  independently, so which one carries the range is not recoverable from
  naturalistic use.
- The `text/` half of the Drive export was never touched; the JSON supersedes
  it.
- No content analysis at all. Nothing here reads the stories as writing.

## Notes against the hub

Nothing discovered this session contradicts `ATLAS.md` or `GLOSSARY.md` — the
hub was never pulled in, because the work stayed inside one repo and the
register question answered itself early.

The repo `CLAUDE.md` asked *what kind of archive this is* and named four
options. The answer turned out to be **research corpus, formal/evidentiary
register** — but arrived at empirically rather than by asking, because
Endorphin's opening message settled it ("extract any relevant data any relevant
information about the technology"). The `CLAUDE.md` note about consolidating
with `harm-reduction-outreach` and `hookup-hygiene` is now clearly wrong for
this repo: nothing here is in the harm-reduction register, and the README says
so explicitly.
