# Fresh helper low byte and buffer byte-four diagnostics

Partial/unaccepted;88instructionbytes;inherited40frame,R6=entryR1bufferpointer.
CFB6 query43D0CEwithliveargs;bit1zero→CFE6. Otherwisecall45A568withcurrentliveargs;LOW8result→SP12;thenfreshunsignedbyte[R6+4]→SP8;literal47D920→SP4;81→SP0;43D574(4,literal47D918,literal47D914,literal47D910,81,literal47D920,freshByte4,LOW8helperResult).
CFE6 freshquerybit0one→CFF6;elseanotherquerybit2zero→pendingD00E. CFF6 independentlycall45A568withliveargs;LOW8result→SP0;thenindependentlyfreshunsignedbyte[R6+4]→R3;43CE9E(0x10800000,literal47D924,same,freshByte4,LOW8independentHelperResult);fallthroughpendingD00E.
Bothhelpercalls precedetheirrespectivebyte4read;do notcachehelperresultorbufferbyte. No pointerguardorlengthcheckinthisslice;stackwriteslocalSP0..12. No C/freeze/completenessclaim.
