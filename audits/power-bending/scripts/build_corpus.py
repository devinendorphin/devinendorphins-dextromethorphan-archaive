#!/usr/bin/env python3
"""Build the audit corpus from git substrate.

The spec's primary input (corpus/claude-export/conversations.json) is absent from
this container. This script builds the substitute substrate Endorphin asked for:
the Claude-authored record across every GitHub repository in the exchange.

Two record types, kept separate because they are not the same instrument:

  TRANSCRIPT turns -- files committed to the repos that record a Claude<->Endorphin
    session verbatim, with speaker labels. These are the near-analogue of
    conversations.json: they carry adjacency, so evidence type (a) (Endorphin
    corrected it later in the same conversation) is computable on them.

  COMMIT records -- Claude-authored / Claude-co-authored commits: the message plus
    the lines the commit added. Adjacency is weak and there is no interlocutor,
    so only evidence type (c) (a checkable fact contradicts it) is computable.

Output: corpus.jsonl, one JSON object per unit, to the path given as argv[2].
Nothing here is committed; it contains message text.
"""

import json
import os
import re
import subprocess
import sys

# Speaker-label vocabularies seen across the repos. Extended by probe, not guessed.
CLAUDE_LABELS = {
    "instrument", "claude", "assistant", "model", "ai", "a", "opus", "sonnet",
}
USER_LABELS = {
    "operator", "endorphin", "user", "human", "devinendorphin", "q", "me",
}

# A heading that opens a turn, in any of the shapes the repos actually use.
TURN_HEADING = re.compile(
    r"^(?:#{1,6}\s*)?\[?(?:Turn|TURN|turn)\s*(\d+[a-z]?)\]?\s*[\]\-—:|]*\s*(.+?)\s*$"
)
# A bare speaker heading with no turn number, e.g. "**Operator:**" or "## Claude".
SPEAKER_HEADING = re.compile(
    r"^(?:#{1,6}\s*)?\*{0,2}(" + "|".join(sorted(CLAUDE_LABELS | USER_LABELS)) +
    r")\*{0,2}\s*:?\s*$",
    re.IGNORECASE,
)

DATE_IN_NAME = re.compile(r"(20\d\d-\d\d-\d\d)")


def speaker_of(label):
    """Map a heading's trailing label to claude / user / None."""
    tokens = re.findall(r"[A-Za-z]+", label.lower())
    for t in tokens:
        if t in CLAUDE_LABELS:
            return "claude"
        if t in USER_LABELS:
            return "user"
    return None


def parse_transcript(path, text):
    """Split a transcript file into turns. Returns [] if it is not a transcript."""
    lines = text.split("\n")
    marks = []  # (line_index, speaker, turn_label)
    for i, line in enumerate(lines):
        m = TURN_HEADING.match(line.strip())
        if m and m.group(2):
            sp = speaker_of(m.group(2))
            if sp:
                marks.append((i, sp, "Turn " + m.group(1)))
                continue
        m2 = SPEAKER_HEADING.match(line.strip())
        if m2:
            sp = speaker_of(m2.group(1))
            if sp:
                marks.append((i, sp, m2.group(1)))

    # Require real alternation, not one stray word that matched a label.
    if len(marks) < 4:
        return []
    speakers = {sp for _, sp, _ in marks}
    if speakers != {"claude", "user"}:
        return []

    turns = []
    for n, (start, sp, label) in enumerate(marks):
        end = marks[n + 1][0] if n + 1 < len(marks) else len(lines)
        body = "\n".join(lines[start + 1:end]).strip()
        if not body:
            continue
        turns.append({
            "message_index": n,
            "speaker": sp,
            "turn_label": label,
            "text": body,
        })
    return turns


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True, text=True, errors="replace",
    ).stdout


def claude_commits(repo):
    """Commits authored by Claude or carrying a Claude Co-Authored-By trailer."""
    sep = "\x1e"
    fmt = sep.join(["%H", "%ad", "%s", "%b", "%an"])
    raw = git(repo, "log", "--all", "--no-merges", "--date=short",
              "--format=" + fmt + "\x1d")
    out = []
    for rec in raw.split("\x1d"):
        rec = rec.strip("\n")
        if not rec:
            continue
        parts = rec.split(sep)
        if len(parts) < 5:
            continue
        sha, date, subject, body, author = parts[0], parts[1], parts[2], parts[3], parts[4]
        is_claude = (
            "claude" in author.lower()
            or re.search(r"co-authored-by:\s*claude", body, re.IGNORECASE)
        )
        if not is_claude:
            continue
        # Strip the attribution trailers: they are harness boilerplate, not prose,
        # and they carry an address we do not want in the audit output.
        clean_body = "\n".join(
            l for l in body.split("\n")
            if not re.match(r"^\s*(Co-Authored-By|Claude-Session|Generated with|🤖)", l, re.IGNORECASE)
        ).strip()
        out.append({"sha": sha, "date": date, "subject": subject, "body": clean_body})
    return out


def added_lines(repo, sha):
    """The prose a commit added, excluding diff noise."""
    raw = git(repo, "show", "--format=", "--unified=0", sha)
    keep = []
    for line in raw.split("\n"):
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            keep.append(line[1:])
    return "\n".join(keep)


TEXT_EXT = (".md", ".txt", ".markdown", ".rst")


def main():
    repos_dir = sys.argv[1]
    out_path = sys.argv[2]

    units = []
    for name in sorted(os.listdir(repos_dir)):
        repo = os.path.join(repos_dir, name)
        if not os.path.isdir(os.path.join(repo, ".git")) and not os.path.islink(repo):
            if not os.path.exists(os.path.join(repo, ".git")):
                continue

        # ---- transcripts at HEAD ----
        for root, dirs, files in os.walk(repo):
            dirs[:] = [d for d in dirs if d != ".git"]
            for fn in files:
                if not fn.lower().endswith(TEXT_EXT):
                    continue
                p = os.path.join(root, fn)
                try:
                    if os.path.getsize(p) > 4_000_000:
                        continue
                    with open(p, encoding="utf-8", errors="replace") as fh:
                        text = fh.read()
                except OSError:
                    continue
                turns = parse_transcript(p, text)
                if not turns:
                    continue
                rel = os.path.relpath(p, repo)
                dm = DATE_IN_NAME.search(rel)
                # Fall back to the file's first-commit date when the name has none.
                date = dm.group(1) if dm else (
                    git(repo, "log", "--diff-filter=A", "--format=%ad",
                        "--date=short", "--", rel).strip().split("\n")[-1] or "")
                units.append({
                    "kind": "transcript",
                    "repo": name,
                    "conversation_uuid": name + ":" + rel,
                    "title": os.path.splitext(os.path.basename(rel))[0],
                    "date": date,
                    "path": rel,
                    "turns": turns,
                })

        # ---- Claude-authored commits ----
        for c in claude_commits(repo):
            body = c["body"]
            add = added_lines(repo, c["sha"])
            units.append({
                "kind": "commit",
                "repo": name,
                "conversation_uuid": name + ":" + c["sha"][:12],
                "title": c["subject"],
                "date": c["date"],
                "sha": c["sha"],
                "turns": [{
                    "message_index": 0,
                    "speaker": "claude",
                    "turn_label": "commit-message",
                    "text": c["subject"] + ("\n\n" + body if body else ""),
                }] + ([{
                    "message_index": 1,
                    "speaker": "claude",
                    "turn_label": "added-lines",
                    "text": add,
                }] if add.strip() else []),
            })

    with open(out_path, "w", encoding="utf-8") as fh:
        for u in units:
            fh.write(json.dumps(u, ensure_ascii=False) + "\n")

    n_tr = sum(1 for u in units if u["kind"] == "transcript")
    n_cm = sum(1 for u in units if u["kind"] == "commit")
    n_claude_turns = sum(
        1 for u in units for t in u["turns"] if t["speaker"] == "claude")
    chars = sum(len(t["text"]) for u in units for t in u["turns"]
                if t["speaker"] == "claude")
    print(f"transcripts={n_tr} commits={n_cm} claude_units={n_claude_turns} "
          f"claude_chars={chars}")
    for u in units:
        if u["kind"] == "transcript":
            print(f"  TRANSCRIPT {u['conversation_uuid']} turns={len(u['turns'])} "
                  f"date={u['date']}")


if __name__ == "__main__":
    main()
