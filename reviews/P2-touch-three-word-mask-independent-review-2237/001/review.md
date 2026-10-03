# Independent review 2237

**Result:** PASS_SCOPED.

The source hash, `[0x5188,0x51BC)` body hash, and candidate artifact hashes match the receipt. The 26 decoded Thumb/M-class instructions agree with the pseudocode: it loads and caches the three original words, writes each masked value in order, then conditionally writes `original | mask` to word 0/1/2 according to mode bits 2/1/0. Those selected writes use the cached original values. The shifts test the intended mode bits; R0 and R2 remain unchanged, while the pushed R4–R6 and SP are restored.

An isolated replay regenerated all 288 fixtures exactly. The fixture assertions compare the complete ordered write ledger, all three output words and four-byte tail, R0/R2/R4/SP, and vary upper mode bits independently of the low selection bits.

**Limits:** Fixtures use separate input/output storage and synthetic RAM. They do not establish aliasing, concurrent modification behavior, physical register meaning, or hardware effects. No canonical admission is made.
