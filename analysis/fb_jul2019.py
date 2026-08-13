#!/usr/bin/env python3
"""OCR and characterise the July 2019 screenshot series.

157 of 314 posts in 2019 carry an image and no text, so every word-count pass
over this archive is blind to half that year (analysis/fb_imageposts.py). The
174 images attached to 2019-07-20..23 are that blind spot's core. Endorphin
cleared them for analysis on 2026-08-13: they are pre-redacted.

The redaction claim checks out and is worth stating precisely, because it is
not what "redacted" usually means. There are no names, handles, phone numbers
or email addresses anywhere in the OCR -- every capitalised name that appears
is a public figure or a published author. What is blacked out is a recurring
*category term*, struck out with a bar everywhere it occurs, including in
running text where the sentence needs it. The argument is built to work
without the label.

Requires tesseract. Register classification is deliberately crude and leaves
roughly half the set unlabelled; treat the counts as indicative, and read the
OCR rather than the tally when it matters.

Usage:
    python3 analysis/fb_jul2019.py ocr        # write exports/facebook/ocr/
    python3 analysis/fb_jul2019.py report
"""
import os, re, sys, glob, json, subprocess, collections, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORK = os.environ.get("FB_WORK", os.path.join(ROOT, "exports", "facebook"))
OUT, OCR = os.path.join(WORK, "extracted"), os.path.join(WORK, "ocr")
sys.path.insert(0, HERE)
from fb_export import parse_date

SRC = os.path.join(OUT, "your_facebook_activity", "posts",
                   "your_posts__check_ins__photos_and_videos_1.html")
LO, HI = datetime.datetime(2019, 7, 20), datetime.datetime(2019, 7, 24)

def series():
    """(timestamp, image path) for every image posted in the window."""
    h = open(SRC, encoding="utf-8", errors="replace").read()
    out = []
    for raw in re.split(r'(?=<div class="_a6-g)', h[h.find("<body"):])[1:]:
        ts = re.search(r'<div class="_a72d">([^<]+)</div>', raw)
        if not ts:
            continue
        dt = parse_date(ts.group(1))
        if not dt or not (LO <= dt < HI):
            continue
        for p in re.findall(r'<img src="(your_facebook_activity/[^"]+)"', raw):
            out.append((dt, p))
    return sorted(out)

def cmd_ocr():
    os.makedirs(OCR, exist_ok=True)
    n = 0
    for _, p in series():
        src = os.path.join(OUT, p)
        if not os.path.exists(src):
            continue
        dst = os.path.join(OCR, os.path.basename(p)[:-4])
        subprocess.run(["tesseract", src, dst, "--psm", "4"],
                       capture_output=True)
        n += 1
    print(f"ocr'd {n} images -> {OCR}", file=sys.stderr)

REGISTERS = [
    ("mechanism",      r"agent [ab]\b|lovebomb|the host|smear campaign|flying monkey|"
                       r"triangulat|stonewall|turn their back"),
    ("multiplicity",   r"dissociat|different selves|voices|underworld|"
                       r"antipsychotic|psychiatr|therapist|clinical"),
    ("drug politics",  r"methamphetamine|dopamine|harm reduction|drug war|nixon|"
                       r"ehrlichman|opioid|prohibition"),
    ("DM",             r"hugz|screenshot you wanted|nevermind please|belittle our|"
                       r"jun \d{1,2}, 2019"),
    ("theory",         r"hegel|bergson|deleuze|monstrous|pity|plateaus|bateson"),
]

def classify(t):
    for name, pat in REGISTERS:
        if re.search(pat, t, re.I):
            return name
    return "unclassified" if len(t) >= 60 else "no text"

def cmd_report():
    order = {os.path.basename(p)[:-4]: dt for dt, p in series()}
    texts = {os.path.basename(f)[:-4]:
             " ".join(open(f, encoding="utf-8", errors="replace").read().split())
             for f in glob.glob(os.path.join(OCR, "*.txt"))}
    if not texts:
        sys.exit("no OCR output; run `ocr` first")

    print(f"{len(texts)} screenshots, "
          f"{sum(1 for t in texts.values() if len(t) >= 60)} with readable text, "
          f"{sum(len(t) for t in texts.values()):,} characters\n")

    # identity scan -- the check behind the redaction claim
    joined = "\n".join(texts.values())
    for label, pat in [("@handles", r"@[A-Za-z0-9_.]{3,}"),
                       ("phone numbers", r"\b\d{3}[-.]\d{3}[-.]\d{4}\b"),
                       ("emails", r"[\w.]+@[\w.]+\.\w+")]:
        print(f"  {label:14} {len(set(re.findall(pat, joined)))}")

    print("\nregister (indicative -- see module docstring):")
    c = collections.Counter(classify(t) for t in texts.values())
    for k, n in c.most_common():
        print(f"  {n:4}  {k}")

    print("\nby day:")
    per = collections.defaultdict(collections.Counter)
    for k, t in texts.items():
        per[order[k].date().isoformat() if k in order else "?"][classify(t)] += 1
    for day in sorted(per):
        tot = sum(per[day].values())
        print(f"  {day}  {tot:3}  " +
              ", ".join(f"{k}:{n}" for k, n in per[day].most_common()))

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    {"ocr": cmd_ocr, "report": cmd_report}.get(cmd, lambda: sys.exit(__doc__))()
