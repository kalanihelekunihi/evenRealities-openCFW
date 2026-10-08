# Full-word bit-five OR helper

Partial/unaccepted; 6 instruction bytes481830..481836. Frameless helper: R0=R0 OR32, full32-bit value preserved except bit5 set; no byte truncation or conditional ASCII range handling. Non-S ORR leaves condition flags unchanged. BX LR, no memory access, no stack change. No C, freeze, whole coverage or equality claim.
