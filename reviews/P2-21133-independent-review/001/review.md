# P2-21133 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x4807FC..0x480826 (42 bytes); instruction and literal-reference outputs match the candidate. The initial masked word is compared with the full expected value before the budget test, so an initial match succeeds at budget zero. On mismatch, the code uses the old budget to decide whether to call the helper, decrements with 32-bit wrap, ignores the helper result, and reloads the word. Thus positive N permits up to N helper calls and N+1 observations; the expected value is not masked. The 24-byte epilogue restores saved entry R3 into R1 and returns status in R0. Helper timing/physical behavior remains unresolved.
