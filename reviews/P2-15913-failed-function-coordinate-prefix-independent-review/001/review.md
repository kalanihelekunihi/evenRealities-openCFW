# P2-15913 independent review

Fresh disassembly verifies and tiles the 66 original bytes at 0x540036..0x540078. The entry saves R3-R11/LR and reserves 184 local bytes for a 224-byte frame. It preserves entry R1/R2 in R5/R8, leaves R0 untouched, then performs four ordered stack stores at offsets 148, 156, 152, and 160 with repeated reads from the input structures and 32-bit add/subtract arithmetic.

This is only the beginning of the discovered candidate. The continuation, full ABI, return behavior, and coordinate interpretation remain open; no hardware or implementation claim follows. Status remains partial and unaccepted.
