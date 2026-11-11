# Touch identity probe C control flow without fixed-register constraints

Current implementation: [ordinary C identity status ABI](touch-probe-pure-c-review.md). The remaining R3 bindings described below have been retired.

`board/native_touch_identity.c` now expresses its power sequence, polling counter and cleanup using ordinary C control flow. Removed the fixed-R4 counter, unused fixed-R5 binding and repeated empty assembly barriers. The incoming/outgoing R3 bindings remain because the stock boundary exposes the complete saved word in R3; this change does not claim an assembly-free probe.

The current compiler emits a 16-byte probe frame, reduced from 24 bytes. Stock also uses 16 bytes, but the private word occupies a different location. The optimizer represents the polling counter differently in R4. Private counter encoding and complete frame byte identity are excluded; public polling behavior is checked. Caller R4–R11 are preserved on return. R5–R11 are also checked at modeled provider entries; live R4 is excluded for the full probe because it holds the compiler's private counter representation.

All 928 ready-reader pairs and 2,592 complete identity-probe pairs pass against the locked stock application. The actual production request and ready-reader helpers execute. Cases cover readiness on reads 1, 2, 3, 99 and 100, exhaustion, every ready byte, raw provider statuses, changing cached handles, untouched/partial/full ID buffer updates, incoming word seeds and late cleanup mutations. Provider order/arguments, delays, polling count, final R0 and full R3, SP, masks and caller-preserved registers agree. A separately compiled 99-poll defect is rejected at the exhaustion close boundary, confirming that excluding the private counter encoding did not remove the polling-limit check.

The fixture normalizes private buffer pointers as in the earlier identity review. It checks the new frame and pointer positions explicitly. GPIO, power, delay and final registry boundaries are modeled; electrical behavior, actual timing, arbitrary aliases/faults/concurrency and caller-clobbered registers other than R0/R3 are unproven. There are no memory-read hooks.

Existing authenticated REA raw-byte evidence is retained in `build/goal-r1-touch-identity-c/rea.json`; the complete local body is also disassembled from the locked ELF through its final POP. The current REA/Ghidra session has no defined procedure at `0x5128c`, so this review does not claim fresh function-dossier coverage for that entry. The locked ELF and raw application hashes still identify the analysis reference.

All 720 R1 units compile and compose with no failures or duplicate strong symbols. The other 719 objects remain byte unchanged from the preceding touch-wrapper build. Application / bootloader imports remain 177 / 34, both source manifests pass, and the source plan is unchanged. No instruction identity, complete firmware C closure, flashing, commit or publication is claimed.

[The receipt](touch-probe-c-review.json) binds production hashes, replay, the defect control, frame disassembly and the unchanged-object audit.
