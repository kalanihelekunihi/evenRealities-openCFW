# P2-21283 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482B56..0x482BCA (116 bytes); instruction/reference outputs match exactly. Both pointer guards and the comparison branch are preserved. The prepend route calls the initializer and returns its allocation result, with the zero-allocation path returning zero. The unequal path performs allocation and then the four link-helper calls in the candidate's exact order and argument registers, keeping live R3. The epilogue returns R4 in R0 and saved entry R3 in R1. Link-helper semantics and ownership are not inferred.
