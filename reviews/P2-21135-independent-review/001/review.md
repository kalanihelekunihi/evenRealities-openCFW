# P2-21135 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x480826..0x480872 (76 bytes); instruction and literal-reference outputs match the candidate. The routine loads the fifth argument from SP+24 and applies UXTB polarity before each fresh word read. Its initial predicate test precedes the budget check; on continuation it uses the old budget, decrements modulo 2^32, and either returns status 4 or calls 0x4807A0 while ignoring that result. For positive N, at most N helper calls and N+1 reads occur. The expected value is compared full-width. The separate 0x48086A wrapper calls external 0x48 and returns saved entry R7 through R0. External target behavior remains unresolved.
