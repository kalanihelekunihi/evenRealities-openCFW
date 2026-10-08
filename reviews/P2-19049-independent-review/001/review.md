# P2-19049 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x468BB6–0x468C24 (110 bytes, 41 instructions) against locked image SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`. Candidate and fresh instruction/reference records match exactly and cover the slice.

Verified in-place low-byte R4 test, separate fresh payload bytes for each diagnostic call, explicit byte clear before 47E58E, shared epilogue discard of saved R3 and live R0. No success constant inferred.

Out-of-range branch targets and child contracts remain unresolved. No acceptance or corpus-gate claim is made.
