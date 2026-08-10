import os, sys, re, html
from playwright.sync_api import sync_playwright

PROXY = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
print("using proxy:", PROXY)

def run(urls, dump=2500):
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium",
                              args=["--no-sandbox","--disable-dev-shm-usage","--ssl-version-max=tls1.2"],
                              proxy={"server": PROXY} if PROXY else None)
        ctx = b.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width":1280,"height":900}, ignore_https_errors=True)
        pg = ctx.new_page()
        for u in urls:
            print("="*70); print("URL:", u)
            try:
                r = pg.goto(u, wait_until="domcontentloaded", timeout=60000)
                print("status:", r.status if r else None)
                pg.wait_for_timeout(8000)
                print("title:", pg.title())
                t = pg.content()
                txt = re.sub(r'<script.*?</script>','',t,flags=re.S|re.I)
                txt = re.sub(r'<[^>]+>',' ',txt); txt = html.unescape(txt)
                txt = re.sub(r'\s+',' ',txt).strip()
                print("textlen:", len(txt)); print(txt[:dump])
            except Exception as e:
                print("ERR:", str(e).split("\n")[0][:200])
        b.close()

run(sys.argv[1:])
