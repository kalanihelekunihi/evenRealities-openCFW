# Comparison and return 0x46931C..0x469388

Partial/unaccepted;108 instruction bytes. Inherit32-byte frame, R5 earlier bool, SP16 original R0 word. Load unsigned byteSP16 toR0; truncateR5 in place low8; compareR5 toR0. Equalbranches sharedreturn469384 withR0 originalinputbyte. UnequalsetsSP0=4, R3=0, R2=1, R1=SP16, R0=266; call464F76. Thus child receives pointer tosavedinputword plus stackextra4; do not infer immutable input or childcontract. SaveFULLchildresultR4; FULLzero branchesreturn withR0=0.

Nonzero child: fresh43D0CE bit1 enables SP8=R4, SP4=literal469B60, SP0=126, R3=literal469B4C, R2=literal469B38, R1=literal469B3C, R0=1 ->43D574. Separatefreshbit0 orconditional thirdfreshbit2 enables R1=literal469B64, R3=R4 fullsavedchildresult, R2=R1, R0=0x04400000 ->43CE9E.

Shared469384 ADD SP20 skips16 localbytes AND savedoriginalR0word, thenPOP R4/R5/PC consumesremaining12, restoring32-byteframe. R0 remains live; no blanket bool/zero return: earlier globalguard diagnosticpath also reachesreturn, equality path returnsinputbyte, childzero path returns0, otherpaths retain mask-shift orlastchildresult. Savedinputword may be writable via464F76. No C, acceptance, runtimeorwholecorpusclaim.
