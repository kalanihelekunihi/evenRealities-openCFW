# Ordered initialization and wrapping times-six update pair

Partial/unaccepted;142 instruction bytes4801FC..48028A. 01FCframeless: literal4806D0pointer;freshwordclearlowbitstore,thenfullword272store samepointer (firstRMWnoteliminated). Word4806D4=256;word4806D8=FFFFFFFF;word4806DC=FFFFFFFF;word4806E0=C0000000;freshword4806E4OR40000000store. BX LRreturnsR0literal4806E4pointer,R1lastwrittenword,R2/R3unchanged. No stack/helper/PRIMASK.

0240PUSH R4,LR8;R4fullentryR0. 4C44BC(4,49,liveR2/R3),returnignored. R4*=6mod2^32,storethrough4806D8. Freshword4806E8OR8000store. Freshword4806D0OR2store;independentlyfreshsamewordAND~2store. Word4806EC=40000hex. Independentlyfreshword4806D0OR1store. POP R4,PC releases8;fullR0remainsliteral4806D0pointerreturned,notzero/status/product;R1lastwrittenword,R2literal4806ECpointer. No timing/MMIO semantics impliedbyordering/values. Pointedownership/externalhelpersemantics/C/freeze/fullcoverage unresolved/notclaimed.
