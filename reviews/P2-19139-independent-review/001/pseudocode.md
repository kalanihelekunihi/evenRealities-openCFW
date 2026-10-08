# Byte enqueue leaf 0x469C26..0x469C98

Partial/unaccepted;complete114instructionbytefunction. PUSH R4/R5/R6 saves12bytes,LRunchanged,nocalls. FULLR0sourcepointerzero orlow16R1lengthzero returnsR0=NOT2=0xFFFFFFFD. OtherwiseR2=literal46A824globaladdress;freshunsignedhalf[R2+132] ->R3;R3=low16(wrapping32(128-R3));R4=low16R1. UnsignedR3<R4 returns0xFFFFFFFF;otherwiseR3index=0.

Looptest usesunsigned low16R3 < low16R1. EachiterationR4=unsignedbyte[R0+low16R3];R5=freshunsignedhalf[R2+128];storebyteR4[R2+R5] WITHOUTpre-normalizingR5. Freshunsignedhalf[R2+128] ->R4;R4=wrapping32(R4+1);R5=128;R6=SIGNEDdivideR4byR5truncatedtowardzero;R4=R4-R5*R6 viaMLS;storelow16R4[R2+128]. Freshunsignedhalf[R2+132] ->R4;increment1;storelow16[R2+132]. IncrementfullR3thenrepeatlow16test. AfterloopR0=0. SharedPOP4/5/6 thenBXLR restores12bytes.

Preservelow16wrappedcapacitycalculation, initialindexnotclampedbeforestore, orderedfreshhalfreads andsource/destaliaspossibility. Signeddivision appliedto0..65536 incrementsofreloadedhalf, yieldingremainder0..127. No globalinvariantsassumed; no C,freezeorwholecorpusclaim.
