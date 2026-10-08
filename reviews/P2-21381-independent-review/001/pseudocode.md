# String tail, percent/default output and terminating NUL return

Partial/unaccepted;110 instructionbytes483F5E..483FCC continuing88-byteframe483960. Stringtailflagsbit1clear→483F7C;setconditionoldR0=R11,R11=old+1wrap,unsignedold<R7→spacecallbackR5(R0=32,R1freshSP40,R2R6,R3freshSP44),ignoredresult,R6++;repeat;failedconditionalsoincrementsR11. FreshSP48cursor++store,branch48398E.

Percent483F84callbackwithR0=37,R1freshSP40,R2R6,R3freshSP44;ignoredresult,R6++;freshcursor++store,loop. Default483F98 sameargs exceptfreshcursorbyteR0;ignoredresult,R6++;freshcursor++store,loop. End483FAEloadSP44capacity→R0;unsignedR6<R0 selectsR2=R6 elsefreshSP44reloadthenR2=capacity-1wrap (capacity0→FFFFFFFF). ReloadR3SP44,R1SP40,R0=0,BLXR5;ignorecallbackresult,R0=R6total. ADDSP52 discardslocals36 plus savedentryR0..R3 16,POP R4..R11/PC36,total88Brestore. Preserve all freshreads andcallbackevenzerocapacity; no C,freeze,wholecoverage or equalityclaim.
