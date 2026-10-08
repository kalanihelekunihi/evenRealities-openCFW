# Selector two second match message and bit-five actions

Partial/unaccepted;100instructionbytes;inherited40frame,R5buffer,R6priorhelperresult,R4inherited. D4B2fromsecondmatchbyte6==1:call47CE90withliveargs;→D514.
D4B8freshbyte[R5+6]compare0. Exact0:ptrliteral47D900;freshflagAND247store(clearbit3);47D8CE(liveargs);R6=LOW8oldR6;comparetofullnewR0;unequalR4=1/equalR4=0;D4DAcall47CE90withliveargs;→D514.
Nonzero→D4E0independentlyfreshbyte6compare3. Exact3:ptrliteral47D900;freshflagOR32store(setbit5);4A2914(liveargs);fullresultnonzero→D514;else4A2EA4(1,liveR1/R2/R3);→D514. R4preserved.
Not3→D502independentlyfreshbyte6compare2. Not2→D514;exact2 freshflagbyteatliteral47D900 AND223store(clearbit5);nohelpercall,R4preserved. D514unconditionallybranchpendingD7B6 sharedtail.
Preservefreshreadsandsideeffectorder. MessagehelperdoesnotdictateR4. No C/freeze/completenessclaim.
