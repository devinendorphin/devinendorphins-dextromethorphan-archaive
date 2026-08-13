#!/usr/bin/env python3
"""Manifest the October 2020 episode videos -- "cohort A" in analysis/FACEBOOK.md.

These are the fifteen videos posted 2020-10-02 .. 2020-11-09, before the
242-day silence that separates them from the VQGAN cohort. They are the
earliest surviving output of the loop READINGS.md IX reads as a score, so what
matters about them is whether they actually carry narration: a score played
aloud should be video with a continuous audio track, not silent generative art.

Duration and track types are read straight out of the MP4 atoms rather than
shelling to ffprobe, which is not installed in the container.

Writes data/fb_cohort_a.tsv -- dates, durations and Endorphin's own captions.
Never the "Upload IP address" field that sits in the same HTML block.

Usage:
    python3 analysis/fb_cohort_a.py            # after fb_export.py fetch
"""
import os, re, sys, struct, datetime, html as htmlmod

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORK = os.environ.get("FB_WORK", os.path.join(ROOT, "exports", "facebook"))
OUT = os.path.join(WORK, "extracted")
sys.path.insert(0, HERE)
from fb_export import parse_date

LO = datetime.datetime(2020, 10, 1)
HI = datetime.datetime(2020, 11, 10)

# ------------------------------------------------------------------ mp4 atoms

def atoms(fh, end, want, depth=0):
    """Yield (type, payload_start, payload_end) for atoms at this level."""
    while fh.tell() < end - 8:
        pos = fh.tell()
        hdr = fh.read(8)
        if len(hdr) < 8:
            return
        size = struct.unpack(">I", hdr[:4])[0]
        typ = hdr[4:8].decode("latin1", "replace")
        if size == 1:                       # 64-bit extended size
            size = struct.unpack(">Q", fh.read(8))[0]
            body = pos + 16
        elif size == 0:                     # extends to end of file
            size = end - pos
            body = pos + 8
        else:
            body = pos + 8
        if size < 8:
            return
        if typ in want:
            yield typ, body, pos + size
        fh.seek(pos + size)

def probe(path):
    """Return (duration_seconds, set_of_track_handler_types)."""
    total = os.path.getsize(path)
    dur, handlers = None, set()
    with open(path, "rb") as fh:
        for _, mb, me in atoms(fh, total, {"moov"}):
            fh.seek(mb)
            for typ, b, e in atoms(fh, me, {"mvhd", "trak"}):
                if typ == "mvhd":
                    fh.seek(b)
                    ver = fh.read(1)[0]
                    fh.seek(b + (20 if ver == 1 else 12))
                    if ver == 1:
                        ts, d = struct.unpack(">IQ", fh.read(12))
                    else:
                        ts, d = struct.unpack(">II", fh.read(8))
                    if ts:
                        dur = d / ts
                else:
                    fh.seek(b)
                    for _, mb2, me2 in atoms(fh, e, {"mdia"}):
                        fh.seek(mb2)
                        for _, hb, _he in atoms(fh, me2, {"hdlr"}):
                            fh.seek(hb + 8)
                            handlers.add(fh.read(4).decode("latin1", "replace"))
                        break
                fh.seek(b if typ == "mvhd" else b)
            break
    return dur, handlers

# ------------------------------------------------------------------- manifest

TAGS = re.compile(r"<[^>]+>")

def entries():
    src = os.path.join(OUT, "your_facebook_activity", "posts", "your_videos.html")
    h = open(src, encoding="utf-8", errors="replace").read()
    out = []
    for raw in re.split(r'(?=<div class="_a6-g)', h[h.find('role="main"'):])[1:]:
        m = re.search(r'<video src="([^"]+)"', raw)
        t = re.search(r'<div class="_a72d">([^<]+)</div>', raw)
        if not (m and t):
            continue
        dt = parse_date(t.group(1))
        if not dt or not (LO <= dt < HI):
            continue
        # caption sits in the _3-95 div beside the <video>; the sibling table
        # holds the upload IP, which is deliberately not read.
        cap = re.search(r'<div class="_3-95">(.*?)</div>', raw, re.S)
        cap = htmlmod.unescape(TAGS.sub("", cap.group(1))).strip() if cap else ""
        out.append({"dt": dt, "path": m.group(1), "caption": " ".join(cap.split())})
    return sorted(out, key=lambda e: e["dt"])

def main():
    rows, missing, total = [], 0, 0.0
    for e in entries():
        p = os.path.join(OUT, e["path"])
        if not os.path.exists(p):
            missing += 1
            continue
        dur, handlers = probe(p)
        total += dur or 0
        rows.append((e["dt"], os.path.getsize(p), dur, handlers, e["caption"],
                     os.path.basename(e["path"])))

    print(f"{len(rows)} videos, {missing} missing, "
          f"{sum(r[1] for r in rows)/1e6:.0f} MB, "
          f"{total/60:.1f} min total runtime\n")
    print(f"{'date':<20}{'MB':>7}{'dur':>9}  tracks       caption")
    for dt, sz, dur, hs, cap, _ in rows:
        d = f"{int(dur//60)}:{int(dur%60):02d}" if dur else "?"
        print(f"{dt.strftime('%Y-%m-%d %H:%M'):<20}{sz/1e6:7.1f}{d:>9}  "
              f"{'+'.join(sorted(hs)) or '?':<12} {cap[:64]}")

    withaudio = sum(1 for r in rows if "soun" in r[3])
    print(f"\naudio track present: {withaudio}/{len(rows)}")

    dst = os.path.join(ROOT, "data", "fb_cohort_a.tsv")
    with open(dst, "w") as fh:
        fh.write("date\tbytes\tseconds\ttracks\tfilename\tcaption\n")
        for dt, sz, dur, hs, cap, name in rows:
            fh.write(f"{dt.isoformat()}\t{sz}\t{dur or ''}\t"
                     f"{'+'.join(sorted(hs))}\t{name}\t{cap}\n")
    print(f"wrote {dst}")

if __name__ == "__main__":
    main()
