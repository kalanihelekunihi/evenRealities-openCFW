# Independent review 6119

**Result:** PASS_SCOPED.

I independently recomputed the latest instruction-ledger union against the locked source. In [0x42863e, 0x42a04a), 49 maps contribute 2,321 candidate rows covering 6,512 unique bytes of the 6,668-byte extent, without byte conflicts. A GNU linear Thumb disassembly has 2,398 rows over the extent. The 11 explicit gaps are: 0x42891e–0x428920, 0x428a78–0x428a94, 0x428ba8–0x428bb0, 0x428c84–0x428ca4, 0x4291e0–0x4291ec, 0x42951c–0x429524, 0x429624–0x42962c, 0x429700–0x429718, 0x429a1e–0x429a30, 0x429d9e–0x429da4, 0x429df6–0x429e00.

**Limits:** This audit measures candidate-byte union and compares a linear decode only. It does not classify gaps, establish code ownership or semantic coverage, or authorize canonical admission/C/freeze. Private evidence remains `accepted:false`.
