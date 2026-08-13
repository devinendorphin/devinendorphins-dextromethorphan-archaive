#!/usr/bin/env python3
"""Test Endorphin's 2020-10-02 claim that dictated text is identifiable by
'the lack of commas'.

He wrote: "For most of it, i've been using the dictation function which I never
use, so you'll know who wrote what by the lack of commas."

If that discriminator is real, comma rate per word in his own posts should fall
once dictation becomes the default input method (his post dates that to
roughly Sept-Oct 2020).

House rule applies: match on length before comparing, since comma rate is not
length-independent -- a 12-word status update has less room for a subordinate
clause than a 400-word essay.
"""
import os, sys, datetime, collections, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fb_export import feed_entries

posts = [p for p in feed_entries(
    "exports/facebook/extracted/your_facebook_activity/posts/"
    "your_posts__check_ins__photos_and_videos_1.html")
    if p["dt"] and p["text"]]

def rate(p, ch=","):
    w = len(p["text"].split())
    return p["text"].count(ch) / w if w else 0.0

print("=== comma rate per word, by year (all posts) ===")
by = collections.defaultdict(list)
for p in posts:
    by[p["dt"].year].append(p)
for y in sorted(by):
    g = by[y]
    med = st.median(len(p["text"].split()) for p in g)
    print(f"  {y}  n={len(g):5}  median_len={med:5.0f}w  "
          f"comma/word={st.mean(rate(p) for p in g):.4f}")

# Length-matched comparison. Dictation is dated to Sept 2020 by the post
# itself; compare the two years either side, restricted to a shared length band.
pre = [p for p in posts if 2018 <= p["dt"].year <= 2020 and p["dt"] < datetime.datetime(2020, 9, 1)]
post_ = [p for p in posts if datetime.datetime(2020, 9, 1) <= p["dt"] < datetime.datetime(2023, 1, 1)]

print(f"\npre-dictation  (2018-01 .. 2020-08): n={len(pre)}")
print(f"post-dictation (2020-09 .. 2022-12): n={len(post_)}")

for lo, hi in [(0, 10**9), (20, 60), (60, 150), (150, 400), (400, 10**9)]:
    a = [p for p in pre if lo <= len(p["text"].split()) < hi]
    b = [p for p in post_ if lo <= len(p["text"].split()) < hi]
    if len(a) < 15 or len(b) < 15:
        print(f"  band {lo}-{hi}w: too few (n={len(a)}/{len(b)}), skipped")
        continue
    ra = st.mean(rate(p) for p in a); rb = st.mean(rate(p) for p in b)
    la = st.median(len(p['text'].split()) for p in a)
    lb = st.median(len(p['text'].split()) for p in b)
    band = "ALL" if hi > 10**8 and lo == 0 else f"{lo}-{hi}w"
    print(f"  band {band:>10}: pre n={len(a):4} ({la:4.0f}w) {ra:.4f}  |  "
          f"post n={len(b):4} ({lb:4.0f}w) {rb:.4f}  |  delta {rb-ra:+.4f} "
          f"({100*(rb-ra)/ra:+.1f}%)")

# Control: a punctuation mark dictation should NOT suppress the same way.
# Sentence-final periods survive dictation because the speaker pauses; if the
# period rate moves as much as the comma rate, the effect is about post style
# generally, not about dictation.
print("\n=== control: period rate, same bands ===")
for lo, hi in [(20, 60), (60, 150), (150, 400)]:
    a = [p for p in pre if lo <= len(p["text"].split()) < hi]
    b = [p for p in post_ if lo <= len(p["text"].split()) < hi]
    if len(a) < 15 or len(b) < 15:
        continue
    ra = st.mean(rate(p, ".") for p in a); rb = st.mean(rate(p, ".") for p in b)
    print(f"  band {lo}-{hi}w: pre {ra:.4f}  post {rb:.4f}  "
          f"delta {rb-ra:+.4f} ({100*(rb-ra)/ra:+.1f}%)")
