#!/usr/bin/env python3
"""Bulk-export an AI Dungeon library: adventures, scenarios, story cards, scripts.

AI Dungeon has no first-party bulk export, and per-adventure export through the
web UI does not scale to a large library. This walks the whole thing over the
public GraphQL API and writes, per item, the verbatim API response (`raw.json`,
the archival ground truth) plus a readable Markdown render.

    python3 analysis/aid_export.py --out ./exports

The token is prompted for on stdin and never accepted as an argument, because
argv lands in shell history and a Firebase ID token is a live credential. Grab
it from DevTools -> Application -> IndexedDB -> firebaseLocalStorageDb ->
firebaseLocalStorage -> the `firebase:authUser:*` key -> `stsTokenManager.accessToken`.
It expires in about an hour; the run is resumable, so expiry costs nothing but a
re-paste.

## How the list query was found, and why that matters

The spec this was built from listed "enumerate everything the user owns" as the
one unverified piece, to be recovered by copying a request out of the browser's
Network tab. That turned out to be unnecessary. This API runs **GraphQL
validation before Firebase authentication**, so an unauthenticated probe
distinguishes a real field from a bogus one:

    { zzzNotAField }  -> HTTP 400  GRAPHQL_VALIDATION_FAILED, 'Cannot query field ...'
    { user { id } }   -> HTTP 200  UNAUTHENTICATED,           'Not authorized [Firebase]'

That is a schema oracle with no credential attached, and the server's
"Did you mean" hints enumerate neighbours for free. The whole enumeration path
below was recovered that way on 2026-08-10 and every query in this file was
validated against the live schema before a token ever existed:

    Query.user: User!                      -- no arguments; this is the "me" query
    Query.search(input: SearchInput!): SearchResults!
    SearchInput  { contentType: [String!]!   <- the only required field
                   searchTerm, sortOrder, userId, username, tags,
                   contentRating, timeRange: String
                   limit, offset: Int        <- offset/limit paging, not cursors
                   published, following: Boolean }
    SearchResults { items: [SearchableContent!]!, total, hasMore }

One correction to that spec worth flagging, because it would have produced a
query that fails validation: `SearchableContent` is a **concrete object type,
not an interface**. The `CardSearchable` fragment found in the userscript spreads
`... on Adventure` / `... on Scenario`, and doing that here is rejected outright
("objects of type SearchableContent can never be of type Adventure"). The
adventure-only and scenario-only fields are instead flat on the one type --
`actionCount` and `adventuresPlayed` sit side by side. See SEARCH_FIELDS.

Both full per-item queries from the spec were also re-validated verbatim against
the live schema: no drift, nothing shed. The field-shedding path below is a
safety net for future drift, not something currently needed.

Prior art, both MIT: the per-page queries come from the "Adventure + Scenario
Exporter" userscript by magicoflolis; the token-auth pattern and JSON output
conventions from AIDCAT (github.com/CuriousNekomimi/AIDCAT, archived 2023).

Deviation from the spec's architecture note: stdlib only, no `requests`. This
matches `fetch_export.py` next door and keeps the tool runnable anywhere without
a virtualenv.
"""

import argparse
import getpass
import hashlib
import html
import json
import os
import pathlib
import re
import stat
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

DEFAULT_HOST = "api.aidungeon.com"

# Every field on SearchableContent, recovered by probing the validation oracle.
# Flat -- do not wrap adventure/scenario-specific fields in inline fragments.
SEARCH_FIELDS = """
    id publicId shortId title description image tags contentType contentRating
    createdAt editedAt publishedAt deletedAt blockedAt published unlisted
    isOwner userId voteCount saveCount commentCount actionCount
    adventuresPlayed playerCount userJoined publishTable thirdPerson scenarioId
"""

Q_ME = "{ user { id username email isMember createdAt } }"

Q_SEARCH = """
query Enumerate($input: SearchInput!) {
  search(input: $input) {
    items { %s }
    total
    hasMore
  }
}
""" % SEARCH_FIELDS

# Verbatim from the magicoflolis userscript, re-validated against the live
# schema 2026-08-10. actionWindow is parameterised so we can page it.
Q_ADVENTURE = """
query GetAdventure($shortId: String!, $limit: Int!, $offset: Int!) {
  adventure: adventureState(shortId: $shortId) {
    id shortId scenarioId details instructions title description tags
    gameState actionCount contentType deletedAt thirdPerson memory
    authorsNote image
    actionWindow(limit: $limit, offset: $offset, desc: true) {
      imageText id text type imageUrl shareUrl adventureId decisionId
      undoneAt deletedAt createdAt
    }
    storyCards {
      id
      ... on StoryCard {
        id type keys value title useForCharacterCreation description deletedAt
      }
    }
  }
}
"""

Q_SCENARIO = """
query GetScenario($shortId: String!) {
  scenario(shortId: $shortId) {
    id shortId title description prompt memory authorsNote details image
    isOwner allowComments tags thirdPerson type contentType contentRating
    parentScenarioId
    options { id shortId title prompt parentScenarioId deletedAt }
    gameCodeSharedLibrary gameCodeOnInput gameCodeOnOutput gameCodeOnModelContext
    storyCards {
      id
      ... on StoryCard {
        id type keys value title useForCharacterCreation description deletedAt
      }
    }
  }
}
"""

SCRIPT_FIELDS = {
    "gameCodeSharedLibrary": "sharedLibrary.js",
    "gameCodeOnInput": "onInput.js",
    "gameCodeOnOutput": "onOutput.js",
    "gameCodeOnModelContext": "onModelContext.js",
}


def is_homebrew_python():
    """Homebrew installs under /usr/local (Intel) or /opt/homebrew (Apple silicon)."""
    prefix = (sys.prefix or "") + " " + (getattr(sys, "base_prefix", "") or "")
    return "/opt/homebrew" in prefix or "/usr/local/Cellar" in prefix or "/usr/local/opt" in prefix


def ssl_context():
    """Prefer certifi's CA bundle when it is installed, else the system store.

    Python does not share the OS trust store on macOS: both the python.org and
    the Homebrew builds resolve certificates through their own OpenSSL, and
    either can end up pointing at a directory that was never populated. certifi
    is Mozilla's bundle as a Python package and sidesteps the whole question --
    but installing it does nothing on its own, because stdlib urllib will not
    consult it unless asked. This asks. It stays an optional import, so the tool
    still has no required dependencies.
    """
    import ssl
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def local_network_hint(reason):
    """Turn a urllib transport failure into the actual fix, where one is known.

    The certificate case is near-universal on macOS and has two distinct causes
    that need different fixes, so the advice has to be told which one it is
    looking at rather than guessing. python.org's build ships an unpopulated
    trust store and fixes it with a bundled script. Homebrew's build resolves
    through Homebrew's OpenSSL and needs the `ca-certificates` formula, where
    that script does not exist at all. Both look identical from the error alone;
    the interpreter's own prefix is what separates them.
    """
    text = str(reason or "")
    if "CERTIFICATE_VERIFY_FAILED" in text or "SSL" in text.upper():
        head = ("  This is your Python's certificate store, not the API and not this tool.\n"
                "  curl and your browser will work while Python fails.\n")
        if is_homebrew_python():
            return head + (
                "  This is a Homebrew Python, so there is no Install Certificates.command.\n"
                "  Fix Homebrew's CA bundle:\n"
                "      brew install ca-certificates\n"
                "  If that alone does not do it, install certifi and this tool will use it:\n"
                "      python3 -m pip install --user --upgrade certifi\n"
                "      # if pip refuses with 'externally-managed-environment', add:\n"
                "      #     --break-system-packages\n"
                "  Then re-run this command."
            )
        return head + (
            "  On macOS with python.org's build, run its certificate script once:\n"
            "      /Applications/Python\\ 3.*/Install\\ Certificates.command\n"
            "  If that path does not exist, install certifi instead and this tool\n"
            "  will pick it up automatically:\n"
            "      python3 -m pip install --user --upgrade certifi\n"
            "  Then re-run this command."
        )
    if "Name or service not known" in text or "nodename nor servname" in text:
        return ("  DNS could not resolve the host. Check your connection, or whether a\n"
                "  VPN or content filter is blocking it.")
    if "Connection refused" in text or "timed out" in text.lower():
        return ("  The connection was refused or timed out. Check your connection, and\n"
                "  whether a VPN, firewall or content filter is in the way.")
    return None


class AuthExpired(Exception):
    """A 401/UNAUTHENTICATED came back mid-run; the token needs re-pasting."""


class Fatal(Exception):
    pass


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def slugify(text, limit=60):
    s = re.sub(r"[^\w\s-]", "", (text or "untitled").lower())
    s = re.sub(r"[\s_-]+", "-", s).strip("-")
    return (s[:limit].rstrip("-") or "untitled")


def clean_token(pasted):
    """Salvage a token from whatever actually got pasted.

    Copying the right thing out of DevTools is fiddly, and the three near-misses
    are predictable: the whole `firebase:authUser:*` JSON record instead of the
    one field inside it, the value with its surrounding quotes, or the value
    with the header word still attached. All three are recoverable, so recover
    them rather than failing with 'unauthorized' twenty seconds later.
    """
    tok = (pasted or "").strip()
    if tok.startswith("{"):
        try:
            blob = json.loads(tok)
        except ValueError:
            raise Fatal("that looks like JSON but will not parse — re-copy the value")
        found = None

        def walk(node):
            nonlocal found
            if found or not isinstance(node, (dict, list)):
                return
            items = node.items() if isinstance(node, dict) else enumerate(node)
            for k, v in items:
                if k == "accessToken" and isinstance(v, str) and v:
                    found = v
                    return
                walk(v)

        walk(blob)
        if not found:
            raise Fatal("no accessToken inside that JSON — copy stsTokenManager.accessToken")
        print("  (pulled accessToken out of the pasted JSON record)", file=sys.stderr)
        tok = found
    tok = tok.strip().strip('"').strip("'").strip()
    for prefix in ("firebase ", "bearer "):
        if tok.lower().startswith(prefix):
            tok = tok[len(prefix):].strip()
    return tok


def human_minutes(mins):
    """'about 48 min' / 'about 3 h 10 min'. Absurd values mean it is not a real token."""
    if mins is None:
        return None
    if abs(mins) > 60 * 24 * 30:
        return "an implausible amount of time — this is probably not a real token"
    if abs(mins) < 90:
        return f"about {mins:.0f} min"
    return f"about {int(abs(mins) // 60)} h {int(abs(mins) % 60)} min"


def token_expiry(tok):
    """Minutes left on a JWT, read locally from its payload. None if unreadable."""
    try:
        import base64
        payload = tok.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        exp = json.loads(base64.urlsafe_b64decode(payload)).get("exp")
        if not exp:
            return None
        return (datetime.fromtimestamp(exp, timezone.utc) - datetime.now(timezone.utc)).total_seconds() / 60
    except Exception:
        return None


def mask(tok):
    """A fingerprint you can eyeball without putting the token on screen."""
    if not tok:
        return "(empty)"
    if len(tok) < 24:
        return f"{len(tok)} chars — too short to be a token"
    return f"{len(tok)} chars, {tok[:10]}...{tok[-6:]}"


class TokenManager:
    """Holds the token in memory. Never reads it from argv (R7).

    argv is the one place a token must never go, because it lands in shell
    history and in `ps` output. stdin is fine, and that leaves two ways in: a
    hidden prompt, or a pipe. The pipe matters more than it looks -- typing into
    a hidden prompt gives no feedback at all, so a paste that silently failed
    is indistinguishable from one that worked, which is exactly where this got
    stuck in practice. `pbpaste | ... --token-stdin` never touches the keyboard.
    """

    def __init__(self, path=None, from_stdin=False):
        self.path = pathlib.Path(path).expanduser() if path else None
        self.from_stdin = from_stdin
        self.token = None
        if self.path and self.path.exists():
            self.token = self.path.read_text().strip() or None
            if self.token:
                left = token_expiry(self.token)
                if left is not None and left <= 0:
                    # Saying so now beats a puzzling rejection on the first request.
                    print(f"  ! saved token in {self.path} expired {human_minutes(-left)} ago",
                          file=sys.stderr)
                    self.token = None
                elif left is not None:
                    print(f"  using saved token from {self.path}, {human_minutes(left)} left",
                          file=sys.stderr)

    def can_reprompt(self):
        """Is there an interactive human to ask again? A pipe is spent after one read."""
        return not self.from_stdin and sys.stdin.isatty()

    def get(self):
        if not self.token:
            self.prompt()
        return self.token

    def prompt(self, reason=None):
        if reason:
            print(f"\n  {reason}", file=sys.stderr)

        # Piped in (`pbpaste | ... --token-stdin`), or stdin is not a terminal
        # at all, in which case there is nobody to prompt.
        if self.from_stdin or not sys.stdin.isatty():
            raw = sys.stdin.read()
            if not raw.strip():
                raise Fatal(
                    "no token arrived on stdin.\n"
                    "  On macOS, copy the token in Chrome, then run:\n"
                    "      pbpaste | python3 analysis/aid_export.py --whoami --token-stdin"
                )
            tok = clean_token(raw)
            print(f"  read from stdin: {mask(tok)}", file=sys.stderr)
        else:
            print(
                "\n  Paste your AI Dungeon token, then press Enter.\n"
                "  DevTools -> Application -> IndexedDB -> firebaseLocalStorageDb ->\n"
                "  firebaseLocalStorage -> the firebase:authUser:* key ->\n"
                "  stsTokenManager -> accessToken.\n"
                "\n  NOTE: nothing appears on screen while you paste -- no dots, no stars.\n"
                "  That is normal. Paste once, then press Enter.\n"
                "  If pasting into the terminal will not work, Ctrl+C and pipe it instead:\n"
                "      pbpaste | python3 analysis/aid_export.py --whoami --token-stdin",
                file=sys.stderr,
            )
            tok = clean_token(getpass.getpass("  token: "))
            print(f"  read: {mask(tok)}", file=sys.stderr)
        if not tok:
            raise Fatal("no token given — nothing was read")
        if tok.count(".") != 2:
            print("  ! that does not look like a token (expected two dots). Trying it anyway.",
                  file=sys.stderr)
        left = token_expiry(tok)
        if left is not None:
            if abs(left) > 60 * 24 * 30:
                print("  ! this token's expiry date is implausible — it is probably not a real "
                      "AI Dungeon token. Trying it anyway.", file=sys.stderr)
            elif left <= 0:
                print(f"  ! this token expired {human_minutes(-left)} ago — grab a fresh one.",
                      file=sys.stderr)
            else:
                print(f"  token accepted, {human_minutes(left)} before it expires.", file=sys.stderr)
        self.token = tok
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(tok)
            os.chmod(self.path, stat.S_IRUSR | stat.S_IWUSR)
            print(f"  saved to {self.path} (0600)", file=sys.stderr)


class GqlClient:
    """POST wrapper: auth headers, pacing, backoff, re-auth, field-shedding."""

    def __init__(self, tokens, host=DEFAULT_HOST, delay=0.5, verbose=False):
        self.tokens = tokens
        self.url = f"https://{host}/graphql"
        self.delay = delay
        self.verbose = verbose
        self.shed = {}
        self._last = 0.0
        self.ssl = ssl_context()

    def _pace(self):
        wait = self.delay - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.monotonic()

    def _post(self, query, variables):
        self._pace()
        body = json.dumps({"query": query, "variables": variables or {}}).encode()
        req = urllib.request.Request(
            self.url,
            data=body,
            headers={
                "Accept": "application/graphql-response+json, application/json, multipart/mixed",
                "authorization": f"firebase {self.tokens.get()}",
                "content-type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=120, context=self.ssl) as r:
                return r.status, json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            raw = e.read()
            try:
                return e.code, json.loads(raw or b"{}")
            except ValueError:
                return e.code, {"errors": [{"message": raw[:400].decode("utf8", "replace")}]}
        except urllib.error.URLError as e:
            return 0, {"errors": [{"message": f"transport: {e.reason}", "_reason": e.reason}]}

    def query(self, query, variables=None, tag=""):
        query = self._apply_sheds(query)
        backoff = [5, 15, 45]
        attempt = 0
        while True:
            status, payload = self._post(query, variables)
            errors = payload.get("errors") or []
            codes = {(e.get("extensions") or {}).get("code") for e in errors}

            if not errors and "data" in payload:
                return payload["data"]

            if status in (401, 403) or "UNAUTHENTICATED" in codes:
                raise AuthExpired(errors[0].get("message") if errors else "unauthorized")

            detail = errors[0].get("message") if errors else f"HTTP {status}"

            # A broken TLS trust store or an unresolvable host is a machine
            # configuration problem: it will fail identically in 45 seconds, so
            # say what is wrong instead of napping three times first.
            if status == 0:
                hint = local_network_hint(errors[0].get("_reason") if errors else None)
                if hint:
                    raise Fatal(f"{tag}: {detail}\n{hint}")

            if status == 429 or 500 <= status < 600 or status == 0:
                if attempt < len(backoff):
                    nap = backoff[attempt]
                    attempt += 1
                    print(f"  ! {tag} {detail} — retrying in {nap}s", file=sys.stderr)
                    time.sleep(nap)
                    continue
                raise Fatal(f"{tag}: giving up after backoff — {detail}")

            missing = self._unknown_field(errors)
            if missing:
                if len(self.shed) >= 5:
                    raise Fatal(f"{tag}: too many schema mismatches, last: {missing}")
                print(f"  ! schema drift: dropping unknown field {missing!r}", file=sys.stderr)
                self.shed[missing] = True
                query = self._apply_sheds(query)
                continue

            raise Fatal(f"{tag}: {errors[0].get('message') if errors else payload}")

    @staticmethod
    def _unknown_field(errors):
        for e in errors:
            m = re.search(r'Cannot query field "([^"]+)"', e.get("message", ""))
            if m:
                return m.group(1)
        return None

    def _apply_sheds(self, query):
        for field in self.shed:
            query = re.sub(rf"(?m)^\s*{re.escape(field)}\s*$", "", query)
            query = re.sub(rf"(?<![\w.]){re.escape(field)}(?![\w(:])", "", query)
        return query


def with_reauth(client, fn, *a, **kw):
    """Run fn, and on token expiry prompt for a fresh token and run it again.

    Only when there is someone to prompt. A piped token cannot be re-read --
    stdin is already at EOF -- so retrying there would replace a true "your
    token was rejected" with a misleading "nothing arrived on stdin".
    """
    while True:
        try:
            return fn(*a, **kw)
        except AuthExpired as e:
            if not client.tokens.can_reprompt():
                # A piped token cannot be replaced in place, but nothing is lost:
                # the manifest has every completed item, so re-running the same
                # command with a fresh token resumes rather than restarts.
                raise Fatal(
                    f"the token was rejected by the API: {e}\n"
                    "  It has most likely expired — they last about an hour.\n"
                    "\n  Your progress is saved. Nothing needs re-fetching.\n"
                    "  Reload play.aidungeon.com, copy a fresh token (Step 3), then run\n"
                    "  the SAME command again — it picks up where it stopped."
                )
            client.tokens.token = None
            client.tokens.prompt(f"token rejected ({e}) -- it has probably expired.")


class Manifest:
    """exports/manifest.json -- makes any abort cheap (R6)."""

    def __init__(self, path):
        self.path = pathlib.Path(path)
        self.data = {}
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text())
            except ValueError:
                print(f"  ! unreadable manifest at {self.path}, starting fresh", file=sys.stderr)

    def done(self, key):
        return self.data.get(key, {}).get("status") == "ok"

    def record(self, key, **fields):
        self.data[key] = {"fetched_at": now(), **fields}
        self.save()

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(self.data, indent=2, sort_keys=True))
        tmp.replace(self.path)


def enumerate_library(client, kinds, user_id=None, username=None, page=100, limit=None):
    """Every item the authenticated user owns, via the discovered search query."""
    seen = {}
    for kind in kinds:
        offset, total = 0, None
        while True:
            spec = {"contentType": [kind], "limit": page, "offset": offset}
            if user_id:
                spec["userId"] = user_id
            if username:
                spec["username"] = username
            data = with_reauth(
                client, client.query, Q_SEARCH, {"input": spec}, tag=f"search {kind}"
            )
            res = data.get("search") or {}
            items = res.get("items") or []
            if total is None:
                total = res.get("total")
                print(f"  {kind}: {total if total is not None else '?'} reported", file=sys.stderr)
            for it in items:
                sid = it.get("shortId")
                if sid and sid not in seen:
                    seen[sid] = it
            offset += len(items)
            print(f"    ...{len(seen)} collected", end="\r", file=sys.stderr)
            if not items or not res.get("hasMore") or (limit and len(seen) >= limit):
                break
        print(file=sys.stderr)
    return list(seen.values())


def fetch_adventure(client, short_id, page_size=2000):
    """Base record plus the full action history, paged (§1.3 note, R2)."""
    first = with_reauth(
        client, client.query, Q_ADVENTURE,
        {"shortId": short_id, "limit": page_size, "offset": 0}, tag=f"adventure {short_id}",
    )
    adv = first.get("adventure")
    if not adv:
        raise Fatal(f"adventure {short_id}: empty response")

    pages = [adv.get("actionWindow") or []]
    actions = list(pages[0])
    expected = adv.get("actionCount")

    while len(pages[-1]) == page_size:
        nxt = with_reauth(
            client, client.query, Q_ADVENTURE,
            {"shortId": short_id, "limit": page_size, "offset": len(actions)},
            tag=f"adventure {short_id} +{len(actions)}",
        )
        window = ((nxt.get("adventure") or {}).get("actionWindow")) or []
        if not window:
            break
        known = {a.get("id") for a in actions}
        fresh = [a for a in window if a.get("id") not in known]
        if not fresh:
            break
        pages.append(window)
        actions.extend(fresh)
        print(f"    {short_id}: {len(actions)} actions", end="\r", file=sys.stderr)

    adv["actionWindow"] = actions
    # R4: raw.json stays complete; _pages preserves the original boundaries so
    # the paging can be audited after the fact.
    adv["_pages"] = [len(p) for p in pages]
    adv["_fetched_at"] = now()
    if expected is not None and len(actions) != expected:
        adv["_action_count_mismatch"] = {"actionCount": expected, "fetched": len(actions)}
        print(
            f"  ! {short_id}: actionCount={expected} but fetched {len(actions)}",
            file=sys.stderr,
        )
    return adv


def fetch_scenario(client, short_id, visited=None):
    """Scenario plus its option tree, recursively. Cycle-safe (§1.3 note)."""
    visited = visited if visited is not None else set()
    if short_id in visited:
        return None
    visited.add(short_id)

    data = with_reauth(
        client, client.query, Q_SCENARIO, {"shortId": short_id}, tag=f"scenario {short_id}"
    )
    scn = data.get("scenario")
    if not scn:
        raise Fatal(f"scenario {short_id}: empty response")
    scn["_fetched_at"] = now()

    children = []
    for opt in scn.get("options") or []:
        osid = opt.get("shortId")
        if not osid:
            continue
        child = fetch_scenario(client, osid, visited)
        if child:
            children.append(child)
    scn["_options_expanded"] = children
    return scn


# --- rendering -------------------------------------------------------------
#
# The spec was firm that the plot-component mapping should be read off a real
# response rather than guessed, so this does not guess. `memory`, `authorsNote`
# and `instructions` are rendered under the names AI Dungeon's own UI uses for
# them. `details` and `gameState` are the two whose in-app labels are not
# established here, so they are dumped verbatim under a clearly provisional
# heading instead of being silently mislabelled. Confirm against one real
# raw.json and promote them into PLOT_SECTIONS when you know.

PLOT_SECTIONS = [
    ("memory", "Plot Essentials / Memory"),
    ("authorsNote", "Author's Note"),
    ("instructions", "AI Instructions"),
]
PLOT_UNMAPPED = ["details", "gameState"]

ACTION_PREFIX = {"do": "> ", "say": "> ", "see": "> "}


def chronological(actions):
    """Oldest first.

    The query asks for desc:true, so the fetch order should be newest-first and
    a reverse would do. Sorting on createdAt instead means the render is right
    whichever way the server actually ordered it -- the spec flagged that
    ordering as needing empirical confirmation, and this sidesteps needing it.
    """
    if actions and all(a.get("createdAt") for a in actions):
        return sorted(actions, key=lambda a: a["createdAt"])
    return list(reversed(actions))


def front_matter(fields):
    out = ["---"]
    for k, v in fields.items():
        if v in (None, "", [], {}):
            continue
        if isinstance(v, list):
            v = ", ".join(str(x) for x in v)
        out.append(f"{k}: {json.dumps(v) if isinstance(v, str) and ':' in v else v}")
    out.append("---")
    return "\n".join(out)


def render_adventure(adv):
    md = [front_matter({
        "title": adv.get("title") or "Untitled",
        "shortId": adv.get("shortId"),
        "scenarioId": adv.get("scenarioId"),
        "created": (adv.get("actionWindow") or [{}])[-1].get("createdAt"),
        "actionCount": adv.get("actionCount"),
        "tags": adv.get("tags"),
        "contentType": adv.get("contentType"),
        "deletedAt": adv.get("deletedAt"),
    }), ""]
    md.append(f"# {adv.get('title') or 'Untitled'}\n")
    if adv.get("description"):
        md.append(f"*{adv['description'].strip()}*\n")

    for key, heading in PLOT_SECTIONS:
        val = (adv.get(key) or "").strip() if isinstance(adv.get(key), str) else adv.get(key)
        if val:
            md.append(f"## {heading}\n\n{val}\n")

    provisional = {k: adv.get(k) for k in PLOT_UNMAPPED if adv.get(k)}
    if provisional:
        md.append("## Other plot fields (in-app labels unconfirmed)\n")
        for k, v in provisional.items():
            body = v if isinstance(v, str) else json.dumps(v, indent=2)
            md.append(f"**`{k}`**\n\n```\n{body}\n```\n")

    cards = [c for c in (adv.get("storyCards") or []) if not c.get("deletedAt")]
    if cards:
        md.append(f"## Story Cards ({len(cards)})\n")
        for c in cards:
            keys = c.get("keys") or ""
            md.append(f"- **{c.get('title') or c.get('type') or 'card'}**"
                      f"{f' — `{keys}`' if keys else ''}"
                      f"{chr(10) + '  ' + (c.get('value') or '').strip() if c.get('value') else ''}")
        md.append("")

    md.append("## Story\n")
    shown = 0
    for act in chronological(adv.get("actionWindow") or []):
        # R5/§3: undone and deleted actions stay in raw.json, out of the render.
        if act.get("undoneAt") or act.get("deletedAt"):
            continue
        text = (act.get("text") or "").strip("\n")
        if not text.strip():
            continue
        shown += 1
        md.append(ACTION_PREFIX.get(act.get("type"), "") + text.strip() + "\n")
    if not shown:
        md.append("*(no visible actions)*\n")
    return "\n".join(md)


def render_scenario(scn):
    md = [front_matter({
        "title": scn.get("title") or "Untitled",
        "shortId": scn.get("shortId"),
        "type": scn.get("type"),
        "contentType": scn.get("contentType"),
        "contentRating": scn.get("contentRating"),
        "tags": scn.get("tags"),
        "parentScenarioId": scn.get("parentScenarioId"),
    }), ""]
    md.append(f"# {scn.get('title') or 'Untitled'}\n")
    if scn.get("description"):
        md.append(f"*{scn['description'].strip()}*\n")
    if scn.get("prompt"):
        md.append(f"## Prompt\n\n{scn['prompt'].strip()}\n")
    for key, heading in PLOT_SECTIONS:
        if scn.get(key):
            md.append(f"## {heading}\n\n{str(scn[key]).strip()}\n")
    if scn.get("details"):
        md.append(f"## Other plot fields (in-app labels unconfirmed)\n\n"
                  f"**`details`**\n\n```\n{scn['details']}\n```\n")

    cards = [c for c in (scn.get("storyCards") or []) if not c.get("deletedAt")]
    if cards:
        md.append(f"## Story Cards ({len(cards)})\n")
        for c in cards:
            keys = c.get("keys") or ""
            md.append(f"- **{c.get('title') or c.get('type') or 'card'}**"
                      f"{f' — `{keys}`' if keys else ''}")
        md.append("")

    opts = scn.get("options") or []
    if opts:
        md.append(f"## Options ({len(opts)})\n")
        for o in opts:
            flag = " *(deleted)*" if o.get("deletedAt") else ""
            md.append(f"- **{o.get('title') or 'Untitled'}** — `{o.get('shortId')}`{flag}")
        md.append("")

    scripts = [n for f, n in SCRIPT_FIELDS.items() if (scn.get(f) or "").strip()]
    if scripts:
        md.append("## Scripts\n\n" + "\n".join(f"- `scripts/{n}`" for n in scripts) + "\n")
    return "\n".join(md)


def md_to_html(md, title):
    """Deliberately minimal -- raw.json and the Markdown are the real outputs."""
    body = []
    for block in md.split("\n\n"):
        b = block.strip()
        if not b or b == "---":
            continue
        if b.startswith("#"):
            lvl = len(b) - len(b.lstrip("#"))
            body.append(f"<h{lvl}>{html.escape(b.lstrip('#').strip())}</h{lvl}>")
        elif b.startswith("> "):
            body.append(f"<blockquote>{html.escape(b[2:])}</blockquote>")
        else:
            body.append(f"<p>{html.escape(b)}</p>")
    return (
        "<!doctype html><meta charset=utf-8>"
        f"<title>{html.escape(title)}</title>"
        "<style>body{max-width:42em;margin:3em auto;padding:0 1em;"
        "font:16px/1.6 Georgia,serif}blockquote{color:#555;border-left:3px solid #ccc;"
        "margin:0;padding-left:1em}</style>\n" + "\n".join(body)
    )


def write_item(out_dir, raw, rendered, story_cards, name, fmt, scripts=None):
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_text = json.dumps(raw, indent=2, ensure_ascii=False)
    (out_dir / "raw.json").write_text(raw_text, encoding="utf8")
    if fmt in ("md", "both"):
        (out_dir / f"{name}.md").write_text(rendered, encoding="utf8")
    if fmt in ("html", "both"):
        (out_dir / f"{name}.html").write_text(
            md_to_html(rendered, raw.get("title") or name), encoding="utf8"
        )
    if story_cards:
        (out_dir / "story-cards.json").write_text(
            json.dumps(story_cards, indent=2, ensure_ascii=False), encoding="utf8"
        )
    for field, fname in (scripts or {}).items():
        code = (raw.get(field) or "").strip()
        if code:
            sdir = out_dir / "scripts"
            sdir.mkdir(exist_ok=True)
            (sdir / fname).write_text(code, encoding="utf8")
    return hashlib.sha256(raw_text.encode("utf8")).hexdigest()[:16]


def write_scenario_tree(scn, out_dir, fmt):
    """Scenario plus its options nested underneath, mirroring §3's layout."""
    children = scn.pop("_options_expanded", [])
    sha = write_item(
        out_dir, scn, render_scenario(scn), scn.get("storyCards"),
        "scenario", fmt, scripts=SCRIPT_FIELDS,
    )
    for child in children:
        sub = out_dir / "options" / f"{child.get('shortId')}__{slugify(child.get('title'))}"
        write_scenario_tree(child, sub, fmt)
    return sha


def doctor(host=DEFAULT_HOST):
    """Can this machine talk to the API at all? Runs before any token exists.

    Exploits the same property the enumeration was built on: the server
    validates the GraphQL document before it checks the Firebase token, so an
    unauthenticated request that comes back UNAUTHENTICATED proves the whole
    network path works. No credential involved, nothing sent but a literal.
    """
    print(f"\n  python      {sys.version.split()[0]}  ({sys.platform})")
    try:
        import ssl
        print(f"  openssl     {ssl.OPENSSL_VERSION}")
        paths = ssl.get_default_verify_paths()
        store = paths.cafile or paths.capath
        exists = bool(store) and pathlib.Path(store).exists()
        kind = "file" if paths.cafile else "dir"
        print(f"  ca store    {store or '(none configured)'}  [{kind}]"
              f"{'' if exists else '   <-- MISSING'}")
        if paths.capath and not paths.cafile:
            print("              (a directory, no cert.pem — this is the usual cause)")
        print(f"  build       {'Homebrew' if is_homebrew_python() else 'python.org / system'}"
              f"   prefix={sys.prefix}")
        try:
            import certifi
            print(f"  certifi     installed — using {certifi.where()}")
        except ImportError:
            print("  certifi     not installed (optional; would override the store above)")
    except Exception as e:
        print(f"  ssl         unavailable: {e}")

    print(f"  endpoint    https://{host}/graphql")
    req = urllib.request.Request(
        f"https://{host}/graphql", data=b'{"query":"{__typename}"}',
        headers={"content-type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30, context=ssl_context()) as r:
            payload = json.loads(r.read() or b"{}")
        code = ((payload.get("errors") or [{}])[0].get("extensions") or {}).get("code")
        if code == "UNAUTHENTICATED":
            print("\n  OK — reachable, and the API answered as expected.")
            print("  Next: python3 analysis/aid_export.py --whoami")
            return 0
        print(f"\n  Reached it, but got an unexpected reply: {str(payload)[:200]}")
        return 1
    except urllib.error.HTTPError as e:
        print(f"\n  Reached it. HTTP {e.code} — unexpected, but the network path works.")
        return 1
    except urllib.error.URLError as e:
        print(f"\n  FAILED to reach the API: {e.reason}\n")
        print(local_network_hint(e.reason) or
              "  Unrecognised network error. Compare against:\n"
              f"      curl -sS -X POST https://{host}/graphql "
              "-H 'content-type: application/json' -d '{\"query\":\"{__typename}\"}'\n"
              "  If curl works and this does not, it is Python's config, not the network.")
        return 2


def main():
    ap = argparse.ArgumentParser(
        description="Bulk-export an AI Dungeon library to JSON + Markdown.",
        epilog="The token is read from stdin only, never from the command line.",
    )
    ap.add_argument("--out", default="exports", help="output directory (default: exports)")
    ap.add_argument("--host", default=DEFAULT_HOST, help=f"GraphQL host (default: {DEFAULT_HOST})")
    ap.add_argument("--delay", type=float, default=0.5, help="seconds between requests")
    ap.add_argument("--page-size", type=int, default=2000, help="actionWindow page size")
    ap.add_argument("--search-page", type=int, default=100, help="enumeration page size")
    ap.add_argument("--only", action="append", metavar="SHORTID",
                    help="fetch just this item (repeatable); accepts a play.aidungeon.com URL")
    ap.add_argument("--kind", choices=["adventure", "scenario", "both"], default="both")
    ap.add_argument("--format", choices=["md", "html", "both", "none"], default="md")
    ap.add_argument("--limit", type=int, help="stop after N items (for a trial run)")
    ap.add_argument("--save-token", metavar="PATH", nargs="?", const="~/.aid_token",
                    help="persist the token to PATH, chmod 0600 (default off)")
    ap.add_argument("--force", action="store_true", help="re-fetch items already done")
    ap.add_argument("--whoami", action="store_true",
                    help="check the token works and exit — run this first")
    ap.add_argument("--token-stdin", action="store_true",
                    help="read the token from a pipe instead of prompting, e.g. "
                         "pbpaste | %(prog)s --whoami --token-stdin")
    ap.add_argument("--doctor", action="store_true",
                    help="check this machine can reach the API. No token needed")
    args = ap.parse_args()

    if args.doctor:
        return doctor(args.host)

    out = pathlib.Path(args.out)
    tokens = TokenManager(args.save_token, from_stdin=args.token_stdin)
    client = GqlClient(tokens, host=args.host, delay=args.delay)

    if args.whoami:
        user = (with_reauth(client, client.query, Q_ME, tag="user") or {}).get("user") or {}
        print(f"\n  token works. Signed in as: {user.get('username') or '(no username)'}")
        print(f"    user id:  {user.get('id')}")
        print(f"    email:    {user.get('email')}")
        print(f"    member:   {user.get('isMember')}")
        left = token_expiry(tokens.token)
        if left is not None:
            print(f"    expires:  in {human_minutes(left)}")
        print("\n  Next: python3 analysis/aid_export.py --only <shortId> --out ./exports")
        return 0

    manifest = Manifest(out / "manifest.json")

    targets = []
    if args.only:
        for spec in args.only:
            m = re.search(r"(?:^|/)(adventure|scenario)/([^/?#]+)", spec)
            if m:
                targets.append({"shortId": m.group(2), "contentType": m.group(1), "title": None})
            else:
                targets.append({"shortId": spec, "contentType": None, "title": None})
    else:
        me = with_reauth(client, client.query, Q_ME, tag="user")
        user = me.get("user") or {}
        print(f"  authenticated as {user.get('username') or user.get('id')}", file=sys.stderr)
        kinds = ["adventure", "scenario"] if args.kind == "both" else [args.kind]
        targets = enumerate_library(
            client, kinds, user_id=user.get("id"),
            page=args.search_page, limit=args.limit,
        )

    if args.limit:
        targets = targets[: args.limit]
    print(f"  {len(targets)} item(s) to export -> {out}", file=sys.stderr)

    ok = skipped = failed = 0
    for i, item in enumerate(targets, 1):
        sid = item["shortId"]
        kind = item.get("contentType")
        key = f"{kind or 'item'}:{sid}"
        if manifest.done(key) and not args.force:
            skipped += 1
            continue
        label = (item.get("title") or sid)[:48]
        print(f"  [{i}/{len(targets)}] {kind or '?'} {sid} — {label}", file=sys.stderr)
        try:
            if kind == "scenario":
                scn = fetch_scenario(client, sid)
                d = out / "scenarios" / f"{sid}__{slugify(scn.get('title'))}"
                sha = write_scenario_tree(scn, d, args.format)
                title, deleted = scn.get("title"), scn.get("deletedAt")
            else:
                # Unknown kind is treated as an adventure; --only on a bare id
                # is nearly always an adventure, and a wrong guess just errors.
                adv = fetch_adventure(client, sid, page_size=args.page_size)
                d = out / "adventures" / f"{sid}__{slugify(adv.get('title'))}"
                sha = write_item(d, adv, render_adventure(adv), adv.get("storyCards"),
                                 "story", args.format)
                title, deleted = adv.get("title"), adv.get("deletedAt")
                kind = kind or "adventure"
                key = f"{kind}:{sid}"
            manifest.record(key, status="ok", type=kind, title=title, sha=sha,
                            path=str(d), deleted=bool(deleted))
            ok += 1
        except Fatal as e:
            print(f"  ! FAILED {sid}: {e}", file=sys.stderr)
            manifest.record(key, status="failed", type=kind, error=str(e))
            failed += 1
        except KeyboardInterrupt:
            manifest.save()
            print(f"\n  interrupted — {ok} done, rerun to resume", file=sys.stderr)
            return 130

    manifest.save()
    deleted = sum(1 for v in manifest.data.values() if v.get("deleted"))
    print(f"\n  done: {ok} exported, {skipped} already had, {failed} failed", file=sys.stderr)
    if deleted:
        print(f"  {deleted} item(s) carry deletedAt — kept and flagged, not skipped (R1)",
              file=sys.stderr)
    print(f"  manifest: {out / 'manifest.json'}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Fatal as e:
        print(f"  fatal: {e}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        sys.exit(130)
