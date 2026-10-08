# P2-20767 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed; image SHA-256 and source/fresh receipt hashes verified.

182B replay passes. Disassembly confirms fresh LDRB [R5,#46], LSLS #29 and BPL: bit2 clear branches to 47BAA6; bit2 set executes 4751C8 with R5+7/R4+7/16/live R3. Note a pseudocode mismatch: it says “Bit0 one calls,” but the raw test is bit2. Nonzero helper route runs diagnostic1958 then two unconditional ordered 43DACC dumps and clears R6; zero route runs diagnostic1963 and leaves R6 unchanged.

Review finding: correct the pseudocode bit test from bit0 to bit2. No source or gate files were changed.
