# Touch source switch 9F44

Body 9F44..9F8E is 74 instruction bytes, excluding the adjacent NOP and three literal words. Unsigned requested selector greater than one returns the invalid-input literal without peripheral access. Otherwise actual 9F34 freshly reads current bits 1..0 at 40030028. An already-selected source returns zero without checking readiness or writing.

For a changed selector zero, freshly read 40030030 and require bit 31. For changed selector one, actual 9C38 reads RAM 20000F20 and requires a nonzero word. A failed prerequisite returns the disabled-source literal. A successful change freshly reads 40030028 again, replaces bits 1..0 with requested selector, stores once and returns zero. The frame restores R4 and SP. No polling loop occurs.

Original-instruction fixtures cover invalid requests, all four current selectors, both enable states, three RAM frequencies and three upper-register patterns. Counts are recorded in the receipt. Exact reads, writes, return and frame restoration agree with the separate model. Synthetic register values establish instruction behavior; physical clock readiness and concurrent changes remain unresolved. No canonical admission or C implementation.
