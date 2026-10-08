# Handler tail 0x46951A..0x469576

Partial/unaccepted;92 instruction bytes. Inherit32-byteframe,R4payloadbyte,R5fullcontextbool. TemporaryR0=low8R4; if!=1 branch469556. Then temporaryR0=low8R5; if!=0 branch469556. Matching1/0 setsR0=1,R1=literal469B88,storebyte1[R1],R0=1 ->49BF24 withliveotherargs. Fallthrough469538 calls45A568 withliveargs; FULLresult1 calls45A8EE(266,0,0,500); otherwise skips.469550explicitR0=0;469552ADDSP20,POP R4/R5/PC12 restores32-byteframe.

469556 truncatesR4inplacelow8; ifnonzero branches469572. ZerotruncatesR5inplacelow8; FULLlowbyteR5!=1 branches469572. Matching0/1 setsR0=0,R1=literal469B88,storebyte0[R1];R0=0 ->4691BC withliveotherargs, thenbackwardbranch469538 sharedmodecheck. Othercombination469572explicitR0=0 ->469552epilogue. Allrecordedentryguards/actions therefore return0; retainchildsideeffects andeachorderedcall. Following469576zeroalignment andADR-targetdata469578/57C excluded. Childcontracts unresolved; no C,freezeorwholecorpusclaim.
