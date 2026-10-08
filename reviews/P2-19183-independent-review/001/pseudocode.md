# Object tail and next guard entry 0x46A2AA..0x46A2F0

Partial/unaccepted;70instructionbytes. Previous16frameR6globaladdress:ordered44121C,44122A,441238 each(freshword[R6],0,0,liveR3). EachR0reloadfresh;lastchildFULLR0retainedthroughPOP R4/R5/R6/PC at46A2C8. Function46A18C..46A2CAends; no explicitboolreturn.

New46A2CA STMDBSP! R3/R4/R5/R6/R7/R8/R9/R10/R11/LR creates40frame. R6literal46AE70,R0freshword[R6];FULLzero branches46A2EE. NonzeroR7literal46ACD4,R0freshword[R7];FULLzero branches46A2EE. NonzeroR8literal46ACD8,R0freshword[R8];FULLnonzero branches46A2F0 outsidechunk,zero falls46A2EE. Shared46A2EEbranch46A3D2 outsidechunk. ShortcircuitguardsmeanR7/R8notinitializedonallfailurepaths; preservethatstate. No childcallsinnewentryyet. No C,freezeorwholefunctionclaim.
