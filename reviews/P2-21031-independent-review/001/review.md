# P2-21031 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47EF38..0x47EF74 (60 bytes); instructions and references match candidate. The 16-byte-frame routine compares a fresh global word to FFFFFFFF, conditionally calls initialization with (1, 580, 1, pointer), and then uses separate fresh global/helper full-zero tests to decide whether to clear. Initialization precedes output-pointer validation. The return is explicit 0 or 6 in R0, while POP R1 aliases saved entry R3. No status or global ownership contract is inferred.
