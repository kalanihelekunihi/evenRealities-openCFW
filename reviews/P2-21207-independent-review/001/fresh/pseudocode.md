# Second body, trailing padding and string length setup

Partial/unaccepted;176 instruction bytes481B08..481BB8. Continues481836232frame. R7=wordSP20+wordSP32mod2^32,R4wordSP36;CBZ skipssecondbodywhenzero;otherwisecallbackR6SP192once,freshpostincrementbodybyte→R1,R0SP16,BLXR6 liveR2/R3;fullresultSP16;zero→4824E4;nonzeroincrementSP52/decrementR4 repeatuntil0;storeR6SP192. ThenSP48signedcountzero-padding:unconditionalbyteSP0=48;positiveonlyrepeat482684(callbackSP192,SP8,SP,1),nonzeroerror;decrementuntil0/storecallbackslot.

FreshbyteSP64flags bit2 testedviaLSL29sign. Ifclear→481868mainloop. Ifset:byteSP0=space32unconditional;R5signed<=0→mainloop;positiveR5repeat482684(callbackR4SP192,SP8,SP,1),nonzeroerror;decrementR5until0;storeR4SP192;mainloop. R5remainingwidthdefinitionfromotherhandlersunresolved.

Nullreplacemententry481B88 ADR R0=4826E4,SP20=pointer,branch4824AC. Nonnullstring481B92:R5precisionSP56;signednegative→44A43C(R0R4string,liveargs),R4fullhelperresult. Nonnegative→4D40E0(R0R4string,R2R5precision,R1live,R3live);nonnullresultR4=result-originalstringmod2^32,zeroresultR4=precision. StoreR4SP32 thencommon4824AC. Do notassumehelperstrlen/memchrsemanticsuntilrecovered. Preserveliveargs/outputorder,no C/freeze/fullcoverage/equality claim.
