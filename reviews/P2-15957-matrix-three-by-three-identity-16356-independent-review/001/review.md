# 15957 independent review

Status: partial; accepted: false.

Fresh replay decoded `32` original bytes at `0x561810..0x561830` from the locked image and passed. VMOV.F32 S0,#1.0; store diagonal at offsets 0/16/32; MOVS R1,0 and store off-diagonals. R0 preserved, R1=0, S0=1.0, APSR N=0/Z=1 with C/V retained; BX LR.

This is bounded instruction/pseudocode evidence only. Architectural FP conditions and runtime fault/reachability behavior remain unqualified. No admission or gate change.
