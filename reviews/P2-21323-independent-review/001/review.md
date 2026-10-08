# P2-21323 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x483278..0x48329C (36 bytes); instruction/reference outputs match. The seven stack arguments are stored in the observed order, including fresh word reads from SP104 and SP100 and the zero-extended byte from SP92. Entry R1/R2/R3 remain live for the 0x4830DA call. The returned R0 is retained through ADD SP,64 plus POP24, releasing the 88-byte frame.
