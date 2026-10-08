# P2-21159 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x480ED8..0x480F0C (52 bytes); instruction and literal-reference outputs match. The first frameless leaf stores the full index shifted right five before storing a 32-bit `1 << (index & 31)` mask; the store order means aliased outputs make the second store win. The next leaf loads the table pointer before checking the unsigned 224 bound, then checks the output pointer. Thus the index error takes precedence over null output, and either error returns without output writes. Table contents/ownership remain unresolved.
