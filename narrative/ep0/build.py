#!/usr/bin/env python3
"""Build Episode 0 of The Trajectory: the edit, the mix, the captions and the picture.

Inputs (none of the media is committed):
  --voice   Endorphin's narration recording (any format ffmpeg reads)
  --words   word timestamps for it, JSON from faster-whisper medium.en
            ([{"words": [[start, end, word], ...]}, ...])
  --tts     directory of Kokoro card readings, <card id>.wav (see voice_cards)
  --fonts   directory with AtkinsonHyperlegible-*.ttf, IBMPlexMono-*.ttf, SourceSerif4*.ttf
  --out     working directory; writes ep0.mp4, ep0.srt, timeline.json

The narration text is narrative/ep0/narration.txt; the cards are narrative/ep0/cards.json,
checked verbatim against narrative/TRAJECTORY.md. The look follows
narrative/ART_DIRECTION.md (proposal 2), Episode 0 and section 4. Everything on screen is type,
data from data/, or drawn by this script. No generated imagery.
"""
import argparse, bisect, difflib, json, math, os, re, subprocess, sys
from datetime import date, datetime, timezone

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

SPEED = 1.3          # narration tempo; he offered 1.3 or 1.4. 1.4 puts him near 240 wpm.
PAUSE_MAX = 0.6      # raw-time pauses longer than this are cut down to it
SR = 48000
W, H, FPS = 1920, 1080, 24
COL_W = round(H * 9 / 16)            # the centred 9:16 column (ART_DIRECTION 4.7)
COL_X = (W - COL_W) // 2
PAD = 26
STRIKE, PULSE = 2.0, 1.2   # the Body forms, then one pulse out and back, inside the opening

GROUND, INK = (11, 15, 12), (207, 233, 214)
PHOS, AMBER = (111, 227, 154), (255, 179, 71)
WARM = (246, 238, 222)
PAPER, PAPER_INK = (236, 230, 214), (28, 26, 22)


# ---------------------------------------------------------------- narration and edit

def read_narration():
    typed, units = None, []      # units: ("say", text) | ("card", id)
    for line in open(os.path.join(HERE, "narration.txt")):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        if line.startswith("[TYPED]"):
            typed = line[7:].strip()
        elif line.startswith("[CARD"):
            units.append(("card", line[5:].strip(" ]")))
        else:
            units.append(("say", line))
    return typed, units


def norm(w):
    w = w.lower().replace("’", "'")
    w = re.sub(r"[^a-z0-9']", "", w)
    return {"11th": "11th", "1000": "1000", "1": "1"}.get(w, w)


def align(units, words):
    """Give every narration token a raw time, by sequence alignment to the ASR words."""
    toks = []                                  # (unit index, token)
    for ui, (kind, text) in enumerate(units):
        if kind == "say":
            for t in text.replace("—", " ").split():
                if norm(t):
                    toks.append((ui, t))
    a = [norm(t) for _, t in toks]
    b = [norm(w[2]) for w in words]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    times = [None] * len(toks)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                times[i1 + k] = (words[j1 + k][0], words[j1 + k][1])
        elif tag == "replace" and j2 > j1:
            t0, t1 = words[j1][0], words[j2 - 1][1]
            n = i2 - i1
            for k in range(n):
                times[i1 + k] = (t0 + (t1 - t0) * k / n, t0 + (t1 - t0) * (k + 1) / n)
    # fill gaps (inserted tokens) from neighbours
    for i in range(len(times)):
        if times[i] is None:
            prev = next((times[j][1] for j in range(i - 1, -1, -1) if times[j]), 0.0)
            nxt = next((times[j][0] for j in range(i + 1, len(times)) if times[j]), prev)
            times[i] = (prev, max(prev, nxt))
    return [(ui, t, s, e) for (ui, t), (s, e) in zip(toks, times)]


def pauses(raw, sr):
    """Low-energy runs of at least PAUSE_MAX + 0.3 s, in raw time."""
    h = int(sr * 0.05)
    n = len(raw) // h
    r = 20 * np.log10(np.sqrt((raw[: n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
    thr = np.percentile(r, 10) + 8
    q = r < thr
    out, i = [], 0
    while i < n:
        if q[i]:
            j = i
            while j < n and q[j]:
                j += 1
            if (j - i) * 0.05 >= PAUSE_MAX + 0.3:
                out.append((i * 0.05, j * 0.05))
            i = j
        else:
            i += 1
    return out


class Piece:
    """A raw-time span of the narration, with long pauses removed, then sped up."""

    def __init__(self, t0, t1, silences):
        keep, cur = [], t0
        for s, e in silences:
            if e <= t0 or s >= t1:
                continue
            s, e = max(s, t0), min(e, t1)
            cut0 = s + PAUSE_MAX / 2
            cut1 = e - PAUSE_MAX / 2
            if cut1 > cut0:
                keep.append((cur, cut0))
                cur = cut1
        keep.append((cur, t1))
        self.keep = keep
        self.dur = sum(b - a for a, b in keep) / SPEED

    def map(self, t):
        """raw time -> seconds from the start of this piece, after cuts and tempo."""
        acc = 0.0
        for a, b in self.keep:
            if t <= a:
                return acc / SPEED
            if t <= b:
                return (acc + t - a) / SPEED
            acc += b - a
        return acc / SPEED


def ff_tempo(x, sr):
    p = subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-",
         "-af", f"atempo={SPEED}", "-f", "f32le", "-"],
        input=x.astype(np.float32).tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32)


def load_mono(path, sr=SR):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr),
                        "-af", "highpass=f=70,afftdn=nf=-42", "-f", "f32le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32).copy()


def load_tts(path):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR),
                        "-f", "f32le", "-"], capture_output=True, check=True)
    return np.frombuffer(p.stdout, np.float32).copy()


def build_edit(args):
    typed, units = read_narration()
    cards = {c["id"]: c for c in json.load(open(os.path.join(HERE, "cards.json")))}
    words = [w for s in json.load(open(args.words)) for w in s["words"]]
    toks = align(units, words)
    raw = load_mono(args.voice)
    sil = pauses(raw, SR)

    # split the narration into runs between cards
    runs, cur = [], []
    for ui, (kind, val) in enumerate(units):
        if kind == "card":
            runs.append(("say", cur)); cur = []
            runs.append(("card", val))
        else:
            cur.append(ui)
    runs.append(("say", cur))

    timeline, audio, t = [], [], 0.0
    def put(x):
        nonlocal t
        audio.append(x); t += len(x) / SR

    PRE = 2.8                                            # the typed prompt line
    timeline.append({"kind": "typed", "t0": 0.0, "t1": PRE, "text": typed})
    put(np.zeros(int(PRE * SR), np.float32))

    caps = []
    for kind, val in runs:
        if kind == "card":
            c = cards[val]
            v = load_tts(os.path.join(args.tts, f"{val}.wav"))
            lead, tail = 0.5, 1.0
            timeline.append({"kind": "card", "id": val, "t0": t, "t1": t + lead + len(v) / SR + tail,
                             "v0": t + lead, "v1": t + lead + len(v) / SR})
            put(np.zeros(int(lead * SR), np.float32)); put(v); put(np.zeros(int(tail * SR), np.float32))
            continue
        tk = [x for x in toks if x[0] in val]
        if not tk:
            continue
        r0 = max(0.0, tk[0][2] - 0.12)
        r1 = tk[-1][3] + 0.25
        pc = Piece(r0, r1, sil)
        seg = np.concatenate([raw[int(a * SR):int(b * SR)] for a, b in pc.keep])
        fade = int(0.01 * SR)
        seg[:fade] *= np.linspace(0, 1, fade); seg[-fade:] *= np.linspace(1, 0, fade)
        seg = ff_tempo(seg, SR)
        base = t
        timeline.append({"kind": "say", "t0": base, "t1": base + len(seg) / SR,
                         "units": val})
        for ui, tok, s, e in tk:
            caps.append({"ui": ui, "tok": tok, "t0": base + pc.map(s), "t1": base + pc.map(e)})
        put(seg)
        put(np.zeros(int(0.35 * SR), np.float32))

    # boundary card and credits
    bv = load_tts(os.path.join(args.tts, "boundary.wav"))
    t0 = t
    timeline.append({"kind": "boundary", "t0": t0, "t1": t0 + 0.8 + len(bv) / SR + 6.0,
                     "v0": t0 + 0.8, "v1": t0 + 0.8 + len(bv) / SR})
    put(np.zeros(int(0.8 * SR), np.float32)); put(bv); put(np.zeros(int(6.0 * SR), np.float32))
    timeline.append({"kind": "credits", "t0": t, "t1": t + 9.0})
    put(np.zeros(int(9.0 * SR), np.float32))

    voice = np.concatenate(audio)
    return {"timeline": timeline, "caps": caps, "units": units, "typed": typed,
            "cards": cards, "dur": t}, voice


# ---------------------------------------------------------------- captions

def caption_cues(edit):
    """Group tokens into caption cues of at most two short lines, breaking at punctuation."""
    cues, cur = [], []
    def flush():
        if cur:
            cues.append({"t0": cur[0]["t0"], "t1": cur[-1]["t1"],
                         "text": " ".join(x["tok"] for x in cur)})
            cur.clear()
    for i, x in enumerate(edit["caps"]):
        if cur and x["ui"] != cur[-1]["ui"] and x["t0"] - cur[-1]["t1"] > 0.6:
            flush()
        cur.append(x)
        text = " ".join(y["tok"] for y in cur)
        end = x["tok"][-1] in ".?!:" or (x["tok"][-1] in ",;" and len(text) > 34)
        if end or len(text) > 64:
            flush()
    flush()
    merged = []
    for c in cues:                             # never leave a fragment like "2020." on its own
        if merged and len(c["text"]) < 12 and c["t0"] - merged[-1]["t1"] < 0.4:
            merged[-1]["text"] += " " + c["text"]; merged[-1]["t1"] = c["t1"]
        else:
            merged.append(c)
    cues = merged
    for a, b in zip(cues, cues[1:]):          # hold each cue until the next, within reason
        a["t1"] = min(max(a["t1"] + 0.25, a["t1"]), b["t0"]) if b["t0"] - a["t1"] < 1.2 else a["t1"] + 0.4
    return cues


def srt(cues, edit, path):
    def ts(s):
        ms = int(round(s * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000); return f"{h:02}:{m:02}:{s:02},{ms:03}"
    items = [(c["t0"], c["t1"], c["text"]) for c in cues]
    for ev in edit["timeline"]:
        if ev["kind"] == "card":
            c = edit["cards"][ev["id"]]
            items.append((ev["v0"], ev["v1"], "[" + {"endorphin": "my words, read by Kokoro",
                          "claude": "Claude, read by Kokoro", "record": "news report, read by Kokoro"}
                          [c["speaker"]] + "] " + c["text"].replace("\n", " ")))
        if ev["kind"] == "typed":
            items.append((0.4, ev["t1"], "[typed] " + ev["text"]))
    items.sort()
    with open(path, "w") as f:
        for i, (a, b, x) in enumerate(items, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{x}\n\n")


# ---------------------------------------------------------------- sound design

def sound_bed(edit, n):
    """ART_DIRECTION 7: a low tone under the Horizon, a dry crack for the Body's pulse."""
    bed = np.zeros(n, np.float32)
    tt = np.arange(n) / SR
    for ev in edit["scenes"]:
        if ev["scene"] == "lens":
            a, b = int(ev["t0"] * SR), int(ev["t1"] * SR)
            x = tt[a:b]
            env = np.minimum(1, np.minimum((x - x[0]) / 2.0, (x[-1] - x) / 2.0))
            tone = 0.6 * np.sin(2 * np.pi * 55 * x) + 0.25 * np.sin(2 * np.pi * 110.3 * x)
            bed[a:b] += (10 ** (-34 / 20)) * env * tone
    rng = np.random.default_rng(11)
    for t in edit["cracks"]:
        a = int(t * SR); m = int(0.09 * SR)
        if a + m > n:
            continue
        noise = rng.standard_normal(m).astype(np.float32)
        noise = np.diff(noise, prepend=0)                      # crude high-pass: dry
        env = np.exp(-np.arange(m) / (0.012 * SR))
        bed[a:a + m] += (10 ** (-30 / 20)) * noise * env
    return bed


# ---------------------------------------------------------------- picture

class Fonts:
    def __init__(self, d):
        self.d = d; self.cache = {}
    def get(self, name, size):
        k = (name, size)
        if k not in self.cache:
            files = {"atk": "AtkinsonHyperlegible-Regular.ttf", "atkb": "AtkinsonHyperlegible-Bold.ttf",
                     "atki": "AtkinsonHyperlegible-Italic.ttf",
                     "mono": "IBMPlexMono-Regular.ttf", "monom": "IBMPlexMono-Medium.ttf",
                     "monoi": "IBMPlexMono-Italic.ttf",
                     "serif": "SourceSerif4%5Bopsz,wght%5D.ttf",
                     "serifi": "SourceSerif4-Italic%5Bopsz,wght%5D.ttf"}
            p = os.path.join(self.d, files[name]) if name in files else name
            f = ImageFont.truetype(p, size)
            if name.startswith("serif"):
                try:
                    f.set_variation_by_axes([420, min(max(size, 8), 60)])   # (wght, opsz)
                except Exception:
                    pass
            self.cache[k] = f
        return self.cache[k]


def wrap(draw, text, font, width):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split(" "):
            nxt = (cur + " " + w).strip()
            if draw.textlength(nxt, font=font) <= width or not cur:
                cur = nxt
            else:
                lines.append(cur); cur = w
        lines.append(cur)
    return lines


def reg_marks(d):
    c = (*INK, 38)
    m = 18
    for x, y in [(COL_X + 10, 14), (COL_X + COL_W - 10, 14), (COL_X + 10, H - 14), (COL_X + COL_W - 10, H - 14)]:
        d.line([(x - m // 2, y), (x + m // 2, y)], fill=c, width=1)
        d.line([(x, y - m // 2), (x, y + m // 2)], fill=c, width=1)
        d.ellipse([x - 5, y - 5, x + 5, y + 5], outline=c, width=1)


def day_series():
    start, end = date(2020, 8, 11), date(2024, 5, 31)
    days = (end - start).days + 1
    aid = np.zeros(days); nai = np.zeros(days)
    for line in open(os.path.join(REPO, "data", "AID_DAYS.tsv")):
        d, n = line.split("\t")
        k = (date.fromisoformat(d) - start).days
        if 0 <= k < days:
            aid[k] += int(n)
    for line in open(os.path.join(REPO, "data", "stories_meta.jsonl")):
        c = json.loads(line).get("created_at")
        if c:
            k = (datetime.fromtimestamp(c, timezone.utc).date() - start).days
            if 0 <= k < days:
                nai[k] += 1
    return start, days, aid, nai


def horizon_strip(px_per_day=1, height=500):
    """The Horizon for Episode 0: two bands, square-root scale, textured by grain not hue."""
    start, days, aid, nai = day_series()
    Wd = days * px_per_day
    rng = np.random.default_rng(7)
    def smooth(v, k=5):
        return np.convolve(v, np.ones(k) / k, mode="same")
    a = smooth(np.sqrt(aid) * 4.5, 7) + 3
    b = smooth(np.sqrt(nai) * 26.0, 7) + np.where(np.arange(days) >= (date(2021, 6, 1) - start).days, 2, 0)
    xs = np.arange(Wd) / px_per_day
    a = np.interp(xs, np.arange(days), a); b = np.interp(xs, np.arange(days), b)
    img = np.zeros((height, Wd, 3), np.float32)
    base = int(height * 0.74)
    yy = np.arange(height)[:, None]
    top_a = base - a; top_b = top_a - b
    # bedrock below the record
    img[:] = np.array(GROUND, np.float32)
    bed = yy >= base
    img[bed[:, 0]] = np.array((26, 28, 26), np.float32)
    silt = (yy >= top_a[None, :]) & (yy < base)
    sand = (yy >= top_b[None, :]) & (yy < top_a[None, :])
    g1 = rng.normal(0, 6, (height, Wd))
    g2 = rng.normal(0, 14, (height, Wd)) + 6 * np.sin(yy / 2.3)
    for ch, (s, t) in enumerate(zip((58, 64, 60), (198, 182, 150))):
        img[..., ch] = np.where(silt, s + g1, img[..., ch])
        img[..., ch] = np.where(sand, t + g2, img[..., ch])
    img = np.clip(img, 0, 255).astype(np.uint8)
    return Image.fromarray(img), start, px_per_day, base, top_b


def hare_tracks(d, x, y, col):
    for i, (dx, dy) in enumerate([(0, 0), (7, 3), (22, -2), (30, 2)]):
        r = 3 if i % 2 == 0 else 5
        d.ellipse([x + dx - r, y + dy - r // 2 - 3, x + dx + r, y + dy + r // 2 - 3], fill=col)


def body_path(seed=3):
    """The Body as a fulgurite: hand -> device -> mast -> fibre -> data centre, and back."""
    rng = np.random.default_rng(seed)
    nodes = [(170, 820), (330, 760), (560, 640), (1350, 600), (1700, 420)]
    pts = [nodes[0]]
    for (x0, y0), (x1, y1) in zip(nodes, nodes[1:]):
        n = max(6, int(math.hypot(x1 - x0, y1 - y0) / 22))
        for k in range(1, n + 1):
            f = k / n
            j = 0 if k == n else rng.normal(0, 9)
            pts.append((x0 + (x1 - x0) * f + rng.normal(0, 4), y0 + (y1 - y0) * f + j))
    branches = []
    for i in rng.choice(range(5, len(pts) - 5), 9, replace=False):
        bx, by = pts[i]; ang = rng.uniform(-2.4, -0.7) if rng.random() < .5 else rng.uniform(0.7, 2.4)
        br = [(bx, by)]
        for k in range(rng.integers(3, 7)):
            ang += rng.normal(0, .4)
            bx += 14 * math.cos(ang); by += 14 * math.sin(ang); br.append((bx, by))
        branches.append((i, br))
    return nodes, pts, branches


def draw_body(img, prog, pulse, alpha=1.0, data=None):
    """prog 0..1: how much of the strike has formed. pulse: position 0..2 (out and back) or None."""
    nodes, pts, branches = data
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    n = max(2, int(len(pts) * prog))
    crust = (150, 132, 104, int(170 * alpha)); glass = (220, 236, 240, int(200 * alpha))
    seg = pts[:n]
    d.line(seg, fill=crust, width=9, joint="curve")
    for i, br in branches:
        if i < n:
            d.line(br, fill=crust, width=5, joint="curve")
            d.line(br, fill=(190, 205, 210, int(120 * alpha)), width=1)
    d.line(seg, fill=glass, width=2, joint="curve")
    if prog >= 1:
        hx, hy = nodes[0]                       # the hand: fused sand, no human detail
        d.rounded_rectangle([hx - 26, hy - 8, hx + 18, hy + 22], 9, fill=(150, 132, 104, int(150 * alpha)))
        dx, dy = nodes[1]
        d.rounded_rectangle([dx - 12, dy - 22, dx + 12, dy + 22], 4, outline=(170, 160, 140, int(170 * alpha)), width=2)
        mx, my = nodes[2]
        d.line([(mx, my), (mx, my + 70)], fill=(150, 132, 104, int(150 * alpha)), width=3)
        cx, cy = nodes[4]                       # the data centre: far, large, a field of racks
        for r in range(4):
            for c in range(9):
                x = cx - 60 + c * 22; y = cy - 40 + r * 30
                d.rectangle([x, y, x + 14, y + 22], outline=(150, 140, 120, int(150 * alpha)), width=1)
    if pulse is not None and prog >= 1:
        f = pulse if pulse <= 1 else 2 - pulse
        k = int(f * (len(pts) - 1))
        x, y = pts[k]
        for r, a in [(18, 40), (9, 110), (4, 255)]:
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, int(a * alpha)))
    img.alpha_composite(lay)


class Renderer:
    def __init__(self, edit, fonts):
        self.e, self.F = edit, fonts
        self.strip, self.h0, self.ppd, self.hbase, self.htop = horizon_strip()
        self.body = body_path()
        self.cues = edit["cues"]
        self.cue_t = [c["t0"] for c in self.cues]

    # ---- helpers
    def xdate(self, d):
        return (d - self.h0).days * self.ppd

    def accent(self, t):
        return AMBER if t >= self.e["amber_at"] else PHOS

    def stamp(self, d, text):
        f = self.F.get("mono", 18)
        d.text((COL_X + COL_W - PAD, 34), text, font=f, fill=(*INK, 210), anchor="ra")

    def source(self, d, text, y=None):
        f = self.F.get("mono", 15)
        for i, ln in enumerate(wrap(d, text, f, COL_W - 2 * PAD)):
            d.text((COL_X + PAD, (y or H - 46) + i * 19), ln, font=f, fill=(*INK, 150))

    def caption(self, d, t):
        i = bisect.bisect_right(self.cue_t, t) - 1
        if i < 0 or t > self.cues[i]["t1"]:
            return
        f = self.F.get("atk", 27)
        lines = wrap(d, self.cues[i]["text"], f, COL_W - 2 * PAD)
        y = H - 92 - 34 * (len(lines) - 1)
        for k, ln in enumerate(lines):
            w = d.textlength(ln, font=f)
            d.rectangle([W / 2 - w / 2 - 8, y + k * 34 - 3, W / 2 + w / 2 + 8, y + k * 34 + 31], fill=(0, 0, 0, 170))
            d.text((W / 2, y + k * 34), ln, font=f, fill=(*WARM, 255), anchor="ma")

    def prompts(self, d, lines, t, y0=110, typed_until=None):
        """Text-adventure prompt lines, top of the column, with a block cursor."""
        f = self.F.get("mono", 26)
        acc = self.accent(t)
        y = y0
        for k, (txt, t_on) in enumerate(lines):
            if t < t_on:
                break
            n = len(txt) if t - t_on > len(txt) / 14 else int((t - t_on) * 14)
            s = "> " + txt[:n]
            d.text((COL_X + PAD, y), s, font=f, fill=(*acc, 255))
            last = (s, y)
            y += 40
        if t >= lines[0][1] if lines else False:
            s, yy = last
            if int(t * 2) % 2 == 0:
                x = COL_X + PAD + d.textlength(s, font=f) + 4
                d.rectangle([x, yy + 4, x + 14, yy + 30], fill=(*acc, 255))
        return y

    def lens(self, img, d, cx, cy, r, x_right, t, tracks=False, label_alpha=255):
        """The circular lens onto the Horizon. x_right: strip pixel shown at the lens's right edge."""
        sw = 2 * r
        x0 = int(max(0, x_right - sw))
        crop = self.strip.crop((x0, 0, x0 + sw, sw)) if self.strip.height == sw else self.strip.crop((x0, 0, x0 + sw, self.strip.height)).resize((sw, sw))
        if crop.width < sw:
            pad = Image.new("RGB", (sw, sw), GROUND); pad.paste(crop, (sw - crop.width, 0)); crop = pad
        # never show a date before the episode reaches it: mask everything right of x_right
        m = Image.new("L", (sw, sw), 0)
        ImageDraw.Draw(m).ellipse([0, 0, sw - 1, sw - 1], fill=255)
        reveal = Image.new("L", (sw, sw), 0)
        ImageDraw.Draw(reveal).rectangle([0, 0, int(x_right - x0), sw], fill=255)
        mm = Image.fromarray(np.minimum(np.array(m), np.array(reveal)))
        crop = crop.convert("RGBA")
        cd = ImageDraw.Draw(crop)
        top = self.htop
        # the episode's accent as a thin skin of light on the top surface
        acc = self.accent(t)
        xs = np.arange(x0, min(x0 + sw, len(top) * 1))
        ptsk = [(int(x - x0), int(top[x] * sw / self.strip.height)) for x in xs[::3] if x < x_right]
        if len(ptsk) > 1:
            cd.line(ptsk, fill=(*acc, 200), width=2)
        if tracks:
            xt = self.xdate(date(2023, 11, 4)) - x0
            if 0 < xt < sw:
                yt = int(top[int(xt + x0)] * sw / self.strip.height) + 7
                hare_tracks(cd, int(xt) - 14, yt, (40, 34, 26, 255))
        vig = Image.new("L", (sw, sw), 0)
        ImageDraw.Draw(vig).ellipse([r * 0.12, r * 0.12, sw - r * 0.12, sw - r * 0.12], fill=255)
        vig = vig.filter(ImageFilter.GaussianBlur(r * 0.18))
        mm = Image.fromarray((np.array(mm).astype(np.float32) * np.array(vig) / 255).astype(np.uint8))
        img.paste(crop, (cx - r, cy - r), mm)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(150, 170, 200, 70), width=2)
        d.ellipse([cx - r - 2, cy - r - 1, cx + r - 1, cy + r + 1], outline=(220, 140, 150, 40), width=1)

    # ---- frame
    def frame(self, t):
        e = self.e
        img = Image.new("RGBA", (W, H), (*GROUND, 255))
        d = ImageDraw.Draw(img, "RGBA")
        sc = next((s for s in e["scenes"] if s["t0"] <= t < s["t1"]), e["scenes"][-1])
        getattr(self, "s_" + sc["scene"])(img, d, t, sc)
        reg_marks(d)
        if sc["scene"] not in ("card", "boundary", "credits"):
            self.caption(d, t)
        return img.convert("RGB")

    # ---- scenes
    def s_open(self, img, d, t, sc):
        # the first full drawing of the Body, on the first keystroke; slow, once, no caption
        k = sc["strike"]
        if t >= k:
            prog = min(1, (t - k) / STRIKE)
            pulse = None
            if prog >= 1:
                p = (t - k - STRIKE) / PULSE
                pulse = p if 0 <= p <= 2 else None
            draw_body(img, prog, pulse, alpha=0.55, data=self.body)
            d = ImageDraw.Draw(img, "RGBA")
        self.prompts(d, sc["prompts"], t)
        if t >= sc["date_on"]:
            self.source(d, "First timestamped action, 2020-08-11T03:17Z · AI Dungeon export · "
                           "data/AID_DAYS.tsv (analysis/aid_days.py)")

    def s_lens(self, img, d, t, sc):
        f = (t - sc["t0"]) / (sc["t1"] - sc["t0"])
        f = 0.5 - 0.5 * math.cos(math.pi * min(1, f))
        xr = self.xdate(sc["from"]) + f * (self.xdate(sc["to"]) - self.xdate(sc["from"]))
        r = 250
        self.lens(img, d, W // 2, 420, r, xr, t)
        shown = self.h0 + (sc["to"] - self.h0) * 0 if False else None
        cur = date.fromordinal(self.h0.toordinal() + int(xr / self.ppd))
        fm = self.F.get("mono", 18)
        d.text((COL_X + COL_W - PAD, 34), cur.isoformat(), font=fm, fill=(*INK, 210), anchor="ra")
        fl = self.F.get("mono", 15)
        k = 2 * r / self.strip.height
        if xr > self.xdate(date(2020, 8, 25)):
            d.text((W // 2 - r * 0.55, 420 - r + int(self.hbase * k) + 10), "AI Dungeon", font=fl, fill=(*INK, 190))
        if xr > self.xdate(date(2021, 7, 15)):
            d.text((W // 2 + r * 0.05, 420 - r + int(self.hbase * k) - 150), "NovelAI", font=fl, fill=(*INK, 190))
        self.source(d, "Band thickness: square root of AI Dungeon actions per day (data/AID_DAYS.tsv) "
                       "and of NovelAI stories created per day (data/stories_meta.jsonl).", y=700)

    def s_ground(self, img, d, t, sc):
        pr = sc.get("prompts") or ([] if any(i["type"] == "turns" for i in sc.get("items", [])) else [("", sc["t0"])])
        y = self.prompts(d, pr, t) if pr else 110
        for it in sc.get("items", []):
            if t < it["t"]:
                continue
            if it["type"] == "title":
                f = self.F.get(it.get("font", "atkb"), it.get("size", 40))
                for k, ln in enumerate(wrap(d, it["text"], f, COL_W - 2 * PAD)):
                    d.text((COL_X + PAD, it["y"] + k * int(f.size * 1.2)), ln, font=f,
                           fill=(*(PAPER if it.get("font", "").startswith("serif") else WARM), 255))
            elif it["type"] == "source":
                self.source(d, it["text"])
            elif it["type"] == "mono":
                self.monobox(d, it["who"], it["text"], it["y"], it.get("stamp"), size=22)
            elif it["type"] == "number":
                f = self.F.get("atkb", 92)
                d.text((W // 2, it["y"]), it["text"], font=f, fill=(*self.accent(t), 255), anchor="ma")
                fs = self.F.get("atk", 22)
                for k, ln in enumerate(wrap(d, it["note"], fs, COL_W - 2 * PAD)):
                    d.text((W // 2, it["y"] + 120 + k * 28), ln, font=fs, fill=(*INK, 220), anchor="ma")
            elif it["type"] == "turns":
                f = self.F.get("mono", 26)
                n = min(8, int((t - it["t"]) / it["step"]) + 1)
                for k in range(n):
                    d.text((COL_X + PAD, it["y"] + k * 40), ">", font=f, fill=(*self.accent(t), 150))
                if n == 8 and int(t * 2) % 2 == 0:
                    d.rectangle([COL_X + PAD + 26, it["y"] + 7 * 40 + 4, COL_X + PAD + 40, it["y"] + 7 * 40 + 30],
                                fill=(*self.accent(t), 255))
            elif it["type"] == "tracks":
                self.lens(img, d, W // 2, it["y"], 150, self.xdate(date(2023, 11, 20)), t, tracks=True)
                d = ImageDraw.Draw(img, "RGBA")

    def monobox(self, d, who, text, y, stamp=None, size=24, reveal=1.0):
        f = self.F.get("mono", size)
        lines = wrap(d, text, f, COL_W - 2 * PAD - 32)
        lh = int(size * 1.45)
        hgt = len(lines) * lh + 30
        x0, x1 = COL_X + PAD, COL_X + COL_W - PAD
        fs = self.F.get("monom", 16)
        d.text((x0, y - 26), " ".join(who.upper()), font=fs, fill=(*INK, 200))
        if stamp:
            d.text((x1, y - 26), stamp, font=self.F.get("mono", 15), fill=(*INK, 150), anchor="ra")
        d.rectangle([x0, y, x1, y + hgt], outline=(*INK, 160), width=1)
        total = sum(len(l) for l in lines); show = int(total * reveal)
        for k, ln in enumerate(lines):
            part = ln[:max(0, show)]; show -= len(ln)
            d.text((x0 + 16, y + 15 + k * lh), part, font=f, fill=(*INK, 255))
        return y + hgt

    def s_card(self, img, d, t, sc):
        c = self.e["cards"][sc["id"]]
        # type on at reading speed, a little ahead of the voice
        rv = min(1.0, max(0.0, (t - sc["v0"]) / max(0.1, (sc["v1"] - sc["v0"]) * 0.92)) + 0.04)
        self.stamp(d, c["stamp"])
        self.source(d, c["source"])
        if c["speaker"] == "endorphin":
            fl = self.F.get("mono", 16)
            d.text((COL_X + PAD, 96), c["label"].upper(), font=fl, fill=(*INK, 170))
            size = 30 if len(c["text"]) < 300 else 27
            f = self.F.get("atkb", size)
            lines = wrap(d, c["text"], f, COL_W - 2 * PAD)
            lh = int(size * 1.32)
            y = max(140, (H - len(lines) * lh) // 2 - 20)
            total = sum(len(l) for l in lines); show = int(total * rv)
            for k, ln in enumerate(lines):
                part = ln[:max(0, show)]; show -= len(ln)
                d.text((COL_X + PAD, y + k * lh), part, font=f, fill=(*WARM, 255))
        elif c["speaker"] == "claude":
            f = self.F.get("mono", 24)
            lines = wrap(d, c["text"], f, COL_W - 2 * PAD - 32)
            y = max(150, (H - len(lines) * 35) // 2 - 40)
            self.monobox(d, "Claude", c["text"], y, None, size=24, reveal=rv)
        else:
            # the public record: set like a printed page, with a rule and the source below
            f = self.F.get("serif", 27)
            text = c["text"]
            lines = wrap(d, text, f, COL_W - 2 * PAD - 48)
            lh = 38
            hgt = len(lines) * lh + 90
            y0 = (H - hgt) // 2 - 20
            d.rectangle([COL_X + PAD, y0, COL_X + COL_W - PAD, y0 + hgt], fill=(*PAPER, 255))
            d.text((COL_X + PAD + 24, y0 + 18), c["label"], font=self.F.get("serifi", 19), fill=(*PAPER_INK, 200))
            d.line([COL_X + PAD + 24, y0 + 50, COL_X + COL_W - PAD - 24, y0 + 50], fill=(*PAPER_INK, 160), width=1)
            total = sum(len(l) for l in lines); show = int(total * rv)
            xf = self.F.get("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 25)
            for k, ln in enumerate(lines):
                part = ln[:max(0, show)]; show -= len(ln)
                x = COL_X + PAD + 24; y = y0 + 66 + k * lh
                for j, chunk in enumerate(part.split("\U0001D54F")):
                    if j:
                        d.text((x, y + 2), "\U0001D54F", font=xf, fill=(*PAPER_INK, 255)); x += d.textlength("\U0001D54F", font=xf)
                    d.text((x, y), chunk, font=f, fill=(*PAPER_INK, 255)); x += d.textlength(chunk, font=f)

    def s_boundary(self, img, d, t, sc):
        # the Horizon frozen at the episode's last date, at 30%
        r = 230
        self.lens(img, d, W // 2, 800, 170, self.xdate(date(2024, 5, 31)), t)
        ov = Image.new("RGBA", (W, H), (*GROUND, int(255 * 0.7)))
        img.alpha_composite(ov)
        d = ImageDraw.Draw(img, "RGBA")
        est = ["the start of the archive on 11 August 2020;",
               "the Bugs Bunny Optimization, dated 4 November 2023, the day of Musk's Grok personality post;",
               "a guess that I marked as a guess, confirmed by Claude as observed evidence, and conceded as unsourced eight turns later;",
               "the first dated steps of the coercive-harm work and the artist-value work."]
        nes = ["that the 2024 estimate of “100 to 1,000 times” is more than Claude's estimate in one conversation."]
        # two columns, equal width and equal time; each item arrives on a cut
        span = sc["v1"] - sc["v0"]
        cw = 640; gap = 60; xl = W // 2 - cw - gap // 2; xr = W // 2 + gap // 2
        fh = self.F.get("atkb", 32); fb = self.F.get("atk", 25)
        d.text((xl, 150), "Establishes", font=fh, fill=(*WARM, 255))
        d.text((xr, 150), "Does not establish", font=fh, fill=(*WARM, 255))
        d.line([xl, 198, xl + cw, 198], fill=(*AMBER, 200), width=2)
        d.line([xr, 198, xr + cw, 198], fill=(*AMBER, 200), width=2)
        times = sc["item_t"]
        y = 222
        for k, s in enumerate(est):
            if t < times[k]:
                break
            for j, ln in enumerate(wrap(d, "– " + s, fb, cw)):
                d.text((xl, y), ln, font=fb, fill=(*INK, 255)); y += 33
            y += 14
        if t >= times[len(est)]:
            y = 222
            for j, ln in enumerate(wrap(d, "– " + nes[0], fb, cw)):
                d.text((xr, y), ln, font=fb, fill=(*INK, 255)); y += 33
        self.source(d, "Episode 0 boundary card · narrative/TRAJECTORY.md")

    def s_credits(self, img, d, t, sc):
        rows = [("atk", "Written, researched, voiced and directed by", "atkb", "Endorphin"),
                ("mono", "Narration wording, art direction, edit:", "mono", "Claude (Anthropic)"),
                ("mono", "Card voices:", "mono", "Kokoro-82M · am_michael, af_heart, bm_george"),
                ("serif", "Records:", "serif", "AI Dungeon export · NovelAI export · Claude export"),
                ("atk", "Generated imagery:", "atk", "none — type, data and drawing"),
                ("atk", "Fonts:", "atk", "Atkinson Hyperlegible · IBM Plex Mono · Source Serif 4 (SIL OFL)"),
                ("serifi", "Systems reading:", "serifi", "Gregory Bateson, Steps to an Ecology of Mind (1972)")]
        y = 170
        for fa, a, fb_, b in rows:
            f1 = self.F.get(fa, 19); f2 = self.F.get(fb_, 25)
            d.text((W // 2, y), a, font=f1, fill=(*INK, 170), anchor="ma")
            for ln in wrap(d, b, f2, COL_W - 2 * PAD):
                y += 32; d.text((W // 2, y), ln, font=f2, fill=(*WARM, 255), anchor="ma")
            y += 52
        d.text((W // 2, H - 110), "github.com/devinendorphin/devinendorphins-dextromethorphan-archaive",
               font=self.F.get("mono", 13), fill=(*INK, 200), anchor="ma")


# ---------------------------------------------------------------- scenes from the edit

def plan_scenes(edit):
    """Lay the picture over the edit. Times come from the narration tokens, so a re-record
    or a different tempo moves every cut with it."""
    caps, units = edit["caps"], edit["units"]
    def word_t(phrase, after=0.0, end=False):
        ws = phrase.lower().split()
        toks = [norm(c["tok"]) for c in caps]
        for i in range(len(caps)):
            if caps[i]["t0"] < after:
                continue
            if toks[i:i + len(ws)] == [norm(w) for w in ws]:
                return caps[i + len(ws) - 1]["t1"] if end else caps[i]["t0"]
        raise KeyError(phrase)
    tl = edit["timeline"]
    cards = [ev for ev in tl if ev["kind"] == "card"]
    bnd = next(ev for ev in tl if ev["kind"] == "boundary")
    cred = next(ev for ev in tl if ev["kind"] == "credits")

    t_lens = word_t("for me a language model")
    t_bbo = word_t("my oldest project")
    t_ten = word_t("ten minutes later")
    t_musk = word_t("musk sold")
    t_apr8 = word_t("on april 8th")
    t_ask = word_t("i asked for correction")
    t_eight = word_t("eight turns later")
    t_idea = word_t("the idea went into")
    t_hund = word_t("in that conversation claude estimated")
    t_apr20 = word_t("on april 20th")
    t_may = word_t("on may 10th")
    t_three = word_t("we had three")
    t_end = cards and caps[-1]["t1"] + 0.4

    S = []
    S.append({"scene": "open", "t0": 0.0, "t1": t_lens,
              "prompts": [(edit["typed"], 0.3), ("2020-08-11", word_t("on august 11th"))],
              "date_on": word_t("on august 11th"), "strike": word_t("the first record")})
    S.append({"scene": "lens", "t0": t_lens, "t1": t_bbo,
              "from": date(2020, 12, 20), "to": date(2023, 10, 20)})
    S.append({"scene": "ground", "t0": t_bbo, "t1": cards[0]["t0"],
              "prompts": [("2023-11-04", t_bbo)],
              "items": [{"type": "title", "t": word_t("the bugs bunny optimization"), "y": 190,
                         "text": "The Bugs Bunny Optimization", "size": 40},
                        {"type": "tracks", "t": word_t("the bugs bunny optimization"), "y": 560},
                        {"type": "source", "t": t_bbo, "text": "Claude export · f4e5d724 · 2023-11-04"}]})
    for i, ev in enumerate(cards):
        S.append({"scene": "card", "t0": ev["t0"], "t1": ev["t1"], "id": ev["id"],
                  "v0": ev["v0"], "v1": ev["v1"]})
    # grounds between the cards
    S.append({"scene": "ground", "t0": cards[0]["t1"], "t1": cards[1]["t0"],
              "prompts": [("", cards[0]["t1"])], "items": []})
    S.append({"scene": "ground", "t0": cards[1]["t1"], "t1": cards[2]["t0"],
              "prompts": [("2023-11-04 23:51", t_ten)], "items": []})
    S.append({"scene": "ground", "t0": cards[2]["t1"], "t1": t_apr8,
              "prompts": [("later that night", word_t("later that night"))],
              "items": [{"type": "mono", "who": "Claude", "t": word_t("more dismissive", ),
                         "text": "“more dismissive of the core idea than was appropriate.”",
                         "y": 300, "stamp": "2023-11-05"},
                        {"type": "source", "t": word_t("later that night"),
                         "text": "Claude export · f4e5d724"}]})
    S.append({"scene": "ground", "t0": t_apr8, "t1": cards[3]["t0"],
              "prompts": [("2024-04-08", t_apr8)],
              "items": [{"type": "source", "t": t_apr8, "text": "Claude export · e5825937 · 2024-04-08"}]})
    S.append({"scene": "ground", "t0": cards[3]["t1"], "t1": cards[4]["t0"],
              "prompts": [("", cards[3]["t1"])], "items": []})
    # signature shot: eight blank turns tick past
    S.append({"scene": "ground", "t0": cards[4]["t1"], "t1": t_idea,
              "items": [{"type": "turns", "t": cards[4]["t1"] + 0.2, "y": 150,
                         "step": max(0.15, (word_t("for the paper", end=True) - cards[4]["t1"] - 0.2) / 8)},
                        {"type": "source", "t": cards[4]["t1"], "text": "Claude export · e5825937 · turns 15–23 · audits/power-bending/CAT_VIDEO_PROPAGATION.md"}]})
    S.append({"scene": "ground", "t0": t_idea, "t1": t_apr20,
              "prompts": [("artists", t_idea)],
              "items": [{"type": "number", "t": word_t("at 100 to"), "y": 330, "text": "100–1,000×",
                         "note": "Claude's estimate of the true value, in one conversation."},
                        {"type": "source", "t": word_t("at 100 to"), "text": "Claude export · e5825937 · 2024-04-08"}]})
    S.append({"scene": "ground", "t0": t_apr20, "t1": t_may,
              "prompts": [("2024-04-20", t_apr20)],
              "items": [{"type": "title", "t": word_t("coercive harm"), "y": 220, "text": "coercive harm", "size": 40},
                        {"type": "source", "t": t_apr20, "text": "Claude export · 1e8358d5 · 2024-04-20"}]})
    S.append({"scene": "ground", "t0": t_may, "t1": bnd["t0"],
              "prompts": [("2024-05-10", t_may)],
              "items": [{"type": "title", "t": word_t("in a conversation called"), "y": 200, "font": "serif",
                         "text": "The Full Value of Artists' Work", "size": 34},
                        {"type": "title", "t": word_t("called creativeunits"), "y": 300, "font": "mono",
                         "text": "CreativeUnits", "size": 30},
                        {"type": "source", "t": t_may, "text": "Claude export · 014de5b7 · 2024-05-10"}]})
    vb = bnd["v1"] - bnd["v0"]
    S.append({"scene": "boundary", "t0": bnd["t0"], "t1": bnd["t1"], "v0": bnd["v0"], "v1": bnd["v1"],
              "item_t": [bnd["v0"] + vb * f for f in (0.0, 0.12, 0.30, 0.55, 0.72)]})
    S.append({"scene": "credits", "t0": cred["t0"], "t1": cred["t1"] + 1})
    S.sort(key=lambda s: s["t0"])
    edit["scenes"] = S
    edit["amber_at"] = t_bbo
    o = S[0]
    edit["cracks"] = [o["strike"] + STRIKE + PULSE, o["strike"] + STRIKE + 2 * PULSE]   # pulse out, back


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", required=True); ap.add_argument("--words", required=True)
    ap.add_argument("--tts", required=True); ap.add_argument("--fonts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--still", type=float, nargs="*", help="render stills at these times only")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    edit, voice = build_edit(a)
    edit["cues"] = caption_cues(edit)
    plan_scenes(edit)
    srt(edit["cues"], edit, os.path.join(a.out, "ep0.srt"))
    json.dump({k: edit[k] for k in ("timeline", "scenes", "cues", "dur")},
              open(os.path.join(a.out, "timeline.json"), "w"), default=str, indent=1)

    R = Renderer(edit, Fonts(a.fonts))
    if a.still:
        for t in a.still:
            R.frame(t).save(os.path.join(a.out, f"still_{t:07.2f}.png"))
        return

    n = len(voice)
    mix = voice + sound_bed(edit, n)
    wav = os.path.join(a.out, "mix.wav")
    sf.write(wav, mix, SR, subtype="FLOAT")
    nf = int(edit["dur"] * FPS)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                          "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart",
                          os.path.join(a.out, "ep0.mp4")], stdin=subprocess.PIPE)
    for i in range(nf):
        p.stdin.write(R.frame(i / FPS).tobytes())
        if i % (FPS * 20) == 0:
            print(f"{i / FPS:6.1f}s / {edit['dur']:.1f}s", file=sys.stderr, flush=True)
    p.stdin.close(); p.wait()


if __name__ == "__main__":
    main()
