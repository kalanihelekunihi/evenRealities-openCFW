# Independent review 2583

**Result: PASS_SCOPED.**

The candidate `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-power-pre-post-callbacks-2582/001` binds to the pinned flash source. Receipt, artifact and two body-range hashes match. The isolated replay passed all 72 cases.

The pre-hook sets the flag byte and returns zero. The post-hook saves/disables/restores PRIMASK, checks the pending byte, conditionally calls `0x42CDF8` with the current index byte, ignores that result, clears pending when nonzero, and always clears the flag. The test ledger confirms conditional call order/argument, critical-section writes, zero status and R1/R2 epilogue values along with SP/high-register/PRIMASK preservation. Input variation covers pending 0/1/255, index 0/28/255 and both PRIMASK values.

The child callback is controlled, so its implementation and physical effect are not established. Pending/index mutation between loads, concurrency, installation and caller ownership remain unresolved. Private bounded evidence only; accepted:false and no canonical admission.
