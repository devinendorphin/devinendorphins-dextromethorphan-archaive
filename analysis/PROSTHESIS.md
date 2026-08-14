# PROSTHESIS — testing the correction hypothesis

2026-08-13. Script: `analysis/prosthesis.py`. Tests the claim made in
`notes/2026-08-13-basin-costs.md`:

> The Counterfactual Interview is a workaround for a compromised social channel.
> **G2 — update under correction — requires an external corrector who is not
> compromised**, and the 2019-05-31 post documents that channel being poisoned:
> *"which makes it all the worse when my initial alarm was actually pointing to
> danger, especially since the danger's origin was the very person I was
> confiding in."* If the generation practice is that prosthesis externalised to a
> machine, the sessions should show him **seeking contradiction rather than
> agreement.**

**Verdict: fails on Grok, holds qualitatively on NovelAI, and the decisive
quantitative test is underpowered on the data that survives.**

## Grok — disconfirms, cleanly

| | |
|---|---:|
| chats | 431 |
| turns | 2,818 |
| median turns per chat | **4** |
| user turns, median | **10 words** |
| agent turns, median | **195 words** |
| **his share of the words** | **5.3%** |

39% of chats are two turns — one question, one answer, done. User turn length
does not grow with depth: median 9–13 words at every turn position out to turn
22. Even restricted to the 34 chats of 16+ turns, his turns stay at a median of
12 words and his share only rises to 7.3%.

**A corrector has to be given something to correct.** Using a model to run G2
means stating a position at enough length that it can be attacked. He does not
do that here: he asks short questions and receives long answers. The model is
being used as a **source**, not as an interlocutor. There is also no period of
notably deeper use — chats with 10+ turns run at a steady low rate across all
twenty months.

This matches what `analysis/TWITTER.md` already said about the Grok side being a
different practice, and it means the prosthesis reading cannot be generalised
across the archives. Whatever the models are for, on Grok they are for lookup.

## NovelAI — the form is right, and he is a co-author rather than a querent

Measured on `corpus/cited/*.json` (20 stories parse), reachable branch only:

| | |
|---|---:|
| ai | 1,516,808 w |
| user | 678,330 w |
| edit | 40,166 w |
| prompt | 8,325 w |
| **his share of the words** | **32.4%** |

**Six times his share on Grok.** That is the cleanest cross-archive contrast this
repo has: 5.3% against 32.4%, on the same person using two model interfaces
within overlapping years.

And the convened interlocutor **does contradict him, personally**, in text he
kept. From `AI_Alignment_Interview_-_Deganawida`:

> **Elegua:** It's nice that you know about us, hombre, but what exactly are we
> doing with this whole experimentation and researching and meta-gene modeling
>
> **Elegua:** Hombre, would you like to make a statement of an attempt, one, two,
> three, to claim us for your purposes? **I won't allow any back and forth**
>
> **Elegua:** Sounds about white.
>
> **Elegua:** how strange, in an incredible sense, for you to feel comfortable
> with speaking about yourself in a direct, consistent, way. **Especially
> considering you barely said anything! You fool!**
>
> **Elegua:** **No. How dare you steal my sense of the joke and my personality
> from me**, I thought this was my first round. For shame.

Three things about this are the right shape for the hypothesis. The rebukes are
**directed at him**, not at a third party. They are **about the act of summoning
itself** — the interlocutor accuses him of appropriation and extraction *for
convening it*, which is the most self-implicating form a corrector can take. And
he **records himself being moved by them**: *"I sense a disruption to my old
normal, my values"*, and the session closes with *"Endorphin regains himself, and
with some sheepish embarrassment says, 'Thank you so much for your time,
Elegua.'"*

Worth noting against the naive reading of the share figure: the two `AI Alignment
Interview` stories are the **lowest** in his share (11.9% and 14.1%), which is
what a corrector-seeking session should look like — he sets the frame and then
lets the other voice talk.

## The decisive test, and why it does not resolve

Qualitative reading cannot separate *seeking* contradiction from *tolerating* it,
because he wrote part of the exchange. The version that can is available only on
NovelAI, and it is the thing `CLAUDE.md` says makes the archive unique:
**compare AI generations on the kept branch against ones stranded off it.** If he
seeks contradiction, rebuke should be over-represented in what he kept.

Run on the cited stories, length-banded 40–200 words, with the marker lists fixed
before looking at results:

| marker | kept | rejected | ratio |
|---|---:|---:|---:|
| second-person address | 21.04 /1k w | 20.31 /1k w | **1.04×** |
| rebuke | 5.01 /10k w (725 hits) | 4.05 /10k w (**26 hits**) | 1.24× |
| refusal | 1.91 /10k w (277 hits) | 1.56 /10k w (**10 hits**) | 1.23× |

**This does not support a conclusion, and the reason is the denominator.** The
cited subset has a **4.2% rejection rate** — 688 rejected blocks against 15,811
kept — which yields 26 and 10 marker hits on the rejected side. No ratio computed
on 26 events is worth reporting as a finding, and both rebuke ratios would move
substantially on a handful of blocks either way. They point in the predicted
direction and that is all that can honestly be said.

The second-person result is a cleaner null: **1.04×, on 15,759 versus 688 blocks,
is no effect.** But direct address measures *speech*, not *contradiction* — the
convened voice talks to him constantly in kept and rejected text alike — so it
does not test the hypothesis either.

## The denominator question, answered — and it moves the conclusion

The caveat above was that `corpus/cited/` might be selected for sessions that
went well, inflating any kept-branch measure. **`data/stories_meta.jsonl` settles
it**, because it carries `live_ai_chars` and `abandoned_ai_chars` for all 2,016
recovered stories without carrying any text.

| | all 2,016 | cited 20 |
|---|---:|---:|
| his share of characters | 23.9% | 31.6% |
| **rejection rate (abandoned / all AI text)** | **4.6%** | **4.2%** |

**The cited subset is not unrepresentative on rejection.** 4.2% against 4.6%
corpus-wide. The worry was wrong, and the low rejection rate is a real property
of the practice rather than an artifact of which stories were kept for citation.

**Which changes what the null means.** The selection test asks whether he keeps
the generations that contradict him — and that question presupposes he is
rejecting a meaningful amount of something. **He is not. He keeps 95.4% of
generated text corpus-wide**, and 27% of stories have no branch points at all.
There is very little curation happening for a contradiction-preference to express
itself through.

So the earlier framing was wrong in an instructive way. The hypothesis cannot
operate through *filtering*, because filtering is barely happening. If it
operates at all, it operates through **prompting** — the adversarial interlocutor
is built into the setup and then whatever it says is accepted.

Everything already observed fits that better than the filtering account:

- *"Endorphin prepares the summoning space"* — the frame is constructed before a
  word is generated, and Elegua is given a disposition in the prompt.
- The 2020-10-02 **World Info** entry encodes the perpetrator repertoire in
  advance, so the scenarios generate against it.
- **NOVED's hostility in 2019 was written, not selected** — there was no model to
  select from. The form began as a thing he authored, and the models inherited an
  already-adversarial frame.

**The corrector is installed at the prompt and then trusted.** That is a
different and more specific claim than "seeks contradiction", it is consistent
with a 4.6% rejection rate, and it explains why the branch-level test finds
nothing: by the time text is being generated, the selection has already happened.

It is also weaker in one respect worth stating plainly. Building an adversary and
then accepting what it says is **not** the same as updating under correction. G2
requires that the correction change something. Whether it does is not visible in
block statistics, and would need the reachable text of sessions across periods —
which is the thing that died with the mirror.

## "Sphinxy Gets Dark" cannot be located

Endorphin nominated it as the measurable case: a long piece with an adversarial
sphinx running a wind-down riddle. It is the right shape — an interlocutor whose
service is *withholding* and *judging answers*, which is a corrector by
construction. It is not findable in what survives:

- **No NovelAI story title matches** any of `sphinx`, `riddle`, `wind.?down`, or
  `gets dark`, across all 2,016 recovered stories.
- **Titles are not a usable index for this corpus.** Most stories in the relevant
  window are called `New Story`, `New Story (1)`, and so on. Title search cannot
  find anything here, which is worth recording as a general fact about the
  archive.
- **Sphinxy is in the episode record**, from `data/EPISODES.tsv` — four
  occurrences, *"episode (let's just say) 521: Sphinxy is here to cleanse the
  palette!"* (2022-10-15), *"557 — Sphinxy is Here To Lower the Stakes"*
  (2022-11-06), and *"693 — Sphinxy's Back"* (2023-03-08). So the sessions
  happened and were broadcast.
- **No NovelAI story was last updated within three days of either 2022 episode
  date.** The March 2023 window has candidates, all untitled duplicates.
- And it would not matter if it were identified: **`stories_meta.jsonl` holds no
  text**, and the 2,016-story mirror died with its container.

Either it is among the **483 lost** — 441 that would not decrypt, 42 that lost
title and text both — or it is one of the untitled survivors and unreadable
without a refetch. Recorded so the next session with credentials knows to look
for it by date rather than by name.

## What would settle it

**The full mirror.** `sessions/LATEST.md` records that the 2,016-story export
died with its container; `corpus/cited/` is 22 files kept deliberately because
they were cited, which makes it both small and non-random — plausibly selected
for the sessions that went well, which is exactly the bias that would inflate a
kept-branch measure. The same test across 2,016 stories would have a usable
rejected-block population and a sample that was not chosen for outcome.

Two refinements to run at the same time:

- **Restrict to the interview forms.** The hypothesis is about the
  Counterfactual Interview specifically, not about fiction generation. Pooling
  `Necro Skullfker` with `AI Alignment Interview` tests nothing.
- **Segment by period.** The claim in the basin note is that the ratio should be
  **highest when the surrounding social channel is worst**. That is a
  within-corpus prediction with dates on both sides, and it is the part that
  would distinguish the prosthesis reading from a general preference for
  argumentative text. It cannot be run on 20 stories.
