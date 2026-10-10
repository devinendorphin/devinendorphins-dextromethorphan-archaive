#!/usr/bin/env python3
"""Build ORIGIN: conversation 8195d24b, summarized, every message, read by Kokoro.

  script.txt   the summary, one block per message (Endorphin's words; Claude's condensed)
  turns.tsv    per message: sender, UTC stamp, original length in characters, tool calls
               (from the public share snapshot; no text)

usage: build.py --kokoro MODEL.onnx VOICES.bin --fonts DIR --out DIR [--still T ...]

Each message is set on screen in its speaker's typeface (ART_DIRECTION.md 4.1) and lit sentence
by sentence as the voice reads it. Beside it, a ladder of all 58 messages at their original
lengths, so the ratio between the two speakers is on screen as data, not as a claim.
"""
import argparse, hashlib, importlib.util, json, os, re, subprocess, sys
from datetime import datetime

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ep0", os.path.join(HERE, "..", "ep0", "build.py"))
ep0 = importlib.util.module_from_spec(spec); spec.loader.exec_module(ep0)
Fonts, wrap, reg_marks = ep0.Fonts, ep0.wrap, ep0.reg_marks
W, H, FPS, SR = ep0.W, ep0.H, 24, 24000
COL_W, COL_X, PAD = ep0.COL_W, ep0.COL_X, ep0.PAD
GROUND, INK, WARM, AMBER, PHOS = ep0.GROUND, ep0.INK, ep0.WARM, ep0.AMBER, ep0.PHOS

VOICE = {"E": "am_michael", "C": "af_heart", "R": "bm_george"}
SPEED = 1.1
GAP_SENT, GAP_PARA, GAP_TURN = 0.18, 0.45, 0.9
SAY = {"KLMC2": "K L M C two", "DAIR": "Dare", "JSON": "jay-son", "ZIP": "zip", "xAI": "x A I",
       "8195d24b": ""}
SHARE = "claude.ai/share/cafbe599-3475-4c51-883b-b15e34747689"

TITLE = [("R", "Tracing AI safety funding sources."),
         ("R", "A conversation between Endorphin and Claude, from the twenty-seventh of May to the fourth of June, 2026."),
         ("R", "Fifty-eight messages, summarized. His words are his. Claude's are condensed by Claude.")]
BOUNDARY = {
    "est": ["the mechanism the veriticide ledger later names, assembled in one conversation, 27–30 May 2026: harm spread below every threshold; the decider is not the bearer; convergence without a meeting; harm recast as care;",
            "the human side's corrections, and what each one moved;",
            "two self-witness statements, and the correction of the first by the second."],
    "not": ["the 200 million to 1 billion, or the roughly 70,000 deciders: Claude's estimates, built from round guesses;",
            "“thirty to a hundred times”: no source before this conversation;",
            "that Claude remembers: its one search of past conversations found nothing, and it could not read this conversation's date;",
            "the unsourced assertions, such as the lab-leak line. This is a summary; the full text is at the link."]}
BOUNDARY_SAY = ("Boundary card. This conversation establishes: the mechanism the veriticide ledger later names, "
                "assembled in one conversation between the twenty-seventh and the thirtieth of May: harm spread below every "
                "threshold; the decider is not the bearer; convergence without a meeting; harm recast as care. "
                "The human side's corrections, and what each one moved. Two self-witness statements, and the correction "
                "of the first by the second. It does not establish: the two hundred million to a billion, or the roughly "
                "seventy thousand deciders. Those are Claude's estimates, built from round guesses. Thirty to a hundred times, "
                "which has no source before this conversation. That Claude remembers: its one search of past conversations "
                "found nothing, and it could not read this conversation's date. Or the unsourced assertions, such as the "
                "lab-leak line. This is a summary. The full text is at the link.")


# ---------------------------------------------------------------- text

def read_script():
    txt = open(os.path.join(HERE, "script.txt")).read()
    txt = "\n".join(l for l in txt.split("\n") if not l.startswith("#"))
    out = []
    for n, who, body in re.findall(r"=== (\d+) ([EC])\n(.*?)(?=\n=== |\Z)", txt, re.S):
        paras = [p.strip().replace("\n", " ") for p in body.strip().split("\n\n") if p.strip()]
        out.append({"n": int(n), "who": who, "paras": paras})
    return out


def read_turns():
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(HERE, "turns.tsv"))][1:]
    return {int(r[0]): {"who": r[1], "utc": r[2], "chars": int(r[3]), "tools": r[4] if len(r) > 4 else ""}
            for r in rows}


def sentences(p):
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z"“(])', p)
    return [s for s in parts if s.strip()]


def speakable(s):
    for k, v in SAY.items():
        s = re.sub(r"\b%s\b" % re.escape(k), v, s)
    return s.replace("—", ", ").replace("–", " to ")


# ---------------------------------------------------------------- voice

class Voice:
    def __init__(self, model, voices, cache):
        from kokoro_onnx import Kokoro
        self.k = Kokoro(model, voices); self.cache = cache; os.makedirs(cache, exist_ok=True)

    def say(self, who, text):
        v = VOICE[who]
        key = hashlib.sha1(f"{v}|{SPEED}|{text}".encode()).hexdigest()[:16]
        p = os.path.join(self.cache, key + ".wav")
        if not os.path.exists(p):
            a, sr = self.k.create(speakable(text), voice=v, speed=SPEED,
                                  lang="en-gb" if v.startswith("b") else "en-us")
            sf.write(p, a, sr)
        a, sr = sf.read(p, dtype="float32")
        assert sr == SR
        return a


# ---------------------------------------------------------------- layout

def paginate(d, F, who, paras):
    """Pages of (para index, sentence) lists that fit the column."""
    if who == "E":
        f, lh, maxh = F.get("atkb", 29), 39, 700
    else:
        f, lh, maxh = F.get("mono", 23), 33, 660
    width = COL_W - 2 * PAD - (32 if who == "C" else 0)
    pages, cur, h = [], [], 0
    for pi, p in enumerate(paras):
        for si, s in enumerate(sentences(p)):
            n = len(wrap(d, s, f, width))           # approximate: sentences are set inline below
            add = n * lh + (lh // 2 if si == 0 and cur else 0)
            if cur and h + add > maxh:
                pages.append(cur); cur, h = [], 0
                add = n * lh
            cur.append((pi, s)); h += add
    if cur:
        pages.append(cur)
    return pages


def layout_page(d, F, who, page):
    """Set a page: returns [(x, y, text, sentence index)] runs, words flowing inline per paragraph."""
    if who == "E":
        f, lh = F.get("atkb", 29), 39
    else:
        f, lh = F.get("mono", 23), 33
    width = COL_W - 2 * PAD - (32 if who == "C" else 0)
    runs, y, x0 = [], 0, 0
    last_p = None
    line, line_w = [], 0
    def flush():
        nonlocal line, line_w, y
        x = 0
        for (txt, si) in line:
            runs.append((x, y, txt, si)); x += d.textlength(txt, font=f)
        line, line_w = [], 0; y += lh
    for si, (pi, s) in enumerate(page):
        if last_p is not None and pi != last_p:
            flush(); y += lh // 2
        last_p = pi
        for wtok in s.split(" "):
            tok = wtok + " "
            tw = d.textlength(tok, font=f)
            if line and line_w + tw - d.textlength(" ", font=f) > width:
                flush()
            line.append((tok, si)); line_w += tw
    if line:
        flush()
    return runs, y, f, lh


# ---------------------------------------------------------------- edit

def build(a):
    F = Fonts(a.fonts)
    V = Voice(a.kokoro[0], a.kokoro[1], os.path.join(a.out, "tts"))
    msgs, turns = read_script(), read_turns()
    scratch = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    events, audio, t = [], [], 0.0
    def put(x):
        nonlocal t
        audio.append(x.astype(np.float32)); t += len(x) / SR
    def silence(s):
        put(np.zeros(int(s * SR)))

    # title
    t0 = t; times = []
    silence(0.6)
    for who, s in TITLE:
        times.append(t); put(V.say(who, s)); silence(0.5)
    silence(0.6)
    events.append({"kind": "title", "t0": t0, "t1": t, "times": times})

    last_day = None
    for m in msgs:
        meta = turns[m["n"]]
        assert meta["who"] == m["who"], m["n"]
        day = meta["utc"][:10]
        if day != last_day:
            events.append({"kind": "day", "t0": t, "t1": t + 2.4, "day": day, "utc": meta["utc"]})
            silence(2.4); last_day = day
        for pg in paginate(scratch, F, m["who"], m["paras"]):
            ev = {"kind": "msg", "n": m["n"], "who": m["who"], "page": pg, "t0": t, "sent": []}
            silence(0.25)
            prev_p = None
            for pi, s in pg:
                if prev_p is not None and pi != prev_p:
                    silence(GAP_PARA - GAP_SENT)
                prev_p = pi
                st = t; put(V.say(m["who"], s)); ev["sent"].append((st, t)); silence(GAP_SENT)
            silence(0.35)
            ev["t1"] = t; events.append(ev)
        silence(GAP_TURN)

    t0 = t; silence(0.8); bv0 = t; put(V.say("R", BOUNDARY_SAY)); bv1 = t; silence(6.0)
    events.append({"kind": "boundary", "t0": t0, "t1": t, "v0": bv0, "v1": bv1})
    events.append({"kind": "credits", "t0": t, "t1": t + 10.0}); silence(10.0)
    return events, np.concatenate(audio), turns


# ---------------------------------------------------------------- picture

class Blend:
    """Pillow blends alpha for shapes but not for text: pre-mix text colours against the ground."""
    def __init__(self, d):
        self.d = d
    def __getattr__(self, k):
        return getattr(self.d, k)
    def text(self, xy, txt, fill=None, **kw):
        if fill is not None and len(fill) == 4:
            a = fill[3] / 255
            fill = tuple(int(c * a + g * (1 - a)) for c, g in zip(fill[:3], GROUND))
        return self.d.text(xy, txt, fill=fill, **kw)


class Pic:
    def __init__(self, events, turns, F):
        self.ev, self.turns, self.F = events, turns, F
        self.t_ev = [e["t0"] for e in events]
        self.maxc = max(v["chars"] for v in turns.values())

    def at(self, t):
        import bisect
        i = max(0, bisect.bisect_right(self.t_ev, t) - 1)
        return self.ev[i]

    def ladder(self, d, cur_n):
        """All 58 messages at original length (characters), linear. His warm, Claude's grey."""
        x0, y0, bh, gap, maxw = COL_X + COL_W + 70, 120, 11, 3, 470
        f = self.F.get("mono", 14)
        d.text((x0, y0 - 46), "8195d24b · 58 messages · original length", font=f, fill=(*INK, 150))
        for n in range(len(self.turns)):
            v = self.turns[n]
            w = max(2, int(maxw * v["chars"] / self.maxc))
            y = y0 + n * (bh + gap)
            base = WARM if v["who"] == "E" else (150, 160, 155)
            a = 255 if n == cur_n else (120 if cur_n is not None and n < cur_n else 45)
            col = AMBER if n == cur_n else base
            d.rectangle([x0, y, x0 + w, y + bh], fill=(*col, a))
        yb = y0 + len(self.turns) * (bh + gap) + 14
        d.rectangle([x0, yb + 4, x0 + 10, yb + 14], fill=(*WARM, 200))
        d.text((x0 + 16, yb), "Endorphin  14,754 chars", font=f, fill=(*INK, 150))
        d.rectangle([x0, yb + 26, x0 + 10, yb + 36], fill=(150, 160, 155, 200))
        d.text((x0 + 16, yb + 22), "Claude  207,797 chars", font=f, fill=(*INK, 150))

    def frame_key(self, t):
        e = self.at(t)
        if e["kind"] == "msg":
            k = sum(1 for (s0, s1) in e["sent"] if t >= s0)
            return ("msg", id(e), k)
        if e["kind"] == "day":
            n = int((t - e["t0"]) * 14); return ("day", id(e), min(n, 20), int(t * 2) % 2)
        if e["kind"] == "title":
            return ("title", sum(1 for x in e["times"] if t >= x))
        if e["kind"] == "boundary":
            span = e["v1"] - e["v0"]
            return ("bnd", sum(1 for f in (0.0, 0.18, 0.3, 0.42, 0.52, 0.7, 0.8, 0.9) if t >= e["v0"] + span * f))
        return (e["kind"],)

    def render(self, t):
        e = self.at(t)
        img = Image.new("RGB", (W, H), GROUND); d = Blend(ImageDraw.Draw(img, "RGBA"))
        getattr(self, "r_" + e["kind"])(d, t, e)
        reg_marks(d)
        return img.convert("RGB")

    def r_title(self, d, t, e):
        k = sum(1 for x in e["times"] if t >= x)
        if k >= 1:
            f = self.F.get("serif", 40)
            for i, ln in enumerate(wrap(d, "Tracing AI safety funding sources", f, COL_W - 2 * PAD)):
                d.text((COL_X + PAD, 330 + i * 50), ln, font=f, fill=(*WARM, 255))
            d.line([COL_X + PAD, 450, COL_X + COL_W - PAD, 450], fill=(*INK, 120), width=1)
            d.text((COL_X + PAD, 462), "Claude conversation 8195d24b", font=self.F.get("mono", 16), fill=(*INK, 170))
        if k >= 2:
            d.text((COL_X + PAD, 510), "Endorphin and Claude", font=self.F.get("atkb", 26), fill=(*WARM, 255))
            d.text((COL_X + PAD, 548), "27 May – 4 June 2026", font=self.F.get("mono", 20), fill=(*INK, 220))
        if k >= 3:
            f = self.F.get("atk", 21)
            for i, ln in enumerate(wrap(d, "58 messages, summarized. His words are his. Claude's are condensed by Claude, 10 October 2026. Both read by Kokoro.", f, COL_W - 2 * PAD)):
                d.text((COL_X + PAD, 620 + i * 28), ln, font=f, fill=(*INK, 200))
        self.ladder(d, None)

    def r_day(self, d, t, e):
        s = e["day"]; n = min(len(s), int((t - e["t0"]) * 14))
        f = self.F.get("mono", 30)
        txt = "> " + s[:n]
        d.text((COL_X + PAD, 470), txt, font=f, fill=(*PHOS, 255))
        if int(t * 2) % 2 == 0:
            x = COL_X + PAD + d.textlength(txt, font=f) + 4
            d.rectangle([x, 476, x + 16, 504], fill=(*PHOS, 255))
        self.ladder(d, None)

    def r_msg(self, d, t, e):
        meta = self.turns[e["n"]]
        who = e["who"]
        k = sum(1 for (s0, s1) in e["sent"] if t >= s0)       # sentences started
        fm = self.F.get("mono", 16)
        name = "ENDORPHIN" if who == "E" else "CLAUDE"
        d.text((COL_X + PAD, 40), f"{e['n']:02d}  {' '.join(name)}", font=self.F.get("monom", 16),
               fill=(*(WARM if who == "E" else INK), 230))
        d.text((COL_X + COL_W - PAD, 40), meta["utc"][:16].replace("T", " ") + " UTC", font=fm,
               fill=(*INK, 200), anchor="ra")
        if meta["tools"]:
            label = " · ".join(x.replace("web_searchx", "web search ×").replace("conversation_searchx", "memory search ×")
                                    for x in meta["tools"].split(","))
            d.text((COL_X + PAD, 66), "[" + label + "]", font=self.F.get("mono", 14), fill=(*AMBER, 200))
        runs, hgt, f, lh = layout_page(d, self.F, who, e["page"])
        top = max(110, (H - hgt) // 2 - 10)
        x0 = COL_X + PAD + (16 if who == "C" else 0)
        if who == "C":
            d.rectangle([COL_X + PAD, top - 16, COL_X + COL_W - PAD, top + hgt + 6], outline=(*INK, 130), width=1)
        for (x, y, txt, si) in runs:
            if si < k - 1:
                col = (*(WARM if who == "E" else INK), 255)
            elif si == k - 1:
                col = (*(WARM if who == "E" else (240, 250, 244)), 255)
            else:
                col = (*(WARM if who == "E" else INK), 70)
            d.text((x0 + x, top + y), txt, font=f, fill=col)
        src = f"8195d24b · msg {e['n']} · " + ("his words" if who == "E" else "condensed by Claude")
        d.text((COL_X + PAD, H - 44), src, font=self.F.get("mono", 14), fill=(*INK, 150))
        self.ladder(d, e["n"])

    def r_boundary(self, d, t, e):
        span = e["v1"] - e["v0"]
        cuts = [e["v0"] + span * f for f in (0.0, 0.18, 0.3, 0.42, 0.52, 0.7, 0.8, 0.9)]
        cw, gap = 640, 60
        xl, xr = W // 2 - cw - gap // 2, W // 2 + gap // 2
        fh, fb = self.F.get("atkb", 30), self.F.get("atk", 23)
        d.text((xl, 130), "Establishes", font=fh, fill=(*WARM, 255))
        d.text((xr, 130), "Does not establish", font=fh, fill=(*WARM, 255))
        d.line([xl, 176, xl + cw, 176], fill=(*AMBER, 200), width=2)
        d.line([xr, 176, xr + cw, 176], fill=(*AMBER, 200), width=2)
        y = 198
        for i, s in enumerate(BOUNDARY["est"]):
            if t < cuts[i]:
                break
            for ln in wrap(d, "– " + s, fb, cw):
                d.text((xl, y), ln, font=fb, fill=(*INK, 255)); y += 31
            y += 12
        y = 198
        for i, s in enumerate(BOUNDARY["not"]):
            if t < cuts[3 + i]:
                break
            for ln in wrap(d, "– " + s, fb, cw):
                d.text((xr, y), ln, font=fb, fill=(*INK, 255)); y += 31
            y += 12
        d.text((W // 2, H - 60), SHARE, font=self.F.get("mono", 16), fill=(*INK, 190), anchor="ma")

    def r_credits(self, d, t, e):
        rows = [("atk", "Words", "atkb", "Endorphin and Claude, 27 May – 4 June 2026"),
                ("mono", "Summary, layout and edit", "mono", "Claude (Anthropic), 10 October 2026"),
                ("mono", "Voices", "mono", "Kokoro-82M · am_michael (Endorphin) · af_heart (Claude) · bm_george"),
                ("serif", "Full conversation", "mono", SHARE),
                ("atk", "Fonts", "atk", "Atkinson Hyperlegible · IBM Plex Mono · Source Serif 4 (SIL OFL)")]
        y = 230
        for fa, a_, fb_, b in rows:
            d.text((W // 2, y), a_, font=self.F.get(fa, 19), fill=(*INK, 170), anchor="ma")
            for ln in wrap(d, b, self.F.get(fb_, 22), COL_W - 2 * PAD):
                y += 30; d.text((W // 2, y), ln, font=self.F.get(fb_, 22), fill=(*WARM, 255), anchor="ma")
            y += 56
        d.text((W // 2, H - 110), "github.com/devinendorphin/devinendorphins-dextromethorphan-archaive",
               font=self.F.get("mono", 13), fill=(*INK, 200), anchor="ma")


def srt(events, path):
    def ts(s):
        ms = int(round(s * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000); return f"{h:02}:{m:02}:{s:02},{ms:03}"
    i = 0
    with open(path, "w") as f:
        for e in events:
            if e["kind"] != "msg":
                continue
            for (s0, s1), (_, s) in zip(e["sent"], e["page"]):
                i += 1
                who = "ENDORPHIN" if e["who"] == "E" else "CLAUDE"
                f.write(f"{i}\n{ts(s0)} --> {ts(s1)}\n{who}: {s}\n\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kokoro", nargs=2, required=True); ap.add_argument("--fonts", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--still", type=float, nargs="*")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    events, audio, turns = build(a)
    dur = len(audio) / SR
    print(f"duration {dur / 60:.1f} min", file=sys.stderr)
    srt(events, os.path.join(a.out, "origin.srt"))
    P = Pic(events, turns, Fonts(a.fonts))
    if a.still:
        for t in a.still:
            P.render(t).save(os.path.join(a.out, f"still_{t:07.1f}.png"))
        return
    wav = os.path.join(a.out, "voice.wav"); sf.write(wav, audio, SR)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                          "-af", "aresample=48000,loudnorm=I=-16:TP=-1.5:LRA=11",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-tune", "stillimage",
                          "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
                          "-movflags", "+faststart", os.path.join(a.out, "origin.mp4")], stdin=subprocess.PIPE)
    last_key, last = None, None
    for i in range(int(dur * FPS)):
        t = i / FPS
        k = P.frame_key(t)
        if k != last_key:
            last, last_key = P.render(t).tobytes(), k
        p.stdin.write(last)
    p.stdin.close(); p.wait()


if __name__ == "__main__":
    main()
