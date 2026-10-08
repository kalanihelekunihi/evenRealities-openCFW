# P2-21227 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x481FD6..0x482040 (106 bytes); instruction and literal-reference outputs match. The 4D4338 return is copied to R1, and the loop uses unsigned division by ten to generate quotient/remainder pairs. Four iterations emit eight ASCII decimal digits backwards using the two byte stores and pair-counter decrements; LR is scratch but the routine has saved its entry value in the enclosing frame. R7 is reduced by eight and tested signed after R6 is set to cursor+8; the nonpositive path branches through the budget recheck. The positive path follows the recorded 4D4346, 4D4314, and 4D4354 helper return chain, including literal 0x48267C. Helper semantics remain unresolved.
