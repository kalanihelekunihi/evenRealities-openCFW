# State pair diagnostic prefix 0x46A848..0x46A8C0

Partial/unaccepted;120instructionbytes. PUSH3/4/5/6/7/LR24 withnoadditionalallocation. Fresh43D0CE(entryliveargs) bit1set: freshword[addressliteral46B00C]SP12 overwrites savedR6;freshword[addressliteral46AE98]SP8 overwrites savedR5;literal46B04CSP4 overwrites savedR4;504SP0 overwrites savedR3. Call43D574(4,literal46B058,literal46B054,literal46B050).

Fresh43D0CE bit0set or,ifclear,furtherfresh43D0CE bit2set: freshword[addressliteral46B00C]SP0 overwrites savedR3again;call43CE9E(0x10800000,literal46B05C,sameliteral,freshword[addressliteral46AE98]),extraSP0word. Preserve separatefreshreads and call-dependentstackaliasing;epilogueoutsidecomponent.

At8AC loadR0=addressliteral46B00C;freshword[R0]R1FULLnot2 branches98Eoutsidecomponent. FULL2 loadsR1=addressliteral46AE98;freshword[R1]R0FULLnonzero branches91Coutsidecomponent,zero falls8C0. Childcontracts unresolved;no C/freeze/corpusclaim.
