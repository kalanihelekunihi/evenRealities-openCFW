# Independent review 1819: touch extended read first phase independent review 1819

Status: **REVISE_PROSE**. Accepted: **no**.

## Checks

- Authenticated exact span [0x82E0,0x847C) has 412 bytes and 191 decoded instructions; pseudocode calls itself partial and does not claim a callable/full function.
- Revalidated all six predecessor trace receipt hashes; all correspond to the six paths pinned by this candidate.
- Manually traced 0x8352–0x83A2: after 0x812A, R6 starts at zero; loop tests count<=R6 before each step, calls 0x810C, checks the stepped candidate, increments on rejection, and on exhaustion retains the final stepped pointer. The stated “up to count times” is accurate; no-match exhaustion is not fixture-covered.
- Manually traced mirror stride at 0x8420–0x8430: the body computes ((count*copies)*(physical_width>>2))<<2, i.e. count*copies*(floor(width/4)*4). This is not generally equivalent to rounding count*copies*physical_width down to a multiple of four.

## Required correction

Clarify the mirror increment as count * copies * (physical_width rounded down to a multiple of four), matching the shift-right-before-multiply sequence. A separate later correction packet may supersede this snapshot; this report binds only to 1814/001.

## Limits

- Partial region ending at 0x847C, not callable/full recovery; function return and later phase are outside scope.
- Trace evidence is bounded; multi-copy search exhaustion and arbitrary callback mutation are untested.
- No canonical admission or C implementation.
