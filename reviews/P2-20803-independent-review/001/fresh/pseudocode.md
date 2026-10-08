# Global counter sentinel record update and saved-slot return

Partial/unaccepted; 198 instruction bytes. PUSH R0..R6,LR creates32-byte frame; R4=full entryR0. If zero branch C148 directly. Otherwise R5=R4,R6=literal47C558; read word[R6]. If unequal FFFFFFFF branch C0E2.
Sentinel path C09A: query43D0CE bit1 zero skips C0C0. Otherwise SP4=literal47CAD4,SP0=2067;43D574(2,literal47C548,literal47C544,literal47CAD8,2067,literal47CAD4). C0C0 fresh query bit0one→C0D0;else another query bit2zero→C0DE. C0D0:43CE9E(0x08000000,literal47CADC,same,liveR3). C0DE unconditionally calls47C164 with live arguments on the sentinel path; do not infer helper behavior.
C0E2 independently read word[R6], add1 modulo32, store word[R6], independently reload word[R6] and store word[R5+196]. Do not reuse earlier loads.
C0EE query status bit1zero→C11A. Otherwise independently read word[R5+196] intoSP8, SP4=literal47CAE0,SP0=2072;43D574(4,literal47C548,literal47C544,literal47CAD8,2072,literal47CAE0,freshWord196).
C11A fresh query bit0one→C12A;else anotherquery bit2zero→C13C. C12A independently read word[R5+196] intoR3;43CE9E(0x10400000,literal47CAE4,same,independentFreshWord196).
C13C call479B74(R4,liveR1/R2/R3); then47B730(R4,liveR1/R2/R3). C148 POP R0..R6,PC restores32 bytes. ReturnedR0 is savedSP0: original entryR0 unless overwritten by logger2067 or logger2072 (last executed logger wins); null returns0. SP4/SP8 diagnostic writes also overwrite saved entryR1/R2. Final helper results do not determine returnR0.
Separate status calls and fresh reads retained. No C implementation, freeze or completeness claim.
