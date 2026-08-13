#!/usr/bin/env python3
"""Find the posts whose content is in their images, not their text.

Word-count analysis of this archive has a blind spot. A post that carries a
screenshot and no caption contributes ~0 words to the 439,512 in FACEBOOK.md,
so any measure built on words treats it as though nothing was said. In most
years that is a rounding error. In 2019 it is half the year.

A post counts as image-only here if it carries at least one attached image and
at most three words of its own text -- the threshold absorbs Facebook's
"Timeline photos" auto-caption and short markers like "who's mr pot now?"
without absorbing real captions. Bare URLs are not counted as words, since a
link is not the post's own prose.

Usage:
    python3 analysis/fb_imageposts.py          # after fb_export.py fetch
"""
import os, re, sys, collections, html as htmlmod

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORK = os.environ.get("FB_WORK", os.path.join(ROOT, "exports", "facebook"))
OUT = os.path.join(WORK, "extracted")
sys.path.insert(0, HERE)
from fb_export import parse_date

SRC = os.path.join(OUT, "your_facebook_activity", "posts",
                   "your_posts__check_ins__photos_and_videos_1.html")
TAG = re.compile(r"<[^>]+>")
CAP = 3          # words of own text at or below which a post is "image-only"

def posts():
    h = open(SRC, encoding="utf-8", errors="replace").read()
    for raw in re.split(r'(?=<div class="_a6-g)', h[h.find("<body"):])[1:]:
        ts = re.search(r'<div class="_a72d">([^<]+)</div>', raw)
        if not ts:
            continue
        dt = parse_date(ts.group(1))
        if not dt:
            continue
        cells = re.findall(r'<div class="_2pin">(.*?)</div></div>', raw, re.S)
        txt = " ".join(htmlmod.unescape(TAG.sub(" ", c)) for c in cells)
        txt = re.sub(r"Updated \w{3} \d{1,2}, \d{4}[^A-Za-z]*", "", txt)
        words = [w for w in txt.split() if not w.startswith("http")]
        imgs = re.findall(r'<img src="(your_facebook_activity/[^"]+)"', raw)
        yield dt, len(words), imgs

def main():
    rows = list(posts())
    print(f"{'year':<6}{'posts':>7}{'image-only':>12}{'images':>8}{'share':>8}")
    for y in sorted({d.year for d, _, _ in rows}):
        r = [x for x in rows if x[0].year == y]
        io = [x for x in r if x[2] and x[1] <= CAP]
        flag = "  <--" if len(io) / len(r) > .25 else ""
        print(f"{y:<6}{len(r):>7}{len(io):>12}{sum(len(x[2]) for x in io):>8}"
              f"{100*len(io)/len(r):>7.0f}%{flag}")

    io = [x for x in rows if x[2] and x[1] <= CAP]
    print(f"\n{len(io)} image-only posts carrying {sum(len(x[2]) for x in io)} "
          f"images, contributing ~0 words to the corpus total")

    # the 2019 burst, by day
    b = collections.Counter(d.date() for d, w, i in rows
                            if d.year == 2019 and i and w <= CAP)
    print("\n2019 image-only posts by day (top 8):")
    for day, n in b.most_common(8):
        print(f"  {day}  {n:3}  {'#'*n}")

if __name__ == "__main__":
    main()
