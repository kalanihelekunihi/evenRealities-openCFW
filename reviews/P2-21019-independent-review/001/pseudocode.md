# Linked-node mask matching with deferred aggregate clear

Partial/unaccepted;176instructionbytes47ED76..47EE26,twoentries.
ED76 PUSH R4,R5,R6,R7,R8,LR24;R7=entryR1,R5=0,R4=entryR0,R1=0. NullobjectorentrymaskFF000000nonzero→distinct5FA0A4/write0toFFFFFFFF/selfloopfatalbranches. Maskzeroallowed. R8=object+4,R6=object+12sentinel;454D7C(liveargs). R2=freshwordobject16head;freshwordobject0ORentrymaskstoredobject0. LoopwhileR2!=sentinel;no nullnodecheck.
EachnodeR7=freshword[node+4]next;R1=freshword[node]fullflags/mask;R0=0;R3=R1&FF000000;R1&=00FFFFFF. Flagsbit26set→freshobjectword&R1equalR1→match1;otherwise0 (zeromaskmatches). Bit26clear→freshobjectwordTSTR1nonzero→match1;otherwise0. Match:flagsbit24set→R5|=R1;freshobjectwordOR02000000→R1;45547C(node,R1,liveR2,R3). RegardlessmatchR2=savednextR7,repeat. Helperscanmutatelinksafterpreloadednext;do notre-readnextorsimplifycurrentobjectword.
Afterlistendfreshobjectword&~R5storedobject0;454DCC(liveargs);independentlyfreshobjectwordreturnedfullR0. POP R4/R5/R6/R7/R8/PC24 restoreframe. Nodeflagsandmaskremainseparate,aggregateclearafterallmatches. No loopbound/cyclehandlingrecovered.
EE1E PUSH R7,LR8;47ED76(liveargs);POP R0,PC returnsownsavedentryR7,discardinginnerobjectwordreturn. No C/freeze/completenessclaim.
