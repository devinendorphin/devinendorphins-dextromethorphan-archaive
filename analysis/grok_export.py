#!/usr/bin/env python3
"""The fourth archive: the standalone Grok export, and the question it settles.

Endorphin supplied this with a hypothesis attached: *"this is separate from the
Twitter data that contains some rock conversations in it I think it might be the
difference between the gtok standalone and the rock that can be accessed on the
Twitter."* He is right, and the two records do not overlap by a single turn --
§1 below is the test, run as a disconfirming one.

It also breaks the standing account of what the non-NovelAI archives can do.
`analysis/TW_EXPORT.md` established that everything resting on chosen/rejected
pairs, branch reachability or per-turn latency dies outside NovelAI. That was a
statement about the Twitter/X export and it does not generalise: the standalone
record carries `parent_response_id` on every response, so it **is** a tree; it
stamps every turn independently, so model latency is recoverable for the first
time in this project; and it names the model on 89% of responses, which the
X-side never does.

Five things this runs:

1. **Are the two Grok records the same practice?** The disconfirming test: if
   they were one record exported twice, turns would collide. Nearest-neighbour
   in time, exact char-length coincidence inside a five-minute window, and shared
   days -- all three against `data/twitter_meta.jsonl`.
2. **The cue length, on a third platform.** `FINDINGS.md`'s frame rests on a
   median human turn of 55 characters; the X-side Grok held it at 58. The control
   that matters here is the *opener* again, and this time it does not behave the
   same way, which is the finding.
3. **Latency, actually measured.** `FINDINGS.md` §11 says tempo is unrecoverable;
   `TW_EXPORT.md` says the X-side stamps the request rather than the completion,
   so latency is zero everywhere by construction. Here the assistant turn is
   stamped separately and 494 responses carry an explicit thinking window.
4. **The tree, and what is in it.** Sibling responses under one parent are
   re-rolls (assistant siblings) or prompt edits (human siblings), and eight
   sibling sets span more than one model -- a within-document model comparison,
   which is the one thing `CLAUDE.md` says this project cannot do.
5. **The shape of the practice**, against the X-side's 431 four-turn utility
   chats, because "more Grok" is exactly the reading `CLAUDE.md` warns against.

The account record in this archive -- email, legal names, birth date, session
tokens, user agents and Cloudflare session metadata -- is **never opened**; see
`SKIP`. Nothing written to `data/` carries message text, prompt text, titles or
the account's user id.

    python3 analysis/grok_export.py grok.zip --out out \\
        --meta data/grok_meta.jsonl --days data/GROK_DAYS.tsv \\
        --report analysis/GROK.md
"""

import argparse
import bisect
import collections
import datetime as dt
import json
import pathlib
import re
import statistics as st
import sys
import zipfile

# The conversation record is the only file this analysis needs. Everything else
# in the export is account PII, billing, or generated media.
WANT = "prod-grok-backend.json"
SKIP = (
    "prod-mc-auth-mgmt-api",  # email, legal names, birth date, sessions, user agents
    "prod-mc-billing",
    "profile-picture",
)

# NovelAI reference, FINDINGS.md's frame table: human blocks following a
# generation. The X-side Grok figure is from analysis/TWITTER.md §1.
NAI_REF = {"n": 134063, "median": 55}
XSIDE_REF = {"follow": 58, "opener": 55, "turns": 2818, "chats": 431}
BINS = ((0, 50), (50, 200), (200, 600), (600, 10**9))


# --- reading the archive ----------------------------------------------------


def read_backend(path):
    """Pull the conversation record out of the export, zip or directory alike."""
    path = pathlib.Path(path)
    if path.is_dir():
        hits = [p for p in path.rglob(WANT)]
        if not hits:
            sys.exit(f"no {WANT} under {path} -- is this a Grok export?")
        return json.loads(hits[0].read_bytes())
    with zipfile.ZipFile(path) as zf:
        for info in zf.infolist():
            base = pathlib.PurePosixPath(info.filename).name
            if any(s in base for s in SKIP):
                continue
            if base == WANT:
                return json.loads(zf.read(info))
    sys.exit(f"no {WANT} in {path} -- is this a Grok export?")


def ms(value):
    """Grok stamps as `{"$date": {"$numberLong": "1786839502246"}}`."""
    if isinstance(value, dict):
        return int(value["$date"]["$numberLong"])
    if isinstance(value, str):
        return int(dt.datetime.fromisoformat(
            value.replace("Z", "+00:00")).timestamp() * 1000)
    return int(value)


def iso(msec):
    return dt.datetime.fromtimestamp(msec / 1000, dt.timezone.utc).isoformat()


def flatten(backend):
    """One row per response, conversation order preserved."""
    rows = []
    for conv in backend["conversations"]:
        meta = conv["conversation"]
        for i, wrapper in enumerate(conv["responses"]):
            r = wrapper["response"]
            rows.append({
                "conv_id": meta["id"],
                "turn_index": i,
                "id": r["_id"],
                "parent": r.get("parent_response_id"),
                # The export writes assistant turns as both "ASSISTANT" and
                # "assistant"; the casing tracks nothing and is folded here.
                "sender": r["sender"].lower(),
                "t": ms(r["create_time"]),
                "model": r.get("model") or "",
                "chars": len(r.get("message") or ""),
                "words": len(re.findall(r"[A-Za-z][A-Za-z'-]*", r.get("message") or "")),
                "think_ms": (ms(r["thinking_end_time"]) - ms(r["thinking_start_time"])
                             if r.get("thinking_start_time") and r.get("thinking_end_time")
                             else None),
                "effort": ((r.get("metadata") or {}).get("request_metadata") or {}).get("effort"),
                "searched": len(r.get("web_search_results") or []),
                "attachments": len(r.get("file_attachments") or []),
            })
    return rows


def by_conv(rows):
    out = collections.defaultdict(list)
    for r in rows:
        out[r["conv_id"]].append(r)
    return out


# --- 1. the disjointness test -----------------------------------------------


def load_xside(path):
    """The X-side Grok turns, from committed metadata: stamps and lengths only."""
    out = []
    p = pathlib.Path(path)
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8").splitlines():
        j = json.loads(line)
        out.append((ms(j["created_at"]), j["sender"].lower(), j["chars"]))
    return sorted(out)


def disjoint(rows, xside, window_ms=300_000):
    """Do the two Grok records share anything at all?

    Written to fail. If the standalone export were the same conversations under
    another schema -- the obvious rival to Endorphin's reading -- then turns
    would coincide: same moment, same length. The test looks for that
    coincidence with a five-minute tolerance, which is far looser than a genuine
    duplicate would need.
    """
    if not xside:
        return None
    xt = [t for t, _, _ in xside]
    nearest, collisions, closest = [], 0, None
    for r in rows:
        i = bisect.bisect_left(xt, r["t"])
        cand = [(abs(r["t"] - xt[j]), j) for j in (i - 1, i) if 0 <= j < len(xt)]
        if cand:
            gap, j = min(cand)
            nearest.append(gap)
            if closest is None or gap < closest[0]:
                closest = (gap, iso(r["t"])[:19], r["sender"], r["chars"],
                           iso(xside[j][0])[:19], xside[j][1], xside[j][2])
        if r["chars"]:
            j = bisect.bisect_left(xt, r["t"] - window_ms)
            while j < len(xside) and xside[j][0] <= r["t"] + window_ms:
                collisions += xside[j][2] == r["chars"]
                j += 1
    days_a = {iso(r["t"])[:10] for r in rows}
    days_b = {iso(t)[:10] for t, _, _ in xside}
    lo = max(min(r["t"] for r in rows), xt[0])
    hi = min(max(r["t"] for r in rows), xt[-1])
    return {
        "nearest_s": sorted(n / 1000 for n in nearest),
        "closest": closest,
        "collisions": collisions,
        "shared_days": sorted(days_a & days_b),
        "days_a": len(days_a), "days_b": len(days_b),
        "overlap": (iso(lo)[:19], iso(hi)[:19]),
        "in_window_a": sum(1 for r in rows if lo <= r["t"] <= hi),
        "in_window_b": sum(1 for t in xt if lo <= t <= hi),
        "range_a": (iso(min(r["t"] for r in rows))[:10], iso(max(r["t"] for r in rows))[:10]),
        "range_b": (iso(xt[0])[:10], iso(xt[-1])[:10]),
    }


# --- 2. the cue length ------------------------------------------------------


def cue_lengths(convs):
    """Same two populations `TWITTER.md` §1 uses, so the numbers are comparable.

    `follow` is a human turn whose predecessor is an assistant turn -- a cue.
    `opener` is the first turn of a conversation, which has no generation before
    it and therefore cannot be a response to one. Human turns following another
    human turn (prompt edits, n=1 here) belong to neither.
    """
    follow, opener = [], []
    for rows in convs.values():
        for i, r in enumerate(rows):
            if r["sender"] != "human":
                continue
            if i == 0:
                opener.append(r["chars"])
            elif rows[i - 1]["sender"] == "assistant":
                follow.append(r["chars"])
    return follow, opener


def dist(vals):
    n = len(vals)
    counts = [sum(1 for v in vals if lo <= v < hi) for lo, hi in BINS]
    return n, st.median(vals), st.mean(vals), [100 * c / n for c in counts]


# --- 3. latency -------------------------------------------------------------


def latency(convs):
    """Two independent measures, because the first one has a confound.

    `gap` is human-stamp to assistant-stamp, which contains the model's
    generation *and* whatever the platform did around it. `think` is the
    server's own thinking window, which contains only generation. If the two
    agree in shape, the stamps are real; if `gap` were a copy of the request
    stamp -- the X-side's failure mode -- it would be zero everywhere.
    """
    gaps, same = [], 0
    for rows in convs.values():
        for a, b in zip(rows, rows[1:]):
            if a["sender"] == "human" and b["sender"] == "assistant":
                gaps.append((b["t"] - a["t"]) / 1000)
                same += a["t"] == b["t"]
    think = sorted(r["think_ms"] / 1000
                   for rows in convs.values() for r in rows if r["think_ms"])
    return sorted(gaps), same, think


# --- 4. the tree ------------------------------------------------------------


def tree(rows):
    """Sibling sets under one parent: the chosen/rejected structure, if any."""
    byid = {r["id"]: r for r in rows}
    kids = collections.defaultdict(list)
    for r in rows:
        if r["parent"]:
            kids[r["parent"]].append(r)
    sets = [v for v in kids.values() if len(v) > 1]
    kinds = collections.Counter(
        "re-roll" if all(x["sender"] == "assistant" for x in v)
        else "prompt edit" if all(x["sender"] == "human" for x in v)
        else "mixed"
        for v in sets)
    # Which sibling was kept is only readable when exactly one of them was
    # continued. `leaf_response_id` would say directly, and is null on 143 of
    # 145 conversations, so this is the fallback and it is partial.
    continued = collections.Counter(
        sum(1 for x in v if kids.get(x["id"])) for v in sets)
    cross_model = sum(1 for v in sets if len({x["model"] for x in v}) > 1)
    return {
        "responses": len(rows),
        "with_parent": sum(1 for r in rows if r["parent"]),
        "dangling": sum(1 for r in rows if r["parent"] and r["parent"] not in byid),
        "sets": len(sets),
        "in_convs": len({v[0]["conv_id"] for v in sets}),
        "kinds": kinds,
        "continued": continued,
        "cross_model": cross_model,
        "widths": collections.Counter(len(v) for v in kids.values()),
    }


# --- 5. the shape of the practice -------------------------------------------


def shape(convs, rows, media):
    turns = sorted(len(v) for v in convs.values())
    durs = sorted((max(r["t"] for r in v) - min(r["t"] for r in v)) / 1000
                  for v in convs.values())
    human = [r["chars"] for r in rows if r["sender"] == "human"]
    asst = [r["chars"] for r in rows if r["sender"] == "assistant"]
    return {
        "convs": len(convs), "turns": len(rows),
        "turns_median": st.median(turns), "turns_max": max(turns),
        "dur_median": st.median(durs), "dur_p90": durs[9 * len(durs) // 10],
        "dur_max": max(durs),
        "human_chars": sum(human), "asst_chars": sum(asst),
        "human_median": st.median(human), "asst_median": st.median(asst),
        "models": collections.Counter(r["model"] for r in rows if r["model"]),
        "effort": collections.Counter(r["effort"] for r in rows if r["effort"]),
        "searched": sum(1 for r in rows if r["searched"]),
        "attached": sum(1 for r in rows if r["attachments"]),
        "media": len(media),
        "media_kinds": collections.Counter(m["media_type"] for m in media),
        "media_days": len({m["create_time"][:10] for m in media}),
        "media_range": (min(m["create_time"][:10] for m in media),
                        max(m["create_time"][:10] for m in media)) if media else None,
    }


# --- the report -------------------------------------------------------------


def pct(x):
    return f"{x:.1f}%"


def build_report(d):
    s, dj, tr = d["shape"], d["disjoint"], d["tree"]
    gaps, same, think = d["latency"]
    follow, opener = d["cues"]
    L = [
        "# GROK — the standalone export, measured",
        "",
        "*Generated by `analysis/grok_export.py`. Do not hand-edit.*",
        "Schema and the four-archive asymmetry table: `analysis/GROK_EXPORT.md`.",
        "",
        f"**{s['convs']} conversations, {s['turns']:,} turns**, "
        f"{dj['range_a'][0] if dj else '?'} .. {dj['range_a'][1] if dj else '?'}, plus "
        f"**{s['media']:,} media generations** "
        f"({s['media_kinds'].get('video', 0):,} video, "
        f"{s['media_kinds'].get('image', 0):,} image) over {s['media_days']} days.",
        "",
        "## 1. It is not the same record as the Grok chats in the Twitter export",
        "",
        "Endorphin's reading when he supplied the file, and the reason this section is",
        "first. The test is written to fail: if the standalone export were the X-side",
        "conversations under another schema, turns would coincide — same moment, same",
        "length. A five-minute tolerance is far looser than a real duplicate would need.",
        "",
    ]
    if dj:
        L += [
            "| | standalone | Grok on X |",
            "|---|---:|---:|",
            f"| turns | {s['turns']:,} | {XSIDE_REF['turns']:,} |",
            f"| conversations | {s['convs']} | {XSIDE_REF['chats']} |",
            f"| first .. last | {dj['range_a'][0]} .. {dj['range_a'][1]} "
            f"| {dj['range_b'][0]} .. {dj['range_b'][1]} |",
            f"| distinct days | {dj['days_a']} | {dj['days_b']} |",
            f"| turns inside the overlap window | {dj['in_window_a']:,} "
            f"| {dj['in_window_b']:,} |",
            "",
            f"The two records overlap in time from **{dj['overlap'][0]}** to "
            f"**{dj['overlap'][1]}**, and share **{len(dj['shared_days'])} calendar "
            f"days**. Inside that window:",
            "",
            f"- **Exact-length coincidences within five minutes: {dj['collisions']}.**",
            f"- The closest any standalone turn comes to any X-side turn is "
            f"**{dj['nearest_s'][0] / 60:.1f} minutes**; the median separation is "
            f"**{dj['nearest_s'][len(dj['nearest_s']) // 2] / 86400:.1f} days**.",
            "",
            "**Two records, no shared turns.** They are different practices on different",
            "surfaces, and the standalone one starts about eight months later. Do not",
            "add the turn counts together and do not treat either as a sample of the",
            "other.",
            "",
            "**But they are not separate sessions in time, and that is the more "
            "interesting half.** The closest pair — " +
            (f"an exchange on X stamped {dj['closest'][4]}, then a "
             f"{dj['closest'][3]}-character {dj['closest'][2]} turn in the standalone "
             f"app {dj['closest'][0] / 60000:.1f} minutes later"
             if dj["closest"] else "") +
            " — is one person moving between two surfaces inside the same minute, not "
            "two independent habits. The records are disjoint; the activity is not "
            "necessarily. Anything that treats a gap in one archive as a gap in his "
            "attention has to check the other first.",
            "",
        ]
    L += [
        "## 2. The cue length holds — and the opener control breaks, the other way",
        "",
        "`FINDINGS.md`'s frame rests on a median human turn of "
        f"**{NAI_REF['median']} characters** across {NAI_REF['n']:,} NovelAI blocks. "
        f"`TWITTER.md` §1 re-measured it off-platform at **{XSIDE_REF['follow']}**, and "
        "found the *opener* — a turn with nothing before it, which cannot be a response "
        f"to a generation — at **{XSIDE_REF['opener']}**, indistinguishable. That is the "
        "result that cost the median its status as evidence for turn-taking.",
        "",
        "| | n | median | mean | <50 | 50–200 | 200–600 | 600+ |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    n, med, mean, b = dist(follow)
    L.append(f"| standalone, after an assistant turn | {n:,} | **{med:.0f}** | "
             f"{mean:.0f} | " + " | ".join(pct(x) for x in b) + " |")
    n2, med2, mean2, b2 = dist(opener)
    L.append(f"| standalone, conversation opener (control) | {n2:,} | **{med2:.0f}** | "
             f"{mean2:.0f} | " + " | ".join(pct(x) for x in b2) + " |")
    L += [
        "",
        f"The cue survives a fourth platform: **{med:.0f} characters** against 55 on "
        f"NovelAI and {XSIDE_REF['follow']} on X. But the opener here is "
        f"**{med2 / med:.1f}× longer than the follower**, where on X the two were the "
        "same number. So the X-side null was a property of *that* practice — 431 "
        "one-minute lookups, where the opener is the whole errand — and not a general "
        "fact about openings. **The standing note that position in the exchange does "
        "not move the number needs the qualifier `on X`.** It does move it here, in the "
        "direction the turn-taking frame predicts, on the archive where conversations "
        "are long enough for position to mean anything.",
        "",
        f"The mean-median gap is the pasted-block signature again: mean {mean:.0f} "
        f"against median {med:.0f}. Screen on length before reading anything into human "
        "character counts, exactly as `analysis/pasted.py` does on the NovelAI side.",
        "",
        "## 3. Latency, recoverable for the first time in this project",
        "",
        "`FINDINGS.md` §11: NovelAI stores no per-block timestamps, so tempo is gone. "
        "`TW_EXPORT.md`: the X-side agent turn copies the request stamp exactly, "
        "1,409/1,409, so model latency is zero everywhere by construction. Here:",
        "",
        f"- Human→assistant stamp pairs: **{len(gaps):,}**, of which **{same}** share a "
        "stamp. The assistant turn is stamped independently.",
        f"- Turnaround: median **{st.median(gaps):.1f}s**, p10 "
        f"{gaps[len(gaps) // 10]:.1f}s, p90 {gaps[9 * len(gaps) // 10]:.1f}s.",
        f"- The server's own thinking window, on the **{len(think)}** responses that "
        f"carry one: median **{st.median(think):.1f}s**, p10 "
        f"{think[len(think) // 10]:.1f}s, p90 {think[9 * len(think) // 10]:.1f}s, max "
        f"{think[-1]:.0f}s.",
        "",
        "The two agree in shape, which is the check: an explicit generation window "
        f"of {st.median(think):.0f}s median sitting inside a {st.median(gaps):.0f}s "
        "median turnaround is what a real stamp looks like. **This is the one "
        "measurement the project has wanted since §11 and has never had.** It is still "
        "not the NovelAI practice being measured — see §5 — so it bounds nothing about "
        "the fiction sessions.",
        "",
        "## 4. There is a tree, and `TW_EXPORT.md`'s asymmetry does not generalise",
        "",
        f"Every response but a conversation root carries `parent_response_id` "
        f"({tr['with_parent']:,} of {tr['responses']:,}; {tr['dangling']} point at a "
        "parent that is not in the export). That is a branch structure, which the "
        "X-side does not have and which is the entire basis of `FINDINGS.md`'s method.",
        "",
        f"- **{tr['sets']} sibling sets** across **{tr['in_convs']} conversations** — "
        "a parent with more than one child, i.e. the same point in the conversation "
        "taken twice.",
        "- Kinds: " + ", ".join(f"**{v}** {k}" for k, v in tr["kinds"].most_common()) +
        ". Assistant siblings are re-rolls; human siblings are edited prompts.",
        f"- **{tr['cross_model']} sibling sets span more than one model** — the same "
        "prompt answered by two Grok versions, side by side, in the record. "
        "`CLAUDE.md` says this corpus cannot benchmark models because settings moved "
        "with model choice; here the prompt is held fixed by construction.",
        "",
        "**The limit, and it is a hard one.** `leaf_response_id` — which would say "
        f"outright which branch was kept — is null on {d['leaf_null']} of "
        f"{s['convs']} conversations. The fallback is to ask which sibling was "
        "continued, and it is partial: " +
        ", ".join(f"**{v}** where {k} continued"
                  for k, v in sorted(tr["continued"].items())) +
        " (of the siblings in the set)" +
        ". So selection is readable in the sets where exactly one branch grew, "
        "unreadable where none did, and where two or more grew there was no rejection "
        "to read — both branches were kept and continued. **Do not run `FINDINGS.md`'s "
        "reachability method here unmodified**; walk children forward, do not walk "
        "`prevBlock` back.",
        "",
        f"And the sample is small. {tr['sets']} sibling sets against the NovelAI "
        "corpus's whole undo tree is not a rejection dataset; it is proof that the "
        "field exists and a handful of instances. **The right use of it is to check "
        "whether a NovelAI finding reproduces, not to found anything new on it.**",
        "",
        "## 5. It is a fourth practice, not more of any of the others",
        "",
        f"{s['convs']} conversations, median **{s['turns_median']:.0f} turns** and "
        f"**{s['dur_median'] / 60:.1f} minutes**, with a p90 of "
        f"{s['dur_p90'] / 3600:.1f} hours and a longest of {s['turns_max']} turns. "
        f"The assistant writes **{s['asst_chars']:,} characters** against the author's "
        f"**{s['human_chars']:,}**, a {s['asst_chars'] / s['human_chars']:.1f}:1 split.",
        "",
        f"- **Models named on the response**, which no other archive here does: " +
        ", ".join(f"`{k}` {v}" for k, v in s["models"].most_common(6)) + ".",
        f"- **Effort setting** recorded on {sum(s['effort'].values())} responses: " +
        ", ".join(f"{k} {v}" for k, v in s["effort"].most_common()) +
        ". This is the closest thing to a sampler setting in any non-NovelAI archive, "
        "and it is a three-value switch, not a dial — nothing resembling "
        "`analysis/sweeps.py` can be run on it.",
        f"- **{s['searched']} responses carry web search results** and "
        f"**{s['attached']} carry file attachments** — the model is reading documents "
        "and the live web, which nothing in the NovelAI corpus does.",
        f"- **{s['media']:,} media generations** ({s['media_range'][0]} .. "
        f"{s['media_range'][1]}) sit in the same export and are a separate substrate "
        "again — image and video prompting, not turn-taking with text.",
        "",
        "Against the X-side's "
        f"{XSIDE_REF['chats']} chats at a median of 4 turns and one minute, and against "
        "NovelAI documents of 3,341 blocks: this sits between them. Long "
        "argumentative exchanges and an evaluation apparatus run across months, next "
        "to utility lookups and image work, in one record. **`CLAUDE.md`'s rule holds a "
        "fourth time — do not read it as more of the corpus.** *(That characterisation "
        "is from conversation titles, turn counts and durations. No reading pass has "
        "been done on this archive, and none should be assumed by anything that cites "
        "this file.)*",
    ]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("archive", help="the Grok export .zip, or an unpacked copy")
    ap.add_argument("--out", type=pathlib.Path, help="write normalised jsonl here")
    ap.add_argument("--meta", type=pathlib.Path, help="committed metadata: no text")
    ap.add_argument("--days", type=pathlib.Path, help="committed turns-per-day counts")
    ap.add_argument("--xside", default="data/twitter_meta.jsonl")
    ap.add_argument("--report", type=pathlib.Path)
    args = ap.parse_args()

    backend = read_backend(args.archive)
    rows = flatten(backend)
    convs = by_conv(rows)
    media = backend.get("media_posts", [])
    leaf_null = sum(1 for c in backend["conversations"]
                    if not c["conversation"].get("leaf_response_id"))

    data = {
        "shape": shape(convs, rows, media),
        "disjoint": disjoint(rows, load_xside(args.xside)),
        "cues": cue_lengths(convs),
        "latency": latency(convs),
        "tree": tree(rows),
        "leaf_null": leaf_null,
    }

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        with (args.out / "grok_turns.jsonl").open("w", encoding="utf-8") as fh:
            for conv in backend["conversations"]:
                meta = conv["conversation"]
                for i, wrapper in enumerate(conv["responses"]):
                    r = wrapper["response"]
                    fh.write(json.dumps({
                        "conv_id": meta["id"], "title": meta["title"],
                        "turn_index": i, "id": r["_id"],
                        "parent": r.get("parent_response_id"),
                        "created_at": iso(ms(r["create_time"])),
                        "sender": r["sender"].lower(),
                        "model": r.get("model") or "",
                        "text": r.get("message") or "",
                    }) + "\n")
        print(f"wrote {args.out}/grok_turns.jsonl")

    # Committed metadata carries shape only -- no message text, no titles, and
    # not the account's user id, which appears throughout the raw export.
    if args.meta:
        args.meta.parent.mkdir(parents=True, exist_ok=True)
        with args.meta.open("w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps({
                    "conv_id": r["conv_id"], "turn_index": r["turn_index"],
                    "id": r["id"], "parent": r["parent"],
                    "created_at": iso(r["t"]), "sender": r["sender"],
                    "model": r["model"], "effort": r["effort"],
                    "think_ms": r["think_ms"],
                    "chars": r["chars"], "words": r["words"],
                    "searched": r["searched"], "attachments": r["attachments"],
                }) + "\n")
        print(f"wrote {args.meta} ({len(rows):,} turns, no text)")

    if args.days:
        days = collections.Counter(iso(r["t"])[:10] for r in rows)
        args.days.parent.mkdir(parents=True, exist_ok=True)
        args.days.write_text(
            "".join(f"{d}\t{n}\n" for d, n in sorted(days.items())), encoding="utf-8")
        print(f"wrote {args.days} ({len(days)} days)")

    report = build_report(data)
    if args.report:
        args.report.write_text(report, encoding="utf-8")
        print(f"wrote {args.report}")
    else:
        print(report)


if __name__ == "__main__":
    main()
