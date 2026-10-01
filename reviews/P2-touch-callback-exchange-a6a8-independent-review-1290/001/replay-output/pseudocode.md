# Touch callback slot exchange A6A8

Body A6A8..A6BA is 18 instruction bytes; adjacent NOP and literal are excluded. If unsigned index exceeds four, return zero without data access. Otherwise load the old word from literal base plus four times index, store incoming R1 to the same slot, and return the old word in R0. No stack frame, indirect call or interrupt exclusion occurs. Concurrent atomicity is not established.

Sixty-three original-instruction fixtures cover all five valid slots, two invalid indices, three new words and three old words. Exact reads, writes and returns match the separate model. This establishes exchange behavior, not callback target validity or dispatch. No canonical admission or C implementation.
