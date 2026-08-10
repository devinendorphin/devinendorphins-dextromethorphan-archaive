# Usenet search log — Prodigy `YGXS04D` / `YGXS04B`, plus name key "Devon Gallegos"

Run 2026-08-10, against the brief in `SEARCH_BRIEF.md`. This file records what was searched,
what was found, and — mostly — what the archives do and do not hold. Per the brief's §7, a
zero is a coverage finding, not a conclusion about whether the person posted.

**Result in one line: nine groups, ~320,000 messages from the 1990–1998 window, and a census
of every Prodigy address in them — 330 canonical Prodigy Classic IDs — containing no match for
`YGXS04`, for `YGSX04`, or for anything within edit distance 2 of either.**

The negatives are worth less than the things the pass established along the way, so those
are stated first.

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

## 2. Six findings that change how the next pass should be run

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

### 2.5 The ID is a memory artifact, so the search was rebuilt around a census

Prompted by a proposed alternate spelling — `YGSX04D`, transposing the middle two letters —
the search was restructured. The point generalises past that one variant:

**Only the domain is verified.** The brief establishes `@prodigy.com` against 256 real
messages. The ID itself is a remembered seven-character string from roughly thirty years ago,
and the suffixes `D` and `B` are remembered too. `YGSX04D` is not a worse guess than
`YGXS04D`; neither is authoritative. Testing one exact spelling per pass was the wrong shape
for the problem — each new guess cost a fresh 1.1 GB of downloads to answer.

So instead of grepping for a string, every Prodigy address in all nine groups was extracted
into a census: **25,776 address tokens → 374 distinct `prodigy.com` IDs → 330 canonical
`LLLLDDL` IDs**, plus 483 distinct `prodigy.net` locals. That census is committed as
`prodigy_classic_ids.tsv`, so any future variant is a grep against a 20 KB file rather than
another download.

Against the census (`match.py`):

| Test | Result |
|---|---|
| `YGXS04` exact | **absent** |
| `YGSX04` exact | **absent** |
| All 24 letter-permutations of {Y,G,X,S} + `04` | **absent** |
| Any ID within **edit distance ≤2** of either stem | **none** |
| Any ID beginning `YG` | **none** |
| Any `prodigy.net` local containing `gallegos` | **none** |
| Raw-text regex `[YGXS]{4}0?4` across all nine mboxes | **zero matches** |

Edit distance ≤2 is a wide net — it absorbs any single transposition, any two substitutions,
insertions or deletions. Nothing in these nine groups comes close.

The four IDs in the census whose digits are `04` are `PAHB04B`, `TQXB04A` (Daniel Morris),
`ULWB04B` (Dody Carleton) and `ULWB04C` (Barbie Doll). The eleven Y-prefix IDs are `YBXD10A`
(Beau Gales), `YBXD10C` (K pennington Lewis), `YCQT19A`, `YEKQ78C` (Sara Barr), `YELH71A`
(Doug Hutton), `YLRP82A`, `YPKL49C` (Brad Everett), `YRLW82A` (Courtney Pender iv), `YUZQ54A`
(Skyler rae Peacock / Steven Peacock), `YYYC39A` (Brice Wellington), `YYZA05A` (Joel Smith).
None is a plausible corruption of either target.

**This upgrades the negative substantially.** The earlier result was "the exact string is not
there," which a spelling error would explain. The result now is "no ID resembling either
spelling is there, out of 330 canonical Prodigy Classic IDs." Within these nine groups the
account is absent, and misremembering the ID is no longer a live explanation for why.

### 2.5.1 A truncation scare that turned out to be my own error

Partway through, the census appeared to contain left-truncated IDs — `Y49C@prodigy.com`,
`YG96A@prodigy.com`, `YGV93A@prodigy.com` — which would have implied addresses were being
line-wrapped in the archive, and therefore that every full-stem grep in this search *and in
the brief* could silently miss a wrapped occurrence.

It was an artifact of the checking grep, not of the archive. An unanchored pattern was
matching mid-token: `Y49C` is the tail of **KXVY49C**, `YG96A` of **RVYG96A**, `YGV93A` of
**LYGV93A**. All are canonical seven-character IDs. 337 of 374 IDs are exactly seven
characters; the remainder are vanity or staff addresses (`AARON`, `ABUSE`, `BRAD`,
`BOUCHER`) and hex Message-ID locals, not damaged user addresses.

**No wrapping problem exists and the stem greps were sound.** Recorded because the reasoning
looked convincing for several minutes, and because anchoring matters when auditing an
extraction with the same tool that produced it.

### 2.6 Household census

13 of 316 canonical stems appear under more than one suffix — about 4%:

```
ATMF00 [A,C]   BBHL55 [A,C]   KUVZ84 [A,B]   LJNF40 [A,C,D]   LXUT53 [A,B]
PDRR30 [A,D]   QGBF56 [A,B]   ULWB04 [B,C]   WGVP44 [A,D]     XBHN14 [A,B]
YBXD10 [A,C]   ZBJZ24 [B,F]   ZPNY64 [B,C]
```

Suffixes A through F are all attested, and `LJNF40` runs to three members. A `D`/`B` pair as
in the target is entirely ordinary. This is the population-level version of the `XBHN14`
finding in §2.4.

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

### 4.2 Tier 2 — usenetarchives.com: browser works; one blocked host stops the challenge

The brief guessed Cloudflare. Confirmed exactly, from response headers:

```
HTTP/2 403
cf-mitigated: challenge
server: cloudflare
```

The brief's proposed fix — use a real browser — **works.** An earlier revision of this file
claimed the container's browser had no outbound network at all. **That was wrong**, and the
error mattered: it wrote off the brief's highest-value lead on a false premise. Two unrelated
misconfigurations produced the same symptom:

1. **The agent proxy's port rotates within a session** — `42167` early, `41413` later. The
   browser scripts had it hardcoded from an earlier reading, so Chromium was dialling a dead
   port. Read `HTTPS_PROXY` from the environment at launch time, never copy the number.
2. **The egress gateway cannot complete Chromium's TLS 1.3 handshake.** With the right port
   the CONNECT tunnel opens and is then closed mid-handshake. Python's `ssl` negotiates TLS
   1.3 + ALPN h2 through the very same tunnel without trouble, so it is specific to Chromium's
   ClientHello. Post-quantum key share and Encrypted Client Hello were both tested and
   disconfirmed. **`--ssl-version-max=tls1.2` fixes it outright.**

Working recipe (`br.py`, `cf.py`, `gg.py`, `ggs.py`):

```python
chromium.launch(executable_path="/opt/pw-browsers/chromium",
                args=["--no-sandbox","--disable-dev-shm-usage","--ssl-version-max=tls1.2"],
                proxy={"server": os.environ["HTTPS_PROXY"]})
```

With that, usenetarchives.com loads and the Cloudflare challenge actually executes, reaching
"Verification successful". **It still does not complete, for a precisely identifiable
reason:** Turnstile fetches `brunhild.challenges.cloudflare.com`, and the egress gateway
denies exactly that host.

```
challenges.cloudflare.com:443           200 Connection Established
www.usenetarchives.com:443              200 Connection Established
brunhild.challenges.cloudflare.com:443  502 Bad Gateway   <- policy denial
```

No `cf_clearance` cookie is ever issued, so the site stays behind the interstitial. This is an
organization policy denial rather than a transient failure, and the proxy's own documentation
says to report those rather than retry. Fabricating responses for Cloudflare's endpoints to
force clearance would be circumventing the site's access control, and was not attempted.

usenetarchives.com is therefore still **untried, not excluded** — but the obstacle is now one
allowlist entry rather than a mystery. Either `brunhild.challenges.cloudflare.com` is allowed,
or the queries run from a human's browser: `YGXS04D@prodigy.com`, `YGXS04B@prodigy.com`, the
`YGSX04` spellings, and `Gallegos`.

### 4.2.1 Google Groups is alive, and it is a second independent corpus

The brief records Google Groups as discontinued on 22 February 2024 and "not reachable by web
search." The first half is true and the second is misleading. With the working browser,
**per-group Usenet search still serves results without any sign-in**:

```
https://groups.google.com/g/<group>/search?q=<term>
```

Only the cross-group search (`/search?q=`) demands a Google account. This matters because the
underlying Deja archive began 16 March 1995 and covers the target window independently of the
Internet Archive spool.

**The method was validated with a positive control before any zero was trusted.** Searching
`YEKQ78C` — a Prodigy ID this pass had already recovered from the Internet Archive — in
`soc.religion.christian` returns 7 conversations authored by "Sara Barr", the correct holder.
Google does index the Prodigy member ID.

One hard constraint discovered by the same control: **stem search does not work.** `YEKQ78`
returns zero where `YEKQ78C` returns seven, and `YBXD10` likewise returns zero. Google
tokenizes the full seven-character ID, so every query must carry a suffix letter — which is
why the sweep below enumerates suffixes A–F rather than searching the six-character stem.

### 4.2.2 Google Groups sweep — 117 queries, 108 of them on the ID, all zero

Nine groups × (`YGXS04` + `YGSX04`) × suffixes A–F, plus `Gallegos` in each group. Raw output
in `google_groups_sweep.txt`.

| | |
|---|---|
| ID queries run | 108 |
| ID queries returning anything | **0** |
| `Gallegos` queries run | 9 |
| `Gallegos` queries returning anything | 5, all false positives |

The `Gallegos` results are the same population of noise as the Internet Archive pass, arriving
by a completely independent route: a New Mexico shooting story in
`alt.politics.homosexuality`, the Gustavo Gallegos P.E.R.S.O.N. Project item in
`soc.women.lesbian-and-bi`, Mario Gallegos in `soc.motss`, and two more of the same kind.

This is the most valuable negative in the whole file. Google's Deja-derived archive is not the
Internet Archive spool — different provenance, different coverage, different gaps, and it
covers the target window by construction from 16 March 1995. Both corpora now say the same
thing about both spellings across every suffix.

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
3. **Stop testing remembered spellings against the Internet Archive.** §2.5 settles every
   variant of the ID at once for these nine groups. A new spelling only becomes worth testing
   against *new* groups, or against the archives in steps 1 and 2 — and there it should be
   run as a census, not a grep.
4. **Get a second household surname.** Per §2.4 the two suffixes may not share one, so the
   current name key can clear at most half the target.
5. **Keep extending the census to new groups, chosen by measured depth, not hierarchy**
   (§2.1). The frontier is much larger than the brief assumed. `alt.*` is not written off.
   `inventory.sh` appends to the same census file.
6. Restore archive.org full-text search access if at all possible (§4.3) — it would replace
   all of step 5.

Still live, and untouched by any of this: §6 of the brief. If these accounts used
`X-No-Archive`, the posts are gone by the poster's own instruction and nothing above would
ever have found them.
