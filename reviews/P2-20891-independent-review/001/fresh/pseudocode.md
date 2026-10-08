# Selector four low-bit insert fresh flag clears conditional call

Partial/unaccepted;138instructionbytes;inherited40frame,R5buffer,R4zero.
D5B8query43D0CEbit1zero→D5E0;elsefreshbyte6→SP8,literal47D984→SP4,193→SP0;43D574(3,literal47D918,literal47D914,literal47D910,193,literal47D984,freshByte6). D5E0freshquerybit0one→D5F0;elseanotherquerybit2zero→D600. D5F0independentlyfreshbyte6→R3;43CE9E(0x0C400000,literal47D988,same,freshByte6).
D600R6=literal47D900;freshbufferbyte6→R0;freshflagbyte→R1;BFI insertsR0bit0 intoR1bit6 only;storeflagbyte. Independentlyreloadflagbytebit6;nonnull→D62A. Zero:independentlyreloadflagbyteAND239store(clearbit4);independentlyreloadflagbyteAND223store(clearbit5). PreservetwoseparateRMWs,notcombinedmask.
D62Acall45A568withliveargs;fullresult!=1→D640. Exact1:independentlyreloadflagbytebit6→R1(0or1);4ABD60(1,R1,liveR2/R3). D640branchpendingD7B6. R4unassigned. Inputbyte6lowbitisused,notboolean(nonzero). No C/freeze/completenessclaim.
