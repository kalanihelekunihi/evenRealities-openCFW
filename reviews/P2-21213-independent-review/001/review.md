# P2-21213 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481CF2..0x481D7A (136 bytes); instruction and literal-reference outputs match. The ITTEE paths select the cursor input, compute 8-byte alignment, store the aligned cursor before LDRD, then advance and store the cursor by eight; the raw double word is copied to SP8/SP12. Sign output checks the raw high-word sign first, then flag bit 1 for plus, then bit 0 for space, appending through SP28. Raw values and sign handling are preserved. The code then sets the prefix pointer/count and saves the raw word at SP176/SP180. Conversion `a` bypasses precision defaults; other conversions set negative precision to 6 and zero precision for `g` to 1. Floating-number semantics and later formatting remain unresolved.
