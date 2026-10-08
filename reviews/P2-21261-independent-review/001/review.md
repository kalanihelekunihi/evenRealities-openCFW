# P2-21261 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x4826FC..0x48277E (130 bytes); the candidate instruction and reference outputs match exactly. The small wrapper returns saved entry R7 via POP, not the helper result. The predicate is a fresh byte comparison to FF. In the lookup, the nonzero-predicate layout uses stride-8 entries with separate terminator and key byte reads; the zero-predicate layout builds a packed-key base from the initial count and separately reloads the count in its loop. Both write the output only on a match and reload the selected value before storing it. Miss paths return zero without modifying output. No null or bounds checks beyond the observed loop guards are inferred.
