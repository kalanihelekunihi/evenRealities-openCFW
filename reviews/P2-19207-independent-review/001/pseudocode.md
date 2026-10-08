# Signed limit and increment path 0x46A6D2..0x46A74A

Partial/unaccepted;120instructionbytes. PUSH0/1/2/3/4/LR24. R4=addressliteral46AE98;freshword[R4]R0;R1=freshword[addressliteral46B00C]minus1wrapping32. SIGNED R0>=R1 branches73C. Otherwise SECONDfreshword[R4]increment1wrapping32store[R4]. Call43D0CE(liveargs);bit1set storesfreshword[R4]SP8(overwritesorigR2),literal46B024SP4(overwritesorigR1),477SP0(overwritesorigR0);call43D574(4,literal46A834,literal46A830,literal46B028). Fresh43D0CE bit0set or,ifclear, furtherfresh43D0CE bit2set calls43CE9E(0x10400000,literal46B02C,sameliteral,freshword[R4]). Ordered46A53A(liveargs),then46A4E2(liveargs),branch77Coutsidecomponent.

Limit-failure73C fresh43D0CE bit1clear branches75Eoutsidecomponent. Ifset, literal46B030storedSP4 at748; diagnosticcontinues74A. Separatecalls/freshreads remain distinct. Returnrestore isoutsidecomponent, so savedargument-slot overwrites must be retained. No C/freeze/corpusclaim.
