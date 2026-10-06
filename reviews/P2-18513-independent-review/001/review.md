# Independent review P2-18513

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 102-byte span `0x4609DE..0x460A44`; instruction/reference manifests match. The opening logger call uses R0=3, R1/R2 literals, and R3 literal from the inherited path. Subsequent flag branches make fresh `0x43D0CE` calls. On the bit-0-clear/bit-2-set route, it computes the destination field pointer, calls `0x460084`, then calls `0x45FFFE` with the full first result and a separately recomputed field pointer. It retains the selector in R3 and literal `0x461560` in R1.

The code then freshly reads byte at destination entry +40 and stores it at SP4. It replaces R8's stride value with `low32(R8*R7)` and freshly reads word at destination base plus that offset plus 48, storing at SP0. It next calls `0x43CE9E` with R2=the retained selector and R0=`0x0CC00000`. These repeated table lookups are separate calls, not cached; R8 replacement occurs only on this diagnostic branch. The alternate route joins external `0x460B00`.

The diagnostic stack writes are local and can overwrite earlier logger arguments. The loop/test and later body are outside this map; no stride-reset behavior is asserted. Partial/unaccepted only.
