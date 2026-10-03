# Independent review 2641: profile derivation map

**Result: PASS_SCOPED.** `accepted` remains false.

The candidate and source pins match. The body `[0x42A550, 0x42A85E)` contains 317 contiguous instructions; all recorded instruction bytes and 16 literal words match the source. The isolated static verifier passes and derives 24 keys in the first subtraction ladder. Independent objdump decoding confirms the six nibble updates, equality targets, second-key map, error paths, and epilogue.

The unmatched paths are accurately described. The first-switch fallback at `0x42A81C` loads status 5 and branches directly to the POP at `0x42A736`, skipping the second-output store. The second-switch fallback at `0x42A85A` also loads status 5 and branches to that POP, after the first output has already been written.

This is static evidence only; first-output arithmetic per target and dynamic behavior remain open. Concurrent input changes, aliases, and ownership are unresolved. The packet remains private and unaccepted.
