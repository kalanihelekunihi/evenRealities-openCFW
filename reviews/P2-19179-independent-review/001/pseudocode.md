# Ordered calls and second store 0x46A1DE..0x46A23A

Partial/unaccepted;92instructionbytes. Inherit16frame,R4literal46ACC4address,R5literal46ACC8address,R6originalR0. Call44E368(freshword[R4],0,live2/3). R0=0 ->44104C(liveargs),R1FULLresult,R2=0,R0freshword[R4] ->44127E. Call44129E(freshword[R4],255,0,live3). R0=0 ->SECOND44104C(liveargs),R1FULLsecondresult,R2=0,R0freshword[R4] ->4412EC. Ordered44131C(freshword[R4],0,0,live3),469BF4(freshword[R4],0,0,live3), retainingwrapperliveR3semantics.

R6=literal46ACCC overwritesoriginalR0snapshot. R0freshword[R4] ->43DE82(liveargs),storeFULLresult[R6]. R2freshword[R5],R1=184,R0freshword[R6] ->43F4C0(live3). R4/R5/R6globaladdressesremainliveat46A23A. Allfreshreloadsanddistinct44104Cresultforwardingspreserved; no table/layout/creationcontracts inferred. No C,freezeorwholefunctionclaim.
