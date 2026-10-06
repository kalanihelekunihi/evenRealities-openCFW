# Ordered matrix translation update, 0x561856..0x5618B8

98 original bytes; partial/accepted:false. R0 matrix, entry S0=x,S1=y. No integer register writes, stack or calls. FMAC(a,b,c) below means the exact VMLA.F32 accumulator a plus b times c instruction with architectural intermediate rounding/status behavior; not an invented fused operation or unrestricted real-number formula. Ordered instructions:
S2=Fword[R0+24]; S3=Fword[R0]; S3=FMAC(S3,S0,S2); Fword[R0]=S3
S4=Fword[R0+28]; S2=Fword[R0+4]; S2=FMAC(S2,S0,S4); Fword[R0+4]=S2
S3=Fword[R0+32]; S2=Fword[R0+8]; S2=FMAC(S2,S0,S3); Fword[R0+8]=S2
S0=Fword[R0+24]; S2=Fword[R0+12]; S2=FMAC(S2,S1,S0); Fword[R0+12]=S2
S0=Fword[R0+28]; S2=Fword[R0+16]; S2=FMAC(S2,S1,S0); Fword[R0+16]=S2
S0=Fword[R0+32]; S2=Fword[R0+20]; S2=FMAC(S2,S1,S0); Fword[R0+20]=S2
return via LR

Fword load/store moves binary32 bits without integer conversion. Last row is read repeatedly and remains unwritten. EntryS0 is consumed before S0 reused for last-row values; finalS0 lastrowthird, S1 entryy, S2 finalupdatedword20, S3 lastrowthird, S4 lastrowsecond. APSR unchanged; FP status and rounding, NaNs/subnormals/overflow, architectural access/memory faults and concurrent changes remain conditional. Name inferred from operation. No C/admission/gates.
