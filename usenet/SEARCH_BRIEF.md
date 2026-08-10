# Search Brief: Locating Usenet posts by Prodigy account YGXS04D

## Objective

Find surviving Usenet messages posted from Prodigy Classic accounts
`YGXS04D` and `YGXS04B`, circa 1993–1998. Recover full message text,
headers, thread context, and correspondents.

---

## 1. Exact target strings

Grep for the **stem**, case-insensitively. This catches both household
suffixes and any format variation:

```
YGXS04
```

Full expected addresses:

```
YGXS04D@prodigy.com
YGXS04B@prodigy.com
```

**Domain is `.com`, not `.net`.** This is verified, not assumed.
Prodigy Classic's Usenet gateway stamped `@prodigy.com`. `@prodigy.net`
was the later Prodigy Internet service, which used name-style addresses
(`rrhorton@prodigy.net`), not the alphanumeric member IDs.

### Header format to expect

Verified against 256 real Prodigy Classic messages in
`soc.religion.christian`:

```
From: BSTE27A@prodigy.com (David Fuertsch)
From: CBSG31A@prodigy.com (Valerie Southard)
From: BWHT68B@prodigy.com (Jay Tularaksa)
```

The gateway did **not** rewrite or anonymize the ID, and it appended the
subscriber's real name in parentheses. Two consequences:

- A `From:` match is exact and unambiguous. No stylometry needed.
- If the account holder's legal name is known, it is a **second
  independent search key**, and one that survives even if the ID string
  was mangled in a given archive's ingest.

### Secondary keys, in priority order

1. `YGXS04` (stem)
2. Account holder's real name as it would appear in the `From:` parens
3. `prodigy.com` narrowed by date range 1993–1998, then scanned by hand
   if volume is small

---

## 2. Already searched — do not repeat

Full-corpus greps run against the Internet Archive Usenet Historical
Collection. All returned **zero** hits for `YGXS04` (stem, case-insensitive):

| Group | Size | Result |
|---|---|---|
| `soc.motss` | 641 MB mbox | 0 hits |
| `soc.religion.christian` | 383 MB mbox | 0 hits |
| `talk.religion.misc` | 193 MB zip | 0 hits |
| `alt.politics.homosexuality` | 251 MB zip | 0 hits |

Also searched: `handelman` (a named correspondent). Only false positives
— a textbook listing (Ethridge/Handelman, *Politics in a Changing World*)
and an unrelated "paul handelman".

---

## 3. Known coverage trap — read before spending bandwidth

**The Internet Archive's Usenet Historical Collection is overwhelmingly a
1999-and-later spool for most hierarchies.** Verified year histograms:

- `soc.motss`: ~190 messages total across 1995–1998; 27,971 in 1999 alone
- `alt.politics.homosexuality`: 2 messages in 1993, 2 in 1996, 6 in 1998
- `talk.religion.misc`: 17 in 1995, 32 in 1996, 52 in 1997

The exception found so far:

- `soc.religion.christian`: 1,473 (1994), 2,136 (1995), 21,388 (1996) —
  genuine mid-90s depth

**Therefore: always pull the year histogram before running a full grep.**
A group with fewer than ~1,000 messages in 1995–1998 is not worth the
download for this target.

---

## 4. Method — Internet Archive (works, no auth, no rate limit hit yet)

### Step 1: list candidate groups in a hierarchy

```bash
curl -s "https://archive.org/metadata/usenet-alt" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for f in d.get('files',[]):
    n=f['name'].lower()
    if any(k in n for k in ['homosexu','gay','christ','religion','lesbian','queer','bible']):
        print(f['name'], round(int(f.get('size',0))/1e6,1),'MB')
"
```

Hierarchy items: `usenet-alt`, `usenet-soc`, `usenet-talk`,
`usenet-comp`, `usenet-misc`, `usenet-rec`, `usenet-net`, `usenet-sci`.

### Step 2: download and unzip

```bash
curl -sL -o t.zip "https://archive.org/download/usenet-alt/GROUPNAME.mbox.zip"
unzip -o -q t.zip
```

Use `-L`. Without follow-redirects the download silently returns 0 bytes.

### Step 3: histogram first, then grep

```bash
grep -ao "^Date: .*" GROUPNAME.mbox | grep -ao "19[89][0-9]" | sort | uniq -c
grep -aic "YGXS04" GROUPNAME.mbox
grep -aic "@prodigy\.com" GROUPNAME.mbox
```

Use `-a` throughout. Mbox files contain binary segments and grep will
otherwise report "binary file matches" and stop.

### Step 4: on a hit, extract with context

```bash
grep -ain "YGXS04" GROUPNAME.mbox
# then pull the surrounding message by byte offset or line range,
# including Message-ID, Newsgroups, Date, Subject, References
```

Capture `References:` — it gives the thread, which gives the
correspondents, which is the actual prize.

### Cleanup

Delete each mbox after grepping. These are 300 MB–1 GB uncompressed.

---

## 5. Ranked search targets

### Tier 1 — highest prior, not yet checked

Community and academic archives assembled deliberately, by people who
went looking for these specific groups in these specific years:

- **Queer Digital History Project** (Avery Dame-Griff) — extensive
  curated archive of queer/trans Usenet, used for *The Two Revolutions*
  (NYU Press, 2023). Exactly the subject matter and era. Has a human to
  email.
- Other university digital-humanities Usenet corpora, especially any
  built for computational analysis of 90s newsgroups.

### Tier 2 — reachable but blocked from this environment

- **usenetarchives.com** — extensive archive with search, carries mid-90s
  material the Internet Archive spool lacks. Sits behind a Cloudflare
  challenge; a scripted client gets a JS interstitial. **Needs a real
  browser.** Query `YGXS04D@prodigy.com` then `YGXS04B@prodigy.com`
  directly.
- **Google Groups / Deja corpus** — Deja began archiving 16 March 1995,
  so it structurally covers the target window. Google discontinued Usenet
  viewing and posting on 22 February 2024; existing archives are stated
  to remain but are no longer served through the general interface and
  are not reachable by web search.

### Tier 3 — long shots worth a pass

- Archive.org CD-ROM collections (e.g. InfoMagic Usenet source
  snapshots) — these mostly carry `comp.sources.*`, unlikely to help,
  but cheap to check.
- Individual group maintainers' personal spools, often posted to
  personal sites or GitHub.
- `alt.religion.gay-les-bi-tran`, `alt.homosexual`,
  `alt.politics.homosexual`, `alt.religion.christian`,
  `alt.christnet.*`, `soc.support.youth.gay-lesbian-bi` — check
  histograms before downloading.

---

## 6. One thing that could void the whole search

The `X-No-Archive` header was introduced in 1995 in response to
DejaNews, and Deja honored it by declining to archive those messages. If
these accounts used it, the posts are gone by the poster's own
instruction and no amount of searching recovers them.

---

## 7. Reporting discipline

- A zero result is a **coverage finding**, not a conclusion about whether
  the person posted. Always report which groups, which years, and how
  many messages that archive actually held for those years.
- Never infer authorship from style. The `From:` header is exact; use it
  or report nothing.
- On any hit, capture the raw message verbatim before summarizing it.
