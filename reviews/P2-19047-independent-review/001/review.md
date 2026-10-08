# P2-19047 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x468B36–0x468BB6 (128 bytes, 49 instructions) against locked image SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`. Candidate and fresh instruction/reference records match exactly and cover the slice.

Verified diagnostic byte reads in +1 then +0 order, interleaved destination/source byte reads and stores, explicit byte-2 store of 1, SP+16 byte and SP+0 extra word setup, and live 465480 builder arguments.

Out-of-range branch targets and child contracts remain unresolved. No acceptance or corpus-gate claim is made.
