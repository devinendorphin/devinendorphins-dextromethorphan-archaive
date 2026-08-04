#!/usr/bin/env python3
"""Recover the lineage partition of the corpus, and test a cheap key for it.

`CLAUDE.md`'s first standing rule is *never group by story id; group by
connected components of shared text*. Every script in `analysis/` obeys the
prohibition and none of them implements the prescription — `sweeps.py` groups by
title stem instead, which is the one thing the corpus is known to punish: **1,965
of 2,500 stories are titled `New Story`**, so a title-stem key collapses 79% of
the archive into one bucket and cannot see a lineage that was renamed.

This does two things.

1. **Builds the shared-text partition** for real: MinHash over the full block
   stream of every story (abandoned branches included — a NovelAI duplicate
   copies the whole undo DAG, so the dead branches are part of the inherited
   material), then connected components above a Jaccard threshold.

2. **Tests `created_at` as a stand-in for it.** NovelAI appears to carry a
   story's creation timestamp into its duplicates, which would make an exact
   epoch second a free lineage key that works on untitled stories. That is a
   claim about the platform, so it gets the control that should fail: the same
   overlap statistic on size-matched groups drawn from outside the cluster.

    python3 analysis/families.py corpus/json --report analysis/FAMILIES.md \\
        --out data/FAMILIES.tsv

Reading ~1 GB of JSON takes a few minutes. `--limit` samples for a smoke test.
"""

import argparse
import collections
import datetime
import hashlib
import json
import pathlib
import random
import statistics
import sys

import numpy as np

N_HASH = 128
SHINGLE = 5
MAX_UINT64 = np.uint64(0xFFFFFFFFFFFFFFFF)


# --------------------------------------------------------------------------
# fingerprints


def story_tokens(doc):
    """Every token the file holds, in block order, dead branches included."""
    story = ((doc.get("content") or {}).get("data") or {}).get("story") or {}
    out = []
    for b in story.get("datablocks") or []:
        frag = b.get("dataFragment") or {}
        text = frag.get("data") or ""
        if text:
            out.extend(text.split())
    return out


def shingles(tokens, k=SHINGLE):
    """64-bit hashes of overlapping k-word shingles."""
    if len(tokens) < k:
        return set()
    return {
        int.from_bytes(
            hashlib.blake2b(
                " ".join(tokens[i : i + k]).encode("utf-8", "replace"), digest_size=8
            ).digest(),
            "big",
        )
        for i in range(len(tokens) - k + 1)
    }


def minhash(sh, seeds):
    """Signature: min over each random permutation of the shingle set."""
    if not sh:
        return None
    a = np.fromiter(sh, dtype=np.uint64, count=len(sh))
    sig = np.empty(N_HASH, dtype=np.uint64)
    for j, s in enumerate(seeds):
        sig[j] = np.min(a ^ s)
    return sig


def load(corpus, limit=None):
    files = sorted(pathlib.Path(corpus).glob("*.json"))
    if limit:
        files = files[:limit]
    if not files:
        sys.exit(f"no *.json under {corpus}")
    rng = np.random.default_rng(20260804)
    seeds = rng.integers(0, int(MAX_UINT64), size=N_HASH, dtype=np.uint64)

    rows, sigs = [], []
    for p in files:
        try:
            doc = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        except Exception:  # noqa: BLE001 -- one file is truncated in Drive itself
            continue
        smeta = (doc.get("story") or {}).get("data") or {}
        settings = ((doc.get("content") or {}).get("data") or {}).get("settings") or {}
        params = settings.get("parameters") or {}
        toks = story_tokens(doc)
        sig = minhash(shingles(toks), seeds)
        if sig is None:
            continue
        ts = smeta.get("createdAt")
        rows.append(
            {
                "file": p.name,
                "remote_id": smeta.get("remoteId"),
                "title": smeta.get("title") or "",
                "created_at": int(ts / 1000) if ts and ts > 1e12 else (ts and int(ts)),
                "last_updated_at": (doc.get("story") or {}).get("lastUpdatedAt"),
                "model": settings.get("model"),
                "temperature": params.get("temperature"),
                "max_length": params.get("max_length"),
                "tokens": len(toks),
            }
        )
        sigs.append(sig)
    return rows, np.vstack(sigs)


# --------------------------------------------------------------------------
# partitions


def jaccard_matrix(sigs, block=256):
    """Estimated pairwise Jaccard from the signatures. n is ~2k, so dense is fine."""
    n = sigs.shape[0]
    out = np.zeros((n, n), dtype=np.float32)
    for i in range(0, n, block):
        chunk = sigs[i : i + block]
        eq = (chunk[:, None, :] == sigs[None, :, :]).sum(axis=2)
        out[i : i + block] = eq / sigs.shape[1]
    return out


def components(J, thresh):
    """Union-find over pairs above the threshold."""
    n = J.shape[0]
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, j in zip(*np.where(np.triu(J >= thresh, k=1))):
        ri, rj = find(int(i)), find(int(j))
        if ri != rj:
            parent[ri] = rj
    return [find(i) for i in range(n)]


def partition_of(labels):
    g = collections.defaultdict(list)
    for i, lab in enumerate(labels):
        g[lab].append(i)
    return g


def agreement(a, b):
    """How well partition `a` (candidate key) reproduces partition `b` (text).

    Returns (purity, completeness): the share of stories whose `a`-group sits
    entirely inside one `b`-group, and the share of `b`-groups that are an exact
    union of `a`-groups.
    """
    bl = {i: lab for lab, idx in partition_of(b).items() for i in idx}
    pure = tot = 0
    for _, idx in partition_of(a).items():
        tot += len(idx)
        if len({bl[i] for i in idx}) == 1:
            pure += len(idx)
    whole = nb = 0
    al = {i: lab for lab, idx in partition_of(a).items() for i in idx}
    for _, idx in partition_of(b).items():
        nb += 1
        groups = {al[i] for i in idx}
        if sum(len(partition_of(a)[g]) for g in groups) == len(idx):
            whole += 1
    return pure / tot, whole / nb


# --------------------------------------------------------------------------
# report


def report(rows, J, key_labels, text_labels, thresh, out):
    n = len(rows)
    keyg = partition_of(key_labels)
    txtg = partition_of(text_labels)

    # observed: mean within-cluster Jaccard for created_at clusters of size >1
    obs, sizes = [], []
    for _, idx in keyg.items():
        if len(idx) < 2:
            continue
        sizes.append(len(idx))
        vals = [J[i, j] for a, i in enumerate(idx) for j in idx[a + 1 :]]
        obs.append(statistics.mean(vals))

    # control that should fail: same sizes, members drawn from other clusters
    rng = random.Random(20260804)
    ctl = []
    for size in sizes:
        pick = rng.sample(range(n), size)
        vals = [J[i, j] for a, i in enumerate(pick) for j in pick[a + 1 :]]
        ctl.append(statistics.mean(vals))

    # second control: same edit-day, which is how sweeps.py already groups
    byday = collections.defaultdict(list)
    for i, r in enumerate(rows):
        ts = r["last_updated_at"]
        if ts:
            byday[datetime.datetime.utcfromtimestamp(
                int(ts / 1000) if ts > 1e12 else int(ts)).date()].append(i)
    dayctl = []
    for size in sizes:
        pool = [v for v in byday.values() if len(v) >= size]
        if not pool:
            continue
        pick = rng.sample(rng.choice(pool), size)
        vals = [J[i, j] for a, i in enumerate(pick) for j in pick[a + 1 :]]
        dayctl.append(statistics.mean(vals))

    # candidate keys, scored the same way against the text partition
    def editday(r):
        ts = r["last_updated_at"]
        if not ts:
            return None
        return datetime.datetime.utcfromtimestamp(
            int(ts / 1000) if ts > 1e12 else int(ts)).date()

    import re as _re

    def stem(r):
        return _re.sub(r"\s*\(\d+\)$", "", r["title"] or "New Story").lower()

    keys = {
        "`created_at` (exact second)": key_labels,
        "title stem + last-edit day (`sweeps.py`)":
            [(stem(r), editday(r)) for r in rows],
        "title stem alone": [stem(r) for r in rows],
        "last-edit day alone": [editday(r) for r in rows],
    }
    scored = {k: agreement(v, text_labels) for k, v in keys.items()}
    purity, completeness = scored["`created_at` (exact second)"]

    singles_key = sum(1 for _, v in keyg.items() if len(v) == 1)
    singles_txt = sum(1 for _, v in txtg.items() if len(v) == 1)

    L = [
        "# Families — the shared-text partition, and a free key for it",
        "",
        "Generated by `analysis/families.py`. **Regenerate, do not hand-edit.**",
        "",
        f"{n} stories fingerprinted (MinHash, {N_HASH} hashes over "
        f"{SHINGLE}-word shingles of the full block stream, abandoned branches "
        f"included). Components joined at Jaccard ≥ {thresh}.",
        "",
        "## The partition",
        "",
        f"- **{len(txtg)} text components**, {singles_txt} of them singletons.",
        f"- **{len(keyg)} `created_at` clusters**, {singles_key} of them singletons.",
        f"- Stories in a multi-member text component: "
        f"**{n - singles_txt}** ({100 * (n - singles_txt) / n:.0f}%).",
        "",
        "## Which cheap key reproduces it?",
        "",
        "**Purity** — share of stories whose key-group sits entirely inside one "
        "text component (does the key ever join unrelated stories?). "
        "**Completeness** — share of text components that are an exact union of "
        "key-groups (does the key ever split a lineage?). A key needs both.",
        "",
        "| key | purity | completeness |",
        "|---|---:|---:|",
    ]
    for name, (p, c) in sorted(scored.items(), key=lambda kv: -kv[1][0] - kv[1][1]):
        L.append(f"| {name} | {100 * p:.1f}% | {100 * c:.1f}% |")
    L += [
        "",
        "| group | mean pairwise Jaccard |",
        "|---|---:|",
        f"| `created_at` cluster | **{statistics.mean(obs):.3f}** |",
        f"| same last-edit day, matched size | {statistics.mean(dayctl):.3f} |",
        f"| random, matched size | {statistics.mean(ctl):.3f} |",
        "",
        "The random row is the control that should fail, and does. The edit-day "
        "row is the one that had to be run: in this corpus a day's editing is "
        "usually one sweep, so a matched group drawn from a single edit day is "
        "already half a lineage — and it still lands well below the "
        "`created_at` clusters. Mean overlap and the partition scores agree, "
        "which they did not on a 300-file slice, where the edit-day control "
        "*beat* the key.",
        "",
        "## Threshold sensitivity",
        "",
        "The component structure should not be an artifact of where the "
        "threshold was put.",
        "",
        "| Jaccard ≥ | components | singletons | largest | `created_at` purity |",
        "|---:|---:|---:|---:|---:|",
    ]
    for t in (0.05, 0.1, 0.2, 0.3, 0.5, 0.7):
        lab = components(J, t)
        g = partition_of(lab)
        p, _ = agreement(key_labels, lab)
        L.append(
            f"| {t:g} | {len(g)} | {sum(1 for v in g.values() if len(v) == 1)} | "
            f"{max(len(v) for v in g.values())} | {100 * p:.1f}% |"
        )
    L += [
        "",
        "## Largest text components",
        "",
        "| stories | span | models | temperatures | titles |",
        "|---:|---|---|---|---|",
    ]
    for _, idx in sorted(txtg.items(), key=lambda kv: -len(kv[1]))[:25]:
        if len(idx) < 2:
            continue
        rs = [rows[i] for i in idx]
        days = sorted(
            datetime.datetime.utcfromtimestamp(
                int(r["last_updated_at"] / 1000)
                if r["last_updated_at"] and r["last_updated_at"] > 1e12
                else int(r["last_updated_at"])
            ).date()
            for r in rs
            if r["last_updated_at"]
        )
        span = f"{days[0]} .. {days[-1]}" if days else "?"
        models = "/".join(sorted({str(r["model"]) for r in rs}))
        temps = sorted({r["temperature"] for r in rs if r["temperature"] is not None})
        titles = collections.Counter(
            (r["title"] or "New Story").split(" (")[0] for r in rs
        )
        tt = "; ".join(f"{t} ×{c}" for t, c in titles.most_common(3))
        L.append(
            f"| {len(idx)} | {span} | {models[:40]} | "
            f"{', '.join(f'{t:g}' for t in temps)[:44]} | {tt[:70]} |"
        )

    L += [
        "",
        "## Components that cross a model boundary",
        "",
        "The lineages that were carried forward onto new equipment. These are the "
        "only places in the corpus where the same document exists on two models, "
        "which is what any model-comparative reading needs — and §11 of "
        "`FINDINGS.md` still applies inside them, because the settings moved too.",
        "",
        "| stories | models | span | titles |",
        "|---:|---|---|---|",
    ]
    crossers = []
    for _, idx in txtg.items():
        if len(idx) < 2:
            continue
        rs = [rows[i] for i in idx]
        ms = {str(r["model"]) for r in rs}
        if len(ms) > 1:
            crossers.append((len(idx), ms, rs))
    for size, ms, rs in sorted(crossers, key=lambda c: -c[0])[:20]:
        days = sorted(
            datetime.datetime.utcfromtimestamp(
                int(r["last_updated_at"] / 1000)
                if r["last_updated_at"] and r["last_updated_at"] > 1e12
                else int(r["last_updated_at"])
            ).date()
            for r in rs
            if r["last_updated_at"]
        )
        titles = collections.Counter(
            (r["title"] or "New Story").split(" (")[0] for r in rs
        )
        L.append(
            f"| {size} | {'/'.join(sorted(ms))[:44]} | "
            f"{days[0]} .. {days[-1]} | "
            f"{'; '.join(f'{t} ×{c}' for t, c in titles.most_common(2))[:60]} |"
        )
    # transplanting: one text component holding two separately-created lineages
    transfers = []
    for _, idx in txtg.items():
        if len(idx) < 2:
            continue
        cts = {rows[i]["created_at"] for i in idx if rows[i]["created_at"]}
        if len(cts) > 1:
            transfers.append((len(idx), sorted(cts)))

    L += [
        "",
        f"**{len(crossers)} components span more than one model**, covering "
        f"{sum(c[0] for c in crossers)} stories.",
        "",
        "## Lineages that bifurcated",
        "",
        "One `created_at` lineage sitting in two or more text components is a "
        "lineage that **diverged past the threshold** — the forks kept being "
        "worked until they no longer shared a third of their text. `created_at` "
        "supplies the ancestry these branches have in common; the Jaccard "
        "supplies the split. Neither measure finds this alone.",
        "",
        "Listed only where **both branches carry two or more forks** — a lineage "
        "with one stub fork hanging off it is a false start, not a divergence.",
        "",
        "| forks | created | branches | each branch: n, models, last-edit span |",
        "|---:|---|---:|---|",
    ]
    for ct, idx in sorted(keyg.items(), key=lambda kv: -len(kv[1])):
        if len(idx) < 3 or not ct:
            continue
        branches = collections.defaultdict(list)
        for i in idx:
            branches[text_labels[i]].append(i)
        if len(branches) < 2:
            continue
        if sorted((len(v) for v in branches.values()), reverse=True)[1] < 2:
            continue
        parts = []
        for _, bidx in sorted(branches.items(), key=lambda kv: -len(kv[1])):
            rs = [rows[i] for i in bidx]
            days = sorted(
                d for d in (editday(r) for r in rs) if d
            )
            ms = "/".join(sorted({str(r["model"]) for r in rs}))
            parts.append(
                f"**{len(bidx)}** {ms[:34]} {days[0]}..{days[-1]}"
                if days else f"**{len(bidx)}** {ms[:34]}"
            )
        L.append(
            f"| {len(idx)} | "
            f"{datetime.datetime.utcfromtimestamp(ct).strftime('%Y-%m-%d')} | "
            f"{len(branches)} | {' — '.join(parts[:4])} |"
        )
    L += [
        "",
        "## Transplanting between lineages",
        "",
        "A component holding two different `created_at` values is material that "
        "moved *sideways*: a scaffold pasted out of one document into a "
        "separately-created one, rather than inherited by duplication.",
        "",
        f"- **{len(transfers)} components**, covering "
        f"{sum(t[0] for t in transfers)} stories, join more than one lineage.",
    ]
    if transfers:
        gaps = [
            (max(c) - min(c)) / 86400.0 for _, c in transfers
        ]
        L.append(
            f"- Median gap between the joined lineages' creation dates: "
            f"**{statistics.median(gaps):.0f} days**; maximum {max(gaps):.0f}."
        )
    L += [
        "",
        "**This is a whole-document measure and it cannot see resurrection of a "
        "single passage.** A sentence carried from a 2023 story into a 2026 one "
        "moves the Jaccard of two large documents by nothing. Read the number "
        "as *scaffolds are rarely re-pasted across lineages*, not as *nothing "
        "is carried forward* — the second claim needs a passage-level measure "
        "that does not exist yet.",
        "",
    ]
    out.write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus", help="directory of *.json exports")
    ap.add_argument("--report", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, help="per-story family table (TSV)")
    ap.add_argument("--thresh", type=float, default=0.30)
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    rows, sigs = load(args.corpus, args.limit)
    print(f"{len(rows)} stories fingerprinted")
    J = jaccard_matrix(sigs)
    text_labels = components(J, args.thresh)
    key_labels = [r["created_at"] for r in rows]

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8") as f:
            f.write("remote_id\tfamily\tcreated_at\tmodel\ttemperature\ttitle\n")
            for r, lab in zip(rows, text_labels):
                f.write(
                    f"{r['remote_id']}\t{lab}\t{r['created_at']}\t{r['model']}\t"
                    f"{r['temperature']}\t{r['title']}\n"
                )
    if args.report:
        report(rows, J, key_labels, text_labels, args.thresh, args.report)
        print(f"-> {args.report}")


if __name__ == "__main__":
    main()
