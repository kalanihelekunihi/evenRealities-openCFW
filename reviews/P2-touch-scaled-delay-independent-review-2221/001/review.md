# Independent review 2221

**Result:** PASS_SCOPED.

The source and receipt files/ranges match their hashes. Wrapper [0xA324, 0xA332), literal [0xA334, 0xA338), and leaf [0x4480, 0x4492) have the declared extents and hashes; independent Thumb/M-class decoding agrees with the listing.

An isolated replay regenerated all 807 records exactly: 39 complete executions and 768 wrapper-prefix stops. Complete cases match the wrapped 32-bit multiplication, derived loop count, exact iterations, zero return and R4/SP restoration. Prefix fixtures stop at 0x4480 and check the multiplied argument without claiming leaf completion.

The leaf computes `W(input + 2) >> 2`, exits immediately for a zero count, and otherwise repeats ADD +1 / SUB -2 / BNE, reducing the counter by one each pass. The wrapper loads the unsigned scale byte at `0x20000870`, multiplies into R0 and calls the leaf.

**Limits:** Large positive loop counts are not completed. Scale provenance, elapsed-time calibration, physical timing, interrupt/concurrency effects and hardware behavior remain unresolved. No canonical admission is made.
