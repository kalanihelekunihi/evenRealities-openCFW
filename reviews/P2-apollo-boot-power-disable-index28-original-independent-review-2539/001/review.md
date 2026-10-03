# Independent review 2539

**Result: PASS_SCOPED.**

The reviewed candidate is `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-power-disable-index28-original-2538/001`. Receipt, pseudocode, replay and fixtures match declared hashes; source images and inventory pins also match. The isolated replay passed all 12 cases.

For index 28, the original path clears E000EDFC bit 24, performs ordered independent reads/clears of bit 0 then bits 1–3 at `0x40020250`, runs the null pre-wrapper, performs the PRIMASK-protected control clear, calls the decision helper and inequality poll, then reaches the null post-wrapper. The individual-mask condition enables the final wrapper call. The fixtures confirm order, exact writes, poll reads/delays, return, SP/high-register/PRIMASK restoration for immediate, second-read and timeout readiness. The decision helper returns 1 for this group; that result is ignored by the caller.

Callbacks are null in fixture RAM; ITCM/FPU and clock setup are assumed fixture state. Hardware effects, physical transition, nonnull callbacks, other index paths, concurrent changes and enclosing ownership remain unresolved. Bounded private evidence only; accepted:false, no canonical admission.
