# Independent review 2233

**Result:** PASS_SCOPED.

The source hash, `[0x5868,0x58F6)` body hash, and all candidate artifact hashes match the receipt. The decoded 142-byte body supports the stated 144-byte row stride and field accesses. Type 7 branches around all updates. Otherwise, it clears parameter byte 35 bit 0 and clears item byte 6 bits 0–1 for each of the saved `count` entries at 10-byte stride. The type-6 path calls `A9D4(row+40, parameter+32 byte, count*2)`; types 2/3/5 copy that byte to the first timer byte only when row byte 122 equals 1. Types 2–5 clear parameter byte 40, and clear descriptor byte 4 only when the low byte of row word 112 is nonzero. R4 and SP are restored; R0 has no promised status meaning.

An isolated replay regenerated all 486 fixture rows. The only intercepted function is `A9D4`; the replay verifies its arguments and models its fill. Assertions cover all exercised type/count/validity/config combinations, timer and item bytes, parameter/history updates, and R4/SP. The fixtures test counts 0, 1, and 3, so the per-item loop is checked at empty, singleton, and multi-item cases.

**Limits:** The fill implementation itself is outside this candidate’s proof; this replay supplies its behavior. Index validity, dynamic type/pointer mutation, aliasing, concurrency, and physical meaning are not established. No canonical admission is made.
