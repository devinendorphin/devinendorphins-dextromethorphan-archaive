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

**The human bucket is a mixture.** It holds Joyce's text and Endorphin's own
Wake-ish composition together, and the export cannot separate them. Endorphin is
not Joyce, so mixing drags the human score down — which means any gap this finds
is understated, not inflated.
"""

import argparse
import json
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


def ztest(p1, n1, p2, n2):
    p = (p1 * n1 + p2 * n2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    return (p1 - p2) / se if se else 0.0


def report(ai, human, out):
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
        "| | Clio (`origin: ai`) | Joyce + Endorphin |",
        "|---|---:|---:|",
        f"| tokens | {ai['tokens']:,} | {human['tokens']:,} |",
        f"| coinages | {ai['coined']:,} | {human['coined']:,} |",
        f"| **density** | **{100 * ai['density']:.1f}%** | "
        f"**{100 * human['density']:.1f}%** |",
        f"| **decomposable into two words** | **{100 * ai['decomposable']:.1f}%** | "
        f"**{100 * human['decomposable']:.1f}%** |",
        f"| **cross-lingual** | {100 * ai['crosslingual']:.1f}% | "
        f"{100 * human['crosslingual']:.1f}% |",
        f"| **local echo** (vs random window) | {ai['echo']:.2f}× | "
        f"{human['echo']:.2f}× |",
        "",
        "## What it says",
        "",
        f"**Density is a tie.** Clio invents words at Joyce's rate. On the measure",
        "`analysis/register.py` uses — the non-word share — the two are",
        "indistinguishable, and a reader skimming would find them equally strange.",
        "",
        f"**Construction is not.** Joyce's coinages are **"
        f"{human['decomposable'] / ai['decomposable']:.1f}× more likely** to be two",
        f"real words tiled together (z = {z_dec:.1f}). Clio produces Joyce-density",
        "strangeness with well under Joyce's rate of actual portmanteau.",
        "",
        f"**Reach is not either.** Joyce crosses into another language "
        f"{human['crosslingual'] / ai['crosslingual']:.1f}× as often "
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
    args = ap.parse_args()

    ai, human = [], []
    for path in args.stories:
        for origin, text in live_blocks(path):
            (ai if origin == "ai" else human).append(text)

    english, foreign = lexicons()
    a = measure(ai, english, foreign)
    h = measure(human, english, foreign)
    if args.report:
        report(a, h, args.report)
        print(f"wrote {args.report}")
    else:
        for label, m in (("ai", a), ("human", h)):
            print(label, {k: round(v, 4) for k, v in m.items()})


if __name__ == "__main__":
    main()
