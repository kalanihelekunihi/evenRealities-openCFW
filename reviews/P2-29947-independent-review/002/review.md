# Independent review 29947 — attempt 002

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-third-fp-sequence-lowbyte-status-gate-frame3408-middle-30346-map/001`. This corrected attempt binds the assigned map30346 candidate; attempt 001 is preserved separately. The candidate receipt and all five listed file hashes match. Independent reassembly confirms 100 locked bytes and 34 contiguous instructions over `[0x4EABC4,0x4EAC28)` with no gaps or mismatches.

The initial SP-relative raw S0 load and conversion, followed by the fresh R4+68 load and helper calls, match the instructions. The next raw loads independently read SP+328 into S0 and convert to D1, then read SP+332 into S0 and convert to D0. The subsequent fresh R4+72 helper path uses current SP as its buffer argument. D1 aliases S2/S3; S0 aliases D0's low half and the VCVT destinations update the stated overlapping registers. Actual post-call state is carried forward without ABI assumptions.

The later fresh SP+376 word and SP+384 pointer precede raw S2/S1/S0 loads from SP+380/+340/+336, with the stated aliases. `MOVS R0,R5` sets N/Z and preserves C/V. Following opaque `4FF4C0`, its actual R0 is truncated to low byte and tested; zero branches to the excluded continuation. The nonzero path loads literal `0x4EB4A0`, sets R0=20, then narrow `MULS R5,R0` updates N/Z and preserves C/V; the following high-register ADD does not update flags. Fresh current `[R4+64]` feeds `498680`.

FP conversion claims were checked against Arm DDI0553B.y C2.4.323 and E2.1.172 (printed pages 1074, 1995-1996): architectural `ExecuteFPCheck`, FPSCR-controlled `FPSingleToDouble(..., TRUE)`, NaN/DN and exception behavior, and exact widening for non-flushed finite values are retained. This is bounded partial evidence, not helper or global-coverage proof.
