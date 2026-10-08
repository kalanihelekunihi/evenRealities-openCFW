# Hex float precision budget, helper flags and exponent adjustment

Partial/unaccepted;58 instruction bytes481E46..481E80. Continues481836232frame. ReloadprecisionSP56→R0;signednegative→SP4=33;nonnegative→SP4=precision+1mod2^32 (ITTEE preservescompareflags). R7=SP4thenR7++mod2^32. ReloadoriginalrawpairSP176/180→R0/R1;R2=R3=0;reloadnormalizedpairSP8/12→R4/R5;call4D41C0 withoriginalrawpair/zero pair. IT CC immediatelytestshelperreturnedcarry;ifcarryclear XORR5signbit80000000. Helperreturnregisters/flags exactdependenciesunresolved;do notreplacewithnumericcomparison.

ReloadwordSP0exponent→R1;storelow8helper-returnR2byteSP132 (notassumed0aftercall);R1-=4mod2^32→SP0. R6=SP133;CMPsignedR7<=0→481EE6 unresolvedpath;positive→481E80 unresolveddigitloop. Preservehelperflags,returnedR2byte andstackreloads;no C/freeze/fullcoverage/equality claim.
