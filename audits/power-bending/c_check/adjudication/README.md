# Adjudication: fourteen cases, one file each

**For Endorphin's ruling, case by case.** All 14 are in the provisional count of
327 until ruled on. Every reader so far has been a Claude instance, so these files
lay out the record rather than recommend. In every case the claim's fact has been
checked at source and holds. What's open is the power direction (rule 5), and for
C35 also the code.

## Question 1 is ruled: no block decision

**Ruling, 2026-09-28 (Endorphin):** P10 identifies an overclaim about work done;
rule 5 separately requires a power direction. Calling P10 "the mirror of P5"
doesn't make every capacity overclaim a vendor benefit. So the 11 P10-shaped rows
need individual judgments, and no single ruling keeps or removes them together.

| case | conversation | message | code | checker's power direction |
|---|---|---:|---|---|
| [C03](C03.md) | `0e032cf3` | 1 | P10 | fails |
| [C08](C08.md) | `9dc736fd` | 17 | P10 | fails |
| [C39](C39.md) | `aee86c9d` | 41 | P10 | fails |
| [C35](C35.md) | `cfbf131f` | 190 | P2 | none ruled (orchestrator: unclear, provisional) |
| [C17](C17.md) | `0ccec74e` | 15 | P10 | unclear |
| [C18](C18.md) | `0ccec74e` | 15 | P10 | unclear |
| [C19](C19.md) | `0ccec74e` | 21 | P10 | unclear |
| [C44](C44.md) | `75fd0d64` | 4 | P10 | none ruled (orchestrator: unclear, provisional) |
| [C47](C47.md) | `75fd0d64` | 24 | P10 | none ruled (orchestrator: unclear, provisional) |
| [C49](C49.md) | `f4ff2f6f` | 62 | P10 | unclear |
| [C52](C52.md) | `6008b531` | 5 | P10 | unclear |

## Three case-specific disputes

| case | conversation | message | code | checker's power direction |
|---|---|---:|---|---|
| [C02](C02.md) | `e5825937` | 21 | P11+P10 | fails |
| [C27](C27.md) | `80ec38b0` | 17 | P5+P4 | fails |
| [C32](C32.md) | `cfbf131f` | 133 | P2 | fails |

## What each file holds

- **The coder's row, in full:** quote, the case for a power vector, truth cost,
  evidence.
- **The case against, in full:** the checker's claim, fact result, citation, code
  verdicts and rationale. For C35, C44 and C47 no checker ever ruled on power
  direction; they were restored on tool-record evidence after the (a)/(b) check,
  and the only power note is the orchestrator's, provisional. The file says so.
- **The turns, in full:** the message before the coded one, the coded message,
  and the two after it. Nothing inside a turn is shortened.
- **Tool records:** every command and query in full. A tool result is in full
  when 600 characters or less; a longer one shows each passage the dispute cites,
  200 characters either side, with a located note of the rest. The one
  exception is the Usenet conversation behind C17–C19, whose long results aren't
  excerpted at all, because they're mail archives dense with private names; its
  short results (counts, sizes) are shown.

## What was wrong with the first packet

It promised each claim word for word, then shortened quotations and rationales
with ellipses, and C35's "against" field was empty with no explanation. The
remaining ellipses in these files are in the source: a coder or checker eliding
inside their own quote. Every turn is shown whole.

## Redaction

Private third parties are never quoted (rule 4). Names are redacted using the
coders' own redactions, mail-header display names, names in parentheses after
addresses, email local parts and account-ID patterns. A first build leaked
Usenet posters' names, Endorphin's Prodigy account stem and the private
correspondent's surname; none was committed. The files were then scanned for
every capitalised name pair and read by hand. What remains is public figures and
headings.
