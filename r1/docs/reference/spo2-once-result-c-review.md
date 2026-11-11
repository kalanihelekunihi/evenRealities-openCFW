# R1 SpO2 once-result callback in C

Stock entry 0x4abec now uses C, closing the once controller's result dependency. It reuses the existing portable 70–100 predicate, piecewise calibration and integer-division support, plus the canonical three-slot stream owner. No new state owner or assembly was added.

The callback logs all six sample fields, preserving signed byte 3 and native read order. It captures plausibility before checking health mode and reloads the value for calibration afterward. When publishing, the eight-byte topic-8 record contains the calibrated byte and seven zero bytes; no timestamp is inserted. Calibration logs read the current raw input but retain the captured converted value.

Cleanup always unregisters the incoming SpO2 handle and clears once slot zero, including rejected values, health-disabled results and failed publication. Unlike the timing callback, it does not release the timer or change completion flags.

Stock/C replay passes 5,116 cases with the actual C controller, timing callback, predicate/calibration and integer support. Coverage includes all input bytes, every byte value injected after validation, an independent calibration oracle, signed diagnostics, logging/health changes, ignored lengths, provider mutations and mixed once/timing calls. Eight compiled defects are rejected. Source execution into stock code or an unused vendor-provider trap fails the replay.

Checks compare full event records, callback identity, provider arguments/order, call-time state/input snapshots, guarded shared buffers, preserved registers, SP and masks. Tests use mapped six-byte samples even when length is zero. Private record pointers and caller-clobbered registers are excluded. Unused vendor imports are trapped rather than executed.

All 758 R1 units compile without failures or duplicate strong symbols. All 757 prior objects retain their hashes. The result import closes without new imports, leaving 131 application and 34 bootloader imports. The R1 source check passes; the global check still flags the existing G2 resident_rom_thumb_set.S manifest gap.

Stream registry, health mode, logging, event delivery and lower timer release are modeled. Calibration equivalence is established over the callback byte domain, not arbitrary signed 32-bit helper inputs. Existing integer ABI support is unchanged. Physical sensors, asynchronous scheduling, complete firmware linkage and device behavior remain unproved.

See [machine-readable evidence](spo2-once-result-c-review.json) and [REA publication/cleanup receipt](spo2-once-result-c-rea.json).
