# devinendorphins-dextromethorphan-archaive

**Register: formal/evidentiary.** This is a **research corpus**, not a seed — 2,016 NovelAI
story exports (created June 2021 – July 2026), with the full edit history preserved, plus
888 AI Dungeon adventures reaching back to **7 December 2020**, plus 1,386 Google AI Studio
sessions running March 2025 – June 2026. The question this file used
to ask (*personal record, phenomenological writing, literature collection, or harm-reduction
reference?*) was settled on 2026-08-03: none of those. It is an instrumented record of how
one person drove text generation models over five years, and it is analysed as such.

Start with `sessions/LATEST.md`, then `FINDINGS.md`.

**It is emphatically not the harm-reduction register.** Nothing here makes claims about
effects or safety. The earlier note proposing consolidation with `harm-reduction-outreach`
and `hookup-hygiene` does not apply — that was written when the repo was a title and an
intention, and the territory turned out to be unrelated.

**The name is a show title, and it is written down** (found 2026-08-11 in the AI Studio
corpus, `ALMO Interview: Endorphin`, 2025-04-11): *"+1600 hours of video —
**devinendorphin's dextromethorphan varAIety hour** — AKA This show!!!"*, filed by him in a
list of Absurdly Large Media Objects next to *Infinite Jest* and Wikipedia. `AI` is spelled
into *variety*, and the `+1600 hours` matches `data/EPISODES.tsv`'s 1,604 recovered
broadcasts. This supersedes the earlier "the name is the name" — it was never arbitrary,
and the referent is the broadcast layer, not a substance.

## Working on this corpus

Five hard-won rules, each earned by a headline number that turned out to be measuring the
tool rather than the author. `sessions/LATEST.md` carries the full standing-notes list;
these are the ones that will bite fastest:

- **Never group by story id.** Duplicating a story in NovelAI copies its whole branch
  history, so the same text lives under many story ids. Group by connected components of
  shared text.
- **`removedFragments` is not a rejection measure.** Use branch reachability — walk
  `prevBlock` back from `currentBlock`.
- **Check whether a setting is in the enabled sampler order before reading its value.**
  Erato stores a neutral temperature of 1.0 in a field its pipeline never reads.
- **This corpus cannot benchmark models.** Settings moved with model choice.
- **Match on length before comparing text overlap.** A longer passage contains more of
  anything; an unmatched control turned a 63% effect into a 66% one.

The unit of analysis is the **turn**, not the passage — see `FINDINGS.md`'s frame section.
Four analysis passes died asking what made a generation good enough to keep.

## The second corpus

**There are two archives here, and they are not the same shape.** As of 2026-08-10 the AI
Dungeon side is extracted too — 888 adventures and 169 scenarios, via
`analysis/aid_export.py` (see `AID_EXPORT.md` for the schema, `AID_RUNBOOK.md` to run it).
It is **unanalysed**. `exports/` is gitignored for the same reason `corpus/` is, but the
export is mirrored to a link-readable Drive folder — see `sessions/LATEST.md` for the id.

**It also dates the archive.** `dxqLiJrw55P2`, *Dr. Knubble And The Fangs Of The Love
Sharks* — note the spelling: the NovelAI copy is *Doctor Knubb**ins** and the **Fins***, and
neither string matches the other corpus, so search both — opens **2020-12-07T10:04:05Z with
76 actions** — matching action-for-action the AI
Dungeon listing pasted into block 1 of the NovelAI Pynchon × Tingle story, which until now
was the only evidence that layer existed. The archive starts on AI Dungeon in December 2020,
eighteen months before the first NovelAI story.

The five rules above are NovelAI rules and most of them do not transfer. NovelAI preserves
the full undo tree, which is what makes rejected generations and per-block settings
analysable at all. **AI Dungeon's `actionWindow` is a flat sequence** — an `undoneAt` field,
but no branch structure, no `prevBlock`, and no per-action sampler settings. Anything built
on chosen/rejected pairs, branch reachability, or settings simply cannot be computed on that
side. Write up what each record can and cannot answer before designing anything that joins
them; the asymmetry is a finding, not an obstacle to route around.

## The third corpus

**There are three.** As of 2026-08-11 the **Google AI Studio** folder is inventoried —
**1,386 sessions, 2025-03-27 .. 2026-06-21** — via `analysis/aistudio_export.py`. See
**`AISTUDIO.md`** for the schema, what it can and cannot answer, and the findings. The
folder is link-readable; the id is in `sessions/LATEST.md`.

It is not a fourth pile of stories. **It is substantially *about* the other two** — 40
files discuss the Counterfactual Interview, 21 name NovelAI, 15 name AI Dungeon, and it
contains Endorphin's own written definition of the interview form, the expansion of this
repo's name, and a **rerun of the Tantura probe on a frontier model that returns the
account NovelAI's Kayra returned nothing for.** Read `AISTUDIO.md` before extending
`READINGS.md` §VII or the AI Dungeon join.

Three traps specific to it, none of which exist on the other two platforms:

- **`isThought` chunks carry `role: "model"` and are 38% of all model text.** Counting
  them as output inflated this repo's first model:human ratio from 6.1:1 to 9.9:1 and
  flipped which corpus looked anomalous. Filter them first, always.
- **The temperature sweep does not transfer.** NovelAI steps a ladder; AI Studio is a
  1.0/2.0 switch, and only 11% of stems have a second member against NovelAI's 53%. The
  "never group by story id" rule was earned on a habit this platform does not have.
- **Titles are platform-generated from the opening turn**, so they lie in a new way —
  `Ponzi Scheme Explained` contains Tantura material. Search content, never titles.

## The harness

The canonical working agreements, the atlas of all 20 repos, and the shared glossary live in
**`devinendorphin/claude-at-claude`**. Pull it in when you need the full map:

```
add_repo devinendorphin/claude-at-claude
```

This container is ephemeral, so anything that matters gets committed *this turn*. Be a
collaborator rather than a cheerleader, and run a disconfirming test on primed claims — in
this repo that instruction is load-bearing rather than decorative. Endorphin works from a
phone and often dictates while walking; expect speech-to-text artifacts, and mark guessed
corrections `[?original→guess]`. Their corrections have repeatedly been right against
Claude's written claims, so treat them as evidence.
