# Independent review 6129

**Result:** PASS_SCOPED.

The locked image and dependency/artifact hashes match. The complete 232-byte range [0x42a1bc, 0x42a2a4) tiles exactly in 80 instructions, with byte-for-byte agreement and independent GNU Thumb boundaries. The selector override is R1==8 -> selector 7; otherwise the selector is the input R0. The map’s eight cases/default and fresh byte/word read pairs match the instruction ledger; the paired reads are not elided or cached. The routine merges the first five-bit value into bits 25..29, then the second into bits 8..12 using separate fresh register reads. It returns the second output pointer in R0, with R1/R2/R3 carrying the values/merged words described by the packet.

**Limits:** Static leaf review only; no execution rerun or hardware purpose claim. No canonical admission/C/freeze change; private evidence remains `accepted:false`.
