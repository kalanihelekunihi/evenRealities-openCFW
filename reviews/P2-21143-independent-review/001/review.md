# P2-21143 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x480A32..0x480AD4 (162 bytes); instruction and literal-reference outputs match. The mode-two path retains the distinction between a literal mask value and pointer dereferences, with separate fresh source observations and the recorded SP0 staging/reload sequence. The later word updates are separate read/modify/write operations in order (OR 1, 16, 8), followed by the helper call. The optional byte==1 branch performs its own fresh word read and masked update. Final POP loads the current SP0 scratch value into R1; it does not restore entry R3 from that slot. Other dispatch paths remain outside this candidate.
