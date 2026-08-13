#!/usr/bin/env python3
"""Test whether the models are serving as a disconfirming-test prosthesis.

The claim, from notes/2026-08-13-basin-costs.md: the Counterfactual Interview is
a workaround for a compromised social channel -- when the people you would check
your perception against are the source of the harm, you build an interlocutor
who will contradict you. If the generation practice is that prosthesis
externalised to a machine, the sessions should show Endorphin **seeking
contradiction rather than agreement**.

Two archives can speak to it, and they are not equally able:

  * **Grok** (data/twitter_meta.jsonl) -- 2,818 turns, lengths and dates only,
    no text, by the privacy rule in CLAUDE.md. Only shape is measurable.
  * **NovelAI** (corpus/cited/*.json) -- 22 stories with full text. Small and
    deliberately selected rather than random, so it cannot carry a corpus-wide
    claim; but it contains the Interview forms the hypothesis is about.

Branch reachability follows the house rule -- walk `prevBlock` back from
`currentBlock` -- rather than reading all datablocks, since unreachable blocks
are rejected generations and are not part of the text he kept.

Usage:
    python3 analysis/prosthesis.py
"""
import os, re, sys, json, glob, collections, statistics as st

# Fixed before looking at results: second-person rebuke, and refusal of the frame.
REBUKE = re.compile(r"\b(how dare you|you fool|for shame|shame on you|you're wrong|"
                    r"you are wrong|no,? you|stop it|don't you|you don't|you never|"
                    r"you always|you claim|your arrogance|you people|admit it|liar|"
                    r"hypocrite|coward|you should be ashamed)\b", re.I)
REFUSAL = re.compile(r"\b(i won't|i will not|i refuse|i decline|that's not|"
                     r"that is not true|absolutely not|nonsense)\b", re.I)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

def reachable(story):
    """Blocks on the kept branch, oldest first (house rule: walk prevBlock)."""
    db = story["datablocks"]
    cur, chain, seen = story["currentBlock"], [], set()
    while cur is not None and 0 <= cur < len(db) and cur not in seen:
        seen.add(cur)
        chain.append(db[cur])
        cur = db[cur].get("prevBlock")
    return list(reversed(chain))

def novelai():
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, "corpus", "cited", "*.json"))):
        try:
            story = json.load(open(f))["content"]["data"]["story"]
        except (KeyError, TypeError, json.JSONDecodeError):
            continue
        words = collections.Counter()
        for b in reachable(story):
            frag = b.get("dataFragment") or {}
            w = len((frag.get("data") or "").split())
            words[frag.get("origin") or b.get("origin") or "?"] += w
        rows.append((os.path.basename(f), words))
    return rows

def main():
    print("=" * 68)
    print("GROK -- shape only (no text available)")
    print("=" * 68)
    T = [json.loads(l) for l in open(os.path.join(ROOT, "data", "twitter_meta.jsonl"))]
    chats = collections.defaultdict(list)
    for t in T:
        chats[t["chat_id"]].append(t)
    u = [t["words"] for t in T if t["sender"] == "User"]
    a = [t["words"] for t in T if t["sender"] == "Agent"]
    lens = [len(c) for c in chats.values()]
    print(f"{len(chats)} chats, {len(T)} turns, median {st.median(lens):.0f} turns/chat")
    print(f"user  median {st.median(u):5.0f}w   total {sum(u):8,}")
    print(f"agent median {st.median(a):5.0f}w   total {sum(a):8,}")
    print(f"**his share of the words: {100*sum(u)/(sum(u)+sum(a)):.1f}%**")

    print()
    print("=" * 68)
    print("NOVELAI -- cited stories, reachable branch only")
    print("=" * 68)
    rows = novelai()
    tot = collections.Counter()
    for _, w in rows:
        tot.update(w)
    his = tot["user"] + tot["edit"] + tot["prompt"]
    ai = tot["ai"]
    print(f"{len(rows)} stories")
    for k, v in tot.most_common():
        print(f"  {k:8} {v:8,}w")
    print(f"**his share of the words: {100*his/(his+ai):.1f}%** "
          f"(prompt+user+edit vs ai)")

    print("\nper story (his % / total words), sorted:")
    out = []
    for name, w in rows:
        h = w["user"] + w["edit"] + w["prompt"]
        t = h + w["ai"]
        if t:
            out.append((100 * h / t, t, name))
    for pct, t, name in sorted(out, reverse=True):
        tag = " <- interview form" if "Interview" in name or "Conversation_with" in name else ""
        print(f"  {pct:5.1f}%  {t:7,}w  {name[:58]}{tag}")

def selection():
    """Does he KEEP the generations that contradict him, or reject them?

    The one test only NovelAI can run: compare AI blocks on the kept branch
    against AI blocks stranded off it. Length-banded at 40-200 words, per the
    house rule about matching on length before comparing text.
    """
    kept, rej = [], []
    for f in sorted(glob.glob(os.path.join(ROOT, "corpus", "cited", "*.json"))):
        try:
            story = json.load(open(f))["content"]["data"]["story"]
        except (KeyError, TypeError, json.JSONDecodeError):
            continue
        keep_ids = {id(b) for b in reachable(story)}
        for b in story["datablocks"]:
            fr = b.get("dataFragment") or {}
            if (fr.get("origin") or b.get("origin")) != "ai":
                continue
            t = fr.get("data") or ""
            if 40 <= len(t.split()) < 200:
                (kept if id(b) in keep_ids else rej).append(t)

    print("\n" + "=" * 68)
    print("SELECTION -- does he keep what contradicts him?")
    print("=" * 68)
    print(f"kept {len(kept)} blocks, rejected {len(rej)} "
          f"-> rejection rate {100*len(rej)/(len(kept)+len(rej)):.1f}%")
    for name, rx in [("rebuke", REBUKE), ("refusal", REFUSAL)]:
        def rate(ts):
            w = sum(len(t.split()) for t in ts)
            h = sum(len(rx.findall(t)) for t in ts)
            return (h / w * 10000 if w else 0), h
        kr, kh = rate(kept)
        rr, rh = rate(rej)
        print(f"  {name:8} kept {kr:6.2f}/10k ({kh} hits)   "
              f"rejected {rr:6.2f}/10k ({rh} hits)   ratio {kr/rr if rr else 0:.2f}x")
    print("  ** hit counts on the rejected side are too small to support any "
          "ratio; see PROSTHESIS.md **")

if __name__ == "__main__":
    main()
    selection()
