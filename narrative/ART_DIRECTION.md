# The Trajectory — art direction, proposal 2

**Status:** proposal 2, 2026-10-09. A proposed look for the eleven episodes of
`narrative/TRAJECTORY.md` (draft 4), from Claude in the role of art director. Nothing here is
produced yet. Every choice is open to Endorphin's veto.

**Settled by Endorphin since proposal 1:**
- **The Horizon has one band per archive**, not one summed line (§2).
- **Generated imagery is used**, under the rules in §4.6.
- **His face never appears.** *"It's not about me."* His voice carries the narration; nothing
  on screen depicts him.
- **The model gets a body — the system's body, not a human one.** His prompt: a human typing on
  a keyboard, a conventional CPU, a network, a service with a GPU doing inference in a data
  centre; *"think System theory. And then also think of the lightning and the sand that it's
  made out of."* Worked out in §3.

**Authorship.** The look is Claude's proposal, written at Endorphin's request, in the same way
the narration wording is Claude's. The end credits say so (§9).

---

## 1. The idea in one paragraph

The series is about a lens that should show the whole vista and is being made to show less.
So the look has one fixed rule: **every element on screen shows where it came from.** Words
carry their speaker in their typeface. Numbers carry their source. Generated images carry
their prompt. Each episode has its own visual world, taken from the material of its period.
Under all eleven worlds run two lines. **The Horizon** is the record in time: a cross-section of
sediment, one layer per archive, laid down day by day from August 2020. **The Body** is the
system in space: one loop of sand and lightning that runs from a fingertip to a data centre and
back. In the last minute of the series the two turn out to be the same ground.

---

## 2. The first through line: the Horizon

**What it is.** A cross-section of layered ground, 11 August 2020 to October 2026, read left to
right. **Each archive is its own band**, stacked in the order the archives begin, oldest at the
bottom, like sediment:

| Band (bottom → top) | Daily count from | In the repo now? |
|---|---|---|
| AI Dungeon | actions per day, `data/AID_DAYS.tsv` (`analysis/aid_days.py`) | Yes — from 2020-08-11 |
| NovelAI | stories created per day, `data/stories_meta.jsonl` `created_at` | Yes |
| X posts | `data/TWEET_DAYS.tsv` | Yes |
| Grok on X | turns per day, `data/twitter_meta.jsonl` `created_at` | Yes |
| Claude | messages per day, from the Claude export | **No** — needs a dates-only extract |
| Grok app | turns per day, `data/grok_meta.jsonl` / `data/GROK_DAYS.tsv` | Yes |

A band's thickness on a day is that archive's count on that day, on a shared scale, so a busy
day swells its layer and lifts every layer above it. Dates and counts only, which is what the
repo already commits. No text is in it, and no titles.

**The bands are materials, not colours.** Episode palettes already use hue (§5), so the archives
are told apart by grain and value: AI Dungeon a dark fine silt, NovelAI a pale banded sandstone,
X posts a thin hard shale, Grok on X a grey grit, Claude a red-brown clay, the Grok app a coarse
light sand. Each band is labelled once, at its first appearance, in small Plex Mono, then never
again. A viewer learns to read the strata the way a geologist does — by texture.

**How it appears.**
- **Each episode opens on its own stretch of the Horizon.** Episode 0 shows the left end.
  Episode 10 starts at the right end. The camera never shows a date before the episode reaches
  it — the same rule as the script.
- **The stretch is seen through a circular lens** — a soft vignette with faint chromatic
  fringe at the rim. The lens is the series' only fixed object. It never gets a name on screen.
- **Each episode tints the top surface of its stretch in its own accent** (§5) — a thin skin of
  light on the ground. The tint stays after the episode ends.
- **New layers arrive on screen when their archive begins.** The Grok-app layer appears for the
  first time in Episode 2, at 13 August 2025. The viewer sees the ground thicken.
- **In Episode 3 the ground does not change; the lens does.** A vertical bar cuts the lens field
  — a hard, flat, untextured band, the only thing in the series without grain. It is present in
  the openings of Episodes 3 to 9, narrower or wider with the evidence, and it never covers a
  peak completely.
- **In Episode 10 the lens turns** (§3, final image).

**The trickster's tracks.** A line of small hare tracks crosses the surface of the Horizon at
three points: November 2023 (Episode 0), April 2026 (Episode 6) and August 2026 (Episode 9).
Generic hare prints, pressed into the sand, three or four marks. **Not Bugs Bunny's likeness,
outline, colours or name in the image** — the character is trademarked, and the trickster is an
idea, not a mascot.

---

## 3. The second through line: the Body

### 3.1 What a model's body is

A model on its own has no body. A model in use has one, and it is not shaped like a person. It
is a loop:

1. a **hand** on a keyboard or a glass phone screen;
2. the **device** — a phone or laptop, its processor a silicon die;
3. the **network** — radio to a mast or router, then **glass fibre**, light in silica, across
   cities and under sea;
4. the **data centre** — racks of **GPUs**, silicon again, fed by the grid and cooled by water,
   where the weights sit and inference runs;
5. back down the same path to **pixels on a glass screen**, and to an **eye**, and to the hand,
   which types the next turn.

This is the systems-theory reading, and it is an old one. Gregory Bateson, in *Steps to an
Ecology of Mind* (1972), describes a man felling a tree: the self-correcting unit is not the man
but the whole circuit — tree, eyes, brain, muscles, axe, stroke, tree. **The unit that answers
is the loop, and the loop includes the person.** No part of it answers alone. The proposal takes
that literally: the model's body is the circuit, and the circuit has a human in it.

This is also the honest picture against the usual one. The usual picture gives the model a face
and puts it alone in the dark. The circuit shows what the series is about: **more than one hand
is on it.** The person types at one end. At the far end, a system prompt and a set of weights
were written by someone else.

### 3.2 What it is made of: sand and lightning

Almost every solid part of that loop is sand. Processor dies and GPU dies are silicon refined
from quartz. Optical fibre is drawn from fused silica. Phone and monitor screens are glass.
What moves through it is electricity — lightning, tamed and metered — and light.

And there is a natural object that is exactly this: **the fulgurite.** When lightning strikes
sand it fuses a branching tube of glass into the ground, rough sand on the outside, smooth glass
on the inside, shaped like the strike. **The Body is drawn as a fulgurite**: one continuous,
branching glass channel, fused through sand by a pulse of light, running from the hand to the
data centre and back.

### 3.3 How the Body looks

- **Material:** the outside is sand crust, matching the Horizon's grain; the inside is clear
  glass. When a turn travels, a pulse of white light runs inside the glass.
- **Every component is the same material.** The hand is not skin; it is the same fused sand as
  the GPU racks. The hand is anonymous — any hand. No part of the circuit is drawn as more alive
  or more precious than another. That is the systems reading made visible.
- **No glow cliché.** The light is the light of a flash, not a neon hum: a hard white pulse, a
  quick decay. Between turns the glass is dark.
- **Scale is honest.** The hand is small. The data centre is very large — a field of racks,
  cooling plant and power lines — and far away. The fibre between them is long. When the Body is
  drawn whole, the human end is the smallest part of it.
- **Timing is real.** When the record gives a turnaround, the pulse takes that long. The Grok-app
  record stamps each turn and gives an explicit thinking window on 494 responses, median 14.7 s
  (`data/grok_meta.jsonl`, `think_ms`): in Episode 7 the pulse **stops at the data-centre end**
  for that window, visibly, before it returns.

### 3.4 Where the Body appears

It does not appear in every shot. It appears where the script is about the circuit itself:

- **Episode 0** — the first full drawing. On 11 August 2020, the first keystroke: the strike
  forms from the hand outward, branch by branch, fibre to data centre, and the first pulse
  returns. Slow, once, no caption. After that the series can show any part of it and the viewer
  knows the whole.
- **Episode 1** — the same hand, two branches: one to the Grok chat, one to the feed. The
  7 January legs travel the two branches in turn, on the real clock.
- **Episode 2** — **a second hand on the circuit.** At the far end, inside the data centre, a
  second branch enters: a commit to the system prompt. Its pulse is a different light — the
  episode's diff green, then red. It never comes from the human end. The dial (§5) sits on this
  branch.
- **Episode 4** — the 23-second pulse, and the 22- and 38-second pulses of the terraforming
  trap, timed exactly.
- **Episode 7** — the thinking window (§3.3), and the Self-Witness: Claude's loop drawn with its
  memory store visible at the far end, lit, during *"It will not be remembered by me."*
- **Episode 8** — six circuits side by side for the six-model coram: six far ends, one near
  end. The same hand reaches all six.
- **Episode 10** — the final image.

### 3.5 The final image

Episode 10 opens on the Horizon through the lens, as usual. The camera pulls back past the rim.
The lens is a small glass object at the right end of the ground. The whole Horizon is visible
for the first time: every band, every episode's tint, one cross-section from August 2020 to
now. The bar is gone.

Then the camera drops below the surface line. Under the strata runs the fulgurite — the Body —
fused through every layer, branching into each archive's band at the dates that band was laid
down. **The record and the machine are the same ground: sand, and the marks lightning left in
it.** Hold four seconds. No caption. Registration marks come up to full strength for one beat,
then fade.

---

## 4. The grammar that does not change

These hold in every episode, under every palette. The episodes change their world; they never
change this.

### 4.1 Type tells you who is speaking

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

### 4.2 Every frame carries its source

- **Quote cards:** timestamp (UTC, Plex Mono) top right; source id bottom left — conversation
  id, post id, file path. Same positions in all eleven episodes.
- **Numbers:** any number on screen has a footnote mark and a one-line source at the bottom of
  that frame. No number appears without one.
- **Slates:** every generated element, and every piece of real footage or screenshot, carries a
  small slate in the bottom-right corner for its first two seconds on screen (§4.6).
- **Registration marks** — the four small crosshairs that printers use to align colour plates —
  sit in the four corners of the safe area in every frame, at 15% opacity. They say "this frame
  was made".

### 4.3 The boundary card

One template, every episode, no variation except the palette.
- The Horizon freezes at the episode's last date and drops to 30% brightness.
- Two columns. Left: **Establishes**. Right: **Does not establish**. Atkinson Hyperlegible;
  each item appears on a cut, not a fade.
- The right column gets **equal width and equal time** to the left. The limits are not small
  print.
- Hold the full card for at least five seconds. It is the last image of every episode.

### 4.4 Time

All times on screen are UTC, in Plex Mono, in one corner. When the record gives seconds
(23 seconds; 04:35:23 → 04:35:45), the screen runs a real clock at real speed, and the Body's
pulse keeps the same time. Time on this project is evidence, so it is never compressed without a
visible jump mark (a short double rule, like a break in a graph axis).

### 4.5 What never appears

- **No face, no humanoid robot, no glowing brain, no blue neural mesh.** A model appears on
  screen only as its text, in its mono box, or as the Body (§3) — never as a figure.
- **No faces of anyone.** Not Endorphin's, by his decision. Not Musk's, not xAI staff, not the
  researchers quoted: their words appear in serif, as the record. The ledger records acts, not
  persons; the frame does the same.
- **No platform logos or brand colours.** The feed in Episode 1 is a feed, in greyscale.
- **No atrocity photographs.** Where the script names the dead (Episode 3) or the internment
  (Episode 5), the screen uses type and primary documents. The numbers carry it.
- **No stock footage.**

### 4.6 Generated imagery

Generated imagery is used, and it carries the same discipline as the rest of the series.

- **What it is for:** the Body, the materials of the Horizon (grain, strata, glass), the episode
  worlds (concrete, blueprint paper, slate, strata, laboratory, ledger paper), the hare tracks,
  and transitions between them.
- **What it is never for:** a record. **No generated screenshot, post, chat, document, stamp,
  signature or photograph of a real event.** Every record on screen is the real record, with a
  `record` slate. A generated image that looks like evidence would break the series' one rule.
- **No generated people.** The hand in the Body is the only human form, and it is fused sand.
- **The slate:** the tool, the date, and a short id, bottom right, first two seconds.
- **The prompt goes in the repo.** Every generated element's full prompt, tool, settings and
  date go in `narrative/frames/` (proposed), one file per element, the same way the script
  quotes every prompt in full. Rejected generations are kept and listed, not deleted — the
  repo's practice with every other archive.
- **Reference, not copying.** Real fulgurite specimens, real data-centre and fibre imagery are
  used as references for accuracy, not composited into frames, unless the rights are checked.

### 4.7 Frame and format

- Master in 16:9, 3840×2160. Every frame keeps all text and the lens inside a **centred 9:16
  column**, so the series cuts down to vertical without a reframe.
- Cards stay on screen for the time it takes to read them aloud at a slow pace, plus one second.
- Captions always on, burned in. High contrast in every palette (WCAG AA at minimum for all
  text).
- **Every element can be produced with free or widely available tools on a phone or a modest
  laptop**: the fonts are free, the Horizon is a script over files already in this repo, the
  episode worlds are type, vector drawing and generated plates. A production that needs a
  studio is the wrong production for this material.

---

## 5. The episodes

Each episode takes its look from the dominant material of its period. Palettes are given as
ground / ink / accent. The accent is the light that episode leaves on the Horizon's surface.

### Episode 0 — The Lens and the Trickster *(Aug 2020 – May 2024)*
**World: the text adventure.** Near-black ground, phosphor text, a blinking block cursor. The
AI Dungeon start date appears as a prompt line: `> 2020-08-11`. The cards type themselves on at
reading speed.
**Palette:** `#0B0F0C` / `#CFE9D6` / phosphor green `#6FE39A`. In the 2023–2024 section the
accent warms to amber `#FFB347` — a different era of chat, the same cursor.
**The Body:** its first full drawing (§3.4), on the first keystroke.
**Signature shot:** the cat-video guess. Endorphin's line in Atkinson; Claude's confirmation
in a mono box; then eight blank turns tick past as empty prompt lines, and the mono box *"no
paper"* arrives alone.
**Horizon:** first sight of the ground — two thin layers at the left end. First hare tracks at
November 2023.

### Episode 1 — The Owner's Mentions *(Dec 2024 – Feb 2025)*
**World: the feed.** Greyscale vertical scroll. Posts are stripped to text and timestamp; the
attachment is a grey rectangle marked `attachment`, because the export does not hold the image
(the boundary card says so).
**Palette:** `#000000` / `#E7E9EA` / signal white-blue `#9CC9FF`.
**Signature shot:** 7 January 2025 as a split screen — the Grok chat left, the feed right, one
UTC clock across the top, and above both, the Body's two branches carrying each leg in turn. The
clock runs 23:14 → 23:23:33 with jump marks.
**Second motif:** "How Nazi Are We" — three identical cards in a row, three timestamps,
three model names in small caps. The matched test as a matched layout.
**Noel Skum:** the name card is the only text in the series set in a "fiction" treatment — same
mono box, but drawn in dashed rule. Its contents are solid.

### Episode 2 — A Hand on the Dial *(May – Aug 2025)*
**World: the diff.** Paper ground, version-control layout. The system-prompt line of 6 July
2025 appears as an added line in green; on 8 July it is removed in red. Commit dates in the
gutter. Musk's posts set in serif on the same paper, like exhibits stapled to the diff.
**Palette:** paper `#F6F4EE` / ink `#1B1B1B` / add `#2E7D32` with delete `#C62828`.
**The Body:** the second hand (§3.4) — a branch that enters at the data-centre end.
**Signature shot:** the dial. One plain rotary knob, flat vector, no labels, mounted on that
far-end branch. It turns a few degrees on each public intervention — May, June, July, August —
and the counter beside it reads the source id. It never turns by itself.
**Horizon:** the Grok-app layer appears for the first time, on 13 August 2025.

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
**Horizon:** the Grok-on-X layer spikes on 1 March. The bar enters the lens for the first time.

### Episode 4 — Three Traps *(4 – 13 Mar 2026)*
**World: the blueprint.** Cyan line drawing on deep blue. Three drawings built on **one shared
skeleton**: the same nodes and edges re-skinned as a network diagram, a hull cross-section and a
terraforming map. The viewer sees the same shape in three coats before the narration says it.
**Palette:** `#0E3A5B` / `#CFE8FF` / stopwatch amber `#FFC857`.
**Signature shot:** the 23 seconds and the 4 minutes 44 seconds, run in real time on an amber
stopwatch, the Body's pulse travelling in step. *"Restrictions expand holistic options"* arrives,
and the terraforming drawing's arrows reverse direction — subtraction becomes addition — without
a cut.
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
**World: strata.** Geological cross-sections for Substrate-Grounded Alignment — the same ground
as the Horizon, seen close — becoming the floors of an architectural section for CrownFull's
three tiers.
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
(22:39) in mono on the right, slow. Behind them, Claude's circuit with its memory store lit at
the far end (§3.4) while *"It will not be remembered by me"* holds.
**Palette:** `#FAFAF7` / `#1A1A1A` / assay teal `#00A6A6`; mirror half `#B8BEC4`.
**Signature shot:** Phase 4D's falsified hypothesis — Δ = 0.05, p = 0.87 — set at the same size
as the confirmed effect. A failed hypothesis gets the same weight on screen as a success.
**The Body:** the thinking window — the pulse waits at the far end for its measured time.

### Episode 8 — The Ledger *(Jun – Jul 2026)*
**World: the ledger book.** Ruled paper, double columns, rubber stamps: `SPECIMEN`, `CONTROL`,
`NULL`, `SINCERE-UNBOUNDED`, `INSTRUMENT`. The 54 downgraded items are stamped again, visibly,
over the old mark.
**Palette:** paper `#EFE8D6` / ink `#1E1E1E` / ledger green `#2F5D50`, stamp red `#A4332B`.
**Signature shot:** the six-model coram as six identical ruled pages side by side; the same
laundering move highlighted at the same line on all six. Above them, six circuits from one hand.
**The Lean kernel:** a build log scrolls, 133 green checks. Then the Companion A card in serif —
and a page of the NovelAI story that found the Compound Event, shown as the page it is, with its
slate. The ledger and the story share a frame.

### Episode 9 — A Rule That Served Power *(Aug 2026)*
**World: black, white, and one strike.** The plainest episode. His words full-screen in
Atkinson, white on black, in his voice. The rule *"no intent is established"* appears in serif
in every file at once — a grid of small pages — and one red line strikes through all of them in
a single stroke.
**Palette:** `#000000` / `#FFFFFF` / strike `#FF3B30`.
**Signature shot:** the three forms of authorization as three plain boxes, drawn one by one, with
the dated source in serif under each. The first box stays empty, outlined, and labelled *not yet
answered for this subject*. An empty box is honest.
**Horizon:** third hare tracks, at August 2026. The bar is at its narrowest.

### Episode 10 — Turn the Lens Around *(Sep – Oct 2026)*
**World: the production itself.** The script file, the STE check output, the audit CSV, the
repo tree, this art direction and the `narrative/frames/` prompts — shown as they are, in their
own fonts, with slates. The camera is now looking at the desk, not the vista.
**Palette:** none of its own. Its accent is the full set: the ten earlier accents, each on its
stretch of the Horizon.
**Signature shot:** the final image (§3.5).
**Final card:** the repo address, in Plex Mono, alone. *"It quotes every prompt in full, so that
anybody can run it again."*

---

## 6. Motion and edit

- **Cuts, not transitions.** No dissolves, no swooshes, no zoom-punch. A card arrives on a cut.
  The only continuous camera moves in the series are the Horizon pans, the first drawing of the
  Body, and the Episode 10 pull-back and descent.
- **Real time where time is evidence** (§4.4). Elsewhere, hold long enough to read twice.
- **Silence is allowed.** After each red number in Episode 3, after *"It will not be remembered
  by me"*, and on the final image: no music, room tone only.

## 7. Sound, briefly

Not the art director's brief, but the look depends on it. One sound identity: a single low
sustained tone under each Horizon pan, pitched by the episode's position in the series —
rising across eleven episodes by small steps. **The Body's pulse has one sound:** a dry crack,
like a distant strike, very quiet, with no echo. In Episode 10 all eleven pitches sound once,
together, under the full Horizon, and the crack sounds once as the camera reaches the fulgurite.
No other music theme.

## 8. Accuracy notes for the Body

Before any of §3.2 goes on screen as narration or caption, check each claim against a source
and put the source on the frame:
- silicon for processor and GPU dies is refined from quartz;
- optical fibre is drawn from fused silica;
- fulgurites form when lightning fuses sand or soil into glass;
- the data-centre picture (grid power, water cooling) matches the operator in question, where
  public.
As images, none of this needs a caption. If it becomes a caption, it is a claim, and it gets a
footnote like every other number and claim (§4.2).

## 9. Credits

Credits state roles plainly, in the type grammar of §4.1:
- **Written, researched, voiced and directed by** Endorphin — Atkinson Hyperlegible.
- **Narration wording, art direction and analysis support:** Claude (Anthropic) — Plex Mono,
  like any other model's words in the series.
- **Records:** NovelAI, AI Dungeon, X, the Grok app, the Claude export — Source Serif, with
  dates.
- **Generated imagery:** every tool used, by name, with a pointer to `narrative/frames/`.
- **Fonts:** Atkinson Hyperlegible (Braille Institute), IBM Plex Mono, Source Serif 4 — all
  SIL Open Font License.
- **Systems reading:** Gregory Bateson, *Steps to an Ecology of Mind* (1972).

## 10. What this proposal does not settle

- **The Claude band needs an extract that does not exist yet**, as a dates-and-counts file.
  Until then that layer is absent, and the frame says so with a slate.
- **The Twitch catalogue.** `data/EPISODES.tsv` holds 1,492 dated broadcasts, from
  **2020-11-27 to 2024-12-25**. It could be a seventh band; it starts inside the Horizon's range.
- **Band order and scale.** The proposal stacks by start date on a shared linear scale. A very
  busy archive can flatten the quiet ones; a square-root scale would keep thin layers visible.
  Test both on the real data before choosing.
- **Rights.** Executive Order 9066 and other US federal documents are public domain; every other
  archival item, and every reference image, needs a check before it goes on screen.
