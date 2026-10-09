# Independent review 29943

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-three-raw-fp-loads-second-lowbyte-status-gate-frame3408-middle-30342-map/001`. Receipt and five candidate file hashes match. Independently reassembled the 84 locked bytes as 25 contiguous instructions covering `[0x4EAAF6,0x4EAB4A)` with no gaps or mismatches.

The initial fresh SP-relative word and address values, three separate R12 save/restore pairs, and raw `VLDR` addresses match the instructions. S2 updates D1's low half, S1 updates D0's high half, and S0 updates D0's low half; no FP conversion occurs in this interval. After `MOVS R0,R7`, `4FF4C0` is called with the actual R0. Its returned R0 is truncated to low byte then compared with zero; the zero branch exits at the excluded boundary. The nonzero path loads the literal at `0x4EB4A0`, assigns R0=20, and executes narrow `MULS R7,R0`, which updates N/Z while preserving C/V. The following high-register `ADD R1,R7` does not update flags. Fresh current `[R4+40]` supplies the final call's R0. Calls remain opaque and no ABI preservation is assumed.

Partial evidence only; continuation and helper semantics, whole-image completeness, source completeness, freeze, and byte equality remain unproved.
