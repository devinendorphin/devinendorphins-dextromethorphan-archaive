# AID_RUNBOOK — exporting your AI Dungeon library, step by step

Six steps. Steps 1–3 are one-time setup. **You need a desktop or laptop** — the
token has to come out of a browser's developer tools, which phones don't have.

Two rules before anything else:

- **Never paste the token into a chat, an issue, a commit, or anywhere but the
  script's own prompt.** It is a live credential — for about an hour, it *is*
  your account. Claude does not need it and should never be given it.
- **It expires in about an hour.** That is fine and expected. The export saves
  its progress continuously, so when the token dies you paste a fresh one and
  pick up exactly where you stopped. Nothing is lost and nothing is re-fetched.

---

## Step 1 — check you have Python

Open a terminal (macOS: Terminal; Windows: PowerShell; Linux: you know) and run:

```sh
python3 --version
```

**Expected:** `Python 3.9` or higher.

- `command not found` → install from python.org, then reopen the terminal.
- Windows may want `python --version` instead. If `python` works, use `python`
  everywhere below in place of `python3`.

---

## Step 2 — get the code

```sh
git clone https://github.com/devinendorphin/devinendorphins-dextromethorphan-archaive.git
cd devinendorphins-dextromethorphan-archaive
git checkout claude/ai-dungeon-text-extraction-th0xtm
```

**Expected:** a folder you are now inside. Check with:

```sh
ls analysis/aid_export.py
```

If that prints the filename, you are in the right place. If it says "No such
file", you are in the wrong directory — `cd` into the cloned folder.

No `pip install` step. There are no dependencies on purpose.

Sanity-check the tool before pointing it at your account — this needs no token
and takes a few seconds:

```sh
python3 analysis/test_aid_export.py
```

**Expected:** a list of `ok` lines ending in `ALL PASS`.

If the offline tests pass but the last four (`live query validation`) fail, the
tool is fine and your machine cannot reach the API. Go straight to Step 2a.

---

## Step 2a — check this machine can reach the API

No token needed. Do this before the token faff, not after.

```sh
python3 analysis/aid_export.py --doctor
```

**Expected:** your Python version, your certificate store, then
`OK — reachable, and the API answered as expected.`

**The common failure, on macOS specifically:**

```
FAILED to reach the API: [SSL: CERTIFICATE_VERIFY_FAILED] ...
```

This is **not** the tool and **not** AI Dungeon. Python does not use the macOS
system trust store — it goes through its own OpenSSL, which can end up pointing
at a certificate directory nobody ever populated. curl and Safari keep working
on the same machine, which is why it reads as a broken tool.

**Try this first. It is the fastest, and it cannot break anything else:**

```sh
python3 -m pip install --user --upgrade certifi
python3 analysis/aid_export.py --doctor
```

`certifi` is Mozilla's CA bundle as a plain Python package — a data file, no
compiler, no system changes. This tool prefers it over the system store whenever
it is present. Verified: with the system store deliberately emptied, certifi
alone gets the connection through. If pip refuses with
`externally-managed-environment` (Homebrew Python does this), add
`--break-system-packages`.

**Only if that fails**, fix the system store instead — and note which Python you
have, from the `build` line `--doctor` prints:

- **python.org** (`prefix=/Library/Frameworks/...`):

  ```sh
  /Applications/Python\ 3.*/Install\ Certificates.command
  ```

- **Homebrew** (`prefix=/usr/local/...` or `/opt/homebrew/...`) — there is no
  `Install Certificates.command`; that file exists only in python.org's build.

  ```sh
  brew install ca-certificates
  ```

  > **On macOS 12 or older, prefer the certifi route above.** Homebrew does not
  > support those versions, and any `brew install` may start rebuilding
  > unrelated dependencies from source — half an hour of cmake to fix a missing
  > data file. Ask first if you are not sure.

Re-run `--doctor` after any of these. **Do not continue until it says OK.**

---

## Step 3 — get your token out of the browser

**Use the Console, not the Application tab.** The IndexedDB viewer in DevTools
is genuinely bad at this — clicking around its tree tends to copy a neighbouring
cell rather than the field you aimed at, with no indication it did. Reading the
database directly avoids the whole problem.

1. On **play.aidungeon.com**, logged in, press **F12**.
2. Click the **Console** tab.
3. Chrome refuses pasted input in the console until you permit it. Type these
   two words, press Enter:

   ```
   allow pasting
   ```

4. Paste this one line, press Enter:

   ```js
const r=indexedDB.open('firebaseLocalStorageDb');r.onsuccess=e=>{const s=e.target.result.transaction('firebaseLocalStorage','readonly').objectStore('firebaseLocalStorage').getAll();s.onsuccess=()=>{const k=s.result.find(x=>String(x.fbase_key||'').includes('authUser'));const t=k&&k.value&&k.value.stsTokenManager&&k.value.stsTokenManager.accessToken;if(!t){console.log('NOT FOUND - log in to AI Dungeon first');return}copy(t);const p=JSON.parse(atob(t.split('.')[1].replace(/-/g,'+').replace(/_/g,'/')));console.log('COPIED to clipboard: '+t.length+' chars, expires '+new Date(p.exp*1000).toLocaleTimeString())}};
   ```

**Expected:**

```
COPIED to clipboard: 1160 chars, expires 4:12:38 PM
```

The token is now on your clipboard, exactly and only the token. Note that
expiry time — if it is less than about ten minutes away, run the line again
after reloading the page to get a fresh hour.

`NOT FOUND` means you are not logged in on that tab.

> This reads the same value the Application tab shows, at
> `firebase:authUser:* -> stsTokenManager -> accessToken`, and `copy()` is
> Chrome's own console helper. If you would rather click through the tree by
> hand, that path still works — but **do not** copy `refreshToken`, which sits
> next to it and is long-lived.

---

## Step 4 — prove the token works

**Easiest way, macOS — never type into the terminal at all.** Copy the token in
Chrome (Step 3), then run this. `pbpaste` hands your clipboard straight to the
script:

```sh
pbpaste | python3 analysis/aid_export.py --whoami --token-stdin
```

**Expected:**

```
  read from stdin: 912 chars, eyJhbGciOi...A3f9Qk
  token accepted, about 58 min before it expires.
  token works. Signed in as: <your username>
```

That first line is the point of it: it proves the token arrived, and how much of
it, without printing the token itself.

**The other way** is an interactive prompt:

```sh
python3 analysis/aid_export.py --whoami
```

**Nothing appears on screen while you paste — no dots, no stars, no cursor
movement.** That is deliberate, and it means a paste that failed looks exactly
like one that worked. It now prints `read: 912 chars, eyJ...` afterwards so you
can tell. If pasting does not seem to register at all, Ctrl+C and use the
`pbpaste` form above instead.

**Reading the result:**

| What it says | What to do |
|---|---|
| `token works. Signed in as: ...` | Done — go to Step 5 |
| `read from stdin: 4 chars — too short` | Clipboard had the wrong thing; redo Step 3 |
| `this token expired about N min ago` | Redo Step 3; they last about an hour |
| `expiry date is implausible` | You copied something that isn't the token |
| `the token was rejected by the API` | Usually expired. Redo Step 3 and pipe again |
| Nothing at all, no prompt, just a hang | Ctrl+C, use the `pbpaste` form |

Do not continue until it prints your username.

---

## Step 5 — export ONE adventure first

Never start with the whole library. Pick any adventure, open it in the browser,
and look at the URL:

```
https://play.aidungeon.com/adventure/AbC-123xyz/some-title
                                     ^^^^^^^^^^ this is the shortId
```

Paste the **whole URL** — the script pulls the id out itself:

```sh
python3 analysis/aid_export.py --only "https://play.aidungeon.com/adventure/AbC-123xyz/some-title" --out ./exports
```

Quote the URL, as above. Unquoted URLs with `?` in them confuse the shell.

**Expected:** a couple of progress lines, then `done: 1 exported`.

Now **actually look at what came out** — this is the step people skip:

```sh
ls exports/adventures/*/
```

You should see `raw.json`, `story.md`, and `story-cards.json`. Open `story.md`
in any text editor and read it. **Compare it against the story in the browser.**

You're checking three things:
1. The text matches, and is in the right order (oldest at the top).
2. Nothing is obviously missing from the middle.
3. If the script printed a line about `actionCount`, tell me — that means it
   fetched a different number of actions than AI Dungeon claims exist, and I
   want to see it.

If the story reads backwards, or the sections are mislabelled, stop and tell me.
Those are both things I could not verify without an account, and they are
cheap to fix once seen.

---

## Step 6 — the full run

Small batch first, to confirm enumeration finds your library at all:

```sh
python3 analysis/aid_export.py --out ./exports --limit 5
```

**Expected:** a line like `adventure: 431 reported`, then five items exported.

**That "reported" number is the one to check.** Compare it against how many
adventures you actually have. If it's roughly right, go. If it's far too low,
the search is probably only returning *published* work — that is the one open
question in this tool, tell me the number and I'll fix it.

Then the whole thing:

```sh
python3 analysis/aid_export.py --out ./exports
```

This will take a while. It paces itself at two requests a second on purpose, to
stay well clear of rate limits.

**When the token expires mid-run** — and on a large library it will — the script
stops and asks for a new one. Go do Step 3 again, paste, and it continues. You
can also just press **Ctrl+C** and walk away; re-run the same command later and
it resumes, skipping everything already done.

**Expected at the end:**

```
  done: 431 exported, 0 already had, 0 failed
  manifest: exports/manifest.json
```

Any number in `failed` — tell me which items and what the error said.

---

## Afterwards

Your export is in `exports/`. **It is not in git and should not be** — the
`.gitignore` keeps `corpus/*` out for the same reason. It's your raw archive:
back it up somewhere that isn't this laptop.

Each item has `raw.json` (the exact API response — the archival ground truth,
never edited) and `story.md` (readable). If the two ever disagree, `raw.json`
is right and the renderer has a bug.

## When something goes wrong

| What you see | What it means |
|---|---|
| `command not found: python3` | Step 1 — Python isn't installed, or try `python` |
| `No such file or directory: analysis/aid_export.py` | You're not inside the cloned folder — `cd` into it |
| Nothing appears while typing the token | Correct and intended. Paste, press Enter |
| `token rejected ... expired` | Redo Step 3, tokens last ~1 hour |
| `! that does not look like a token` | You copied the wrong field — want `accessToken`, not `refreshToken` |
| `CERTIFICATE_VERIFY_FAILED`, or the 4 live tests fail with `HTTP 0` | Step 2a — Python's cert store. `brew install ca-certificates`, or install `certifi` |
| `zsh: no matches found: /Applications/Python 3.*/...` | You have Homebrew Python; that script doesn't exist. Use `brew install ca-certificates` |
| `429 ... retrying in 5s` | Rate limited; it backs off by itself. Leave it |
| `! schema drift: dropping unknown field` | AI Dungeon changed their API. Not fatal, but tell me |
| `! <id>: actionCount=N but fetched M` | Possible paging bug. Tell me the numbers |
| It stopped and you don't know where | Just re-run the same command. It resumes |

Anything not on this list: copy the last ten lines of output and send them over.
Redact nothing except the token, which shouldn't be in the output anyway.
