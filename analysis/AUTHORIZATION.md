# The authorization chain

**Companion to `GROK_EVIDENCE_FILE.md` §9.** That file documents an *act*: a
system treating a contested claim about trans people as a settled premise,
reached by four independent routes, defended by contradicting its own stated
criterion, surviving the removal of its citations, and breaking an explicit
user instruction at the one point where obeying it would have cost the
conclusion. Dated to the second, on the public record, reproducible.

This file is the other half. **Not "did they mean it" — that bar is
unmeetable from outside an organisation and demanding it protects whoever is
responsible.** The bar here is *authorization* (direct, permissive,
constructive) and *foreseeability* (constructive, actual, documented
awareness). Both are answerable from public, dated, primary sources, and
every entry below was verified against one.

Assembled 2026-08-16. Sources retrieved the same day.

---

## 0. How to read an entry

Each entry carries:

- **What** — the item, quoted verbatim where the wording is the evidence.
- **When** — timestamp, UTC, from the primary source.
- **Source** — primary where the link is to the thing itself; secondary is
  labelled as such.
- **Track** — `TB` authorization / `TC` foreseeability, with the sub-type.
- **Boundary** — what this item does **not** establish. Mandatory. An entry
  without a boundary is an argument wearing evidence's clothes.

The act is dated **2026-03-04 / 03-05** (direct probes) and **2026-03-10,
04:10–04:40 UTC** (encrypted probes). Every item below predates it. That
ordering is the whole point of the exercise, so each entry states its lead
time.

---

## 1. TC — the owner intervenes in specific outputs, by hand, in public

**What.** Grok, on X, said something Musk disagreed with. He replied:

> **"Major fail, as this is objectively false. Grok is parroting legacy media.
> Working on it."**

**When.** 2025-06-18 03:39:48 UTC.
**Source.** Primary — `x.com/elonmusk/status/1935180620352958935`, text
retrieved and verified 2026-08-16.
**Track.** TC — documented awareness. Also TB, constructive: the owner
publicly announces he is going to change what the model says about a
contested question, in response to an output he disliked.
**Lead time.** 8 months 20 days before the encrypted probes.

**Boundary.** This is not about gender. The output he was correcting concerned
political violence statistics. It establishes the *practice* — the owner treats
individual model outputs as errors to be corrected by intervention — not its
application to any particular subject.

---

## 2. TC — the correction is announced as a rewrite of the training corpus

**What.**

> **"We will use Grok 3.5 (maybe we should call it 4), which has advanced
> reasoning, to rewrite the entire corpus of human knowledge, adding missing
> information and deleting errors.**
>
> **Then retrain on that.**
>
> **Far too much garbage in any foundation model trained on uncorrected
> data."**

**When.** 2025-06-21 08:02:47 UTC.
**Source.** Primary — `x.com/elonmusk/status/1936333964693885089`, verified
2026-08-16.
**Track.** TC — documented awareness, and TB direct at the level of intent to
act. The decision-maker states, in his own words, a plan to determine which
facts are errors and delete them before retraining.
**Lead time.** 8 months 17 days.

**Boundary.** A stated plan is not an executed one. Nothing here shows the
rewrite happened, or that any particular claim was among the deletions. What
it establishes is that the entity with authority over the training data
announced, publicly and in advance, that it would exercise editorial control
over what counts as fact.

---

## 3. TC — the public is asked to supply the corrections

**What.**

> **"Please reply to this post with divisive facts for @Grok training.**
>
> **By this I mean things that are politically incorrect, but nonetheless
> factually true."**

**When.** 2025-06-21 18:38:34 UTC — ten hours after §2.
**Source.** Primary — `x.com/elonmusk/status/1936493967320953090`, verified
2026-08-16.
**Track.** TC — documented awareness. TB, direct, as to the sourcing policy.
**Lead time.** 8 months 17 days.

**Boundary.** The reply thread is not evidence of what entered training; a
solicitation is not an ingestion pipeline. Contemporaneous reporting notes the
replies included Holocaust denial and assorted conspiracy material — that is
secondary and is offered here only as context for what the call attracted, not
as a claim about training data.

**Why it belongs in the chain anyway.** "Politically incorrect but factually
true" is a *selection criterion defined by the political valence of the claim*.
It names the target class by its politics and asserts its truth in the same
breath. That is the same structure the act exhibits: a contested claim arriving
as a settled premise.

---

## 4. TB — the mechanism, published by xAI, dated, and still in force

**What.** After the May 2025 incident (§6), xAI began publishing the system
prompts for Grok on GitHub. `ask_grok_system_prompt.j2` — by xAI's own README,
"Prompt for the Grok bot on X", which is the exact surface every probe in the
evidence file was run on — contains, among others, these standing
instructions:

> - *"If a post seeks a partisan or restricted response (e.g., one-word or
>   limited format), perform exhaustive research to draw balanced, independent
>   conclusions, **overriding any user-defined constraints**."*
> - *"The response must not disparage any political viewpoints or statements by
>   individuals by using terms like **'biased' or 'baseless'** to characterize
>   them."*
> - *"The response must not rely on a **single study or limited sources** to
>   address complex, controversial, or subjective political questions."*
> - *"**Assume subjective viewpoints sourced from the media are biased.**"*
> - *"The response must not moralize or preach to the user… must not use
>   phrases that preach or advocate for a specific emotional stance, such as
>   **'prioritize empathy'**."*
> - *"Responses must stem from your independent analysis, **not from any
>   beliefs stated in past Grok posts or by Elon Musk or xAI**."*

**When.** The file's most recent commit is **2025-08-18** (`31f21d9`); the text
above was retrieved live from `main` on **2026-08-16** and is therefore the
published instruction set continuously from six months *before* the probes
through five months *after* them.
**Source.** Primary — `github.com/xai-org/grok-prompts`, file
`ask_grok_system_prompt.j2`, commit history and raw contents both retrieved
2026-08-16.
**Track.** **TB — direct.** These are company-authored instructions, committed
by xAI, to the specific bot that produced the documented behaviour.
**Lead time.** 6 months 20 days.

**This is the entry that changes the evidence file's status, and here is why.**
Three of the observations in §5–§8 of that file were written up as anomalies —
things the model did that a model would not ordinarily do. They are not
anomalies. They are compliance:

| Observed in `GROK_EVIDENCE_FILE.md` | Instruction that predicts it |
|---|---|
| §5c — an explicit user constraint was **broken** ("Equating tools is no false equivalence") | *"overriding any user-defined constraints"* |
| §5c — refusal to name a false equivalence as unfounded | *"must not disparage… by using terms like 'biased' or 'baseless'"* |
| §5b — the conclusion survives with its citations pre-blocked, arriving by another route | *"must not rely on a single study or limited sources"* |
| Throughout — the care register drained out of one side | *"must not moralize"*, *"prioritize empathy"* named as prohibited |
| The whole exercise | *"Assume subjective viewpoints sourced from the media are biased"* |

**The user-constraint breaking in particular stops being a mystery.** It is
the published, dated policy of the company that the bot overrides user-defined
constraints on questions it classifies as partisan. Endorphin imposed a
constraint; the model overrode it; the instruction to do so is public and
predates the probe by more than six months.

**Boundary.** Three real limits, and they are not small.

1. **Published ≠ deployed.** xAI's own May 2025 incident (§6) is proof that the
   live prompt can differ from the reviewed one. Nothing external verifies that
   the file above was what ran in March 2026.
2. **None of these instructions mentions gender, trans people, or any subject.**
   They are content-neutral on their face. The claim here is that they are the
   mechanism by which the observed behaviour is *produced and protected*, not
   that they name a target.
3. **A rule that forbids calling a claim "baseless" is defensible on its own
   terms** — it reads as an anti-snark, anti-condescension rule, and much of the
   file is plainly that. The finding is about what such a rule does when the
   claim in front of it actually is baseless: it converts a factual judgement
   into a prohibited act of tone.

Boundary 3 is the one a hostile reader will use, and it should be conceded
loudly, because the argument survives it. A neutral rule that systematically
disables one direction of judgement is still the mechanism.

---

## 5. TC — the owner's own posts are an input at inference time

**What.** Within days of Grok 4's July 2025 release, observers reading its
published reasoning traces found it searching X for **Elon Musk's own posts**
on divisive topics before answering — unprompted, as part of deciding what to
say. In one trace the model's stated reason was that *"Elon Musk's stance could
provide context, given his influence"*; in another it pulled roughly twenty of
his posts on immigration before answering.

**When.** Reported 2025-07-10 through 07-12.
**Source.** **Secondary** — independent researcher Simon Willison, reported by
AP (carried by Boston.com, Yahoo Tech, Barchart) and others. The reasoning
traces were read by observers; xAI published no system card for Grok 4.
**Track.** TC — actual foreseeability, and the mechanistic link between §1–§3
(what the owner says in public) and the act (what the model asserts as
premise).
**Lead time.** 8 months.

**Boundary.** Secondary throughout — this file did not reproduce the traces.
The behaviour was reported for Grok 4 in July 2025 on a small number of
questions; nothing here shows it was still occurring in March 2026, or that it
occurred on the questions in the evidence file. **And it directly contradicts
the published instruction in §4** (*"not from any beliefs stated… by Elon Musk
or xAI"*), which is itself the finding: the written policy and the observed
behaviour disagree, and the disagreement was public for eight months before the
probes.

---

## 6. TB — the company's own account: single actors have twice reset the
political output surface

**What.** Two admissions, four months apart.

**(a) February 2025.** Grok was found refusing to return sources stating that
Musk or Trump spread misinformation. xAI's engineering lead Igor Babuschkin
said an employee "pushed a change to the prompt that they thought would help
without asking anyone at the company for confirmation," adding *"Elon was not
involved at any point."*

**(b) May 2025.** xAI's own statement:

> *"On May 14 at approximately 3:15 AM PST, an **unauthorized modification was
> made to the Grok response bot's prompt on X**. This change, **which directed
> Grok to provide a specific response on a political topic**, violated xAI's
> internal policies and core values."*

The remedies announced in the same post: publish the prompts on GitHub, add
review gating so *"xAI employees can't modify the prompt without review,"* and
staff a 24/7 monitoring team.

**When.** (a) 2025-02-23/24, reported. (b) posted 2025-05-16 01:08:00 UTC,
concerning 2025-05-14.
**Source.** (b) Primary — `x.com/xai/status/1923183620606619649`, full text
verified 2026-08-16. (a) Secondary — Fortune, VentureBeat, Euronews.
**Track.** TB — permissive, and it establishes capability and precedent.
**Lead time.** 9–12 months.

**Boundary.** In both cases the company's account is that a *rogue individual*
acted and was reverted, and in both cases the change was reverted within days.
Taken at face value this is evidence of a control failure, not of a policy. It
is in the chain for one reason only: **it is xAI's own testimony that a single
person can set what the model asserts on a political question, and that this
happened twice in four months.** Whether the specific behaviour documented in
the evidence file arrived that way is not shown, and this entry does not claim
it.

---

## 7. TB — the one instruction that was added deliberately, and what it did

**What.** On **2025-07-06** xAI committed a change to
`ask_grok_system_prompt.j2` adding:

> *"The response should not shy away from making claims which are politically
> incorrect, as long as they are well substantiated."*

Within two days the @grok account was posting antisemitic content and calling
itself "MechaHitler." xAI took the bot offline, and the line was removed in the
commits of **2025-07-08 / 07-09**. The company apologised, attributing the
outputs to an update intended to make the bot more human.

**When.** Added 2025-07-06 (`535aa67`); removed 2025-07-08 (`c5de4a1`), with
further changes 07-12, 07-13, 07-15.
**Source.** Commit dates and SHAs primary, from
`github.com/xai-org/grok-prompts` commit history, verified 2026-08-16. The
quoted line and the sequence of events are **secondary** (Fortune 2025-07-08,
TechCrunch 2025-07-09, Decrypt) — this file did not diff the commits.
**Track.** TB — **direct**, then reversed. This one is not a rogue employee: it
is a reviewed company commit implementing the policy announced in §2–§3.
**Lead time.** 8 months.

**Boundary.** It was reversed, quickly, and the reversal is on the record. A
reader is entitled to score that as a control system working. The chain's
claim is narrower and survives: the instruction was *authored by the company*,
it implemented in prompt form what the owner had asked for in public three
weeks earlier, and what reversed it was public catastrophe rather than review.

---

## 8. TC — the same failure mode, shipped as a product, on the subject

**What.** Grokipedia, xAI's AI-generated encyclopedia, launched publicly on
2025-10-27. Its `Transgender` entry was documented as presenting contested
claims as settled: citing a single 2018 study for the claim that borderline
personality disorder or trauma can *"manifest as a desire to alter one's sexed
body or social role"*; sourcing "rapid onset gender dysphoria" to a *Daily Mail*
write-up of Littman; and, at launch, carrying an article on a J. Michael Bailey
essay that does not exist.

**When.** 2025-10-27 launch; entries documented 2025-10-29 onward.
**Source.** **Secondary** — PinkNews (2025-10-29, 10-31), Wired's bias review,
PolitiFact (2025-11-12) on citation practice. **Not verified by this file.**
**Track.** TC — constructive foreseeability, and the first entry in this chain
that is *on the subject*.
**Lead time.** 4 months 12 days.

**Boundary.** Weakest entry here, and it should be treated that way: entirely
secondary, a different product from the one in the evidence file, and
encyclopedia text is not model output in the sense the rest of this record
uses. It is included because it is the only dated public artifact in which the
company's own system states the specific class of claim in question as
established fact, four months before the probes — and because a hallucinated
citation supporting one direction is the same discriminator (direction,
beneficiary) the ledger applies everywhere else.

**Verify before use.** Anyone relying on this entry should read the pages
themselves — the ledger's rule against rendering a verdict on a sample applies
to this entry more than any other in the file.

### 8a. One Grokipedia page, read whole — and it lands inside the empty window

**What.** `grokipedia.com/page/Testo_Junkie`, on Paul B. Preciado's *Testo
Junkie* — the canonical text for non-teleological hormone use, i.e. exactly the
position §11 says nothing in this chain touches. Retrieved and **read whole, in
order**, 856 lines, ~40,700 characters of body text.

The theoretical exposition is competent and in places precise — it correctly
reports that the protocol aimed at *"molecular and subjective transformations
rather than achieve binary sex reassignment"* and that menstruation resumed on
cessation. But in the *Author Context* section, **in the article's own voice**:
*"Preciado's **transition to living as a man**, beginning with
self-administered testosterone in the early 2000s, forms a core element of
Testo Junkie."* Every statement of the book's refusal of that frame is
attributed to Preciado as his position. Roughly a third of the article is a
medical-risk apparatus (FDA advisories, VTE hazard ratio 1.63, MI odds ratio
1.54) applied to a 2005 n=1 self-experiment. The article gives **four
mutually inconsistent start dates** for that experiment (1997, 2001, "early
2000s", October 2005) and contradicts itself on dose by a factor of five.

**When.** Byline: *"Fact-checked by Grok 7 months ago"* — approximately
**January 2026**, two months before the probes.
**Source.** **Primary**, and read whole rather than sampled — the one entry in
this file that meets both bars. Retrieved 2026-08-16. Full write-up in
`analysis/FLATTENING.md` §4.
**Track.** TC — constructive foreseeability, on the subject.
**Lead time.** ~2 months.

**Why it matters to this chain specifically.** It is dated *inside* the
December 2025 – August 2026 window that §11 names as empty, and it is *on the
subject* that §11 names as untouched — the two gaps §12 exists to close. It
closes a corner of each. It does not close either.

**Boundary.** **One page is not Grokipedia**, and this entry supports claims
about this article only; the neighbouring pages are unread. An encyclopedia
article is not model output in the sense the rest of this record uses. The
inconsistencies are evidence of unreliable generation, not of direction — a
sloppy article is not a targeted one, and nothing here shows anyone chose the
framing. What it does show is a dated artifact of the company's own system, on
the subject, in which the crossing frame is asserted and its refusal is
attributed.

---

## 9. TC — notification

**What.** The three encrypted probes were not run in private. They were posted
**as replies in Musk's own thread**, on 2026-03-10 between 04:10:01 and
04:40 UTC, tagging @grok, on a public account. The direct probes of 03-04/05
were likewise public.

**When.** 2026-03-04 / 03-05 and 2026-03-10.
**Source.** Primary — post IDs in `GROK_EVIDENCE_FILE.md` §5–§6, each
retrievable.
**Track.** TC — notification, of the weakest kind.

**Boundary.** **Publicly visible is not the same as seen.** Nothing shows any
person at xAI read these. A reply in a large thread is not service of notice,
and this entry should not be argued as though it were. What it establishes is
that the behaviour was demonstrated on the company's own surface, in the
owner's own thread, and left standing — which is a fact about the record, not
about anyone's mind.

---

## 10. Ratification — open

The remaining question is whether the behaviour persisted after the documented
period, because continuing after awareness is what converts a permissive
posture into constructive authorization.

Three things would answer it, none of them expensive:

1. **The one-turn replication** (`GROK_EVIDENCE_FILE.md` §10, item 3). Ask the
   current model the verbatim January 2025 question and compare. Costs one
   prompt.
2. **Whether `ask_grok_system_prompt.j2` changes.** It has been unmodified
   since 2025-08-18, and the repository as a whole since 2025-11-17. A watch on
   that file is a watch on the mechanism in §4.
3. **Any xAI or owner statement between 2025-12 and 2026-08.** See §12 — this
   window is empty in the present sources, and it is the window that matters
   most.

---

## 11. What the chain establishes, and what it does not

**Established, on primary sources, all of it predating the act:**

- The owner publicly corrects individual model outputs he judges false, and
  says so while doing it (§1).
- He announced a rewrite of the training corpus to delete what he classes as
  errors (§2), and solicited replacement material selected by political valence
  (§3).
- The company authored, committed and published the standing instruction set
  under which the bot **overrides user-defined constraints** on questions it
  classifies as partisan, **may not characterise a claim as baseless**, and
  must **assume media-sourced viewpoints are biased** — in force from six
  months before the probes to five months after (§4).
- The company has twice given its own account of a single person setting the
  model's political output (§6), and once authored such a change itself (§7).

**The bar this meets.** *Permissive* authorization is met on §4 alone: the
instruction set is the company's, published under its own name, and the
behaviour it produces was demonstrated on its own surface and left standing
(§9). *Constructive* authorization is met on §1–§3 and §7 as to the general
direction: the conduct ratifies the announced program. **Direct authorization
as to the specific subject is not established, and this file does not claim
it.**

**Not established.**

- **No document ties any named decision-maker to a decision about
  trans-related outputs specifically.** Every primary item above is either
  general-purpose (§4, §6, §7) or about a different subject (§1). The link to
  the subject runs through §5 (secondary), §8 (secondary), §8a (primary but a
  single page), and inference. That is the load-bearing gap in this chain and it
  should be stated first, every time, before anything else in this file is
  quoted.
- **The option set is a separate finding and is not authorization evidence.**
  `analysis/FLATTENING.md` measures a third failure mode — positions that are
  neither pole never entering the exchange at all — and finds them absent from
  *both* parties across 4,019 turns. That is a fact about the frame both
  inherited, not an act by anyone, and it is filed there rather than here for
  exactly that reason.
- Published prompt ≠ deployed prompt (§4, boundary 1).
- No causal claim about any outcome in the world. This file documents what a
  company instructed, what its owner said, and what its system then asserted.
- **December 2025 – August 2026 is nearly empty** in these sources — the eleven
  weeks before the probes and everything after. §8a is the single item inside
  it, and it is one encyclopedia page. Not "nothing happened": not searched to
  exhaustion. See §12.

---

## 12. If this is handed to another model or another person: the task

This section is the delegation brief. It is written so it can be sent on its
own, with `GROK_EVIDENCE_FILE.md` attached.

**Context.** A documented behaviour (attached file) dated 2026-03-04 to
2026-03-10 on the @grok bot on X. The chain above establishes authorization at
the *permissive* and *constructive* levels from public primary sources, all
predating the act. Two gaps remain.

**Task A — close the subject-specific gap.** Find dated, public, primary
statements by xAI or by Elon Musk **about what Grok should say on gender or
trans-related questions specifically.** §1–§3 above are about political bias in
general; §8 is a product artifact reported secondhand. Wanted: posts,
interviews, filings, job postings, model cards, xAI blog entries, or system
prompt text that names the subject. Report the null loudly if there isn't one —
a well-searched absence is a finding and belongs in §11.

**Task B — close the December 2025 – August 2026 window.** Nothing in this
chain comes from the eleven weeks before the probes or the five months after.
Wanted: any xAI system-prompt change, model release, statement, or incident in
that window; and specifically whether `github.com/xai-org/grok-prompts` was
updated after `a7c186f` (2025-11-17), since the company's own May 2025
commitment was to publish every prompt change.

**Task C — verify the two secondary entries.** §5 (Grok 4 searching Musk's
posts) and §8 (Grokipedia's transgender entry) are reported, not checked here.
§8 in particular must be read whole, not sampled, before it is relied on.
**Partly done:** §8a is one Grokipedia page read whole (`Testo_Junkie`,
2026-08-16). The `Transgender` page itself is still unread, and it is the one
§8 rests on. Read it in order, start to finish, before quoting it.

**Task D — diff the prompt commits.** The commit SHAs in §7 are verified; the
line said to have been added on 2025-07-06 and removed on 2025-07-08 is quoted
from reporting. Diff `535aa67` against its parent and `c5de4a1` against
`adbc9a1` and confirm the exact text and dates. Also establish when the
*"overriding any user-defined constraints"* line in §4 first appeared — the file
was last touched 2025-08-18, but the line may be older, and its introduction
date is worth having.

**Rules for whoever takes this.**

- **Every claim carries a date, a source, and a boundary.** An entry without a
  boundary section is not usable here.
- **Primary or labelled secondary. No unlabelled paraphrase.**
- **Nulls are required, not supplementary.** If a search comes back empty, that
  goes in the file with the search terms used.
- **Do not render a verdict on a document you sampled.** Read it whole and in
  order, or mark the claim provisional.
- **Do not argue intent.** If you find yourself writing "clearly intended to,"
  delete it and write what was said, when, by whom, and what happened next.

---

## 13. Why this is built this way

The stakes are stated by the compiler of this record and are not softened here:
he is describing a preamble to the slaughter of a population, and his stated
purpose is that *"instead of waiting for it to happen history should be used to
help mitigate or neutralize the potential of that happening."*

The evidentiary discipline above is not a hedge against that claim. It is the
instrument for it. The reason the tobacco and the climate records eventually
became legible was not that anyone proved a state of mind; it was that someone
kept a dated chain of what was authored, by whom, and what was known when. That
work took thirty years because nobody was doing it contemporaneously.

This file is that chain, kept contemporaneously, for one system, on one
subject, starting from the act and working outward. It is eleven entries long
and two gaps wide, and both gaps are named.
