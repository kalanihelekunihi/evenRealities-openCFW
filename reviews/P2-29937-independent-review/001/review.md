# Independent review 29937

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-three-raw-fp-loads-lowbyte-status-gate-frame3408-middle-30336-map/001`. The receipt and all five receipt-listed candidate file hashes match. I independently reassembled the locked 86-byte span from the pinned image and decoded 25 contiguous instructions over `[0x4EA9B4,0x4EAA0A)` with no byte mismatch.

The fresh SP reads, three distinct R12 save/restore sequences, and computed word addresses match the candidate. The loads are raw `VLDR` writes: S2 aliases D1's low half, S1 aliases D0's high half, and S0 aliases D0's low half. There is no FP conversion in this span. The call `4FF4C0` receives the actual R8 value in R0; the returned R0 is truncated to its low byte and compared with zero, with the zero branch reaching the excluded continuation. On the nonzero path, the literal at `0x4EB4A0` is freshly loaded; `MOVS R0,#20` sets N/Z while preserving C/V; the subsequent `MUL.W` is non-flag-setting, and the high-register `ADD R1,R8` is also non-flag-setting. Fresh `[R4+16]` supplies R0 to `498680`. The helper's behavior and preserved registers are not inferred.

Scope is limited to this exact partial interval; the continuation, external call semantics, and firmware-level completeness remain unresolved.
