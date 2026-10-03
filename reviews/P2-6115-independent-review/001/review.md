# Independent review 6115

**Result:** PASS_SCOPED.

The pinned dependencies and packet files match their receipt hashes. All instruction bytes match the locked image; GNU Thumb decoding confirms the recorded boundaries for [0x429f68, 0x42a030) (200 bytes, 74 instructions).

This 32-byte-frame routine computes first/second row pointers from its inputs, then writes four masked metadata fields at SP0..SP3, overwriting saved R3. The second-row low/high fields and both indexed metadata values are discarded; first-row high/low fields are retained in R7/R8. A fresh bit-0 test skips polling when clear. Otherwise it loops up to 60 with fresh bit-30 status reads, delaying/incrementing only while clear, and then calls the helper. It publishes the argument/index and fresh row fields, makes the a1bc call with (R5,R4) and ignores the result, then returns packed metadata from SP0 in R0 while restoring R4-R9/PC/SP. No row-field register modification follows the publication.

**Limits:** Static review only; no execution rerun. This is local source-flow evidence only, not child/hardware semantics, global ownership, canonical admission, or C/freeze approval. Private evidence remains `accepted:false`.
