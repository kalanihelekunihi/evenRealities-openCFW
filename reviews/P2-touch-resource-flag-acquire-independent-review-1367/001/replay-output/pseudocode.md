# Touch resource flag acquisition 8FA0

Body8FA0..8FC8 is40 instruction bytes, followed by two errorliterals. Require nonzeroR0,R1,R2 in thatorder orreturn invalidliteral. Freshlyload byte atR2; nonzero returnsbusyliteral. Otherwise store lowbyte ofR1 atR2 andreturnzero. R0's pointedresource is notdereferenced; it is onlycheckednonnull. No interruptmasking,frame or atomicoperation occurs.

Receipt-derived originalinstruction fixtures include zero/nonzeroarguments, busyflags and owner256, which passesnonnullguard butstoreszero. Exactflagwrites andreturns matchindependentmodel. Realresourceeffects,atomicity andpointervalidity remainunresolved. No canonicaladmission orCimplementation.
