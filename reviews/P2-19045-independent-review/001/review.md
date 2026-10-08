# P2-19045 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x468AE8–0x468B36 (78 bytes, 27 instructions) against locked image SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`. Candidate and fresh instruction/reference records match exactly and cover the slice.

Verified entry on the FULL non-one `4434D0` result, independent diagnostics, and zero test on retained low-byte R4 snapshot; no payload reread is implied.

Out-of-range branch targets and child contracts remain unresolved. No acceptance or corpus-gate claim is made.
