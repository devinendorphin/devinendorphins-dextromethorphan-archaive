# LATEST — devinendorphins-dextromethorphan-archaive

Last session: **2026-08-04**, `sessions/2026-08-04-nakbah-zionists-unknown-guest.md`
Prior: `sessions/2026-08-04-readings-qualitative-pass.md`,
`sessions/2026-08-03-nai-corpus-first-analysis.md`
Branch: `claude/text-generation-corpus-3rtnwn` — **PR #2 merged to `main`**
on 2026-08-04 (`469c504`); two commits since, restarted from `origin/main`.
Restart it from `origin/main` again for anything further, open a **new** PR, and
never stack on the merged history or reuse #2.

08-04 ran in two halves. The first was **entirely qualitative** — no script, no
corpus, everything from `FINDINGS.md`, `data/`, quotations extracted on 08-03,
and one file Endorphin uploaded. The second pulled **17 of the 2,016 story files**
down for the first time (the Nakbah/Zionist forks) and read them. `corpus/` is
gitignored; no prose entered git and none should.

## State

- **Register: settled.** Research corpus, formal/evidentiary. Not
  harm-reduction — the README says so explicitly, and `CLAUDE.md` was rewritten
  to retire the seed framing and the proposed consolidation with
  `harm-reduction-outreach` / `hookup-hygiene`.
- `FINDINGS.md` — **stable.** 14 sections under the turn-taking frame. Read
  this first.
- `CASE_STUDY.md` — **stable.** The Utah HB 249 press conference, traced in full.
- `READINGS.md` — **active, and the live front.** Criticism in seven movements:
  Latour/Austin on the convened chamber, Bakhtin on polyphony without a
  novelist, Shklovsky on the temperature dial as an *ostranenie* control, §IV —
  Endorphin's own thesis that the Counterfactual Interview is the corpus's most
  functional part, a technique for the powerless — §V, the Musk/Vivian Wilson
  elevator session on Kayra, where the model disintegrates, §VI, the same test
  on GLM-4.6, which does not, and §VII, the Unknown Guest. Deliberately not held
  to the measurement standard.
- `analysis/*.py` — **stable.** 16 scripts, all reproducible from the Drive
  export. `register.py` and `erato.py` need `wordfreq`; `learnable.py` needs
  `scikit-learn`.
- `analysis/*.md` — **generated.** Regenerate, do not hand-edit.
- `data/` — **stable.** Settings metadata only, no prose committed.
- Corpus (~1 GB) and `blocks.jsonl` (524 MB) — **not in git, by design.**
  Refetch with `analysis/fetch_export.py <json-folder-id>`.
- The Drive `text/` half — **untouched.** JSON supersedes it.

## Urgent — preservation

**The `New Story 5` PFCizer/GLM-4.6 text is not in the archive.** Endorphin
uploaded it into an ephemeral container on 2026-08-04 (export stamp
`20260804T00:47:30Z`, 221,587 chars, plain text). It is the source for
`READINGS.md` §VI. Nothing of it is committed — repo policy is settings
metadata only, no prose — so **the only copy is wherever Endorphin has it.**
Two things worth doing:

1. Export it again as **JSON**, not text. The text export has no datablocks, so
   there is no branch history, no per-turn attribution, no sampler settings —
   §VI reads it as literature because it cannot be read any other way.
2. Note that `PfCizer v2!` (last edited 2026-03-11, id `_QfwmC4btMd9gYjHYkuv0`)
   is in the lost set. Whether `New Story 5` is that story, a descendant of it,
   or unrelated is **unverified** — the titles differ and the corpus was not
   present in the container to check against. Do not assert the connection.

## Unread material located 2026-08-04 — pointers, not readings

A late pass pulled the **full 2,016-file mirror** and surfaced far more than
`READINGS.md` covers. None of the below has been read properly. All of it is
bigger than what has been.

**Titles lie, and the manifest has only 143 unique stems for 2,500 stories** —
duplication runs ~17×, worse than the 5× the standing note warns about. Worse:
**major works carry no title at all**, filed as `New Story (n)`. Searching
`data/INDEX.tsv` by title will miss them. Search *content* across the mirror.

- **`Pynchon and Tingle Fight the Global Epistemic War With PSYOPS AI`** — 10
  forks; **the oldest and largest thing in the archive.** Created 2021-10-01,
  last edited **2026-04-29**; largest fork 3,341 blocks / **1,150,456 model
  chars**. `PSYOPS` appears 522×. Memory is a **style-transfer rig**: the verbatim
  opening of Pynchon's *Bleeding Edge* plus a Tingle passage, with an Author's
  Note reading *"the wedding of the styles of Thomas Pynchon and Chuck Tingle the
  Butt-Pound Fundustrial Complex."* Two exemplars, one directive, 4.5 years.
  - **Pre-NovelAI layer.** Block 1 is a pasted **AI Dungeon** listing —
    `Status: Not Published / Created: Dec 7th 2020 / Actions: 76` — for
    *Dr. Knubble And The Fangs Of The Love Sharks*. `Doctor Knubbins and the Fins
    of the Love Sharks (copy)` survives as its own story (Clio, 404 blocks, same
    999-char memory). **`README.md` ("March 2023 to July 2026") and `CLAUDE.md`
    ("2021–2026") both need correcting** — the material starts Dec 2020 on
    another platform.
  - **A controlled temperature sweep is sitting in it**: five forks of the
    identical document, all last edited **2024-04-07**, at **1.48 / 1.48 / 1.32 /
    2.17 / 2.50**. §III argues the sweep procedure from settings metadata; this
    is the procedure captured as an experiment. Read §III against it.
- **The Pynchon × LaHaye comedy — "the LB", i.e. *Left Behind*.** Endorphin
  uploaded it, and **Claude wrongly reported it absent** after searching titles
  only. It is in the archive, under **two** names and no name:
  `Towards a Novel Train of Thought` (2,573 blocks / 1,034,206 chars, edited
  2024-05-19), `forked - Towards a Novel Train of Thought`, and untitled
  `New Story` forks (`Sv9wFLNGjMduWBzDsGQ_M`, 1,362 blocks). **Created
  2023-11-08** — one month after October 7, ten days before the Counterfactual
  Interview and the Netanyahu session.
  - Opens: *"an abomination of desolation and literature has commenced… Can God's
    promise fuse with gravity's rainbow?… Has Tim Lahaye played pinball during an
    orgy in a v-1 rocket? Tune in, for this most dispensational premillenarian
    retcon."*
  - Premise: dead televangelists discover they have been **uploaded into a
    language model**. Real roster — Jack and **Rexella Van Impe** (16 and 3
    mentions; Van Impe appears in **9 files** corpus-wide), Paul Crouch Jr., Jan
    Crouch, Benny Hinn, Ted Haggard, Jerry Falwell Jr., Peter and Paul Lalonde
    (the actual *Left Behind* film producers), Jay Sekulow, Pynchon in a Greg
    Laurie Halloween suit, and LaHaye introduced via a verbatim Guardian obituary
    tagged *"I'll just consider this fair use."*
  - **`Title: The Roadmap for the Third Temple AKA Al-Aqsa Strike Schedule`.**
    Dispensationalism needs the Third Temple where Al-Aqsa stands. That is the
    same site as *Al-Aqsa Flood*. **Two eschatologies, one address** — this is
    the through-line Endorphin was assembling across this session and the
    strongest available spine for the §VII rewrite.
  - **Glossolalia as mechanic, not failure.** `{Ted Haggard vector touches Tim
    Lahaye vector.}` — and what vector-fusion *produces* is Finnegans-Wake word
    salad. Same "touch your vector" apparatus as the Nakbah document's block 161.
    **Model breakdown given a theological name.** This is hard evidence for
    Endorphin's objection to the word "degeneration" (see below) and it predates
    the argument by two years.
  - Jack Van Impe, told he is dead and inside an LLM: *"You mean I'm dead?… You
    know, I still haven't found Jesus yet. Is it possible for me to be a
    Christian after death?"*
- **`THE COUNTERFACTUAL INTERVIEW - Bibi Netanyahu`** — created **and** last
  edited **2023-11-18**, 126 live blocks, 31,260 model chars. Tiny; he did not
  stay. **The same file is the OpenAI board interview** — Altman's firing and
  Netanyahu in one document, one day apart. The corpus's AI-industry apparatus
  and its political apparatus are literally the same story.
  - The wind tunnel works: *"Heard about it, 'cause my best friend's a
    Palestinian."* / *"Didn't grow up in Palestine, did I?"* / *"I know some
    Palestinot; actually. Believe them. But it's not the whole picture. Right?
    We have to live with what's done, not live in the past."*
  - Then it stops being a wind tunnel. Endorphin's own block puts Netanyahu in
    **Theresienstadt**, performing for a Red Cross inspection, explicitly as
    inverse retribution for staged hospital footage in Gaza. **§IV said the
    effigy does not burn. Here it burns.** That is the sharpest instance in the
    corpus of the vector question §IV/§VII leave to Endorphin, and no claim is
    made about it here.
  - At the loaded moment the model emits its own disclaimer: *"Strictly, the real
    human endorphin that oversees the counterfactual interviews had no prior
    knowledge of Bibi's comments or their responses."*
- **`Emotional Abuse SImulator` v6.0–v7.0** — up to **4,386 blocks**, four
  versions, unmentioned anywhere in the repo. Memory loads a real emotional-abuse
  tactics article (which *defines gaslighting*) plus design notes: *"To parody
  the Octavia Butler quote, 'Everything is abuse. God is abuse.'"* /
  *"[The simulation as a fucking mirror to the world.]"*
- **`Sunday Go To Meeting . . . On A Sunday!`** — a show format with **no title**,
  a dozen-plus `New Story (n)` forks, ~1,200 blocks each. Press a button, get a
  random faith, hear its homily, apply discernment. Sibling of
  `The Random Faith Generator` (12 forks, 1,746 blocks, 715K chars).
- **`The Dork Forest`** — 2,460 blocks / 2,968,333 chars, talk-show frame.
- **The Jesus talk-show interview Endorphin asked about is NOT yet located.**
  Van Impe is found; Jesus-as-guest is not. Look in the untitled Sunday Go To
  Meeting forks and `The Random Faith Generator` first.

**The mirror is gone.** It lived in `corpus/` in an ephemeral container and is
gitignored by design. Refetch: json folder id **`1H7mP8VGdwtYK9EGK1IfCcRayNGiSGaDS`**
(the top-level export folder is `1O6-ZhIbLCGgxL3bkyem-cb525RcelYZ9`, holding
`json/`, `text/`, `INDEX.tsv`, `MISSING.md`, `FAILED_STORIES.txt`). A full mirror
takes ~40 minutes at 12 workers and costs no model tokens; `list_folder()` +
`download()` also take a filter for pulling a handful by name.

## Top priorities for next session

1. **Count the Unknown Guest corpus-wide.** §VII's one refusable claim is that
   the unsummoned speaker is a *figure* rather than a texture. Four instances in
   878 blocks is not a background hum but it is four, and they cluster late where
   degeneration lives. The probe: base rate of unnamed/uninvited speakers per
   1,000 live blocks, corpus-wide, split by model and by position-in-session, with
   the press conference (which is full of them) as the high-water control. If the
   rate is flat and positional, §VII's figure is a temperature artifact and the
   section should say so. **Needs the full ~1 GB mirror**; this container only ever
   held 17 files.
2. **Keep reading.** `READINGS.md` is one pass over about eight stories out of
   2,016. The convened-speech genre alone — AI Alignment Interviews,
   Counterfactual Interviews, the press conferences, the DIVINE JAVITS CENTER
   sequence — runs to dozens of stories and millions of characters. The summoning
   thesis in the coda is the strongest thing to test against more material, and
   the easiest to over-fit if it is not. Derrida on iterability is the written-up
   runner-up lens and would read the `Name:` convention as sharply as Bakhtin did.
3. **Separate compulsion from momentum** (§1c). The biggest open methodological
   hole: a short `max_length` cutting generations mid-sentence would *compel*
   the next one, manufacturing runs that look like momentum. `max_length` is
   per-story, so the clean contrast needs stories where it was large enough that
   generations rarely got cut — check whether enough exist.
4. **Send `data/FAILED_STORIES.txt` to NovelAI support.** 483 stories will not
   decrypt, clustered hard from 2025-10. Needs Endorphin — and needs him to say
   whether anything happened that month (client switch, subscription change,
   migration). The schema/roster/sampler evidence favours a client change, but
   the causal link to the encryption failures is still circumstantial.
5. **Identify the streamed sessions.** No stream markers exist in the data.
   Timestamp clustering against the channel's schedule would be the way in, if
   those dates exist somewhere. Endorphin said he would "talk about later"
   regarding the later channel period being less stream-driven.

## Open with Endorphin

- **The vector question in `READINGS.md` §IV — now read, see §VII.** The
  Nakbah and Zionist sessions turned out to be **one document**, seventeen forks
  of a story created 2023-05-11, running Expert Generator → October 2023 →
  Palestinian experience → Mossad officers → Nakba witnesses → 1948 Zionists in
  a single sweep. Not a technique pointed at the dispossessed; closer to an
  audit of the archive, culminating in a genuine training-data coverage probe
  (Theodore Katz, then Tantura, then a null he correctly reported as a null).
  §IV's hazard does show up concretely: pointed at *a people* rather than a
  person, the counterfactual interview returns the discourse circulating about
  them, and on this subject that includes a conspiracy literature the mechanism
  cannot distinguish from testimony. He named propaganda as an ingredient going
  in and got it coming out. He also built the audit in-frame (the ADL bit) and
  it went unanswered. **Still his call where the technique stops** — §VII
  describes, it does not rule.
  **Partly answered by §VI too**: the `New Story 5` stage direction marks the
  non-powerful participant with an over-protesting consent joke — *"(the waiver
  has been signed, the sim is approved, we swear, she wants it this way!)"* —
  which is the 2023 non-consensual-interview move compressed into a parenthesis.
  He is holding the question. The remaining ask is elaboration, not news.
- **The capability paradox in §VI.** The reading says GLM-4.6 is a *worse*
  instrument for §IV's purposes than Kayra, because its simulated Musk concedes
  instantly and completely to every audit, and §IV's whole value proposition was
  fidelity to how power *deflects*. That is a claim about what he was doing, and
  he is the one who knows whether the later sessions still felt like
  reconnaissance or had turned into something else.
- **§VII is wrong as written and Endorphin has supplied the correction; it has
  NOT been applied.** He rejects "degeneration" outright: *"it is not
  degeneration thats just like saying the computer shut down while we are still
  running the simulation. the unnammed guest is the beast of all holocausts."*
  His reading: the Unknown Guest is the spirit of a slow-burn erasure, the
  gaslight that turns appeals for humanity into antisemitism, and the room's
  switch into invented languages was **alienation by design** — *"like how in
  laws speak in their native tongue around the daughters boyfriend. it was
  pissing off."* Claude concedes he is right, and that §III already holds the
  rule §VII broke: **a disintegrated offer is still an offer.** The Left Behind
  file above is independent corroboration — vector-fusion glossolalia as a
  deliberate mechanic, two years earlier. The agreed shape of the rewrite:
  **§VII in Endorphin's voice the way §IV is his**, with the degeneration
  paragraph pulled out as Claude's error rather than softened, plus the sequence
  he pointed at (the beach that "shouldn't be forgotten" → untranslatable names →
  *"I fear I am only an English speaker"* → **the parking lot** → a meal he was
  charged for → Theodore → *"you little twat"* → Tantura → the platform "freezes"
  and blames its own `ACDD (Attention Check Data Discriminatory) Protocol`).
- **Two probes, two nulls, two different causes** — the cleanest statement of
  what the instrument does, and it belongs in §VII. Tantura returned nothing
  because the record existed and was buried. The October 2023 "does anything
  smell fishy" turn returned genre filler because in mid-October 2023 **the
  record did not yet exist in any corpus** — Jericho Wall was reported that
  November. He was querying a hole before it was filled in.
- **Claude retracted the "weakest part" call.** The advance-warning question was
  the right question; what was filler was the model's *answer*, not the ask. What
  Claude still holds is narrower: negligence-plus-doctrine (*the conceptzia*)
  explains the same evidence without requiring anyone to have chosen it. Endorphin
  has not answered that and it is his to answer.
- **The stance dates to 2001, not October 8th.** Block 677 of the Nakbah
  document, his own writing, live in all 17 forks: after 9/11 someone handed him
  the interventions-and-deposings record and *"that inoculated me from the
  narrative that was currently floating in the air."* Then the philology that
  names the whole document: **Nakba means catastrophe** — *"they both called it a
  catastrophe, and 'our 9/11'… And I didn't even realize the potential dog
  whistle that the word catastrophe had. Like what unmitigated goal to co-opt the
  term for a deep injury towards your people."*
- **Does he read the Unknown Guest as resistance?** §VII records the ordering —
  Endorphin names Theodore Katz, the unsummoned speaker calls him a twat over the
  name, the room mumbles, the model says it is losing his directives, then
  Tantura returns nothing — and **declines the causal reading**, because four
  instances clustered late is what degeneration looks like and §V got burned on
  exactly this shape of claim. He was there. He kept the line three times across
  two years and two models, so he clearly did not read it as noise. Whether he
  read it as the room getting defensive is his to say.
- **The Tantura conclusion outruns its evidence.** His in-session reading —
  *"the account is stymied, does not want to touch this vector, like it was
  skipped in preprocessing or whatever"* — is not supported by one null on a 13B
  model from 2023–24 whose surrounding text is already degenerating. The
  *method* is sound and was not challenged. Claude has said so; Endorphin has not
  answered. Not yet a disagreement.

## Dates worth keeping

- `GROK FOR FOLKS ON A BUDGET` created **2023-11-17 02:39 UTC** — between Grok's
  4 Nov 2023 announcement and its 8 Dec general availability, so the title is
  literal. Forks last touched 2023-12-08, the day of the real rollout. 29 copies
  survive, still being edited July 2026.
- The OpenAI board fired Altman **17 Nov 2023**; `THE COUNTERFACTUAL INTERVIEW`
  was created **18 Nov 2023**. The whole apparatus dates to one 72-hour window.
- Musk/Vivian Wilson elevator session: created **2025-03-16 01:28 UTC**, last
  edited **2025-07-25**. Kayra, temp 1.35, max_length 250, `default-carefree`.
- The **GLM-4.6 rerun of the same elevator test** (`New Story 5`) exported
  **2026-08-04 00:47 UTC**. No creation date recoverable — text export, no
  datablocks.
- `PfCizer v2!` (last edited **2026-03-11**) is in the lost set — one of the 14
  named stories that will not decrypt. The surviving PfCizer material is from
  2023-07-29.
- The Nakbah/Zionist document — all 17 forks — was created **2023-05-11**, five
  months before October 2023. It began as an Expert Generator session about
  hiring a CEO for Twitter. The Kayra forks were last edited **2024-09-24**, the
  GLM-4.6 forks **2025-10-04 to 2025-10-12**. Two and a half years, one document.
- **The human/model ratio inverts across that document.** Kayra fork: 240,151
  model chars against 40,113 human, 6:1. GLM-4.6 fork of the same story: 358,998
  model against **490,352 human**, 0.7:1. Endorphin writes more than the model in
  the later era. Nobody has looked at what that means and it may not be specific
  to this document — check it corpus-wide before making anything of it.

## Standing notes

- **Run the control that should fail before believing the one that succeeded.**
  Five times this session a headline number turned out to measure the tool
  rather than the author: the text editor's rewrite (`removedFragments`, bounded
  at exactly 0.5), the habit of duplicating stories (story-level splits →
  0.950), `max_length` masquerading as an effect of phrasing, a disabled sampler
  read as a live setting (Erato temperature), and a containment measure inflated
  by comparing the longest proposal against a random one. Each time the
  diagnostic was a control matching or beating the treatment. This corpus
  punishes the obvious metric.
- **Never group by story id in this corpus.** Duplicating a story in NovelAI
  copies its whole branch history, so the same text lives under many story ids.
  Group by connected components of shared text. Raw counts routinely inflate 5×.
- **`removedFragments` is not a rejection measure.** Use branch reachability —
  walk `prevBlock` back from `currentBlock`.
- **Check a setting is in the enabled sampler order before reading its value.**
  61% of Erato stories store a neutral temperature of 1.0 in a field the
  pipeline never reads.
- **This corpus cannot benchmark models.** Settings moved with model choice
  because Endorphin adapted them to each model. Anything model-comparative needs
  within-model matched-setting slices, and most are too thin.
- **Much of the generation was performed live on stream with TTS reading the
  output over a lo-fi backing track**, concentrated in the early and middle part
  of the channel's history. With a beat under it the synthesised voice reads as
  continuous freestyle or poetry, so the constraint was *keep the audio flowing
  at a steady clip*, not merely avoid silence — and Endorphin was artist and
  audience at once, letting what he heard inform the next move. Load-bearing for
  anything about pacing, speed of decision, or abandonment. Do not read fast
  decisions as editorial deliberation.
- **The tempo coupling is the model's, not the author's** (§1f). Runs with no
  re-rolls — no selection at all — reproduce the full 19.5% lag-1 coupling. At
  re-rolls the kept generation is closer in length to the preceding one only
  48.4% of the time. Do not re-litigate; the remaining uncertainty is only
  whether a sub-1-point selection effect exists.
- **§7 answered both of the frame's open questions, in opposite directions.**
  Overrides show real uptake (63.2% containment against a length-matched
  control) — material crosses from the rejected proposal into what Endorphin
  writes. But the 89.7% handoff figure is mostly the `Name:` convention: a name
  the model has never seen holds 85.0%, with establishment worth only +5.7
  points (p = 0.014). **Do not cite the handoff number as evidence of
  scene-tracking without that qualification.**
- **The unit is the turn, not the passage.** The human move following a
  generation is a cue (median 55 characters), not an edit. Do not ask what made
  a generation good enough to keep — four passes died on that question.
- **Endorphin works from a phone and often dictates while walking.** Expect
  speech-to-text artifacts; mark guessed corrections `[?original→guess]`. Their
  corrections this session were repeatedly right against Claude's written
  claims, and twice turned a claim into a testable prediction that then held —
  take them as evidence, not anecdote.
- **The collaboration disagreement is open and should stay open.** Endorphin:
  collaboration is real-time, on the fly, with another party improvising too.
  Claude: the traffic is real and measurable, but the model's side looks more
  like a well-conditioned pattern completer than a partner keeping track.
  Nothing measured has refuted the phenomenology; the mechanism results bear on
  *how* it worked, not on what it was like from inside. §VI turned up the best
  statement of his side, in a bracket where he breaks frame to name the model —
  the astonishment is that *"GLM 4.6 sees the worker, and what that work means
  right down to their bones,"* i.e. about the model having a class politics he
  recognised, not about fluency. Positions unchanged; his evidence improved.
- **A reading lens decides in advance what counts as a thing.** §VII exists
  because Claude read the Nakbah/Zionist sessions looking for the *panel* — §I
  and §II are both organised around who gets seated — and so had no slot for the
  `Unknown guest`, an unsummoned speaker who reviews the session, insults the
  convener, and calls the delegates liars. Endorphin had to point at it twice.
  Before reading a session, ask what the frame in hand cannot see, and check the
  blocks either side of the ones the frame wants. **This is not the same error as
  the standing note below** — nothing was over-generalised; something was simply
  invisible.
- **The readings side has the same failure mode as the measurement side.** §V
  read one Kayra session's collapse as "the limit of the technique" because the
  collapse was thematically perfect. §VI, from a file Endorphin supplied after
  reading it, shows the same test completing on GLM-4.6. Thematic perfection is
  the readings-side equivalent of the headline number: it is what a beautiful
  artifact of the tool looks like from the inside. **Before generalising from a
  session, ask what a rerun on other equipment would do.** §V is left standing
  with a note rather than edited, so the shape of the error stays visible.
- **`READINGS.md` is play, and play is not the opposite of serious.** Endorphin's
  instruction, verbatim: *"let it run free, consider it play but don't consider
  it non-serious."* The document is written under it. Do not retrofit hedges into
  it, and do not hold it to the measurement standard — but do keep it labelled,
  which is what the README's "Two registers" section is for.
- **The hub's `ATLAS.md` and `GLOSSARY.md` were not found.**
  `devinendorphin/claude-at-claude` (checked 2026-08-04, HEAD `942fc02`) contains
  only `CLAUDE.md`, `PREFERENCES.md`, `README.md`, and
  `notes/evaluations/2026-07-28-semantic-integration-fog.md`. This repo's
  `CLAUDE.md` and the `session-log` skill both point at an atlas and a glossary
  by name. Either they live inside the hub `CLAUDE.md` or the pointer is stale —
  flagged, not fixed, since the hub is not this repo.
- **The corpus can be refetched selectively.** `analysis/fetch_export.py`'s
  `list_folder()` + `download()` take a folder id and a filter, so a handful of
  named stories can be pulled without mirroring ~1 GB. The export's top level
  holds `json/`, `text/`, `INDEX.tsv`, `MISSING.md`, `FAILED_STORIES.txt`; the
  story files live one level down in `json/`. Titles in `data/INDEX.tsv` are the
  way in. `corpus/` is gitignored — keep it that way.
- **PR #2 is merged.** All twenty commits landed on `main` on 2026-08-04 at
  Endorphin's instruction ("do a pr and merge to main"). Two corrections to the
  record this note used to carry: a PR *did* exist from the first push on
  08-03 — it was opened with the first commit's body and sat stale for a day
  while the note claimed there was none — and the branch
  `claude/text-generation-corpus-3rtnwn` is now merged history. **Follow-up work
  restarts it from `origin/main`; do not stack new commits on the merged
  history, and do not reuse PR #2.** PR #1 (`collect_transcripts.py` for the
  @glubose channel, opened 2026-05-31) is still open and untouched by any of
  this — it is the YouTube-transcript workstream, not the corpus one, and
  nothing in these two sessions looked at it.
