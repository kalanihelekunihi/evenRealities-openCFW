# Fraction rounding carry and half-comparison parity branches

Partial/unaccepted;112 instructionbytes48348C..4834FC,continues48335080-byteframe. FirstentryR4++mod;VMOVs2,R4;VCVT.f64.u32d1,s2;R9+=R7<<3mod;VLDRd2eightbytes[R9];VCMPd1,d2/VMRS;LT→4834C8,elseR4=0,R5++mod,branch4834C8. Separate4834AE immediateVMOV.f64d3,#96(0.5);VCMPd1,d3/VMRS;MI→4834C8. OtherwiseifR4==0incrementR4;nonzeroR4LSL31signbit0clear→skip,bit0setincrementR4. Do not silentlyreplaceFPconditionbrancheswithstandardroundingalgorithm.

Common4834C8 R7!=0→unresolved4834FC. Zero precision:VMOVs2,R5;VCVT.f64.s32d1,s2;VSUBd0=d0-d1;VMOV.f64d2,#96(0.5);VCMPd0,d2/VMRS;PL→4834F4. MIpathVLDRd2eightbytes483644;VCMPd0,d2/VMRS;LT→unresolved48355C,else4834F4. R5LSL31bit0clear→48355C;setR5++modthen48355C. PreservedifferentLT/MI/PLFPconditions,currentd0mutation,tablepointerR9overwrite,full32-bitcarry/parity and8byteconstantobligation. No C,freeze,wholecoverage or equalityclaim.
