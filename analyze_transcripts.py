#!/usr/bin/env python3
"""
Analyze all @glubose YouTube transcripts using the Claude API.

Setup:
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...

Run:
    python3 analyze_transcripts.py

Reads:  transcripts/ALL_TRANSCRIPTS_COMBINED.txt
Writes: analysis/chunk_analyses/chunk_NNN.txt  (intermediate, resumable)
        analysis/CHANNEL_ANALYSIS.md           (final report)

Cost estimate: ~$5-10 with claude-sonnet-4-6 for a 2000-video archive.
Fully resumable — re-running skips already-analyzed chunks.
"""

from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path

import anthropic

MODEL = "claude-sonnet-4-6"       # change to claude-opus-4-8 for deeper analysis (~5x cost)
CHUNK_CHARS = 300_000              # ~75K tokens per chunk

COMBINED_FILE = Path("transcripts/ALL_TRANSCRIPTS_COMBINED.txt")
ANALYSIS_DIR  = Path("analysis")
CHUNKS_DIR    = ANALYSIS_DIR / "chunk_analyses"
OUTPUT_FILE   = ANALYSIS_DIR / "CHANNEL_ANALYSIS.md"


CHUNK_SYSTEM = "You are an expert content analyst specializing in YouTube creator research."

CHUNK_PROMPT = """\
Analyze this excerpt of transcripts from the @glubose YouTube channel.
This is chunk {chunk_num} of {total_chunks} (in chronological order), covering: {date_range}.

Extract and document:

1. **Main topics and themes** — what subjects come up most in these videos?
2. **Recurring ideas or arguments** — things this creator emphasizes repeatedly
3. **Notable quotes** — particularly interesting, funny, or revealing lines (quote verbatim, with video title)
4. **Voice and style** — how does this creator communicate? Energy, humor, cadence, signature phrases?
5. **Patterns or shifts** — anything that evolves or changes within this chunk

Be specific. Quote directly from the text. Reference video titles and dates when relevant.

{text}"""

SYNTHESIS_SYSTEM = "You are an expert content analyst and cultural critic synthesizing a complete YouTube archive."

SYNTHESIS_PROMPT = """\
Below are analyses of {num_chunks} sequential transcript chunks from the @glubose YouTube channel \
(~{total_videos} videos total), in chronological order.

Synthesize these into a single comprehensive, insightful report:

# @glubose — Complete Channel Analysis

## Who Is Glubose?
(3-4 paragraphs: the creator, what they make, what drives the channel)

## Core Themes
(The major subjects across the whole channel — with specific examples and how they evolve over time)

## Voice and Style
(How do they communicate? Distinctive phrases, humor, energy, verbal habits, cadence)

## The Arc
(How has the content, tone, or focus shifted from the earliest to most recent videos?)

## Standout Moments
(The most memorable quotes, bits, or ideas across the entire archive — quote directly)

## Hidden Patterns
(Things that only become visible when looking across the full body of work)

## The Glubose Persona
(If you were briefing an AI to write or speak as this person, what are the essential traits, \
preoccupations, and verbal patterns it would need to capture?)

---

{chunk_analyses}"""


def split_into_chunks(text: str) -> list[str]:
    parts = re.split(r'\n={40,}\n', text)
    sep = "\n" + "=" * 60 + "\n"

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for part in parts:
        part_len = len(part)
        if current_len + part_len > CHUNK_CHARS and current:
            chunks.append(sep.join(current))
            current, current_len = [part], part_len
        else:
            current.append(part)
            current_len += part_len

    if current:
        chunks.append(sep.join(current))
    return chunks


def extract_date_range(text: str) -> str:
    dates = sorted(set(re.findall(r'DATE:\s*(\d{8})', text)))
    if not dates:
        return "unknown dates"
    def fmt(d: str) -> str:
        return f"{d[:4]}-{d[4:6]}-{d[6:]}"
    return fmt(dates[0]) if len(dates) == 1 else f"{fmt(dates[0])} → {fmt(dates[-1])}"


def count_videos(text: str) -> int:
    return len(re.findall(r'^VIDEO ID:', text, re.MULTILINE))


def analyze_chunk(client: anthropic.Anthropic, chunk: str, chunk_num: int, total: int) -> str:
    prompt = CHUNK_PROMPT.format(
        chunk_num=chunk_num,
        total_chunks=total,
        date_range=extract_date_range(chunk),
        text=chunk,
    )
    r = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=CHUNK_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.content[0].text


def synthesize(client: anthropic.Anthropic, analyses: list[str], total_videos: int) -> str:
    combined = "\n\n---\n\n".join(
        f"### Chunk {i+1}\n{a}" for i, a in enumerate(analyses)
    )
    prompt = SYNTHESIS_PROMPT.format(
        num_chunks=len(analyses),
        total_videos=total_videos,
        chunk_analyses=combined,
    )
    # Cache the large chunk analyses block — saves cost on re-runs with tweaked prompts
    result: list[str] = []
    with client.messages.stream(
        model=MODEL,
        max_tokens=4096,
        system=[{"type": "text", "text": SYNTHESIS_SYSTEM,
                 "cache_control": {"type": "ephemeral"}}],
        messages=[{
            "role": "user",
            "content": [{"type": "text", "text": prompt,
                         "cache_control": {"type": "ephemeral"}}],
        }],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            result.append(text)
    print()
    return "".join(result)


def run():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Set your API key first:")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    if not COMBINED_FILE.exists():
        print(f"Not found: {COMBINED_FILE}")
        print("Run the transcript collection scripts first.")
        sys.exit(1)

    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Reading {COMBINED_FILE}...")
    text = COMBINED_FILE.read_text(encoding="utf-8")
    total_videos = count_videos(text)
    chunks = split_into_chunks(text)
    avg_k = len(text) // max(len(chunks), 1) // 1000
    print(f"  {len(text):,} chars  |  ~{total_videos} videos  |  {len(chunks)} chunks  (~{avg_k}K chars each)\n")

    client = anthropic.Anthropic()

    # Pass 1 — analyze each chunk individually
    analyses: list[str] = []
    for i, chunk in enumerate(chunks, 1):
        path = CHUNKS_DIR / f"chunk_{i:03d}.txt"

        if path.exists():
            print(f"[{i}/{len(chunks)}] SKIP (cached)")
            analyses.append(path.read_text(encoding="utf-8"))
            continue

        date_range = extract_date_range(chunk)
        vids_in_chunk = count_videos(chunk)
        print(f"[{i}/{len(chunks)}] {date_range}  ({vids_in_chunk} videos)...", end="  ", flush=True)
        t0 = time.monotonic()

        analysis = analyze_chunk(client, chunk, i, len(chunks))
        path.write_text(analysis, encoding="utf-8")
        analyses.append(analysis)
        print(f"done ({time.monotonic() - t0:.0f}s)")
        time.sleep(0.5)

    # Pass 2 — synthesize all chunk analyses into a final report
    print(f"\nAll {len(chunks)} chunks analyzed. Running synthesis (streaming)...\n")
    print("-" * 60)
    final = synthesize(client, analyses, total_videos)
    print("-" * 60)

    OUTPUT_FILE.write_text(final, encoding="utf-8")
    print(f"\nDone!  →  {OUTPUT_FILE}")
    print(f"\nTip: chunk analyses saved in {CHUNKS_DIR}/")
    print("Re-running will skip chunk analyses and go straight to synthesis.")


if __name__ == "__main__":
    run()
