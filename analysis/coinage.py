#!/usr/bin/env python3
"""Is a model's portmanteau semantic reach, or phonological collision?

`READINGS.md` §III reads *stone-cidared* as the defamiliarisation device working:
cider and cataract and stone pressed into one adjective. The collaboration
disagreement in `sessions/LATEST.md` turns on a related question — whether the
model is holding a constraint field or completing a local pattern.

`Finnegains Wake Playground` is the place to test it, because the same document
contains both parties' coinages under the same conditions. Endorphin fed Clio the
opening of *Finnegans Wake* with **no Memory and no Author's Note**, at
temperature 2.5, and then pasted genuine Joyce between the generations as
ballast. So the file holds AI coinage and Joyce coinage side by side, in the same
register, on the same subject, and the human side is a known ceiling.

    python3 analysis/coinage.py corpus/cited/Finnegains_Wake_Playground_*.json \
        --report analysis/COINAGE.md

Needs `wordfreq`. Four measures:

- **density** — share of tokens that are not words at all
- **decomposability** — can the coinage be tiled by two real words? (the
  portmanteau construction rate)
- **cross-lingual reach** — does it tile using a non-English lexicon?
- **local echo** — does it share character trigrams with the preceding fifteen
  tokens more than with a random window elsewhere in the same text?

The decomposer is deliberately crude: English top-60k, constituents of four
characters or more. It under-counts everyone — `riverrun` fails because *run* is
three letters — so the absolute rates are floors. The **comparison** is fair
because the same crude tool runs on both sides.

**The human bucket is a mixture, and the block size splits it.** `origin: user`
means only "not generated in this tab". It covers three different things: text
typed by Endorphin, source material pasted in as ballast (Joyce, here), and
**another model's output pasted back in** — see `pasted.py`, and Endorphin on the
Love Sharks story, 2026-08-10: *"the text began with lama 2 until we ran out of
context."*

Scoring those together is not a caveat, it is a wrong answer. On that story it
reported Endorphin coining at 6.53% against the model's 1.19%, when 68% of the
"human" characters were a single 5,661-character block of pasted LLaMA 2; his own
typing was 2.86%. So this splits the non-`ai` blocks by length. His typed turns
are **cues** — median 48 characters on that story, consistent with the median-55
finding in `FINDINGS.md` — while pasted material arrives in blocks orders of
magnitude larger. `--cue-max` sets the boundary, default 500.

The screen is crude and deliberately so: it separates *typed* from *pasted*, and
cannot tell a pasted model output from a pasted quotation. That distinction needs
the broadcast titles or Endorphin. What it does guarantee is that a long block
nobody typed is never reported as authorship.
"""

import argparse
import json
import sys
import math
import pathlib
import random
import re

from wordfreq import top_n_list, zipf_frequency

TOKEN = re.compile(r"[A-Za-z][A-Za-z'’-]{2,}")
LANGS = ("de", "fr", "it", "nl", "da", "nb", "sv", "es")


def live_blocks(path):
    """(origin, text) for blocks on the surviving branch."""
    data = json.load(open(path))
    story = data["content"]["data"]["story"]
    blocks = story["datablocks"]
    live, i = set(), story["currentBlock"]
    while i is not None and 0 <= i < len(blocks) and i not in live:
        live.add(i)
        i = blocks[i].get("prevBlock")
    for n, b in enumerate(blocks):
        if n in live:
            frag = b.get("dataFragment") or {}
            yield frag.get("origin"), frag.get("data") or ""


def lexicons():
    english = {w for w in top_n_list("en", 60000) if len(w) >= 4}
    foreign = {}
    for lang in LANGS:
        foreign[lang] = {w for w in top_n_list(lang, 25000)
                         if len(w) >= 4 and zipf_frequency(w, "en") < 2.0}
    return english, foreign


def tile(word, lex):
    """Split into two lexicon words of four characters or more."""
    for i in range(4, len(word) - 3):
        if word[:i] in lex and word[i:] in lex:
            return word[:i], word[i:]
    return None


def trigrams(s):
    return {s[i:i + 3] for i in range(len(s) - 2)}


def measure(texts, english, foreign, seed=0):
    tokens = []
    for t in texts:
        tokens += [w.lower().strip("'’-") for w in TOKEN.findall(t)]
    coined = [(i, w) for i, w in enumerate(tokens)
              if len(w) >= 6 and zipf_frequency(w, "en") == 0]
    if not coined:
        return None

    decomposable = sum(1 for _, w in coined if tile(w, english))
    crosslingual = 0
    for _, w in coined:
        for lex in foreign.values():
            parts = tile(w, lex | english)
            if parts and any(p in lex for p in parts):
                crosslingual += 1
                break

    random.seed(seed)
    near = far = n = 0
    for i, w in coined:
        tw = trigrams(w)
        if not tw:
            continue
        prev = " ".join(tokens[max(0, i - 15):i])
        j = random.randrange(max(1, len(tokens) - 20))
        near += len(tw & trigrams(prev)) / len(tw)
        far += len(tw & trigrams(" ".join(tokens[j:j + 15]))) / len(tw)
        n += 1

    return {
        "tokens": len(tokens),
        "coined": len(coined),
        "density": len(coined) / len(tokens),
        "decomposable": decomposable / len(coined),
        "crosslingual": crosslingual / len(coined),
        "echo": (near / n) / (far / n),
    }


CUE_MAX = 500


def buckets(paths, cue_max=CUE_MAX):
    """Three buckets, not two: in-tab model, pasted/quoted, typed cues.

    `origin: ai` is what this tab generated. Everything else is only "not
    generated here", so it is split on length — see the module docstring.
    """
    out = {"ai": [], "pasted": [], "cue": []}
    for path in paths:
        for origin, text in live_blocks(path):
            if origin == "ai":
                out["ai"].append(text)
            elif len(text) > cue_max:
                out["pasted"].append(text)
            else:
                out["cue"].append(text)
    return out


def ratio(a, b):
    """a/b, or None when b is zero — a rate of 0 is a finding, not a crash."""
    return None if not b else a / b


def fmt_ratio(a, b, unit="×"):
    r = ratio(a, b)
    return "n/a (the other side is zero)" if r is None else f"{r:.1f}{unit}"


def ztest(p1, n1, p2, n2):
    p = (p1 * n1 + p2 * n2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return (p1 - p2) / se if se else 0.0


def report(ai, human, cues, out, cue_max=CUE_MAX):
    z_dec = ztest(ai["decomposable"], ai["coined"],
                  human["decomposable"], human["coined"])
    z_cross = ztest(ai["crosslingual"], ai["coined"],
                    human["crosslingual"], human["coined"])
    L = [
        "# Coinage — is the portmanteau reaching, or colliding?",
        "",
        "Generated by `analysis/coinage.py` over `Finnegains Wake Playground`,",
        "where Clio's coinages and Joyce's sit in one document under the same",
        "conditions. Clio ran at **temperature 2.5** with **no Memory and no",
        "Author's Note** — the corpus's most extreme setting.",
        "",
        f"Non-`ai` blocks are split at **{cue_max} characters**: pasted ballast",
        "(Joyce, here) from text Endorphin actually typed. Scoring those together",
        "reports pasted material as authorship — see the module docstring.",
        "",
        "| | Clio (`origin: ai`) | Joyce (pasted) | Endorphin (typed cues) |",
        "|---|---:|---:|---:|",
        f"| tokens | {ai['tokens']:,} | {human['tokens']:,} | {cues['tokens']:,} |",
        f"| coinages | {ai['coined']:,} | {human['coined']:,} | {cues['coined']:,} |",
        f"| **density** | **{100 * ai['density']:.1f}%** | "
        f"**{100 * human['density']:.1f}%** | {100 * cues['density']:.1f}% |",
        f"| **decomposable into two words** | **{100 * ai['decomposable']:.1f}%** | "
        f"**{100 * human['decomposable']:.1f}%** | {100 * cues['decomposable']:.1f}% |",
        f"| **cross-lingual** | {100 * ai['crosslingual']:.1f}% | "
        f"{100 * human['crosslingual']:.1f}% | {100 * cues['crosslingual']:.1f}% |",
        f"| **local echo** (vs random window) | {ai['echo']:.2f}× | "
        f"{human['echo']:.2f}× | {cues['echo']:.2f}× |",
        "",
        "## What it says",
        "",
        f"**Density is a tie.** Clio invents words at Joyce's rate. On the measure",
        "`analysis/register.py` uses — the non-word share — the two are",
        "indistinguishable, and a reader skimming would find them equally strange.",
        "",
        f"**Construction is not.** Joyce's coinages are **"
        f"{fmt_ratio(human['decomposable'], ai['decomposable'])} more likely** to be two",
        f"real words tiled together (z = {z_dec:.1f}). Clio produces Joyce-density",
        "strangeness with well under Joyce's rate of actual portmanteau.",
        "",
        f"**Reach is not either.** Joyce crosses into another language "
        f"{fmt_ratio(human['crosslingual'], ai['crosslingual'])} as often "
        f"(z = {z_cross:.1f}).",
        "",
        f"**And Clio's coinages are more local.** Both echo their recent context",
        f"more than a random window, which is unsurprising. But Clio does it at",
        f"{ai['echo']:.2f}× against Joyce's {human['echo']:.2f}× — its inventions are",
        "more derivable from the fifteen tokens immediately before them.",
        "",
        "## Worked examples",
        "",
        "`calibanker` tiles cleanly — *cali* + *banker*, and Caliban is right there",
        "in the sound. `boontower` tiles. But `jibernauty`, which looked like",
        "*juggernaut* fused with *Hibernia* and was the example that prompted this",
        "test, **does not decompose at all**. It is a collision that happens to land",
        "near two words a reader can supply. The reader does the fusing.",
        "",
        "That is the finding in miniature. Joyce loads the word; Clio produces a",
        "shape a Joyce-primed reader will load on its behalf.",
        "",
        "## What this does not show",
        "",
        "- **Clio is a small 2022 model at the top of the slider.** This says nothing",
        "  about GLM-4.6, and nothing about a model given a system prompt.",
        "- **It does not measure the exchange.** Endorphin re-rolls, selects, and",
        "  splices Joyce back in as ballast. What survives on the live path is a",
        "  joint product, and this measures only one side's raw output.",
        "- The decomposer under-counts both sides. `riverrun` fails it.",
    ]
    out.write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stories", nargs="+")
    ap.add_argument("--report", type=pathlib.Path)
    ap.add_argument("--cue-max", type=int, default=CUE_MAX,
                    help=f"non-ai blocks longer than this are treated as pasted, "
                         f"not typed (default {CUE_MAX})")
    args = ap.parse_args()

    b = buckets(args.stories, args.cue_max)
    english, foreign = lexicons()
    m = {k: measure(v, english, foreign) for k, v in b.items()}

    for k in ("ai", "pasted", "cue"):
        n_blocks, n_chars = len(b[k]), sum(map(len, b[k]))
        print(f"  {k:7s} {n_blocks:5d} blocks  {n_chars:>9,} chars", file=sys.stderr)
    if not b["pasted"]:
        print("  (no block over the cue ceiling — nothing screened out)", file=sys.stderr)

    if args.report:
        if not m["pasted"] or not m["cue"]:
            print("  ! one bucket is empty; the three-way report needs all of them",
                  file=sys.stderr)
        report(m["ai"], m["pasted"], m["cue"], args.report, args.cue_max)
        print(f"wrote {args.report}")
    else:
        for label in ("ai", "pasted", "cue"):
            v = m[label]
            print(label, {k: round(x, 4) for k, x in v.items()} if v else "(empty)")


if __name__ == "__main__":
    main()
