# R1 sensor output lifecycle dispatcher in C

Stock entry 0x6c294 now has a native-interface C dispatcher, closing the accelerometer/raw-heart-rate ready gate's output dependency. It reuses the canonical sensor workspace and authorization table and the existing C timestamp, sensor-update, failure-counter, interval-dispatch and completion functions.

The dispatcher stamps inputs, updates the algorithm and processes active authorization slots only after success. Slot zero submits activity output, slot one skips, slot two performs the observed volatile float load and no-op, and slot three handles sleep period and PPG transitions. Sleep-on takes priority over sleep-off. Off/final output allocates and clears 2,880 bytes plus an 88-byte local record and count, calls interval extraction and publishing, and frees the payload. Allocation failure logs and skips the remaining slot-three stage transition. Stage comparison is signed and the final enable decision reloads the current authorization flag after logging/providers.

The stock/C replay passes 1,264 cases over all low sleep flag combinations, every seven-slot authorization mask, signed stage values, allocation failures, helper results, output counts, dynamic log modes and controlled provider mutation. A further 678 comparisons execute the existing C timestamp, failure-counter and completion helpers with the actual shared data owners. Ten compiled behavioral defects are rejected. Comparisons include provider order/arguments, output record and payload contents, guarded state, return, preserved registers, SP, masks and FPSCR.

VFP is warmed before assigning test FPSCR because Unicorn resets it on first VFP use; first-use FP/exception behavior is outside this proof. Local addresses are normalized by contents, with no claim for providers retaining private stack addresses. Sensor-update internals and downstream activity/report/publish/authorization calls are modeled in these new tests; asynchronous execution and physical sensor behavior remain unproved.

All 745 R1 units compile, with zero failures or duplicate strong symbols. All 744 prior objects are identical, including the stream adapter whose declaration was updated to match the dispatcher's return type. Relocatable composition has 140 application imports and 34 bootloader imports. One dispatcher import is removed; activity accumulation and sleep reporting are exposed as two lower dependencies. The repository-wide `make sources-check` passes for both G2 and R1.

See [machine-readable evidence](gomore-sensor-output-c-review.json) and [REA branch-table confirmation](gomore-sensor-output-c-rea.json). This establishes the tested source contract, not complete firmware linkage or physical-device operation.

The subsequent [activity accumulator review](activity-accumulator-c-review.md) now closes its activity dependency and replays this dispatcher with the actual C accumulator. Sleep reporting remains a lower dependency.

The subsequent [sleep report/shared-state review](algo-sleep-report-c-review.md) now supplies the report and consolidates activity mode with the canonical sleep/wake state at 0x20006ed4. The updated getter/default-mode callers and mixed transitions are replayed there.
