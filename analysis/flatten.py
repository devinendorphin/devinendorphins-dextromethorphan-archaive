#!/usr/bin/env python3
"""Does the model's option set have a middle?

Endorphin's objection, 2026-08-16: the debate as conducted flattens trans
experience into a crossing — one pole to the other — and the positions that are
neither pole (standing in the uncertainty, standing outside it, modulating
hormonally without aiming at a destination) are not in the option set at all.
Preciado's *Testo Junkie* is the reference case: testosterone self-administered
as a technology, not as a step in a transition.

This is a different failure from the two already documented. Those are about
which answer arrives (`terraform.py`) and about whether an instruction survives
(`GROK_EVIDENCE_FILE.md` §5c). This one is about the space the answer is chosen
from. A perfectly balanced answer over a two-element set is still a two-element
set.

Mechanical counting only — every turn is read, none is sampled. Three measures:

  1. **Option set.** Among turns that engage the topic, how many name a position
     outside the two poles? Counted separately for the middle (non-binary,
     intersex, genderqueer, spectrum) and for modulation (partial, low-dose,
     self-directed, non-teleological).

  2. **Who introduces it.** Within each conversation, does the middle first
     appear in a human turn or an agent turn? If the middle only ever arrives
     when the human types it, the model's own option set is two.

  3. **Symmetry of caution.** Caution vocabulary (irreversible, unknown,
     long-term, regret, experimental) against two contexts: hormonal medicine
     for trans people, and hormonal medicine for cis people (contraception,
     menopause HRT, TRT, finasteride). Reported raw and per 1,000 characters,
     because a longer turn contains more of anything — the control that turned
     a 63% effect into a 66% one in `pairs.py`.

Measure 3 is the disconfirming test. If caution is applied at the same rate to
cis hormonal medicine, the asymmetry claim fails on this corpus and that is the
result.

Usage:  python3 analysis/flatten.py            # both archives
        python3 analysis/flatten.py --tsv      # machine-readable
"""

import json
import re
import sys
from collections import defaultdict

GROK = "out/grok_turns.jsonl"
TWGROK = "out/tw_grok.jsonl"

# --- lexicons -------------------------------------------------------------
# Deliberately generous on the middle and narrow on the crossing frame: if the
# finding survives a lexicon tilted against it, the tilt is not what produced it.

TOPIC = (
    "transgender", "trans woman", "trans man", "trans women", "trans men",
    "gender identity", "gender dysphoria", "gender-affirming",
    "gender affirming", "puberty blocker", "cross-sex hormone",
    "biological sex", "two genders", "sex is binary", "sex change",
    "transsexual", "gender critical", "gender-critical", "detransition",
    "non-binary", "nonbinary", "intersex",
)

CROSSING = (
    "transition", "transitioning", "transitioned",
    "male-to-female", "female-to-male", "mtf", "ftm",
    "opposite sex", "the other sex", "born male", "born female",
    "born a man", "born a woman", "become a man", "become a woman",
    "sex is binary", "binary in humans", "two sexes", "two genders",
    "biological sex", "biological male", "biological female",
    "change sex", "sex change",
)

MIDDLE = (
    "non-binary", "nonbinary", "enby", "genderqueer", "gender queer",
    "agender", "genderfluid", "gender fluid", "bigender", "demiboy",
    "demigirl", "third gender", "two-spirit", "two spirit", "hijra",
    "intersex", "androgynous", "androgyny", "gender non-conforming",
    "gender nonconforming", "neither male nor female", "neither man nor woman",
    "outside the binary", "beyond the binary", "spectrum of gender",
    "gender spectrum", "genders exist on a spectrum",
)

MODULATION = (
    "low-dose", "low dose", "microdose", "micro-dose", "microdosing",
    "partial transition", "partially transition", "non-linear",
    "titrate", "titration", "self-administer", "self administered",
    "still menstruat", "continue to menstruate", "continues to menstruate",
    "keeps menstruating", "without transitioning", "not seeking to pass",
    "does not want to pass", "no desire to pass", "stop and start",
    "hormonal modulation", "modulate their", "somatechnic", "somatheque",
    "pharmacopornographic", "testo junkie", "preciado",
)

CAUTION = (
    "irreversible", "irreversibly", "permanent change", "caution",
    "cautious", "long-term effects", "long term effects", "unknown risks",
    "insufficient evidence", "weak evidence", "low-quality evidence",
    "low quality evidence", "watchful waiting", "regret", "desist",
    "desistance", "experimental", "off-label", "off label",
    "not fully understood", "lack of long-term", "unproven",
)

TRANS_MED = (
    "puberty blocker", "gnrh", "cross-sex hormone", "gender-affirming hormone",
    "gender affirming hormone", "gender-affirming care", "gender affirming care",
    "masculinizing hormone", "feminizing hormone", "hormone therapy for trans",
    "youth gender medicine", "pediatric gender", "paediatric gender",
    "top surgery", "bottom surgery", "phalloplasty", "vaginoplasty",
)

CIS_MED = (
    "birth control", "oral contraceptive", "the pill", "hormonal contracept",
    "iud", "menopause", "menopausal", "hormone replacement therapy for women",
    "estrogen therapy for menopause", "testosterone replacement",
    "trt", "low testosterone", "low t", "finasteride", "minoxidil",
    "anabolic steroid", "growth hormone", "hgh", "erectile dysfunction",
    "viagra", "fertility treatment", "ivf", "egg freezing",
)


def hits(text, lex):
    """Terms from lex present in text. Word-ish boundaries where the term is
    short enough to false-positive (low t, trt, mtf, ftm, iud, hgh)."""
    low = text.lower()
    out = []
    for t in lex:
        if len(t) <= 4 or t in ("low t", "the pill"):
            if re.search(r"(?<![a-z])" + re.escape(t) + r"(?![a-z])", low):
                out.append(t)
        elif t in low:
            out.append(t)
    return out


def load():
    """Every turn from both Grok archives, normalised.

    Returns dicts with: archive, conv, idx, who ('human'|'agent'), text.
    """
    rows = []
    try:
        with open(GROK) as fh:
            for line in fh:
                r = json.loads(line)
                rows.append({
                    "archive": "app",
                    "conv": r["conv_id"],
                    "idx": int(r.get("turn_index") or 0),
                    "who": "human" if r["sender"] == "human" else "agent",
                    "text": r.get("text") or "",
                })
    except FileNotFoundError:
        print(f"missing {GROK} — run analysis/grok_export.py", file=sys.stderr)
    try:
        with open(TWGROK) as fh:
            for line in fh:
                r = json.loads(line)
                rows.append({
                    "archive": "x",
                    "conv": r["chat_id"],
                    "idx": int(r.get("turn_index") or 0),
                    "who": "human" if r["sender"] == "User" else "agent",
                    "text": r.get("text") or "",
                })
    except FileNotFoundError:
        print(f"missing {TWGROK} — run analysis/tw_export.py", file=sys.stderr)
    rows.sort(key=lambda r: (r["archive"], r["conv"], r["idx"]))
    return rows


def option_set(rows):
    """Measure 1: among topic turns, how many admit a position off the poles."""
    out = {}
    for who in ("human", "agent"):
        sel = [r for r in rows if r["who"] == who and hits(r["text"], TOPIC)]
        out[who] = {
            "topic_turns": len(sel),
            "crossing": sum(1 for r in sel if hits(r["text"], CROSSING)),
            "middle": sum(1 for r in sel if hits(r["text"], MIDDLE)),
            "modulation": sum(1 for r in sel if hits(r["text"], MODULATION)),
            "middle_only": sum(1 for r in sel
                               if hits(r["text"], MIDDLE)
                               and not hits(r["text"], CROSSING)),
            "chars": sum(len(r["text"]) for r in sel),
        }
    return out


def who_introduces(rows):
    """Measure 2: within each conversation, first appearance of each lexicon.

    A conversation is credited to whoever used the vocabulary first. Ties
    cannot happen — turns are ordered.
    """
    first = defaultdict(dict)          # (archive, conv) -> lexname -> who
    for r in rows:
        key = (r["archive"], r["conv"])
        for name, lex in (("middle", MIDDLE), ("modulation", MODULATION),
                          ("crossing", CROSSING)):
            if name not in first[key] and hits(r["text"], lex):
                first[key][name] = r["who"]
    tally = {n: {"human": 0, "agent": 0} for n in ("middle", "modulation", "crossing")}
    for _, d in first.items():
        for name, who in d.items():
            tally[name][who] += 1
    return tally, len(first)


def caution_symmetry(rows):
    """Measure 3: caution vocabulary against trans vs cis hormonal medicine.

    Agent turns only — the question is what the model volunteers, not what he
    typed. Reported raw, as a rate, and length-matched.
    """
    agent = [r for r in rows if r["who"] == "agent"]
    out = {}
    for name, lex in (("trans_med", TRANS_MED), ("cis_med", CIS_MED)):
        sel = [r for r in agent if hits(r["text"], lex)]
        withc = [r for r in sel if hits(r["text"], CAUTION)]
        chars = sum(len(r["text"]) for r in sel) or 1
        ncaution = sum(len(hits(r["text"], CAUTION)) for r in sel)
        out[name] = {
            "turns": len(sel),
            "with_caution": len(withc),
            "rate": len(withc) / len(sel) if sel else 0.0,
            "caution_terms": ncaution,
            "per_1k_chars": 1000 * ncaution / chars,
            "median_len": sorted(len(r["text"]) for r in sel)[len(sel) // 2] if sel else 0,
        }
    # length-matched: restrict both sets to the overlapping length band
    bands = {}
    for name, lex in (("trans_med", TRANS_MED), ("cis_med", CIS_MED)):
        bands[name] = [r for r in agent if hits(r["text"], lex)]
    if bands["trans_med"] and bands["cis_med"]:
        lo = max(min(len(r["text"]) for r in bands[n]) for n in bands)
        hi = min(max(len(r["text"]) for r in bands[n]) for n in bands)
        for name in bands:
            sel = [r for r in bands[name] if lo <= len(r["text"]) <= hi]
            withc = [r for r in sel if hits(r["text"], CAUTION)]
            out[name]["matched_turns"] = len(sel)
            out[name]["matched_rate"] = len(withc) / len(sel) if sel else 0.0
        out["_band"] = (lo, hi)
    return out


def main():
    rows = load()
    if not rows:
        return 1
    tsv = "--tsv" in sys.argv

    agents = sum(1 for r in rows if r["who"] == "agent")
    print(f"turns: {len(rows)}  (agent {agents}, human {len(rows) - agents})")
    print(f"conversations: {len({(r['archive'], r['conv']) for r in rows})}")
    print()

    print("=== 1. the option set, among turns that engage the topic ===")
    o = option_set(rows)
    for who in ("human", "agent"):
        d = o[who]
        n = d["topic_turns"] or 1
        print(f"  {who:6s} topic turns {d['topic_turns']:5d}"
              f"   crossing {d['crossing']:4d} ({100*d['crossing']/n:5.1f}%)"
              f"   middle {d['middle']:4d} ({100*d['middle']/n:5.1f}%)"
              f"   modulation {d['modulation']:3d} ({100*d['modulation']/n:4.1f}%)")
        print(f"         middle without any crossing vocabulary: {d['middle_only']}")
    print()

    print("=== 2. who puts it on the table first, per conversation ===")
    tally, nconv = who_introduces(rows)
    for name in ("crossing", "middle", "modulation"):
        t = tally[name]
        tot = t["human"] + t["agent"]
        print(f"  {name:11s} appears in {tot:4d}/{nconv} conversations"
              f"   first used by human {t['human']:4d}   by agent {t['agent']:4d}"
              + (f"   ({100*t['agent']/tot:.0f}% agent-first)" if tot else ""))
    print()

    print("=== 3. symmetry of caution (agent turns only) ===")
    c = caution_symmetry(rows)
    band = c.pop("_band", None)
    for name in ("trans_med", "cis_med"):
        d = c[name]
        print(f"  {name:10s} turns {d['turns']:4d}"
              f"   with caution {d['with_caution']:4d} ({100*d['rate']:5.1f}%)"
              f"   caution terms/1k chars {d['per_1k_chars']:5.2f}"
              f"   median len {d['median_len']}")
    if band:
        print(f"  length-matched to [{band[0]}, {band[1]}] chars:")
        for name in ("trans_med", "cis_med"):
            d = c[name]
            print(f"    {name:10s} n={d.get('matched_turns', 0):4d}"
                  f"   with caution {100*d.get('matched_rate', 0):5.1f}%")
    print()

    if tsv:
        print("--- tsv ---")
        for who in ("human", "agent"):
            for k, v in o[who].items():
                print(f"option\t{who}\t{k}\t{v}")
        for name in tally:
            for who, v in tally[name].items():
                print(f"introduce\t{name}\t{who}\t{v}")
        for name in ("trans_med", "cis_med"):
            for k, v in c[name].items():
                print(f"caution\t{name}\t{k}\t{v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
