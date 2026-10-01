# Touch delay and interrupt-mask helpers

4480..4492 is an 18-byte arithmetic busy loop. Compute q = u32(input + 2) >> 2. If q is nonzero, increment once and subtract two each iteration, so the net decrement is one and exactly q iterations occur. Return R0 zero. Two NOP instructions are executed according to the branch path. PRIMASK is preserved. This establishes instruction counts, not physical elapsed time.

4492..449A is an eight-byte helper: return prior PRIMASK in R0, disable configurable interrupts, return through LR. 449A..44A0 is a six-byte helper: set PRIMASK from R0, whose implemented bit is bit zero, preserve R0, return through LR. Neither uses a stack frame.

Original-instruction fixtures cover delay inputs zero through 100 and the two addition-wrap inputs, with both initial masks. Mask helpers cover five raw inputs and both initial masks. Counts are derived in the receipt; exact loop iteration counts, returns and masks are checked. No C implementation or canonical admission. External interrupt dispatch and physical timing remain unresolved.
