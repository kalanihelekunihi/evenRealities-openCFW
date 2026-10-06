# Independent review P2-18515

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 106-byte branch `0x460A44..0x460AAE`; instruction/reference manifests match. It inherits source/destination bases, index, stride, and source stride. The code replaces R9 with `low32(R9*R7)`, reads source word at source base plus that offset plus 48, and writes it to destination base + destination stride*index +48. No other default-field or copy writes are present in this span.

A fresh `0x43D0CE` bit-1 gate controls repeated table lookups. When set, it calls `0x460084` with the destination field pointer, then `0x45FFFE` with the full prior result and a separately recomputed pointer. It freshly reads destination byte +40 to SP16 and word +48 to SP12, stores the full selector in SP8, then writes literal and 439 to SP4/SP0 before calling `0x43D574`. These are local stack slots. On this branch, R9 remains the source offset rather than becoming a destination pointer.

Later masks/loop tests and branch-entry selection lie outside the span; no alternative-entry premise is added. Child contracts remain unresolved. Partial/unaccepted only.
