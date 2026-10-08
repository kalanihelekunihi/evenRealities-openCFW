# Ordered child configuration 0x4695FE..0x46966A

Partial/unaccepted;108instructionbytes. Inherit32frame,R5originalR3,R4addressliteral469B98. R6=literal469B9C; R0=R5 ->43DE82 withliveotherargs; storeFULLresult[R6]. Call43F4C0(freshword[R6],576,288,liveR3); call43F09A(freshword[R6],0,0,liveR3); call43DFA4(freshword[R6],16,liveR2,liveR3).

R0=0 ->44104C withliveargs; R1=FULLresult,R2=0,R0=freshword[R6] ->44127E. Thenorderedcalls44129E(freshword[R6],255,0,liveR3),44131C(freshword[R6],0,0,liveR3),44146A(freshword[R6],0,0,liveR3),46916C(freshword[R6],0,0,liveR3). Eachfreshwordreloadoccursafterprecedingchild; do not substitute cachedpointer. Wrapper46916C itself reloadsonlyR0..2 foritsfourchildren.

Freshword[R6] ->R0; call43DE82 withliveR1/R2/R3; storeFULLresult[R4]. R4/R6 globaladdressesremainlive at46966A. No creation,geometry,colororconfigurationcontracts inferredfromconstants orchildnames; orderedrawcalls only. No C,freezeorwholefunctionclaim.
