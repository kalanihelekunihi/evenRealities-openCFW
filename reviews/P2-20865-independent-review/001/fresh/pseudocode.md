# Fresh helper low byte and buffer byte-five diagnostics

Partial/unaccepted;88instructionbytes;inherited40frame,R6=entryR1bufferpointer.
D00E query43D0CEwithliveargs;bit1zero→D03E. Otherwisecall45A568withcurrentliveargs;LOW8result→SP12;thenfreshunsignedbyte[R6+5]→SP8;literal47D928→SP4;82→SP0;43D574(4,literal47D918,literal47D914,literal47D910,82,literal47D928,freshByte5,LOW8helperResult).
D03E freshquerybit0one→D04E;elseanotherquerybit2zero→pendingD066. D04E independentlycall45A568withliveargs;LOW8result→SP0;thenindependentlyfreshunsignedbyte[R6+5]→R3;43CE9E(0x10800000,literal47D92C,same,freshByte5,LOW8independentHelperResult);fallthroughpendingD066.
Bothhelpercalls precedetheirrespectivebyte5read;do notcachehelperresultorbufferbyte. No pointerguardorlengthcheckinthisslice;stackwriteslocalSP0..12. No C/freeze/completenessclaim.
