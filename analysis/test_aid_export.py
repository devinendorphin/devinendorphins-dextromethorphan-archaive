#!/usr/bin/env python3
"""Tests for aid_export.py.

    python3 analysis/test_aid_export.py

The last four run against the live API with a deliberately invalid token: a
reply of UNAUTHENTICATED rather than GRAPHQL_VALIDATION_FAILED proves each
query parsed and validated server-side. No credential needed, and no data
leaves the machine. Everything else is offline.
"""
import json, pathlib, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import aid_export as A

fails = []
def check(name, cond, extra=""):
    print(("  ok   " if cond else "  FAIL ") + name + ("" if cond else f"  {extra}"))
    if not cond: fails.append(name)

# --- offline: renderer ----------------------------------------------------
adv = {
    "title": "Doctor Knubbins: colon test", "shortId": "abc123", "actionCount": 4,
    "tags": ["weird", "long"], "memory": "MEM TEXT", "authorsNote": "AN TEXT",
    "instructions": "INSTR TEXT", "details": "DETAILS BLOB", "gameState": {"k": 1},
    "description": "a description",
    "storyCards": [{"title": "Knubbins", "keys": "knubbins", "value": "a doctor"},
                   {"title": "Ghost", "keys": "ghost", "deletedAt": "2025-01-01"}],
    # deliberately shuffled, with one undone and one deleted
    "actionWindow": [
        {"id": "3", "text": "third", "type": "continue", "createdAt": "2025-01-03"},
        {"id": "1", "text": "first", "type": "story",    "createdAt": "2025-01-01"},
        {"id": "u", "text": "undone one", "type": "do",  "createdAt": "2025-01-02", "undoneAt": "x"},
        {"id": "2", "text": "second",  "type": "do",     "createdAt": "2025-01-02"},
        {"id": "d", "text": "deleted one", "type": "do", "createdAt": "2025-01-02", "deletedAt": "x"},
    ],
}
md = A.render_adventure(adv)
order = [md.index(t) for t in ("first", "second", "third")]
check("actions render oldest-first", order == sorted(order), order)
check("undone action excluded", "undone one" not in md)
check("deleted action excluded", "deleted one" not in md)
check("fragments are concatenated, not paragraph-split", "firstsecond" in md.replace("\n", ""))
check("memory/AN/instructions labelled", all(
    h in md for h in ("Plot Essentials / Memory", "Author's Note", "AI Instructions")))
check("unmapped fields flagged not mislabelled",
      "in-app labels unconfirmed" in md and "DETAILS BLOB" in md)
check("deleted story card excluded from render", "Ghost" not in md)
check("live story card present", "Knubbins" in md)
check("front-matter title with colon is quoted",
      '"Doctor Knubbins: colon test"' in md, md.split("---")[1])

# ordering fallback when createdAt is absent
noc = {"title": "t", "actionWindow": [{"id": "b", "text": "newest"}, {"id": "a", "text": "oldest"}]}
check("falls back to reverse without createdAt",
      A.render_adventure(noc).index("oldest") < A.render_adventure(noc).index("newest"))

# --- offline: story is a concatenation, not decorated paragraphs -------------
# Observed on adventure p8Y-OSHLzTZn 2026-08-10: `continue` fragments open with
# a space and resume mid-sentence, and `say` arrives already carrying its own
# '\n> ' formatting. So the renderer must add nothing and strip nothing. This
# supersedes the handoff spec's '> do ...' / '> say "..."' prefix convention.
frags = [
    {"id": "0", "type": "start",    "text": "{This is a test} The colors, ",
     "createdAt": "2024-05-30T22:52:27Z"},
    {"id": "1", "type": "continue", "text": "you see them shimmer.",
     "createdAt": "2024-05-30T22:53:00Z"},
    {"id": "2", "type": "say",      "text": '\n> You say "Hello."\n',
     "createdAt": "2024-05-30T22:54:00Z"},
    {"id": "3", "type": "continue", "text": "The crypt answers.",
     "createdAt": "2024-05-30T22:55:00Z"},
    {"id": "u", "type": "continue", "text": "NEVER SHOWN", "undoneAt": "x",
     "createdAt": "2024-05-30T22:56:00Z"},
]
st = A.story_text(frags)
check("mid-sentence fragments join seamlessly", "The colors, you see them shimmer." in st)
check("say keeps the app's own newline and quote", '\n> You say "Hello."\n' in st)
check("the '> ' prefix is not doubled", st.count("> You say") == 1 and "> > " not in st)
check("undone action still excluded from the join", "NEVER SHOWN" not in st)
check("story continues past the say fragment", st.rstrip().endswith("The crypt answers."))
fmd = A.render_adventure({"title": "T", "actionWindow": frags})
check("rendered story carries the joined prose", "The colors, you see them shimmer." in fmd)
# server returns ascending despite desc:true, so 'created' must be the oldest
check("front-matter created is the oldest action", '"2024-05-30T22:52:27Z"' in fmd.split("---")[1])
check("empty action list still renders", "(no visible actions)" in
      A.render_adventure({"title": "T", "actionWindow": []}))

# --- offline: details mapping (shape observed on adventure p8Y-OSHLzTZn) ------
det = {"title": "T", "details": {
    "instructions": {"type": "custom", "custom": "BE TERSE", "scenario": "SCENARIO INSTR"},
    "storySummary": "SUMMARY TEXT", "storyCardInstructions": "SC INSTR",
    "storyCardStoryInformation": "SC INFO", "brandNewFieldAIDAdded": "SURPRISE"},
    "actionWindow": [{"id": "1", "text": "hello", "type": "story", "createdAt": "2025-01-01"}]}
dmd = A.render_adventure(det)
check("details.storySummary gets its real name", "## Story Summary" in dmd and "SUMMARY TEXT" in dmd)
check("details.instructions.custom named", "## AI Instructions\n\nBE TERSE" in dmd)
check("scenario instructions kept distinct from custom",
      "AI Instructions (from scenario)" in dmd and "SCENARIO INSTR" in dmd)
check("storyCardInstructions named", "## Story Card Instructions" in dmd)
check("storyCardStoryInformation named", "## Story Card Story Information" in dmd)
# A field AID adds later must not disappear just because we do not know it yet.
check("unrecognised details key still surfaces", "not yet identified" in dmd and "SURPRISE" in dmd)
check("details no longer labelled unconfirmed", "in-app labels unconfirmed" not in dmd)

# the sample as actually observed: every value empty -> no empty headings
emptydet = {"title": "T", "gameState": None, "details": {
    "instructions": {"type": None, "custom": None, "scenario": None},
    "storySummary": "", "storyCardInstructions": "", "storyCardStoryInformation": ""},
    "actionWindow": [{"id": "1", "text": "hi", "type": "story", "createdAt": "2025-01-01"}]}
emd = A.render_adventure(emptydet)
check("all-empty details render nothing",
      "Story Summary" not in emd and "AI Instructions" not in emd and "not yet identified" not in emd)
check("null gameState renders nothing", "gameState" not in emd)
check("dig survives a non-dict mid-path", A.dig({"a": "x"}, "a.b.c") is None)
check("render_details tolerates a plain string", "```" in "".join(A.render_details("legacy")))
check("render_details tolerates None", A.render_details(None) == [])

# --- offline: slug + html -------------------------------------------------
check("slugify strips punctuation", A.slugify("Doctor Knubbins & the Love Sharks!") ==
      "doctor-knubbins-the-love-sharks", A.slugify("Doctor Knubbins & the Love Sharks!"))
check("slugify handles empty", A.slugify("") == "untitled")
check("slugify handles unicode-only", bool(A.slugify("日本語")))
check("html escapes", "<script>" not in A.md_to_html("# <script>x", "t"))

# --- offline: write layout + manifest resume ------------------------------
with tempfile.TemporaryDirectory() as td:
    out = pathlib.Path(td)
    d = out / "adventures" / "abc123__x"
    sha = A.write_item(d, adv, md, adv["storyCards"], "story", "both")
    check("raw.json written", (d / "raw.json").exists())
    check("story.md written", (d / "story.md").exists())
    check("story.html written", (d / "story.html").exists())
    check("story-cards.json written", (d / "story-cards.json").exists())
    check("raw.json is valid json", json.loads((d / "raw.json").read_text())["shortId"] == "abc123")
    check("sha is stable", sha == A.write_item(d, adv, md, adv["storyCards"], "story", "md"))

    m = A.Manifest(out / "manifest.json")
    check("unknown key not done", not m.done("adventure:abc123"))
    m.record("adventure:abc123", status="ok", sha=sha)
    check("recorded key is done", A.Manifest(out / "manifest.json").done("adventure:abc123"))
    m.record("adventure:zzz", status="failed", error="boom")
    check("failed key is not done", not A.Manifest(out / "manifest.json").done("adventure:zzz"))

    # scenario tree with scripts + nested options
    scn = {"title": "Root", "shortId": "s1", "prompt": "P", "options": [{"shortId": "s2", "title": "Opt"}],
           "gameCodeOnInput": "console.log(1)", "gameCodeSharedLibrary": "",
           "storyCards": [], "_options_expanded": [
               {"title": "Opt", "shortId": "s2", "prompt": "P2", "_options_expanded": []}]}
    sd = out / "scenarios" / "s1__root"
    A.write_scenario_tree(scn, sd, "md")
    check("scenario.md written", (sd / "scenario.md").exists())
    check("script written", (sd / "scripts" / "onInput.js").read_text() == "console.log(1)")
    check("empty script skipped", not (sd / "scripts" / "sharedLibrary.js").exists())
    check("nested option written", (sd / "options" / "s2__opt" / "scenario.md").exists())

# --- offline: field shedding ---------------------------------------------
c = A.GqlClient.__new__(A.GqlClient); c.shed = {"lastModelContext": True}
shed = c._apply_sheds("{ scenario { id lastModelContext title } }")
check("shed removes the field", "lastModelContext" not in shed and "title" in shed, shed)
check("shed finds field name in error",
      A.GqlClient._unknown_field([{"message": 'Cannot query field "foo" on type "Q".'}]) == "foo")

# --- offline: token salvage + expiry --------------------------------------
import base64, time
JWT = "eyJhbGciOiJSUzI1NiJ9.eyJleHAiOjk5OTk5OTk5OTl9.sig"
check("token: plain passthrough", A.clean_token(JWT) == JWT)
check("token: strips 'firebase ' prefix", A.clean_token("firebase " + JWT) == JWT)
check("token: strips 'Bearer ' prefix", A.clean_token("Bearer " + JWT) == JWT)
check("token: strips quotes and whitespace", A.clean_token(f'  "{JWT}" \n') == JWT)
record = json.dumps({"fbase_key": "firebase:authUser:xyz", "value": {
    "uid": "u1", "stsTokenManager": {"refreshToken": "R", "accessToken": JWT}}})
check("token: digs accessToken out of a pasted JSON record", A.clean_token(record) == JWT)
for bad, want in [("{nope", "re-copy"), ('{"a":1}', "accessToken")]:
    try:
        A.clean_token(bad); check(f"token: {bad!r} raises", False)
    except A.Fatal as e:
        check(f"token: {bad!r} fails with a usable message", want in str(e), e)

def jwt_expiring_in(seconds):
    p = base64.urlsafe_b64encode(json.dumps({"exp": int(time.time()) + seconds}).encode())
    return "h." + p.decode().rstrip("=") + ".s"

check("expiry: reads ~30 min", 29 < A.token_expiry(jwt_expiring_in(1800)) <= 30)
check("expiry: expired reads negative", A.token_expiry(jwt_expiring_in(-600)) < 0)
check("expiry: garbage returns None", A.token_expiry("not-a-jwt") is None)

# --- offline: transport diagnosis -----------------------------------------
# A broken TLS trust store is the one failure that looks like a broken tool.
# python.org's macOS build ships an unpopulated cert store, so curl works and
# Python does not; without a hint that reads as "your export is broken".
CERT_ERR = "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:1016)"
ssl_hint = A.local_network_hint(CERT_ERR)
check("cert failure names the real cause", ssl_hint and "certificate store" in ssl_hint)

# The two macOS builds need different fixes and look identical from the error
# alone. Homebrew has no Install Certificates.command, so offering it wastes a
# round trip -- which is exactly what happened on the first real run.
_prefix = sys.prefix
try:
    sys.prefix = "/usr/local/opt/python@3.14"
    brew = A.local_network_hint(CERT_ERR)
    check("homebrew detected from prefix", A.is_homebrew_python())
    # It may *name* the script to say it is absent; it must not offer the path.
    check("homebrew hint says brew, and does not offer the missing script",
          "brew install ca-certificates" in brew and "/Applications/Python" not in brew)
    check("homebrew hint warns about externally-managed pip",
          "break-system-packages" in brew)
    sys.prefix = "/Library/Frameworks/Python.framework/Versions/3.12"
    org = A.local_network_hint(CERT_ERR)
    check("python.org not flagged as homebrew", not A.is_homebrew_python())
    check("python.org hint gives the bundled script", "Certificates.command" in org)
    check("both builds offer certifi as the fallback",
          "certifi" in brew and "certifi" in org)
finally:
    sys.prefix = _prefix

# certifi must actually be consulted -- installing it does nothing unless the
# tool passes it to urllib, which was the flaw in the first round of advice.
import inspect
check("ssl_context prefers certifi when present",
      "certifi.where()" in inspect.getsource(A.ssl_context))
check("client builds an ssl context", "ssl_context()" in inspect.getsource(A.GqlClient.__init__))
check("client passes it to every request", "context=self.ssl" in inspect.getsource(A.GqlClient._post))
check("doctor uses the same path as the client", "context=ssl_context()" in inspect.getsource(A.doctor))
check("dns failure diagnosed", "DNS" in (A.local_network_hint("nodename nor servname provided") or ""))
check("timeout diagnosed", "timed out" in (A.local_network_hint("Connection timed out") or "").lower()
      or "firewall" in (A.local_network_hint("Connection timed out") or ""))
check("unknown transport error gets no bogus advice", A.local_network_hint("weird thing") is None)
check("no reason at all gets no advice", A.local_network_hint(None) is None)

# and it must fail fast rather than sleeping 5+15+45s first
class _DeadClient(A.GqlClient):
    def _post(self, q, v):
        return 0, {"errors": [{"message": "transport: [SSL: CERTIFICATE_VERIFY_FAILED] x",
                               "_reason": "[SSL: CERTIFICATE_VERIFY_FAILED] x"}]}
_tm = A.TokenManager(); _tm.token = "dummy"
_t0 = time.time()
try:
    _DeadClient(_tm, delay=0).query(A.Q_ME, {}, tag="t")
    check("cert failure raises", False)
except A.Fatal as e:
    check("cert failure fails fast, no backoff nap", time.time() - _t0 < 2, f"{time.time()-_t0:.0f}s")
    check("cert failure surfaces the reason, not just 'HTTP 0'", "CERTIFICATE_VERIFY_FAILED" in str(e))

# --- offline: masked feedback + pipe input --------------------------------
# Hidden input gives no signal, so a paste that silently failed looks exactly
# like one that worked. The fingerprint is what makes the two distinguishable.
check("mask reports length and ends", A.mask(JWT).startswith(f"{len(JWT)} chars, eyJhbGciOi"))
check("mask never shows the middle", JWT[20:40] not in A.mask(JWT))
check("mask flags something too short to be a token", "too short" in A.mask("abc"))
check("mask handles empty", A.mask("") == "(empty)")

# A pipe is spent after one read, so re-prompting would report the wrong error.
piped = A.TokenManager(from_stdin=True)
check("piped token manager will not re-prompt", not piped.can_reprompt())

check("human expiry: minutes", A.human_minutes(55) == "about 55 min")
check("human expiry: rolls over to hours", A.human_minutes(190) == "about 3 h 10 min")
check("human expiry: implausible is called out", "implausible" in A.human_minutes(999999))
check("human expiry: None passes through", A.human_minutes(None) is None)

# --- offline: saved-token reuse ------------------------------------------
with tempfile.TemporaryDirectory() as td:
    tp = pathlib.Path(td) / "tok"
    tp.write_text(jwt_expiring_in(3300))
    tm = A.TokenManager(str(tp))
    check("saved token is loaded", tm.token is not None)
    check("saved token can be reused without stdin", tm.get() is not None)
    tp.write_text(jwt_expiring_in(-900))
    check("expired saved token is discarded, not used", A.TokenManager(str(tp)).token is None)

# --- offline: every mode flag reaches its branch with its names defined -----
# --probe-search shipped referencing `client` three lines before it was
# constructed: an UnboundLocalError that no amount of query testing would find,
# because argparse wiring is not exercised by unit-testing the functions.
import unittest.mock as _mock
def _mode_runs(argv, patches):
    with _mock.patch.object(sys, "argv", ["aid_export.py"] + argv):
        with _mock.patch.multiple(A, **patches):
            try:
                A.main()
            except (NameError, UnboundLocalError) as e:
                return f"{type(e).__name__}: {e}"
            except SystemExit:
                pass
            except Exception:
                pass  # network/token failures are fine; undefined names are not
    return None

_sentinel = {"user": {"id": "u1", "username": "x"}}
for argv, patches in [
    (["--doctor"],        {"doctor": _mock.Mock(return_value=0)}),
    (["--rerender"],      {"rerender": _mock.Mock(return_value=0)}),
    (["--probe-search"],  {"with_reauth": _mock.Mock(return_value=_sentinel),
                           "probe_search": _mock.Mock(return_value=0)}),
    (["--whoami"],        {"with_reauth": _mock.Mock(return_value=_sentinel)}),
]:
    err = _mode_runs(argv, patches)
    check(f"mode {argv[0]} has all its names defined", err is None, err)

print("\n--- live query validation (dummy token; UNAUTHENTICATED == query is well-formed)")
tm = A.TokenManager(); tm.token = "dummy-token-not-real"
live = A.GqlClient(tm, delay=0.4)
for name, q, v in [
    ("Q_ME", A.Q_ME, {}),
    ("Q_SEARCH", A.Q_SEARCH, {"input": {"contentType": ["adventure"], "limit": 10, "offset": 0}}),
    ("Q_ADVENTURE", A.Q_ADVENTURE, {"shortId": "x", "limit": 2000, "offset": 0}),
    ("Q_SCENARIO", A.Q_SCENARIO, {"shortId": "x"}),
]:
    try:
        live.query(q, v, tag=name)
        check(f"{name} unexpectedly succeeded", False)
    except A.AuthExpired as e:
        check(f"{name} parses + reaches auth", "Firebase" in str(e) or "auth" in str(e).lower(), e)
    except A.Fatal as e:
        check(f"{name} parses + reaches auth", False, f"VALIDATION ERROR: {e}")

print(("\nALL PASS" if not fails else f"\n{len(fails)} FAILED: {fails}"))
sys.exit(1 if fails else 0)
