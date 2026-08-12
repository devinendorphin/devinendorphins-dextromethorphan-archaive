# devinendorphins-dextromethorphan-archaive

**Register: formal/evidentiary.** This is a **research corpus**, not a seed — 2,016 NovelAI
story exports (created June 2021 – July 2026), with the full edit history preserved, plus
888 AI Dungeon adventures reaching back to **7 December 2020**. The question this file used
to ask (*personal record, phenomenological writing, literature collection, or harm-reduction
reference?*) was settled on 2026-08-03: none of those. It is an instrumented record of how
one person drove text generation models over five years, and it is analysed as such.

Start with `sessions/LATEST.md`, then `FINDINGS.md`.

**It is emphatically not the harm-reduction register.** Nothing here makes claims about
effects or safety. The earlier note proposing consolidation with `harm-reduction-outreach`
and `hookup-hygiene` does not apply — that was written when the repo was a title and an
intention, and the territory turned out to be unrelated. The name is the name.

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

**As of 2026-08-12 there are three archives, and the newest is the smallest and the most
different.** A Twitter/X export (`analysis/tw_export.py`, schema and asymmetry table in
`analysis/TW_EXPORT.md`, measurements in `analysis/TWITTER.md`): 3,909 tweets, 432 long-form
posts, and **2,818 Grok chat turns across 431 chats**, 2024-12-07 .. 2026-07-29.

Two rules for it, and they pull in opposite directions:

- **Almost nothing transfers to it.** No undo tree, no rejected generations, no sampler
  settings, strict User/Agent alternation. Everything built on chosen/rejected pairs,
  branch reachability or settings — most of `analysis/` — simply cannot be computed here.
- **It is the only archive with a clock**, which is the one measurement NovelAI is
  structurally incapable of (`FINDINGS.md` §11). But the resolution is **one timestamp per
  exchange, not per turn**: the Agent turn copies the request stamp exactly, in 1,409 of
  1,409 cases, so model latency is unrecoverable and every interval mixes generation,
  reading and typing.

**And it is not the same practice** — 431 utility chats at a median of 4 turns and one
minute, against NovelAI documents of 3,341 blocks. Do not read it as more of the corpus.

**Privacy is not inherited here.** The public-repo decision was made about Endorphin's own
fiction; it does not extend to an export containing direct messages, a phone number, an
email and an IP audit. `tw_export.py` has a `SKIP` list and never opens them. Anything
committed to `data/` from this archive carries **lengths and dates only, never message
text**. Keep it that way.

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
