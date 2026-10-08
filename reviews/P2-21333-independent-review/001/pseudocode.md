# Floating precision cap, integer and fractional scaling

Partial/unaccepted;104 instructionbytes483424..48348C,continues48335080-byteframe. FlagsR12bit10clear→R7=6defaultprecision;setretainsR7. LoopunsignedR8<32 andunsignedR7>=10: R4=48,R5=SP16buffer,storelowbyte[R5+R8],R8++mod,R7--mod;repeat. Thuswriteszeroswhileprecision>=10butnootherprecisionclampwhenbufferfull.

VCVT.s32.f64 s2,d0;VMOVR5,s2(integerbits). Freshliteral484000→R9tablepointer. VMOVs2,R5;VCVT.f64.s32d1,s2;VSUBd1=d0-d1. R4=R9+(R7<<3)mod;VLDRd2eightbytes[R4];VMULd1=d1*d2;VCVT.u32.f64s4,d1;VMOVR4,s4(fractionintegerbits);VMOVs4,R4;VCVT.f64.u32d2,s4;VSUBd1=d1-d2. VLDRd3eightbytesliteral483644;VCMPd1,d3;VMRSAPSR;LT(N!=V)→unresolved4834AE,elsefallthrough48348C. PreservehardwareFPconversion/FPSCRsemanticswithoutassuminghostrounding,signedintegerconversionversusunsignedfractionconversion,indexwrappingand8byteconstant/tableobligations. No C,freeze,wholecoverage or equalityclaim.
