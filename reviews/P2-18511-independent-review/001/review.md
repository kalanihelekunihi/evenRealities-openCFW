# Independent review P2-18511

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 110-byte interval `0x460970..0x4609DE`; instruction/reference manifests match. It inherits R5 source base, R6 destination base, R7 index, R8 stride 52, and R9 source stride. The first child gets the source word at `R5 + R9*R7 +16`; R9 is then replaced with the computed source offset. The code computes a destination field pointer `R6 +52*R7 +4`, replaces R9 with that pointer, and calls `0x439BE4` with R0=field pointer, R2=the full previous child result, and live R1/R3. Callee semantics are not assumed.

A fresh `0x43D0CE` result gates the table lookups on bit 1. When set, the code calls `0x460084` with the destination field pointer; then passes its full return and the field pointer to `0x45FFFE`. It freshly reads destination byte +40 into SP16 and word +48 into SP12, in that order, and stores the full selector at SP8, literal at SP4, and 446 at SP0. These local writes occur only on the bit-1-set path. R9 remains the field pointer after the calls, so any next iteration must restore its prior stride before using it.

Child contracts and later diagnostics/loop test are outside the map. Partial/unaccepted only.
