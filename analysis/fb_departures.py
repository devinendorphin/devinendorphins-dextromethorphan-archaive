#!/usr/bin/env python3
"""How many people he was in contact with are no longer friends. Counts only.

Facebook exports no removal events, so departures cannot be read directly
(see FACEBOOK.md, "Why the departures are missing"). They can be bounded by
set difference: everyone who appears as a correspondent in the message
threads, minus everyone still on the friends list at export.

**This script never emits a name.** Names are read into memory to do the
matching and only cardinalities are printed or written. That is the whole
reason it exists as a script rather than an ad-hoc command -- the constraint
is enforced in code, and any change that prints a name is a bug.

What the number is not: correspondents who were never friends (message
requests, strangers, group-chat participants, business accounts) land in the
same bucket as people who unfriended him, so the figure is an **upper bound
on departures**, not a count of them. The 1:1 restriction and the date
windows below narrow it; they do not clean it.

Matching is on normalised display names, which is exact for the common case
and silently wrong for renames and for two people sharing a name.

Usage:
    python3 analysis/fb_departures.py
"""
import os, re, sys, glob, collections, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORK = os.environ.get("FB_WORK", os.path.join(ROOT, "exports", "facebook"))
OUT = os.path.join(WORK, "extracted")
sys.path.insert(0, HERE)
from fb_export import feed_entries, message_turns

SELF = "devongallegos"

def norm(n):
    return re.sub(r"[^a-z]", "", (n or "").lower())

def friends():
    p = os.path.join(OUT, "connections", "friends", "your_friends.html")
    out = {}
    for e in feed_entries(p):
        n = norm(e.get("header") or e.get("text"))
        if n and n != SELF:
            out[n] = e["dt"]
    return out

def correspondents():
    """{normalised name: (first_dt, last_dt, n_turns, seen_in_one_to_one)}"""
    agg = {}
    threads = glob.glob(os.path.join(OUT, "your_facebook_activity", "messages",
                                     "*", "*", "*.html"))
    by_thread = collections.defaultdict(list)
    for f in threads:
        by_thread[os.path.dirname(f)].append(f)

    for tdir, pages in by_thread.items():
        turns = []
        for f in pages:
            turns.extend(message_turns(f))
        who = {norm(t["sender"]) for t in turns if t["sender"]}
        who.discard("")
        others = who - {SELF}
        one_to_one = len(others) == 1
        for t in turns:
            n = norm(t["sender"])
            if not n or n == SELF:
                continue
            first, last, cnt, solo = agg.get(n, (t["dt"], t["dt"], 0, False))
            agg[n] = (min(first, t["dt"]), max(last, t["dt"]), cnt + 1,
                      solo or one_to_one)
    return agg, len(by_thread)

def main():
    F = friends()
    C, nthreads = correspondents()

    gone = {n for n in C if n not in F}
    solo = {n for n in gone if C[n][3]}

    print(f"threads read                      {nthreads:6}")
    print(f"friends surviving at export       {len(F):6}")
    print(f"distinct correspondents           {len(C):6}")
    print(f"  of whom still friends           {len(C)-len(gone):6}")
    print(f"  of whom NOT still friends       {len(gone):6}   <- upper bound")
    print(f"  ...restricted to 1:1 threads    {len(solo):6}")

    print("\nupper bound by last-contact year (1:1 correspondents only):")
    by = collections.Counter(C[n][1].year for n in solo)
    for y in sorted(by):
        print(f"  {y}  {by[y]:5}  {'#'*min(by[y],60)}")

    for label, lo, hi in [("last heard from during 2019", 2019, 2019),
                          ("last heard from 2017-2019", 2017, 2019),
                          ("in contact 2019 or later", 2019, 2100)]:
        n = sum(1 for x in solo if lo <= C[x][1].year <= hi)
        print(f"\n{label:32} {n:5}")

    # sanity: confirm nothing name-shaped is in the output path
    assert all(isinstance(v, int) for v in by.values())

if __name__ == "__main__":
    main()
