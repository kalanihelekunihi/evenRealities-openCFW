# P2-21285 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482BCA..0x482C0E (68 bytes); instruction/reference outputs match. The 16-byte allocator wrapper preserves the allocation-zero early return. On nonzero allocation, endpoint links are read freshly and the two opposite-endpoint helper calls use the observed ordered argument tuples with live R3. The endpoint stores happen in the recorded order, followed by R4 in R0 and saved entry R3 in R1 at POP. No descriptor-null or helper contract is inferred.
