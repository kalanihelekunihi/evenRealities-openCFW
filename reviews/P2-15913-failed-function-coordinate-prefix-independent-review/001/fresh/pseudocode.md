# Failed raw function coordinate preparation prefix, 0x540036..0x540078

Partial; accepted:false.66 exact original instruction bytes. This is only the entry prefix of raw discovered candidate540036..5409C4 (2446bytes), not a complete function. PUSH R3-R11/LR consumes40bytes, then SUBSP184: total224. R5=entryR1, R8=entryR2; R0 untouched in this prefix. All word reads below occur in stated order, arithmetic wraps32bits:

R2=word[R8];R1=word[R5+44];R2=u32(R1+R2);R1=freshword[R5+40];R2=u32(R2-R1);word[SP+148]=R2
R2=word[R8+8];R1=freshword[R5+44];R2=u32(R1+R2);R1=freshword[R5+40];R2=u32(R1+R2);word[SP+156]=R2
R2=word[R8+4];R1=word[R5+48];R2=u32(R1+R2);R1=freshword[R5+40];R2=u32(R2-R1);word[SP+152]=R2
R2=word[R8+12];R1=freshword[R5+48];R2=u32(R1+R2);R1=freshword[R5+40];R2=u32(R1+R2);word[SP+160]=R2
continue at540078 with224byte frame active

No validation before these reads, no childcalls or FP in prefix; stack stores and repeated loads preserve aliases/fault/order effects. Inputpointees unnamed; coordinate terminology is inferred from symmetric additions/subtractions and not a physical UI contract. The extent outside this prefix must be recovered independently:2446-66=2380bytes in raw candidate, whose discovery boundaries/semantics remain unreviewed. Raw Ghidra export failed with memory-range error; prefix itself decodes normally. No complete ABI/return/exception behavior claimed. No C/admission/freeze/gates.
