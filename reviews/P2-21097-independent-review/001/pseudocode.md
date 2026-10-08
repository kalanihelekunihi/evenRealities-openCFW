# Single-snapshot three-byte output and float-input helper pair

Partial/unaccepted;80 instruction bytes480008..480058. 0008frameless: R1=0thenliteral4801F4pointer→freshwordR1single snapshot. bits8..9→byte[entryR0+0],bits4..5→byte+1,bits0..1→byte+2,inorder. No nullguard;outputmayaliasinputword,butallfieldsderiveonecachedword. BX LR returnsfullentryR0pointer;R1low2snapshotbits,R2middle2bits.

0028 PUSH R0,R1,R2,R3,R4,LR24;R4entryoutputpointer. VSTR S0raw32bits→SP0 overwrites savedentryR0;480312(2,0,SP,liveR3). Fullhelperzero→freshSP4wordstore[R4],freshSP8wordstore[R4+4],return0;theseareinitiallysavedentryR1/R2andmaybemodifiedbyhelper,donotassumeinitializedlocals. Fullnonzero→word[R4]=0thenword[R4+4]=0,return1normalized. No nullguard;orderedloads/storespreservealiasbehavior. ADDSP16discardsentryslots,POP R4,PC releases8,total24. S0notnumericallyconverted;rawbitsstored. Externalhelpersemantics/ownership unresolved,noMMIO/C/freeze/fullcoverageclaim.
