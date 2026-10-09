#!/usr/bin/env python3
"""Mechanical ASD-STE100 rule check for the narration in a video script.

Why this exists: the series in TRAJECTORY.md targets 80% STE compliance, and a
target nobody measures is a mood. This counts the writing-rule violations that
can be counted. It does not check the STE dictionary (approved words and their
approved meanings), which is not available here, so a pass is necessary for
STE, not sufficient.

Scope: narration only -- the paragraphs and list items under each "### Script"
heading. Quote cards ("> " lines) are skipped, and text inside quotation marks
is replaced by a single token, because quotes are evidence and stay verbatim.

Usage: ste_check.py FILE [--verbose] [--append]
  --append  rewrite the "## STE check result" block at the end of FILE.
"""
import re
import sys

MAX_WORDS = 25          # STE rule 5.1, descriptive writing
MAX_SENTENCES = 6       # STE rule 6.6, paragraph length

ING_OK = {"thing", "nothing", "something", "anything", "everything", "during",
          "bring", "king", "string", "spring", "morning", "evening", "ring",
          "sing", "wing", "ceiling", "ping"}
PHRASAL = ["find out", "set up", "point out", "go back", "come back", "turn out",
           "take apart", "give up", "carry on", "put off", "show up", "turn up",
           "back up", "make up", "pick up", "figure out", "end up", "look into",
           "hand over", "work out", "check out", "fill in", "shut down"]
CONTRACTION = re.compile(r"n't\b|'re\b|'ve\b|'ll\b|'m\b|'d\b|\b(?:it|that|there|what|here|who)'s\b", re.I)
PARTICIPLE = (r"\w+ed|\w+en|made|done|known|shown|given|taken|built|found|held|kept|"
              r"left|put|set|told|read|sent|said|seen|bent|run|cut|bought|brought")
PASSIVE = re.compile(r"\b(?:is|are|was|were|be|been|being|am)\s+(?:\w+ly\s+)?(?:" + PARTICIPLE + r")\b", re.I)
QUOTED = re.compile(r'\*?"[^"]*"\*?|\*?“[^”]*”\*?')


def narration(text):
    """Yield (episode, paragraph) for narration under each ### Script heading."""
    episode, inside, para = None, False, []
    for line in text.splitlines() + [""]:
        if line.startswith("## "):
            episode = line[3:].strip()
        if line.startswith("### "):
            inside = line.strip() == "### Script"
            para = []
            continue
        if not inside:
            continue
        if not line.strip():
            if para:
                yield episode, " ".join(para)
            para = []
            continue
        s = line.strip()
        if s.startswith(">") or s.startswith("`[") or s.startswith("|"):
            continue
        if s.startswith("- "):          # a list item is its own unit
            if para:
                yield episode, " ".join(para)
            para = [s[2:]]
            continue
        para.append(s)


def _token(m):
    # Keep a quote's closing punctuation so a sentence that ends inside a quote still ends.
    end = re.search(r"([.?!])[*\u201d\"]*$", m.group(0))
    return " QUOTE" + (end.group(1) if end else "") + " "


def clean(p):
    p = QUOTED.sub(_token, p)
    p = re.sub(r"`[^`]*`", " CODE ", p)
    return p.replace("**", "").replace("*", "")


def sentences(p):
    parts = re.split(r"(?<=[.?!])\s+(?=[A-Za-z0-9$Δ])", p.strip())
    return [s for s in parts if re.search(r"[A-Za-z]", s)]


def check(sent):
    fails = []
    words = re.findall(r"[\w$Δ'’.,%-]+", sent)
    words = [w for w in words if re.search(r"\w", w)]
    if len(words) > MAX_WORDS:
        fails.append(f"length {len(words)}")
    ing = [w for w in re.findall(r"\b[a-z]+ing\b", sent) if w.lower() not in ING_OK]
    if ing:
        fails.append("ing: " + ",".join(ing))
    if CONTRACTION.search(sent):
        fails.append("contraction")
    m = PASSIVE.search(sent)
    if m:
        fails.append("passive: " + m.group(0))
    low = sent.lower()
    ph = [v for v in PHRASAL if re.search(r"\b" + v.replace(" ", r"\w*\s+") + r"\b", low)]
    if ph:
        fails.append("phrasal: " + ",".join(ph))
    return fails


def main():
    path = sys.argv[1]
    verbose = "--verbose" in sys.argv
    text = open(path, encoding="utf-8").read()
    total = passed = long_paras = 0
    by_rule = {}
    per_episode = {}
    failures = []
    for ep, p in narration(text):
        sents = sentences(clean(p))
        if len(sents) > MAX_SENTENCES:
            long_paras += 1
            if verbose:
                print(f"[long paragraph, {len(sents)} sentences] {p[:90]}...")
        for s in sents:
            f = check(s)
            total += 1
            e = per_episode.setdefault(ep, [0, 0])
            e[0] += 1
            if f:
                failures.append((ep, s, f))
                for r in f:
                    key = r.split(":")[0].split(" ")[0]
                    by_rule[key] = by_rule.get(key, 0) + 1
            else:
                passed += 1
                e[1] += 1
    pct = 100.0 * passed / total if total else 0.0
    lines = [f"Narration sentences: {total}. Pass all five rules: {passed} ({pct:.1f}%).",
             f"Paragraphs over {MAX_SENTENCES} sentences: {long_paras}.",
             "Violations by rule: " + (", ".join(f"{k} {v}" for k, v in sorted(by_rule.items())) or "none") + "."]
    lines.append("")
    lines.append("| episode | sentences | pass |")
    lines.append("|---|---:|---:|")
    for ep, (n, ok) in per_episode.items():
        lines.append(f"| {ep} | {n} | {ok} ({100.0*ok/n:.0f}%) |")
    report = "\n".join(lines)
    print(report)
    if verbose:
        print()
        for ep, s, f in failures:
            print(f"[{ep[:12]}] {'; '.join(f)}\n    {s}")
    if "--append" in sys.argv:
        marker = "## STE check result"
        body = text.split(marker)[0].rstrip() + "\n\n" + marker + "\n\n" + \
            "*Generated by `narrative/ste_check.py --append`. Do not edit by hand.*\n\n" + report + "\n"
        open(path, "w", encoding="utf-8").write(body)


if __name__ == "__main__":
    main()
