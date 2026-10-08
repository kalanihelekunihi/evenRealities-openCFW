# Zero padding, body callbacks and second zero padding

Partial/unaccepted;112 instruction bytes481A98..481B08. Continues481836232frame. R4wordSP40paddingcount;byteSP0='0'(48) storeevenifcountnonpositive. Signedcount<=0 skipfirstpadding;positive:reloadcallbackR6SP192once;repeat482684(R0R6,R1SP8,R2SP,R3=1);fullnonzero→4824E4error;zero→decrementR4 repeatuntil0;storeR6SP192aftercompletion. HelperstackSP8state/countersemanticsremainunresolved.

R7wordSP20bodypointer,R4wordSP32bodycount;zero skipbody. Nonzero reloadcallbackR6SP192once;freshbyte[R7]postincrement1→R1;R0wordSP16;BLXR6 withliveR2/R3;fullresultSP16;zero→4824E4. Nonzero reloadSP52incrementmod2^32,decrementR4,storecounterSP52,repeatuntil0. CounttestCBZ unsignedfullword;negativebitpatternwoulditeratewrappingratherthansignedskip. StoreR6SP192afterbody.

R4wordSP44secondpaddingcount;byteSP0='0' storeunconditionally; signed<=0 skipto481B08. Positive repeatidentical482684paddingcall/error/decrementloopthenstoreR6SP192. Preservefreshbodybytes/stateandcallbackslotreloadlocations;no mergedemissionorassumedhelpercountupdates. Continuationunresolved,no C/freeze/fullcoverage/equality claim.
