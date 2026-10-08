# Mask-clear snapshot return and deferred callback wrapper

Partial/unaccepted;102instructionbytes47ED10..47ED76,threeentries.
ED10 PUSH R4,R5,R6,LR16;R4=entryR1mask,R5=entryR0object. Fullobjectzero→5FA0A4(liveargs),ifreturnsstore0toFFFFFFFFthenED26selfloop. MaskTSTFF000000nonzero→samefatalwrite/selfloopED3A;maskzeroallowed.4420D0(liveargs);firstfreshword[object]→R6snapshot;secondindependentfreshword[object]&~mask→R4storeword[object];4420E8(liveargs). ReturnR0=firstsnapshotR6,notstoredclearedword. POP R4,R5,R6,PC restorepreservedregs.
ED52 PUSH R7,LR8;R2=entryR1,R3=0,R1=entryR0;R0=address47EE29 (ADDWalignedPCED5C+205).47EB4A(addressEE29,entryR0,entryR1,0) buildsmessage -2/address/entry0/entry1 andcalls441952withR2=0perrecoveredcontract. ReturnfullhelperR0;POP R1,PC setsR1=savedentryR7. EE29Thumbcallbacktargetnotyetrecovered.
ED64 PUSH R4,LR8;R4=entryR0;5FA0A4(liveargs);ifnormallyreturnsfreshword[entryR0]→R4;5FA0BA(liveargs);R0=R4returns. Do notassumefirsthelpernoreturn,becauselocalfallthroughread/secondhelperexists. No C/freeze/completenessclaim.
