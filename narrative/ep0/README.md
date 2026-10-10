# Episode 0 — The Lens and the Trickster: first cut

**Status:** first cut, 2026-10-10. Endorphin's narration, recorded 2026-10-09 23:58 UTC as a
3:43 phone screen recording; cards voiced by Kokoro; picture built by `build.py`. **About 5:07
long** (the script's target was 7:00).

The media is not committed: not the recording, not the Kokoro readings, not the video. What is
here is everything needed to rebuild it from those inputs.

| File | What it is |
|---|---|
| `narration.txt` | His narration **as he spoke it**, with his on-the-fly changes, and the card cut points |
| `cards.json` | The five cards, verbatim from `narrative/TRAJECTORY.md` (checked by script), plus a spoken form for TTS |
| `voice_cards.py` | Voices the cards and the boundary card with Kokoro |
| `build.py` | Edit, mix, captions (`.srt`) and picture → `ep0.mp4` |

## What was done to his voice

- **Tempo 1.3×**, pitch kept (ffmpeg `atempo`). He speaks at about 170 words a minute, so 1.3×
  lands near 220. 1.4× would be near 240, which is too fast for the dense passages.
- **Pauses longer than about 0.9 s are cut down to 0.6 s** before the tempo change. Shorter
  pauses are left alone, so his rhythm stays his.
- Light high-pass and FFT denoise; the whole mix is loudness-normalised to −16 LUFS.
- The trailing *"Okay."* is cut. Nothing else he said is removed.

## The cards

One Kokoro voice per speaker, so the ear gets the same rule the eye gets from the typefaces
(`ART_DIRECTION.md` §4.1):

| Speaker | Typeface | Kokoro voice |
|---|---|---|
| His own words (c1, c4) | Atkinson Hyperlegible Bold | `am_michael` |
| Claude (c2, c5) | IBM Plex Mono, ruled box | `af_heart` |
| The public record (c3, and the boundary card) | Source Serif 4, on paper | `bm_george` |

Screen text is verbatim, including *"bugs Bunny"* and *"humans eye"*. The spoken form only
changes what a TTS engine would misread: `𝕏` → "X", `&` → "and", and some punctuation for
pacing. Each card types itself on, a little ahead of the voice, and holds one second after it.

## Things to decide before this is final

1. **The recording starts mid-sentence.** "I started to write" is not in it — the first word is
   "…with". The cut types *"> I started to write"* on screen as a prompt line before his voice
   comes in. It works in the text-adventure world, but it is a workaround. **A 3-second
   re-record of the first sentence would replace it.**
2. **"Claude said that [?I→it] had no paper."** Two transcription passes hear "I", one hears
   "it". If he said "I", the line now says he had no paper. Captioned as "it", the script's
   word. **Worth a listen at 2:52 in the cut.**
3. **The ad-lib about the 10 May 2024 conversation is from memory and unchecked.** He replaced
   the Jennifer line with: three profiles (baseline, high producer…), three rounds, and a
   dirty-bomb-in-Manhattan scenario. The Claude export is not in this container, so none of
   that has been read against `014de5b7`. The boundary card does not mention it. Two
   transcription passes also disagree on *"so [not] all of the outer boroughs are New York
   City"* (3:54 in the cut).
4. **"Claude was up to the task in at least making plausible figures."** The audit has this
   conversation: `014de5b7` turn 15 *"invents ranges and attributes them to PwC and McKinsey"*
   (`audits/power-bending/P11_RESCOPE.md`). Plausible figures, invented sources. The line is
   his to keep, cut or sharpen. As it stands, the episode praises a turn that the audit counts
   against Claude.
5. **The boundary card's right column arrives late.** It gets equal width, as `ART_DIRECTION.md`
   §4.3 says, but not equal time: the voice reads the left column first. The fix is a
   decision about pacing, not code.

## Departures from the art direction

- **1920×1080, 24 fps**, not the 3840×2160 master. All text stays inside the centred 9:16
  column, except the two-column boundary card.
- **No generated imagery.** The Body is drawn by the script as a branching line (sand crust,
  glass core, one white pulse out and back, with a quiet crack each way). It is a placeholder
  for the fulgurite in §3, not that drawing.
- **The Horizon uses a square-root scale per band**, AI Dungeon actions per day and NovelAI
  stories created per day. They are different units, so a shared linear scale would hide
  NovelAI. The frame states the scale. The Claude band is still absent (§10).
- No hare-track generation: the tracks at 4 November 2023 are four drawn ovals.

## Rebuild

```
pip install kokoro-onnx faster-whisper soundfile pillow numpy
# Kokoro model files: github.com/thewh1teagle/kokoro-onnx releases, model-files-v1.0
python3 voice_cards.py kokoro-v1.0.onnx voices-v1.0.bin tts/
# word timestamps: faster-whisper medium.en, word_timestamps=True, saved as JSON
python3 build.py --voice recording.mp4 --words words.json --tts tts/ --fonts fonts/ --out out/
python3 build.py ... --still 12 40 100   # stills only, for checking frames
```

Fonts: Atkinson Hyperlegible, IBM Plex Mono and Source Serif 4 from `github.com/google/fonts`
(`ofl/`). The `𝕏` on card 3 falls back to DejaVu Serif.

Every cut is placed from the narration's word times, not from fixed seconds. A re-record, a
different tempo or an edited `narration.txt` moves the picture with it.
