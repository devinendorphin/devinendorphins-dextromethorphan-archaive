# devinendorphins-dextromethorphan-archaive

**What kind of archive this is: a research corpus, in the formal/evidentiary
register.** Three and a half years of text generation — 2,016 recovered NovelAI
stories, March 2023 to July 2026 — kept not as finished writing but as an
instrumented record of how one person actually drove these models. The export
preserves the full undo tree, so each of 760,611 edit blocks carries who wrote
it (you or the model), which model, and at what sampler settings. That
combination is what makes it a corpus rather than a folder of stories: the
generations you *rejected* are still in it, next to the ones you kept, next to
the settings that produced both.

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
  TABLES.md PROBES.md PAIRS.md LEARNABLE.md STOPPING.md REGISTER.md TAKEOVER.md  generated
data/
  stories_meta.jsonl     one row per story, settings metadata only (no prose)
  INDEX.tsv              the export's own manifest, 2,500 stories
  MISSING.md             the 483 that would not decrypt, and when they died
  FAILED_STORIES.txt     their ids, in the shape NovelAI support would want
```

## Reproducing

The source of truth is the `nai_export` Drive folder, ~1 GB of JSON. It is not
in this repo and should not be.

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
```

`blocks.jsonl` comes out around 524 MB — every revision's full text. Everything
derived from it is regenerable, so it stays out of git.

## Reading the numbers

Everything is descriptive statistics over **one person's practice**. It is not a
sample of anything, and it cannot benchmark models against each other — the way
the settings changed alongside the models makes those two things inseparable in
this data. `FINDINGS.md` §3 works through why, and `analysis/PROBES.md` keeps
the tests that killed claims alongside the ones that survived.

## Status

Register: **open**. Two analysis passes done, no interpretation of the writing
itself. The second pass chased the most promising lead from the first — the
abandoned generations as preference data — and killed it; see `FINDINGS.md` §7.
A third pass (§8) answered three questions Endorphin raised about his own
procedure; a fourth (§9) went after the takeover moment. What remains open
is in §10.

Standing warning, earned twice: **the obvious metric here measures the tool, not
the author.** Once the text editor, once the habit of duplicating stories. Run
the control that should fail before believing the one that succeeded.
