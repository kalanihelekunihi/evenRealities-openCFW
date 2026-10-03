# Independent review 6067

**Result:** PASS_SCOPED.

I recomputed the selected map union from the latest instruction ledgers and confirmed their recorded instruction bytes against the locked image. The audit range [0x42863e, 0x429624) is 4,070 bytes; 29 maps contribute 1,420 candidate rows covering 3,980 unique bytes with no conflicting overlaps. The six explicit gaps are 0x42891e–0x428920, 0x428a78–0x428a94, 0x428ba8–0x428bb0, 0x428c84–0x428ca4, 0x4291e0–0x4291ec, and 0x42951c–0x429524. A separate GNU linear Thumb decode spans the full extent in 1,464 instructions / 4,070 decoded bytes.

**Limits:** This is instruction-candidate coverage accounting and a linear-decoder comparison only. It does not resolve gaps as code or data, prove entrypoints or global code/data boundaries, close semantics, or support canonical admission, freeze, C completeness, or byte-identity claims. Private evidence remains `accepted:false`.
