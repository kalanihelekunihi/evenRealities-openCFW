# R1 Goodix initialization controller and sensor adapters in C

The [HRV frame-execution review](goodix-hrv-execute-c-review.md) now adds the C adapter and disabled report. The existing `r1_goodix_hrv_initialization_count` cell is the last-HR cache during execution; it remains the same owner initialized here. HRV calculation itself remains an explicit unfinished core.

The [ADT execution review](goodix-adt-calculate-c-review.md) now supplies the wear executor, six-sample filter and soft-event reporter in C, sharing the existing ADT flags with init/deinit. Four engine executors remain unfinished.

The [native calculation-dispatch review](goodix-algorithm-calculate-c-review.md) now supplies `GH3X2X_AlgoCalculate` in C, sharing the canonical started/frame/init owners. Its five engine executors remain explicit unfinished providers; this closes only the outer dispatcher.

The [engine setup review](goodix-engine-setup-c-review.md) implements the four engine boundaries described below. Four lower-level context constructors remain unimplemented.

`r1/src/application/goodix/native_algorithm_init.c` implements the native initialization controller, five sensor adapters, memory-status getter and disabled strategy hook. The [machine-readable receipt](goodix-algorithm-init-c-review.json) pins REA evidence, sources, objects, test harnesses and build reports.

The full license-free build compiles all 879 units without failures or duplicate strong symbols. It replaces the unresolved high-level `GH3X2X_AlgoInit` with four explicit engine boundaries, so application imports rise from 60 to 63; bootloader imports remain 22. This exposes the remaining work beneath the controller and does not establish complete sensor initialization.

| Native entry | C provider |
| --- | --- |
| `0x2a008` | `GH3X2X_AlgoInit` |
| `0x2a540` | `GH3X2X_GetAlgoMemStatus` |
| `0x2e950` | `Gh3x2xOutputValueStrategyInit` |
| `0x2b4c4` | `GH3x2xAdtAlgoInit` |
| `0x2caa4` | `GH3x2xHrAlgoInit` |
| `0x2cc5c` | `GH3x2xHrvAlgoInit` |
| `0x2d16c` | `GH3x2xSpo2AlgoInit` |
| `0x2cfac` | `GH3x2xSoftAdtAlgoInit` |

The controller returns immediately for a null frame-table owner. Otherwise it ORs the complete request into the started bitmap before checking memory readiness, which must equal exactly one. It reads the live owner, initialized byte and frame pointer in native order for each selected slot. Only an initialized byte of exactly one skips initialization. Successful callbacks store one; failures propagate the signed low byte after the strategy hook. The locked build's strategy hook has no effects.

ADT clears its three flags in native order. HR clears the current result byte and reloads the result pointer before clearing its word at offset four, including after engine failure. HRV marks the algorithm on success but always reloads the global HR frame to clear its result and resets the initialization word. SpO2 maps the engine's full-word result to success/failure. Soft ADT handles null frames, stores the function-type flags, and ignores its engine's return.

All 2,567 paired stock/C comparisons pass. They cover all 256 memory-status values, all 64 callback masks, all 20 individual bits, full/high-bit requests, initialized bytes zero/one/two/255, engine returns and failure positions, rate/type boundaries, accepted null paths and live provider changes to frame owners, result pointers and flags. All 282 native instruction bytes execute. Public reads and writes match in order, width and value; engine arguments, state snapshots, final state, saved integer/FP registers, SP, masks and guards also match. Independent oracles check the started bitmap and early returns. Source execution cannot enter stock, and modeled providers return through BX LR instructions.

Twelve compiled defects are rejected: wrong started-bitmap update, accepting an arbitrary nonzero ready byte, skipping arbitrary nonzero init flags, wrong successful flag, truncating an engine error, wrong ADT write order, omitted HR clear, clearing the wrong HRV frame, wrong HRV success condition, wrong soft-ADT type, wrong initialization-word reset, and wrong SpO2 rate.

The four modeled engine boundaries remain unimplemented:

| Native entry | Dependency |
| --- | --- |
| `0x6d3c0` | `r1_goodix_hr_engine_init` |
| `0x6df14` | `r1_goodix_hrv_engine_init` |
| `0x6ec28` | `r1_goodix_spo2_engine_init` |
| `0x32788` | `r1_goodix_soft_adt_engine_init` |

Existing frame, started, init-byte, memory and ADT owners are shared. The memory struct moves to the shared header without changing the configuration object. New state ownership comprises a four-byte initialization word at `0x20007c2c` and two flags at `0x20007c30`; only their observed initialization behavior is claimed. All 867 other prior nongenerated source/object pairs remain unchanged, and the tested object equals the normal build object. Existing generated startup and uecc objects differ.

Invalid pointers, cold FP activation, interrupt concurrency and physical sensor behavior are unproven. Caller scratch, APSR and private frames are excluded. Final RAM/startup placement, executable linking, the engine implementations, other hardware dependencies and device boot remain open. Relocatable composition is not bootable firmware; no instruction or image identity is claimed.
