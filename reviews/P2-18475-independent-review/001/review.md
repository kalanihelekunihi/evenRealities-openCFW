# Independent review P2-18475

Status: partial, unaccepted. No source or gate changes.

Fresh GNU ARM replay confirms the 66-byte interval `0x460302..0x460344`; instruction and PC-reference manifests match. The entry is the loop body reached from the prefix after an initial test. It reads the source byte using the current halfword at ring base +258, stores to output plus `low16(R2)`, then separately reloads +258, increments and applies signed division/MLS modulo 256 before storing the halfword. Only after that store does it freshly read +260, decrement, and store it. R2 then increments. These operations are alias-sensitive; count and index are not cached across iterations.

The loop test compares `low16(R2)` and `low16(R1)` unsigned. On exit it replaces R1 with its low 16 bits and copies that to R0 before the shared POP/BX LR, so the normal return is the selected low-16 length. Prefix error/empty values can reach the same epilogue unchanged. The span itself has no null guard, count recheck, or child call. The inherited prefix assumptions are limited to the preceding local map; later routine behavior is not inferred.

No source/gate changes or global coverage claim.
