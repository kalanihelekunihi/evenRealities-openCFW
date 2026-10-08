# Zero-fill/global wrappers and allocation diagnostic/list prefix

Partial/unaccepted;96 instructionbytes484380..4843E0. 484380PUSH R7/LR8B;R2=entry1,R1=0,R0entry0,R3live;454746;POP R0(savedR7)/PC,overrideshelperresult. 48438C8BframeR0=wordliteral4849A4;4D46DE;POP R0(savedR7)/PC.

484398PUSH R5/R6/R7/LR16B;44F730withentryargs;R0nonnull→4843CE. Nullorderedstackwords literals4849AC→SP8(overwritessavedR7),4849B0→SP4(savedR6),4849B4→SP0(savedR5);R3=wordliteral4849B8,R2=84,R1=wordliteral4849BC,R0=3;44D25C. Thenloop4843C4R0=0,R1=FFFFFFFF,storeword[R1]=0,branchrepeat;actualinvalid-addressstorebehaviorretained,exceptionbehavioroutsidecandidate. Nonnull4843CER1=wordliteral4849A8;R2=freshword[R1+316];word[R0]=R2;word[R1+316]=R0;R2=freshword[R1+320]. Fallthrough4843E0unresolved. Pointerdata/helpercontractsnotinferred. No C,freeze,wholecoverage or equalityclaim.
