# Independent review 2203

**Result:** PASS_SCOPED.

The source and all receipt-bound files match. The dispatcher body [0x5FC6, 0x6044), mode leaf [0x5CF8, 0x5D2C), literal pool [0x5D2C, 0x5D34), and function leaf [0x5D34, 0x5D6E) match their declared hashes and independently decoded boundaries.

An isolated replay regenerated all 16,384 fixtures exactly. It executes original 5FC6, both leaves and 4492/449A without interceptions. Cases cover all valid pins, modes, functions, enable and initial PRIMASK states, and all-zero/all-one starting words. Assertions verify call order, modeword address/value, packed three-bit and high-bit updates, enable word, restored PRIMASK and saved registers/SP.

The literals and instructions support the address formula: port `0x40040000` maps to mode word `0x40020000`. 5CF8 clears and replaces the selected four-bit lane at `4*pin` with `mode&15`. 5D34 clears and replaces the three-bit field at `3*pin` with `function&7`, then separately updates bit `pin` from function bit 3. The dispatcher invokes the leaves in the stated order under the original PRIMASK wrappers.

**Limits:** Only port `0x40040000` and bounded valid pin/mode/function inputs were exercised. Invalid BKPT paths, other addresses, aliasing, concurrency and physical peripheral effects remain unverified. No canonical admission is made.
