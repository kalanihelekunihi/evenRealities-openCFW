# Signed positive state decrement 0x46A77E..0x46A7FA

Partial/unaccepted;124instructionbytes. PUSH0/1/2/3/4/LR24. R4=addressliteral46AE98;freshword[R4]SIGNED<1 branches7E0. Otherwise SECONDfreshword[R4]minus1wrapping32store[R4]. Fresh43D0CE bit1set storesfreshword[R4]SP8(overwritesorigR2),literal46B038SP4(overwritesorigR1),491SP0(overwritesorigR0);call43D574(4,literal46A834,literal46A830,literal46B03C). Fresh43D0CE bit0set or,ifclear,anotherfresh43D0CE bit2set calls43CE9E(0x10400000,literal46B040,sameliteral,freshword[R4]). Ordered46A53A(liveargs),then46A4E2(liveargs),branch820outsidecomponent.

Failure7E0 fresh43D0CE bit1clear branches802outsidecomponent. Ifset storeliteral46B044SP4,496SP0,R3literal46B03C,R2literal46A830 at7F8; diagnosticcontinues7FA. Keep separatefreshcalls and savedslot writes. Returnrestoreoutsidecomponent. No C/freeze/corpusclaim.
