# Flag-selected object parameter and signed scaled dimensions

Partial/unaccepted. Exact 148 instruction bytes 484BA4..484C38, continuing 32-byte frame at 484A98 with object R4. Fresh byte+36 bit0 set: call 48834C(18,2,live R2/R3); clear: call 488290(R0=18,R1 live from previous helper,R2/R3 live). Move helper result to R1 and call 4D48AA(object+76,result,live R2/R3). Set R5=32767; call 4D4A6E(object+76,32767,live R2/R3).

Compute q7 = signed_divide(signed32(wrap32(7*word[object+44]+80)),160), truncating toward zero. If signed q7<2 choose R1=1; otherwise freshly reload word+44 and repeat wrap multiply/add/signed division into R1. Call 484A26(object+76,R1,live R2/R3). That wrapper restores its entry R3 into R0; its return is ignored here.

Compute q5 analogously with multiplier5 and same +80/divisor160. Signed q5<2 chooses1; otherwise freshly reload word+44 and recompute R1. Call 4D481A(object+76,R1,live R2/R3). Then call 4D48C4(object+76,102,live R2/R3). These clamps are branch decisions with independently repeated reads, not a single cached max expression; preserve 32-bit wrapping before signed division. Frame remains open and continuation starts484C38. Helper contracts unresolved. No C, freeze, whole coverage or equality claim.
