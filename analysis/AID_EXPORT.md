# AID_EXPORT — bulk-exporting the AI Dungeon library

`analysis/aid_export.py`. Built 2026-08-10 from Endorphin's handoff spec. This
note records what the spec got right, the one thing it got wrong, and the piece
of it that turned out not to be needed.

The NovelAI side of the archive is settled — 2,016 stories, `FINDINGS.md`. AI
Dungeon is the other half of the record and has no first-party bulk export.

## Usage

```
python3 analysis/aid_export.py --out ./exports          # whole library
python3 analysis/aid_export.py --only <shortId-or-URL>  # one item, smoke test
python3 analysis/aid_export.py --out ./exports --limit 5 --format both
```

The token is prompted on stdin and **never read from argv** — a Firebase ID
token is a live credential and argv lands in shell history. Get it from
DevTools → Application → IndexedDB → `firebaseLocalStorageDb` →
`firebaseLocalStorage` → the `firebase:authUser:*` key → `stsTokenManager.accessToken`.
It expires in roughly an hour. The run is resumable, so expiry costs a re-paste
and nothing else: `exports/manifest.json` records every completed item, and a
re-run skips them. Kill it mid-run deliberately once and you will see this work.

## The finding: validation runs before authentication

The spec listed one unknown — no verified query for "list everything I own" —
and budgeted a user-in-the-loop DevTools session to recover it by copying a
request out of the Network tab (§4 Step 0, *"do this FIRST"*).

That was not necessary, and the reason generalises. This API validates the
GraphQL document **before** it checks the Firebase token, and the two failures
are distinguishable without a credential:

| probe | HTTP | code |
|---|---|---|
| `{ zzzNotAField }` | 400 | `GRAPHQL_VALIDATION_FAILED` — *Cannot query field …* |
| `{ user { id } }` | 200 | `UNAUTHENTICATED` — *Not authorized [Firebase]* |

So an unauthenticated probe is a boolean oracle on "does this field exist", and
the server volunteers `Did you mean "adventure", "adventureState", …` on a miss,
which enumerates neighbours for free. Type names leak the same way — asking for
an object field without a selection set returns *Field "search" of type
`SearchResults!` must have a selection of subfields*. Required arguments
announce themselves, and a wrong literal type reports the expected one.

Introspection proper (`{ __schema { … } }`) **is** gated — it returns the
Firebase error, because `__schema` is a valid field. The oracle is the
validator, not introspection.

The whole enumeration path came out of that, with no token in play:

```
Query.user: User!                       # takes no arguments — this is the "me" query
  { id username email isMember createdAt profile{…} friends{…} settings }

Query.search(input: SearchInput!): SearchResults!

SearchInput   contentType: [String!]!   # the ONLY required field; "adventure" / "scenario"
              searchTerm sortOrder userId username tags contentRating timeRange : String
              limit offset : Int        # offset/limit paging, not cursors
              published following : Boolean

SearchResults { items: [SearchableContent!]!  total  hasMore }
```

`contentType`'s two values are lowercase `adventure` and `scenario`, confirmed
against the userscript's own comparisons rather than guessed.

## The correction: `SearchableContent` is not an interface

§1.4 of the spec offered the `CardSearchable` fragment as a hint, and that
fragment spreads `... on Adventure { actionCount … }` / `... on Scenario { … }`.
Reusing that shape against `search` fails validation outright:

```
Fragment cannot be spread here as objects of type "SearchableContent"
can never be of type "Adventure".
```

`SearchableContent` is a concrete object type carrying the union of both sets
**flat** — `actionCount` and `adventuresPlayed` sit side by side on it, and
either may be null. `CardSearchable` is real, but it is a fragment on a
different type (`Searchable`) used elsewhere in the app. Anyone extending the
enumeration should add fields flat and check them with the oracle first.

The full field list is in `SEARCH_FIELDS` in the script; all 29 were confirmed
individually.

## What the spec had right

Everything in §1, verified rather than assumed:

- `POST https://api.aidungeon.com/graphql`, raw query strings, no persisted-query
  hashes. Confirmed by direct probe.
- The `authorization: firebase <TOKEN>` header shape and the three header lines.
- **Both §1.3 queries validate verbatim against the live schema — no drift,
  nothing shed.** They were re-checked field-for-field on 2026-08-10 against the
  userscript source as well, which still carries them unchanged.
- The four alternate hosts, exposed as `--host`.

The `--host` values and both queries were re-extracted from the live userscript
rather than trusted from the spec's transcription; the only transcription slip
found was cosmetic (§1.4 drops `blockedAt`, `contentResponses` and `__typename`
from `CardSearchable`), and it does not matter because that fragment is not used.

## Deliberate departures

- **Stdlib only, no `requests`** (spec §3 allowed it). Matches `fetch_export.py`
  next door and keeps the tool runnable without a virtualenv.
- **The renderer sorts actions on `createdAt` rather than reversing the fetch
  order.** §5 flagged `actionWindow` desc/asc semantics as needing empirical
  confirmation on the first real run. Sorting is correct under either ordering,
  so the render does not depend on an answer. The fallback to `reversed()` only
  fires if some action lacks `createdAt`.
- **The plot-component mapping is not guessed.** §4 Step 5 was explicit about
  this. `memory`, `authorsNote` and `instructions` render under the labels AI
  Dungeon's UI uses. `details` and `gameState` — the two whose in-app labels are
  not established — render verbatim under *"Other plot fields (in-app labels
  unconfirmed)"* rather than being silently mislabelled. Read one real
  `raw.json`, then promote them into `PLOT_SECTIONS`.

## Still unverified — needs one authenticated run

Everything above is schema-level. These are runtime questions that a token
answers in about a minute, and the first one is the only one that could force a
change:

1. **Does `search` scoped to your own `userId` return unpublished/private
   adventures?** R1 requires it. The profile page in the web app lists your own
   private work, and this is the query behind it, so it should — but it is not
   proven. If it does not, the fallback is `published: false` as a second sweep,
   or the `user { … }` object, which has unexplored subfields (`profile`,
   `settings`, `friends`).
2. Whether items with `deletedAt` set come back at all. The tool keeps and flags
   them when they do (R1) and reports the count at the end.
3. Valid `sortOrder` values — a plain `String`, so the validator cannot tell us.
   Left unset, which takes the server default.
4. Real rate limits. Default pacing is 0.5s with 5/15/45s backoff on 429/5xx.
5. Whether `actionWindow` paging past a large offset behaves. Page size 2,000,
   `--page-size` to change it. The fetcher de-duplicates by action `id` across
   pages and stops on a page that adds nothing new, so a server that ignores
   `offset` degrades to "one page" instead of looping forever. A mismatch against
   `actionCount` is recorded in `raw.json` as `_action_count_mismatch` and
   printed, rather than passing silently.

## Testing

30 offline assertions cover the renderer (chronological ordering, undone/deleted
exclusion, action-type prefixes, plot-section labelling, story-card filtering,
front-matter quoting), slugging, the output layout, script extraction, nested
option trees, manifest resume semantics, and field-shedding. Option recursion is
tested against a deliberate `s1 → s2 → s1` cycle.

Four further assertions run against the live API with a deliberately invalid
token: each of the four queries, sent through the real client code path, comes
back `UNAUTHENTICATED` rather than `GRAPHQL_VALIDATION_FAILED` — which proves the
document parsed and validated server-side and that the auth path is wired
correctly. That is as far as testing goes without a credential.

## Not done (v2)

NovelAI-format conversion, re-import, other users' content, worlds, posts and the
social graph. Conversion is the interesting one: if these exports are ever to sit
alongside the NovelAI corpus in the same analysis, they need a shared block-level
shape, and AI Dungeon's action list is a flat sequence where NovelAI's is a tree
with the rejected branches still in it. That asymmetry is a finding in itself and
should be written up before any converter is designed — see `FINDINGS.md` on the
turn as the unit of analysis.
