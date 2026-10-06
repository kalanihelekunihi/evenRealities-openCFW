# Packed color byte adapter, 0x4B06A8..0x4B06C0,24 bytes
PUSH entryR0/LR8. R3=UXTB(entryR1)
R2=byte[SP]; R1=byte[SP+1]; R0=byte[SP+2]; call4B15A6()
POP R1,PC; SP+=8; return
EntryR0 saved as littleendianword supplies low3bytes to child in reverseargumentorder. FinalR1 restoredentryR0, notchildR1; finalR0 childresult. Callee-saved unaffected locally.

Partial; accepted:false. Original instruction bytes; opaque children supply return/register/memory effects. Aliasing, fault and concurrentglobal effects remain conditional; names inferred. No C, admission, freeze or gates.
