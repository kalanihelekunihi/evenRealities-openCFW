# P2-21125 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x4806A6..0x4806D0 (42 bytes); instruction/reference outputs match candidate. A final fresh version/state predicate conditionally stores the two literal values to table offsets 32 and 36. The callback path performs a separate nonzero test and reload before BLX, preserving the possibility of table mutation between observations. It passes current version pointer plus live R2/R3 and returns full callback R0 through R4; absence returns the initial full zero. Prior stores persist regardless of callback result. POP releases the inherited 16-byte frame. No callback/initialization contract inferred.
