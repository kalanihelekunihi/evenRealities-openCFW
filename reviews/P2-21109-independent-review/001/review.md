# P2-21109 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x48028A..0x480312 (136 bytes); instruction/reference outputs match candidate. The frameless function performs three ordered fresh word updates, computes/stores R0*6 modulo 2^32, then returns the full final word after a separate OR/store. The shutdown wrapper repeats ordered writes, ignores the helper result, performs the mapped fresh read through F8 even though R1 is then overwritten with F0, and stores 0x40000 through that pointer. Its POP R0,PC returns saved entry R7, discarding live R0. No PRIMASK or external helper semantics inferred.
