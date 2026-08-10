import sys, re, zlib, struct, subprocess, collections

def probe(item, group, mb=4):
    url = f"https://archive.org/download/{item}/{group}.mbox.zip"
    raw = subprocess.run(["curl","-sL","--max-time","180","-r",f"0-{mb*1024*1024}",url],
                         capture_output=True).stdout
    if len(raw) < 1000: return None, f"short read ({len(raw)}B)"
    if raw[:4] != b'PK\x03\x04': return None, f"not a zip prefix {raw[:4]!r}"
    nlen, elen = struct.unpack("<HH", raw[26:30])
    off = 30 + nlen + elen
    d = zlib.decompressobj(-15)
    try: data = d.decompress(raw[off:])
    except Exception as e: return None, f"inflate err {e}"
    years = re.findall(rb"^Date:.*?((?:19|20)\d\d)", data, re.M)
    hist = collections.Counter(int(y) for y in years if 1980 <= int(y) <= 2015)
    pcom = len(re.findall(rb"@prodigy\.com", data, re.I))
    return (len(data), hist, pcom), None

for spec in sys.argv[1:]:
    item, group = spec.split(":")
    r, err = probe(item, group)
    if err: print(f"{group:38s} PROBE FAIL: {err}"); continue
    n, hist, pcom = r
    early = sum(v for k,v in hist.items() if k <= 1998)
    tot = sum(hist.values())
    top = " ".join(f"{k}:{v}" for k,v in sorted(hist.items())[:8])
    print(f"{group:38s} head={n//1024}KB dates={tot} <=1998={early} pcom={pcom} | {top}")
