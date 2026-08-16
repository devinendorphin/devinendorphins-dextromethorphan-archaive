# devinendorphins-dextromethorphan-archaive

**What kind of archive this is: a research corpus, in the formal/evidentiary
register.** Five and a half years of text generation — 2,016 recovered NovelAI
stories created between June 2021 and July 2026, and 888 AI Dungeon adventures
reaching back to **7 December 2020** — kept not as finished writing but as an
instrumented record of how one person actually drove these models. The export
preserves the full undo tree, so each of 760,611 edit blocks carries who wrote
it (you or the model), which model, and at what sampler settings. That
combination is what makes it a corpus rather than a folder of stories: the
generations you *rejected* are still in it, next to the ones you kept, next to
the settings that produced both.

A third archive arrived on 2026-08-12 — a Twitter/X export whose Grok chat
history is 2,818 turns with a language model, **timestamped**. It has none of the
undo tree, so almost nothing the rest of this repo measures can be run on it; it
has the one thing the NovelAI export lacks, which is a clock. What each of the
three can and cannot answer is set out in
[`analysis/TW_EXPORT.md`](analysis/TW_EXPORT.md).

A fourth arrived on 2026-08-16 — the **standalone Grok app**, 145 conversations
and 1,201 turns, which is a different record from the Grok chats inside the
Twitter export and shares not one turn with them. It is the only archive that has
both a branch structure and a clock, and the only one where the model's context
is open: web search, file attachments and cross-conversation memory are in the
input, so nothing here supports a closed-context reading.
[`analysis/GROK_EXPORT.md`](analysis/GROK_EXPORT.md) carries the four-archive
table; [`analysis/GROK.md`](analysis/GROK.md) is the measurements.

It was not made as research. It was made by playing, for years, with no thought
toward use. The claim here is that the record is analysable anyway, and that
some of what it shows is precisely what nobody was aiming at — see
[`FINDINGS.md`](FINDINGS.md).

This is emphatically *not* the harm-reduction register. Nothing here makes
claims about effects or safety, and nothing here should be read as doing so.
The name is the name.

## Layout

```
FINDINGS.md              the writeup — read this
CASE_STUDY.md            one session traced in full — the press conference
READINGS.md              criticism — ten movements, read not measured
analysis/
  fetch_export.py        mirror the Drive export locally
  extract.py             story JSON -> stories.jsonl + blocks.jsonl
  report.py              descriptive tables
  probe.py               disconfirming tests for the claims in FINDINGS
  pairs.py               build chosen/rejected pairs from branch points
  learnable.py           is there signal in the rejected text? (no)
  stopping.py            what actually ends a retry run
  register.py            rare-word vs non-word by sampler order; enter-chains
  takeover.py            what makes the author stop pressing enter and type
  cues.py                taxonomy of the author's turns, and what each buys
  erato.py               the Erato era; the border re-tested on the Unified sampler
  tempo.py               did the generation keep a beat? (lag structure of turn length)
  direction.py           who keeps it — author selection vs the model's own autocorrelation
  handover.py            what the author writes when they override the model
  handoff.py             why a bare `Name:` works — convention or scene-tracking
  trace.py               render one story's live path turn by turn
  episodes.py            OCR the Twitch dashboard; test it against story edits
  sweeps.py              recover the temperature-sweep procedure from the forks
  pasted.py              text that arrived by clipboard, not from the model
  coinage.py             is the portmanteau semantic reach or phonological collision?
  aid_export.py          bulk-export the AI Dungeon library — the other half
  test_aid_export.py     its tests; the live four need no credential
  AID_RUNBOOK.md         how to actually run it, step by step
  AID_EXPORT.md          how the undocumented list query was recovered
  tw_export.py           the Twitter/X export — the first archive with a clock
  TW_EXPORT.md           its schema, and what the three archives can't ask
  grok_export.py         the standalone Grok export — tree *and* clock
  GROK_EXPORT.md         its schema, and the four-archive asymmetry table
  terraform.py           the trans-discourse question, six runs of one prompt
  longitudinal.py        did the X-side Grok change? 2024-12 to 2026-07
  TABLES.md PROBES.md PAIRS.md LEARNABLE.md STOPPING.md
  REGISTER.md TAKEOVER.md CUES.md ERATO.md TEMPO.md
  DIRECTION.md HANDOVER.md HANDOFF.md EPISODES.md SWEEPS.md
  PASTED.md COINAGE.md TWITTER.md GROK.md
  TERRAFORMING.md LONGITUDINAL.md                           generated
corpus/cited/             the 19 documents the readings quote — see its README
data/
  stories_meta.jsonl     one row per story, settings metadata only (no prose)
  INDEX.tsv              the export's own manifest, 2,500 stories
  MISSING.md             the 483 that would not decrypt, and when they died
  FAILED_STORIES.txt     their ids, in the shape NovelAI support would want
  EPISODES.tsv           1,492 broadcasts recovered by OCR, 2020-11 to 2024-12
  twitter_meta.jsonl     one row per Grok turn, lengths only (no message text)
  TWEET_DAYS.tsv         tweets per day, 580 days — the second external clock
  grok_meta.jsonl        one row per standalone Grok turn — tree, stamps, lengths
  GROK_DAYS.tsv          standalone Grok turns per day, 97 days
```

## Reproducing

The source of truth is the `nai_export` Drive folder — **1,004 MB across 2,016
files**, plus a 524 MB `blocks.jsonl` once extracted. That does not belong in
git: GitHub blocks single files over 100 MB, and git keeps every version forever.
It is all regenerable from Drive, which is the durable copy.

The exception is [`corpus/cited/`](corpus/cited/) — the nineteen documents
`READINGS.md` and `CASE_STUDY.md` actually quote, 36 MB, committed so the
arguments can be checked without a full re-mirror. **That is not a release**; see
the note there.

```sh
python3 analysis/fetch_export.py <json-folder-id> --out corpus/json --check
python3 analysis/extract.py corpus/json --out out --with-blocks
python3 analysis/report.py out/stories.jsonl --out analysis/TABLES.md
python3 analysis/probe.py out --report analysis/PROBES.md
python3 analysis/pairs.py out --out out/pairs.jsonl --report analysis/PAIRS.md
python3 analysis/learnable.py out/pairs.jsonl --report analysis/LEARNABLE.md
python3 analysis/stopping.py out --report analysis/STOPPING.md
python3 analysis/register.py out --report analysis/REGISTER.md   # needs wordfreq
python3 analysis/takeover.py out --report analysis/TAKEOVER.md
python3 analysis/cues.py out --report analysis/CUES.md
python3 analysis/erato.py out --report analysis/ERATO.md     # needs wordfreq
python3 analysis/tempo.py out --report analysis/TEMPO.md
python3 analysis/direction.py out --report analysis/DIRECTION.md
python3 analysis/handover.py out --report analysis/HANDOVER.md
python3 analysis/handoff.py out --report analysis/HANDOFF.md
python3 analysis/episodes.py corpus/twitch \
    --out data/EPISODES.tsv --join data/stories_meta.jsonl \
    --titles data/INDEX.tsv > analysis/EPISODES.md      # needs tesseract
python3 analysis/sweeps.py data/stories_meta.jsonl --report analysis/SWEEPS.md
python3 analysis/pasted.py data/stories_meta.jsonl --report analysis/PASTED.md
python3 analysis/coinage.py corpus/cited/Finnegains_Wake_Playground_*.json \
    --report analysis/COINAGE.md                        # needs wordfreq
```

The AI Dungeon side is a separate pull, not part of the NovelAI pipeline above.
It needs a Firebase token pasted on stdin, and it needs a desktop browser to get
one. Step-by-step: [`analysis/AID_RUNBOOK.md`](analysis/AID_RUNBOOK.md). How the
undocumented list query was recovered: [`analysis/AID_EXPORT.md`](analysis/AID_EXPORT.md).

```sh
python3 analysis/aid_export.py --whoami                 # check the token first
python3 analysis/aid_export.py --only <shortId-or-URL>  # smoke test one item
python3 analysis/aid_export.py --out ./exports          # the whole library
```

The Twitter/X side is a third pull again, and a third *shape* — no undo tree, no
sampler settings, but the only per-exchange timestamps in the project. It reads
straight out of the delivered `.zip` without unpacking its 4 GB of media, and it
never opens the direct messages or the account PII:
[`analysis/TW_EXPORT.md`](analysis/TW_EXPORT.md).

```sh
python3 analysis/tw_export.py twitter-<date>-<hash>.zip --out out \
    --meta data/twitter_meta.jsonl --days data/TWEET_DAYS.tsv \
    --report analysis/TWITTER.md
```

`exports/` is gitignored for the same reason `corpus/` is: the repo is public and
the pull is raw personal archive, not a release.

`blocks.jsonl` comes out around 524 MB — every revision's full text. Everything
derived from it is regenerable, so it stays out of git.

## Two registers

`FINDINGS.md` and `analysis/` **measure**. `READINGS.md` **reads**. They are not
the same activity and are not held to the same standard: nothing in `READINGS.md`
is a finding, and no script can falsify it. Kept apart deliberately, and neither
is a substitute for the other — the corpus has had several hundred hours of
measurement and about four of reading.

## Reading the numbers

Everything is descriptive statistics over **one person's practice**. It is not a
sample of anything, and it cannot benchmark models against each other — the way
the settings changed alongside the models makes those two things inseparable in
this data. `FINDINGS.md` §11 works through why, and `analysis/PROBES.md` keeps
the tests that killed claims alongside the ones that survived.

## Status

Register: **open**. `FINDINGS.md` is written under the turn-taking frame: the
corpus records an exchange, not an authorship. Five passes went into it, and
the frame arrived last — the first four asked what made a generation good
enough to keep, and every version of that question came back null or
artifactual. §§9–11 keep those failures rather than tidying them away, because
how they failed is the most reusable thing here.

Standing warning, earned four times: **the obvious metric measures the tool,
not the author.** Once the text editor (§10a), once the habit of duplicating
stories (§10b), once `max_length` masquerading as an effect of phrasing (§2b),
once a disabled sampler read as a live setting (§6a).
Each time the tell was the same — a control matching or beating the treatment,
or a number that could not move. Run the control that should fail before
believing the one that succeeded.
