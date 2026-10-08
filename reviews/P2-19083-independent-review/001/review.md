# P2-19083 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x46916C–0x4691BC (80 bytes; 35 instructions) and candidate instruction/reference records match exactly. Locked image SHA-256: `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

Verified both function boundaries. The first wrapper makes four ordered child calls, reloading only R0–R2 each time; R3 is live across calls, and only the fourth R0 survives its POP. The second wrapper branches on the full child result before reading byte +21, normalizes the predicate with UXTB, and its POP restores saved R7 into R1. No context-accessor contract is inferred.
