# Selector six byte-five match bit-five three-two helper actions

Partial/unaccepted;218instructionbytes;inherited40frame,R5buffer,R4zero.
D642query43D0CEbit1zero→D664;elsefreshbyte6→SP8,literal47D98C→SP4,208→SP0;43D574(3,literal47D918,literal47D914,literal47D910,208,literal47D98C,freshByte6). D664freshquerybit0one→D674;elseanotherquerybit2zero→D684;D674independentfreshbyte6→R3;43CE9E(0x0C400000,literal47D990,same,freshByte6).
D684call45A568withliveargs;thenfreshbyte[R5+5];compareLOW8helperresult;unequal→D71A. EqualD690querybit1zero→D6B0;elsefreshbyte6→SP8,literal47D994→SP4,210→SP0;43D574(4,literal47D918,literal47D914,literal47D910,210,literal47D994,freshByte6). D6B0freshquerybit0one→D6C0;elseanotherquerybit2zero→D6CE;D6C0independentfreshbyte6→R3;43CE9E(0x10400000,literal47D998,same,freshByte6).
D6CEindependentlyfreshbyte6==3:ptrliteral47D900;freshflagOR32store;4D306C(2,liveR1/R2/R3);49E448(3,0,liveR2/R3);4A2914(liveargs);fullresultnonzero→D71A;else4A2EA4(1,liveR1/R2/R3);→D71A.
Not3→D6FCindependentlyfreshbyte6==2;not2→D71A;exact2freshflagatliteral47D900AND223store;4D306C(1,liveR1/R2/R3);49E448(2,0,liveR2/R3). D71AbranchpendingD7B6. R4neverassignedinthiscase. Preserveallfreshreadsandcallorder,localstackwrites. No C/freeze/completenessclaim.
