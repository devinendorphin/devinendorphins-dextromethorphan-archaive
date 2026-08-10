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

Do this in **Chrome or Edge on a desktop**. Firefox works but the panel names
differ slightly.

1. Go to **play.aidungeon.com** and make sure you are logged in.
2. Press **F12** to open DevTools. (Or right-click the page → Inspect.)
3. Click the **Application** tab along the top of the DevTools panel. If you
   don't see it, click the **»** overflow arrow — it hides when the panel is narrow.
4. In the left sidebar, find **Storage → IndexedDB**, and expand it.
5. Expand **firebaseLocalStorageDb** → click **firebaseLocalStorage**.
6. The main area shows one row. Its key starts with `firebase:authUser:`.
   Click the row to expand its value.
7. Inside, expand **stsTokenManager**, and find **accessToken**.
8. Right-click the `accessToken` **value** → Copy. It's a very long string with
   two dots in it, starting `eyJ...`.

> **If you can't isolate just that field**, copy the whole record instead — the
> script will dig the token out of pasted JSON for you and tell you it did.
> Don't fight the DevTools UI over this.

**Do not copy `refreshToken`.** That one is long-lived and this tool has no use
for it.

---

## Step 4 — prove the token works

```sh
python3 analysis/aid_export.py --whoami
```

It asks for the token. **Paste it and press Enter. Nothing will appear on
screen while you paste — no dots, no stars, nothing. That is deliberate, not a
freeze.** Paste once, hit Enter.

**Expected:**

```
  token accepted, about 58 min before it expires.
  token works. Signed in as: <your username>
    user id:  ...
    expires:  in about 58 min
```

**If it says the token expired or was rejected:** go back to Step 3 and copy it
again. The most common cause is grabbing it long before running this, or
copying `refreshToken` by mistake.

Do not continue until this step prints your username.

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
