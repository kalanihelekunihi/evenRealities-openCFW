# Two-word division small divisor fast paths

Partial/unaccepted;114 instruction bytes. EntryR1:R0 numerator,R3:R2 divisor. CC60 ifR3nonzero→pendingCCD2;otherwiseifR1zero→CC9E. NonzeroR1:unsignedR2>=65536→pendingCD68;elseCMP R2,2 and<=2→CCAE.
For3..65535:IP=oldR1;R1=UDIV(oldR1,R2);R3=oldR1-R2*R1;R3=(R3<<16)|(oldR0>>16);IP=UDIV(R3,R2);R3-=R2*IP;R0=LOW16(oldR0);R3=R0|(R3<<16);R0=UDIV(R3,R2);R2=R3-divisor*R0;R0|=IP<<16;R3=0;BXLR. Thus quotientR1:R0 and remainderR3:R2; preserveintermediateIP.
CC9E (entryR1zero):CMP R2,2;<=2→CCAE;elseIP=oldR0,R0=UDIV(oldR0,R2),R2=oldR0-divisor*R0;BXLR;R1/R3 remainzero.
CCAE CBZ R2→CCC4 withoutalteringCMPflags;BNE CCBE uses precedingCMP R2,2. ThereforeR2==2:remainderR2=oldR0&1;LSRS R1,1 setscarryoldR1bit0;RRX R0 usingcarry;BXLR. R2==1:CCBE setsR2=0,R3=0;quotientunchanged;BXLR. R2==0:CCC4 tailbranch4D2B98 withlivearguments; nozero-divisorresultassumed.
SeparateentryCCC8 copiesR1toR3,R0toR2,zerosR1/R0,BXLR. No fallthroughfromunconditionalCCC4branch; callers/ownershipofCCC8unproven. No frame inthismap. Pendinglargedivisorpaths remain. No C/freeze/completenessclaim.
