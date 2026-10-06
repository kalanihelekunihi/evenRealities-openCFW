# Expanded bounds continuation, 0x540078..0x5400B8

Partial; accepted:false.64 bytes of candidate540036..5409C4, not standalone. Entry frame224 active; R5/R8 from previous prefix. Repeated ordered computations:

R2=word[SP+148];R1=SDIV(s32(word[R5+36]),2);R3=2;R2=u32(R2-R1-1);word[SP+44]=R2
R2=word[SP+156];R1=SDIV(s32(freshword[R5+36]),2);R3=2;R2=u32(R1+R2+1);word[SP+52]=R2
R2=word[SP+152];R1=SDIV(s32(freshword[R5+36]),2);R3=2;R2=u32(R2-R1-1);word[SP+48]=R2
R2=word[SP+160];R1=SDIV(s32(freshword[R5+36]),2);R3=2;R2=u32(R1+R2+1);word[SP+56]=R2
continue5400B8

Signed division truncates towardzero, unlike arithmetic shift for negative oddvalues; denominator2 nonzero. All subsequent additions/subtractions wrap32. R0 unchanged; R1/R2/R3 finalscratch as above, no child/extraSPchange. Repeatedpointee loads not collapsed. Fullfunction bounds/ABI/fault/alias/concurrency unresolved; no C/admission/gates.
