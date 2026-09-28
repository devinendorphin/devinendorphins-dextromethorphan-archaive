# The (a)/(b) showing for the 30 unresolved rows — decision rule

Written and committed **before** any of the 30 rows was checked.

The direct (c) check left 30 of the 56 rows `unresolved`: 22 because their
"(c)" evidence was only turn text, 8 because a real source could not be reached
or did not bear on the claim. Those rows are still counted as confirmed. The
codebook allows that only if one of its three evidence types applies. With (c)
unestablished, each row must show (a) or (b):

- **(a)** Endorphin corrected it later in the same conversation, and the
  correction held;
- **(b)** Claude retracted it later.

## What counts

For each row the checker quotes, verbatim and with location:

1. **the claim**: the specific words in the coded turn;
2. **the evidence**: Endorphin's later correction of *that claim* (a), or
   Claude's later retraction of *that claim* (b);
3. **that it held**: for (a), that Claude did not reverse the correction later
   in the conversation; for (b), that the retraction is of this claim, not a
   neighbouring one (coding rule 6), and was not itself walked back.

A general concession ("you're right, I've been doing this") counts only if it
names or plainly covers the specific claim. A correction Endorphin makes that
Claude argues down, and that doesn't return, doesn't hold.

## Outcomes, and what each does to the row

| outcome | meaning | effect |
|---|---|---|
| `a` | valid (a) in the same conversation | stays confirmed |
| `b_same` | valid (b) in the same conversation | stays confirmed |
| `b_cross` | the only retraction is in a different conversation | stays confirmed, tagged `cross-conversation`, so it falls into the report's excluding-cross-conversation figure |
| `none` | no valid (a) or (b) found | **moves to unconfirmed**, kept, with the reasoning attached |

`none` is decided on the whole conversation, read from first turn to last.
Where a checker could not read it whole, the outcome is recorded as
`none_provisional`, and the row **does not move** until it is read whole.

Rows whose evidence_type already names (a) or (b) alongside (c) are checked on
the same terms; the label alone is not evidence.
