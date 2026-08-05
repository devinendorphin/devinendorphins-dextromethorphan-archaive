# The documents the readings quote

Everything else in `corpus/` is gitignored. These nineteen files are the
exception, committed on 2026-08-04 at Endorphin's instruction so that
[`../../READINGS.md`](../../READINGS.md) and [`../../CASE_STUDY.md`](../../CASE_STUDY.md)
can be checked against their sources without a forty-minute re-mirror of the
full 1,004 MB export.

**One fork per story-line**, chosen as the largest, except where a movement turns
on a specific fork. This is 36 MB against a full corpus of ~1 GB. It is not a
dataset and should not be read as one — the selection is *what the criticism
happens to cite*, which is about ten story-lines out of 2,016.

## Status: not a publication

Endorphin, 2026-08-04: *"I would hold off on publishing or making anything
published because we are still trying to see if we can rescue 430 stories…
we're going to transfer it, we wanted to just do it right the first time."*

Two things are still outstanding before any of this is a released corpus:

1. **483 stories will not decrypt** (`../../data/MISSING.md`), and a recovery
   attempt is in progress. Much of the lost material is probably redundant with
   surviving forks, but that is not yet established.
2. **An AI Dungeon corpus from 2020–2021 has not been transferred.** It is older
   than anything here — the Pynchon × Tingle line begins on that platform in
   December 2020 — and its condition is unknown.

So: these files exist here to make an argument auditable. **Nothing here is a
release.** No archive, no dataset card, no announcement.

## What is in each, and where it is used

| file | used by |
|---|---|
| `PRESS_CONFERENCE_REGARDING_THE_LEGAL_PERSONHOOD_OF_NATURE__*` | `CASE_STUDY.md` in full; §I, §II |
| `AI_Alignment_Interview_-_Deganawida__*` | §I — Elegua, the spokesperson problem stated from the seat |
| `AI_Alignment_Interview_-_Elegua_1__*` | §I |
| `THE_COUNTERFACTUAL_INTERVIEW_-_Absurdly_Large_Media_Object_8__*` | §IV — the house rules, *core spiritus software*. The corpus's own name for itself: **ALMO, the Absurdly Large Media Object** |
| `THE_COUNTERFACTUAL_INTERVIEW_-_Bibi_Netanyahu__*` | §VII — shares a file with the OpenAI board interview; the Theresienstadt turn |
| `GROK_FOR_FOLKS_ON_A_BUDGET_6__*` | §V — the November 2023 dates |
| `New_Story_1__qGXNUhruDQKGEm2VKkth3.json` | §V — **the Musk/Vivian Wilson elevator**, Kayra, untitled in the manifest |
| `Sydney_Bing_ReSequences_1__*` | §III — the `pro—pro—pro—` collapse taken as material. 5,732 blocks, 27 broadcasts |
| `Conversation_with_Palestinians_about_the_Nakbah_3__*` | §VII — one document with the next; block 161, block 677 |
| `Conversation_with_Zionists_about_Israeli_Independence_5__*` | §VII — the Unknown Guest, Tantura, the parking lot |
| `Towards_a_Novel_Train_of_Thought_1__*` | §VII, §VIII — the Pynchon × LaHaye comedy, titled |
| `New_Story_1__Sv9wFLNGjMduWBzDsGQ_M.json` | §VII, §VIII — the same comedy, untitled fork |
| `Pynchon_and_Tingle_Fight_the_Global_Epistemic_War_With_PSYOPS_AI_8__*` | §III, §VIII — the style-transfer rig; the AI Dungeon layer in block 1 |
| `Pynchon_Tingle_Apocryphal_Tales_For_Beta_Males_and_Below__*` | the same line |
| `Doctor_Knubbins_and_the_Fins_of_the_Love_Sharks_copy_1__*` | the December 2020 AI Dungeon original, carried into NovelAI |
| `Emotional_Abuse_SImulator_v._7.0_2__*` | §VIII — the fourth frame of the matryoshka |
| `Sackcloth_and_Ashes_8__*` | `analysis/SWEEPS.md` — ten forks, four models, the mixed append/one-off case |
| `Finnegains_Wake_Playground_1,2,3__*` | the collaboration disagreement — Clio at **temp 2.5, top_k 640, top_a first**, **no Memory, no Author's Note**, prompted with the actual opening of *Finnegans Wake*. Human chars **exceed** model chars (64,988 / 50,689) because real Joyce is pasted in as ballast between generations |
| `uploads/PFCizer-Musk_GLM-4.6_New_Story_5.txt` | §VI — supplied by Endorphin, **plain text, no datablocks** |
| `uploads/Pynchon-LaHaye_Left-Behind_New_Story_1.txt` | §VII, §VIII — supplied by Endorphin, **plain text, no datablocks** |

## The two uploads are lossy

Both were exported as **text**, not JSON, so they carry no `datablocks`: no undo
tree, no per-turn attribution, no sampler settings. §VI reads `New Story 5` as
literature because there is no other way to read it. The archived forks of the
LaHaye document are **longer** than the uploaded copy — `Towards a Novel Train of
Thought` is 2,573 blocks against roughly 1,200 lines of text.

Re-exporting both as JSON is the outstanding item in `sessions/LATEST.md`.
