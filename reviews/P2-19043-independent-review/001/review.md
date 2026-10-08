# P2-19043 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x468A40–0x468AE8 (168 bytes, 59 instructions) against locked image SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`. Candidate and fresh instruction/reference records match exactly and cover the slice.

Verified 32-byte frame/save layout, original R1 null guard, null-route diagnostics, distinct fresh mask reads, nonnull fresh byte snapshot in R4, and FULL-result `4434D0 == 1` branch. Pointer is not assumed preserved after its register is reused.

Out-of-range branch targets and child contracts remain unresolved. No acceptance or corpus-gate claim is made.
