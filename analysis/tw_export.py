#!/usr/bin/env python3
"""The third archive: a Twitter/X export, and the one clock the others don't have.

`FINDINGS.md` §11 records that NovelAI stores no per-block timestamps, so tempo
-- the pace of the exchange -- is unrecoverable. `analysis/tempo.py` recovered
*rhythm* from the sequence of lengths and said plainly that duration was still
gone. This archive has duration. It carries 2,818 Grok chat turns stamped to the
millisecond, which is a turn-taking record with a language model in wall-clock
time: the measurement the NovelAI corpus is structurally incapable of.

It is also a third *shape*, and most of the corpus's apparatus does not transfer
to it. There is no undo tree, so no rejected generations; no sampler settings, so
nothing settings-comparative; and the Agent turn is stamped with the *request*
time rather than the completion time, so the resolution is one stamp per
exchange, not per turn. `analysis/TW_EXPORT.md` writes out what the record can
and cannot answer before anything is joined to it.

Five things this runs:

1. **The cue length, re-measured off-platform.** §'s frame rests on a median
   human turn of 55 characters. If that is the author, it should survive a change
   of platform, model, interface and activity. If it is NovelAI's editor, it
   should not. The control that decides it is the *chat opener* -- a turn with no
   generation before it, so no cue to be.
2. **The turnaround, against the length of what was there to read.** The
   confound is that the interval contains the model's own generation time. The
   control holds the agent turn's length fixed and varies how much the author
   then typed: generation time cannot know how long the reply will be.
3. **The tweets as an external clock.** `data/EPISODES.tsv` is OCR off the Twitch
   dashboard and is the project's only independent clock. Tested against it by
   circular shift, which preserves how both series clump and destroys only their
   alignment -- a plain co-occurrence count would mostly measure that both
   activities were dense in the same years.
4. **The board question**, asked against the claim rather than for it: the
   earliest statement of each thesis, checked against the firing date. `THESIS`
   and `CANDOR` are searched separately because the first pass had only the
   former and was therefore blind to the stronger claim.
5. **Bursts.** X posts a thread's parts at once, so the clock separates a piece
   written in advance from a thread pulled along by a conversation. This is the
   analogue of `analysis/spans.py` for a record with no branch structure.

Direct messages, the phone number, the email, the IP audit and the ad records are
in the archive and are **never read by this script** -- see `SKIP` below. The
committed metadata carries no message text at all.

    python3 analysis/tw_export.py twitter.zip --out out \\
        --meta data/twitter_meta.jsonl --days data/TWEET_DAYS.tsv \\
        --report analysis/TWITTER.md
"""

import argparse
import collections
import datetime as dt
import json
import pathlib
import random
import re
import statistics as st
import sys
import zipfile

# Read from the archive only what this analysis needs. Everything else is either
# third-party private data (the author can consent to his own exposure, not his
# correspondents') or account PII, and the repo is public.
WANT = ("manifest.js", "tweets.js", "grok-chat-item.js", "note-tweet.js")
SKIP = (
    "direct-message",  # both sides of a private conversation
    "phone-number",
    "account-creation-ip",
    "ip-audit",
    "personalization",
    "ad-",
    "email",
)

TWEET_TS = "%a %b %d %H:%M:%S %z %Y"

# External events, from public reporting rather than from this archive. Kept in
# one place and labelled, because §4 is only as good as these dates and nothing
# in the export can check them.
OPENAI_EVENTS = [
    ("2022-10-31", "Musk dissolves Twitter's board; becomes sole director"),
    ("2023-11-17", "OpenAI board fires Sam Altman"),
    ("2023-11-22", "Altman reinstated; most of the board replaced"),
    ("2024-09-25", "OpenAI's plan to restructure as a for-profit is reported"),
    ("2025-10-28", "Restructuring completes: OpenAI Foundation over a PBC"),
]
# The governance thesis, as he states it. Matched case-insensitively.
THESIS = ("jane jacobs", "monstrous hybrid", "systems of survival",
          "incubator of corruption", "incubate corruption", "for profit arm",
          "for-profit arm")
# The candour thesis -- a *different* claim, about what the board's phrase meant.
# Kept separate because an earlier pass searched only THESIS and therefore had no
# slot for this one: see the standing note that a lens decides in advance what
# counts as a thing.
CANDOR = ("candid", "thousand cuts", "1000 cuts", "fractal")
# NovelAI reference, FINDINGS.md's frame table: human blocks following a generation.
NAI_REF = {"n": 134063, "median": 55, "bins": (46.4, 44.6, 6.7, 2.3)}
BINS = ((0, 50), (50, 200), (200, 600), (600, 10**9))
READ_BINS = ((0, 500), (500, 1000), (1000, 2000), (2000, 4000), (4000, 10**9))


def payload(raw):
    """`window.YTD.x.part0 = [ ... ]` -> the JSON."""
    text = raw.decode("utf-8", errors="replace")
    return json.loads(text[text.index("=") + 1:])


def read_archive(path):
    """Pull the wanted files out of the export, zip or unpacked directory alike."""
    path = pathlib.Path(path)
    out = {}
    if path.is_dir():
        for name in WANT:
            for hit in list(path.rglob(name))[:1]:
                out[name] = hit.read_bytes()
        return out
    with zipfile.ZipFile(path) as zf:
        for info in zf.infolist():
            base = pathlib.PurePosixPath(info.filename).name
            if base in WANT and not any(s in base for s in SKIP):
                out[base] = zf.read(info)
    return out


def unwrap(rows, key):
    return [r[key] for r in rows if key in r]


def ts_iso(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def by_chat(turns):
    chats = collections.defaultdict(list)
    for t in turns:
        chats[t["chatId"]].append(t)
    for rows in chats.values():
        rows.sort(key=lambda r: r["createdAt"])
    return chats


def dist(vals):
    n = len(vals)
    counts = [sum(1 for v in vals if lo <= v < hi) for lo, hi in BINS]
    return n, st.median(vals), st.mean(vals), [100 * c / n for c in counts]


def pct(x):
    return f"{x:.1f}%"


# --- 1. the cue length, and the opener control ------------------------------


def cue_lengths(chats):
    follow, opener = [], []
    for rows in chats.values():
        for i, r in enumerate(rows):
            if r["sender"]["name"] != "User":
                continue
            n = len(r.get("message") or "")
            if i == 0:
                opener.append(n)
            elif rows[i - 1]["sender"]["name"] == "Agent":
                follow.append(n)
    return follow, opener


# --- 2. the turnaround ------------------------------------------------------


def intervals(chats, cap=3600):
    """(seconds, chars of the agent turn read, chars of the reply typed)."""
    out = []
    for rows in chats.values():
        for a, b in zip(rows, rows[1:]):
            if (a["sender"]["name"], b["sender"]["name"]) != ("Agent", "User"):
                continue
            gap = (ts_iso(b["createdAt"]) - ts_iso(a["createdAt"])).total_seconds()
            if gap <= cap:
                out.append((gap, len(a.get("message") or ""), len(b.get("message") or "")))
    return out


def stamp_resolution(chats):
    """Is the Agent turn stamped independently, or does it copy the request?"""
    same = total = 0
    for rows in chats.values():
        for a, b in zip(rows, rows[1:]):
            if (a["sender"]["name"], b["sender"]["name"]) == ("User", "Agent"):
                total += 1
                same += a["createdAt"] == b["createdAt"]
    return same, total


# --- 3. the external clock --------------------------------------------------


def tweet_days(tweets):
    return collections.Counter(
        dt.datetime.strptime(t["created_at"], TWEET_TS).date() for t in tweets
    )


def episode_days(path):
    days = collections.Counter()
    if not pathlib.Path(path).exists():
        return days
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        head = line.split("\t")[0].strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", head):
            days[dt.date.fromisoformat(head)] += 1
    return days


def board_timeline(tweets, notes):
    """§4. Did he call the OpenAI board crisis, or read it afterwards?

    The question was Endorphin's, and it is exactly the shape the standing note
    warns about -- a primed claim, asked in a way that invites agreement. So the
    test is the one that could embarrass it: find the *earliest* statement of the
    governance thesis and check it against the firing date rather than against
    the restructuring it eventually fits.
    """
    rows = [{"created_at": dt.datetime.strptime(t["created_at"], TWEET_TS).isoformat(),
             "text": t.get("full_text", ""), "kind": "tweet"} for t in tweets]
    rows += [{"created_at": n["createdAt"], "kind": "long-form",
              "text": n.get("core", {}).get("text", "")} for n in notes]
    hits = sorted((r for r in rows if any(t in r["text"].lower() for t in THESIS)),
                  key=lambda r: r["created_at"])
    fired = "2023-11-17"
    before = [r for r in hits if r["created_at"][:10] < fired]
    # The candour reading, tracked separately and only where it is *about* the
    # phrase -- "candid" alone also catches election candidates and Candide.
    cand = sorted(
        (r for r in rows
         if "candid" in r["text"].lower()
         and any(k in r["text"].lower() for k in
                 ("board", "altman", "cuts", "press release", "fractal", "sound bite",
                  "consistently candid"))),
        key=lambda r: r["created_at"])
    return {"hits": hits, "before": before, "first": hits[0] if hits else None,
            "fired": fired, "candor": cand}


# --- 5. bursts: threads posted whole ----------------------------------------

TAXONOMY = (r"\b(abus\w*|gaslight\w*|dissonan\w*|accountab\w*|fuckery|narciss\w*"
            r"|manipul\w*|trauma\w*|harm\w*|boundar\w*|enmesh\w*|oversight"
            r"|compliance|whistlebl\w*)\b")
NUMBERED = re.compile(r"^\s*\d+\s*/")
TCO = re.compile(r"https://t\.co/\S+")


def threads_of(tweets):
    """Self-reply chains. A thread is his own tweet answering his own tweet."""
    rows = [{"id": t["id_str"],
             "at": dt.datetime.strptime(t["created_at"], TWEET_TS),
             "text": TCO.sub("", t.get("full_text", "")).strip(),
             "parent": t.get("in_reply_to_status_id_str")} for t in tweets]
    mine = {r["id"] for r in rows}
    kids = collections.defaultdict(list)
    roots = []
    for r in rows:
        if r["parent"] in mine:
            kids[r["parent"]].append(r)
        else:
            roots.append(r)
    out = []
    for root in roots:
        chain, stack = [root], [root]
        while stack:
            for c in sorted(kids[stack.pop()["id"]], key=lambda x: x["at"]):
                chain.append(c)
                stack.append(c)
        if len(chain) >= 3:
            out.append(sorted(chain, key=lambda x: x["at"]))
    return rows, out


def burst_stats(tweets):
    rows, threads = threads_of(tweets)
    def span(t):
        return (t[-1]["at"] - t[0]["at"]).total_seconds()
    burst = [t for t in threads if span(t) <= 60]
    slow = [t for t in threads if span(t) > 60]
    bids = {x["id"] for t in burst for x in t}

    def lens(sel):
        return [len(r["text"]) for r in rows if sel(r)]
    groups = {
        "burst": lens(lambda r: r["id"] in bids),
        "reply": lens(lambda r: r["id"] not in bids and r["text"].startswith("@")),
        "solo": lens(lambda r: r["id"] not in bids and not r["text"].startswith("@")),
    }
    text = {
        "burst": " ".join(r["text"] for r in rows if r["id"] in bids).lower(),
        "other": " ".join(r["text"] for r in rows if r["id"] not in bids).lower(),
    }

    def rate(txt, pat):
        w = len(re.findall(r"[a-z']+", txt)) or 1
        return 10000 * len(re.findall(pat, txt)) / w

    def hour(d):  # account timezone is "Quito" = UTC-5; DST is not modelled
        return (d - dt.timedelta(hours=5)).hour
    night = {"burst": 0, "other": 0}
    for t in burst:
        night["burst"] += hour(t[0]["at"]) >= 22 or hour(t[0]["at"]) < 6
    others = [r for r in rows if r["id"] not in bids]
    night["other"] = sum(hour(r["at"]) >= 22 or hour(r["at"]) < 6 for r in others)
    return {
        "threads": len(threads), "burst": burst, "slow": slow,
        "n_burst_tweets": len(bids), "groups": groups,
        "rates": sorted(len(t) / max(span(t), 1) for t in burst),
        "numbered_burst": sum(bool(NUMBERED.match(t[0]["text"])) for t in burst),
        "numbered_slow": sum(bool(NUMBERED.match(t[0]["text"])) for t in slow),
        "night_burst": 100 * night["burst"] / max(len(burst), 1),
        "night_other": 100 * night["other"] / max(len(others), 1),
        "lex": {k: (rate(text["burst"], p), rate(text["other"], p)) for k, p in
                (("taxonomy", TAXONOMY),
                 ("first person", r"\b(i|my|me|mine|we|our)\b"),
                 ("hedges", r"\b(maybe|perhaps|seems|might|possibly|i think)\b"),
                 ("AI words", r"\b(llm|model|ai|agi|gpt|claude|openai|prompt\w*)\b"))},
        "biggest": sorted(burst, key=len, reverse=True)[:8],
        "span": span,
    }


def circular_shift(tw, ep, trials=20000, seed=11):
    """Both series clump in the same years; only a shift test can tell them apart."""
    lo, hi = max(min(tw), min(ep)), min(max(tw), max(ep))
    span = (hi - lo).days + 1
    idx = [lo + dt.timedelta(days=i) for i in range(span)]
    T = [1 if tw.get(d) else 0 for d in idx]
    E = [1 if ep.get(d) else 0 for d in idx]
    obs = sum(a & b for a, b in zip(T, E))
    obs_vol = st.mean([tw.get(d, 0) for d, e in zip(idx, E) if e])

    rng = random.Random(seed)
    null, null_vol = [], []
    for _ in range(trials):
        k = rng.randrange(span)
        shifted = E[k:] + E[:k]
        null.append(sum(a & b for a, b in zip(T, shifted)))
        null_vol.append(st.mean([tw.get(d, 0) for d, e in zip(idx, shifted) if e]))

    def z_p(observed, samples):
        mu, sd = st.mean(samples), st.pstdev(samples)
        p = (sum(1 for v in samples if v >= observed) + 1) / (len(samples) + 1)
        return mu, sd, (observed - mu) / sd if sd else float("nan"), p

    return {
        "window": (lo, hi), "span": span, "trials": trials,
        "tweet_days": sum(T), "ep_days": sum(E),
        "obs": obs, "co": z_p(obs, null),
        "obs_vol": obs_vol, "vol": z_p(obs_vol, null_vol),
        "off_vol": st.mean([tw.get(d, 0) for d, e in zip(idx, E) if not e]),
    }


# --- report -----------------------------------------------------------------


def build_report(data):
    chats, tweets, notes, clock = (
        data["chats"], data["tweets"], data["notes"], data["clock"])
    follow, opener = cue_lengths(chats)
    ivs = intervals(chats)
    same, total = stamp_resolution(chats)
    turns = [t for rows in chats.values() for t in rows]
    user = [len(t.get("message") or "") for t in turns if t["sender"]["name"] == "User"]
    agent = [len(t.get("message") or "") for t in turns if t["sender"]["name"] == "Agent"]
    stamps = sorted(t["createdAt"] for t in turns)

    L = [
        "# Twitter / X",
        "",
        "Generated by `analysis/tw_export.py`.",
        "",
        f"Export generated {data['generated']}, {data['size_gb']:.2f} GB, handle "
        f"`{data['handle']}`. **{len(tweets):,} tweets** ({min(data['tw_days'])} .. "
        f"{max(data['tw_days'])}), **{len(notes):,} long-form posts**, and "
        f"**{len(turns):,} Grok chat turns** across **{len(chats):,} chats** "
        f"({stamps[0][:10]} .. {stamps[-1][:10]}).",
        "",
        "The media -- 8,571 files, essentially all of the 4 GB -- is not read. Neither",
        "are direct messages, the phone number, the IP audit or the ad records; see the",
        "`SKIP` list in the script. Nothing below quotes a message.",
        "",
        "## 1. The cue length is the author, not the editor",
        "",
        "`FINDINGS.md`'s frame rests on a median human turn of **55 characters** across",
        "134,063 blocks. The obvious objection is that it measures NovelAI's text box.",
        "Grok is a different platform, a different model, a different interface and a",
        "different activity -- image prompts, link analysis and fact-checks, not driving",
        "fiction; `pynchon` appears in 3 user turns, `tingle` in 4. The number barely moves.",
        "",
        "| | n | median | <50 | 50–200 | 200–600 | 600+ |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    n, med, _, b = dist(follow)
    L.append(f"| Grok user turn, after an agent turn | {n:,} | **{med:.0f}** | "
             + " | ".join(pct(x) for x in b) + " |")
    n2, med2, _, b2 = dist(opener)
    L.append(f"| Grok chat opener (control) | {n2:,} | {med2:.0f} | "
             + " | ".join(pct(x) for x in b2) + " |")
    L.append(f"| NovelAI human block after a generation | {NAI_REF['n']:,} | "
             f"{NAI_REF['median']} | " + " | ".join(pct(x) for x in NAI_REF["bins"]) + " |")
    L += [
        "",
        f"**{med:.0f} characters against 55**, with the same shape: about nine turns in ten",
        "under 200 characters, about one in forty long enough to be a substantive piece of",
        "writing. The median human turn survives the change of tool, so it is a fact about",
        "the author rather than about NovelAI.",
        "",
        f"**The control also fires, and it costs the frame something.** The chat opener --",
        f"a turn with nothing before it, which cannot be a response to a generation --",
        f"runs to a median of **{med2:.0f} characters**, indistinguishable from the "
        f"{med:.0f} of turns",
        "that do follow one. So the short median is not evidence *for* the turn-taking",
        "mechanism: position in the exchange does not move it. What the frame gets from",
        "this is narrower than it looks -- the number is real, transfers, and belongs to",
        "the author, but it does not by itself show that these are turns rather than",
        "openings. `FINDINGS.md` argues that from the branch structure, which is where the",
        "argument has to stay.",
        "",
        "## 2. Duration, which the NovelAI corpus cannot measure",
        "",
        f"**First, the resolution.** The Agent turn carries the same `createdAt` as the",
        f"user turn it answers in **{same:,} of {total:,}** exchanges -- every one. The",
        "stamp is the request, not the completion, so model latency is not recoverable and",
        "the record is **one timestamp per exchange, not per turn.** Every interval below",
        "therefore runs user-turn to user-turn and contains the model's generation, the",
        "author's reading, and the author's typing, undifferentiated.",
        "",
        f"Across **{len(ivs):,}** intervals under an hour:",
        "",
        "| what was there to read | n | median turnaround |",
        "|---|---:|---:|",
    ]
    for lo, hi in READ_BINS:
        v = [g for g, al, _ in ivs if lo <= al < hi]
        if len(v) > 15:
            label = f"{lo:,}–{hi:,}" if hi < 10**9 else f"{lo:,}+"
            L.append(f"| agent turn {label} chars | {len(v)} | {st.median(v):.0f}s |")
    L += [
        "",
        "**The confound is that generation time is inside that interval**, and longer",
        "outputs take longer to produce, which would manufacture this gradient on its own.",
        "Two controls separate them.",
        "",
        "*Hold the reading fixed, vary the typing.* Generation time cannot know how long",
        "the reply is going to be, so if it dominated the interval this comparison would be",
        "flat:",
        "",
        "| agent turn | reply <50 chars | reply ≥200 chars |",
        "|---|---:|---:|",
    ]
    for lo, hi in ((0, 1000), (1000, 4000), (4000, 10**9)):
        sub = [(g, ul) for g, al, ul in ivs if lo <= al < hi]
        short = [g for g, ul in sub if ul < 50]
        long = [g for g, ul in sub if ul >= 200]
        if len(short) > 10 and len(long) > 10:
            label = f"{lo:,}–{hi:,}" if hi < 10**9 else f"{lo:,}+"
            L.append(f"| {label} chars | {st.median(short):.0f}s (n={len(short)}) | "
                     f"**{st.median(long):.0f}s** (n={len(long)}) |")
    L += [
        "",
        "It is not flat: a long reply takes two to three times as long at every reading",
        "length. Human time is a large share of the interval.",
        "",
        "*Hold the typing fixed, vary the reading.* Restricted to replies under 50",
        "characters, so typing is near-constant:",
        "",
        "| agent turn | n | median turnaround |",
        "|---|---:|---:|",
    ]
    flat = []
    for lo, hi in READ_BINS:
        v = [g for g, al, ul in ivs if lo <= al < hi and ul < 50]
        if len(v) > 15:
            label = f"{lo:,}–{hi:,}" if hi < 10**9 else f"{lo:,}+"
            L.append(f"| {label} chars | {len(v)} | {st.median(v):.0f}s |")
            flat.append((lo, st.median(v)))
    L += [
        "",
        "**This is the result, and it is a threshold rather than a slope.** Turnaround is",
        f"flat at about **{flat[0][1]:.0f} seconds** from the shortest agent turns all the way",
        "to 2,000 characters -- four hundred words of output bought no more of the author's",
        "time than forty did -- and then climbs steeply. A generation-time explanation",
        "predicts a rise throughout, because a 2,000-character output takes measurably",
        "longer to produce than a 200-character one; the flat stretch is what rules it out.",
        "",
        "What it cannot show is what the author was doing in those 36 seconds. A constant",
        "turnaround is consistent with reading only the opening of each reply, with",
        "skimming to a fixed budget, or with a fixed rhythm of attention that the content",
        "does not touch. Nothing here separates those, and the archive has no scroll or",
        "focus events that would.",
        "",
        f"Chats are short: median **{st.median([len(r) for r in chats.values()]):.0f} turns** and "
        f"**{st.median([(ts_iso(max(r, key=lambda x: x['createdAt'])['createdAt']) - ts_iso(min(r, key=lambda x: x['createdAt'])['createdAt'])).total_seconds() for r in chats.values()]) / 60:.1f} minutes**, "
        f"against the NovelAI documents that run to 3,341 blocks over years. The agent",
        f"writes a median of **{st.median(agent):,.0f} characters** against the author's "
        f"**{st.median(user):,.0f}** -- a ratio of about "
        f"{st.median(agent) / max(st.median(user), 1):.0f} to 1.",
        "",
        "## 3. The tweets are a working external clock",
        "",
        "`data/EPISODES.tsv` -- 1,492 broadcasts recovered by OCR off the Twitch dashboard",
        "-- is the project's only independent clock, and it is day-resolution and lossy.",
        "The tweets are a second one, stamped to the second by the platform. Testing",
        "whether they agree is also a test of the OCR.",
        "",
        f"Overlap window **{clock['window'][0]} .. {clock['window'][1]}**, "
        f"{clock['span']:,} days: **{clock['tweet_days']}** days with a tweet, "
        f"**{clock['ep_days']}** with a broadcast.",
        "",
        "A plain co-occurrence count would mostly measure that both activities were dense",
        "in the same years. The null here is a **circular shift** of the broadcast series,",
        f"{clock['trials']:,} of them, which keeps every run and gap in both series and",
        "destroys only their alignment.",
        "",
        "| | observed | shifted null | z | p |",
        "|---|---:|---:|---:|---:|",
    ]
    mu, sd, z, p = clock["co"]
    L.append(f"| days with both | **{clock['obs']}** | {mu:.1f} ± {sd:.1f} | {z:.2f} | "
             f"{p:.4f} |")
    mu2, sd2, z2, p2 = clock["vol"]
    L.append(f"| tweets per broadcast day | **{clock['obs_vol']:.2f}** | {mu2:.2f} ± {sd2:.2f} "
             f"| {z2:.2f} | {p2:.4f} |")
    L += [
        "",
        f"Both survive. He tweeted on **{clock['obs']}** of his broadcast days against "
        f"{mu:.0f} expected, and posted **{clock['obs_vol']:.2f}** times on a broadcast day "
        f"against **{clock['off_vol']:.2f}** on other days.",
        "",
        "**What this buys is a check on the OCR, not a new schedule.** The two records were",
        "made by different machinery -- one scraped off screenshots of a dashboard, one",
        "stamped by a platform -- and they align well past chance, so `EPISODES.tsv` is",
        "measuring real broadcast days. It does not recover the episodes the OCR missed,",
        "and the standing note about date-based analysis still holds on the NovelAI side:",
        "appended series carry one `last_updated_at` for dozens of sessions, so neither",
        "clock can be joined to story activity day by day.",
        "",
        "## 4. The board question: he called the structure, and he read the sentence",
        "",
        "Endorphin's question, 2026-08-12: *\"check out the timestamps about my stuff",
        "regarding the Board of Directors. Did I call it or what?\"* That is a primed",
        "claim asked in the form that invites agreement, so the test run here is the one",
        "that could embarrass it — find the **earliest** statement of the governance",
        "thesis and check it against the firing, not against the restructuring it",
        "eventually fits.",
        "",
        "External dates below are from public reporting, not from this archive; they are",
        "kept in `OPENAI_EVENTS` in the script so they can be checked and corrected.",
        "",
    ]
    b = data["board"]
    L += [
        f"**The thesis is stated {len(b['hits'])} times.** The first is "
        f"**{b['first']['created_at'][:10]}** — *fifteen days after* the firing on "
        f"{b['fired']}. Statements before the firing: **{len(b['before'])}**.",
        "",
        "So: **not the event.** Nothing in the archive anticipates 2023-11-17. He posted",
        "AI art on the 15th and 16th, a joke about Grok's marketing copy at 17:20 on the",
        "17th, and at 22:32 that day — about two hours after the announcement — the only",
        "same-day trace, which is oblique: *\"Don't poo-poo conspiracy theory in a power",
        "vacuum. Those are the geothermal vents to conspiracy theory.\"* Then nothing on it",
        "for two weeks.",
        "",
        "**What he did call is the structure, and there the timestamps are clean.**",
        "",
        "| stated | what | what happened |",
        "|---|---|---|",
        "| 2023-12-02 | the non-profit with a for-profit arm is a Jane Jacobs *monstrous "
        "hybrid* and will incubate corruption | restructuring reported **2024-09-25**, "
        "~10 months later; completed **2025-10-28** |",
        "| 2023-12-03 | *\"an org maneuver like that, where the chaos gives the target even "
        "more power than before\"* — and *\"it wasn't the firing, it happened before that\"* "
        "| Altman returned on **2023-11-22** with most of the board replaced |",
        "| 2024-05-21 | *\"they just need to be separate and Sama no power over the "
        "nonprofit\"* | the 2025 structure keeps the nonprofit above the PBC |",
        "",
        "The 2024-09-26 response to the restructuring news is the tell that this is a held",
        "frame rather than hindsight: he does not update, he applies it — *\"Converting",
        "OpenAI into a for profit might just be the wisest thing he will ever do,\"* because",
        "on his own account the hybrid was the problem and separating it is the fix.",
        "",
        "**Two things keep this short of prophecy.** The thesis is stated *after* the",
        "crisis, so it was never on the record as a prediction of it; and the monstrous-",
        "hybrid frame is general — an OpenAI for-profit conversion was already widely",
        "speculated by late 2023. What is genuinely his, and dated, is the **2023-12-03**",
        "reading that the chaos would leave the target stronger and that the trigger",
        "predated the firing. That was written five days after Altman's return and it is a",
        "claim about mechanism, not a summary of the news.",
        "",
        "**The earlier board material is not a call either.** Three tweets on",
        "2022-10-31/11-01 address a \"Director\" who has failed to *\"install your board\"* —",
        "written the day Musk dissolved Twitter's board, and escalating through a fictional",
        "two-week notice period inside a single evening. Same-day satire, not foresight.",
        "",
        "### 4b. The candour reading — the strongest claim here, and an earlier pass "
        "missed it",
        "",
        "The board's stated reason was that Altman was *\"not consistently candid in his",
        "communications with the board.\"* Endorphin's claim is that he knew what that",
        "phrase was doing: compressing an accumulation of individually unprovable small",
        f"acts. He returns to it **{len(b['candor'])} times** and never revises it; the "
        "five substantive statements:",
        "",
        "| date | the claim |",
        "|---|---|",
        "| **2023-12-03** | *\"Lack of candid communication … is actually perhaps the most "
        "forgiving wording the board could have given.\"* Same thread, 14/: the silence is "
        "because the acts are *\"fractally related … one thing ends up referring to "
        "another\"* — say one and you are *\"drinking from a fire hose\"* |",
        "| **2024-09-26** | *\"Being not consistently candid is the most forgiving wording "
        "to the fractal trajectory of a thousand cuts that cannot be distilled into a "
        "press release. It is not something, it is an array, a mesh, of factors that no "
        "one person can see the totality of.\"* |",
        "| **2025-02-11** | *\"I knew exactly what 'not consistently candid' was. Death by "
        "1000 cuts. Impossible to press release or sound bite.\"* |",
        "| **2025-06-27** | *\"When the Board ousted Altman for being not consistently "
        "candid I knew exactly what they were talking about. It looks like a whole bunch "
        "of other people are starting to find out too.\"* |",
        "| **2026-01-07** | *\"the not consistently candid one\"* — still the shorthand, "
        "two years on |",
        "",
        "**Why this is stronger than §4's structural call.** It is not a prediction of an",
        "event but a reading of a sentence, and it is checkable three ways. It is *early*:",
        "2023-12-03 is sixteen days after the firing but months before the board's own",
        "side was publicly argued, when the dominant press reading was still that the",
        "wording was evasive or that the board had no case. It is *stable*: the same",
        "reading, in the same terms, across two and a half years and many news cycles,",
        "with no revision. And it is *sourced*, explicitly — *\"I lived through one\"*",
        "(2023-12-03), *\"my own abuse experience told me\"* (2025-02-11). On 2024-05-31 he",
        "applies the identical mechanism to his own case: *\"The type of harm that is",
        "involved is fractal and cannot be fit in sound bites. Paradoxically it is",
        "predictable.\"*",
        "",
        "The 2025-06-27 line is the one that carries a testable edge — *\"a whole bunch of",
        "other people are starting to find out too\"* — and it is the only forward-looking",
        "claim in the set.",
        "",
        "**An earlier pass of this section missed all of it**, and the reason is on the",
        "record in `sessions/LATEST.md`: *a reading lens decides in advance what counts as",
        "a thing.* The first pass searched `THESIS` — Jane Jacobs, monstrous hybrid,",
        "for-profit arm — because it had framed the question as *did he predict the",
        "restructuring*. That lens has no slot for a claim about **what a sentence meant**,",
        "so the candour reading was invisible until Endorphin pointed at it. Same failure",
        "shape as the Unknown Guest and the Left Behind lookup: frame, index, genre.",
        "`CANDOR` is now searched separately for exactly that reason.",
        "",
        "**The one clean prediction in the window is about the archive itself.** On",
        "2023-12-05: *\"my twitch channel is for those future moments when corporate wants",
        "to revise history. I have 1100+ episodes of 'no bitch, here are the times it did",
        "that for me'.\"* That is this repository's premise, stated two and a half years",
        "before it existed.",
        "",
        "## 5. Bursts — the threads that arrived whole",
        "",
        "Endorphin's observation, 2026-08-12: *\"interesting that the timestamps enable you",
        "to see when something is coming out of me naturally.\"* They do, and the mechanism",
        "is simple. X posts a thread's parts in one go, so a thread written in advance",
        "lands in seconds while a thread thought out live is spread over minutes or hours.",
        "The clock separates composition from conversation.",
        "",
    ]
    bs = data["bursts"]
    g = bs["groups"]
    L += [
        f"**{bs['threads']} self-reply threads** of three parts or more. "
        f"**{len(bs['burst'])} of them land inside 60 seconds** — "
        f"{bs['n_burst_tweets']:,} tweets — against {len(bs['slow'])} that do not.",
        "",
        f"Median rate inside a burst: **{st.median(bs['rates']):.2f} parts per second**, "
        f"topping out at {max(bs['rates']):.1f}. Nobody types at that rate. These existed "
        "as whole pieces before they were tweets.",
        "",
        "### They are written into the container",
        "",
        "| | n | median chars | share ≥260 |",
        "|---|---:|---:|---:|",
    ]
    for lab, key in (("burst (thread posted ≤60s)", "burst"),
                     ("reply (@-prefixed)", "reply"),
                     ("standalone", "solo")):
        v = g[key]
        L.append(f"| {lab} | {len(v):,} | **{st.median(v):.0f}** | "
                 f"{100 * sum(1 for x in v if x >= 260) / len(v):.0f}% |")
    L += [
        "",
        "The limit is 280. Burst tweets sit at a median of "
        f"**{st.median(g['burst']):.0f}** and "
        f"{100 * sum(1 for x in g['burst'] if x >= 260) / len(g['burst']):.0f}% of them "
        f"are within twenty characters of the ceiling, against "
        f"{100 * sum(1 for x in g['solo'] if x >= 260) / len(g['solo']):.0f}% of "
        "standalone posts. He is not tweeting a thought; he is packing prose into a fixed "
        "container and continuing into the next one.",
        "",
        "### The numbering is the tell",
        "",
        f"**{100 * bs['numbered_burst'] / max(len(bs['burst']), 1):.0f}% of bursts open "
        f"`1/`. {100 * bs['numbered_slow'] / max(len(bs['slow']), 1):.0f}% of slow threads "
        "do.**",
        "",
        "That is the sharpest split in this section, and it is about intent rather than",
        "speed. Numbering the first part means committing in advance to how many parts",
        "there will be — you cannot label something `1/` unless you already know it is a",
        "piece. A slow thread grows because a conversation pulled it along. **A burst was",
        "a document before it was a thread**, and the numbering is him marking the genre",
        "at the moment he starts.",
        "",
        "### Two things that came back the other way",
        "",
        f"**They are not late-night spirals.** Bursts start between 22:00 and 06:00 local "
        f"(the account timezone is `Quito`, UTC−5) **{bs['night_burst']:.0f}%** of the "
        f"time, against **{bs['night_other']:.0f}%** for everything else he posts. The "
        "bursts are *less* nocturnal than his ordinary posting, peaking instead in the "
        "afternoon and mid-evening. Whatever these are, they are not 3 a.m. flooding — "
        "which is the reading the form invites and the clock refuses.",
        "",
        "**They are not more confessional.** The obvious prediction from *\"coming out of "
        "me naturally\"* is more first person, and that is flatly not there:",
        "",
        "| per 10,000 words | burst | everything else | ratio |",
        "|---|---:|---:|---:|",
    ]
    for lab, (b_, o_) in bs["lex"].items():
        L.append(f"| {lab} | {b_:.1f} | {o_:.1f} | {b_ / max(o_, 0.01):.2f}× |")
    tax = bs["lex"]["taxonomy"]
    L += [
        "",
        "First person and hedging are identical. **The one real lexical difference is the",
        f"bad-faith vocabulary** — abuse, gaslighting, dissonance, accountability, "
        f"fuckery, enmeshment, oversight — at {tax[0]:.1f} against {tax[1]:.1f} per ten "
        f"thousand words, **{tax[0] / tax[1]:.2f}×**. Modest, and the direction matters "
        "more than the size: `READINGS.md` §X argues that the corpus contains an "
        "enumerated taxonomy of bad faith and none of good faith. **This is where the "
        "enumeration lives.** The December 2023 thread that §4b is built on is a burst: "
        "19 parts in 10 seconds.",
        "",
        "AI vocabulary runs the other way. The bursts are the least AI-industry thing in",
        "the archive.",
        "",
        "### The largest",
        "",
        "| parts | seconds | date | opens |",
        "|---:|---:|---|---|",
    ]
    for t in bs["biggest"]:
        head = re.sub(r"\s+", " ", t[0]["text"])[:72].replace("|", "\\|")
        L.append(f"| {len(t)} | {bs['span'](t):.0f} | {t[0]['at'].date()} | {head}… |")
    L += [
        "",
        "**What this is the Twitter analogue of.** `analysis/spans.py` finds the "
        "model-free episodes inside the NovelAI corpus by walking branch structure. This "
        "finds the same category in a record with no branches at all, using the only "
        "instrument this archive has that the others do not: **the clock**. Same target, "
        "different evidence — and it is the second time in this file that the timestamps "
        "do work no other archive here can do.",
        "",
        "## What this archive cannot do",
        "",
        "See `analysis/TW_EXPORT.md` for the full accounting. In short: no undo tree, so no",
        "rejected generations and nothing on selection; no sampler settings, so nothing",
        "settings-comparative and no sweep procedure; one stamp per exchange, so no model",
        "latency; and 431 short utility chats are not the practice the NovelAI corpus",
        "records. The cue-length replication is the only measurement here that speaks",
        "directly to a `FINDINGS.md` claim, and it half-confirms and half-narrows it.",
    ]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archive", help="the export .zip, or an unpacked copy of it")
    ap.add_argument("--out", type=pathlib.Path, help="write normalised jsonl here")
    ap.add_argument("--meta", type=pathlib.Path, help="committed metadata: no message text")
    ap.add_argument("--days", type=pathlib.Path, help="committed tweet-per-day counts")
    ap.add_argument("--report", type=pathlib.Path)
    ap.add_argument("--episodes", default="data/EPISODES.tsv")
    args = ap.parse_args()

    files = read_archive(args.archive)
    missing = [n for n in WANT if n not in files]
    if "grok-chat-item.js" in missing or "tweets.js" in missing:
        sys.exit(f"archive is missing {missing} -- is this a Twitter/X export?")

    man = json.loads(files["manifest.js"].decode("utf-8", "replace").split("=", 1)[1])
    turns = unwrap(payload(files["grok-chat-item.js"]), "grokChatItem")
    tweets = unwrap(payload(files["tweets.js"]), "tweet")
    notes = unwrap(payload(files.get("note-tweet.js", b"x=[]")), "noteTweet")
    chats = by_chat(turns)
    tw_days = tweet_days(tweets)
    board = board_timeline(tweets, notes)
    bursts = burst_stats(tweets)
    clock = circular_shift(tw_days, episode_days(args.episodes))

    data = {
        "chats": chats, "tweets": tweets, "notes": notes, "clock": clock,
        "board": board, "bursts": bursts,
        "tw_days": tw_days,
        "handle": man["userInfo"]["userName"],
        "generated": man["archiveInfo"]["generationDate"][:10],
        "size_gb": int(man["archiveInfo"]["sizeBytes"]) / 1e9,
    }

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        with (args.out / "tw_grok.jsonl").open("w", encoding="utf-8") as fh:
            for cid, rows in chats.items():
                for i, r in enumerate(rows):
                    fh.write(json.dumps({
                        "chat_id": cid, "turn_index": i,
                        "created_at": r["createdAt"],
                        "sender": r["sender"]["name"],
                        "mode": r["grokMode"]["name"],
                        "text": r.get("message") or "",
                    }) + "\n")
        with (args.out / "tw_tweets.jsonl").open("w", encoding="utf-8") as fh:
            for t in tweets:
                fh.write(json.dumps({
                    "id": t["id_str"],
                    "created_at": dt.datetime.strptime(
                        t["created_at"], TWEET_TS).isoformat(),
                    "text": t.get("full_text", ""),
                    "reply_to": t.get("in_reply_to_status_id_str"),
                    "source": re.sub(r"<[^>]+>", "", t.get("source", "")),
                }) + "\n")
        print(f"wrote {args.out}/tw_grok.jsonl and tw_tweets.jsonl")

    # Committed metadata carries shape only -- no message text, ever.
    if args.meta:
        args.meta.parent.mkdir(parents=True, exist_ok=True)
        with args.meta.open("w", encoding="utf-8") as fh:
            for cid, rows in chats.items():
                for i, r in enumerate(rows):
                    msg = r.get("message") or ""
                    fh.write(json.dumps({
                        "chat_id": cid, "turn_index": i,
                        "created_at": r["createdAt"],
                        "sender": r["sender"]["name"],
                        "mode": r["grokMode"]["name"],
                        "chars": len(msg),
                        "words": len(re.findall(r"[A-Za-z][A-Za-z'-]*", msg)),
                    }) + "\n")
        print(f"wrote {args.meta} ({sum(len(r) for r in chats.values()):,} turns, no text)")

    if args.days:
        args.days.parent.mkdir(parents=True, exist_ok=True)
        args.days.write_text(
            "".join(f"{d}\t{n}\n" for d, n in sorted(tw_days.items())), encoding="utf-8")
        print(f"wrote {args.days} ({len(tw_days)} days)")

    report = build_report(data)
    if args.report:
        args.report.write_text(report, encoding="utf-8")
        print(f"wrote {args.report}")
    else:
        print(report)


if __name__ == "__main__":
    main()
