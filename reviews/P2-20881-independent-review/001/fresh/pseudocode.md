# Selector two first match set bit two asymmetric result compare

Partial/unaccepted;120instructionbytes;inherited40frame,R5buffer,R6fullprior47D8CEresult,R4zero.
D35C call45A568withliveargs;thenfreshunsignedbyte[R5+4];comparetoLOW8helperresult. Unequal→pendingD43C. EqualD368query43D0CEbit1zero→D390;elsefreshbyte6→SP8,literal47D96C→SP4,126→SP0;43D574(4,literal47D918,literal47D914,literal47D910,126,literal47D96C,freshByte6).
D390freshquerybit0one→D3A0;elseanotherquerybit2zero→D3B0. D3A0independentlyfreshbyte6→R3;43CE9E(0x10400000,literal47D970,same,freshByte6).
D3B0independentlyfreshbyte6==1:ptrliteral47D900;freshflagbyteOR4store. Thenindependentlycall47D8CEwithliveargs;R6=LOW8priorR6;compareR6againstfullnewR0. UnequalR4=1→pendingD514;equalR4=0→pendingD514. Newhelperresultisnotnarrowed; oldresultnarrowedonlyaftercall. Byte6not1→pendingD3D4,whereanotherfreshreadoccursoutside map.
Do notassumehelperstableorflagupdateeffects. Diagnosticstackwriteslocal; no C/freeze/completenessclaim.
