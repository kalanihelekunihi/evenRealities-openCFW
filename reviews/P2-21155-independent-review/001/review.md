# P2-21155 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x480D72..0x480E6C (250 bytes); instruction and literal-reference outputs match. The initial null check uses the full entry pointer; selector dispatch uses UXTB. Mode 0 performs the ordered output byte writes at offsets 1, 0, and 2, then reads the source bits independently for each subsequent output byte. It invokes 0x480C7C and ignores its result. Mode 1 invokes 0x480874 with the entry pointer and also ignores its result. The common POP returns saved entry R7 in R1 absent helper alias effects. The following 4-byte zero padding is outside the mapped range.
