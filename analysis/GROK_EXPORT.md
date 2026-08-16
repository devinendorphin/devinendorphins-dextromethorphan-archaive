# GROK_EXPORT — the fourth archive, and what it can and cannot answer

There are now four archives in this project and they are four different shapes.
`CLAUDE.md` sets the rule for adding one: *write up what each record can and
cannot answer before designing anything that joins them; the asymmetry is a
finding, not an obstacle to route around.* This is that write-up for the
standalone Grok export, done before anything was joined.

Run it with `analysis/grok_export.py`; the measurements are in `analysis/GROK.md`.

## The question it was supplied to answer

Endorphin, handing over the Drive link: *"this is separate from the Twitter data
that contains some rock conversations in it I think it might be the difference
between the gtok standalone and the rock that can be accessed on the Twitter I'm
not quite sure."*

**He is right.** `GROK.md` §1 runs it as a disconfirming test — if the two were
one record exported twice, turns would collide — and finds **zero** exact-length
coincidences inside a five-minute window, across a twelve-month overlap and
twelve shared calendar days. The closest any standalone turn comes to any X-side
turn is 81 seconds; the median separation is 7.5 days. Two records, no shared
turns.

That 81 seconds is worth keeping. The records are disjoint, but the *activity*
is not: he moves between the two surfaces inside the same minute. A gap in one
archive is not a gap in his attention.

## What arrived

A standalone Grok account export, delivered as a `.zip` of **148 MB / 653
files**, generated 2026-08-16. `grok_export.py` reads the zip as delivered; there
is no unpacking step.

| path | bytes | what it is |
|---|---:|---|
| `prod-grok-backend.json` | 41.9 MB | **the whole conversation record** |
| `prod-mc-asset-server/*/content` | ~106 MB | generated images and video, 636 files |
| `prod-mc-asset-server/*/previewdoc` | ~1 MB | 13 document previews |
| `prod-mc-auth-mgmt-api.json` | 2.7 KB | **account PII — never opened** |
| `prod-mc-billing.json` | 18 B | empty |

Everything the project needs is one file. The other 148 MB is media output and
account plumbing.

## What is deliberately not read

`prod-mc-auth-mgmt-api.json` carries the account's email, legal given and family
names, birth date, a linked Google address, NSFW-content flag, and a session
table with session ids, sign-in methods, user agents and Cloudflare session
metadata. **`grok_export.py` never opens it** — there is a `SKIP` list in the
script and the archive reader filters on it. Its field *names* were enumerated
once to write this paragraph; no value was read, recorded, or committed.

The same rule as the Twitter archive applies and for the same reason. The
public-repo decision (`sessions/LATEST.md`: *"i am prepared to be scraped"*) was
made about a corpus of the author's own fiction. It does not extend to an account
record. **Nothing in `data/` from this archive carries message text, conversation
titles, media prompts, or the account's user id** — that id appears throughout
the raw export, in asset URLs and on responses, and it is stripped on the way
out. `data/grok_meta.jsonl` is one row per turn holding conversation id, turn
index, response id, parent id, timestamp, sender, model, effort, thinking
duration and *lengths only*. `data/GROK_DAYS.tsv` is a date and a count.

Conversation text and titles go to `out/` via `--out`, which is gitignored, for
local analysis only. **Whether any of this text may be committed is Endorphin's
call and has not been asked.** These are single-party conversations — no
correspondent to protect, unlike the Twitter DMs — but several of them are about
his own life, his family and his health, and the titles alone are more disclosive
than anything the repo currently holds.

## The record, in detail

```json
{"conversations": [{
  "conversation": {
    "id": "…", "title": "…", "create_time": "2026-05-20T…Z",
    "modify_time": "…", "leaf_response_id": null,   // null on 143 of 145
    "starred": false, "system_prompt_name": "", "media_types": []
  },
  "responses": [{
    "response": {
      "_id": "…", "conversation_id": "…",
      "parent_response_id": "…",                    // ← the tree
      "sender": "human" | "assistant" | "ASSISTANT",
      "message": "…",
      "create_time":        {"$date": {"$numberLong": "1786839502246"}},
      "thinking_start_time": {"$date": …},          // 506 responses
      "thinking_end_time":   {"$date": …},          // 494 responses
      "model": "grok-4",                            // 1,069 of 1,201
      "metadata": {"request_metadata": {"effort": "high", "source": "Android"},
                   "usedCustomInstructions": true, "is_think_harder": true,
                   "memoryReferences": [...], "side_by_side_config": {...}},
      "web_search_results": [...], "file_attachments": [...],
      "steps": [...], "agent_thinking_traces": [...]
    }, "share_link": null}]}],
 "projects": [], "tasks": [],
 "media_posts": [{"id": "…", "original_prompt": "…", "media_type": "video",
                  "create_time": "…", "link": "https://grok.com/imagine/post/…"}]}
```

1,201 responses across 145 conversations, 2025-08-13 .. 2026-08-16, on 97
distinct days, plus 2,007 media generations (1,346 video, 661 image) over 66
days, 2025-08-12 .. 2026-05-04.

Four properties decide what it can be asked.

**1. It is a tree.** Every response but a conversation root carries
`parent_response_id`. 32 parents have more than one child — 21 re-rolls
(assistant siblings), 11 prompt edits (human siblings) — across 21
conversations. **This is chosen/rejected structure outside NovelAI**, which
`TW_EXPORT.md` said was impossible off that platform. That statement was true of
the Twitter/X export and does not generalise; it should be read as a fact about
that record, not about the world.

The catch is selection. `leaf_response_id` would name the kept branch outright
and is **null on 143 of 145 conversations**. The fallback is to ask which sibling
was continued, and it is only partial: of the 32 sets, exactly one branch grew in
15, none grew in 6, and **two or more grew in 11** — where nothing was rejected
at all, because both branches were kept. So: walk children *forward*. Do not run
`FINDINGS.md`'s `prevBlock`-backwards reachability method here.

And 32 sets is not a rejection dataset. It is proof the field exists plus a
handful of instances — enough to check whether a NovelAI finding reproduces,
never enough to found a new one.

**2. Every turn is stamped independently, and generation time is explicit.** The
X-side's defining limitation is gone: 0 of 587 human→assistant pairs share a
stamp (against 1,409 of 1,409 on X). Turnaround runs at a 22.2s median, and 494
responses carry an explicit `thinking_start_time`/`thinking_end_time` window at a
14.7s median. **Model latency is recoverable here and nowhere else in the
project** — `FINDINGS.md` §11 has wanted this since the beginning.

Caveat: the thinking window is the server's reasoning phase, not the whole
generation, and the human→assistant gap still contains reading and typing. The
two are separate instruments that happen to agree in shape, which is the check.

**3. The model is named, and there is one setting.** `model` is populated on
1,069 of 1,201 responses — `grok-4`, `grok-3`, `grok-4-auto`, `grok-420`,
`grok-420-computer-use-sa`, `grok-4-1-thinking-*`. **No other archive here
records which model answered**, and the NovelAI `model` field is known to record
what the client was set to rather than what wrote the text.

Better: **8 sibling sets span more than one model** — the same prompt, held fixed
by construction, answered by two versions. `CLAUDE.md` says this corpus cannot
benchmark models because settings moved with model choice; that objection does
not apply to a within-parent sibling pair. It is eight pairs, so it is a probe,
not a benchmark.

The only settings-like field is `effort` (high 399 / low 100 / auto 9). It is a
three-value switch, not a dial, so nothing resembling `analysis/sweeps.py` can
be run — there is no temperature to step.

**4. The model is reading things.** 220 responses carry web search results, 114
carry file attachments, 405 carry agent thinking traces, and `memoryReferences`
shows the platform injecting summaries of *other conversations* into a new one.
The context is not knowable from the transcript. **Nothing in this archive
supports a closed-context claim** — the kind `FINDINGS.md` can make about a
NovelAI story where Memory, Author's Note and the block sequence are the whole
input. This is the sharpest single difference from the NovelAI method and it is
easy to forget, because the transcript looks like a transcript.

## The four archives

| | NovelAI | AI Dungeon | Grok on X | **Grok standalone** |
|---|---|---|---|---|
| items | 2,016 stories | 888 adventures | 431 chats | **145 conversations** |
| turns / blocks | ~134,000 blocks | flat `actionWindow` | 2,818 | **1,201** |
| spans | 2021-06 .. 2026-07 | 2020-12 .. | 2024-12 .. 2026-07 | **2025-08 .. 2026-08** |
| branch structure | full undo tree | none (`undoneAt` only) | none | **parent pointers** |
| rejected generations | yes | partial | no | **32 sibling sets** |
| which branch was kept | `currentBlock` | — | — | **null on 143/145** |
| sampler settings | full, per block | none | none | **`effort`, 3 values** |
| model identity | client field, unreliable | none | none | **named, 89%** |
| timestamps | none per block | per action | one per *exchange* | **one per turn** |
| model latency | no | no | no (zero by construction) | **yes, two ways** |
| closed context | yes | yes | no | **no — search, files, memory** |
| media | none | none | none | **2,007 generations** |

Read down the last column: it is the only archive that is strong on the two axes
NovelAI is strong on *and* has a clock, and the only one where the context is
open. Read across, and the point `CLAUDE.md` keeps making holds a fourth time —
**four archives, four practices**, and 1,201 turns of argument and utility is not
more of a 134,000-block fiction corpus.

## What not to do with it

- **Do not add it to the X-side Grok count.** §1 is the evidence; they are
  disjoint records of different practices.
- **Do not treat the 32 sibling sets as a selection corpus.** Check reproduction,
  found nothing.
- **Do not read a NovelAI-style closed-context claim off any of it.** Search
  results, attachments and cross-conversation memory are in the input.
- **Do not use `effort` as a temperature analogue.** Three values, no dial.
- **Do not benchmark models on it beyond the eight matched sibling pairs**, and
  say "eight pairs" whenever you cite them.
- **Do not commit text, titles or the user id** without asking Endorphin first.
