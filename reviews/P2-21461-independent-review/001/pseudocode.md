# Single-head status predicate and ordered helper wrappers

Partial/unaccepted. Exact 130-byte span 0x4849FC..0x484A7E. At 4849FC load owner+68; null returns zero; nonnull load head+80, return head only when status equals 1, otherwise zero. No stack frame. 484A0E..484A10 is a zero halfword between functions, retained as data/padding rather than executable behavior.

484A10 uses a 16-byte frame saving entry R3,R4,R5,LR; retain entry R0 in R4 and entry R2 in R5. Call 4D481A with R0=R4 and live incoming other registers; then call 4D4826 with R0=R4,R1=R5 and remaining registers live from first call. POP R0 restores saved entry R3 as return value.

484A26 uses the same frame, retaining entry R0/R1 in R4/R5. In order call 4D487A,4D4886,4D4862,4D486E, setting R0=R4,R1=R5 before each; R2/R3 remain live between calls. POP R0 restores entry R3.

484A4E similarly calls 4D487A then 4D4886. 484A66 similarly calls 4D4862 then 4D486E. Both restore entry R3 into R0 on return. Helper semantics and caller ABI remain unresolved; preserve call ordering and register aliases. No C, freeze, whole coverage or equality claim.
