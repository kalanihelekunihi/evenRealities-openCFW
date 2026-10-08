# Selector three byte-five match bit-three zero-one actions

Partial/unaccepted;162instructionbytes;inherited40frame,R5buffer,R4zero. D516call47D8CEwithliveargs;R6=fullresult;45A568withliveargs;thenfreshbyte[R5+5]compareLOW8helperresult. Unequal→D5B6 withoutR4assignment.
EqualD528query43D0CEbit1zero→D550;elsefreshbyte6→SP8,literal47D97C→SP4,179→SP0;43D574(4,literal47D918,literal47D914,literal47D910,179,literal47D97C,freshByte6). D550freshquerybit0one→D560;elseanotherquerybit2zero→D570;D560independentlyfreshbyte6→R3;43CE9E(0x10400000,literal47D980,same,freshByte6).
D570independentlyfreshbyte6==1:ptrliteral47D900;freshflagOR8store;47D8CE(liveargs);R6=LOW8oldR6;comparefullnewR0;unequalR4=1/equalR4=0;→D5B6.
Not1→D594independentlyfreshbyte6compare0;not0→D5B6 unchangedR4. Exact0:ptrliteral47D900;freshflagAND247store;47D8CE(liveargs);R6=LOW8oldR6;comparefullnewR0;unequalR4=1/equalR4=0. D5B6branchpendingD7B6.
No message259callinthiscase. Preservefreshreads/order/asymmetricwidths; oldresultnarrowedafternewcall. No C/freeze/completenessclaim.
