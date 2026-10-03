# Independent review 6117

**Result:** PASS_SCOPED.

The pinned dependencies and packet files match their receipt hashes. All instruction bytes match the locked image; GNU Thumb decoding confirms the recorded boundaries for [0x42a030, 0x42a04a) (26 bytes, 11 instructions).

The three two-byte leaves at 0x42a030/32/34 are BX LR and leave R0/stack/memory unchanged. The wrapper uses an eight-byte frame, reads its flag afresh, and calls 0x429da4 only when nonzero, ignoring that result. It then sets R0=0 and POPs into R1 and PC, so R1 receives the saved incoming R7; SP advances by eight.

**Limits:** Static review only; no execution rerun. This is local source-flow evidence only, not child/hardware semantics, global ownership, canonical admission, or C/freeze approval. Private evidence remains `accepted:false`.
