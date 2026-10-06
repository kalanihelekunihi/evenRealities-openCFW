# 15955 independent review

Status: partial; accepted: false.

Fresh replay decoded `18` original bytes at `0x540024..0x540036` from the locked image and passed. R0 destination is preserved; four ordered LDR/STR pairs with final load into R1, then BX LR. Loads after prior stores mean forward overlap can propagate earlier writes. No stack/calls; APSR unchanged.

This is bounded instruction/pseudocode evidence only. Architectural FP conditions and runtime fault/reachability behavior remain unqualified. No admission or gate change.
