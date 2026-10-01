# Touch 16-bit register field update9FD4

Exact9FD4..A00C savesR4/LR. Accept onlyR0==1, unsignedR1<=1 and unsignedR2<65536; failuresreturnliteral004A0001 andrestoreframewithoutMMIOaccess. Successreadsonefreshwordat40010000+4*(R1+192),preservesitsbits31..24and7..0,placesR2inbits23..8,writesonewordtothesameaddress,returnszeroandrestoresR4/SP.

Twohundredfortyoriginal-instructionfixturesindependentlycheckthepredicate,onefreshread,maskedwrite,returnandframe. Theycoverboundaryvaluesandthreeinitialwordpatterns. Accessesareto syntheticmemory; physicaldevicebehavior,concurrencyandcallerreachabilityremainunresolved. No canonicaladmissionorCimplementation.
