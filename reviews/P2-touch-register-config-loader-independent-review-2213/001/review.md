# Independent review 2213

**Result:** PASS_SCOPED.

The source and all receipt files match their declared hashes. Code [0x8FD0, 0x915C) and pool [0x915C, 0x9178) match the declared range hashes and boundaries; the stored listing agrees with Thumb/M-class decoding.

An isolated replay regenerated all 480 fixtures exactly. It verifies zero request before version read, full-word version equality/mismatch statuses, selectors 0–7, three source/factory patterns, the 28 sparse copies, the eight-word block and three seven-word blocks in order, and selector-specific factory-byte stores. Ordered destination-write ledgers, return values, R4 and SP match.

The instructions support the listed sparse destination offsets and block-copy strides. The selector is source word 68 low three bits. Selectors 0/3/6 read factory-byte pairs at offsets 158/160, 149/151, and 140/142 from `0x0FFFF000`, storing widened words at base+`0xFF04` and base+`0xFF0C`. Unsupported selectors return `0x01260001` after prior copies; version mismatch returns `0x01260003`; zero request returns `0x01260001` before reading version.

**Limits:** Factory bytes are synthetic, not authenticated recovered contents. Source and destination are separate RAM allocations; aliasing, faults and concurrency are not covered. No physical MMIO behavior or canonical admission is established.
