# Mask-clear callback, any/all predicate and deferred wrapper

Partial/unaccepted;50instructionbytes47EE28..47EE5A,threeentries.
EE28 PUSH R7,LR8;47ED10(liveargs) clearsmaskfromobjectperrecoveredcontract;POP R0,PC returnssavedentryR7,discardinginnerpreclearsnapshot. Confirms21416addressEE29ThumbentryEE28.
EE30framelessR3=entryR0word,R0=0. FullentryR2zero→TSTword,entryR1mask nonzero→R0=1 else0. FullentryR2nonzero→R3=word&mask;equalmask→R0=1 else0. Zero maskthereforeanymode0,allmode1. R1/R2unchanged,R3originalwordinanymodeorANDresultinallmode;BXLR. Resolves21410/12two predicatecallswithoutcollapsingfreshsnapshots.
EE4A PUSH R7,LR8;R3=entryR2,R2=entryR1,R1=entryR0,R0=literalEE5C.47EB4A(literal,entryR0,entryR1,entryR2) forwardsmessage -2/literal/entry0/entry1 withentryR2asqueuecallargument. ReturnfullinnerhelperR0;POP R1,PC setsR1=savedentryR7. LiteralEE5Cnotcode,referentownershipnotyetclassified. No C/freeze/completenessclaim.
