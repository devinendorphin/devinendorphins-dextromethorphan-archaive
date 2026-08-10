import os,sys,re
from playwright.sync_api import sync_playwright
PROXY=os.environ.get("HTTPS_PROXY")
pairs=[l.split("|") for l in sys.argv[1:]]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/opt/pw-browsers/chromium",
        args=["--no-sandbox","--disable-dev-shm-usage","--ssl-version-max=tls1.2"],proxy={"server":PROXY})
    pg=b.new_context(ignore_https_errors=True,viewport={"width":1400,"height":1000}).new_page()
    for grp,term in pairs:
        u=f"https://groups.google.com/g/{grp}/search?q={term}"
        try:
            pg.goto(u,wait_until="domcontentloaded",timeout=60000)
            pg.wait_for_timeout(7000)
            txt=pg.evaluate("document.body.innerText")
            if "No conversations matched" in txt:
                count="ZERO"
            else:
                m=re.search(r'\d+[–-]\d+ of (?:about )?[\d,]+',txt)
                count=m.group(0) if m else "??"
            # first result title line
            lines=[l.strip() for l in txt.split("\n") if l.strip()]
            try: i=next(i for i,l in enumerate(lines) if re.match(r'^\d+[–-]\d+ of',l) or l=="No results")
            except StopIteration: i=-1
            snippet=" | ".join(lines[i+1:i+7]) if i>=0 else " | ".join(lines[:6])
            line=(f"{grp:38s} {term:14s} -> {count:22s} {snippet[:110]}"); print(line,flush=True); open("gg_results.txt","a").write(line+"\n")
        except Exception as e:
            line=(f"{grp:38s} {term:14s} -> ERR {str(e).split(chr(10))[0][:70]}")
    b.close()
