# Byte dispatch with stack record and global selector

Partial/unaccepted;150 instructionbytes48297C..482A12. PUSH{R0,R1,R2,R3,R4,LR}24bytes;R4=entryR0;R2=3,R1=0,R0=SP,call43BB00 withliveR3 (semanticsunresolved). Freshliteral482AD8 pointer→R0;freshword[R0]→R0,storeSP8(overwritessavedentryR2). R4=UXTB(currentR4).

Exactdispatch by byte:5,7→482A46;28→482A12;34→482A34;35,49,57,61,69,76,82,88,120→482A20;36,37,41,50,58,62,68,77,83,89,98,99→482A2E;52→482A3A;90→482A40;110,111→482A0C;118→482A4C;allothers→482A52. Targetsoutsidecandidateunresolved. Local482A0C freshliteral482ADCpointer→R0,freshword[R0]→R0,branch482A56. Preserveentrysavedslots/initcall/globalreadorder and full dispatch coverage; no inventedmessage meaning. No C,freeze,wholecoverage or equalityclaim.
