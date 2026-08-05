#!/usr/bin/env python3
"""The apparatus atlas: the recurring rooms, and what each one convenes.

The outside critique that opened this season put an "apparatus atlas" at
priority #1 — *what recurring rooms, machines and jurisdictions did he build?* —
and proposed reading the ten largest **named** families. §13 showed why that
cannot work: 76% of surviving stories are titled `New Story`, and the largest
things in the archive have no titles at all.

§14 supplies the right unit instead. The recurring object in this corpus is not
the story and not the character; it is **the setup text that convenes a room** —
the incantation that establishes a device, its roles, its procedure and its
rules of admission, which then gets pasted into a fresh document whenever the
device is wanted again. §14 found 3,481 such passages crossing lineage
boundaries. This clusters them into devices and describes each one.

Two tiers, because two different things deserve the name apparatus:

  * **Portable devices** — a scaffold that appears in two or more separately
    founded lineages. Clustered by shared spans: passages sharing any 8-word
    span belong to the same device, since a device's incantation is rewritten
    over the years and the variants have to be pulled back together.
  * **Resident apparatuses** — a large single lineage whose forks are all one
    room, never carried elsewhere. Invisible to the first tier by construction,
    and it holds some of the biggest works in the archive.

    python3 analysis/atlas.py corpus/json --report analysis/ATLAS.md \\
        --out data/ATLAS.tsv

Runs `inherit.py`'s two passes, so budget the same few minutes and ~3 GB.
"""

import argparse
import collections
import datetime
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from inherit import crossing, pass1, pass2, redact

MIN_DEVICE_LINEAGES = 2

# A convening text addresses somebody and declares what the room is for. This
# does not decide anything -- it is a column, so a reader can see at a glance
# which devices are the author's machinery and which are pasted-in documents.
CONVENES = re.compile(
    r"\b(welcome to|this is the|before you stands|where we (?:engage|operate|delve)"
    r"|you press|i want you to (?:act|pretend)|we are going to|let'?s (?:begin|start)"
    r"|in this (?:episode|show|segment)|the following is|simulat|generator|interview"
    r"|press conference|tribunal|panel|summon|calls? forth|convene|oracle|auditor"
    r"|prepares? the .{0,20}space)\b",
    re.I,
)

ALPHA = re.compile(r"[A-Za-z]{2,}")


def is_text(s):
    """Reject runs of punctuation and single-token loops as incantations."""
    toks = ALPHA.findall(s)
    if len(set(t.lower() for t in toks)) < 6:
        return False
    return len(set(t.lower() for t in toks)) / max(1, len(toks)) > 0.25


def devices(found):
    """Union-find over passages that share a span."""
    passages = list(found.values())
    parent = list(range(len(passages)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    owner = {}
    for i, r in enumerate(passages):
        for sp in r["spans"]:
            if sp in owner:
                a, b = find(owner[sp]), find(i)
                if a != b:
                    parent[a] = b
            else:
                owner[sp] = i

    g = collections.defaultdict(list)
    for i, r in enumerate(passages):
        g[find(i)].append(r)
    return list(g.values())


def day(ts):
    return datetime.datetime.utcfromtimestamp(int(ts)).date() if ts else None


def summarise(group, meta):
    lineages, stories, spans, cls = set(), set(), set(), set()
    for r in group:
        lineages |= r["lineages"]
        stories |= r["stories"]
        spans |= r["spans"]
        cls.add(r["klass"])
    # the incantation: the longest variant, which is the fullest statement of
    # the device's rules that survives anywhere
    best = max(group, key=lambda r: len(r["raw"] or r["text"]))
    days = sorted(d for d in (day(x) for x in lineages if x) if d)
    titles = collections.Counter()
    for si in stories:
        m = meta[si]
        if m:
            titles[(m["title"] or "New Story").split(" (")[0]] += 1
    return {
        "lineages": len(lineages),
        "stories": len(stories),
        "spans": len(spans),
        "variants": len(group),
        "klass": "both" if len(cls) > 1 or "both" in cls else next(iter(cls)),
        "first": days[0] if days else None,
        "last": days[-1] if days else None,
        "text": (best["raw"] or best["text"]),
        "titles": titles,
        "convenes": bool(CONVENES.search(best["raw"] or best["text"])),
        "lineage_ids": lineages,
    }


def resident(meta, fam_path, corpus, travelled, top=20):
    """Large lineages that contributed nothing to any portable device.

    `travelled` is the set of lineages appearing in tier 1. Excluding them is
    what makes this tier complementary rather than a second view of the same
    rooms: what is left is the documents whose text never left them.
    """
    fam = {}
    if pathlib.Path(fam_path).exists():
        for line in open(fam_path):
            p = line.rstrip("\n").split("\t")
            if len(p) >= 6 and p[0] != "remote_id":
                fam[p[0]] = p
    bycomp = collections.defaultdict(list)
    for p in fam.values():
        bycomp[p[1]].append(p)

    by_rid = {}
    for si, m in enumerate(meta):
        if m and m.get("remote_id"):
            by_rid[m["remote_id"]] = m

    out = []
    for comp, rows in sorted(bycomp.items(), key=lambda kv: -len(kv[1])):
        if len(rows) < 8:
            continue
        lin = {r[2] for r in rows}
        if len(lin) != 1:
            continue  # bifurcated lineages are handled in FAMILIES.md
        if int(next(iter(lin))) in travelled:
            continue
        m = next((by_rid[r[0]] for r in rows if r[0] in by_rid), None)
        if not m:
            continue
        doc = corpus / m["file"]
        try:
            d = json.loads(doc.read_text(encoding="utf-8", errors="replace"))
        except Exception:  # noqa: BLE001
            continue
        st = ((d.get("content") or {}).get("data") or {}).get("story") or {}
        opening = ""
        for b in (st.get("datablocks") or [])[:6]:
            if (b.get("origin") or "") in ("root", "prompt", "user"):
                opening += ((b.get("dataFragment") or {}).get("data")) or ""
            if len(opening) > 400:
                break
        titles = collections.Counter(
            (r[5] or "New Story").split(" (")[0] for r in rows
        )
        out.append(
            {
                "forks": len(rows),
                "lineage": day(int(next(iter(lin)))),
                "models": sorted({r[3] for r in rows}),
                "titles": titles,
                "opening": " ".join(opening.split())[:300],
            }
        )
        if len(out) >= top:
            break
    return out


def report(devs, res, meta, out, tsv):
    devs = [d for d in devs if d["lineages"] >= MIN_DEVICE_LINEAGES]
    devs.sort(key=lambda d: (-d["lineages"], -d["stories"]))
    conv = [d for d in devs if d["convenes"]]

    L = [
        "# The apparatus atlas",
        "",
        "Generated by `analysis/atlas.py`. **Regenerate, do not hand-edit.**",
        "",
        "The recurring object in this corpus is neither the story nor the "
        "character but **the setup text that convenes a room** (§14c). This "
        "clusters §14's cross-lineage passages into devices — passages sharing "
        "any 8-word span are one device, which pulls a scaffold's rewritten "
        "variants back together — and lists the large single-lineage rooms "
        "separately.",
        "",
        f"- **{len(devs)} portable devices**, appearing in two or more "
        f"separately founded lineages.",
        f"- **{len(conv)}** of them ({100 * len(conv) / max(1, len(devs)):.0f}%) "
        "match a convening pattern (*welcome to*, *this is the*, *where we "
        "engage*, *generator*, *interview*, *simulat…*). The rest are mostly "
        "pasted documents — the atlas cannot separate a scaffold the author "
        "wrote from an article he pasted, and does not pretend to.",
        f"- **{len(res)} resident apparatus{'es' if len(res) != 1 else ''}** — "
        "lineages of eight or more forks that contributed nothing to any "
        "portable device.",
        "",
        "## Tier 1 — portable devices",
        "",
        "`lineages` counts separately founded documents the device was pasted "
        "into; `variants` counts distinct merged wordings, which is a measure of "
        "how much the incantation was rewritten. `where` is §14's authorship "
        "class: **both** means the text sits in human *and* model blocks — the "
        "device was pasted somewhere and echoed back by a model somewhere else.",
        "",
        "| lin | stories | var | where | founded | the device |",
        "|---:|---:|---:|---|---|---|",
    ]
    for d in devs[:45]:
        span = f"{d['first']} .. {d['last']}" if d["first"] else "?"
        txt = redact(" ".join(d["text"].split()))[:190].replace("|", "\\|")
        L.append(
            f"| {d['lineages']} | {d['stories']} | {d['variants']} | "
            f"{d['klass']} | {span} | {txt} |"
        )

    L += [
        "",
        "## Tier 2 — resident apparatuses",
        "",
        "One lineage, eight or more forks, contributing to **no convening "
        "device in tier 1** — no scaffold from these documents was ever pasted "
        "into a separately founded one. Rooms built once and worked in place. "
        "Pasted articles and assistant boilerplate do not count as travelling, "
        "or every room in the archive would qualify as portable.",
        "",
        "| forks | founded | models | titles | opens on |",
        "|---:|---|---|---|---|",
    ]
    for r in res:
        t = "; ".join(f"{k} ×{v}" for k, v in r["titles"].most_common(2))
        L.append(
            f"| {r['forks']} | {r['lineage']} | {'/'.join(r['models'])[:34]} | "
            f"{t[:44]} | "
            f"{redact(r['opening'])[:190].replace('|', chr(92) + '|')} |"
        )

    L += [
        "",
        "## What the atlas cannot do",
        "",
        "1. **It cannot name a device.** The rows are incantations, not titles, "
        "because 76% of the stories have no title and the devices that do have "
        "names carry them inside the prose. Naming is a reading job; "
        "`FINDINGS.md` does it for the largest.",
        "2. **It cannot separate the author's machinery from pasted "
        "documents.** Both are `origin: user`. The `convenes` filter is a hint, "
        "not a judgement.",
        "3. **It cannot see a device that lived in Memory.** Memory and Author's "
        "Note are not datablocks (§14d).",
        "4. **It cannot date a device.** With no per-block timestamps (§12), "
        "`founded` is the range of *founding dates of the documents the device "
        "landed in* — a 2024 scaffold pasted into a 2021 story reads as 2021.",
        "",
    ]
    out.write_text("\n".join(L) + "\n", encoding="utf-8")

    if tsv:
        tsv.parent.mkdir(parents=True, exist_ok=True)
        with tsv.open("w", encoding="utf-8") as f:
            f.write("lineages\tstories\tvariants\twhere\tconvenes\tfirst\tlast\t"
                    "incantation\n")
            for d in devs:
                f.write(
                    f"{d['lineages']}\t{d['stories']}\t{d['variants']}\t"
                    f"{d['klass']}\t{int(d['convenes'])}\t{d['first']}\t"
                    f"{d['last']}\t"
                    f"{redact(' '.join(d['text'].split()))[:800]}\n"
                )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus")
    ap.add_argument("--report", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path)
    ap.add_argument("--families", default="data/FAMILIES.tsv")
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    corpus = pathlib.Path(args.corpus)
    files = sorted(corpus.glob("*.json"))
    if args.limit:
        files = files[: args.limit]

    h, s, meta = pass1(files)
    print(f"{len(files)} files, {h.size} spans", flush=True)
    cross = crossing(h, s, meta)
    print(f"{len(cross)} crossing spans", flush=True)
    del h, s
    found, _, _ = pass2(files, meta, cross)
    print(f"{len(found)} cross-lineage passages", flush=True)

    groups = devices(found)
    devs = [summarise(g, meta) for g in groups]
    devs = [d for d in devs if is_text(d["text"])]
    print(f"{len(devs)} device clusters", flush=True)
    travelled = set()
    for d in devs:
        if d["convenes"]:
            travelled |= d["lineage_ids"]
    res = resident(meta, args.families, corpus, travelled)
    print(f"{len(res)} resident apparatuses", flush=True)
    report(devs, res, meta, args.report, args.out)
    print(f"-> {args.report}")


if __name__ == "__main__":
    main()
