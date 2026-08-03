# LATEST — devinendorphins-dextromethorphan-archaive

Last session: **2026-08-03**, `sessions/2026-08-03-nai-corpus-first-analysis.md`
Branch: `claude/text-generation-corpus-3rtnwn` (15 commits, pushed, no PR opened)

## State

- **Register: settled.** Research corpus, formal/evidentiary. Not
  harm-reduction — the README says so explicitly, and `CLAUDE.md` was rewritten
  to retire the seed framing and the proposed consolidation with
  `harm-reduction-outreach` / `hookup-hygiene`.
- `FINDINGS.md` — **stable.** 14 sections under the turn-taking frame. Read
  this first.
- `CASE_STUDY.md` — **stable.** The Utah HB 249 press conference, traced in full.
- `analysis/*.py` — **stable.** 16 scripts, all reproducible from the Drive
  export. `register.py` and `erato.py` need `wordfreq`; `learnable.py` needs
  `scikit-learn`.
- `analysis/*.md` — **generated.** Regenerate, do not hand-edit.
- `data/` — **stable.** Settings metadata only, no prose committed.
- Corpus (~1 GB) and `blocks.jsonl` (524 MB) — **not in git, by design.**
  Refetch with `analysis/fetch_export.py <json-folder-id>`.
- The Drive `text/` half — **untouched.** JSON supersedes it.

## Top priorities for next session

1. **Read the corpus as writing.** Sixteen scripts in, there has been *no*
   content analysis at all — nothing characterises what the stories are about
   or reads them as text. That is now the largest unexplored surface, and the
   one an outside reader would expect a "research corpus" to have. It needs a
   scope decision from Endorphin, since it means engaging the material rather
   than its structure.
2. **Separate compulsion from momentum** (§1c). The biggest open methodological
   hole: a short `max_length` cutting generations mid-sentence would *compel*
   the next one, manufacturing runs that look like momentum. `max_length` is
   per-story, so the clean contrast needs stories where it was large enough that
   generations rarely got cut — check whether enough exist.
3. **Send `data/FAILED_STORIES.txt` to NovelAI support.** 483 stories will not
   decrypt, clustered hard from 2025-10. Needs Endorphin — and needs him to say
   whether anything happened that month (client switch, subscription change,
   migration). The schema/roster/sampler evidence favours a client change, but
   the causal link to the encryption failures is still circumstantial.
4. **Identify the streamed sessions.** No stream markers exist in the data.
   Timestamp clustering against the channel's schedule would be the way in, if
   those dates exist somewhere. Endorphin said he would "talk about later"
   regarding the later channel period being less stream-driven.

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
  *how* it worked, not on what it was like from inside.
- **Do not open a PR unless asked.** Fifteen commits are pushed to the branch
  and no PR exists; that was deliberate.
