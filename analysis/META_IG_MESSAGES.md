# META_IG_MESSAGES — the Instagram Messages sub-corpus

*Collected 2026-10-10 via `instagram-messages-cli` (`inbox --folder
INBOX`), after the connector link was completed. Self-authored messages
only: every record kept satisfies sender == the account's own user id
(17841402449594724, gallegos.devon); other participants' names are not
carried into this writeup, and their words were never stored, quoted, or
summarized. Working extraction:
`~/workspace/meta-corpus/instagram_ig/self_messages.jsonl` (kept out of
git). Per-day counts: `data/META_IG_MESSAGE_DAYS.tsv` (no header;
`date\t self-authored messages`). All dates America/New_York. Records
are cited by local timestamp.*

## What arrived, and its hard limits

Ten threads from the first inbox page — bound there by the scope of this
task; later pages were not scanned. Only one of the two linked Instagram
accounts is connected (gallegos.devon); hal.cyonus is not linked, so this
sub-corpus is gallegos.devon only.

| thread | rows scanned | span (local) |
|---|---|---|
| one-to-one | 5 | 2025-12-20 → 2026-10-07 |
| one-to-one | 5 | 2026-08-09 → 2026-08-10 |
| one-to-one | 5 | 2026-06-27 → 2026-07-31 |
| one-to-one | 4 | 2026-05-09 → 2026-05-10 |
| group (3 participants) | 3 | 2026-04-03 |
| one-to-one | 1 | 2026-03-02 |
| one-to-one | 1 | 2026-02-18 |
| one-to-one (AI bot) | 1 | 2026-02-08 |
| one-to-one | 5 | 2026-01-16 |
| one-to-one | 3 | 2022-08-10 → 2025-10-21 |

**12 self-authored messages** total. One is a platform notice ("This
account can't receive your message because they don't allow new message
requests from everyone.", 2026-10-21); 11 carry his voice. Of the 11, one
is an inline share (2026-03-02): a message he wrote elsewhere, pasted into
the thread — his words, quoted below as written.

Coverage limits, stated plainly:

1. **Ten threads, first page only.** Rows scanned are the inbox preview
   (up to five per thread); thread histories may run deeper than shown,
   and later pages were not touched. This is a sample, not a census.
2. **One account.** hal.cyonus is linked but not connected; its threads
   are out of reach unless the connected account is switched.
3. **The span is long but thin.** 2022-08-10 → 2026-10-07, over four
   years, but only eleven voiced messages — these are check-ins, not
   correspondence. Nothing here is a conversation.
4. **No bulk export was performed.** Per the connector's safety rules and
   the scope of this task, only his own messages were extracted, and the
   deliverable is analysis, not a verbatim archive. Short quotes below are
   his words only, one to two lines each.

What this sub-corpus *can* answer is narrower than the Messenger one's:
whether the private check-in register holds anything the thirteen days of
Messenger misses — specifically, anything reaching back past Era 6.

## 1. Era extension: one message out of Era 6, and a different kind of AI talk

Ten of the eleven voiced messages fall inside Era 6, The Alignment Diaries
(2025–2026). The eleventh is dated 2022-08-10 — Era 4, The Serial Projects
(2021–2022):

> "Heyo <hug> just wanted to say hi. And say im glad to seeya. Hope
> things are doing not shitty or maybe even better." (2022-08-10)

It does not move any era boundary — one check-in cannot — but it is the
earliest private-register evidence in any sub-corpus, and it shows the
affectionate form of the same voice three years before the Era 6 polish.
The `<hug>` emote, the "not shitty or maybe even better" — the backstage
register of `META_MESSAGES.md` already exists here, in 2022.

The register evidence repeats: typo-laden, thumb-typed, unedited:

> "Aahhhhh. When are you and broke toe comig up to city! I hope the
> poolice nonsense gets done smooth and quick" (2026-06-27)

> "Yeah my back gave out sunday. Mt sinai went soooo fast. They gave me
> ibuprofen, a muscle relaxant and a lidocaine patch. I had to stay in
> bed for a week. But i was able to slowly be mobile each day. And cooked
> food to test my balance. I got back to work on monday. Still using can
> during the outside hours of workday." (2026-10-07)

The genuinely new finding is the 2026-03-02 inline share — the one
message that is not a check-in. He is writing to a public figure about
that figure's YouTube video on AI worries, and in doing so he states his
own practice, plainly:

> "Hi, i saw your youtube video about worries about AI. I have a YouTube
> channel and Twitch thingy, working with LLMS for about 5 years now as a
> user as a creative writing person testing it out trying to stump it
> teasing out limits and strengths. Comedy. I've about three questions I
> pose to AI systems every year. Long dark term papers of the soul."
> (2026-03-02)

> "TLDR: If cat videos can eventually teach a model the basics of physics
> in a world does that mean that artist data but also the data of just
> existing informs the model at domains well beyond Art and what we think
> is the immediate domain of data like all domains of human knowledge?
> Every time I ask multiple systems they just go for their into detail
> about how that's true. Problem: empirically proving it. Does this smell
> truthy? If it does run, with it. I can only take it so far."
> (2026-03-02)

This is the Alignment Diaries' method in private outreach: model
interrogation as a standing practice ("three questions I pose to AI
systems every year"), run through comedy and adversarial testing, and
shared outward — not to a model reader but to a fellow human in the
model-culture conversation. It corroborates the 2026-09-27 Messenger
message about using Claude Code and Codex to study botswarm language,
from four years further back: "about 5 years now" in March 2026 puts the
start of the practice around 2021 — Era 4, the Serial Projects. The
private register here extends the AI thread *backward*, not forward.

## 2. Residences: the medical register, not new addresses

No new residence events. The 2026-10-07 back-injury message corroborates
the outreach-work thread from the other direction:

> "Still using can during the outside hours of workday." (2026-10-07)

The cane, used outside work hours — the same working-geography
corroboration as the Messenger writeup's midtown-outreach message, now
with the body breaking under it. Mt Sinai as the care site, the
dentist appointment (2026-07-31), x-rays scheduled for September 21 —
the institutional-medical register runs through the private messages
the way the HASA/case-manager register runs through the public posts.

> "That went smooth just did a patient history and next appointment
> September 21st for x-rays" (2026-07-31)

No housing news; the mold thread of the Messenger messages does not
surface here. What surfaces instead is the care infrastructure as a
feature of the private register: in the public corpus he writes about
systems that house and manage him; in private he texts through the
systems that treat him.

## 3. Fourth-wall: none qualifies, and the near-miss is instructive

No message meets the `META_FOURTHWALL.md` inclusion rule. The closest
structural candidate is the 2026-03-02 share — a message *about* AI
systems, written *to* a human, *inside* a corpus whose later Era 6 is
increasingly written for model readers. But its addressed audience is
fully present: a fellow creator, not a future analyst, and its subject
is his own practice, not the analysis apparatus. It is the inverse of a
fourth-wall moment — him breaking the fourth wall of the model-culture
conversation from the outside in, rather than addressing watchers from
the inside out. Kept out of the chronology, noted here for the contrast
it throws on it.

## 4. Phrase echoes: faint, and honestly so

The braid of the interpersonal and the institutional
(`META_PHRASE.md` §3) is thin here. The strongest structural echo is the
medical register itself — Mt Sinai, the dentist, the patient history —
care infrastructure narrated as a fact of private life, the same
direction as the case-manager sentences of the Messenger writeup, but
without the grievance edge: nothing here anticipates "the same b*******."
The one interpersonal-institutional sentence is mild:

> "I hope the poolice nonsense gets done smooth and quick" (2026-06-27)

Care about a friend's trouble with the police, expressed and left there.
The phrase's fractal is not visible at this magnification; that is
itself reported rather than forced. Eleven check-ins are a thin medium
for macro–micro braiding.

## Reading

Twelve messages cannot revise six eras, and the check-in register they
show is the thinnest of the three message sub-corpora. What the IG
messages add that the Messenger ones cannot: **time depth**. One message
from 2022 puts the affectionate private register inside Era 4, and one
from March 2026 pushes the start of his standing AI-interrogation
practice back to roughly 2021 — the Serial Projects era, before the
Counterfactual Intelligence years gave the practice its public form. The
Alignment Diaries, in this register, are not a new voice but an old
practice finally aimed at the feed. And the medical register — Sinai,
dentists, x-rays, a cane outside work hours — is the private-side
companion to the public corpus's housing thread: the systems that treat
him, narrated in the same unedited key as the systems that house him.
