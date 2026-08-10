# Usenet search log — Prodigy `YGXS04D` / `YGXS04B`, plus name key "Devon Gallegos"

Run 2026-08-10, against the brief in `SEARCH_BRIEF.md`. This file records what was
searched, what was found, and — mostly — what the archives do and do not hold. Per the
brief's §7, a zero is a coverage finding, not a conclusion about whether the person posted.

**Result in one line: no hit on either key, and two of the three unexplored leads turned
out to be blocked at the host rather than at this end.**

---

## 1. What was added to the search

The brief listed the account holder's real name as the second independent key but did not
have it. It is now known: **Devon Gallegos**. Every group below was greped for `Gallegos`
(surname alone, case-insensitive — catches "Devon Gallegos", "D. Gallegos", and any
household member sharing the surname) alongside the `YGXS04` stem.

The name is a **broader** key than the brief treats it as. The brief scopes it as a fallback
for a mangled ID. But a name search is not tied to Prodigy at all: it finds the person under
any provider — a later `@prodigy.net` name-style address, AOL, a school account — and it has
no 1993–1998 ceiling the way a Prodigy Classic member ID does. Where the Internet Archive
spool is thick (1999+), the name is the only key that can work.

---

## 2. Findings

### 2.0 Master table

Every group greped for both keys. `pcom` / `pnet` are line counts for `@prodigy.com` and
`@prodigy.net`.

| Group | msgs | msgs ≤1998 | `YGXS04` | `Gallegos` | pcom | pnet |
|---|---:|---:|---:|---:|---:|---:|
| `soc.religion.christian` | 125,331 | 49,694 | 0 | 0 | 283 | 315 |
| `soc.motss` | 289,313 | 192 | 0 | 2 false | 19 | 9,224 |
| `talk.religion.misc` | — | 161 | 0 | 10 false | 2 | 3,139 |
| `alt.politics.homosexuality` | 160,643 | 10 | 0 | 3 false | 0 | 1,237 |

**No genuine hit on either key in any group.** All 15 `Gallegos` matches are false positives,
and not one of them is a `From:` line:

- `soc.motss` (2): "Sen. Mario Gallegos Jr." — Texas state senator, in quoted news text.
- `alt.politics.homosexuality` (3): one quoted news sentence, "Gallegos who made promises to
  have it stop but the harassment allegedly…", repeated through three levels of quoting.
- `talk.religion.misc` (10): Las Vegas (New Mexico) Police Chief Tim Gallegos in an interview
  transcript, plus a "Veronica Lozada Gallegos" in a pasted address list.

This is the same failure mode the brief hit with `handelman`, and it is why every name hit
needs eyes on the `From:` line before it counts.

### 2.0.1 The archive is a `prodigy.net`-era spool — which is the wrong era for this target

The `pcom` / `pnet` columns above are the most useful thing this pass produced. The
relationship is inverted between the deep group and the shallow ones:

- `soc.religion.christian`, the one group with mid-90s depth: **283** `prodigy.com`, 315 `prodigy.net`.
- The three 1999+-heavy groups: **0, 2, 19** `prodigy.com` — against 1,237 / 3,139 / 9,224 `prodigy.net`.

Prodigy Classic member IDs are essentially absent from the Internet Archive's Usenet
collection except in the rare group that genuinely holds the mid-90s. The archive is
overwhelmingly a spool of the *later* Prodigy Internet service, whose addresses are
name-style and carry no member ID at all.

**Consequence: grepping further Internet Archive groups for `YGXS04` is close to futile
unless the group is first shown to have mid-90s depth.** The `@prodigy.com` line count is
itself the cheapest available proxy for that depth — it measures era and target population in
one number.

The name key is not subject to this, which is precisely why it was worth adding: a
`Gallegos` in a 1999+ spool would still be findable, under `dgallegos@prodigy.net` or any
other provider. It simply is not there.

### 2.1 `soc.religion.christian` — both keys zero, on a genuinely deep spool

Re-downloaded and re-greped, because the brief's pass ran the ID key only.

| | |
|---|---|
| Messages total | 125,331 |
| Messages 1993–1998 | 49,694 |
| `YGXS04` | **0** |
| `Gallegos` | **0** |
| `Devon` | 11, all false positives |
| `@prodigy.com` | 283 lines, 93 distinct IDs |

Year histogram reproduces the brief's numbers exactly (1,473 / 2,136 / 21,388 for
1994/1995/1996), confirming this is the same corpus the brief measured.

The 11 `Devon` hits are all noise: Devon in England (Exeter, Dartmoor, "Somerset, Devon and
Cornwall"), Devon Island in the Arctic, a `Devon Hill <dsbhill@shaw.ca>` from a later year,
and twice the typo "devontion". None is the target.

This is the strongest available negative. It is the one group in the searched set with
verified mid-90s depth **and** verified Prodigy Classic traffic, and neither key appears.

### 2.2 The `From:` format is confirmed, again

```
From: BSTE27A@prodigy.com (David Fuertsch)
From: YEKQ78C@prodigy.com (Sara Barr)
From: CBSG31A@prodigy.com (Valerie Southard)
```

Unrewritten ID, real name in parens, exactly as the brief states. A `From:` match would be
unambiguous.

### 2.3 Y-prefix accounts existed and posted — but the prefix does not date the account

`YGXS04` is a Y-prefix ID. Y-prefix IDs do appear in this spool:

- `YBXD10C@prodigy.com` (K pennington Lewis) — April 1996
- `YEKQ78C@prodigy.com` (Sara Barr) — December 1996
- `YCQT19A@prodigy.com` (Robert Perry) — quoted

`YGXS04` sits just after `YEKQ78` alphabetically, which suggested Prodigy issued IDs roughly
in sequence and that the target account was therefore late-1996 or later — which would have
narrowed the brief's 1993–1998 window considerably.

**That hypothesis was tested and it failed.** Extracting first-seen year for all 60 dated
Prodigy IDs in the group and bucketing by first letter gives a flat distribution: B, C, G, H,
J, L, N, P, R, V, Y, Z all bottom out at 1996; D, E, K, M, S, T, W, X all bottom out at 1995.
There is no monotonic relationship between prefix letter and first activity. Letter position
carries no date information at this resolution.

**Consequence: the brief's 1993–1998 window stands unnarrowed.** Do not use the prefix to
prioritise years.

### 2.4 The household-suffix model is confirmed — and the two suffixes need not share a surname

One stem in the group appears under two suffixes:

```
From: XBHN14A@prodigy.com (Marge Warner)
From: XBHN14B@prodigy.com (Tim Day)
```

Same household account, two suffix letters, **two different people with two different
surnames.**

This directly affects the name key. `YGXS04D` and `YGXS04B` are two members of one
household, and the Marge Warner / Tim Day case shows a household's members can carry
unrelated surnames. So:

- A `Gallegos` hit can be expected to identify **at most one** of the two suffixes.
- The other suffix may be posting under a surname that is not in this search at all.
- Conversely, a zero on `Gallegos` does not clear the *stem* — only the name.

If a second household surname is known, it is worth as much as the first and should be added.

---

## 3. Coverage findings on the unexplored leads

### 3.1 Tier 1 — Queer Digital History Project: **offline at the host**

`queerdigital.com` is reachable and the project is live, but its Transgender Usenet Archive —
the ~400,000-post, 1994–2013 corpus that is the actual prize — is down:

> "Due to technical and funding challenges, the Transgender Usenet Archive is currently
> unavailable. We hope to make it available again in the near future."

This is a host-side outage, not an environment limitation, so no amount of retrying from here
recovers it. The QDHP item catalogue that *is* up indexes communities and documents, not post
full text, so it cannot answer the question even while the Usenet archive is down. The
brief's recommendation — email Avery Dame-Griff — remains the live route, and is now the
*only* route to this corpus.

Note also that the six groups in that archive (`alt.transgendered`,
`soc.support.transgendered`, `alt.support.crossdressing`, `alt.fashion.crossdressing`,
`alt.support.srs`, `uk.support.crossdressing`) are a different subject area from the brief's
targets. Whether they are worth asking for depends on facts about the account holder that
this search does not establish.

### 3.2 Tier 2 — usenetarchives.com: still blocked, and the brief's diagnosis is confirmed

The brief guessed Cloudflare. Confirmed exactly, from response headers:

```
HTTP/2 403
cf-mitigated: challenge
server: cloudflare
```

The brief's proposed fix — use a real browser — was attempted. Chromium and Playwright are
both present in this environment. **It does not work here for an unrelated reason: this
container's browser has no outbound network at all.** Chromium returns
`net::ERR_CONNECTION_RESET` for every destination including `example.com` and `archive.org`,
with and without `--proxy-server` pointed at the agent proxy, so it never reaches Cloudflare
to be challenged in the first place.

So usenetarchives.com remains **untried**, not excluded. It needs a browser with working
egress — a human's own browser is sufficient. The two queries to run are
`YGXS04D@prodigy.com` and `YGXS04B@prodigy.com`, and now also `Gallegos`.

### 3.3 Archive.org full-text search is not available from here

`ia-fts.archive.org` is refused by the egress gateway (502 to CONNECT — policy denial). The
`advancedsearch.php` endpoint works but indexes item metadata only, not message text, so it
cannot find a string inside an mbox. Full-text search across the whole Usenet collection —
which would settle this far faster than group-by-group downloads — is therefore not reachable
from this container.

### 3.4 Other hosts probed

| Host | Result |
|---|---|
| `narkive.com` | root 200, but the search host fails DNS through the proxy |
| `groups.google.com` | 302; Usenet viewing discontinued 22 Feb 2024, per the brief |
| `novabbs.com` | no connection |
| `al.howardknight.net` | no connection |

Ordinary web search is useless for this target, as expected — Usenet archives are not indexed
by general search engines. Queries on both the full addresses and the name returned only
generic Prodigy and Usenet history pages.

---

## 4. Method notes for the next pass

Confirmed working, unchanged from the brief: histogram before grep, `curl -L` or the download
silently returns 0 bytes, `grep -a` throughout, delete each mbox after grepping.

### Cheap histogram screening does not work — and why

The brief's rule is "always pull the year histogram before running a full grep," but pulling
one currently costs a full 100–600 MB download, which is most of the expense the rule exists
to avoid. `probe.py` attempts the obvious fix: HTTP range-request the first few MB of the
zip, parse the local file header, and inflate the raw deflate stream to read `Date:` lines
without fetching the whole file. Mechanically it works — a 4 MB range inflates to ~15 MB of
mbox.

**It does not answer the question, because these mboxes are stored newest-first.** Validated
against the two groups whose full histograms are known: the head of `soc.religion.christian`
is 2007–2010, and the head of `soc.motss` is 2009–2012. Both files run back to the 1990s, but
only at the tail — and a deflate stream cannot be decompressed from the tail.

So there is no cheap screen for mid-90s depth. Either download the group in full, or use a
proxy signal such as the `@prodigy.com` count from a group already fetched. `probe.py` is
kept because the sort-order fact is worth knowing and is not documented anywhere obvious.

Added: `scan.sh <hierarchy-item> <group>` downloads, unzips, counts messages, prints the year
histogram, counts all five keys (`YGXS04`, `Gallegos`, `Devon Gallegos`, `@prodigy.com`,
`@prodigy.net`), dumps hits with line numbers, and cleans up. Roughly 30 GB of scratch is
available, and a 400–600 MB group takes several minutes to fetch.

A caution for the name key that the ID key did not have: `Gallegos` is a reasonably common
surname and will produce false positives, exactly as `handelman` did for the brief. Every hit
needs eyes on the `From:` line before it counts.
