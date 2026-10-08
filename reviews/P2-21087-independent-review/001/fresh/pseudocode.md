# Low-byte mode dispatch: zero and one paths, prefix

Partial/unaccepted;134 instruction bytes47FEA0..47FF26,prefixonly. PUSH R0,R1,R2,R3,R4,LR24;R4=0;R0LOW8entryR0. Mode0→FEB6;mode2→FF26outsideprefix;unsigned<2afterexcluding0/2meansmode1→FEF6;mode3→FF3Aoutsideprefix;others→FFB2outsideprefix. Mode0freshwordthrough480188bits4..5==3→R0=0branchFFB6;otherwise480358(live),FE12(live),ignoredreturns;freshword4801D4OR0x80000000store;freshword4801D8OR15store;48036E(live),ignoredreturn;freshword4801DCOR1store;480384(live),ignoredreturn;branchFFB4outsideprefix.

Mode1byteSP0=0 alterslowbyte savedentryR0;F90C(23,SP,liveR2/R3),returnignored;freshbyteSP0zero→FFB4. NonzeroF56E(live),fullnonzero→FFB6unchanged;zeroF7AE(23,live)→fullR4;nonzeroR0=R4→FFB6;zero→FFB4. Helpersmayalterpassedbyte;nocachedqueryresult. EverywordRMWfreshandordered. Continueexternalpathswith24frameactive; nofinalstatus/unwindclaim untiltaildecoded. Ownership/externalhelpers/MMIO/C/freeze/fullcoverage unresolved/notclaimed.
