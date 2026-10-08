# Raw exponent/fraction checks and special three-byte copy

Partial/unaccepted;110 instruction bytes481D7A..481DE8. Continues481836232frame;rawlowL/highHwordSP8/12,R11conversion,R12prefix-endpointer. ReloadL/H;T=(H<<1mod2^32)|(L>>31);R6=ASR(T,21),R7=ASR(T,31). IfR7==FFFFFFFF ANDR6==FFFFFFFF,formU=(H<<12mod2^32)|(L>>20),V=L<<12mod2^32;nonzero(U|V)→firstspecialpath. PreserveIT EQcompareandexactshiftpredicates. Firstspecial:R5=conversion-97mod2^32;SP32=3;ifunsignedR5<26 sourceADR4826E8 at481DE2;elseADR4826EC at481DB0.

OtherpathreloadL/H;Q=ASR(H<<1mod2^32,21);ifQ!=-1 or(H<<12mod2^32)!=0→481DE8 unresolvednormalization. Else secondspecial:R5conversion-97;SP32=3;unsignedR5<26→481E14 unresolvedsourceADR;elseADR4826F4 at481DD4. Note secondpredicateonlychecksHfractionbits,notL; do notsubstitutestandardisinf/isnanwithoutprovingprecedingfirstpredicatehandling.

Common481DD8:R2=3,R0=R12destination,R1source;call439BE4 withliveR3;ignorefullreturn;branch4824AC. Specialstringbytes/helpersourcedataunresolved;copysemanticsrequirehelperrecovery. No C/freeze/fullcoverage/equality claim.
