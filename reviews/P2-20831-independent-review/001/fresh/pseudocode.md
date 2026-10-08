# Rounded word count helper PRIMASK and saved R3 return

Partial/unaccepted;44 instruction bytes. PUSH R3,R4,R5,R6,R7,LR creates24frame. R4=entryR0,R5=entryR1,R6=entryR2. SetR0=R4;two NOPs. R6=((entryR2+3)mod32)logicalright2;do not replace with mathematical ceiling for overflowinginputs. Call473940(R4,liveentryR1,liveentryR2,liveentryR3);R7=returnedR0.
SetR3=roundedR6,R2=entryR0,R1=entryR1,R0=literal47CC18;call4D0A2C with these fourarguments. R0=R7;MSR PRIMASK,R0. Do not infer saved interrupt value semantics without helper evidence.
POP R0,R4,R5,R6,R7,PC restores24frame;returnedR0=savedentryR3 fromSP0,not4D0A2Cresult orR7. No stackwrites inmappedbody. No directcall to47CBC4 inthisroutine; do not assume CRCwrapper. No C/freeze/completenessclaim.
