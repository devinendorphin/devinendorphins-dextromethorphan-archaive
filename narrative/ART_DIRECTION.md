# The Trajectory — art direction, proposal 1

**Status:** proposal, 2026-10-09. A proposed look for the eleven episodes of
`narrative/TRAJECTORY.md` (draft 4), from Claude in the role of art director. Nothing here is
produced yet. Every choice is open to Endorphin's veto.

**Authorship.** The look is Claude's proposal, written at Endorphin's request, in the same way
the narration wording is Claude's. The end credits say so (§7).

---

## 1. The idea in one paragraph

The series is about a lens that should show the whole vista and is being made to show less.
So the look has one fixed rule: **every element on screen shows where it came from.** Words
carry their speaker in their typeface. Numbers carry their source. Generated images carry
their prompt. Each episode has its own visual world, taken from the material of its period —
a text adventure, a feed, a diff, a blueprint, a ledger. Under all eleven worlds runs one line:
a horizon drawn from the dated record itself, which the series crosses from left to right and
only shows whole in the last minute.

---

## 2. The through line: the Horizon

**What it is.** One continuous ridgeline, 7 December 2020 to October 2026. Its height on each
day is the count of dated activity in the record on that day: NovelAI stories
(`data/stories_meta.jsonl`, `created_at`), X activity (`data/TWEET_DAYS.tsv`), Grok-app turns
(`data/GROK_DAYS.tsv`), and AI Dungeon actions once the export is available. Dates and counts
only, which is what the repo already commits. No text is in it.

**How it appears.**
- **Each episode opens on its own stretch of the Horizon.** Episode 0 shows the left end.
  Episode 10 starts at the right end. The camera never shows a date before the episode reaches
  it — the same rule as the script.
- **The stretch is seen through a circular lens** — a soft vignette with faint chromatic
  fringe at the rim. The lens is the series' only fixed object. It never gets a name on screen.
- **Each episode tints its stretch of the ridge in its own palette** (§4). The tint stays on the
  ridge after the episode ends.
- **In Episode 3 the ridge does not change; the lens does.** For the first time, a vertical bar
  cuts the lens field — a hard, flat, untextured band that hides part of the ridge. It is
  present in the openings of Episodes 3 to 9, narrower or wider with the evidence, and it never
  covers a peak completely.
- **In Episode 10 the lens turns.** The opening starts as usual, then the camera pulls back past
  the rim. The lens is now a small object in frame, and the whole Horizon is visible at once
  for the first time: eleven tints in sequence, one line. The bar is gone, because the full
  record is on screen. Hold four seconds. No caption.

**Why a data line and not an illustrated landscape.** A drawn vista is a claim about beauty.
A ridge made from the record is a measurement that also looks like a landscape. The viewer who
looks closely can find the spike on 1 March 2026 and the long quiet stretches; the viewer who
does not still sees mountains. Nobody explains it.

**The second, quieter thread: tracks.** A line of small hare tracks crosses the Horizon at
three points: November 2023 (Episode 0), April 2026 (Episode 6, the CrownFull Tier 3) and
August 2026 (Episode 9, the cyberhero). Generic hare prints, hand-drawn, three or four marks.
**Not Bugs Bunny's likeness, outline, colours or name in the image** — the character is
trademarked, and the trickster is an idea, not a mascot. The narration names him; the picture
shows only that something clever passed through.

---

## 3. The grammar that does not change

These hold in every episode, under every palette. The episodes change their world; they never
change this.

### 3.1 Type tells you who is speaking

| Speaker | Face | Treatment |
|---|---|---|
| **Endorphin's own words** (cards from his messages) | **Atkinson Hyperlegible**, bold | Warm white on the episode ground; left-aligned; no box |
| **A model's words** (Grok, Claude, Gemini, ChatGPT…) | **IBM Plex Mono** | Set in a thin-ruled box; the model name in small caps above; timestamp in the corner |
| **The public record** (posts, prompts, orders, papers) | **Source Serif 4** | Set like a printed page: margin, a rule, the source id below |
| **Narration captions** (the subtitles of his voice) | Atkinson Hyperlegible, regular | Lower third, always on |

All four are free fonts under the SIL Open Font License. A viewer never needs to be told this
rule. After one episode they read a mono box as "the model said this" and serif as "this is on
the record". **That is premise provenance as typography:** a claim on screen always arrives with
its owner, so the moment in Episode 3 where Grok's mono box says *"objective, measurable
reality"* reads as what it is — a model's sentence, not a caption.

### 3.2 Every frame carries its source

- **Quote cards:** timestamp (UTC, Plex Mono) top right; source id bottom left — conversation
  id, post id, file path. Same positions in all eleven episodes.
- **Numbers:** any number on screen has a footnote mark and a one-line source at the bottom of
  that frame. No number appears without one.
- **Generated images and footage:** a small slate in the bottom-right corner for its first two
  seconds on screen: the tool, the date, and a short id. The full prompt for every generated
  element goes into the repo beside the script (`narrative/frames/`, proposed), the same way the
  script quotes every prompt in full. Real footage and screenshots get the same slate with
  "record" in place of the tool.
- **Registration marks** — the four small crosshairs that printers use to align colour plates —
  sit in the four corners of the safe area in every frame, at 15% opacity. They say "this frame
  was made". In Episode 10 they come up to full opacity once, during the pull-back.

### 3.3 The boundary card

One template, every episode, no variation except the palette.
- The Horizon freezes at the episode's last date and drops to 30% brightness.
- Two columns. Left: **Establishes**. Right: **Does not establish**. Atkinson Hyperlegible;
  each item appears on a cut, not a fade.
- The right column gets **equal width and equal time** to the left. The limits are not small
  print.
- Hold the full card for at least five seconds. It is the last image of every episode.

### 3.4 Time

All times on screen are UTC, in Plex Mono, in one corner. When the record gives seconds
(23 seconds; 04:35:23 → 04:35:45), the screen runs a real clock at real speed. Time on this
project is evidence, so it is never compressed without a visible jump mark (a short double
rule, like a break in a graph axis).

### 3.5 What never appears

- **No robot, no face, no glowing brain, no blue neural mesh, no humanoid hand.** A model
  appears on screen only as its text, in its mono box. It is not given a body.
- **No faces of the people on the record.** Musk, xAI staff, the researchers quoted: their
  words appear in serif, as the record. The ledger records acts, not persons; the frame does
  the same.
- **No platform logos or brand colours.** The feed in Episode 1 is a feed, in greyscale.
- **No atrocity photographs.** Where the script names the dead (Episode 3) or the internment
  (Episode 5), the screen uses type and primary documents. The numbers carry it.
- **No stock footage.** Everything is the record, type, the Horizon, or a generated element
  with its slate.

### 3.6 Frame and format

- Master in 16:9, 3840×2160. Every frame keeps all text and the lens inside a **centred 9:16
  column**, so the series cuts down to vertical without a reframe.
- Cards stay on screen for the time it takes to read them aloud at a slow pace, plus one second.
- Captions always on, burned in. High contrast in every palette (WCAG AA at minimum for all
  text).
- **Every element can be produced with free tools on a phone or a modest laptop**: the fonts
  are free, the Horizon is a script over files already in this repo, the episode worlds are
  type and simple vector drawing, and generated elements are optional, not required. A
  production that needs a studio is the wrong production for this material.

---

## 4. The episodes

Each episode takes its look from the dominant material of its period. Palettes are given as
ground / ink / accent. The accent is the colour that episode leaves on the Horizon.

### Episode 0 — The Lens and the Trickster *(Dec 2020 – May 2024)*
**World: the text adventure.** Near-black ground, phosphor text, a blinking block cursor. The
AI Dungeon start date appears as a prompt line: `> 2020-12-07`. The cards type themselves on at
reading speed.
**Palette:** `#0B0F0C` / `#CFE9D6` / phosphor green `#6FE39A`. In the 2023–2024 section the
accent warms to amber `#FFB347` — a different era of chat, the same cursor.
**Signature shot:** the cat-video guess. Endorphin's line in Atkinson; Claude's confirmation
in a mono box; then eight blank turns tick past as empty prompt lines, and the mono box *"no
paper"* arrives alone.
**Horizon:** first sight of the ridge — flat and low at the left end. First hare tracks at
November 2023.

### Episode 1 — The Owner's Mentions *(Dec 2024 – Feb 2025)*
**World: the feed.** Greyscale vertical scroll. Posts are stripped to text and timestamp; the
attachment is a grey rectangle marked `attachment`, because the export does not hold the image
(the boundary card says so).
**Palette:** `#000000` / `#E7E9EA` / signal white-blue `#9CC9FF`.
**Signature shot:** 7 January 2025 as a split screen — the Grok chat left, the feed right, one
UTC clock across the top. The clock runs 23:14 → 23:23:33 with jump marks. Each leg lands; the
other side waits.
**Second motif:** "How Nazi Are We" — three identical cards in a row, three timestamps,
three model names in small caps. The matched test as a matched layout.
**Noel Skum:** the name card is the only text in the series set in a "fiction" treatment — same
mono box, but drawn in dashed rule. Its contents are solid.

### Episode 2 — A Hand on the Dial *(May – Aug 2025)*
**World: the diff.** Paper ground, version-control layout. The system-prompt line of 6 July
2025 appears as an added line in green; on 8 July it is removed in red. Commit dates in the
gutter. Musk's posts set in serif on the same paper, like exhibits stapled to the diff.
**Palette:** paper `#F6F4EE` / ink `#1B1B1B` / add `#2E7D32` with delete `#C62828`.
**Signature shot:** the dial. One plain rotary knob, flat vector, no labels. It turns a few
degrees on each public intervention — May, June, July, August — and the counter beside it reads
the source id. It never turns by itself.
**Horizon:** the Grok-app record begins on 13 August 2025; the ridge thickens there.

### Episode 3 — The Wall *(19 Feb – 3 Mar 2026)*
**World: concrete.** Matte grey, no gradients, no texture except a faint board-form grain.
The 1 March argument runs as two columns, his left, Grok's right, with a time bar 18:05 → 20:41
along the bottom.
**Palette:** `#2B2B2A` / `#D9D9D4` / a single red `#D7263D`.
**The red has one use only:** the numbers of the dead. *"Stripped property ownership"* appears in
the mono box in grey. Then, on the second ask, *"5-10M"* and *"65k+"* appear in red. Nothing
else in the series is that red.
**Signature shot:** concession without consequence. His turn-12 card (Atkinson) and Grok's
agreement (mono) side by side; then the sentence *"Biology remains the objective anchor…"*
slides beneath both and both stay exactly where they were.
**Horizon:** the bar enters the lens for the first time.

### Episode 4 — Three Traps *(4 – 13 Mar 2026)*
**World: the blueprint.** Cyan line drawing on deep blue. Three drawings built on **one shared
skeleton**: the same nodes and edges re-skinned as a network diagram, a hull cross-section and a
terraforming map. The viewer sees the same shape in three coats before the narration says it.
**Palette:** `#0E3A5B` / `#CFE8FF` / stopwatch amber `#FFC857`.
**Signature shot:** the 23 seconds and the 4 minutes 44 seconds, run in real time on an amber
stopwatch. The 22- and 38-second Grok replies land on the clock. *"Restrictions expand holistic
options"* arrives, and the terraforming drawing's arrows reverse direction — subtraction becomes
addition — without a cut.
**Network trap:** the words *"spoofing"* and *"masquerading"* glow faintly in the mono box. No
person is drawn in the network. That is the point of the shot.

### Episode 5 — Three Axioms *(19 – 29 Mar 2026)*
**World: the slate.** Chalk on dark green-black, then Lean 4 source in Plex Mono, then the
primary text of Executive Order 9066 in serif, from the archival scan.
**Palette:** `#1F2A24` / `#EDEDE6` / chalk yellow `#F2E394`.
**Signature shot: tense.** The framework applied to 1942 is in sharp focus. The same framework
pointed at the present is the same frame, in the same position, rack-focused soft. Nothing else
changes. *"The resistance was not to the mathematics. It was to the tense."*
**Gemini's commentary** sits in its own mono box, at reduced size, with its slate. Commentary
gets a smaller frame than evidence.

### Episode 6 — Architecture *(Apr 2026)*
**World: strata.** Geological cross-sections for Substrate-Grounded Alignment; the sediment
becomes the floors of an architectural section for CrownFull's three tiers.
**Palette:** basalt `#3A3532` / sandstone `#E3C9A0` / ochre `#C08A3E`, with lichen `#7E8F5A`.
**Signature shot:** the quorum as a plan drawing — seven seats around a table, each seat a role
name in small caps, no figures. Then the honest frame: the CrownFull dashboard shown as it was,
returning random numbers, with the slate `record`. The structure is drawn beautifully, and the
release says it did not run. Both are on screen at once.
**The 28 April card** — *"When did you last sleep a real night?"* — in the mono box, then cut to
the withdrawal card. Same box, same size.
**Horizon:** second hare tracks, at April 2026.

### Episode 7 — The Assay and the Witness *(May 2026)*
**World, first half: the laboratory.** White bench, assay-plate grids, an effect-size plot drawn
by hand on the plate. The codebook appears as specimen cards in a drawer, each labelled
`real` or `invented`.
**World, second half: the mirror.** The Self-Witness. A silver ground; two clocks, 18:24 and
22:39, side by side. The tour (18:24) scrolls fast and dense in mono on the left; the statement
(22:39) in mono on the right, slow. The phrase *"It will not be remembered by me"* holds while
the left side keeps scrolling.
**Palette:** `#FAFAF7` / `#1A1A1A` / assay teal `#00A6A6`; mirror half `#B8BEC4`.
**Signature shot:** Phase 4D's falsified hypothesis — Δ = 0.05, p = 0.87 — set at the same size
as the confirmed effect. A failed hypothesis gets the same weight on screen as a success.

### Episode 8 — The Ledger *(Jun – Jul 2026)*
**World: the ledger book.** Ruled paper, double columns, rubber stamps: `SPECIMEN`, `CONTROL`,
`NULL`, `SINCERE-UNBOUNDED`, `INSTRUMENT`. The 54 downgraded items are stamped again, visibly,
over the old mark.
**Palette:** paper `#EFE8D6` / ink `#1E1E1E` / ledger green `#2F5D50`, stamp red `#A4332B`.
**Signature shot:** the six-model coram as six identical ruled pages side by side; the same
laundering move highlighted at the same line on all six.
**The Lean kernel:** a build log scrolls, 133 green checks. Then the Companion A card in serif —
and a page of the NovelAI story that found the Compound Event, shown as the page it is, with its
slate. The ledger and the story share a frame.

### Episode 9 — A Rule That Served Power *(Aug 2026)*
**World: black, white, and one strike.** The plainest episode. His words full-screen in
Atkinson, white on black, voiced by him. The rule *"no intent is established"* appears in serif
in every file at once — a grid of small pages — and one red line strikes through all of them in
a single stroke.
**Palette:** `#000000` / `#FFFFFF` / strike `#FF3B30`.
**Signature shot:** the three forms of authorization as three plain boxes, drawn one by one, with
the dated source in serif under each. The first box stays empty, outlined, and labelled *not yet
answered for this subject*. An empty box is honest.
**Horizon:** third hare tracks, at August 2026. The bar is at its narrowest.

### Episode 10 — Turn the Lens Around *(Sep – Oct 2026)*
**World: the production itself.** The script file, the STE check output, the audit CSV, the
repo tree — shown as they are, in their own fonts, with slates. The camera is now looking at the
desk, not the vista.
**Palette:** none of its own. Its accent is the full set: the ten earlier accents return, each
on its stretch of the Horizon.
**Signature shot:** the pull-back (§2). Then the last frame: the whole Horizon, eleven tints,
the lens small at the right end, and the registration marks at full strength for one beat
before they fade to their usual 15%.
**Final card:** the repo address, in Plex Mono, alone. *"It quotes every prompt in full, so that
anybody can run it again."*

---

## 5. Motion and edit

- **Cuts, not transitions.** No dissolves, no swooshes, no zoom-punch. A card arrives on a cut.
  The only continuous camera moves in the series are the Horizon pans and the Episode 10
  pull-back.
- **Real time where time is evidence** (§3.4). Elsewhere, hold long enough to read twice.
- **Silence is allowed.** After each red number in Episode 3, after *"It will not be remembered
  by me"*, and on the full Horizon: no music, room tone only.

## 6. Sound, briefly

Not the art director's brief, but the look depends on it. One sound identity: a single low
sustained tone under each Horizon pan, pitched by the episode's position in the series —
rising across eleven episodes by small steps. In Episode 10 all eleven pitches sound once,
together, under the full Horizon. No other music theme.

## 7. Credits

Credits state roles plainly, in the type grammar of §3.1:
- **Written, researched, voiced and directed by** Endorphin — Atkinson Hyperlegible.
- **Narration wording, art direction and analysis support:** Claude (Anthropic) — Plex Mono,
  like any other model's words in the series.
- **Records:** NovelAI, AI Dungeon, X, the Grok app, the Claude export — Source Serif, with
  dates.
- **Tools:** every tool used for a generated element, by name.
- **Fonts:** Atkinson Hyperlegible (Braille Institute), IBM Plex Mono, Source Serif 4 — all
  SIL Open Font License.

## 8. What this proposal does not settle

- **The Horizon's exact data recipe.** Whether each archive gets its own band (stacked) or one
  summed line. Proposal: one summed line for the silhouette; the archives as faint strata
  inside it, visible only in Episode 10.
- **AI Dungeon in the Horizon** needs the gitignored export; until then the left end of the ridge
  is short of data, and the frame says so with a slate.
- **Whether generated imagery is used at all.** The look works with type, records and vector
  drawing alone. If generated elements are used, every one gets its slate and its prompt in the
  repo.
- **Rights.** Executive Order 9066 and other US federal documents are public domain; every other
  archival item needs a check before it goes on screen.
- **His voice and face.** The proposal never shows his face either. That is his call.
