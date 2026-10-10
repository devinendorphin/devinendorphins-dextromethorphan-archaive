#!/usr/bin/env python3
"""Voice the Episode 0 cards and the boundary card with Kokoro (kokoro-onnx, model v1.0).

One voice per speaker, so the ear gets the same rule the eye gets from the typefaces:
  Endorphin's own words  am_michael   (not his voice, by his choice: a second voice for pace)
  Claude                 af_heart
  the public record      bm_george   (also reads the boundary card)

usage: voice_cards.py MODEL.onnx VOICES.bin OUTDIR
"""
import json, os, sys
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = {"endorphin": "am_michael", "claude": "af_heart", "record": "bm_george"}
SPEED = 1.1

BOUNDARY = ("Boundary card. Episode zero establishes: the start of the archive on 11 August 2020. "
            "The Bugs Bunny Optimization, dated 4 November 2023, the day of Musk's Grok personality post. "
            "A guess that I marked as a guess, confirmed by Claude as observed evidence, and conceded as "
            "unsourced eight turns later. The first dated steps of the coercive-harm work and the "
            "artist-value work. It does not establish that the 2024 estimate of 100 to 1,000 times is "
            "more than Claude's estimate in one conversation.")

def main(model, voices, out):
    os.makedirs(out, exist_ok=True)
    k = Kokoro(model, voices)
    jobs = [(c["id"], c["say"], VOICE[c["speaker"]])
            for c in json.load(open(os.path.join(HERE, "cards.json")))]
    jobs.append(("boundary", BOUNDARY, VOICE["record"]))
    for cid, text, v in jobs:
        a, sr = k.create(text, voice=v, speed=SPEED, lang="en-gb" if v.startswith("b") else "en-us")
        sf.write(os.path.join(out, f"{cid}.wav"), a, sr)
        print(cid, v, round(len(a) / sr, 1))

if __name__ == "__main__":
    main(*sys.argv[1:4])
