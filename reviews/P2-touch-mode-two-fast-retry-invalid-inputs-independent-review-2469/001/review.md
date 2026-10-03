# Independent review 2469

**Result:** PASS_SCOPED.

Candidate: `g2/build/pseudocode-first/20260930T190500Z/analysis/touch-mode-two-fast-retry-invalid-inputs-2468/001`. Receipt SHA-256 `32675bb94eae6e9fb94edc817134d38396c82deb0eef79c811dcad4197a4df17`; all four declared file hashes match and the ten body spans match the pinned source image.

The isolated replay passed all 120 cases. Each case first runs a successful original mode-two transition with version 2 and supported selector 0/3/6, then mutates both inputs to version 1 and selector 7 before a second request 2. The second call takes the same-mode equality path: no additional port/pin or loader calls, no further destination writes, and zero return. Assertions check the first transition boundary, complete call/write totals, final port configuration, PRIMASK, and R4–R11/SP. Firmware routines run original instructions without interception.

**Limits:** Version and selector are changed together, so their bypass effects are not isolated from each other. This does not establish concurrent mutation behavior, corrupted mode handling, or physical MMIO/factory behavior. Private evidence only; accepted:false, no canonical admission.
