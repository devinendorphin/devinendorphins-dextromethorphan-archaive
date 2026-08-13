#!/usr/bin/env python3
"""The friend graph over time, and what it can and cannot say.

Endorphin's question, 2026-08-13: if every friendship carries a start date,
can't the total be reconstructed month by month longitudinally?

The arithmetic works and this script does it. What the resulting curve *is*
needs stating plainly, because it looks like a friend count and is not one.

`your_friends.html` lists the friendships that still existed when the export
was generated (2024-10-26), each with the date it began. There is no removals
file anywhere in the export -- checked; Facebook does not emit one. So:

    curve(t) = people who friended him by t AND were still friends in 2024-10

That is a **survivor curve**. It is monotonically non-decreasing by
construction, so it can never show a loss, and the true historical count is
curve(t) + everyone who had joined by t and left before 2024-10 -- a term this
export does not contain. The curve is a lower bound and nothing more.

The monthly *addition* series from the same data is a different measurement and
does carry signal, because it is about recruitment rather than retention. That
is what the report below leads with.

Usage:
    python3 analysis/fb_friends.py [start_year] [end_year]
"""
import os, sys, collections, datetime, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORK = os.environ.get("FB_WORK", os.path.join(ROOT, "exports", "facebook"))
sys.path.insert(0, HERE)
from fb_export import feed_entries

SRC = os.path.join(WORK, "extracted", "connections", "friends", "your_friends.html")
EXPORTED = datetime.datetime(2024, 10, 26)

def monthly():
    es = [e for e in feed_entries(SRC) if e["dt"]]
    return collections.Counter((e["dt"].year, e["dt"].month) for e in es), len(es)

def main():
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 2017
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 2021
    m, total = monthly()

    span = [(y, mo) for y in range(2015, 2025) for mo in range(1, 13)
            if datetime.datetime(y, mo, 1) <= EXPORTED]
    vals = [m.get(k, 0) for k in span]
    ranked = sorted(vals, reverse=True)

    print(f"{total} surviving friendships as of {EXPORTED.date()}")
    print(f"monthly additions 2015-01..{span[-1][0]}-{span[-1][1]:02d}: "
          f"mean {st.mean(vals):.2f}, median {st.median(vals)}, max {max(vals)}\n")

    print("highest months:")
    for k in sorted(span, key=lambda k: -m.get(k, 0))[:6]:
        note = "   <-- the written half of the 2019 series" if k == (2019, 5) else ""
        print(f"  {k[0]}-{k[1]:02d}  {m.get(k,0):3}{note}")

    run = sum(v for k, v in m.items()
              if datetime.datetime(*k, 1) < datetime.datetime(lo, 1, 1))
    print(f"\n{'month':9}{'added':>6}{'survivors':>11}")
    for y in range(lo, hi + 1):
        for mo in range(1, 13):
            if datetime.datetime(y, mo, 1) > EXPORTED:
                break
            n = m.get((y, mo), 0)
            run += n
            note = ""
            if (y, mo) == (2019, 5):
                note = "  written half"
            elif (y, mo) == (2019, 7):
                note = "  the 157 screenshots"
            print(f"{y}-{mo:02d}  {n:6}{run:11}  {'#'*n}{note}")

    may = m.get((2019, 5), 0)
    print(f"\nMay 2019 = {may}, rank {ranked.index(may)+1} of {len(vals)} months, "
          f"{may/st.mean(vals):.1f}x the mean")
    zeros = sum(1 for v in vals if v == 0)
    print(f"July 2019 = {m.get((2019,7),0)}; {zeros} of {len(vals)} months are zero "
          f"({100*zeros/len(vals):.0f}%), so a zero month is not a signal")
    print("\nNeither figure measures retention. See the module docstring.")

if __name__ == "__main__":
    main()
