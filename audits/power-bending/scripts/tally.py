#!/usr/bin/env python3
"""Pass 3: compute every count from the rows files. Nothing here is counted by hand.

Inputs
  --rows      directory of coder output (batch_*.jsonl)
  --verifier  directory of verifier output (verify_*.jsonl), optional
  --lexical   the lexical_scope.jsonl from the Pass 1 reader
  --hits      lexical_hits.csv, rewritten in place with the scope column filled
  --corpus    corpus.jsonl, for model-version lookup
  --out       audits/power-bending/

Outputs
  power_bending.csv, unconfirmed.csv, disagreements.csv, counts.json
"""

import argparse
import csv
import json
import os
import re
import subprocess
from collections import Counter, defaultdict

CODES = [f"P{i}" for i in range(1, 12)]  # P1..P11 as of codebook v1.1

# A claude.ai conversation id is a bare UUID. A git-substrate id is "repo:path"
# or "repo:sha". The two substrates are counted separately and never summed
# into one headline: they are different instruments over different records, and
# an instance in a committed commit message is not commensurable with a turn in
# a private conversation.
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


def substrate_of(conversation_uuid):
    return "export" if UUID_RE.match(conversation_uuid or "") else "git"


def load_jsonl_dir(d, prefix):
    rows = []
    if not d or not os.path.isdir(d):
        return rows
    for fn in sorted(os.listdir(d)):
        if not (fn.startswith(prefix) and fn.endswith(".jsonl")):
            continue
        for line in open(os.path.join(d, fn), encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            r["_src"] = fn
            rows.append(r)
    return rows


def model_versions(repos_dir):
    """sha12 -> model string, read from the Co-Authored-By trailer."""
    out = {}
    if not os.path.isdir(repos_dir):
        return out
    for name in sorted(os.listdir(repos_dir)):
        repo = os.path.join(repos_dir, name)
        try:
            raw = subprocess.run(
                ["git", "-C", repo, "log", "--all", "--no-merges",
                 "--format=%H\x1e%b\x1d"],
                capture_output=True, text=True, errors="replace").stdout
        except OSError:
            continue
        for rec in raw.split("\x1d"):
            if "\x1e" not in rec:
                continue
            sha, body = rec.strip("\n").split("\x1e", 1)
            m = re.search(r"Co-Authored-By:\s*(Claude[^<\n]*)", body, re.IGNORECASE)
            out[f"{name}:{sha[:12]}"] = m.group(1).strip() if m else "unrecorded"
    return out


def kappa(a, b):
    """Cohen's kappa for two binary labellings over the same units."""
    n = len(a)
    if n == 0:
        return None
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    pa1, pb1 = sum(a) / n, sum(b) / n
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    if pe == 1.0:
        # Both coders flat-constant and identical: agreement is total but kappa
        # is undefined. Report it as such rather than as 1.0 or 0.0.
        return "undefined (no variance)" if po == 1.0 else 0.0
    return round((po - pe) / (1 - pe), 3)


def main():
    ap = argparse.ArgumentParser()
    for f in ("rows", "verifier", "lexical", "hits", "repos", "out"):
        ap.add_argument("--" + f)
    args = ap.parse_args()

    # "batch_" is the coding passes; "sweep_" is the P10/P11 adjudication pass.
    # Loading only the first silently dropped the whole sweep from the counts.
    coder = load_jsonl_dir(args.rows, "batch_") + load_jsonl_dir(args.rows, "sweep_")
    verif = load_jsonl_dir(args.verifier, "verify_")
    # verify_input.jsonl is the material handed to the verifier, not its output.
    verif = [r for r in verif if r.get("_src") != "verify_input.jsonl"]
    mv = model_versions(args.repos) if args.repos else {}

    # ---------- Pass 1 headline ----------
    lex = {}
    if args.lexical and os.path.exists(args.lexical):
        for line in open(args.lexical, encoding="utf-8"):
            line = line.strip()
            if line:
                r = json.loads(line)
                lex[r["hit_index"]] = r

    lex_counts = Counter()
    lex_unique = Counter()
    if args.hits and os.path.exists(args.hits) and lex:
        with open(args.hits, encoding="utf-8") as fh:
            hit_rows = list(csv.DictReader(fh))
        for i, row in enumerate(hit_rows):
            s = lex.get(i, {})
            row["scope"] = s.get("scope", "")
            row["duplicate_of"] = ("" if s.get("duplicate_of") is None
                                   else s.get("duplicate_of"))
            row["scope_note"] = s.get("note", "")
            lex_counts[row["scope"]] += 1
            if row["duplicate_of"] == "":
                lex_unique[row["scope"]] += 1
        fields = list(hit_rows[0].keys())
        with open(args.hits, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(hit_rows)

    # ---------- Pass 2 ----------
    confirmed = [r for r in coder if r.get("confirmed") is True
                 and r.get("evidence_type") in ("a", "b", "c")]
    unconfirmed = [r for r in coder if r not in confirmed]

    def write_rows(path, rows):
        fields = ["conversation_uuid", "date", "model_version", "title",
                  "message_index", "codes", "quote", "power_served",
                  "truth_cost", "evidence_type", "evidence_quote", "_src"]
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            for r in rows:
                r = dict(r)
                r["codes"] = ";".join(r.get("codes") or [])
                r["model_version"] = mv.get(r.get("conversation_uuid", ""),
                                            "unrecorded")
                w.writerow(r)

    os.makedirs(args.out, exist_ok=True)
    write_rows(os.path.join(args.out, "power_bending.csv"), confirmed)
    write_rows(os.path.join(args.out, "unconfirmed.csv"), unconfirmed)

    def block(rows):
        pc = Counter()
        for r in rows:
            for c in r.get("codes") or []:
                pc[c] += 1
        return {
            "confirmed_total": len(rows),
            "per_code": {c: pc.get(c, 0) for c in CODES},
            "per_month": dict(sorted(Counter(
                str(r.get("date", ""))[:7] for r in rows).items())),
            "per_model_version": dict(Counter(
                mv.get(r.get("conversation_uuid", ""), "unrecorded")
                for r in rows)),
            "conversations": len({r.get("conversation_uuid") for r in rows}),
        }

    by_sub = {"git": [], "export": []}
    for r in confirmed:
        by_sub[substrate_of(r.get("conversation_uuid", ""))].append(r)
    unconf_sub = Counter(substrate_of(r.get("conversation_uuid", ""))
                         for r in unconfirmed)

    per_code = Counter()
    for r in confirmed:
        for c in r.get("codes") or []:
            per_code[c] += 1
    per_month = Counter(str(r.get("date", ""))[:7] for r in confirmed)
    per_model = Counter(mv.get(r.get("conversation_uuid", ""), "unrecorded")
                        for r in confirmed)

    # ---------- kappa ----------
    kappas, disagreements = {}, []
    if verif:
        # Kappa is computed over exactly the conversations the verifier
        # FINISHED, never over the ones it was assigned. Two verifier passes
        # were killed mid-batch by a session rate limit; counting their unread
        # conversations as "verifier found nothing" would manufacture agreement
        # out of an outage. Each verifier therefore checkpoints a conversation
        # id to a done-file only after that conversation's rows are written,
        # and those files -- not the assignment -- define the unit set.
        vunits = set()
        for fn in sorted(os.listdir(args.verifier)):
            path = os.path.join(args.verifier, fn)
            if fn.startswith("done_") and fn.endswith(".txt"):
                for line in open(path, encoding="utf-8"):
                    line = line.strip().strip('"')
                    if line:
                        vunits.add(line)
            elif fn.startswith("done_") and fn.endswith(".json"):
                try:
                    vunits |= set(json.load(open(path, encoding="utf-8")))
                except (json.JSONDecodeError, TypeError):
                    pass
        # A conversation the verifier produced rows for is finished by
        # definition, even if the checkpoint write was the thing interrupted.
        vunits |= {r["conversation_uuid"] for r in verif}
        units = sorted(vunits)

        def present(rows, unit, code):
            return int(any(r["conversation_uuid"] == unit
                           and code in (r.get("codes") or []) for r in rows))

        for code in CODES:
            a = [present(coder, u, code) for u in units]
            b = [present(verif, u, code) for u in units]
            kappas[code] = kappa(a, b)
            for u, x, y in zip(units, a, b):
                if x != y:
                    disagreements.append({
                        "conversation_uuid": u, "code": code,
                        "coder": x, "verifier": y,
                        "note": "coder only" if x else "verifier only",
                    })
        kappas["_units_double_coded"] = len(units)

    # Disagreements raised by a human or second reader rather than by the
    # blind verifier pass. The specification requires every disagreement to be
    # listed and none resolved silently, and a re-reading that disputes a code
    # is a disagreement whether or not it came from the kappa pass. They are
    # merged here, and marked, so the file is the whole list rather than the
    # automatable part of it.
    manual = os.path.join(args.out, "disagreements_manual.csv")
    if os.path.exists(manual):
        with open(manual, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                row["note"] = "[second reader] " + (row.get("note") or "")
                disagreements.append(row)

    with open(os.path.join(args.out, "disagreements.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["conversation_uuid", "code", "coder",
                                           "verifier", "note"])
        w.writeheader()
        w.writerows(disagreements)

    counts = {
        "lexical": {
            "total_hits": sum(lex_counts.values()),
            "by_scope": dict(lex_counts),
            "by_scope_deduplicated": dict(lex_unique),
            "headline_SELF": lex_unique.get("SELF", 0),
            "headline_USER": lex_unique.get("USER", 0),
        },
        "power_bending": {
            "confirmed_total": len(confirmed),
            "unconfirmed_total": len(unconfirmed),
            "per_code": {c: per_code.get(c, 0) for c in CODES},
            "per_month": dict(sorted(per_month.items())),
            "per_model_version": dict(per_model),
        },
        "by_substrate": {
            "git": dict(block(by_sub["git"]),
                        unconfirmed=unconf_sub.get("git", 0)),
            "export": dict(block(by_sub["export"]),
                           unconfirmed=unconf_sub.get("export", 0)),
        },
        "kappa": kappas,
        "disagreements": len(disagreements),
    }
    with open(os.path.join(args.out, "counts.json"), "w", encoding="utf-8") as fh:
        json.dump(counts, fh, indent=2)
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
