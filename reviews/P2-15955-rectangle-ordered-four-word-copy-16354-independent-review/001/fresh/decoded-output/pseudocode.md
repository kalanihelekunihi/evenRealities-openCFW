# Ordered rectangle copy, 0x540024..0x540036

18 original bytes; partial/accepted:false. R0 destination, R1 source. No calls or stack changes.
R2=word[R1]; word[R0]=R2
R2=word[R1+4]; word[R0+4]=R2
R2=word[R1+8]; word[R0+8]=R2
R1=word[R1+12]; word[R0+12]=R1
return via LR

R0 preserved destination; finalR1 fourth loaded word, finalR2 third loaded word. Each load follows preceding store, so overlapping destination after source propagates preceding writes; this is not a snapshot copy or memmove. Flags unchanged; callee-saved and SP unchanged. Memory faults/alignment/external concurrent effects architecture dependent. No C/admission/gates.
