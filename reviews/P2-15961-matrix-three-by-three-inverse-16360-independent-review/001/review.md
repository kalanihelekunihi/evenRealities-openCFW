# 15961 independent review

Status: partial; accepted: false.

Fresh replay decoded `300` original bytes at `0x561b38..0x561c64` from the locked image and passed. Exact sequence of binary32 VMUL/VMLS/VMLA computes determinant/cofactors. VABS and VCMP with literal 0x3727C5AD; VMRS updates APSR; BPL proceeds on N=0, including unordered NaN, while N=1 returns -1 before stores. Success stores all cofactors before reciprocal division and scaling, then returns R0=0. No stack/calls.

This is bounded instruction/pseudocode evidence only. Architectural FP conditions and runtime fault/reachability behavior remain unqualified. No admission or gate change.
