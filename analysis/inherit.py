#!/usr/bin/env python3
"""What crosses a lineage boundary: inheritance measured at the passage.

`FINDINGS.md` §13e is the hole this fills. The lineage partition in
`families.py` is a *whole-document* overlap, so it found 9 cross-lineage
transplants and reported near-silence — while §13d showed the Random Conspiracy
Generator being pasted around the corpus one paragraph at a time. A sentence
carried from a 2023 story into a 2026 one moves the Jaccard of two large
documents by nothing. The measure contradicted the finding, and the finding was
right.

So: an inverted index over every k-word span in the corpus, keyed to the
*lineages* it appears in (lineage = `created_at` to the exact second, which
§13a establishes as a 99.6%-pure ancestry key). Spans occurring in two or more
lineages are material that moved sideways rather than being inherited by
duplication. Contiguous cross-lineage spans are merged back into passages.

Three populations come out, and they are not the same thing:

  * spans occurring in **human** blocks only — scaffolds, incantations, cues the
    author carried forward by hand, plus anything pasted in from outside the
    corpus, which this cannot distinguish and does not try to;
  * spans occurring in **model** blocks only — formulae the models reproduce
    across unrelated documents, which is a boilerplate and degeneration measure
    rather than an inheritance one;
  * spans occurring in both, which is the interesting column: text the model
    produced once and the author then carried somewhere else, or the reverse.

Authorship is counted **per span**, never per merged passage — see `pass2`. Two
further limits worth stating up front: Memory and Author's Note are not
datablocks, so a scaffold that lived in Memory is invisible here and would
surface as model-only recurrence if the model echoed it; and pasted external
material carries `origin: user`, so the human column mixes the author's own
carried text with Wikipedia, obituaries and circulating prompts.

    python3 analysis/inherit.py corpus/json --report analysis/INHERIT.md \\
        --out data/INHERIT.tsv

Two passes over ~1 GB, a few minutes, ~1.5 GB of RAM at k=8.
"""

import argparse
import collections
import datetime
import hashlib
import json
import pathlib
import re
import sys

import numpy as np

K = 8                 # words per span
MIN_PASSAGE = 12      # words; shorter merged runs are dropped as coincidence
WORD = re.compile(r"\S+")

# The corpus is public by the author's decision, but the JSON exports are
# gitignored -- so anything quoted into a committed markdown file is newly
# exposed. Pasted interface chrome carries his account email through into the
# reports. Mask it on the way out.
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(
    r"\b(?:\+?1[ .-]?)?\(?[0-9]{3}\)?[ .-][0-9A-Za-z]{3}[ .-][0-9]{4}\b"
)


def redact(text):
    """Mask contact details on the way into a committed file.

    The corpus is public by the author's decision, but the JSON exports are
    gitignored, so anything quoted into a committed markdown file is *newly*
    exposed — and `sessions/LATEST.md` names the markdown as the ingestion
    vector. Pasted interface chrome carried his account email into these
    reports, and a model-generated scam-call pastiche carried a phone number.
    Neither is a finding; both are collateral.
    """
    return PHONE.sub("[number redacted]", EMAIL.sub("[email redacted]", text))


def norm(text):
    return WORD.findall(text.lower())


def hashes(tokens, k=K):
    """uint64 hash of every k-word span, in order."""
    out = np.empty(max(0, len(tokens) - k + 1), dtype=np.uint64)
    for i in range(len(out)):
        out[i] = int.from_bytes(
            hashlib.blake2b(
                " ".join(tokens[i : i + k]).encode("utf-8", "replace"),
                digest_size=8,
            ).digest(),
            "big",
        )
    return out


def story_stream(path):
    """(tokens, origin) for each block, in file order."""
    try:
        doc = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:  # noqa: BLE001 -- one file is truncated in Drive itself
        return None, None, None
    smeta = (doc.get("story") or {}).get("data") or {}
    story = ((doc.get("content") or {}).get("data") or {}).get("story") or {}
    ts = smeta.get("createdAt")
    lineage = int(ts / 1000) if ts and ts > 1e12 else (int(ts) if ts else None)
    blocks = []
    for b in story.get("datablocks") or []:
        text = ((b.get("dataFragment") or {}).get("data")) or ""
        if text.strip():
            blocks.append((text, b.get("origin") or "unknown"))
    return lineage, smeta, blocks


HUMAN = {"root", "prompt", "user", "edit"}


def pass1(files):
    """Every span hash in the corpus, tagged with its story index."""
    all_h, all_s, meta = [], [], []
    for si, p in enumerate(files):
        lineage, smeta, blocks = story_stream(p)
        if blocks is None:
            meta.append(None)
            continue
        meta.append(
            {
                "file": p.name,
                "lineage": lineage,
                "title": smeta.get("title") or "",
                "remote_id": smeta.get("remoteId"),
                "last": (smeta.get("lastUpdatedAt")),
            }
        )
        toks = []
        for text, _ in blocks:
            toks.extend(norm(text))
        h = hashes(toks)
        if h.size:
            all_h.append(h)
            all_s.append(np.full(h.size, si, dtype=np.uint32))
    return (
        np.concatenate(all_h) if all_h else np.empty(0, dtype=np.uint64),
        np.concatenate(all_s) if all_s else np.empty(0, dtype=np.uint32),
        meta,
    )


def crossing(h, s, meta):
    """Hashes occurring in two or more distinct lineages. Returned sorted.

    Vectorised throughout: at ~90M spans a per-hash Python loop does not
    finish. Sort on (hash, lineage), drop duplicate pairs, then any hash still
    appearing twice is a hash seen in two lineages.
    """
    lut = np.array(
        [(m["lineage"] if m and m["lineage"] else 0) for m in meta], dtype=np.int64
    )
    lin = lut[s]
    order = np.lexsort((lin, h))
    h, lin = h[order], lin[order]
    del order

    new = np.empty(h.size, dtype=bool)
    new[0] = True
    np.logical_or(h[1:] != h[:-1], lin[1:] != lin[:-1], out=new[1:])
    hu = h[new]
    del h, lin, new

    dup = np.empty(hu.size, dtype=bool)
    dup[:-1] = hu[:-1] == hu[1:]
    dup[-1] = False
    return np.unique(hu[dup])


def pass2(files, meta, cross):
    """Rebuild contiguous cross-lineage spans into passages.

    Authorship is tallied **per span**, not per merged passage. The merged text
    of one passage differs between the contexts it appears in — a run extends as
    far as the surrounding text also happens to cross — so keying the tally on
    the merged string splits one passage into several records and can report a
    passage as model-only in the record built from its model-block occurrences
    while a second record holds its human-block ones. That is how the first run
    of this script classified the PFCizer pitch as model-only when it occurs 11
    times in `user` blocks and 12 in `ai` blocks. Span hashes are identical
    wherever the passage appears, so they carry the tally; merged text is for
    reading, and takes its class from the union of its spans.
    """
    span_origin = collections.defaultdict(set)
    span_lineage = collections.defaultdict(set)
    found = collections.defaultdict(
        lambda: {"lineages": set(), "stories": set(), "origins": collections.Counter(),
                 "text": "", "raw": "", "spans": set()}
    )
    for si, p in enumerate(files):
        if meta[si] is None:
            continue
        lineage, _, blocks = story_stream(p)
        if not blocks:
            continue
        for text, origin in blocks:
            toks_raw = WORD.findall(text)
            toks = [t.lower() for t in toks_raw]
            h = hashes(toks)
            if not h.size:
                continue
            idx = np.searchsorted(cross, h)
            idx[idx >= cross.size] = 0
            mask = cross[idx] == h if cross.size else np.zeros(h.size, dtype=bool)
            if not mask.any():
                continue
            klass = "human" if origin in HUMAN else "model"
            for hv in h[mask]:
                span_origin[int(hv)].add(klass)
                span_lineage[int(hv)].add(lineage)

            i = 0
            while i < mask.size:
                if not mask[i]:
                    i += 1
                    continue
                j = i
                while j < mask.size and mask[j]:
                    j += 1
                words = toks[i : j + K - 1]
                if len(words) >= MIN_PASSAGE:
                    key = " ".join(words)
                    rec = found[key]
                    if not rec["raw"]:
                        rec["raw"] = " ".join(toks_raw[i : j + K - 1])
                    rec["lineages"].add(lineage)
                    rec["stories"].add(si)
                    rec["origins"][klass] += 1
                    rec["spans"].update(int(x) for x in h[i:j])
                    rec["text"] = key
                i = j + 1

    # a passage's class is the union over its constituent spans, wherever they
    # occur -- not just over the occurrences that produced this merged string
    for rec in found.values():
        cls = set()
        lins = set()
        for hv in rec["spans"]:
            cls |= span_origin.get(hv, set())
            lins |= span_lineage.get(hv, set())
        rec["klass"] = ("both" if len(cls) == 2 else (cls.pop() if cls else "?"))
        rec["lineages"] |= lins
    return (
        {k: v for k, v in found.items() if len(v["lineages"]) >= 2},
        span_origin,
        span_lineage,
    )


def day(ts):
    if not ts:
        return None
    t = int(ts / 1000) if ts > 1e12 else int(ts)
    return datetime.datetime.utcfromtimestamp(t).date()


def report(found, meta, out, span_origin, span_lineage):
    rows = sorted(
        found.values(), key=lambda r: (-len(r["lineages"]), -len(r["stories"]))
    )

    def distinct(rs, overlap=0.5, limit=None):
        """Drop near-duplicates: one passage yields several merged strings.

        A run stops wherever the surrounding text stops crossing, so the same
        scaffold surfaces as a dozen rows differing by a clause. Greedy: emit a
        passage only if most of its spans are not already covered.
        """
        seen, out = set(), []
        for r in rs:
            sp = r["spans"]
            if sp and len(sp & seen) / len(sp) > overlap:
                continue
            seen |= sp
            out.append(r)
            if limit and len(out) >= limit:
                break
        return out
    by_pop = collections.Counter(r["klass"] for r in rows)
    by_span = collections.Counter(
        "both" if len(v) == 2 else next(iter(v)) for v in span_origin.values()
    )
    nspan = sum(by_span.values())

    L = [
        "# Inheritance — what crosses a lineage boundary",
        "",
        "Generated by `analysis/inherit.py`. **Regenerate, do not hand-edit.**",
        "",
        f"Every {K}-word span in the corpus, indexed by the lineages it appears "
        f"in (lineage = `created_at`, §13a). Contiguous crossing spans merged "
        f"into passages; passages under {MIN_PASSAGE} words dropped.",
        "",
        f"- **{nspan} spans** cross a lineage boundary, merging into "
        f"**{len(rows)} passages** of {MIN_PASSAGE}+ words.",
        f"- Spans by where they occur: **{by_span['human']} human blocks only** "
        f"({100 * by_span['human'] / nspan:.1f}%), **{by_span['model']} model "
        f"blocks only** ({100 * by_span['model'] / nspan:.1f}%), "
        f"**{by_span['both']} both** ({100 * by_span['both'] / nspan:.1f}%).",
        f"- Passages by the same rule: **{by_pop['human']}** human, "
        f"**{by_pop['model']}** model, **{by_pop['both']}** both.",
        "",
        "**Authorship is tallied per span, not per merged passage**, and the "
        "difference is not cosmetic. A run extends as far as the surrounding "
        "text also happens to cross, so one passage yields different merged "
        "strings in different contexts; keying the tally on that string split "
        "the PFCizer pitch into a model-only record and a human-only one when "
        "it occurs 11 times in `user` blocks and 12 in `ai`. The first run of "
        "this script published that split. Spans are identical wherever the "
        "passage appears, so they carry the count.",
        "",
        "The three populations answer different questions. Human-only is "
        "carried scaffolding *and* material pasted in from outside the corpus, "
        "which this cannot separate. Model-only is formulaic output recurring "
        "across unrelated documents — a boilerplate measure, not an inheritance "
        "one. **Both** is the column that matters: text that changed hands.",
        "",
        "## Passages crossing the most lineages",
        "",
        "| lineages | stories | where | passage |",
        "|---:|---:|---|---|",
    ]
    for r in distinct(rows, limit=30):
        where = r["klass"]
        txt = redact(r["text"])[:150].replace("|", "\\|")
        L.append(f"| {len(r['lineages'])} | {len(r['stories'])} | {where} | {txt} |")

    L += ["", "## Passages that changed hands", "",
          "Cross-lineage passages appearing in **both** a human block and a "
          "model block. Either the model produced it and the author carried it "
          "elsewhere, or the author wrote it and a model reproduced it.", "",
          "| lineages | stories | passage |", "|---:|---:|---|"]
    both = distinct([r for r in rows if r["klass"] == "both"], limit=25)
    for r in both:
        L.append(
            f"| {len(r['lineages'])} | {len(r['stories'])} | "
            f"{redact(r['text'])[:150].replace('|', chr(92) + '|')} |"
        )

    L += ["", "## How far back the vessels reach", "",
          "For each passage, the gap between the **founding dates of the "
          "documents it landed in**. Read this carefully: it is not the "
          "passage's own age. §12 records that no per-block timestamps exist, "
          "so when a passage entered a document is unrecoverable — pasting a "
          "2024 scaffold into a story founded in 2021 puts a 2021 date in the "
          "`earliest` column. The Counterfactual Interview scaffold reads as "
          "spanning 1,467 days from 2021-07-19 for exactly that reason: the "
          "2021 lineage is `Emotional Abuse SImulator v. 7.0`, last edited "
          "2023-12-01, two weeks after the Counterfactual Interview was "
          "created. What the column actually measures is **how deep into the "
          "back catalogue he reached for a vessel** when re-using a scaffold, "
          "and by that reading it is still worth having.",
          "", "| lineages | span (days) | earliest vessel | passage |",
          "|---:|---:|---|---|"]
    dated = []
    linday = {}
    for m in meta:
        if m and m["lineage"]:
            linday[m["lineage"]] = day(m["lineage"] * 1000)
    for r in rows:
        ds = [linday.get(x) for x in r["lineages"] if linday.get(x)]
        if len(ds) >= 2:
            dated.append(((max(ds) - min(ds)).days, min(ds), r))
    ordered = sorted(dated, reverse=True, key=lambda t: t[0])
    keep = {id(r) for r in distinct([t[2] for t in ordered], limit=25)}
    for gap, first, r in ordered:
        if id(r) not in keep:
            continue
        L.append(
            f"| {len(r['lineages'])} | {gap} | {first} | "
            f"{redact(r['text'])[:120].replace('|', chr(92) + '|')} |"
        )

    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus")
    ap.add_argument("--report", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path)
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    files = sorted(pathlib.Path(args.corpus).glob("*.json"))
    if args.limit:
        files = files[: args.limit]
    if not files:
        sys.exit(f"no *.json under {args.corpus}")

    h, s, meta = pass1(files)
    print(f"{len(files)} files, {h.size} spans", flush=True)
    cross = crossing(h, s, meta)
    print(f"{len(cross)} crossing span hashes", flush=True)
    del h, s
    found, span_origin, span_lineage = pass2(files, meta, cross)
    print(f"{len(found)} cross-lineage passages", flush=True)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8") as f:
            f.write("lineages\tstories\twhere\tpassage\n")
            for r in sorted(found.values(),
                            key=lambda r: -len(r["lineages"])):
                f.write(
                    f"{len(r['lineages'])}\t{len(r['stories'])}\t"
                    f"{r['klass']}\t"
                    f"{redact(r['text'])[:600]}\n"
                )
    if args.report:
        report(found, meta, args.report, span_origin, span_lineage)
        print(f"-> {args.report}")


if __name__ == "__main__":
    main()
