# Graphics mode wrapper, 0x4B0748..0x4B075E,22 bytes
PUSH entryR5,R6,R7,LR16
R2=0; word[SP+4]=0; R2=FFFFFFFF; word[SP]=R2
R3=1; R2=0; call4B06C0() //R0,R1entryarguments passed directly
POP R0,R1,R2,PC; SP+=16; return

The rewritten save slots are argument memory and outputs: normal finalR0=FFFFFFFF, R1=0, R2=entryR7. ChildR0 discarded. R5,R6,R7 were neverwritten locally and survive underchildABI; this is not a normalcallee-savePOP of those savedslots. No claim aboutchildfailure.

Partial; accepted:false. Original instruction bytes; opaque children supply return/register/memory effects. Aliasing, fault and concurrentglobal effects remain conditional; names inferred. No C, admission, freeze or gates.
