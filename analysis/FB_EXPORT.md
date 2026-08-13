# FB_EXPORT — the Facebook/Meta archive

Extracted 2026-08-13 by `analysis/fb_export.py`. Source: four zips in the
link-readable Drive folder `1eODsrIV0wwekB-lFwYaFsjwIXGdz3lb_` ("META DATA"),
generated **2024-10-26** by Facebook's Download Your Information tool.

This is the **fourth archive** in the corpus and the oldest by a wide margin.
Read `CLAUDE.md`'s corpus sections first; almost nothing from the NovelAI rules
transfers here, and the ways it fails to transfer are the point.

## Getting it without downloading it

The four zips total **24.6 GB**, which does not fit alongside anything else in
an ephemeral container. It does not need to:

| part | size | contents |
|---|---:|---|
| `…-u6fQFxYN.zip` | 6.99 GB | **all 2,701 text-bearing HTML files**, plus media |
| `…-jcye8gmw.zip` | 7.86 GB | media, 5 HTML |
| `…-Qb0Yp5lz.zip` | 6.75 GB | media only |
| `…-ybK72kK8.zip` | 3.01 GB | 14 videos, nothing else |

23.5 GB of the total is `.mp4` and a further 0.6 GB is images. **The entire
textual record is 112 MB in 2,706 HTML files, and 2,701 of them are in one
zip.** `fb_export.py` reads each zip's central directory over HTTP range
requests (a few KB from the tail) and then pulls only matching entries,
coalescing nearby ones — the whole text corpus costs **four requests**.

```
python3 analysis/fb_export.py listing        # central directories -> exports/facebook/
python3 analysis/fb_export.py fetch '\.html$'
python3 analysis/fb_export.py measure        # -> data/fb_summary.json
```

Two properties this depends on, both worth re-checking if it ever breaks:
Drive serves `206 Partial Content` on the confirmed download URL, and the zip
entries are **stored, not deflated** (`csize == usize`), so a ranged fetch of
one entry needs no decompression. The inflate path is kept anyway.

`exports/` is gitignored, for the same reason `corpus/` is, and with more force
— see the privacy section below.

## It is the HTML export, not the JSON one

There is no `.json` anywhere in these zips. Everything is scraped out of
Facebook's generated markup, which uses **two different block shapes**, and
knowing which one a file uses is most of the work:

**Shape A — the feed block.** Posts, comments, events, groups, and *human
message threads*.

```html
<div class="_a6-g">
  <div class="_2ph_ _a6-h _a6-i">Devon Gallegos shared a link.</div>   <!-- header/sender -->
  <div class="_2ph_ _a6-p">…</div>                                     <!-- body -->
    <div class="_2pin">…</div>                                         <!-- posts only -->
  <div class="_3-94 _a6-o"><div class="_a72d">May 15, 2009 3:11:13 am</div></div>
</div>
```

**Shape B — the label/value table.** Post edits, Meta AI chats, and every
settings file.

```html
<td class="_a6_q">Text</td><td class="_2piu _a6_r">…the value…</td>
```

`fb_export.py` exposes `feed_entries()`, `table_entries()`, `message_turns()`
and `ai_turns()` for these. The four are not interchangeable: message threads
and AI chats look superficially alike and use *different* shapes.

## Traps

- **Timestamps in message threads run newest-first.** Sort by `dt` before
  reading any interval off them. Posts run oldest-first. Nothing announces this.
- **Thread pages are paginated** — `message_1.html`, `message_2.html`. A thread
  is the directory, not the file.
- **`_2pin` cells carry a trailing `Updated <date>` line** that is not part of
  the post text. `feed_entries()` strips it; a naive scrape will inflate word
  counts and corrupt any date parse.
- **`start_here.html` and the settings files are shape B with no timestamps**
  and fall out of every date-based pass silently.
- **Header text is not a reliable type field.** 2,208 of 5,018 posts have no
  header at all, and `Shared from Instagram` (1,221) is a syndication marker,
  not a category.

## What this record can and cannot answer

The asymmetry table, in the same form as `TW_EXPORT.md`:

| | NovelAI | AI Dungeon | Twitter/X | **Facebook** |
|---|---|---|---|---|
| undo tree / branches | ✅ full | ❌ flat | ❌ | ❌ |
| rejected generations | ✅ | ❌ | ❌ | ❌ |
| per-turn sampler settings | ✅ | ❌ | ❌ | ❌ |
| model identity | ✅ | partial | ✅ | ❌ |
| **per-event wall clock** | ❌ | partial | one per *exchange* | ✅ **per event, to the second** |
| **author's own revision history** | ✅ (of model text) | ❌ | ❌ | ✅ **(of human text)** |
| span | 2021-06 .. 2026-07 | 2020-12 .. | 2024-12 .. 2026-07 | **2008-03 .. 2024-10** |

Two of those rows are why this archive matters.

**It has a real clock.** `FINDINGS.md` §11 records that NovelAI is structurally
incapable of dating anything, and `analysis/TWITTER.md` records that the
Twitter archive has a clock at only one timestamp per *exchange*. Facebook
stamps **every post, every comment, every message and every revision
individually, to the second**. It is the only archive in the corpus that does.

**It has an edit history of human prose.** `edits_you_made_to_posts.html` holds
377 successive drafts with timestamps — the same chosen/rejected shape that
makes NovelAI analysable, but over text Endorphin wrote himself rather than
text a model proposed. Median gap between drafts in a chain is **68 seconds**.
Nothing else in the corpus contains this.

What it cannot do is anything built on branches, rejected generations, or
sampler settings — which is most of `analysis/`. It also cannot identify a
model: the Meta AI chats name a persona, never a checkpoint.

## Privacy — this is the most exposed archive of the four

`CLAUDE.md` already says the public-repo decision was made about Endorphin's own
fiction and does not inherit. That applies here harder than it did to Twitter.

This export contains **1,524 private message threads with named third parties,
147,233 turns and 1.77 million words** — four times the volume of his public
posts — plus an IP-address audit, login history, device fingerprints, uploaded
phone contacts, a search history, and advertiser targeting categories. The
third parties did not consent to any of it.

Standing rules, matching the Twitter ones:

- `exports/` is gitignored and stays that way.
- Anything committed to `data/` from this archive carries **counts, lengths and
  dates only — never message text and never participant names**.
  `data/fb_summary.json` is aggregate-only by construction; check it stays that
  way.
- `fb_export.py`'s `measure` pass never serialises a thread name, a sender, or
  a message body. Do not add one for convenience.
- The security, contacts, search-history and ads files have no analytic purpose
  identified so far. Leave them unread unless there is a question that needs
  them, and say what the question is first.
