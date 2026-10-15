#!/usr/bin/env python3
"""meta_eras.py — quantitative passes for META_ERAS.md.

For each year and each source (fb / ig):
  - post count, own vs shared (fb), video/photo counts
  - mean and median character length of text (caption or post text)
  - distinctive vocabulary: top terms by log-odds vs the rest of the corpus
    (informative Dirichlet prior, Monroe et al. 2008; z-scores, no significance
    claims — this is exploration, and a disconfirming check is built in:
    the same routine run on random halves of the corpus should show no stable
    year-like structure)

Also dumps sample posts per year (oldest/middle/newest few) for the reading
pass in META_ERAS.md.

Reads the corpora from ~/workspace/meta-corpus; prints a report to stdout.
"""
import json, math, re, collections, sys, random
from pathlib import Path

FB = Path.home() / "workspace/meta-corpus/facebook/corpus.jsonl"
IG = Path.home() / "workspace/meta-corpus/instagram/gallegos.devon/corpus.jsonl"

TOKEN = re.compile(r"[a-z][a-z'\-]{2,}")
STOP = set("""the and for with you your this that have from are was were not but all can has had her his him our out how who get got its one our when what where which there their them then than also just like over into more very will would could should been being made much many some any own way back down off new old even still only also just""".split())

def tok(text):
    return [t for t in TOKEN.findall(text.lower()) if t not in STOP]

def load(path, source):
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            text = d.get("text") or d.get("caption") or ""
            if source == "ig" and not text:
                continue  # story archive items carry media only
            local = d.get("created_at_local") or ""
            year = local.split("-")[0] if local[:4].isdigit() else "????"
            rows.append({
                "year": year, "source": source, "text": text,
                "len": len(text),
                "video": bool(d.get("has_video")) or str(d.get("type","")).upper() in ("REEL",),
                "photo": bool(d.get("has_photo")),
                "type": d.get("type",""),
                "url": d.get("url",""),
                "local": local,
            })
    return rows

fb = load(FB, "fb")
ig = load(IG, "ig")
all_rows = fb + ig

# ---- per-year descriptive table ----
print("== posts per year ==")
for r in all_rows:
    pass
years = sorted({r["year"] for r in all_rows})
print(f"{'year':6} {'fb':>5} {'ig':>5} {'fb_vid':>6} {'ig_vid':>6} {'fb_medlen':>10} {'ig_medlen':>10}")
for y in years:
    fr = [r for r in fb if r["year"] == y]
    ir = [r for r in ig if r["year"] == y]
    def med(rs):
        if not rs: return 0
        s = sorted(r["len"] for r in rs); return s[len(s)//2]
    print(f"{y:6} {len(fr):>5} {len(ir):>5} "
          f"{sum(r['video'] for r in fr):>6} {sum(r['video'] for r in ir):>6} "
          f"{med(fr):>10} {med(ir):>10}")

print(f"\nfb total: {len(fb)} (own: {sum(r['type']=='own' for r in fb)}, shared: {sum(r['type']=='shared' for r in fb)})")
print(f"ig total with text: {len(ig)}")

# ---- distinctive vocabulary by era ----
def logodds(counts_a, counts_b, alpha=0.01):
    """z-scored log-odds with informative Dirichlet prior (Monroe et al.)."""
    vocab = set(counts_a) | set(counts_b)
    n_a = sum(counts_a.values()); n_b = sum(counts_b.values())
    scores = {}
    for w in vocab:
        p = alpha
        num = math.log((counts_a.get(w, 0) + p) / (n_a + p * len(vocab)))
        den = math.log((counts_b.get(w, 0) + p) / (n_b + p * len(vocab)))
        lo = num - den
        var = 1.0 / (counts_a.get(w, 0) + p) + 1.0 / (counts_b.get(w, 0) + p)
        scores[w] = lo / math.sqrt(var)
    return scores

eras = {"2008-2012": ["2008","2009","2010","2011","2012"],
        "2013-2018": ["2013","2014","2015","2016","2017","2018"],
        "2019-2020": ["2019","2020"],
        "2021-2022": ["2021","2022"],
        "2023-2024": ["2023","2024"],
        "2025-2026": ["2025","2026"]}
era_of = {}
for name, ys in eras.items():
    for y in ys:
        era_of[y] = name

era_counts = collections.defaultdict(collections.Counter)
for r in all_rows:
    e = era_of.get(r["year"])
    if e:
        era_counts[e].update(tok(r["text"]))

print("\n== distinctive terms per era (log-odds z, top 15) ==")
for name in eras:
    others = collections.Counter()
    for n2, c in era_counts.items():
        if n2 != name:
            others.update(c)
    scores = logodds(era_counts[name], others)
    top = sorted(scores.items(), key=lambda kv: -kv[1])[:15]
    print(f"{name:9} " + ", ".join(f"{w}({z:.1f})" for w, z in top))

# ---- disconfirming check: random halves should NOT show stable year-like structure ----
random.seed(7)
halves = [[], []]
for r in all_rows:
    halves[random.getrandbits(1)].append(r)
hc = [collections.Counter(), collections.Counter()]
for i, h in enumerate(halves):
    for r in h:
        hc[i].update(tok(r["text"]))
scores = logodds(hc[0], hc[1])
top = sorted(scores.items(), key=lambda kv: -abs(kv[1]))[:10]
print("\n== control: random halves, top |z| (expect small/noisy) ==")
print(", ".join(f"{w}({z:.1f})" for w, z in top))
