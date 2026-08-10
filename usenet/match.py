import re, sys, collections
from itertools import permutations

INV="/tmp/claude-0/-home-user-devinendorphins-dextromethorphan-archaive/1867aab3-9062-534a-a3a3-6d33bd4cfcec/scratchpad/prodigy_ids.tsv"
rows=[]
for line in open(INV, encoding='utf8', errors='replace'):
    p=line.rstrip("\n").split("\t")
    if len(p)<2: continue
    grp, tok = p[0], p[1]
    m=re.match(r"([A-Za-z0-9]+)@prodigy\.(com|net)(?:\s*\(([^)]*)\))?", tok, re.I)
    if not m: continue
    rows.append((grp, m.group(1).upper(), m.group(2).lower(), (m.group(3) or "").strip()))

print(f"total address tokens: {len(rows)}")
com=[r for r in rows if r[2]=="com"]
ids=sorted({r[1] for r in com})
print(f"distinct prodigy.com IDs: {len(ids)}")
print(f"distinct prodigy.net locals: {len({r[1] for r in rows if r[2]=='net'})}")

def ed(a,b):
    if abs(len(a)-len(b))>3: return 9
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]
        for j,cb in enumerate(b,1):
            cur.append(min(prev[j]+1, cur[j-1]+1, prev[j-1]+(ca!=cb)))
        prev=cur
    return prev[-1]

targets=["YGXS04","YGSX04"]
perms={"".join(p)+"04" for p in permutations("YGXS")}
print(f"\n=== exact stem matches (all 24 letter-permutations + 04):")
hit=[i for i in ids if i[:6] in perms]
print("  ", hit if hit else "NONE")

print(f"\n=== IDs within edit distance <=2 of either stem:")
near=[]
for i in ids:
    d=min(ed(i[:6],t) for t in targets)
    if d<=2: near.append((d,i))
for d,i in sorted(near)[:40]:
    names={r[3] for r in com if r[1]==i and r[3]}
    grps={r[0] for r in com if r[1]==i}
    print(f"   dist={d}  {i}  {sorted(names)}  {sorted(grps)}")
if not near: print("   NONE")

print(f"\n=== any prodigy.com ID whose digits are 04:")
d04=[i for i in ids if re.match(r"^[A-Z]{4}04",i)]
for i in sorted(d04):
    names={r[3] for r in com if r[1]==i and r[3]}
    print(f"   {i}  {sorted(names)}")
if not d04: print("   NONE")

print(f"\n=== any ID starting YG:")
yg=[i for i in ids if i.startswith("YG")]
print("  ", yg if yg else "NONE")

print(f"\n=== all Y-prefix prodigy.com IDs (context):")
for i in sorted(i for i in ids if i.startswith("Y")):
    names={r[3] for r in com if r[1]==i and r[3]}
    print(f"   {i}  {sorted(names)}")

print(f"\n=== any prodigy.net local containing 'gallegos':")
g=[ (r[1],r[0]) for r in rows if "GALLEGOS" in r[1]]
print("  ", g if g else "NONE")
