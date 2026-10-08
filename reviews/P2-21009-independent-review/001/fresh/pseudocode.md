# Thirty-two-byte caller object and allocation initialization

Partial/unaccepted;100instructionbytes47EB94..47EBF8,twoentries.
EB94 PUSH R2,R3,R4,LR16;R4=entryR0. Fullzero→5FA0A4(liveargs),ifreturnsstore0toFFFFFFFFthenEBA8selfloop. OtherwiseSP0=32overwritessavedentryR2;freshSP0reloadfull!=32→samefatalwrite/selfloopEBC0. Retainstored/reloadedguarddespiteordinaryequality. FullR4zeroagainatEBC2skipinit;normalpathnonzero→word[object]=0;45607C(object+4,liveargs);byteobject28=1. ReturnR0=R4;POP R1,R2,R4,PC returnsR1=SP0(32onordinarypath),R2=savedentryR3subjectcallee writes,restoresR4.
EBD8 PUSH R4,LR8;456110(32,liveentryR1,R2,R3)→R4. Fullzero→return0. Nonzero→word[object]=0;45607C(object+4,liveargs);byteobject28=0. ReturnR0=R4,discardinitializationhelperresult;POP R4,PC restoresR4. Callerobjectbyte28=1versusallocationbyte28=0 keptdistinct;otherfieldinitializationdepends45607C. No C/freeze/completenessclaim;ownership/externalhelpersemanticsunresolved.
