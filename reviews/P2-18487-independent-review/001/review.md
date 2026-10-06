# Independent review P2-18487

Status: partial, unaccepted. No source or gate changes.

Fresh GNU ARM replay confirms the 98-byte prefix `0x4604C2..0x460524`; instructions and PC-reference manifests match. The function first pushes eight registers (32 bytes) and reserves 48 local bytes, for an 80-byte total frame. Incoming R0/R1 are retained in R4/R5. Two calls to `0x43C0E4` initialize the literal buffer pointers: first with length 892 and zero; second with length 1074 and zero. The second buffer pointer replaces the first in R7, while R8/R9 retain the second pointer. R3 remains live for both calls.

It then writes byte 1 at first-buffer offset 0, incoming-R0 low byte at +1, halfword 4 at +2, and low byte of incoming R1 (R5 narrowed) as a full word at +4. It calls `0x4905F4` with SP+28, second buffer pointer, and 1074; then `0x439C04` with SP+8, SP+28, and 20; then `0x490C32` with SP+8, a literal argument, and the first buffer pointer. The third call's full result decides whether control branches externally to `0x460568` or continues past this map through the zero branch.

Stack-passed buffers can alias local/saved slots, and child effects are unknown; no clear/copy/serialization semantics or initial stack contents are inferred. This map provides no epilogue or complete routine claim.
