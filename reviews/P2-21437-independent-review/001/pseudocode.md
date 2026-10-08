# Global helper, count dispatch and node status signed bounds prefix

Partial/unaccepted;96 instructionbytes48462E..48468E. 48462E8Bwrapper:R0=wordliteral4849A4;4D4724;POP R0savedR7/PC overridesresult. 48463A8Bwrapper:R3=wordliteral4849A8;R3=word[global+320];equals1→4849FCwithentryR0/R1/R2retainedandR3=1;elseUXTB R2,484656withR3=count. POP R1savedR7/PCretainscalleeR0.

484656PUSHentryR3/R4/R5/R6/R7/LR24B;R5=entry0,R4=entry1,R6=entry2. Word[R5+68]R0null→48469E. Nonnull453604→44FA7Ewithpreviousresult/liveargs;R7=result;453604again→44FAA8. Freshnodeword[R5+68]R1;word[node+80]R2==1→48469E;word[node+8]signedR2>=1→48469E;word[node+16]R2,R7--wrap,signedR2<R7→48469E;otherwiseword[node+12]→R2. Fallthrough48468Eunresolved. Preserve signed comparisons, two separate453604calls andfreshnodepointerafterhelpers. No C,freeze,wholecoverage or equalityclaim.
