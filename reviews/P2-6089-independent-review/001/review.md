# Independent review 6089

**Result:** PASS_SCOPED.

I verified the source/dependency hashes and instruction bytes against the locked image. The 34-byte interval [0x4299fc, 0x429a1e) tiles exactly in 12 instructions under the ledger and independent GNU Thumb disassembly. The first fresh register load targets the same address as the low-seven-bit field publication in 6084: both resolve to 0x42a080. The next fresh load reads SP4-selected metadata and BFI replaces the low seven bits at that same register address. The final POP aliases R0 to the row pointer in SP0, R1 to selected metadata in SP4, and R2 to packed metadata in SP8, restoring R4-R11/SP/PC. The extent ends before 0x429a1e alignment bytes.

**Limits:** Static local-flow review only; no execution rerun. Pairing with 6082/6084/6086 supports this routine’s local flow, not child/hardware meaning, canonical admission, or freeze/C gates. Private evidence remains `accepted:false`.
