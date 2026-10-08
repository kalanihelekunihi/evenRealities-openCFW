# P2-21275 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482A12..0x482A5A (72 bytes); instruction/reference outputs match. Both helper entries pass the observed live R3 and are followed by fresh full-word reads from SP4; no copy or initialization contract is assumed. Seven distinct literal-pointer paths were checked against their targets and each loads a full word. The common ADD SP,16 plus POP of R4/PC releases the 24-byte frame while returning the current R0 value. The next predicate at 0x482A5A is outside the candidate.
