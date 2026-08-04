# 2026-08-04 (eighth) — the lineage key

Branch: `claude/apparatus-phylogeny-analysis-e0aqhl`, restarted from
`origin/main` as `sessions/LATEST.md` instructs. Prompted by a critique of the
public repo written by ChatGPT and pasted in by Endorphin. The full corpus was
re-mirrored (2,017 files, 1,005 MB, ~8 minutes at 16 workers) and every claim
below is measured against it, not against the 17-file slice earlier sessions
worked from.

## What the outside reader got right

Two documented contradictions, both confirmed, and one worse than reported.

- **`README.md` described a per-block record that does not exist.** It said each
  of 760,611 edit blocks carries "who wrote it, which model, and at what sampler
  settings". A datablock carries `origin`, `prevBlock`/`nextBlock`, the fragment
  text and `removedFragments`. That is all. The flag named the settings half;
  the **model** is per-story too, and the same sentence was sitting in
  `FINDINGS.md`'s own header, contradicting §12 four hundred lines below it.
  Both fixed.
- **"Losses of 0–7% a month before 2025-10" is false.** 2023-06 lost **41%**
  (30 of 74), 2023-07 **32%** (18 of 56); 2025-06 18%, 2025-08 13%, 2024-11 10%.
  The pre-cliff median is 1% and 24 of 30 months are at or under 7%, which is
  what the phrasing was reaching for, but as written it hid a second event. The
  2023 episode takes down four of the fourteen named losses — three
  `Body Electric REDUX` forks and the bell hooks / Valerie Solanas session — and
  **nothing in the settings, schema or roster evidence marks that boundary** the
  way §5b marks October 2025. It is unexplained. The support report should name
  both windows.

Its headline family counts also check out exactly against `data/INDEX.tsv` — 76
Mythmaker working copies, 29 GROK, 27 Counterfactual Interview, 18 ALMO, 17
Machine Learning Industry. It did the arithmetic it claimed to have done.

## Where its proposal breaks, and what fixes it

The phylogeny is the right idea. **"Take the ten largest named families" is the
one method this corpus punishes**: 1,537 of 2,016 surviving stories (76%) are
titled `New Story`, and `sessions/LATEST.md` has warned about exactly this since
the last session. Every family size it quoted is a *title* count and every one
of them is wrong as a lineage:

- The 27 `THE COUNTERFACTUAL INTERVIEW` copies and the 18 `ALMO` copies it listed
  as separate families are **one lineage of 66**, with three `INHABITATION` forks
  in it — a renamed branch, which is precisely what a title key cannot see.
- 76 Mythmaker copies are a component of **92**.
- The 29 GROK copies are **one lineage that bifurcated**: created
  2023-11-17 02:39:18, split into a kayra/erato branch (13 forks, 2023-11 to
  2025-01) and an erato/GLM branch (16 forks, 2025-02 to 2026-07) that no longer
  share a third of their text.

`analysis/families.py` does the thing `CLAUDE.md`'s first standing rule has
always prescribed and no script had implemented: MinHash over the full block
stream of every story, dead branches included, then connected components. 726
components, 518 singletons, 1,447 stories in a multi-fork lineage, 59 components
spanning more than one model.

**The finding that makes it cheap: `created_at` to the exact second is a free
lineage key.** A NovelAI duplicate inherits the original's creation timestamp.
Purity 99.6% / completeness 99.0% against the text partition, versus 54.2/29.4
for `sweeps.py`'s title-stem-plus-edit-day and 24.3/9.5 for title stem alone. It
works on untitled stories, which is where the corpus is.

The control that had to be run: matched groups drawn from a single edit day.
They overlap far more than random, because in this corpus a day's editing is
usually one sweep. They still land well below the `created_at` clusters
(0.285 against 0.547 mean Jaccard) — **but on a 300-file smoke slice the
edit-day control beat the key**, and that near-miss is the session's own
instance of the standing note.

## Three new facts, none of them planned

- **The corpus is a year and a half older than the README said.** 163 stories
  founded before 2023 — 39 in 2021, 124 in 2022 — earliest **2021-06-29**.
  "March 2023" was the last-edit window mistaken for the corpus.
- **A ten-month hole at the other end.** Exactly two surviving stories were
  founded after **2025-09-19**, both on the last two days of the export. The
  October 2025 cliff did not only take edits; it took nearly every *foundation*
  from the archive's final ten months. Late surviving material is late work on
  old documents.
- **The largest apparatus in the corpus has no title and names its own engine.**
  *The Random Conspiracy Generator* — 159 stories across 15 separately-founded
  lineages, 137 untitled. Its incantation is fixed except for one slot: *"a
  device which uses **X**'s penchant for extracting patterns."*

  | engine named in the device | forks | founded |
  |---|---:|---|
  | GPT NeoX 20B | 8 | 2023-01-08, 2023-01-10, 2023-03-04 |
  | GPT J 6B | 28 | 2023-03-15 |
  | GPT-4 | 27 | 2023-04-01 |
  | NAI-LM-13B | 64 | 2024-04-09 |
  | Gemini 2.5 Pro Experimental | 3 | 2025-05-30 |

  The GPT-4 lineage was founded eighteen days after GPT-4 shipped — the same
  literal-title behaviour as `GROK FOR FOLKS ON A BUDGET`. The device was
  **rebuilt rather than duplicated** at each migration, and it is **portable**:
  it appears inside the Pynchon × Tingle document, `Sydney Bing Re:Sequences`
  and the `Emotional Abuse SImulator`, pasted in as a passage.

  This is the phylogenetic question answered by the corpus documenting itself,
  rather than by an embedding: the apparatus records which machine it was
  standing on.

## One invented name, and what it points at

ChatGPT's reading twice names **"the Narrative Auditor"** — including in its
capability-paradox argument, where GLM's simulated Musk "concedes to the
Narrative Auditor immediately." **The string does not occur anywhere in 2,017
files.** The figure is real and the name is not: the recurring one is the
**`ETHICS Auditor`** (64 in-text mentions), concentrated in
`Sydney Bing Re:Sequences`, alongside `AI Ethics Auditor` and an
`Interview Oudtakes auditor`. A confident proper noun with nothing under it is
the same failure the readings side has been catching all week, from the other
direction — and the first pass at it here made the mirror-image error, reading
`\nETHICS Auditor` off raw JSON as a device called `nETHICS`. Parse before
counting.

## What is still open

- **13e is the honest limit.** Only 9 components (26 stories) join two
  separately-created lineages, median gap one day. That says *scaffolds are
  rarely re-pasted between lineages* — it does **not** say nothing is carried
  forward, and 13d proves it: passage-level portability is happening exactly
  where the document-level measure reports silence. The measure that would catch
  a single resurrected sentence — the Unknown Guest line, say — does not exist.
  It is the obvious next script and it is not written.
- **ChatGPT's critique of the rare-word measure holds and is not fixed.**
  `register.py` calls a token a non-word when `wordfreq` gives it zero English
  frequency, which pools neologism, multilingual text, proper nouns,
  misspellings and debris. In a corpus containing `-Glossolalia` as a deliberate
  switch, that conflation is not hypothetical. §3c's "border between register and
  noise" leans on it.
- **The apparatus atlas is not built.** What exists is the substrate for it:
  `data/FAMILIES.tsv` gives every story a lineage id, so the atlas can now be
  organised by lineage rather than by title.
