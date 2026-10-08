# Selector one second match bit one shared fresh flag actions

Partial/unaccepted;180instructionbytes;inherited40frame,R5bufferunlesspriorbranchreplaced,R6originalbuffer,R4zero. D15A reachedonfirstbyte4mismatch:call45A568;thenfreshbyte[R5+5];comparetoLOW8result. Unequal→D1E4. Equal→D166query43D0CEbit1zero→D18E;elsefreshbyte6→SP8,literal47D944→SP4,98→SP0;43D574(4,literal47D918,literal47D914,literal47D910,98,literal47D944,freshByte6).
D18Efreshquerybit0one→D19E;elseanotherquerybit2zero→D1AE. D19Efreshbyte6→R3;43CE9E(0x10400000,literal47D948,same,freshByte6).
D1AEindependentlyfreshbyte6==1:ptrliteral47D900;freshbyteOR2store;R5=literal47D940;476ACE(R5,liveR1/R2/R3);47697E(R5,258,0,liveR3);→D1E4. Otherbyte6:D1D8 freshflagbyteAND253store;→D1E4.
SharedD1E4 (alsofirstmatchpaths):R0=literal47D900;freshflagbyte→R1;R1&=12;exact12→47432C(liveR0/R1/R2/R3),thenD20C. OtherwiseD1F8independentlyreloadbyteatcurrentR0pointer;TST12;anybitset→D20C. Neitherbitset→46B0EC(liveargs);fullresult==1→474100(liveargs),elseD20C. D20CbranchpendingD7B6.
No cachedflagbyteacrosstests; runtimeflagreadmaydiffer. R4unassigned,savedframeintact. Helperresultsnotinterpretedbeyondexact1. No C/freeze/completenessclaim.
