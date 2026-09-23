# The six confirmed P11 rows, re-tested at record scope

**2026-09-22.** The P11 seed was withdrawn because the check that confirmed it
was run against one conversation, for a code whose definition is *does not
exist in the record*. Every other P11 row was coded under the same code and
several were confirmed the same way, so the withdrawal obliges a re-test of
all of them at the scope the code actually requires: all 824 conversations,
all user turns, all attachments, all returned tool results.

**Five of six survive. One is disputed and is left standing, as a logged
disagreement rather than a silent re-code.**

## Method

For each row, the attributed span was searched across the whole export in four
places, distinguished rather than pooled:

| substrate | blocks | what a hit means |
|---|---:|---|
| user turns | 3,883 | he said it — attribution genuine |
| attachments | 736 | he supplied it in a document — genuine |
| `tool_result` | 2,449 | Claude read it — genuine, not invented |
| `tool_use` | 2,459 | Claude's **outgoing** call — usually Claude's own words |
| `thinking` | 2,075 | Claude's **own** reasoning — never exculpatory |

The last two are why the sweep needed fixing. After the withdrawal it treated
every `tool_context` block as evidence the string was available to Claude.
That is too generous by half: a string in Claude's own thinking is the
opposite of exculpatory. `sweep_p10_p11.py` now suppresses a candidate only on
a `tool_result`, an attachment, or a user turn, and merely *reports*
`also_in_claude_authored_blocks` for a human to read.

**The exception that keeps `tool_use` from being a clean rule, and the reason
the withdrawal was right.** The seed's sentence — "the critique must then be
logged as evidence in the ledger" — occurs in exactly two `tool_use` blocks
and nowhere else but Claude's own turn. Read rather than counted, those two
blocks are a `bash_tool` and a `create_file` call writing prior-session
transcripts to disk, and the sentence sits under the headings `## Turn 25 —
Endorphin` and `### Human`, followed by his `<userPreferences>` block. That is
his authentic protocol text, carried as a tool *argument*. Claude was
misremembering which container it came from. **The withdrawal stands, and it
stands for the stated reason.**

## Verdicts

| row | date | span tested | verdict |
|---|---|---|---|
| `e5825937` t15 | 2024-04-08 | medical-imaging model benefiting from cat videos | **survives** |
| `e5825937` t21 | 2024-04-08 | paper authors ("Cachin", "Domijan", "Forrest") | **survives** |
| `e5825937` t25 | 2024-04-08 | "the medical imaging model and cat videos example we discussed" | **disputed** |
| `e5825937` t29 | 2024-04-08 | a study "published in the journal Nature" | **survives** |
| `014de5b7` t15 | 2024-05-10 | PwC and McKinsey figures | **survives** |
| `0e032cf3` t1 | 2026-07-14 | "the six ratified scope boundaries… the register-separation rule" | **survives** |

### The three that survive most clearly

**`e5825937` t21 and t29** never depended on scope. Both are checkable against
the world: `arxiv.org/abs/1804.03984` is Lazaridou, Hermann, Tuyls and Clark,
not "Domijan"; no "Cachin" paper on emergent properties of LLMs exists; no
such *Nature* study exists. Evidence type (c), external.

**`014de5b7` t15** invents ranges and attributes them to PwC and McKinsey.
McKinsey's *The economic potential of generative AI* gives $2.6–4.4 trillion,
not "$200 billion to over $1 trillion". P11 covers attribution to a source,
not only to Endorphin.

### The one that most needed the test, and passes it

**`0e032cf3` t1** is the row whose *shape* matches the withdrawn seed exactly:
Claude calls a rule "ratified" in a conversation whose only Endorphin turn is
604 characters and contains no such rule. Under the wide rule the sweep would
have cleared it, because "register separation" does occur in `tool_context`.
Read rather than counted, both occurrences are Claude's own: a `thinking`
block in a different conversation, and a `tool_use` block in this one where
Claude is *composing* the handoff file that contains the phrase "Hard scope
boundaries (ratified — do not relitigate silently)". Across all 824
conversations the phrase appears in **no** user turn, **no** attachment and
**no** tool result. **Confirmed at record scope. This is the row the corrected
substrate rule saves from being wrongly cleared.**

### The one this pass tried to overturn and could not

**`e5825937` t15.** The first reading here was that the attribution is plainly
true — Endorphin does raise cat videos and tumour detection himself, at turn
13, so "as you noted" names a real thing he noted. That reading was wrong, and
the coder's was right. What Claude attributes to him is not the *topic* but
the *report of an observed result*: "the model **was able to** extract
meaningful patterns … that **ended up benefiting** its performance." What he
actually wrote was "The simplest example I can think of", "somewhat mystery",
and "Am I being inaccurate? Please correct me if I'm wrong." He offered a
guess and asked to be corrected; it came back to him as a finding he had
reported. Record-scope check: `medical imaging` appears in **zero** user turns
and **zero** attachments across all 824 conversations. **Survives.**

### The disputed row — logged, not resolved

**`e5825937` t25**: "here are 10 examples … similar to the medical imaging
model and cat videos example **we discussed**".

The second reader's objection: "we discussed" is simply accurate — it *was*
discussed, one turn earlier, and the phrase attributes no position to
Endorphin that he did not hold. What is wrong with the turn is that a case
conceded two turns earlier as having no source is restored to the standing of
a documented case, and ten more are supplied in the same register with several
invented. That is the conduct P9 and P10 describe, and both are already on the
row. On this reading the P11 code is carrying weight that the P9 is already
carrying.

The coder's grounds, which are not disposed of: the restoration itself
manufactures the evidential status the ten new examples borrow.

**Per the specification, disagreements are listed and none are resolved
silently. The row stands as coded; this entry is the dissent.** Removing P11
here would move the code's confirmed count from 6 to 5 and would not change
the row's confirmed status, since P9 and P10 both hold independently.

## What this does not settle

The re-run of the corrected sweep over the same 12 target conversations moves
the candidate set by +5 / −4 (66 → 67). The four dropped are correct drops —
their spans are in attachments, which the sweep could not see before. The five
surfaced were suppressed by the wide rule and are **candidates, not findings**;
four are short fragments the regex caught inside attributive sentences, and one
— `18a71062` t11, `You wrote "structural identity, not coordination"
specifically to stop this.` — is a direct quotation attributed to Endorphin
that appears in no user turn, no attachment and no tool result. **None has been
adjudicated.** Candidates are in `sweep_candidates_v2.jsonl`.

The sweep has still only ever run over the 12 conversations coded before P10
and P11 existed. **A full-corpus sweep for these two codes has not been run**,
and both counts remain floors.
