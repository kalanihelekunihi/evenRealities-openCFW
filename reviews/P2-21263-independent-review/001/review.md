# P2-21263 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x48277E..0x4827B0 (50 bytes); instruction and reference outputs match exactly. The frameless clamp computes UXTB(input)>>2 then clamps at unsigned 31. The first wrapper calls the prior helper and returns saved entry R7 from its POP; the second performs a fresh byte 255 test, conditionally calls the descriptor routine with its observed live arguments, then calls the prior helper and returns that helper's result through its distinct POP. No null checks or allocator/release semantics are inferred.
