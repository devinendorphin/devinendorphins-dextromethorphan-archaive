# FACEBOOK — first measurements

2026-08-13. Source and method: `analysis/FB_EXPORT.md`. Aggregates in
`data/fb_summary.json`. Nothing here is held to the `FINDINGS.md` measurement
standard yet; this is the first pass.

## Shape

| | |
|---|---:|
| posts | **5,018** (5,007 with text) |
| words in posts | **439,512** |
| span | **2008-03-12 .. 2024-10-18** |
| post revisions | 377, in 196 chains |
| comments | 1,385 (2008-09 .. 2024-10) |
| private message threads | 1,524 — *not analysed, see below* |
| Meta AI chat turns | 137 in 3 chats |

**The archive is sixteen years older than the corpus knew.** `CLAUDE.md` dates
the archive to 2020-12-07, the first AI Dungeon adventure, and calls that
"eighteen months before the first NovelAI story". The first Facebook post is
**2008-03-12**, twelve years and nine months earlier.

Posts per year, with words:

```
2008    82     990        2017    19     748
2009   189   2,847        2018    26   1,074
2010   196   4,822        2019   313  20,441   ####
2011   100   2,270        2020   524  59,580   ############
2012   120   1,056        2021   943  87,609   ##################
2013    65     837        2022  1110  77,284   ###############
2014    53   1,458        2023   756 108,299   ######################
2015    49   1,453        2024   414  67,580   #############
2016    48   1,164
```

Two regimes, not one. 2008–2018 is eleven years of short status updates
averaging 20 words and never exceeding 5,000 words a year. From 2019 the volume
goes up by an order of magnitude and the median post length goes from ~12 words
to 35–54. **The break is 2019, a year before first contact with AI Dungeon** —
so the shift to long-form is not caused by the generation practice, though it
immediately precedes it.

**Answered, 2026-08-13** — see `notes/riffs/2026-08-13-the-2019-break.md`. The
flat eleven years were deliberate: radio silence held for security,
community-safety and conflict-of-interest reasons while running a growing event.
2016 brought an accountability process "akin to MeToo, about a year in advance";
2017–2019, a crash course in coercive behaviour, adversarial relations, and
bookkeeping to make records that could serve as evidence. 2019 is *"enough distance from the event, enough loss of community,
enough insight"* into the phenomenology of coercive behaviors — the silence ending
rather than a habit forming. The thesis it
ends with, **"authoritarianism is interpersonal violence at scale"**, is
`READINGS.md` §4/§4b arriving five years early by the opposite route; the riff
note argues the two directions are not equivalent and should not be welded shut.

## Half of 2019 is not text, and word counts cannot see it

Flagged by Endorphin, 2026-08-13: *"there is a series that had happened in the
summer of 2019 you probably only see half of it, it was a cohort of posts on
attempt to circumvent and neutralize a triangulation event."*

**Half is the exact figure.** `analysis/fb_imageposts.py` counts posts carrying at
least one image and at most three words of their own text — the threshold
absorbs Facebook's "Timeline photos" auto-caption without absorbing real
captions, and bare URLs do not count as words:

| year | posts | image-only | share |
|---|---:|---:|---:|
| **2019** | 314 | **157** | **50%** |
| 2022 | 1,110 | 83 | 7% |
| 2020 | 524 | 19 | 4% |
| all others | — | ≤4 | ≤4% |

309 image-only posts across the corpus carry 333 images and contribute **~0 words
to the 439,512 total**. In every year but one that is a rounding error. In 2019
it is half the record.

The 2019 burst is four days: **07-22 (83), 07-20 (35), 07-23 (34), 07-21 (5)**.
The 174 attached images have been pulled (10 MB, three range requests). They are
**screenshots of private message threads**, timestamped roughly a month before
posting — the June exchanges published in July, several ending in *"This person
isn't available right now."*

The series has two halves in a second sense — **May is read in full in
`analysis/MAY2019.md`**, which is where the largest findings of this pass sit:
the Counterfactual Interview built by hand fifteen months before AI Dungeon, the
refusal of the diagnostic label stated in May and executed as black bars in July,
and the authorless reading given in his own words and explicitly contrasted with
conspiracy. The **May 2019** posts are the long-form written half: 53 posts, 12,766 words, including a 3,030-word piece
headed *"Transcript 1: noveD sogellaG — Interview with Devon Gallegos"* (his own
name reversed, interviewing himself), a 1,563-word passage on hypervigilance, and
a 305-word post reasoning explicitly about the definition of paranoia against his
own evidence. The **July** posts are the documentary half, and they are almost
entirely images. A word-count pass sees the first half and is blind to the
second.

**Two consequences.**

The 2019 row in the table above is understated. Its 20,441 words describe a year
of which half the posts said nothing measurable, so whatever "the break is 2019"
means, it is a larger break than the word counts show.

And **`Transcript 1` has no `Transcript 2`** anywhere in the export. Absent a
second instalment it is weak evidence on its own — but combined with a series
that is half screenshots, it is the kind of gap worth not explaining away.

### What the screenshots actually are

Cleared for analysis by Endorphin on 2026-08-13 — *"these image already respect
privacy"* — and OCR'd by `analysis/fb_jul2019.py`. 169 of 174 carry readable
text, 106,030 characters.

**The redaction claim holds, and it is stricter than usual.** Across all 174:
**zero** handles, phone numbers or email addresses, and every capitalised
personal name in the OCR belongs to a public figure or published author —
Ehrlichman, Nixon, Bateson, Bergson, Verwoerd, Eli Lilly. Message screenshots are
cropped above the sender. What is blacked out is not a name but a **recurring
category term**, struck with a bar everywhere it occurs, including mid-sentence
where the grammar plainly needs it (*"neither are you aware that your ███ is not
inhabited by a single, solid, coherent, consistent agent"*). The diagnostic label
is removed and the mechanism is left standing. **The argument is built to work
without the category.**

**It is a constructed argument, not an evidence dump.** The 174 images interleave
at least five registers — private message screenshots; behavioural description
(stonewalling, silent treatment); trauma and dissociation literature; critical
psychiatry; drug-war political history (the Ehrlichman confession on criminalising
"the antiwar left and black people") and methamphetamine dose-escalation
neuroscience; and philosophy. Register counts from the script are indicative only
and leave roughly half unclassified; the point is the interleaving, not the tally.

**It is not one-sided.** Among the message screenshots he published are ones
attacking him — *"you ask to be held accountable yet when I (and we) do, you
attack us and belittle our experiences."* Whatever "circumvent and neutralize"
meant in practice, it did not mean publishing only the favourable half.

### The multiplicity thesis is here, in July 2019

The single most consequential screenshot models the abuser as **multiple agents
with no unitary author**:

> Agent A happens to be the lovebombing, fake lovey dovey, fake joy to the world
> kind, Agent A wants to be liked. Agent B is more akin to a malignant ███, Agent
> B just likes to see blood and tears. […] neither are you aware that your ███ is
> not inhabited by a single, solid, coherent, consistent agent. […] no agent in
> the ███ is truly good or righteous, it's agents of various grades of nastiness
> taking turns ruling the actor or faker that we call the I.

Two things follow.

**This is `READINGS.md` §X's small set of shapes, four years early and more
formal than the 2023-12 threads.** Agent A / Agent B is a two-shape taxonomy of
bad faith with the shapes named and their strategies distinguished. It also
predates the 2020-10-02 World Info entry, which was until now the earliest
instance. The same series carries a DARVO dialogue (*"I'm sorry you feel there is
shit on your sofa, but I hear hostility in your voice"*) — a third shape,
deflection, in worked form.

**And the Deleuze passage in the same four days is the monstrous hybrid's
source:** *"I imagined myself approaching an author from behind and giving him a
child that would indeed be his but would nonetheless be monstrous."*

### This corrects the push in the riff note

`notes/riffs/2026-08-13-the-2019-break.md` argues that §4b's authorless hybrid and
the 2019 thesis *"authoritarianism is interpersonal violence at scale"* make
opposite predictions about attribution: that the scaled-up reading always has a
person at the end of the bookkeeping, while the hybrid lets the perpetrator
dissolve. **That argument does not survive these screenshots.**

In July 2019 he is already reading the *interpersonal* perpetrator as authorless
and multi-agent — *"the actor or faker that we call the I"*. The perpetrator
dissolves at the small scale too, in the same series, three weeks before the
sentence about scale. So the two theses are not opposed by scale at all: **both
levels are multi-agent systems producing the same small repertoire without a
unitary author**, and "interpersonal violence at scale" is a claim that the
mechanism is the same mechanism — where the mechanism *is* multiplicity.

The riff note's narrower point survives: a phenomenology takes a subject, and
attribution remains the real boundary. But the boundary does not fall between the
scales, which is what that note claimed. It falls between *mechanism* and
*responsibility* — and the 2017–2019 bookkeeping was assembling responsibility
against a person whose unitary authorship he had already stopped believing in.
That tension is his, not an artifact of reading, and it is live in the same four
days.

### The arc to 2024

The same July series carries multiplicity in its *other* valence — the survivor's:

> her voices […] are many different selves, with different names, ages,
> experiences, feelings, identities; dissociated selves that became internal
> representations of her external world. Rather than trying to eradicate these
> different parts of her […] she begins to embrace them.

Five years later, on 2024-10-17 — one of the 377 revision chains — he applies it
to himself as a survival strategy: *"We are thousands of cortical columns, and
thousands of selves […] Here have one of my selves. It hurt at first. […] Want to
kill this part of me? Fine, have it."* **Multiplicity enters the archive in July
2019 as an account of the person harming him and leaves it in 2024 as an account
of how he survived.** Both framings are present in the same four days of 2019.

## The origin of the practice, which the AI Dungeon export lost

`AID_EXPORT.md` records the earliest surviving adventure as `dxqLiJrw55P2`,
2020-12-07. The Facebook posts document the four months before it, in real time:

| date | what it records |
|---|---|
| **2020-08-10** | First contact. Links the Verge piece on AI Dungeon; *"I spent a couple days with AI Dungeon 1"*. Claims a 30-year prehistory: *"Ever since tapping with Eliza in the form of Freud on my Apple IIE"*, and a botness test — *"Asking how it would react to calfskin wallets would reveal their botness."* |
| **2020-08-13** | First scenario reports from AI Dungeon 2. Notes the model ending a scene unprompted: *"the AI added a simple THE END."* |
| **2020-08-14** | Discovers World Info: *"apparently there's a world-building file, but one thing at a time folks."* |
| **2020-08-30** | GPT-3 named. *"i'm gonna go step into my linguistic holodeck with GPT-3 in it's AI Dungeon role, and ask it to go meta with me today."* |
| **2020-09-21** | Scenario-sharing with other users; names a run *A Comedian*. |
| **2020-10-02** | The method post. World Info used to encode *"a perpetrated-perpetrator dichotomy, and as many tactics of deflection, manipulation"*; dictation as input; Immersive Reader as output. |
| **2020-10-05** | *"episode 4"*, *"episode 5"* — numbered episodes, alternating serial narrative with interstitials, scored to a Creative Commons NIN album. |
| **2020-10-06** | Deliberate capability probe: *"I asked GPT-3 what it knows about COVID-19, more than 19 times"*, reasoning explicitly about the Common Crawl cutoff and calling himself *"a person from the fuuuuuuuture."* |

Three of these matter beyond dating.

**The episodic broadcast form starts in October 2020.** `READINGS.md` §IX reads
the Love Sharks broadcasts as a *score* rather than a document — dictated cues
in, TTS out, nobody in the loop reading. The 2020-10-05 posts show that loop
assembled and already numbered into episodes, with a soundtrack, two months
before the earliest surviving adventure. §IX's reading is not a late
development; it is how the practice began.

**The bad-faith enumeration is three years older than §X thinks.**
`READINGS.md` §X rests on Endorphin enumerating the bad-faith repertoire
unprompted in the 2023-12 threads. On 2020-10-02 he enumerates it as a **World
Info entry** — a prompt-engineering artifact, written to make a model produce
the behaviours. That is the same list put to a different use, and it is the
earliest instance in any of the four archives.

**He states an authorship discriminator.** See the next section.

## The comma test — a claim that half survives

On 2020-10-02 he wrote:

> For most of it, i've been using the dictation function which I never use, so
> you'll know who wrote what by the lack of commas.

This is the only place in any of the four archives where he hands over an
explicit method for separating his text from a model's. It is testable, and it
demonstrates the house length-matching rule twice over.

Comparing posts from 2018-01..2020-08 against 2020-09..2022-12:

| length band | pre | post | delta |
|---|---:|---:|---:|
| **unmatched (all)** | 0.0330 | 0.0430 | **+30.1%** |
| 20–60w | 0.0547 | 0.0429 | −21.5% |
| 60–150w | 0.0522 | 0.0430 | −17.7% |
| 150–400w | 0.0589 | 0.0462 | −21.5% |
| 400w+ | 0.0570 | 0.0499 | −12.5% |

**Unmatched, the effect has the wrong sign.** Median post length goes from 14 to
44 words across the boundary, and longer posts carry more commas per word, so
the naive comparison says commas *rose* 30%. Length-matched, they fall 12–22% in
every band. This is `CLAUDE.md` rule 5 reproducing itself on a fourth archive,
and more sharply than in the original case: not a 63%-to-66% correction but a
sign reversal.

**But the control does not clear it.** Period rate over the same bands:

| band | pre | post | delta |
|---|---:|---:|---:|
| 20–60w | 0.0873 | 0.0514 | −41.1% |
| 60–150w | 0.0626 | 0.0398 | −36.4% |
| 150–400w | 0.0521 | 0.0501 | −3.7% |

In the two shorter bands periods fall roughly **twice as hard as commas**. If
dictation specifically suppressed commas, commas should fall furthest; they do
not. So in short and medium posts the real finding is a general collapse in
punctuation density, and "lack of commas" names a symptom rather than the
mechanism.

The exception is the **150–400 word band**, where commas fall 21.5% and periods
are flat at 3.7%. There, and only there, the discriminator is comma-specific and
does what he said it does. That is also the band where a dictated passage is
long enough to have subordinate clauses but short enough to be spoken in one
sitting. **Verdict: the claim is right about a real signal, wrong about its
specificity, and correct as stated only in one length band.** Worth carrying
into any future attempt to separate his prose from model output, with that
qualification attached.

## The revision chains

`edits_you_made_to_posts.html` holds **377 successive drafts**, 2020-08-11 ..
2024-10-18, grouping into **196 chains** (52 single, 115 pairs, 22 triples, 6
quadruples, 1 five). Chains were built by requiring both a gap under an hour and
text similarity over 0.5, with the similarity computed only after a length
prefilter — an unfiltered ratio merges unrelated short posts.

- median gap between drafts in a chain: **68 seconds** (min 0, max 3,447)
- first-to-last word delta: **74 grew, 17 shrank, 53 unchanged**; median +1 word

Revisions are fast and additive. The unchanged-length cases are the interesting
ones: they are word swaps, and several are **dictation repairs** — the 2021-06-15
chain fixes *"Gary Putz"* to *"Gary Lutz"* (a real author) and passes through
*"GOT J 6B"* before settling on *"GPT J 6B"*. Both are acoustic errors, which is
the same signature `READINGS.md` §IX used to argue the Love Sharks texts were
dictated (*Top apology* for *topology*).

This is the corpus's only edit history of **human** prose. NovelAI preserves
rejected *model* generations; this preserves rejected *authorial* ones, at
second resolution. The obvious next move — comparing what he revises in his own
sentences against what he rejects from a model's — is not attempted here.

## Meta AI: a fourth generation surface, very small

Three chats, 137 turns, all shape B:

| chat | turns | dates |
|---|---:|---|
| `meta_ai` | 113 | 2024-04-29 .. 2024-09-21 |
| `lily_the_wordsmith` | 20 | 2023-12-08 |
| `jane_austen_ai` | 4 | 2023-12-08 |

`lily_the_wordsmith` is a **turn-by-turn collaborative fiction bot** — it opens
by writing one sentence and handing back: *"Now it's your turn! Just add a
sentence or two to continue the story."* That is the NovelAI practice in a
stripped form, with no undo, no settings, and forced alternation. At 20 turns on
a single day it is too small to measure, but it is the only place in the corpus
where a *vendor* imposed the turn-taking frame that `FINDINGS.md` adopts as its
unit of analysis, rather than Endorphin choosing it.

Both December 2023 chats are one-day trials that went nowhere. The practice did
not move to Meta AI.

## The videos are two cohorts, split by 242 days of silence

`your_videos.html` holds 512 dated video posts:

```
2011:1  2014:1  2017:1  2018:1  2019:1  2020:16  2021:104  2022:153  2023:132  2024:102
```

Fifteen of the sixteen 2020 videos fall between **2020-10-02 and 2020-11-09**.
Then video posting stops entirely for **242 days** — the largest gap in the whole
post-2020 record — resuming **2021-07-09**.

- **Cohort A, Oct–Nov 2020.** Attached to the numbered episode posts within
  seconds: episode 3 (+39s), episode 4 (+93s), episode 5 (+27s), episode 6
  (+64s). Their own captions credit *"immersive reader and ai dungeon and open ai
  and microsoft"* and a Creative Commons NIN album.
- **Cohort B, from 2021-07-09.** Endorphin identifies these as VQGAN work made
  before, and alongside, the broadcasts.

**VQGAN cannot account for cohort A.** "Taming Transformers" was not posted until
December 2020, and the VQGAN+CLIP notebooks spread in June–July 2021 — which is
when cohort B restarts, almost to the week. The tool postdates cohort A entirely.

This matters for `READINGS.md` §IX, which reads the Love Sharks texts as a score
— dictated cues in, TTS out, nobody reading. **Cohort A is that loop's earliest
surviving output**, and the captions describe the toolchain in his own words at
the time. It is the strongest available corroboration of §IX, and it is fifteen
files rather than 1,086.

### Cohort A pulled, 2026-08-13

All fifteen, 141 MB, in three range requests (`analysis/fb_cohort_a.py`;
manifest in `data/fb_cohort_a.tsv`). MP4 atoms read directly for duration and
track types.

- **Every one carries an audio track.** 15/15 are `soun+vide`. They are not
  silent generative art, which is what the VQGAN cohort would predict.
- **139.7 minutes of narration**, 2:13 to 24:33 each.
- Captions number them explicitly — *episode 3* through *episode 6* — and name
  the toolchain: *"ai dungeon and i on the saaaaaaame paaage"*, *"just plunked
  in relevant biblical verse re: love into aidungeon"*.

**The cohort is one bounded project, and it under-delivered by half.** The
2020-10-02 post sets the plan: *"i'll try to do one a day so there may be
thirty-one chapters."* Fourteen were posted between 10-02 and 10-31, the last
captioned *"Final post of Domestic Abuse Awareness Month"*; a fifteenth follows
on 11-09 as an election coda. **Planned 31, delivered 14, then the 242-day
silence.** That is the first instance in any of the four archives of a stated
production target set against a countable outcome — everything else in the
corpus is measured against what survives, not against what was intended.

**The 2h20m of audio has never been heard by any pass in this repo.** §IX argues
these texts are scores meant to be spoken; here is the speaking, and it is
unanalysed. Transcription needs tooling the container does not have (no
`ffmpeg`, no `ffprobe`). Flagged, not attempted.

## Not analysed

**The 1,524 private message threads — 147,233 turns, 1.77 million words,
2008-03 .. 2024-10 — are deliberately unread**, and Endorphin confirmed the hold
on 2026-08-13: that work happens in a more private location, not here. They are four times the volume
of the public posts and they belong substantially to other people. See the
privacy section of `FB_EXPORT.md`. `data/fb_summary.json` carries their counts
and dates and nothing else. Any future use of them needs a specific question and
Endorphin's explicit decision, and probably neither.

Also untouched, and lower priority: 994 off-Meta activity records, the ads and
security categories, 1,086 videos and 5,231 images.
