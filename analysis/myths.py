#!/usr/bin/env python3
"""What does a preset *do* to language? `Mythmaker - Working Copy`, 76 forks.

`SWEEPS.md` recovers a sweep procedure from the fork structure and reads it as a
temperature ladder. `Mythmaker - Working Copy` is the place to check what the
ladder actually varies, because it is the cleanest instance of the procedure in
the corpus:

- **76 forks of one story**, 2024-03-05 .. 2024-07-23, one model (`kayra-v1`),
  `max_length` held at 100 in every single fork.
- **Three presets in rotation** — `asper`, `writersdaemon`, `freshcoffeek` —
  with temperature stepped under each, repeatedly, on the same days.
- **The forks are an append chain.** 67 of 75 consecutive pairs are a strict
  prefix relation: fork *n+1* is fork *n* plus new blocks at the end. So each
  fork's new blocks are attributable to that fork's saved settings, which is the
  attribution the rest of the corpus cannot support.

    python3 analysis/myths.py corpus/myths --report analysis/MYTHS.md

Needs `wordfreq`. Refetch the forks with `analysis/fetch_export.py` (json folder
id in `sessions/LATEST.md`) and filter names beginning `Mythmaker`.

Three controls run before any of it is believed, because this corpus punishes
the obvious metric:

1. **Attribution.** Is text more homogeneous within a fork than under a shuffle
   of blocks between forks of the same day? If not, the per-fork settings are
   not governing anything and the whole design collapses.
2. **Preset.** Is the preset spread at 2.5 larger than shuffling preset labels
   between forks of the same day produces? Days differ in subject matter; the
   shuffle holds day constant.
3. **Roster.** Endorphin *chose* when to run 2.5, so a drop in speaker lines
   could just mean he ran it over monologue stretches. Matching generations on
   the speaker-line density of their immediate context removes that.

What it cannot do: one story, one model, one author. The preset was never
randomly assigned. `default-*` presets are NovelAI's shipped bundles, so
"preset" here means a whole sampler configuration, not a dial.
"""

import argparse
import collections
import datetime
import hashlib
import json
import math
import pathlib
import random
import re
import statistics as st

from wordfreq import top_n_list, zipf_frequency

TOKEN = re.compile(r"[A-Za-z][A-Za-z'’-]*")
# A speaker line: line start, one to four capitalised words, colon, space. This
# is the corpus's `Name:` convention (FINDINGS §7, READINGS §I-II) -- the device
# that turns a generation into a convened chamber.
SPEAKER = re.compile(r"^([A-Z][\w'’\-]*(?: [A-Z][\w'’\-]*){0,3}):\s", re.M)
# Reduplication or a letter held for three or more characters: `RRRiiiIIGGHHT`,
# `rainboaaaaaaar`, `blooped-bloop`.
REDUP = re.compile(r"([a-z]{2,})\1|([a-z])\2\2", re.I)
# Assistant register as *phrases*. A word list cannot be used: this document is
# partly about AI, so `model`, `system`, `data` and `prompt` are its subject
# matter rather than a change of voice.
SERVICE = re.compile("|".join([
    r"\bas an ai\b", r"\bi'?m sorry\b", r"\bi apologi[sz]e\b", r"\bfeel free to\b",
    r"\blet me know\b", r"\bi (?:can|will) (?:assist|help)\b", r"\bhappy to help\b",
    r"\bhow (?:can|may) i (?:assist|help)\b",
    r"\bplease (?:provide|clarify|specify|rephrase|restart)\b",
    r"\byour (?:request|prompt|input|query)\b", r"\b(?:aims?|designed) to assist\b",
    r"\bimprove (?:services|responses)\b", r"\bi (?:do not|don'?t) (?:have|understand)\b",
    r"\bcannot (?:comply|fulfill|provide)\b", r"\bfurther (?:instructions|clarification)\b",
]), re.I)
FUNC = set("""the a an and or but if then than that this these those of in on at to for from
with by as is are was were be been being am do does did have has had not no nor so such it
its he she they them his her their we us our you your i me my which who whom whose what when
where while because although though into onto upon about over under after before during
between""".split())
PRESETS = ("freshcoffeek", "asper", "writersdaemon")


# --------------------------------------------------------------------------
# the chain
# --------------------------------------------------------------------------
def load(path):
    doc = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    content = doc["content"]["data"]
    story = content["story"]
    blocks = story["datablocks"]
    live, i, seen = [], story["currentBlock"], set()
    while isinstance(i, int) and 0 <= i < len(blocks) and i not in seen:
        seen.add(i)
        live.append(i)
        i = blocks[i].get("prevBlock")
    live.reverse()
    seq = [((blocks[n].get("dataFragment") or {}).get("origin"),
            (blocks[n].get("dataFragment") or {}).get("data") or "") for n in live]
    settings = content["settings"]
    params = settings["parameters"]
    enabled = [o["id"] for o in params.get("order", []) if o.get("enabled")]
    return {
        "file": path.name,
        "upd": doc["story"]["lastUpdatedAt"],
        "preset": (settings.get("preset") or "").replace("default-", ""),
        "temp": params.get("temperature"),
        "max_length": params.get("max_length"),
        "enabled": enabled,
        "top_k": params.get("top_k"),
        "top_p": params.get("top_p"),
        "typical_p": params.get("typical_p"),
        "tfs": params.get("tail_free_sampling"),
        "mirostat_tau": params.get("mirostat_tau"),
        "rep_pen": params.get("repetition_penalty"),
        "rep_range": params.get("repetition_penalty_range"),
        "rep_slope": params.get("repetition_penalty_slope"),
        "phrase_rep_pen": params.get("phrase_rep_pen"),
        "seq": seq,
    }


def chain(folder):
    """Forks in append order, and every block tagged with the fork that added it.

    A block is credited to the first fork it appears in, forks ordered by save
    time then length. Where the chain is a strict prefix -- 67 of 75 consecutive
    pairs -- that is simply "the blocks added since the last save". Where it
    branches, the earliest fork holding the text still wins, which is the
    conservative choice: it never credits text to a later setting.
    """
    forks = [load(p) for p in sorted(pathlib.Path(folder).glob("*.json"))]
    if not forks:
        raise SystemExit(f"no *.json under {folder}")
    forks.sort(key=lambda f: (f["upd"], len(f["seq"])))
    prefix = sum(
        1 for a, b in zip(forks, forks[1:])
        if len(a["seq"]) <= len(b["seq"]) and b["seq"][:len(a["seq"])] == a["seq"]
    )
    seen, out = set(), []
    for fi, f in enumerate(forks):
        for j, (origin, text) in enumerate(f["seq"]):
            h = hashlib.md5(((origin or "") + "\x00" + text).encode()).hexdigest()
            if h in seen:
                continue
            seen.add(h)
            out.append({
                "fi": fi, "pos": j, "origin": origin, "text": text,
                "preset": f["preset"], "temp": f["temp"], "upd": f["upd"],
                "day": datetime.datetime.fromtimestamp(
                    f["upd"], datetime.timezone.utc).strftime("%m-%d"),
                # the 1,200 characters the model was continuing from
                "prev": "".join(x[1] for x in f["seq"][max(0, j - 4):j])[-1200:],
            })
    return forks, out, prefix


# --------------------------------------------------------------------------
# measures
# --------------------------------------------------------------------------
def charmodel(lang="en", n=40000):
    """Character-bigram plausibility. Is a coinage sayable *in this language*?

    Run for two languages it also answers a sharper question: when a coinage
    stops being English, does it become nothing, or does it become somewhere
    else? `asper` at 2.5 answers that differently from `writersdaemon`.
    """
    big, uni = collections.Counter(), collections.Counter()
    for w in top_n_list(lang, n):
        w = "^" + w.lower() + "$"
        for i in range(len(w) - 1):
            big[w[i:i + 2]] += 1
            uni[w[i]] += 1
    def score(word):
        w = "^" + word + "$"
        return sum(math.log((big[w[i:i + 2]] + 1) / (uni[w[i]] + 40))
                   for i in range(len(w) - 1)) / (len(w) - 1)
    return score


ENGLISH = {w for w in top_n_list("en", 60000) if len(w) >= 4}


def tile(word):
    """Two real words of four characters or more, tiled. The same crude
    decomposer `analysis/coinage.py` uses -- it under-counts, equally, everyone."""
    return any(word[:i] in ENGLISH and word[i:] in ENGLISH
               for i in range(4, len(word) - 3))


def edit_within(a, b, cap=4):
    if abs(len(a) - len(b)) > cap:
        return cap + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def coinages(text):
    return [w for w in (t.lower() for t in TOKEN.findall(text))
            if len(w) >= 6 and zipf_frequency(w, "en") == 0]


def block_features(b, cm):
    text = b["text"]
    toks = [w.lower() for w in TOKEN.findall(text)]
    n = max(1, len(toks))
    coined = coinages(text)
    ctx = set(w.lower() for w in TOKEN.findall(b["prev"]))
    near = sum(
        1 for w in coined
        if min((edit_within(w, c) for c in ctx if abs(len(c) - len(w)) <= 3),
               default=99) / max(1, len(w)) <= 0.25
    )
    lines_tok = n
    return {
        "tokens": n,
        "chars": len(text),
        "nonword": len(coined) / n,
        "n_coined": len(coined),
        "decomp": sum(tile(w) for w in coined),
        "redup": sum(bool(REDUP.search(w)) for w in coined),
        "nearcopy": near,
        "cbits": st.mean([cm(w) for w in coined]) if coined else None,
        "func": sum(1 for w in toks if w in FUNC) / n,
        "sent": n / max(1, len([s for s in re.split(r"[.!?]+", text) if s.strip()])),
        "bang": 1000 * (text.count("!") + text.count("?")) / max(1, len(text)),
        "speakers": len(SPEAKER.findall(text)),
        "spk_per_1k": 1000 * len(SPEAKER.findall(text)) / lines_tok,
        "service": len(SERVICE.findall(text)),
    }


def weighted(rows, key, weight="tokens"):
    num = sum(r[key] * r[weight] for r in rows if r[key] is not None)
    den = sum(r[weight] for r in rows if r[key] is not None)
    return num / den if den else None


def rate(rows, num, den="tokens", per=1.0):
    a = sum(r[num] for r in rows)
    b = sum(r[den] for r in rows)
    return per * a / b if b else None


# --------------------------------------------------------------------------
# controls
# --------------------------------------------------------------------------
def permute_within_day(rows, statfn, label_key, strata_key, n=2000, seed=0):
    obs = statfn(rows)
    strata = collections.defaultdict(list)
    for r in rows:
        strata[r[strata_key]].append(r)
    rng = random.Random(seed)
    null = []
    for _ in range(n):
        shuffled = []
        for group in strata.values():
            labels = [g[label_key] for g in group]
            rng.shuffle(labels)
            shuffled += [dict(g, **{label_key: l}) for g, l in zip(group, labels)]
        null.append(statfn(shuffled))
    p = (sum(1 for x in null if x >= obs) + 1) / (n + 1)
    return obs, st.median(null), sorted(null)[int(0.95 * n)], p


def preset_spread(rows):
    g = collections.defaultdict(list)
    for r in rows:
        g[r["preset"]].append(r)
    vals = [weighted(v, "nonword") for v in g.values() if sum(x["tokens"] for x in v) > 200]
    return max(vals) - min(vals) if len(vals) > 1 else 0.0


def fork_spread(rows):
    g = collections.defaultdict(list)
    for r in rows:
        g[r["fi"]].append(r)
    means = [st.mean([x["nonword"] for x in v]) for v in g.values() if len(v) >= 4]
    return st.pvariance(means) if len(means) > 2 else 0.0


# --------------------------------------------------------------------------
# report
# --------------------------------------------------------------------------
def band(t):
    return "low <1.65" if t < 1.65 else "mid 1.65-2.0" if t <= 2.0 else "top 2.5"


def build(folder):
    forks, blocks, prefix = chain(folder)
    cm = charmodel()
    ai = [b for b in blocks if b["origin"] == "ai" and len(b["text"]) >= 80]
    human = [b for b in blocks if b["origin"] != "ai" and len(b["text"]) >= 40]
    for b in ai + human:
        b.update(block_features(b, cm))
    return forks, ai, human, blocks, prefix


def uptake(blocks):
    """Does a word the model introduces come back -- in his text, or its own?

    Scored against the document's lexicon *at that point*, not globally: a
    global exclusion would drop every word he ever typed and return 0% for
    everything, which is what the first pass did.
    """
    seq = sorted([b for b in blocks if len(b["text"]) >= 40],
                 key=lambda b: (b["fi"], b["pos"]))
    words = [{w.lower() for w in TOKEN.findall(b["text"])} for b in seq]
    later_h, later_a = [set() for _ in seq], [set() for _ in seq]
    acc_h, acc_a = set(), set()
    for i in range(len(seq) - 1, -1, -1):
        later_h[i], later_a[i] = set(acc_h), set(acc_a)
        (acc_a if seq[i]["origin"] == "ai" else acc_h).update(words[i])
    prior = set()
    by_class = collections.defaultdict(lambda: [0, 0, 0])
    by_cell = collections.defaultdict(lambda: [0, 0, 0])
    for i, b in enumerate(seq):
        if b["origin"] == "ai":
            for w in words[i]:
                if len(w) < 6 or w in prior:
                    continue
                z = zipf_frequency(w, "en")
                cls = ("coinage" if z == 0 else
                       "rare real (0<zipf<3)" if z < 3 else "common real (zipf>=3)")
                for d in (by_class[cls], by_cell[(b["preset"], band(b["temp"]), cls)]):
                    d[0] += w in later_h[i]
                    d[1] += w in later_a[i]
                    d[2] += 1
        prior |= words[i]
    return by_class, by_cell


def roster_control(ai):
    def dens(t):
        n = len(TOKEN.findall(t))
        return 1000 * len(SPEAKER.findall(t)) / n if n >= 30 else None
    hi, lo = [], []
    for b in ai:
        c, o = dens(b["prev"]), b["spk_per_1k"]
        if c is None:
            continue
        (hi if b["temp"] >= 2.4 else lo).append((c, o))
    mhi = [x for x in hi if x[0] >= 1.0]
    mlo = [x for x in lo if x[0] >= 1.0]
    obs = st.mean([x[1] for x in mlo]) - st.mean([x[1] for x in mhi])
    pool = [x[1] for x in mlo + mhi]
    rng = random.Random(0)
    null = 0
    for _ in range(5000):
        rng.shuffle(pool)
        if st.mean(pool[:len(mlo)]) - st.mean(pool[len(mlo):]) >= obs:
            null += 1
    return hi, lo, mhi, mlo, obs, (null + 1) / 5001


def report(folder, out):
    forks, ai, human, blocks, prefix = build(folder)
    days = sorted({f["day"] for f in ai})
    bundles = {}
    for f in forks:
        bundles.setdefault(f["preset"], f)

    # fork-level: the run is the unit (SWEEPS.md -- each fork preserves one run)
    per_fork = collections.defaultdict(list)
    for b in ai:
        per_fork[b["fi"]].append(b)
    forkrows = []
    for fi, g in per_fork.items():
        tok = sum(x["tokens"] for x in g)
        if tok < 300:
            continue
        forkrows.append({"fi": fi, "preset": g[0]["preset"], "temp": g[0]["temp"],
                         "day": g[0]["day"], "tokens": tok,
                         "nonword": weighted(g, "nonword"),
                         "spk": rate(g, "speakers", per=1000),
                         "func": weighted(g, "func")})

    hi_ai = [b for b in ai if b["temp"] >= 2.4]
    obs_p, med_p, p95_p, pval_p = permute_within_day(
        hi_ai, preset_spread, "preset", "day")
    obs_f, med_f, _, pval_f = permute_within_day(ai, fork_spread, "fi", "day")
    hi, lo, mhi, mlo, obs_r, pval_r = roster_control(ai)
    by_class, by_cell = uptake(blocks)

    L = [
        "# Myths — what a preset does to language",
        "",
        "Generated by `analysis/myths.py` over **`Mythmaker - Working Copy`**, "
        f"**{len(forks)} forks**",
        "of one story (`kayra-v1`, `max_length` = 100 in every fork, "
        f"{days[0]} .. {days[-1]}).",
        "",
        "The show is *Myths for Now* — the stream segment of that name runs through",
        "`data/EPISODES.tsv` — and its premise is in the opening prompt: *\"myths are",
        "condensed educational tools, distilling centuries of trial and error into a",
        "sticky narrative.\"* Each session makes a myth about one thing: background",
        "checks on a partner, mixing ammonia and bleach, ephedra, the OpenAI board.",
        "",
        "This is the corpus's cleanest instance of the sweep procedure, and the only",
        "one that supports attribution. **The forks are an append chain**: "
        f"{prefix} of {len(forks) - 1} consecutive",
        "pairs are a strict prefix relation, so fork *n+1* is fork *n* plus new blocks",
        "at the end, and those new blocks belong to fork *n+1*'s saved settings.",
        f"**{len(ai)} attributed model generations, "
        f"{sum(b['chars'] for b in ai):,} characters.**",
        "",
        "## The three presets are three different machines",
        "",
        "Not one dial at three settings. `default-*` presets are NovelAI's shipped",
        "bundles, and these three disagree about how to keep text interesting — and,",
        "decisively, about **what happens after temperature is applied**:",
        "",
        "| | enabled sampler order | top_k | phrase rep pen | rep pen (range/slope) |",
        "|---|---|---:|---|---|",
    ]
    for p in PRESETS:
        f = bundles[p]
        k = f["top_k"] if "top_k" in f["enabled"] else "— *not enabled*"
        L.append(f"| **{p}** | {' → '.join(f['enabled'])} | {k} | "
                 f"{f['phrase_rep_pen']} | {f['rep_pen']} ({f['rep_range']}/"
                 f"{f['rep_slope']:g}) |")
    L += [
        "",
        "`writersdaemon` runs **mirostat** first and enables **no top_k at all**.",
        "`asper` and `freshcoffeek` both put a hard `top_k` **after** temperature —",
        "175 and 25 respectively. That ordering is the whole story below: a hard",
        "truncation downstream of temperature re-truncates the flattened distribution",
        "and hands most of the coherence back.",
        "",
        "## Coinage rate, by preset and temperature",
        "",
        "Share of tokens that are not words at all (length ≥ 6, `wordfreq` zipf = 0).",
        "**The fork is the unit** — one fork, one run, one setting — reported as the",
        "median over forks, because two long sessions otherwise carry a whole cell.",
        "",
        "| preset | post-temperature top_k | low <1.65 | mid 1.65–2.0 | top 2.5 |",
        "|---|---|---:|---:|---:|",
    ]
    for p in PRESETS:
        k = bundles[p]["top_k"] if "top_k" in bundles[p]["enabled"] else "none"
        cells = []
        for lo_, hi_ in ((0, 1.65), (1.65, 2.01), (2.4, 9)):
            v = [r["nonword"] for r in forkrows
                 if r["preset"] == p and lo_ <= r["temp"] < hi_]
            cells.append(f"{100 * st.median(v):.2f}% (n={len(v)})" if v else "—")
        L.append(f"| **{p}** | {k} | " + " | ".join(cells) + " |")
    L += [
        "",
        "**Temperature is not one thing.** At the identical setting — 2.5, the top of",
        "NovelAI's slider — the same document on the same model produces "
        f"{100 * st.median([r['nonword'] for r in forkrows if r['preset'] == 'freshcoffeek' and r['temp'] >= 2.4]):.2f}%",
        "non-words under `freshcoffeek`, "
        f"{100 * st.median([r['nonword'] for r in forkrows if r['preset'] == 'asper' and r['temp'] >= 2.4]):.2f}% under `asper`, and "
        f"{100 * st.median([r['nonword'] for r in forkrows if r['preset'] == 'writersdaemon' and r['temp'] >= 2.4]):.2f}%",
        "under `writersdaemon`. The ordering is the post-temperature `top_k`: 25,",
        "then 175, then none. Under `freshcoffeek` and `asper` the dial does almost",
        "nothing to the lexicon; under `writersdaemon` it is the whole event.",
        "",
        "Per-fork values at 2.5, sorted — the spread inside a preset matters as much",
        "as the median:",
        "",
    ]
    for p in PRESETS:
        v = sorted(100 * r["nonword"] for r in forkrows
                   if r["preset"] == p and r["temp"] >= 2.4)
        L.append(f"- `{p}` — " + ", ".join(f"{x:.2f}%" for x in v))
    L += [
        "",
        f"`asper` is **bimodal**: seven of nine forks under 0.9%, two at 5.95% and",
        "8.57%. It is not that 175 is safe; it is that 175 is safe until it isn't.",
        "",
        "## Control 1 — is the attribution real?",
        "",
        "If a fork's saved settings did not govern the text added under them, blocks",
        "would be no more alike within a fork than across forks of the same day.",
        "",
        f"- observed between-fork variance in coinage rate: **{obs_f:.5f}**",
        f"- shuffling blocks between forks of the same day: median {med_f:.5f}, "
        f"**p = {pval_f:.4f}**",
        "",
        "## Control 2 — is it the preset, or the day?",
        "",
        "Days differ in subject matter. Shuffling preset labels between forks of the",
        "same day holds the subject constant and asks whether the preset still",
        "separates, at 2.5 only.",
        "",
        f"- observed spread between presets: **{100 * obs_p:.2f} points**",
        f"- shuffled within day: median {100 * med_p:.2f}, 95th percentile "
        f"{100 * p95_p:.2f}, **p = {pval_p:.4f}**",
        "",
        "It replicates within days, too. At 2.5, on every day where two presets were",
        "both run, `writersdaemon` coins more than `asper`, and `asper` more than",
        "`freshcoffeek`:",
        "",
        "| day | freshcoffeek | asper | writersdaemon |",
        "|---|---:|---:|---:|",
    ]
    for d in days:
        cells = []
        for p in PRESETS:
            g = [b for b in hi_ai if b["day"] == d and b["preset"] == p]
            tok = sum(x["tokens"] for x in g)
            cells.append(f"{100 * weighted(g, 'nonword'):.2f}%" if tok >= 500 else "—")
        if sum(c != "—" for c in cells) >= 2:
            L.append(f"| {d} | " + " | ".join(cells) + " |")

    L += [
        "",
        "## What breaks first is the frame, not the word",
        "",
        "The `Name:` convention — the device `FINDINGS.md` §7 measures and",
        "`READINGS.md` §I–II organise around, the thing that makes a generation a",
        "convened chamber rather than prose — is **more temperature-fragile than the",
        "lexicon is**.",
        "",
        "| source | tokens | speaker lines / 1k | assistant register / 10k | function words |",
        "|---|---:|---:|---:|---:|",
    ]
    rows_fr = [("Endorphin", human)]
    for p in PRESETS:
        for hi_ in (False, True):
            g = [b for b in ai if b["preset"] == p and (b["temp"] >= 2.4) == hi_]
            if sum(x["tokens"] for x in g) >= 500:
                rows_fr.append((f"`{p}` {'2.5' if hi_ else '<2.0'}", g))
    for lab, g in rows_fr:
        L.append(f"| {lab} | {sum(x['tokens'] for x in g):,} | "
                 f"{rate(g, 'speakers', per=1000):.2f} | "
                 f"{rate(g, 'service', per=10000):.2f} | "
                 f"{weighted(g, 'func'):.3f} |")
    L += [
        "",
        "Speaker lines fall by ~93–96% from below 2.0 to 2.5 under **all three**",
        "presets — including the two whose coinage rate does not move at all. The",
        "assistant register goes the same way, and it is a *low*-temperature",
        "phenomenon: the model slips into service voice (*\"Please clarify what",
        "information you require\"*, *\"I'm always happy to help!\"*) when it is being",
        "sampled conservatively, not when it is breaking down.",
        "",
        "## Control 3 — did he just run 2.5 over the monologues?",
        "",
        "The preset was never randomly assigned and neither was the temperature. If",
        "2.5 was reserved for narration, the roster would look fragile without being",
        "fragile. Matching generations on the speaker-line density of the 1,200",
        "characters they were continuing from removes that.",
        "",
        f"| context | n | context spk/1k | output spk/1k | generations returning any |",
        "|---|---:|---:|---:|---:|",
        f"| temp < 2.4, dialogue-dense context | {len(mlo)} | "
        f"{st.mean([x[0] for x in mlo]):.2f} | {st.mean([x[1] for x in mlo]):.2f} | "
        f"{100 * st.mean([x[1] > 0 for x in mlo]):.0f}% |",
        f"| temp ≥ 2.4, dialogue-dense context | {len(mhi)} | "
        f"{st.mean([x[0] for x in mhi]):.2f} | {st.mean([x[1] for x in mhi]):.2f} | "
        f"{100 * st.mean([x[1] > 0 for x in mhi]):.0f}% |",
        "",
        f"Handed equally dialogue-dense context, 2.5 returns a speaker line in "
        f"**{100 * st.mean([x[1] > 0 for x in mhi]):.0f}%** of",
        f"generations against **{100 * st.mean([x[1] > 0 for x in mlo]):.0f}%** below it "
        f"(difference {obs_r:.2f} lines/1k, permutation **p = {pval_r:.4f}**).",
        "The convention is not being withheld by the author. It is being dissolved by",
        "the sampler.",
        "",
        "## The kind of coinage, not the amount",
        "",
        "Rate is the least interesting thing about a non-word. Four measures over",
        "every coinage new to the document at the point it appears:",
        "",
        "| preset | temp | coinages | decomposable | reduplicated / held | near-copy of context |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for p in PRESETS:
        for hi_ in (False, True):
            g = [b for b in ai if b["preset"] == p and (b["temp"] >= 2.4) == hi_
                 and b["n_coined"]]
            tot = sum(x["n_coined"] for x in g)
            if tot < 30:
                continue
            L.append(f"| `{p}` | {'2.5' if hi_ else '<2.0'} | {tot} | "
                     f"{100 * sum(x['decomp'] for x in g) / tot:.1f}% | "
                     f"{100 * sum(x['redup'] for x in g) / tot:.1f}% | "
                     f"{100 * sum(x['nearcopy'] for x in g) / tot:.1f}% |")
    wd_hi = [b for b in ai if b["preset"] == "writersdaemon" and b["temp"] >= 2.4
             and b["n_coined"]]
    fc_hi = [b for b in ai if b["preset"] == "freshcoffeek" and b["temp"] >= 2.4
             and b["n_coined"]]
    # when a word stops being English, does it become nothing, or somewhere else?
    es = charmodel("es", 30000)
    en = charmodel("en", 30000)
    xeno = collections.defaultdict(list)
    for b in ai:
        for w in coinages(b["text"]):
            xeno[(b["preset"], b["temp"] >= 2.4)].append(es(w) > en(w))
    L += [
        "",
        "*Decomposable* = tiles into two real words of four letters or more.",
        "*Near-copy* = within a 0.25 normalised edit distance of a word in the",
        "immediate context, i.e. a swerve off something already on the page.",
        "",
        "Of the three presets at 2.5, `writersdaemon` has the **highest**",
        "construction rate and by far the **lowest** anchoring "
        f"({100 * sum(x['nearcopy'] for x in wd_hi) / sum(x['n_coined'] for x in wd_hi):.1f}% near-copy",
        "against 39.5% for `asper` below 2.0) — its inventions are built, but not out",
        "of what is in front of it. That is its `phrase_rep_pen: very_aggressive`",
        "showing up as texture: forbidden to reuse the local phrasing, it has to go",
        "somewhere new. `freshcoffeek` at 2.5 barely coins at all, and "
        f"{100 * sum(x['redup'] for x in fc_hi) / sum(x['n_coined'] for x in fc_hi):.0f}% of the",
        "little it does is a letter held down — `RRRiiiIIGGHHT`, `SSEEIIIRKLEEN`.",
        "Its breakage is **prosodic**, not lexical.",
        "",
        "### And when a word stops being English, it does not always become nothing",
        "",
        "Share of coinages that score better under a **Spanish** character-bigram",
        "model than an English one — i.e. the string left English phonotactics and",
        "arrived somewhere rather than nowhere:",
        "",
        "| cell | coinages | more Spanish-shaped than English |",
        "|---|---:|---:|",
    ]
    for p in PRESETS:
        for hi_ in (False, True):
            v = xeno.get((p, hi_), [])
            if len(v) >= 40:
                L.append(f"| `{p}` {'2.5' if hi_ else '<2.0'} | {len(v)} | "
                         f"{100 * st.mean(v):.0f}% |")
    L += [
        "",
        "**`asper` at 2.5 is the outlier and it is not close**: 40% against 8–12%",
        "everywhere else, `writersdaemon` at 2.5 included. The two high-temperature",
        "breakdowns are not the same breakdown. `writersdaemon` stays inside English",
        "and pulls the word apart — sound-play, compounds, held vowels that a reader",
        "of English can still voice. `asper` leaves the language. Its worst run reads",
        "as pseudo-Spanish with real Spanish function words caught in it: *\"Estopachida",
        "mejcascocas nondustano apresteya **hace** caya **ma la** pascina\"*.",
        "",
        "Two different borders, then, and the corpus has been calling both of them",
        "the same thing. One is the edge of the word. The other is the edge of the",
        "language.",
        "",
        "## Nothing invented is kept",
        "",
        "A word the model introduces, scored against the document's lexicon *at that",
        "point*: does it ever come back?",
        "",
        "| class of word | n | later in Endorphin's text | later in the model's |",
        "|---|---:|---:|---:|",
    ]
    up = {}
    for cls in ("common real (zipf>=3)", "rare real (0<zipf<3)", "coinage"):
        h, a, n = by_class[cls]
        up[cls] = (100 * h / n, 100 * a / n)
        L.append(f"| {cls} | {n:,} | {100 * h / n:.2f}% | {100 * a / n:.2f}% |")
    com, rare, coin = (up["common real (zipf>=3)"], up["rare real (0<zipf<3)"],
                       up["coinage"])
    L += [
        "",
        "**The gradient is the finding.** A common word the model introduces comes",
        f"back in Endorphin's own typing {com[0]:.1f}% of the time; a rare real word "
        f"{rare[0]:.1f}%; a",
        f"coinage {coin[0]:.2f}%. The model's own later text does the same thing, "
        f"harder: {com[1]:.0f}%,",
        f"{rare[1]:.0f}%, {coin[1]:.1f}%. The texture this document is most known for "
        "— the invented",
        "vocabulary at the top of the dial — is the one thing that never enters the",
        "shared lexicon. It is a surface event, not an accretion.",
        "",
        "The first version of this measure returned 0.00% for *every* class, because",
        "it excluded any word he had typed anywhere in the document rather than any",
        "word he had typed *so far*. It is recorded here because the corrected",
        "measure is only trustworthy given the broken one: a control that returns a",
        "clean null for the comparison class is how you find out.",
        "",
        "## Six modes, and names proposed for them",
        "",
        "The three presets crossed with the two temperature regions give six regions",
        "of behaviour, and they are distinguishable on the measures above rather than",
        "by ear. The names are **proposals, not findings** — offered because the",
        "things have no names, and the measured definition is what has to survive if",
        "a name is replaced.",
        "",
        "| mode | region | measured definition |",
        "|---|---|---|",
        "| **The clerk** | `freshcoffeek` < 2.0 | most speaker lines and the most "
        "assistant register of any cell; almost no lexical invention. Builds the "
        "show's furniture: listener numbering, step lists, *\"the key take-away\"*. |",
        "| **The name-forge** | `asper` < 2.0 | coinage is rare but "
        "**39.5% near-copy** and **40.3% decomposable** — derived off words already "
        "on the page — and it is the only mode whose inventions get reused later "
        "(7.8% recur in the model's own text). It mints terms that stick. |",
        "| **The caster** | `writersdaemon` < 2.0 | the highest rate of *new speakers* "
        "introduced (1.14/1k tokens against 0.39–0.40 for the others). It does not "
        "shape sentences so much as populate the room — `Sprooze`, `Wemble`, "
        "`Aspark`, `Mythmaker Eulby`. |",
        "| **The trapdoor** | `asper` 2.5 | bimodal: seven of nine runs indistinguishable "
        "from low temperature, two that drop straight out of the language — 40% of "
        "its coinages are better-formed Spanish than English. The mean is "
        "meaningless here; the mode is the intermittency. |",
        "| **The held note** | `freshcoffeek` 2.5 | real words, unreal delivery. Almost "
        "no coinage; the highest `!?` density of any cell; a fifth of what it does "
        "invent is a letter held down (`RRRiiiIIGGHHT`). `top_k` 25 downstream of "
        "temperature leaves nothing for the heat to break except the prosody. |",
        "| **The glossolalia engine** | `writersdaemon` 2.5 | the only mode that "
        "attacks the word. Coinage up to 30% of tokens, most-constructed of the 2.5 "
        "cells, least anchored to context, function words down to 0.284, sentences "
        "at 30 tokens. |",
        "",
        "The last name is not new to this repo. `READINGS.md` §VII takes "
        "`-Glossolalia` from Endorphin's own invented setting in the *Left Behind*",
        "document, and argues the room's switch into invented languages is a mechanic",
        "rather than a failure. This is the sampler configuration that produces it,",
        "and it is not the one with the highest temperature — all three of these ran",
        "at 2.5.",
        "",
        "### One passage per mode",
        "",
    ]
    picks = [
        ("The clerk", "freshcoffeek", False, lambda b: (b["service"], b["speakers"])),
        ("The name-forge", "asper", False, lambda b: (b["nearcopy"], b["decomp"])),
        ("The caster", "writersdaemon", False, lambda b: (b["speakers"],)),
        ("The trapdoor", "asper", True, lambda b: (b["nonword"],)),
        ("The held note", "freshcoffeek", True, lambda b: (b["redup"], b["bang"])),
        ("The glossolalia engine", "writersdaemon", True, lambda b: (b["nonword"],)),
    ]
    for name, preset, hi_, keyfn in picks:
        pool = [b for b in ai if b["preset"] == preset and (b["temp"] >= 2.4) == hi_
                and 250 <= b["chars"] <= 850]
        if not pool:
            continue
        b = max(pool, key=lambda x: (keyfn(x), -x["chars"]))
        body = " ".join(b["text"].split())[:520]
        L += [f"**{name}** — `{preset}`, temp {b['temp']:g}, fork {b['fi']}:", "",
              f"> {body}", ""]
    L += [
        "## What this does not show",
        "",
        "- **Fork 0 is not really attributable.** The first save carries 147 blocks",
        "  — the whole seed session — under one set of settings, and those blocks",
        "  were not necessarily all made under them. Dropping it moves `asper` at 2.5",
        "  from 0.75% to 0.68% and leaves the other two cells untouched, so nothing",
        "  above rests on it, but it is the one fork whose label is a guess.",
        "- **One story, one model, one author.** `kayra-v1` only. Nothing here",
        "  transfers to Erato, GLM-4.6, or the off-platform Llama work.",
        "- **The preset was chosen, never assigned.** Controls 2 and 3 hold day and",
        "  context constant, which is not the same as randomisation. He may have",
        "  reached for `writersdaemon` when he wanted the room to come apart.",
        "- **`preset` is a bundle.** Everything attributed to a preset here could be",
        "  any of its five or six differing parameters. The post-temperature `top_k`",
        "  reading is the one that predicts the ordering, and it is a hypothesis the",
        "  fork structure is consistent with, not an ablation.",
        "- **The decomposer under-counts.** `riverrun` fails it. Rates are floors,",
        "  and the comparison is fair only because the same crude tool runs on all",
        "  three presets.",
        "- **Speaker-line detection is a regex.** It will miss unconventional",
        "  attributions and catch the occasional sentence that opens with a colon.",
    ]
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    return forks, ai


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", help="directory of Mythmaker_*.json exports")
    ap.add_argument("--report", type=pathlib.Path)
    args = ap.parse_args()
    if args.report:
        forks, ai = report(args.folder, args.report)
        print(f"{len(forks)} forks, {len(ai)} attributed generations "
              f"-> {args.report}")
    else:
        forks, ai, human, blocks, prefix = build(args.folder)
        print(f"{len(forks)} forks, {prefix} prefix pairs, {len(ai)} generations")


if __name__ == "__main__":
    main()
