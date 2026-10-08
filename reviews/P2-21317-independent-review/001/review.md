# P2-21317 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x483144..0x4831C8 (132 bytes); instruction/reference outputs match. The flag-bit-4 exit, radix load at SP60, and bit-10 count adjustment match. Prefix writes test each count against the 32-byte bound and occur in the observed order for `x`/`X`/`b` followed by `0`; the ASCII marker selection is retained even for other radices when the alternate flag path reaches it. R12 is reused and clobbered by flag/prefix operations, so it no longer holds precision. No caller-level radix constraints are inferred.
