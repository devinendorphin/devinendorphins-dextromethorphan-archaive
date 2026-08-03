# LATEST — devinendorphins-dextromethorphan-archaive

Last session: **2026-08-03**, `sessions/2026-08-03-nai-corpus-first-analysis.md`
Branch: `claude/text-generation-corpus-3rtnwn` (10 commits, pushed, no PR opened)

## State

- **Register: settled.** Research corpus, formal/evidentiary. Not
  harm-reduction — the README says so explicitly. The `CLAUDE.md` note about
  consolidating with `harm-reduction-outreach` / `hookup-hygiene` is wrong for
  this repo.
- `FINDINGS.md` — **stable.** 13 sections, rewritten from the top under the
  turn-taking frame. Read this first.
- `CASE_STUDY.md` — **stable.** The Utah HB 249 press conference, traced in full.
- `analysis/*.py` — **stable.** 12 scripts, all reproducible from the Drive
  export. `register.py` and `erato.py` need `wordfreq`; `learnable.py` needs
  `scikit-learn`.
- `analysis/*.md` — **generated.** Regenerate, do not hand-edit.
- `data/` — **stable.** Settings metadata only, no prose committed.
- Corpus (~1 GB) and `blocks.jsonl` (524 MB) — **not in git, by design.**
  Refetch with `analysis/fetch_export.py <json-folder-id>`.
- The Drive `text/` half — **untouched.** JSON supersedes it.

## Top 3 for next session

1. **What Endorphin writes when they take the turn.** 6,944 cases where the
   model was rewound and a human continuation written from the identical
   context. Paired human/model sample from matched prompts, and it survives the
   duplication problem because the human side is what varies. It is also the
   only route to the question left open in the disagreement below — whether the
   exchange at high temperature looks like uptake rather than correction.
2. **Why a handoff works.** A bare `Name:` is taken up in that voice 89.7% of
   the time on no content at all. Is that the model tracking the scene, or the
   sheer strength of the `Name:` convention in its training data? Answerable:
   compare uptake for names established earlier in the session against names
   appearing for the first time. This is the sharpest open question the frame
   raises.
3. **Send `data/FAILED_STORIES.txt` to NovelAI support.** 483 stories will not
   decrypt, clustered hard from 2025-10. Needs Endorphin to do it — and to say
   whether anything happened that month (client switch, subscription change,
   migration), because the causal link is still circumstantial.

## Standing notes

- **Run the control that should fail before believing the one that succeeded.**
  Four times this session a headline number turned out to measure the tool
  rather than the author: the text editor's rewrite (`removedFragments`, bounded
  at exactly 0.5), the habit of duplicating stories (story-level splits →
  0.950), `max_length` masquerading as an effect of phrasing, and a disabled
  sampler read as a live setting (Erato temperature). Each time the diagnostic
  was a control matching or beating the treatment. This corpus punishes the
  obvious metric.
- **Never group by story id in this corpus.** Duplicating a story in NovelAI
  copies its whole branch history, so the same text lives under many story ids.
  Group by connected components of shared text.
- **`removedFragments` is not a rejection measure.** Use branch reachability —
  walk `prevBlock` back from `currentBlock`.
- **This corpus cannot benchmark models.** Settings moved with model choice
  because Endorphin adapted them to each model. Anything model-comparative needs
  within-model matched-setting slices, and most are too thin.
- **Much of the generation was performed live on stream with TTS reading the
  output**, concentrated in the early and middle part of the channel's history.
  Endorphin said they would "talk about later" — the later part is less so. This
  is load-bearing context for anything about pacing, speed of decision, or
  abandonment. Do not read fast decisions as editorial deliberation.
- **The unit is the turn, not the passage.** The human move following a
  generation is a cue (median 55 characters), not an edit. Do not ask what made
  a generation good enough to keep — four passes died on that question.
- **Endorphin works from a phone and often dictates while walking.** Expect
  speech-to-text artifacts; mark guessed corrections `[?original→guess]`. Their
  corrections this session were repeatedly right against Claude's written
  claims — take them seriously as evidence, not as anecdote.
- **Do not open a PR unless asked.** Ten commits are pushed to the branch and no
  PR exists; that was deliberate.
