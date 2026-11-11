# Native Goodix calculation dispatcher in C

The [SpO2 calculation control-flow review](goodix-spo2-calculate-c-review.md) adds native core control in C, including allocation/status flow and calibration semantics. Fourteen deeper processing stages remain explicit imports; this does not complete the SpO2 engine.

The [SpO2 frame execution review](goodix-spo2-execute-c-review.md) adds the C sensor adapter with bounded floating-point rounding validation and reuses the canonical channel map. All five sensor frame adapters now execute in dispatcher comparisons; `goodix_spo2_calc` remains unfinished.

The [soft-ADT execution review](goodix-soft-adt-execute-c-review.md) adds the C sensor adapter and shared green/IR event reporters, reusing the existing selector, timeout counter and capacitor flag. Timeout advancement on core errors is preserved; the `goodix_nadt_calc` computation core remains unfinished.

The [HR frame-execution review](goodix-hr-execute-c-review.md) adds the C HR adapter and disabled report. Dispatcher replays now execute real ADT, HR and HRV adapters, including the HR record consumed by HRV; calculation cores and HR diagnostics remain explicit unfinished providers.

The [HRV frame-execution review](goodix-hrv-execute-c-review.md) now adds the C adapter and disabled report. The existing `r1_goodix_hrv_initialization_count` cell is the last-HR cache during execution; it remains the same owner initialized here. HRV calculation itself remains an explicit unfinished core.

The [ADT execution review](goodix-adt-calculate-c-review.md) now supplies the wear executor, six-sample filter and soft-event reporter in C, sharing the existing ADT flags with init/deinit. Four engine executors remain unfinished.

`native_algorithm_calculate.c` implements the 190-byte stock dispatcher at `0x29e8c`. It shares the canonical started bitmap, frame-table owner and 20 initialization bytes. No persistent state, executable blob, trap or placeholder engine is added.

The dispatcher preserves live whole-bitmap gates, per-slot frame reloads and sleep-flag updates before executor gating. Unselected slots reset the result even after earlier errors. Selected unsupported slots retain it. After calculation, missing frame results receive the native 68-byte default record; an update byte exactly equal to one publishes the record to the separate output buffer. That final publication is absent from the pinned public outer dispatcher.

The C implementation passes **3,377 paired stock comparisons**, covering all 190 native instruction bytes, full nonstack RAM, helper/executor boundary snapshots, status, saved registers, stack and interrupt masks. Actual native/C sleep, popcount, fill and copy helpers execute. Only engine callbacks are modeled. Tests cover bitmap gates, initialization bytes, results/counters, signed-byte return values, live state/pointer replacement, copy aliases and two matching null-table faults. Nine compiled defects are rejected.

The normal R1 build passes **894 units** without failures or duplicate strong symbols. All 883 prior nongenerated source/object pairs are unchanged, and the tested object equals the normal object. Source-plan/cache layout remains unchanged.

Five engine bodies remain unfinished: ADT, HR, HRV, SpO2 and soft ADT. Their named imports replace the unresolved aggregate dispatcher, so application imports increase from 74 to 78; boot imports remain 22. This is a concrete dispatcher implementation and more explicit dependency accounting, not completed sensor calculation or a bootable firmware image. Physical hardware, concurrency, private frames and final executable startup/linking remain unverified.

[Machine-readable evidence](goodix-algorithm-calculate-c-review.json) records the exact stock table, helper windows, source/object hashes, test fixtures and limitations.
