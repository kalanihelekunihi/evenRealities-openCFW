# P2-19119 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x4697EC–0x469878 (140 bytes; 53 instructions); candidate instruction/reference records match exactly. Locked image SHA-256: `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

Verified the incoming prior result is forwarded to 44127E, then ordered child calls use fresh `[R6]` loads. The later R4-based sequence stores full results at base and +4, with fresh reloads between calls. The final 43F4C0 arguments 400/30 are distinct from the earlier branch’s 484/90 and remain branch-specific raw constants; no creation/layout contract is inferred.
