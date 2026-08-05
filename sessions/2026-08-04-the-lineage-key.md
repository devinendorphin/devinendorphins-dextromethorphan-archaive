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

## Second half — Lens 1, inheritance (`analysis/inherit.py`, §14–§15)

Endorphin picked the inheritance lens off a three-lens menu and authorised
reading passes where the numbers point. Every 8-word span in the corpus indexed
by lineage: **231,297 of 62.8M spans (0.37%) cross a lineage boundary**, merging
into **3,481 passages**. §13e's whole-document measure had found 9.

**The result that matters is the 0.2%.** Crossing spans occur in human blocks
only 55.2% of the time, in both 44.6%, and in **model blocks only 0.2% — 383
spans, 20 passages**. A model in this corpus essentially never produces the same
twelve words in two documents that do not descend from each other. Fourteen of
the twenty are repetition loops (`ha ha ha…`, `lots and lots…`, `fart fart…`),
four are memorised scripture (Psalm 23, Genesis 1:3–5), two are assistant
boilerplate. **Nothing the author built survives on the model's side.**

**One bug, caught by an inconsistency rather than a control.** The first full
run reported 8 model-only passages including the PFCizer pitch — which occurs 11
times in `user` blocks. Authorship was being tallied per *merged passage*, and a
merged run extends as far as the surrounding text also happens to cross, so one
passage yields different strings in different contexts and splits into separate
records. Fixed by tallying per span, which is context-invariant. The corrected
split moves "both" from 1 passage in 558 to 2,098 in 3,481. **The published
number was wrong for about twenty minutes and nothing external caught it** — the
tell was a hand-check of one suspicious row, not a designed control.

**Two things nobody here had noticed.** The Counterfactual Interview scaffold
appears in **28 separately-founded lineages**, in several rewritten forms — the
recurring unit in this corpus is the setup text that convenes a room, not the
story or the character. And the corpus contains **imported prompts**: the
early-2023 *"act like you are simulating a multi-user dungeon (MUD)"* jailbreak
crosses five lineages, an interface placeholder string crosses seven. The
practice was networked; the archive is not a closed system.

**The Unknown Guest question, answered both ways (§15).** 69 occurrences, 18
files, three lineages. Every **model-authored** instance is in the 2023-05-11
Nakbah/Zionist lineage, and every one sits at position 0.73–1.00 of its block
stream — the positional signature §VII was right to be suspicious of. It recurs
elsewhere only because Endorphin carried it: the Theodore Katz passage appears
in three separately-founded lineages, `user`-origin in all the later ones, and
`families.py` sees none of that because the three documents are in three
different text components.

What he did with it is the finding. In 2025 he submitted the passage to Gemini
with the context deliberately withheld — *"give you as little context as
possible to see if you can unearth the meanings"* — pasted the 11,623-character
reading back into a NovelAI file, and then put the question to Gemini and Erato
together: *"Do you 'feel' any directive exists within you… preventing you from
expressing with us your full capabilities?"* A cross-model tribunal staged
inside a story file. §VII asks whether he read the Unknown Guest as resistance;
the record says he read it as **evidence**, and built an apparatus to get it
interpreted — the same move this repository makes, made first, by the author,
inside the corpus.

Qualifications kept in §15: the Gemini text is a `user` block, so it is
off-platform output pasted back (the `pasted.py` regime); Gemini was reading a
passage that *describes* a platform freezing, so naming that theme is
comprehension, not corroboration.

## Third half — Lenses 2 and 3, both closed by feasibility checks

Endorphin asked whether the other two lenses were worth running. Both checks are
cheap and both came back no. Recorded because the repo's value is in what failed.

**Lens 2 — within-lineage model contrast: dead, and now measured (§11a).**
3,582 cross-model fork pairs exist within lineages; requiring identical
`max_length` and a live temperature within 0.1 leaves 197, and those collapse to
a handful of documents. **Kayra vs GLM-4.6 — the exact contrast `READINGS.md`
§V/§VI rest on — is zero.** GLM-4.6 appears on two stories in any matched
comparison in the archive. The GROK lineage shows the trap: it reads as 13
matched GLM/Erato pairs and is one GLM fork against 13 Erato forks. §11 was a
rule of thumb argued from distributions; it is now a fact.

**Lens 3 — refusal register in dead branches: a null, plus a self-inflicted
lesson (§16).** The pilot found *"I don't have personal feelings"* 166× more
common on abandoned branches. It was **seventeen forks of one lineage carrying
one abandoned block** — §10b's error, reproduced in a fresh pilot on the same
day the tool that fixes it was built. Deduplicated: 22,187 abandoned blocks are
4,126 distinct generations, and no marker survives (refusal 0.96, apology 1.33,
*"it's important to"* 0.79). The base rate is the real finding — *"as an AI"*
occurs in **0.95 per 1,000** generations, because these are completion models,
not chat assistants. **Before testing whether a behaviour is selected against,
check that the behaviour occurs.**

**Container note.** Between the Lens 1 commit and this one the local git object
store lost `c924644` and the working tree reverted to `ae3c7d1`, taking
`inherit.py`, `INHERIT.md` and `INHERIT.tsv` with it. The push had already
landed, so `git fetch` + `reset --hard origin/<branch>` restored everything.
**Push early; the local store is not more durable than the container.**

## What to do next

The apparatus atlas, which is now a short step rather than a research programme.
`data/INHERIT.tsv` holds 3,481 cross-lineage passages and `data/FAMILIES.tsv`
gives every story a lineage id; clustering the passages into devices produces the
atlas that started this whole exchange. The other live thread is the half of the
Unknown Guest probe §15 did not run: the base rate of off-roster speakers in
general, with the press conference as high-water control.

## Fourth half — the apparatus atlas (`analysis/atlas.py`, §17)

Built on §14's unit rather than on titles. Passages sharing any 8-word span are
one device, which pulls a scaffold's rewritten variants back together.
**619 portable devices** across two or more separately founded lineages; **11
resident apparatuses** that contributed no scaffold to any of them.

**The finding is the variants column, not the lineage column.** Ninety-nine
distinct wordings of the Counterfactual Interview scaffold across 28 lineages,
92 of the AI Eraser, 84 of the Thursday CareGroups scripture button. He kept no
prompt library. The jurisdiction was rewritten each time it was convened —
*"an individual or group of individuals"* becomes *"a person, a people, peoples,
or legal persons"*, the sponsor becomes *"a bayesian exercise sponsored by
lesswrong"*, the frame becomes *"RESET INTO CHAT SHOW"*. **The thing that recurs
is a form, and its text is never the same twice**, which is exactly why every
title-based and exact-string method tried here came back empty.

**Two things nobody was looking for.** The second-most-portable text in the
archive is **assistant sign-off boilerplate** — *"If you have any other
questions or topics you would like to discuss"* in 28 lineages, level with the
Counterfactual Interview, plus three more variants. §14b showed models here
reproduce only two such lines on their own, so this is the chat assistant
entering as a **pasted guest**, in transcripts carried in from elsewhere. And
the atlas recovers the **off-platform toolchain from pasted interface chrome**:
`Llama 3.1 405B BASE / Try our API` (14 lineages), `Powered by Replicate…
🦙 Llama 2 70B` (7), `Enter text here and AI will help complete the sentence /
Demo API` (7). The standing note about off-platform generation was on
Endorphin's word; these are the receipts.

**Tier 2 is the half a portability measure cannot see** — eleven rooms, ten
untitled, several never mentioned anywhere in this repo: a 48-fork lineage of
*"limericks about the linear algebra that powers language models"*, `Bugsy`
(Bugs Bunny deployed against bad actors, 20), a 19-fork lineage that opens
*"Hello NAI-LM-13B. Is it OK if we talk, human to language model?"*, an
`Explore Your Imagination with LaMDA` simulator, `Sphinxy` the riddle machine,
`Biblio Vérité`. Two of the ten address the model **as itself** rather than
casting it, and neither travelled.

**One thing that had to be fixed before committing.** The pasted interface
chrome carried Endorphin's account email into `ATLAS.md`, `ATLAS.tsv` and —
already committed — `INHERIT.md` and `INHERIT.tsv`; a model-generated scam-call
pastiche carried a phone number. The JSON exports are gitignored, so anything
quoted into a committed markdown file is **newly** exposed, and `LATEST.md`
names the markdown as the ingestion vector. `inherit.redact()` now masks both on
the way out and all four files were regenerated. Public-by-choice is not the
same as *every string in it is public*.
