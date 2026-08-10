# 2026-08-10 — The AI Dungeon transfer

Endorphin opened with a handoff spec for a bulk exporter and the words *"here is a spec for
a tool that helps me extract my AI Dungeon text generations. check it out!"* By the end
**888 adventures and 169 scenarios — 1,057 items — were on his disk.** The AI Dungeon
transfer, named in `LATEST.md` as one of the two things blocking a release, is done as an
extraction. It is not yet safe, and it is not yet analysed.

Nothing in this session touched the NovelAI corpus, `FINDINGS.md`, or `READINGS.md`.

## What was built

`analysis/aid_export.py` (~1,200 lines, stdlib only), `analysis/test_aid_export.py`
(107 assertions), `analysis/AID_EXPORT.md` (the schema findings),
`analysis/AID_RUNBOOK.md` (the step-by-step). `.gitignore` gained `exports/` and the
token files. Branch `claude/ai-dungeon-text-extraction-th0xtm`, ten commits, pushed. No PR
opened — not asked for.

Modes: `--doctor` (reachability, no token), `--whoami`, `--probe-search`, `--rerender`,
`--verify`, plus the export itself. `--token-file` / `--token-stdin` / `--save-token` for
credentials. Resumable through `exports/manifest.json`.

## The finding worth carrying: validation runs before authentication

The spec's §4 named one unknown — no verified query for "list everything I own" — and
budgeted a user-in-the-loop DevTools session to recover it by copying a request out of the
Network tab. *"do this FIRST."* It was not necessary, and the reason generalises past this
API.

`api.aidungeon.com/graphql` validates the GraphQL document **before** it checks the
Firebase token, and the two failures are distinguishable with no credential at all:

```
{ zzzNotAField }  -> HTTP 400  GRAPHQL_VALIDATION_FAILED  'Cannot query field ...'
{ user { id } }   -> HTTP 200  UNAUTHENTICATED            'Not authorized [Firebase]'
```

That is a boolean oracle on "does this field exist", and the server volunteers
`Did you mean "adventure", "adventureState", …` on a miss. Type names leak the same way
(asking for an object field without a selection set names its type), required arguments
announce themselves, and a wrong literal type reports the expected one. Introspection
proper (`{ __schema { … } }`) **is** gated — `__schema` is a valid field, so it hits auth.
The oracle is the validator, not introspection.

The whole enumeration path came out of that before a token existed:

```
Query.user: User!                    # no arguments — this IS the "me" query
Query.search(input: SearchInput!): SearchResults!
SearchInput   contentType: [String!]!   # only required field; "adventure" / "scenario"
              searchTerm sortOrder userId username tags contentRating timeRange : String
              limit offset : Int        # offset/limit paging, not cursors
              published following : Boolean
SearchResults { items: [SearchableContent!]!  total  hasMore }
```

**Reusable elsewhere.** Any GraphQL service that validates before authorising can be mapped
this way. Worth remembering the next time a platform has no export.

## Four things the spec asserted that his data overturned

The spec said §1 was verified and to *"not re-verify unless something fails"*. Re-verifying
it anyway cost four requests and confirmed it: endpoint live, header shape right, and both
per-item queries validate **verbatim** against the live schema, no drift. The userscript it
cites still carries them unchanged. So the spec's facts held. Its *inferences* did not:

1. **`SearchableContent` is a concrete object type, not an interface.** §1.4 offered the
   `CardSearchable` fragment as a hint, and that fragment spreads `... on Adventure`.
   Doing that against `search` is rejected outright — *"objects of type SearchableContent
   can never be of type Adventure."* The adventure- and scenario-only fields are flat on
   the one type; `actionCount` and `adventuresPlayed` sit side by side. Caught by the
   oracle before any token existed.
2. **`actionWindow` returns oldest-first despite `desc: true`.** §5 flagged the ordering as
   needing empirical confirmation and §3 prescribed `reverse()` in the renderer. The first
   real export showed `first ts 22:52` earlier than `last ts 23:00`. **A `reverse()` would
   have inverted all 888 stories.** The renderer sorts on `createdAt` instead, so it was
   correct before the answer was known — the one place where refusing to follow the spec
   paid off directly.
3. **The action text carries its own formatting.** §3 prescribed rendering the action
   `type` as a `> do ...` / `> say "..."` prefix. The fragment dump killed it:

   ```
   0 start     starts='{This is'   ends='colors, '
   1 continue  starts=' you see'   ends='me time.'
   6 say       starts='\n> You s'  ends='rsera."\n'
   ```

   `continue` fragments open with a space and resume mid-sentence; `say` arrives already
   carrying `\n> `. The story is a **literal concatenation**. The first renderer stripped
   each fragment and joined with blank lines, which is what Endorphin saw as *"the lines
   are a bit janky to each other, i dunno know what that might be about. could be viewing
   it from an old computer."* It was not his computer.
4. **`details` is a nested object, not a string.** §1.3 lists it among flat fields. It is
   `{instructions: {type, custom, scenario}, storySummary, storyCardInstructions,
   storyCardStoryInformation}`, and on the sampled adventure the top-level `memory`,
   `authorsNote` and `instructions` were **all empty** — the plot components live inside
   `details`. The key names are now certain; every value in the sample was empty, so the
   headings follow the names rather than observed content. `gameState` was null and stays
   unidentified.

The spec's §4 Step 5 said explicitly not to guess this mapping. Honouring that — rendering
`details` verbatim under *"in-app labels unconfirmed"* rather than mislabelling it — is
what made the real shape legible the moment one response arrived.

## Where Claude was wrong

Recorded because the log's value is in these, not the successes.

- **The cap that wasn't.** The first `--limit 5` run printed `adventure: 100 reported` and
  `scenario: 100 reported`. Two identical round numbers read as a server-side cap and the
  session stopped to build `--probe-search`. It was not a cap: `total` equals `len(items)`
  in every response — **it reports the page, not the collection** — and `--limit 5` had
  already satisfied the stop condition after page one. The hardening was the right change
  for the wrong reason and stays. The probe was still worth its cost: driving the pager
  against the measured 888/169 shape immediately found a `NameError` (`fresh` read in the
  paging loop, only ever assigned in `fetch_adventure`) that **would have crashed any
  enumeration reaching a second page.** Nothing had reached one.
- **`Install Certificates.command` on a Homebrew Python.** Diagnosed the TLS failure
  correctly, prescribed the python.org fix, and zsh answered `no matches found`. Worse,
  the fallback offered — *"or, equivalently, pip install certifi"* — was not equivalent to
  anything, because stdlib urllib never consults certifi unless handed the bundle. Fixed
  by making the tool ask for it.
- **`brew install ca-certificates` cost him 33 minutes.** Recommended before checking the
  OS version. He is on macOS 10.15, which Homebrew dropped; the command pulled in a `git`
  rebuild and compiled cmake from source before failing on an unrelated test. It was also
  a no-op — *"already installed and up-to-date."* What actually fixed the connection was
  the code change; certifi had been on his machine the whole time. The runbook now leads
  with certifi and warns against brew on macOS 12 or older.
- **`copy()` inside an async callback.** The console snippet threw
  `copy is not defined`. Chrome's command-line API helpers exist only in the top-level
  console evaluation; the IndexedDB `onsuccess` fires after it returns.
- **`< ~/Downloads/aid_token.txt`** after having told him to delete that exact file, and
  when Chrome renames repeat downloads anyway. *"your second command has a damn < that
  screws it up!"* — correct. `--token-file` with glob support now removes the redirect.
- **`--out./exports`** — a missing space in a command handed to him ready to paste.
- **`--probe-search` referenced `client` three lines before it was constructed.** Shipped
  broken. 96 tests at the time and **not one went through `main()`** — the wiring between
  a flag and its branch had zero coverage, which is exactly where a late-added mode gets
  attached, and three of the four modes were added that day. Now one test per mode,
  verified real by re-breaking a scratch copy.

## Endorphin's words this session

The UX complaints are the primary source here — each one located a real defect:

- *"ok please remember i'm a noob, you need to step by step this for me so i don't fuck it
  up"* — produced `AID_RUNBOOK.md`, `--whoami`, `--doctor`, and the token-paste salvage.
- *"that is so confusing"* — on being handed three command variants with mid-message
  corrections. Fair. The reply after it was four numbered steps and nothing else.
- *"oh my God this is so f****** frustrating every time I try to copy the token it copies a
  different part of it that what that makes no sense"* — **this is the DevTools IndexedDB
  viewer, not user error.** It copies whichever cell it decides you meant, silently, and a
  wrong grab is indistinguishable from a right one until the request fails. Fixed by
  reading the database directly from the Console and downloading the token as a file.
- *"the lines are a bit janky to each other"* — the concatenation bug, above. He attributed
  it to his own old machine. It was the renderer.
- *"much better"* — after `--rerender`.

**The pattern holds from the standing note.** Every one of his corrections this session was
right against Claude's written claim, and three of them (the janky lines, the token copy,
the `<`) were diagnoses of defects Claude had shipped and not noticed. Take them as
evidence.

## Open, and honest about it

- **The export exists in exactly one place.** `exports/` is gitignored — correctly; the
  repo is public and this is raw personal archive — so 1,057 items live only on his iMac,
  a machine on macOS 10.15 that Homebrew has already given up on. **This is the most urgent
  thing in the repo.** See LATEST.
- **Whether `search` returned unpublished/private work is still not proven.** R1 requires
  it. 888 is large enough that it plainly is not returning only published items, but
  nothing checked `published: false` explicitly. If a private adventure is missing, nothing
  in the output would say so.
- **The renders have been spot-checked on one adventure**, by Endorphin, against the app.
  §6 of the spec asks for that; it has been done once, not systematically.
- **Nothing is analysed.** The AI Dungeon material has not been read, counted, or joined to
  the NovelAI corpus in any way. See the note below on why that join is not trivial.
- **No disagreement of substance was opened this session.** The collaboration disagreement
  and everything in `READINGS.md` sat untouched. Nothing here bears on them.

## What this unlocks, and one caution

`LATEST.md` records a **pre-NovelAI layer**: block 1 of the Pynchon × Tingle story is a
pasted **AI Dungeon** listing for *Dr. Knubble And The Fangs Of The Love Sharks*, `Created:
Dec 7th 2020 / Actions: 76`, and `Doctor Knubbins and the Fins of the Love Sharks (copy)`
survives in the NovelAI corpus as its own story. **That adventure may now be in hand in its
original form.** Worth searching the 888 for it before anything else — it would date the
archive's start from a primary source rather than a pasted screenshot, and both `README.md`
("March 2023 to July 2026") and `CLAUDE.md` ("2021–2026") are already flagged as needing
correction on exactly this point.

**The caution, and it is a real one.** The two corpora are not the same shape. NovelAI's
export preserves the full undo tree — every rejected generation is still in it, next to the
one that was kept, next to the settings that produced both. That is the entire basis of
`FINDINGS.md`'s method. **AI Dungeon's `actionWindow` is a flat sequence.** There is an
`undoneAt` field, so *some* rejection is recoverable, but there is no branch structure, no
`prevBlock` to walk, and no per-action sampler settings at all. Anything in `FINDINGS.md`
that depends on chosen/rejected pairs, on branch reachability, or on settings **cannot be
computed on the AI Dungeon side.** Do not design a converter before establishing what the
AI Dungeon record can and cannot answer — the asymmetry is itself a finding and should be
written up first. This is the same failure the standing notes warn about, one platform
over: the metric that measures the tool rather than the author.
