# Independent review 2967/001

**PASS_SCOPED**; `accepted` remains false.

I reran all 3,456 original-instruction fixtures in a fresh directory. Source and caller/decoder/save-helper body pins match. Operation 3 ORs into snapshot word 0, operation 4 into word 4, and operation 6 replaces word 12; the fixture oracle preserves the condition byte derived from the initial snapshot rather than recomputing it after an OR sets a related bit. The original decoder then executes, with exact publication writes/status, R4–R12/SP and PRIMASK assertions. Replay artifacts hash-match the receipt.

Other snapshot/operation paths, aliasing/volatile changes, and physical effects remain outside scope.

Candidate receipt SHA-256: `58384a1e95863b58704df4c40d4825e9438b625c288912c82daf9e9536e47756`.
