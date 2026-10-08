# Nonnull input and two-bank seven-word direct-write prefix

Partial/unaccepted;136 instruction bytes481468..4814F0. PUSH R2,R3,R4,LR16;R4fullentryR1inputpointer. NullR4→R0=6branch481572 unresolvedepilogue. OtherwiseUXTBentryR0selector==2→twobankpath;other→4814F0 unresolveddispatch. Mode2call473940 withR0fullentryselector,R1lowbyteselector2,liveR2/R3;savefullresultSP0 overwritingentryR2.

For k0..6 inincreasingorder:freshword[R4+4*k],loadtargetpointerliteral4817D8+4*k,storefullwordtargetwithouttargetread. Then repeatsevenfreshinputreads anddirectstoreswithliteral4817F4+4*k. No source snapshot reuse betweentwobanks;firstbankwritescanchangealiasedsecondbankinput. No masking,RMW,orreadback. ReloadSP0→R0;MSR PRIMASK,R0;branch48156C unresolvedstatus/unwind. Preserve ordered14freshinputreads/stores andhelperstackaliasing. No inputsizeguard beyondnonnull. Othermodes/epilogue unresolved;no C/freeze/fullcoverage/equality claim.
