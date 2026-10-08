# P2-21009 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47EB94..0x47EBF8 (100 bytes); instruction/reference outputs match candidate. The caller-side routine keeps its fatal full-pointer and stored/reloaded size guards, initializes word 0 and byte 28=1, and its shifted POP returns stack SP0 (32 on ordinary flow). The allocation wrapper separately requests 32, initializes word 0 and byte 28=0, and returns the full allocated pointer. Initialization helper results are ignored in both paths. No allocation ownership or helper contract inferred.
