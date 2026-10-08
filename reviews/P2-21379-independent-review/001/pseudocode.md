# String bound, leading padding and postdecrement output

Partial/unaccepted;112 instructionbytes483EEE..483F5E continuing88-byteframe483960. R10=wordvararg[R9],R9+=4;R1=R4precisionifnonzeroelseFFFFFFFF;R0=R10;call454770boundedlengthhelper,R11=result. Ifprecisionpresentflagbit10 andunsignedR11>=R4,R11=R4. Flagsbit1setskipprepadding;clear483F2AoldR0=R11,R11=old+1wrap;unsignedold<widthR7→spacecallbackR5withR3freshSP44,R2R6,R1freshSP40,R0=32;ignorecallbackresult,R6++;repeat. FailedconditionincrementsR11too.

483F34freshbyte[R10]zero→483F5Eunresolved. Elseprecisionflagbit10clear→output;setoldR0=R4,R4=old-1wrap;old0→483F5E (underflowsremainingprecisiononfailedcheck). OutputoldR2=R6,R6=old+1beforecallback;R3freshSP44,R1freshSP40,R0=freshbyte[R10];BLXR5ignored;R10++;repeat483F34. Retain bytecheckbeforeprecisionpostdecrement and secondfreshbyteloadatcallback. Stringpointer nullguardabsent inthiscandidate;helpersemantics separate. No C,freeze,wholecoverage or equalityclaim.
