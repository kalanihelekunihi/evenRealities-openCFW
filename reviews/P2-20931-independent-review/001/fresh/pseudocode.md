# Conditional helper dispatch and saved-stack-word returns

Partial/unaccepted;74instructionbytes47DD62..47DDAC,threeentries.
DD62 PUSH R7,LR8;443484(liveentryargs). Fullresultnonzero: R0=0 thenSP0=0 overwrites savedR7;R3=0,R2=2000,R1=4;R0=freshword[pointerliteral47E28C];47E7B0(R0,4,2000,0) withstackwordSP0=0. ThenPOP R0,PC returnsSP0 (zero absent callee mutation),not calleeR0. Fullfirstresultzero:448F98(liveargs),thenPOP R0,PC returns savedentryR7 subjectto helperstackeffects. No boolean normalization of firsthelper result.
DD8A PUSH R7,LR8;callDD62(liveargs);POP R0,PC returns this outer savedentryR7,discarding innerreturn. Stackframes remain distinct; innerSP0zero doesnot overwriteouterSP0 under ordinary local writes.
DD92 PUSH R7,LR8;R0=freshword[pointerliteral47E28C]. Ifzero skip allwrites/helpercalls. OtherwiseR0=0,R1=literal47E290 pointer;storeword0there thencallDD62withliveargs. POP R0,PC returns own savedentryR7,discarding helperreturn. Preserve write-before-call and no entryR0parameter retention. Externalhelpereffectsand literalownership unresolved;no C/freeze/completenessclaim.
