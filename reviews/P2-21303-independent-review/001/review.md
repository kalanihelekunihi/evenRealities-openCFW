# P2-21303 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482EF6..0x482F72 (124 bytes); instruction/reference outputs match. The 16-byte frame has an early alpha shortcut that returns SP0 despite no prior initialization. I verified the threshold order, the special helper path, and the alternate composite-alpha path's ASR/UDIV arithmetic and fresh alpha rereads. The first word's alpha byte is modified before the subsequent helper call; returned SP0 is then overwritten with post-alpha before the final reload. The POP aliases can return an unwritten or transformed scratch word in R1 and the entry word in R2. No higher-level blend formula is inferred.
