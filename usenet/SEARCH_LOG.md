# Usenet search log — Prodigy `YGXS04D` / `YGXS04B`, plus name key "Devon Gallegos"

Run 2026-08-10, against the brief in `SEARCH_BRIEF.md`. This file records what was searched,
what was found, and — mostly — what the archives do and do not hold. Per the brief's §7, a
zero is a coverage finding, not a conclusion about whether the person posted.

**Result in one line: nine groups, ~320,000 messages from the 1990–1998 window, ~1,425
Prodigy Classic address lines, and no genuine hit on either key.**

The negatives are worth less than the four things the pass established along the way, so
those are stated first.

---

## 1. What was added to the search

The brief listed the account holder's real name as the second independent key but did not
have it. It is now known: **Devon Gallegos**. Every group below was greped for `Gallegos`
(surname alone, case-insensitive — catches "Devon Gallegos", "D. Gallegos", and any household
member sharing the surname) alongside the `YGXS04` stem.

The name is a **broader** key than the brief treats it as. The brief scopes it as a fallback
for a mangled ID. But a name search is not tied to Prodigy at all: it finds the person under
any provider — a later `@prodigy.net` name-style address, AOL, a school account — and it has
no 1993–1998 ceiling the way a Prodigy Classic member ID does. Where the archive is thick
(1999+), the name is the only key that can work.

---

## 2. Four findings that change how the next pass should be run

### 2.1 The brief's coverage trap is real but over-generalized — the frontier is much larger

The brief states the Internet Archive collection is "overwhelmingly a 1999-and-later spool for
most hierarchies," with `soc.religion.christian` as "the exception found so far," and advises
skipping any group with fewer than ~1,000 messages in 1995–1998.

Applied literally that rule discards most of what turned out to be the best material. Of nine
groups measured, **six have genuine mid-90s depth**, not one:

| Group | msgs ≤1998 | `@prodigy.com` |
|---|---:|---:|
| `alt.homosexual` | **123,102** | **626** |
| `soc.religion.christian.bible-study` | 58,882 | 293 |
| `soc.religion.christian` | 49,694 | 283 |
| `soc.women.lesbian-and-bi` | 48,036 | 143 |
| `soc.bi` | 24,951 | 27 |
| `soc.support.transgendered` | 15,414 | 32 |
| `soc.motss` | 199 | 19 |
| `talk.religion.misc` | 162 | 2 |
| `alt.politics.homosexuality` | 10 | 0 |

`alt.homosexual` is the sharpest correction. It is an `alt.*` group — the hierarchy the brief
found thinnest — and it holds more mid-90s traffic and more Prodigy Classic posters than any
other group scanned, including 5,634 messages in 1993 and 12,004 in 1994.

The brief's generalization came from an unlucky sample. Three of its four groups
(`soc.motss`, `talk.religion.misc`, `alt.politics.homosexuality`) are the three thinnest in
the table above. `soc.motss` in particular is anomalously bad — 199 messages before 1999
against 27,971 in 1999 alone — and it happened to be the group the coverage rule was
generalized from.

**Coverage varies per group by three orders of magnitude and must be measured per group.
Do not infer a hierarchy's depth from a sibling.**

### 2.2 The archive is a `prodigy.net`-era spool, and `@prodigy.com` count is the cheapest coverage probe

`prodigy.com` line counts track mid-90s depth almost perfectly across the table above, and
invert against `prodigy.net`:

- Deep groups: 626 / 293 / 283 / 143 `prodigy.com`.
- Thin groups: 19 / 2 / 0 `prodigy.com` — against 9,224 / 3,139 / 1,237 `prodigy.net`.

Prodigy Classic member IDs are near-absent from this collection except where a group
genuinely holds the mid-90s; the bulk of it is the later Prodigy Internet service, whose
addresses are name-style and carry no member ID at all.

So `@prodigy.com` is a single number that measures era and target population at once. For any
group already fetched, it says immediately whether the group could ever have held this target.
The name key is not subject to this limit, which is exactly why it was worth adding.

### 2.3 Prodigy ID prefix letters carry no date information

`YGXS04` is a Y-prefix ID, and Y-prefix IDs do appear in the mid-90s spool —
`YBXD10C@prodigy.com` (K pennington Lewis, April 1996), `YEKQ78C@prodigy.com` (Sara Barr,
December 1996), `YCQT19A@prodigy.com` (Robert Perry). Since `YGXS04` sits just after `YEKQ78`
alphabetically, this suggested IDs were issued in rough sequence and the target account was
therefore late-1996 or later — which would have narrowed the brief's window considerably.

**The hypothesis was tested and it failed.** First-seen year for all 60 dated Prodigy IDs in
`soc.religion.christian`, bucketed by first letter, is flat: B, C, G, H, J, L, N, P, R, V, Y,
Z all bottom out at 1996; D, E, K, M, S, T, W, X all bottom out at 1995. No monotonic
relationship between letter and first activity.

**Consequence: the 1993–1998 window stands unnarrowed. Do not use the prefix to prioritise
years.**

### 2.4 The two target suffixes need not share a surname

One stem in `soc.religion.christian` appears under two suffixes:

```
From: XBHN14A@prodigy.com (Marge Warner)
From: XBHN14B@prodigy.com (Tim Day)
```

Same household account, two suffix letters, **two different people with two different
surnames.** This confirms the brief's household-suffix model and adds a limit to the name key:

- A `Gallegos` hit can identify **at most one** of `YGXS04D` / `YGXS04B`.
- The other suffix may post under a surname not in this search at all.
- A zero on `Gallegos` therefore does not clear the *stem* — only the name.

If a second household surname is known, it is worth as much as the first and should be added.

---

## 3. The negatives

| Group | msgs | msgs ≤1998 | `YGXS04` | `Gallegos` | pcom | pnet |
|---|---:|---:|---:|---:|---:|---:|
| `alt.homosexual` | — | 123,102 | 0 | 0 | 626 | 4,776 |
| `soc.religion.christian.bible-study` | 112,274 | 58,882 | 0 | 0 | 293 | 755 |
| `soc.religion.christian` | 125,331 | 49,694 | 0 | 0 | 283 | 315 |
| `soc.women.lesbian-and-bi` | — | 48,036 | 0 | 17 false | 143 | 217 |
| `soc.bi` | — | 24,951 | 0 | 0 | 27 | 561 |
| `soc.support.transgendered` | — | 15,414 | 0 | 1 false | 32 | 4,121 |
| `soc.motss` | 289,313 | 199 | 0 | 2 false | 19 | 9,224 |
| `talk.religion.misc` | — | 162 | 0 | 10 false | 2 | 3,139 |
| `alt.politics.homosexuality` | 160,643 | 10 | 0 | 3 false | 0 | 1,237 |

**`YGXS04`: zero in all nine.** The four groups the brief had already cleared are re-confirmed
against the ID and now also cleared against the name.

**`Gallegos`: 33 matches, all false positives, and not one is a `From:` line.**

- `soc.women.lesbian-and-bi` (17): a "Gustavo Gallegos" quoted in a news article about
  resources for gay teens, and a California Assembly roll-call list
  (`Escutia Figueroa Floyd Gallegos …`).
- `talk.religion.misc` (10): Las Vegas (New Mexico) Police Chief Tim Gallegos in an interview
  transcript, plus a "Veronica Lozada Gallegos" in a pasted address list.
- `alt.politics.homosexuality` (3): one quoted news sentence repeated through three levels of
  quoting.
- `soc.motss` (2): Texas state senator Mario Gallegos Jr., in quoted news text.
- `soc.support.transgendered` (1): the same California Assembly roll call.

This is the failure mode the brief hit with `handelman`, and it is why every name hit needs
eyes on the `From:` line before it counts. `Gallegos` is common enough, and common enough in
quoted political and news text, that a raw count is meaningless.

The strongest single negative is `alt.homosexual`: the most on-profile group in the target
set, 123,102 messages in the window, 626 Prodigy Classic address lines, and neither key
present.

### 3.1 The `From:` format is confirmed again

```
From: BSTE27A@prodigy.com (David Fuertsch)
From: YEKQ78C@prodigy.com (Sara Barr)
From: CBSG31A@prodigy.com (Valerie Southard)
```

Unrewritten ID, real name in parens, exactly as the brief states. A `From:` match would be
unambiguous.

### 3.2 This repository's own corpus holds nothing

Checked, since the brief arrived here. No `YGXS` anywhere in `corpus/`. The `prodigy` matches
are all model-generated prose ("soundboard prodigy", "child prodigy of rationality", a
thesaurus run). The one `Gallegos` match is a pasted personal message thread containing
Devon's own name and address — personal material, unrelated to Usenet, not reproduced here.
No evidence about the Prodigy account exists on this side.

---

## 4. Coverage findings on the unexplored leads

### 4.1 Tier 1 — Queer Digital History Project: offline at the host

`queerdigital.com` is reachable and the project is live, but its Transgender Usenet Archive —
the ~400,000-post, 1994–2013 corpus that is the actual prize — is down:

> "Due to technical and funding challenges, the Transgender Usenet Archive is currently
> unavailable. We hope to make it available again in the near future."

Host-side outage, not an environment limitation, so no amount of retrying from here recovers
it. The QDHP item catalogue that *is* up indexes communities and documents, not post full
text, so it cannot answer the question even while the Usenet archive is down. The brief's
recommendation — email Avery Dame-Griff — remains the live route and is now the only route to
that corpus.

Note that one of its six groups, `soc.support.transgendered`, was reachable through the
Internet Archive and is cleared above.

### 4.2 Tier 2 — usenetarchives.com: still blocked, brief's diagnosis confirmed

The brief guessed Cloudflare. Confirmed exactly, from response headers:

```
HTTP/2 403
cf-mitigated: challenge
server: cloudflare
```

The brief's proposed fix — use a real browser — was attempted. Chromium and Playwright are
both present here. **It fails for an unrelated reason: this container's browser has no
outbound network at all.** Chromium returns `net::ERR_CONNECTION_RESET` for every destination
including `example.com` and `archive.org`, with and without `--proxy-server` pointed at the
agent proxy, so it never reaches Cloudflare to be challenged.

usenetarchives.com is therefore **untried, not excluded.** It needs a browser with working
egress; a human's own browser is sufficient. Run `YGXS04D@prodigy.com`,
`YGXS04B@prodigy.com`, the bare stem `YGXS04`, and `Gallegos`.

### 4.3 Archive.org full-text search is not reachable

`ia-fts.archive.org` is refused by the egress gateway (502 to CONNECT — policy denial).
`advancedsearch.php` works but indexes item metadata only, not message text, so it cannot find
a string inside an mbox. Full-text search across the whole collection — which would settle
this far faster than group-by-group downloads — is unavailable from this container. It is the
single highest-value capability to restore.

### 4.4 Other hosts probed

| Host | Result |
|---|---|
| `narkive.com` | root 200, but the search host fails DNS through the proxy |
| `groups.google.com` | 302; Usenet viewing discontinued 22 Feb 2024, per the brief |
| `novabbs.com` | no connection |
| `al.howardknight.net` | no connection |

Ordinary web search is useless for this target, as expected — Usenet archives are not indexed
by general search engines. Queries on both full addresses and the name returned only generic
Prodigy and Usenet history pages.

---

## 5. Method notes

Confirmed working, unchanged from the brief: histogram before grep, `curl -L` or the download
silently returns 0 bytes, `grep -a` throughout, delete each mbox after grepping. Roughly 30 GB
of scratch is available; a 400–600 MB group takes several minutes to fetch.

`scan.sh <hierarchy-item> <group>` automates the whole loop: download, unzip, message count,
year histogram, counts for all five keys, hits with line numbers, cleanup. Nine groups were
run through it unattended.

### Cheap histogram screening does not work — and why

The brief's rule is "always pull the year histogram before running a full grep," but pulling
one costs a full 100–600 MB download, which is most of the expense the rule exists to avoid.
`probe.py` attempts the obvious fix: HTTP range-request the first few MB of the zip, parse the
local file header, and inflate the raw deflate stream to read `Date:` lines without fetching
the whole file. Mechanically it works — a 4 MB range inflates to ~15 MB of mbox.

**It does not answer the question, because these mboxes are stored newest-first.** Validated
against the two groups whose full histograms were already known: the head of
`soc.religion.christian` is 2007–2010, the head of `soc.motss` is 2009–2012. Both files run
back to the 1990s, but only at the tail — and a deflate stream cannot be decompressed from the
tail.

So there is no cheap screen for mid-90s depth. Either download the group in full, or use the
`@prodigy.com` proxy from §2.2 on a group already fetched. `probe.py` is kept because the
sort-order fact is worth knowing and is not documented anywhere obvious.

---

## 6. What to do next, in order

1. **Run usenetarchives.com from a browser with working egress** (§4.2). It is the one
   named target that is genuinely untried, and it carries mid-90s material the Internet
   Archive lacks.
2. **Email Avery Dame-Griff** for the QDHP Usenet corpus (§4.1) — now the only route to it.
3. **Get a second household surname.** Per §2.4 the two suffixes may not share one, so the
   current name key can clear at most half the target.
4. **Keep grepping the Internet Archive, but choose groups by measured depth, not hierarchy**
   (§2.1). The frontier is much larger than the brief assumed. `alt.*` is not written off.
5. Restore archive.org full-text search access if at all possible (§4.3) — it would replace
   all of step 4.

Still live, and untouched by any of this: §6 of the brief. If these accounts used
`X-No-Archive`, the posts are gone by the poster's own instruction and nothing above would
ever have found them.
