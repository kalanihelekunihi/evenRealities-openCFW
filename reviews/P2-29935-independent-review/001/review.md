# Independent review 29935

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-stack-float-widening-two-resource-helper-frame3408-middle-30334-map/001`. Candidate receipt and all five receipt-listed file hashes match. I independently reassembled the locked 100-byte interval from the pinned image and decoded a contiguous 27-instruction extent `[0x4EA950,0x4EA9B4)` with no byte mismatch.

Instruction and narrative review passed for the three `STR.W IP,[SP,#-4]!` / `LDR.W IP,[SP],#4` save-restore pairs and the resulting per-load effective addresses; the fresh loads and helper arguments; and the actual post-call state treatment. The FP register overlap is correctly represented: each `VLDR S0` writes D0's low word; `VCVT D0,S0` writes aliased S0/S1, while `VCVT D1,S0` writes aliased S2/S3. No register preservation is assumed across helper calls.

I checked the conversion claims against Arm DDI0553B.y, printed pages 1074 and 1995-1996. The encoded operation is `FPSingleToDouble(S[m], TRUE)` after `ExecuteFPCheck`; FPSCR-controlled classification, DN-dependent NaN handling, signaling-NaN InvalidOp processing, signed zero/infinity, and exact finite widening are represented as architectural behavior. APSR flags remain unchanged by the decoded FP operations. This does not claim host-cast equivalence or successful memory access in every execution environment.

The evidence supports only this bounded map. Continuation, helper behavior, global coverage, source completeness, freeze, and byte equality remain unproved.
