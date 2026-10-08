# Caller-supplied forty-four-byte object wrapper with retained fatal checks

Partial/unaccepted;72instructionbytes47E712..47E75A. PUSH R1,R2,R3,R4,R5,LR24. SP0=44 overwritessavedentryR1;freshreloadSP0→R4;fullR4!=44→5FA0A4(liveargs),ifreturnsstoreword0toFFFFFFFFthenselfloopE72Aifstorecompletes. Thisstored/reloadedcheckretained,notdiscardedbecauseordinarylocalexecutionmakesitequal.
R4=freshSP28 (caller'ssixthstackarg);R5=freshSP0. R4zero→secondfatalcall/write/selfloopE740. AtE742againfullR4zero skipswork(return0);withoutregistermutationinbetweenthatbranchisunreachablefromnormalnonzeropathbutinstructionretained.
Nonzero→byte[R4+40]=2;SP4=R4 overwritessavedentryR2;R5=freshSP24(caller'sfifthstackarg);SP0=R5;47E75A(liveentryR0,R1,R2,R3)withstackargsfifthcallerword,sixthR4. R0=R4;POP R1,R2,R3,R4,R5,PC24 returnsR1=SP0,R2=SP4,R3=SP8savedentryR3,subjectcallee memorywrites;restoresentryR4/R5. Helperresultdiscarded. Exactobjectownership/helpersemanticsunresolved; no C/freeze/completenessclaim.
