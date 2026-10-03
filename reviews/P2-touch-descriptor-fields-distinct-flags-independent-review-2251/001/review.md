# Independent review 2251

**Result:** PASS_SCOPED.

The source, `[0x51BC,0x52B6)` body, `[0x52B8,0x52BC)` literal, and all candidate file hashes match the receipt. Decoding agrees with the conditional configuration-byte selection, bit-12 bypass, group threshold, masks, ordered destination writes, zero return, and preserved R4–R8/SP.

An isolated replay regenerated all 5,832 fixtures. Unlike the predecessor, this packet varies configuration bytes 90/91/92 independently across all 27 combinations. For validities 1, 2, and 10, those fixtures distinguish the byte selected by each branch. The two destination writes, final words, return status, and preserved registers are asserted. Count, group, bypass, and source-pattern dimensions remain as in the packet’s bounded matrix.

**Limits:** Invalid pointers, aliasing, concurrent mutation, and physical field meanings remain unresolved. No canonical admission is made.
