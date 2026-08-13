#!/usr/bin/env python3
"""Extract the Facebook/Meta export without downloading it.

The export is four zips totalling 24.6 GB in a link-readable Drive folder, but
23.5 GB of that is video and 0.5 GB is images. The entire textual record is
2,706 HTML files, 112 MB. This script reads each zip's central directory over
HTTP range requests, then pulls only the entries matching a pattern -- the whole
text corpus costs about 115 MB and four requests instead of a 24.6 GB download.

Two things to know before changing this:

  * The export is the HTML format, not JSON. There is no `.json` anywhere in it.
    Everything is scraped out of Facebook's generated markup, which uses two
    different block shapes (see FB_EXPORT.md).
  * The zip entries are STORED, not deflated, so csize == usize and a ranged
    fetch of a single entry needs no decompression. The inflate path is kept
    because Facebook is not required to keep doing that.

Usage:
    python3 fb_export.py listing                 # write central directories
    python3 fb_export.py fetch '\\.html$'         # pull matching entries
    python3 fb_export.py measure                 # aggregate -> data/

The Drive folder id lives in sessions/LATEST.md; the four file ids are below.
"""
import os, re, sys, json, glob, zlib, struct, subprocess, datetime, collections, html as htmlmod

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORK = os.environ.get("FB_WORK", os.path.join(ROOT, "exports", "facebook"))
OUT = os.path.join(WORK, "extracted")

# facebook-devongallegos-2024-10-26-*.zip, generated 2024-10-26, Drive folder
# 1eODsrIV0wwekB-lFwYaFsjwIXGdz3lb_ ("META DATA").
ZIPS = {
    "jcye8gmw": ("1yFPz7Z_DCr5ywCS4vSvkrnK5r7TgK-sQ", 7860929683),
    "u6fQFxYN": ("1oBTugeW9zmEklpjrTRUhPmJIIZxdAkqt", 6989389621),
    "Qb0Yp5lz": ("1oNd4KN6Cwn47tty4SDb-S1FJu6N9ihE5", 6745239846),
    "ybK72kK8": ("1yDORxBLXsEZYXRyEsvEIP5a7NdEW-Fhr", 3009688392),
}

# ---------------------------------------------------------------- remote zip

def resolve(file_id):
    """Confirmed download URL. Files this size always hit the virus-scan page."""
    base = f"https://drive.usercontent.google.com/download?id={file_id}&export=download"
    page = subprocess.run(["curl", "-sSL", "--max-time", "120", base],
                          capture_output=True, text=True).stdout
    if "<html" not in page.lower():
        return base
    f = dict(re.findall(r'<input type="hidden" name="(\w+)" value="([^"]*)"', page))
    if not f:
        raise RuntimeError("no confirm token on interstitial")
    return f"{base}&confirm={f.get('confirm','t')}&uuid={f.get('uuid','')}"

def fetch(url, start, end, tries=4):
    want = end - start + 1
    for n in range(tries):
        p = subprocess.run(["curl", "-sS", "--max-time", "600",
                            "-H", f"Range: bytes={start}-{end}", url], capture_output=True)
        if p.returncode == 0 and len(p.stdout) == want:
            return p.stdout
        print(f"    retry {n+1}", file=sys.stderr)
    raise RuntimeError(f"range fetch failed {start}-{end}")

def central_dir(url, size):
    tail = fetch(url, size - min(size, 131072), size - 1)
    i = tail.rfind(b"PK\x05\x06")
    if i < 0:
        raise RuntimeError("no EOCD")
    cd_size, cd_off = struct.unpack("<II", tail[i+12:i+20])
    total = struct.unpack("<H", tail[i+10:i+12])[0]
    if 0xFFFFFFFF in (cd_size, cd_off) or total == 0xFFFF:
        j = tail.rfind(b"PK\x06\x07")
        z64 = fetch(url, *(lambda o: (o, o+55))(struct.unpack("<Q", tail[j+8:j+16])[0]))
        total = struct.unpack("<Q", z64[32:40])[0]
        cd_size, cd_off = struct.unpack("<QQ", z64[40:56])
    data = b""
    while len(data) < cd_size:
        n = min(32 << 20, cd_size - len(data))
        data += fetch(url, cd_off + len(data), cd_off + len(data) + n - 1)
    return data, total

def parse_cd(data):
    out, p = [], 0
    while p < len(data) - 4 and data[p:p+4] == b"PK\x01\x02":
        method = struct.unpack("<H", data[p+10:p+12])[0]
        csize, usize = struct.unpack("<II", data[p+20:p+28])
        nlen, elen, clen = struct.unpack("<HHH", data[p+28:p+34])
        dd = struct.unpack("<H", data[p+14:p+16])[0]
        lho = struct.unpack("<I", data[p+42:p+46])[0]
        name = data[p+46:p+46+nlen].decode("utf-8", "replace")
        extra = data[p+46+nlen:p+46+nlen+elen]
        if 0xFFFFFFFF in (csize, usize, lho):
            q = 0
            while q < len(extra) - 3:
                hid, hsz = struct.unpack("<HH", extra[q:q+4])
                if hid == 0x0001:
                    vals, r = [], q + 4
                    for orig in (usize, csize, lho):   # ZIP64 order is fixed
                        if orig == 0xFFFFFFFF and r + 8 <= q + 4 + hsz:
                            vals.append(struct.unpack("<Q", extra[r:r+8])[0]); r += 8
                        else:
                            vals.append(orig)
                    usize, csize, lho = vals
                    break
                q += 4 + hsz
        out.append({"name": name, "usize": usize, "csize": csize, "lho": lho,
                    "method": method,
                    "mtime": f"{((dd>>9)&0x7f)+1980:04d}-{(dd>>5)&0xf:02d}-{dd&0x1f:02d}"})
        p += 46 + nlen + elen + clen
    return out

def cmd_listing():
    os.makedirs(WORK, exist_ok=True)
    for tag, (fid, size) in ZIPS.items():
        url = resolve(fid)
        data, total = central_dir(url, size)
        entries = parse_cd(data)
        print(f"{tag}: {len(entries)}/{total} entries", file=sys.stderr)
        json.dump({"file_id": fid, "url": url, "entries": entries},
                  open(os.path.join(WORK, f"cd_{tag}.json"), "w"))

def cmd_fetch(pattern):
    """Pull entries matching `pattern`, coalescing nearby ones into few requests."""
    rx = re.compile(pattern)
    GAP, MAXSPAN, PAD = 4 << 20, 96 << 20, 4096
    written = 0
    for path in sorted(glob.glob(os.path.join(WORK, "cd_*.json"))):
        meta = json.load(open(path))
        sel = sorted((e for e in meta["entries"]
                      if not e["name"].endswith("/") and rx.search(e["name"])),
                     key=lambda e: e["lho"])
        if not sel:
            continue
        groups, cur = [], []
        for e in sel:
            e["_end"] = e["lho"] + PAD + e["csize"]
            if cur and (e["lho"] - cur[-1]["_end"] > GAP
                        or e["_end"] - cur[0]["lho"] > MAXSPAN):
                groups.append(cur); cur = []
            cur.append(e)
        if cur:
            groups.append(cur)
        for g in groups:
            start, end = g[0]["lho"], max(e["_end"] for e in g)
            blob = fetch(meta["url"], start, end)
            for e in g:
                off = e["lho"] - start
                if blob[off:off+4] != b"PK\x03\x04":
                    print(f"  !! bad header {e['name']}", file=sys.stderr); continue
                nlen, elen = struct.unpack("<HH", blob[off+26:off+30])
                d = blob[off+30+nlen+elen: off+30+nlen+elen+e["csize"]]
                if len(d) < e["csize"]:
                    print(f"  !! short {e['name']}", file=sys.stderr); continue
                if e["method"] == 8:
                    d = zlib.decompressobj(-15).decompress(d)
                dst = os.path.join(OUT, e["name"])
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                open(dst, "wb").write(d)
                written += 1
        print(f"{os.path.basename(path)}: {len(sel)} entries in "
              f"{len(groups)} request(s)", file=sys.stderr)
    print(f"wrote {written} files", file=sys.stderr)

# ------------------------------------------------------------------- parsing

TAG = re.compile(r"<[^>]+>")
TS = re.compile(r'<div class="_a72d">([^<]+)</div>')
HDR = re.compile(r'<div class="_2ph_ _a6-h[^"]*">(.*?)</div>', re.S)
PIN = re.compile(r'<div class="_2pin">(.*?)</div></div>', re.S)
ROW = re.compile(r'<td class="_a6_q">(.*?)</td><td class="[^"]*_a6_r">(.*?)</td>', re.S)
DATE = re.compile(r"(\w{3}) (\d{1,2}), (\d{4}) (\d{1,2}):(\d{2}):(\d{2})\s*([ap]m)")
MONTHS = {m: i+1 for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}

def text(s):
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"</div>", "\n", s)
    return htmlmod.unescape(TAG.sub("", s)).strip()

def parse_date(s):
    m = DATE.search(s or "")
    if not m:
        return None
    mon, day, yr, hh, mm, ss, ap = m.groups()
    try:
        return datetime.datetime(int(yr), MONTHS[mon], int(day),
                                 int(hh) % 12 + (12 if ap == "pm" else 0),
                                 int(mm), int(ss))
    except (ValueError, KeyError):
        return None

def feed_entries(path):
    """Shape A: the `_a6-g` feed block (posts, comments, events, groups)."""
    h = open(path, encoding="utf-8", errors="replace").read()
    out = []
    for raw in re.split(r'(?=<div class="_a6-g)', h[h.find("<body"):])[1:]:
        ts, hdr = TS.search(raw), HDR.search(raw)
        cells = [c for c in (text(c) for c in PIN.findall(raw)) if c]
        body = re.sub(r"\nUpdated \w{3} \d{1,2}, \d{4}[^\n]*", "",
                      "\n".join(cells)).strip()
        out.append({"ts": ts.group(1).strip() if ts else None,
                    "dt": parse_date(ts.group(1) if ts else None),
                    "header": text(hdr.group(1)) if hdr else None,
                    "text": body})
    return out

def table_entries(path):
    """Shape B: label/value tables (post edits, messages, settings)."""
    h = open(path, encoding="utf-8", errors="replace").read()
    out = []
    for chunk in re.split(r'(?=<div class="_3-95 _a6-g">)', h[h.find('role="main"'):]):
        ts = TS.search(chunk)
        if not ts:
            continue
        fields = {text(k): text(v) for k, v in ROW.findall(chunk)}
        if fields:
            out.append({"ts": ts.group(1).strip(),
                        "dt": parse_date(ts.group(1)), **fields})
    return out

BODY = re.compile(r'<div class="_2ph_ _a6-p">(.*?)</div></div>', re.S)

def ai_turns(path):
    """Meta AI chat turns. These use shape B, not the human-thread shape.

    A Message row is followed by an unlabelled row holding its timestamp. Like
    the Grok chats in the Twitter archive, turns carry no speaker field -- the
    alternation has to be inferred, and the bot opens.
    """
    h = open(path, encoding="utf-8", errors="replace").read()
    turns, pending = [], None
    for k, v in ROW.findall(h[h.find('role="main"'):]):
        key, val = text(k), text(v)
        if key == "Message":
            pending = val
        elif not key and pending is not None and parse_date(val):
            turns.append({"text": pending, "dt": parse_date(val)})
            pending = None
    return turns

def message_turns(path):
    """A thread page's turns. Uses shape A, with `_a6-h` carrying the sender.

    Two traps: thread pages are paginated (`message_1.html`, `message_2.html`),
    and turns are emitted newest-first, so sort by `dt` before reading any
    interval off them.
    """
    h = open(path, encoding="utf-8", errors="replace").read()
    turns = []
    for raw in re.split(r'(?=<div class="_a6-g)', h[h.find('role="main"'):])[1:]:
        ts, hdr, body = TS.search(raw), HDR.search(raw), BODY.search(raw)
        dt = parse_date(ts.group(1)) if ts else None
        if not dt:
            continue
        turns.append({"sender": text(hdr.group(1)) if hdr else None,
                      "text": text(body.group(1)) if body else "",
                      "dt": dt})
    return turns

# --------------------------------------------------------------- measurement

def cmd_measure():
    """Aggregate to data/. Lengths and dates only -- never message text."""
    P = lambda *a: os.path.join(OUT, *a)
    words = lambda s: len(s.split())
    out = {}

    posts = [p for p in feed_entries(
        P("your_facebook_activity", "posts",
          "your_posts__check_ins__photos_and_videos_1.html")) if p["dt"]]
    withtext = [p for p in posts if p["text"]]
    out["posts"] = {
        "n": len(posts), "n_with_text": len(withtext),
        "words": sum(words(p["text"]) for p in withtext),
        "first": min(p["dt"] for p in posts).isoformat(),
        "last": max(p["dt"] for p in posts).isoformat(),
        "by_year": {str(y): {"posts": n, "words": sum(
            words(p["text"]) for p in withtext if p["dt"].year == y)}
            for y, n in sorted(collections.Counter(
                p["dt"].year for p in posts).items())},
    }

    edits = sorted((e for e in table_entries(
        P("your_facebook_activity", "posts", "edits_you_made_to_posts.html"))
        if e["dt"]), key=lambda e: e["dt"])
    out["post_edits"] = {
        "n": len(edits),
        "first": edits[0]["dt"].isoformat(), "last": edits[-1]["dt"].isoformat(),
        "by_year": dict(collections.Counter(
            str(e["dt"].year) for e in edits)),
        "lengths": [words(e["Text"]) for e in edits],
        "gaps_sec": [int((b["dt"] - a["dt"]).total_seconds())
                     for a, b in zip(edits, edits[1:])],
    }

    ai = {}
    for f in sorted(glob.glob(P("your_facebook_activity", "messages",
                                "ai_conversations", "*.html"))):
        turns = ai_turns(f)
        if not turns:
            continue
        ai[os.path.basename(f)[:-5]] = {
            "turns": len(turns),
            "first": min(t["dt"] for t in turns).isoformat(),
            "last": max(t["dt"] for t in turns).isoformat(),
            "lengths": [words(t["text"]) for t in turns],
        }
    out["ai_conversations"] = ai

    # thread-level only: counts and dates, never text, never participants
    threads = []
    for f in glob.glob(P("your_facebook_activity", "messages", "*", "*", "*.html")):
        turns = message_turns(f)
        if turns:
            threads.append({"folder": f.split(os.sep)[-3],
                            "turns": len(turns),
                            "first": min(t["dt"] for t in turns).isoformat(),
                            "last": max(t["dt"] for t in turns).isoformat(),
                            "words": sum(words(t["text"]) for t in turns)})
    out["message_threads"] = {
        "n": len(threads),
        "turns": sum(t["turns"] for t in threads),
        "words": sum(t["words"] for t in threads),
        "by_folder": dict(collections.Counter(t["folder"] for t in threads)),
        "first": min((t["first"] for t in threads), default=None),
        "last": max((t["last"] for t in threads), default=None),
    }

    dst = os.path.join(ROOT, "data", "fb_summary.json")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    json.dump(out, open(dst, "w"), indent=1)
    print(f"wrote {dst}", file=sys.stderr)
    return out

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "measure"
    if cmd == "listing":
        cmd_listing()
    elif cmd == "fetch":
        cmd_fetch(sys.argv[2])
    elif cmd == "measure":
        cmd_measure()
    else:
        sys.exit(__doc__)
