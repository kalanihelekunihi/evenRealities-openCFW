# Decimal float wrapping exponent estimate, scaling and digit budget

Partial/unaccepted;108 instruction bytes481F6A..481FD6. Continues481836232frame,R8lowercaseconversion. ReloadSP0exponent→R1;R2literal482674divisor;R0=30103;R1=low32(R1*30103);SDIVsignedR1/R2→R2;storeR2SP0. Preservewrappingmultiplybeforedivision,notunboundedrationalestimate. ReloadoriginalrawSP176/180→R4/R5;R2=7-estimatemod2^32;clearR5signbit. IfsignedR2>0 call48262C(R0R4,R1R5,R2scale,R3live). OtherwiseR2=-R2mod2^32;R0=0,R1literal482678;call48262C withliveR3;returnedpair→R2/R3,R0/R1absoluteoriginalR4/R5;call4D4326. Bothpathsreturnpair→R4/R5;helpersemanticsunresolved.

IfR8=='f'(102),R7=wordSP0estimate+10mod2^32;elseR7=6. ReloadprecisionSP56;R7+=precisionmod2^32;if signedR7>20 clamp20;no lowerclamp. Storebyte48SP132;R6=SP133;signedR7<=0→482040 unresolvedrounding;positive→481FD6 unresolveddigitloop. PreserveITconditions/helperargs/literals;no standarddecimalformatreplacement,C/freeze/fullcoverage/equality claim.
