# Independent review P2-18525

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 60-byte continuation `0x460C3A..0x460C76`; instruction/reference manifests match. It inherits header R4, source base R5, index R7, and source stride R9=44. Separate fresh mask calls test bit 0 then conditional bit 2. On the bit-2 path, R7 is replaced by `low32(R9*R7)`; it reads word at source base+offset+48 into R3, then calls `0x43CE9E` with literal selector and mask. The R7 replacement occurs only on that route.

The shared diagnostic route sets R1=1 and R0=low8(R4), calls `0x4604C2` with live R2/R3, and ignores its result. It then calls `0x4601EA` with the full previous child result and original R1/R2/R3 live, without argument reset; its result is also ignored. Finally R0 is set to `0xFFFFFFFF` and control branches to external `0x460D56`. This is the failed-lookup/nonzero-result route; successful zero results took the earlier `0x460A44` route.

Post-lookup key loads remain fresh and are not cached. The epilogue and completion branch are outside the map; underlying child contracts remain unresolved. Partial/unaccepted only.
