# Independent review 2587

**Result: PASS_SCOPED.**

Candidate `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-pending-state-adjust-2586/001` binds to the pinned source. The receipt and artifact hashes, code span `[0x42CDF8,0x42CEA4)`, and six-pointer literal span `[0x42D7A0,0x42D7B8)` match. The isolated replay passed all 1,152 original-instruction cases.

The tests cover the gate/mode guard, flag-controlled boost 15, low-byte index selection (step 10 for indices 0/1), and both arithmetic branches. The independent oracle confirms saturating subtraction when step exceeds boost; otherwise 32-bit wrapped addition followed by saturation to 127 at totals ≥128. Only destination bits 0–6 are replaced. Active calls return the destination pointer in R0; inactive calls preserve incoming R0. The memory oracle verifies exact writes/no-writes, preserved destination bits, status/PC, SP and high registers across threshold, wrap and guard inputs.

Base/state inputs remain stable fixture memory. The replay does not exercise concurrent changes between fresh loads or physical register semantics, and caller ownership remains unresolved. Private evidence only; accepted:false and no canonical admission.
