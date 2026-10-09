# Independent review 29941

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-stack-float-widening-second-resource-helper-frame3408-middle-30340-map/001`. The candidate receipt and all five listed file hashes match. I independently reassembled the locked 100-byte span into 27 contiguous instructions over `[0x4EAA92,0x4EAAF6)` without gaps or byte mismatches.

The three R12 predecrement-save/postincrement-restore pairs and their effective memory addresses agree with the decoded instructions: current SP before each save plus 1460, 1456, then 1460. The `VLDR S0` loads raw bits and the following `VCVT` operations write D0, D1, and D0 in order; S0 aliases D0's low word and D1 aliases S2/S3. The intervening opaque calls are represented with actual arguments and post-call state rather than an ABI preservation assumption. Fresh `[R4+44]` and `[R4+48]` reads feed the two 49942E calls.

The conversion treatment matches Arm DDI0553B.y C2.4.323 and E2.1.172: `VCVT.F64.F32` performs `ExecuteFPCheck` and `FPSingleToDouble(..., TRUE)` under the actual FPSCR, including architectural input classification, DN-sensitive NaN handling, signaling-NaN InvalidOp, signed zero/infinity, and exact widening of non-flushed finite values. The candidate preserves the architectural exception/fault model and does not substitute a host cast. NZCV are unchanged by these FP operations.

The result is limited to this exact bounded interval. Continuation, helper behavior, global coverage, source completeness, freeze, and byte equality are not established.
