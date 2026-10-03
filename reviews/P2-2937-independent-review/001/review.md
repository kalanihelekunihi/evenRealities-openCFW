# Independent review 2937

**PASS_SCOPED**; `accepted` remains false.

Source and decoded ITCM hashes match inventory; declared flash bodies and candidate artifact hashes match. Isolated replay passed 1,440 fixtures. Original descending transition and rearm/delay/ITCM execute without interception. Two rank setups exercise either table A as decisive or all-zero table A followed by decisive table B; the exact memory-read ledger confirms A[new], A[old], and B[new], B[old] only on the second-table path. The 14-write result, rearm timer selection, 625 ITCM entries, incoming R3 return and R4–R11/SP/PRIMASK pass. All fixtures retain increasing/flat synthetic rank patterns, current index zero, active mode, category/comparison 3 and non-special indices. Other ranks/current indices/special paths, concurrent memory changes/aliasing, full register/flag effects and physical hardware remain unresolved.

Candidate receipt SHA-256: `c1ddca791fe9ca99f51ea942ff772c5e3d4e846cda6d45d51fa003fedd5f97ae`.
