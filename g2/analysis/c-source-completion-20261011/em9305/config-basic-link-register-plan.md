# Full basic link reduction plan

Authoritative native span326ed8..3272d8 (config-basic-link-complete-native.txt). Preserve duplicated mode branches and their fresh config reads until whole-body projection verified.

## ISA operands verified

-326f42 MPYWHUL r12,r8,r58;326f54 MPYWHUL r0,r8,r4 (r8=1250).
-327176 MPYWHUL r19,0xbec102,r2 (r2=intervalhalf).
-32717e/3271b4 MPYWHL r1,r1,r18 (r18=10000).
-327186 MPYWHUL r9,r19,r8 (r8=capturedrowfirstlength).
-3271b8 MPYWHUL r11,r19,r2 (r2=freshsecondlength).

## State-sensitive divisions

Flagged branch327110 DIVU destinationR3 inherits precedingsecondlength+5/cap state whenfirstdenominatorzero;327130 destinationR1 inherits firstreproducedproduct. MustuseDIVUwithexplicitprior, notundefinedCdivide orfixeddefault1. Nonflagged327274 R13 initiallyinputpointer;327298 R2 carriesfreshlength; mode0divisors guardednonzero.

32710a firstlengthnonzero branch computesceil with signedMPYWHLproduct, carryunsignedcomparison.32726e nonflaggedceil usesunsignedMPYWHUL then signedLTcomparison. Keep distinct.

Flagged rounding thirdargumentMAX(limit502,limit503); nonflaggedMIN. Inputrow8/9 max. output504 lowbyte. Flaggedadditional sizeprojection uses0xbec102 interval product, firsttime*10000 andsecondtime*10000, twoquotients/remainderceil then5xlarge+small, source-owned30c40c child.

Remaining genuinebody is326ed8; namedISA intervalslice is not closure. FullreturnR0 differs exits: flaggedsecond30c40c result retained; nonflagged317efc result retained. Existing callercontractvoid ignoresresult, but source evidence shouldrecordnativeR0.
