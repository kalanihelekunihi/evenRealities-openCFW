# Packed-key insertion backward shift, count and bitmap return

Partial/unaccepted;70 instructionbytes482900..482946,continues48286832-byteframe. Entry R0=newbase,R1=oldkeybase,R2=fresholdcount fromprecedingpath. DecrementR2mod,initiallybranch48290E. SignedR2>=0: freshbyte[R1+R2]→R3,R7=R1+R2mod,storelowbyteR3 at[R7+4],R2--mod,repeat. Signednegative exits. Backwardbytecopy shiftskeyarray4bytes; do not assume retainedcount stability.

Freshcountbyte[R4+8]→R1,incrementmod,storelowbyteback. Independentlyreloadcount→R1,R1=R0+4*countmod;independentlyreloadcount→R2,R1+=R2mod;storelowbyteR5 at[R1-1]. Independentlyreloadcount→R1,R0+=4*countmod;storefullR6 at[R0-4]. R0=UXTB(R5),call48277E quarter-clamphelper withliveR1/R2/R3. Freshword[R4+4]→R1,R2=1;R0=R2 shiftedleft byreturnedR0 usingregistershift semantics;ORfreshR1;storebitmap[R4+4].

Commonreturn482944 POP{R0,R1,R2,R4,R5,R6,R7,PC}32bytes. TheseR0/R1/R2loadsavedentryR1/R2/R3 respectively;diagnosticpredecessorsoverwriteSP0/SP4, so returnedR0 isnothelper/allocation/statusresult. Existing-key/failure/diagnostic paths reachsamePOPwithoutinsertiontail. Preserve bytecountwrap, orderedfreshreads/stores, savedslotreturns. No C,freeze,wholecoverage or equalityclaim.
