# Packed rectangle-command candidate, 0x522AE0..0x522B30

80 original bytes; partial/accepted:false. PushR4..R7/LR20 +local4, total24.
R6=entryR2; R4=entryR0; R5=entryR1; R7=entryR3
CMP signed R6,1; if GE: CMP signed R7,1
if resulting APSR.N!=APSR.V: goto522B2C
R0=3; call514AEC()
if R0==0: goto522B2C
R2=(R4&FFFF)|((R5<<16)&FFFF0000)
R1=260; word[R0]=R1; word[R0+4]=R2
R5=u32(R7+R5); R4=u32(R6+R4)
R2=(R4&FFFF)|((R5<<16)&FFFF0000)
R1=264; word[R0+8]=R1; word[R0+12]=R2
R1=word[0x5232CC]; word[R0+16]=R1
R2=word[0x5232D0]; R3=word[R2]; R1=word[R3+24]; R1=R1|2; word[R0+20]=R1
522B2C: SP+=4; restoreR4..R7/PC fromsavedframe; SP+=20; return

Widths/heights rejected if signedless1; compare uses conditionalIT execution, not unsigned. RejectedentryR0 retained, childNULL returns0, successR0 allocatedpointer. Literal5232CC FF000100,5232D0 20074EFC outsidecode. Allocator/output ownership/capacity/ABI and globalpointer lifetime unresolved; stores precede global reads, preserve alias/fault ordering. No exactrectangle physical qualification or C/admission/gates.
