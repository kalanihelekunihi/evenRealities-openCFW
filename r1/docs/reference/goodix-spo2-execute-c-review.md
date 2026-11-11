# SpO2 sensor frame adapter in C

The [channel-assembly review](goodix-spo2-assemble-c-review.md) adds the real C assembler and parity helpers, with live enable/PPG integrity effects checked through the C core. The remaining numeric decoder is explicit as `r1_goodix_spo2_decode`; the complete computation engine is still unfinished.

The [packet-layout correction](goodix-spo2-packet-layout-c-review.md) makes the enable mask and following PPG samples one C object. It preserves the assembler12-byte scan and live integrity-write aliasing that the earlier four-byte boundary checks did not cover. The deeper processing stages remain unfinished.

The [SpO2 calculation control-flow review](goodix-spo2-calculate-c-review.md) adds native core control in C, including allocation/status flow and calibration semantics. Fourteen deeper processing stages remain explicit imports; this does not complete the SpO2 engine.

The [SpO2 math review](goodix-spo2-math-c-review.md) adds the native calibration polynomial as a separate C owner. The calculation core and its other processing stages remain unfinished.

`native_spo2_execute.c` implements the frame adapter and disabled native result reporter: **380 native instruction bytes**. It reuses the canonical channel map and adds no persistent state.

The adapter preserves sparse channel selection, signed accelerometer input, AGC driver-byte addition, gain masking, descending enable bits, accepted statuses0/3/4 and the exact-one result flag. Output includes HB mean, the duplicate rounded result and mask255/count8. Signed integer conversion precedes float32 division by10000 and the existing round helper.

Validation passes **4,433 stock-versus-C comparisons**:

- 1,044 direct cases include independent packet and exact rational floating-point oracles, all four active rounding modes/status bits and81 matching selected faults.
- 3,389 dispatcher cases execute all five actual sensor frame adapters. Computation cores, diagnostics and logging remain modeled.
- Both fixtures execute all380 new native bytes and74 reused round-helper bytes. Sixteen compiled defects are rejected. Full nonstack RAM, boundary snapshots, saved registers, stack and masks agree; source cannot execute stock.

The round proof is limited to the finite signed32/10000 domain reached by this adapter. It does not establish the full arbitrary-input helper contract or cold physical FPU behavior.

All **899 R1 units** compile and compose without failures or duplicate strong symbols. The tested object equals the normal object;888 prior nongenerated source/object pairs and source-plan/cache files are unchanged. The aggregate adapter import is replaced by unfinished `goodix_spo2_calc`, leaving78 application/22 bootloader imports.

This is relocatable composition. SpO2 computation, remaining dependencies, final startup/placement and physical hardware validation remain unfinished.

[Machine-readable evidence](goodix-spo2-execute-c-review.json) records contracts and exact hashes.
