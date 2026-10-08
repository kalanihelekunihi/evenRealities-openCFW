# Selector one byte-six flag bit zero conditional helper pair

Partial/unaccepted;128instructionbytes;inherited40frame,R5buffer,R4inheritedzero.
D0DA query43D0CEbit1zero→D102;elsefreshunsignedbyte[R5+6]→SP8,literal47D938→SP4,89→SP0;43D574(4,literal47D918,literal47D914,literal47D910,89,literal47D938,freshByte6).
D102freshquerybit0one→D112;elseanotherquerybit2zero→D122. D112independentlyfreshbyte6→R3;43CE9E(0x10400000,literal47D93C,same,freshByte6).
D122independentlyfreshbyte6 compareexact1;unequal→D14C. Exact1:ptr=literal47D900;readfreshbyte[ptr],OR1,storebyte[ptr]. ThenR5=literal47D940 (replacesbufferregister);476ACE(R5,liveR1/R2/R3);47697E(R5,258,0,liveR3);branchpendingD1E4.
D14C:ptr=literal47D900;readfreshbyte[ptr],AND254,storebyte[ptr];branchpendingD1E4. Nohelperpaironthispath. Both paths retainR6originalbuffer;R4notassigned. Read-modify-writeofruntimeflagnotatomicclaim. Preservethree independentbyte6readsandhelperargs. No C/freeze/completenessclaim.
