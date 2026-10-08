# P2-21153 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x480D06..0x480D72 (108 bytes); instruction and literal-reference outputs match. The unqualified and helper-failure branches each perform the first three output12 updates, then diverge: unqualified ORs 0x10000 while failure clears it. The failure branch still uses the SP0 byte, which may be helper-written or the saved entry value. The full helper result in R0 is preserved as the return value. POP loads current SP0 into R1 and SP4 into R2 (saved entry R3 absent alias effects), then restores the 16-byte frame.
