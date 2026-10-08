# Selector two fresh zero three two flag helper actions

Partial/unaccepted;104instructionbytes;inherited40frame,R5buffer,R6priorfullhelperresult,R4inherited. D3D4freshunsignedbyte[R5+6]compare0. Equal:ptrliteral47D900;freshflagbyteAND251store(clearbit2);47D8CE(liveargs);R6=LOW8priorR6;comparetofullnewR0;unequalR4=1/equalR4=0;both→pendingD514.
Nonzero→D3F8independentlyfreshbyte6compare3. Equal:ptrliteral47D900;freshflagbyteOR16store(setbit4);4D306C(2,liveR1/R2/R3);49E448(3,0,liveR2/R3);→pendingD514. R4preserved.
Not3→D41Aindependentlyfreshbyte6compare2. Not2→pendingD514withoutflagwrite/helpercall/R4assignment. Exact2:ptrliteral47D900;freshflagbyteAND239store(clearbit4);4D306C(1,liveR1/R2/R3);49E448(2,0,liveR2/R3);→pendingD514. R4preserved.
Threeindependentbyte6readsmustnotbeoneswitchsnapshot; valuecanchangebetweencomparisons. CallsandruntimeRMWexactorder. No inferredhelpercontract/C/freeze/completenessclaim.
