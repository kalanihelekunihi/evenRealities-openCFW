# P2-21271 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482946..0x48297C (54 bytes); instruction and reference outputs match. The wrapper narrows the key to a byte and returns the lookup result in R0 while POP places saved R7 in R1. The initializer uses a 24-byte frame, calls the observed helper, stores descriptor fields in the listed order, conditionally selects the default literal, and loads entry arguments from SP28 before SP24. Its POP returns saved entry R3 in R0, not the fifth argument or helper result. No null or helper contracts are inferred.
