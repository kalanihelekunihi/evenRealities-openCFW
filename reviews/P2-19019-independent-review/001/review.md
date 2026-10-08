# P2-19019 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x468558–0x4685E8 (144 bytes) against the locked flash image. The isolated `instructions.json` and `references.json` match the candidate records exactly; the byte tiling covers the full interval. Candidate and fresh replay artifacts are retained here.

Semantic checks: the first diagnostic gate uses a fresh `43D0CE` result and the shifted bit test at 0x46855C; its enabled route reads `[R4]` and builds the 3-argument diagnostic call. The later gates are independent fresh reads for bit 0 and conditional bit 2. They load the first literal into R1 before a fresh `[R4]` byte read into R3, then call the diagnostic with mask `0x0C400000`. R6 is explicitly truncated in place to its low byte before the exact `== 1` route check. On the 0x4685B6 entry, each exact-one child result is tested before continuing. The final route reads a byte through the loaded pointer, stores it at SP+1, and passes SP+1 to the child; the store overlaps the earlier SP+0 diagnostic word’s bytes, as stated. No child buffer contract is inferred. The 0x4685E8 destination is outside this map and remains unresolved.

Replay used the locked image SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`. This review does not change acceptance or corpus gates.
