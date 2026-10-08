# P2-21093 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed; Map 0x47FFC4..0x480002 is 62 bytes. Fresh reads independently test bits 17 and 16. On rejection byte SP0==3 returns 1 without storing. Otherwise the three input bytes are OR-packed unmasked into overlapping fields; SP3 is ignored. Literal-pointer destination gets one full word; return is explicit zero.
