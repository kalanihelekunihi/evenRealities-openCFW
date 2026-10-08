# Floating exponent callback, numeric output, padding and return

Partial/unaccepted;104 instruction bytes4838A0..483908. R0 is staged E/e, R2 prior position, R9 priorposition+1. R3=R5,R1=R10,R0=UXTB(R0),BLX callbackR4 (ignore callback result). SignedR7<0 setsR0=1 else0; signedR7<0 thenR7=-R7 wrapping (INT_MIN retained). Ordered stack writes5→SP20,R8--wrapping→SP16,0→SP12,10→SP8,UXTB(R0sign)→SP4,R7magnitude→SP0. R3=R5,R2=R9,R1=R10,R0=R4;call48320A unsigned radix numeric formatter;R9=resultR0.

FlagsR6bit1clear→483900. Set enters4838F6: reloadinitialpositionSP24 each condition;R0=R9-initialmod;unsignedR0<R11→spacecallback at4838E8 withR3R5,R2R9,R1R10,R0=32;ignorecallbackresult;R9++wrap;repeat. Exit483900 setsR0=R9. Fallback direct483902 retains483350resultR0 without this assignment. ADDSP28 thenPOP R4..R11/PC36,release64B. Preserve sign after callback, savedinitialposition and ordered stack values. No C,freeze,wholecoverage or equalityclaim.
