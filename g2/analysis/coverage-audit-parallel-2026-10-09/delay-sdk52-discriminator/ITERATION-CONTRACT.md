# Bounded delay iteration comparison

The selected stock instructions authenticate the arithmetic path: unsigned input is converted to binary32, then converted to unsigned fixed point with five fractional bits (equivalent here to truncating `f32(us) * 32`). Performance status 2 selects conversion of that integer to binary32, multiplication by 250, division by 96, truncation to unsigned integer, then adjustment 24. Other status values use adjustment 15. The loop is called only when the unsigned raw count exceeds adjustment. SDK 5.2 uses integer `83 * us + (us + 1) / 3`, adjustment 25 for HP, and `32 * us`, adjustment 15 otherwise.

[38 predictions](iteration-predictions.json) cover zero, all three small-input residues modulo 3, intermediate-product rounding boundaries, and binary32 input precision around 2^24. [Reproducible derivation](derive-contract.py) uses binary32 rounding at every stock arithmetic step. These are arithmetic predictions, not passed firmware comparisons. They require round-to-nearest ties-to-even for floating-point arithmetic and truncating integer conversions. An execution receipt must authenticate FPSCR state before using them; no unknown rounding state is silently normalized. All selected final raw counts are within uint32 bounds, avoiding unspecified/out-of-range C conversions. SDK unsigned intermediate sums also remain in range for these inputs.

| Input us | Mode | Stock loop argument | SDK 5.2 loop argument |
|---:|---|---:|---:|
| 0 | either | no call | no call |
| 1 | LP | 17 | 17 |
| 1 | HP | 59 | 58 |
| 2 | HP | 142 | 142 |
| 3 | HP | 226 | 225 |
| 16777217 | LP | 536870897 | 536870929 |
| 16777217 | HP | 1398101352 | 1398101392 |

HP input 1 is the smallest clear discriminator. HP input 2 is an equality control: the new nearest-thirds integer formula compensates the changed adjustment for this residue. LP input 16777217 distinguishes input precision loss; integer input is rounded to 16777216 in binary32 stock conversion. The large cases must stop at loop entry rather than execute hundreds of millions of iterations.

Recommended finite owner execution boundary: enter authenticated stock wrapper with chosen r0 and seeded performance-status register, capture whether BL at 0x4807ea is reached and r0 immediately before entering ITCM 0x40, then stop. This executes the wrapper rather than an intercepted delay provider; it does not claim the loop ran, scatter initialization succeeded, or physical microseconds elapsed. Synthetic register seeding and any instrumentation must be declared. Actual FPU exception/rounding behavior remains platform-dependent until checked. No execution was performed by this audit.

This independent work adds predictions only and does not duplicate sealed tests. Whole-ledger coverage, source completeness and byte equality do not advance from these 38 rows. The existing public-source contract is available; the bounded unresolved item is execution of wrapper arithmetic under authenticated runtime state, separate from physical delay calibration.
