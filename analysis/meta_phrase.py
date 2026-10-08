#!/usr/bin/env python3
"""meta_phrase.py — measurements for META_PHRASE.md.

Counts, per year, occurrences of theme vocabularies related to the phrase
"authoritarianism is interpersonal violence at scale": power/control/
domination, coercion/force, institutional authority (cops, bosses, landlords,
state), intimate coercion (gaslight, manipulate, abuse, narcissist),
scale/abstraction language (system, empire, fascis, authoritarian, regime).

Output is per-10k-chars density so year comparisons survive the huge
differences in posting volume. Also prints the top co-occurring content
words next to the theme hits, and a disconfirming control: the same
density for a thematically-neutral vocabulary (weather words) — if the
theme series looks like the weather series, it is just volume noise.
"""
import json, re, sys, collections
from pathlib import Path

FB = Path.home() / "workspace/meta-corpus/facebook/corpus.jsonl"
IG = Path.home() / "workspace/meta-corpus/instagram/gallegos.devon/corpus.jsonl"

THEMES = {
    "power":      r"\b(power|control|dominat|authority|authoritarian|submit|obey|command|rule over|ruler)\b",
    "coercion":   r"\b(coerc|force[ds]?|violence|violent|threat|intimidat|bully|oppress|suppress|censor|silenc)\b",
    "institutions": r"\b(cop(s)?|police|boss(es)?|landlord|government|state\b|regime|empire|fascis|nazi|prison|jail|arrest|court|judge|military|army|ice\b|border)\b",
    "intimate":   r"\b(gaslight|manipulat|narcissis|abuse|abusive|toxic|boundar|consent|victim|trauma|trigger)\b",
    "scale":      r"\b(system(s|ic)?|structural|institutional|society|culture|capitalis|scale|at scale|epidemic|crisis)\b",
}
CONTROL = {"weather": r"\b(rain|snow|sun|sunny|cloud|storm|wind|hot|cold|weather|humid)\b"}

def load(path, source):
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            text = (d.get("text") or d.get("caption") or "")
            local = d.get("created_at_local") or ""
            year = local[:4] if local[:4].isdigit() else "????"
            rows.append((year, text))
    return rows

rows = load(FB, "fb") + load(IG, "ig")

by_year = collections.defaultdict(list)
for year, text in rows:
    by_year[year].append(text)

pat = {k: re.compile(v, re.I) for k, v in {**THEMES, **CONTROL}.items()}

print(f"{'year':6} {'n':>5} {'chars':>8} " + " ".join(f"{k[:6]:>7}" for k in list(THEMES)+list(CONTROL)))
print("(densities per 10k chars)")
for y in sorted(by_year):
    texts = by_year[y]
    chars = sum(len(t) for t in texts) or 1
    dens = {}
    for k, p in pat.items():
        hits = sum(1 for t in texts for _ in p.finditer(t))
        dens[k] = hits / chars * 10000
    print(f"{y:6} {len(texts):>5} {chars:>8} " + " ".join(f"{dens[k]:>7.2f}" for k in dens))

# top content words co-occurring with any theme hit (for the writeup's quoting pass)
TOKEN = re.compile(r"[a-z][a-z'\-]{2,}")
STOP = set("the and for with you your this that have from are was were not but all can has had her his him our out how who get got its one our when what where which there their them then than also just like over into more very will would could should been being made much many some any own way back down off new old even still only just because about".split())
co = collections.Counter()
theme_rows = []
for year, text in rows:
    if any(p.search(text) for p in list(pat.values())[:5]):
        theme_rows.append((year, text))
        co.update(t for t in TOKEN.findall(text.lower()) if t not in STOP)
print("\n== top co-occurring words near theme hits ==")
print(", ".join(f"{w}({c})" for w, c in co.most_common(40)))
print(f"\n{len(theme_rows)} theme-hit records total", file=sys.stderr)
