# Counter reset ten-record loop and stack-aliased return

Partial/unaccepted;188 instruction bytes; inherited32-byte PUSH R0..R6,LR frame. R4 global word pointer,R5 currentrecord,R6 fullindex initially0.
C1BA freshly read unsignedbyte[R5+47];zero→C22C. Otherwise freshlyread byte48;zero→C22C. Bothnonnull:read word[R4],add1mod32,store word[R4],independentlyreload andstore word[R5+196].
C1D6 statusquerybit1zero→C200;otherwisefreshword196→SP12,fullR6→SP8,literal47CAF8→SP4,2101→SP0;43D574(4,literal47C548,literal47C544,literal47CAEC,2101,literal47CAF8,fullR6,freshWord196).
C200 freshquerybit0one→C210;elseanotherquerybit2zero→C226. C210 independentlyfreshword196→SP0;43CE9E(0x10800000,literal47CAFC,same,fullR6,freshWord196). This fifth-argument write replaces savedR0, even if logger skipped. C226 call479B74(R5,liveR1/R2/R3).
C22C incrementfullR6mod32,R5+=200mod32. C230 signedfullR6<10→C1BA;otherwiseC234. Initial prefix branches directlyC230, so ten iterations with stride200, unlike preceding stride256 routine.
C234 querybit1zero→C256;elseSP4=literal47CB00,SP0=2110;43D574(4,literal47C548,literal47C544,literal47CAEC,2110,literal47CB00). C256 freshquerybit0one→C266;elseanotherquerybit2zero→C274. C266:43CE9E(0x10000000,literal47CB04,same,liveR3),no explicit R3 assignment or SP0 write.
C274 POP R0..R6,PC restores32bytes. R0 returns last SP0 value: entryR0 or prefix2091 or loop2101 or independentlyfreshword196 from loopmask or final2110. SavedR1/R2/R3 also can be overwritten atSP4/SP8/SP12 by looplogger. Preserve exact order and independent reads, no stability assumption. No C/freeze/wholefirmwareclaim.
