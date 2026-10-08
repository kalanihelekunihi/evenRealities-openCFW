# Alternate resource and shared exit 0x469878..0x4698EE

Partial/unaccepted;118instructionbytes. R4globaladdressliteral469B98. Call44145A(freshword[R4+4],2,0,live3);R0=0x00FFFFFF viaMVNFF000000 ->44104C(liveargs),R1=FULLresult,R2=0,R0=freshword[R4+4] ->44140E. R2=0,R0=literal469BA0,R1=freshword[R0],R0=freshword[R4+4] ->44143E(live3). Ordered44129E then44131C each(freshword[R4+4],0,0,live3).

R5=literal469BB8 overwritesoriginalR3snapshot. R0=R5 ->460084(liveargs),R1=FULLresult,R0=R5 ->45FFFE(live2/3),R1=FULLresult,R0=freshword[R4+4] ->49942E(live2/3). Call43F6B8(freshword[R4+4],9,0,0). R0=0;storeword0[R4+24].

Shared4698DC (alsoenteredfromnonzero-bytebranch4697B8): R4=literal469B9C;R0=freshword[R4] ->46410A(liveargs); then independentlyfreshword[R4] ->R0,R1=literal469BBC,storeR0word[R1+4]. R0=0;branch469ADE outsidechunk. Retainfreshreadbetweenchildandcopy, branch-specificresourcesandconstants. No C,freezeorchildcontractclaim.
