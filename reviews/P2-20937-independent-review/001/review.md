# P2-20937 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed for the 174-byte span 0x47DE7A..0x47DF28, with two entries. Candidate and fresh instruction, pseudocode, and reference artifacts match exactly.

The first entry returns zero if 474550 returns zero. Otherwise it conditionally takes 474870's full result, always calls 4745F4, then uses signed `R5 >= 1` to retain R5 or clamp it to zero. Thus only positive signed results survive; the return is full-width and POP R1 receives the saved entry R3 slot.

The second entry calls 43C0E4 and explicitly initializes word4 to FFFFFFFF before its helper/loop. A zero 474B02 result returns FFFFFFFB (-5); a nonzero result enters the loop. 474BB8 supplies a pointer; byte `[pointer+256]` must equal 8 to reach the DE18 parser helper, otherwise the loop repeats. On parser nonzero, word0 increments with 32-bit wrap. The returned SP0 value is compared unsigned to word4 and word8 via independent loads; the SP0 reloads before each conditional store are distinct. A zero loop pointer instead reaches 474C66 and returns 0. Final POP R1 receives SP0 (which begins as saved entry R3 and may be replaced by parser state), while the other saved registers are restored.

No termination, buffer ownership, or helper contract is inferred. Candidate remains partial/unaccepted; no source or gate files changed.
