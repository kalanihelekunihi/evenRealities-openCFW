# P2-21221 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481E80..0x481EE6 (102 bytes); instruction and literal-reference outputs match. The helper sequence preserves the carry branch, returned working pairs, and signed R7 checks/decrements. In the nibble loop, R0 starts at R6+7 and the code conditionally decrements R1 with flag-setting, then uses the ITTT PL block to write the low nibble at a predecremented address and arithmetic-shift R8 by four. The subsequent zero-fill loop has a distinct flag-setting decrement/test and writes zero bytes backward. Each loop is bounded by its observed signed decrement sequence (up to seven writes); nibble values are raw 0..15, with no ASCII conversion inferred. The final R6=R0+7 and signed R7 test controls repeat/fallthrough. Helper semantics and rounding continuation remain unresolved.
