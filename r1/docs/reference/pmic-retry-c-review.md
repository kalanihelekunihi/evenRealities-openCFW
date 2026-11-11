# R1 recurring PMIC retry callback in C

`runtime/native_pmic_retry.c` supplies stock callback `0x96a60`. It first schedules itself with argument zero and raw delay `0x199`, then requests battery-thread flag four through the existing wrapper and shared thread-handle owner. Incoming callback arguments and incidental return registers are ignored under the delayed worker's void callback ABI. No new state owner or executable blob is added. A full timer table or failed flag result does not undo or skip the other operation.

REA binds all 26 stock bytes, including the PC-relative self-reference and tail branch to the task-flag wrapper. Delay units and conversion remain the scheduler's contract; no wall-clock duration is inferred here.

Verification passes 288 direct stock/C pairs, 128 actual scheduler registration pairs and 64 expiry/dispatch/rearm roundtrips. The real C flag wrapper and scheduler/scheduler-state/reschedule/push/worker bodies execute, with RTOS time, lock, timer, critical-section, queue and flag leaves modeled. Coverage includes zero/full-width input arguments and flags statuses, null/full-width thread handles, live handle replacement during scheduling, mutex errors, timer errors, delayed-loop initialization waits, empty/first/last/full timer tables, tick wraparound and interrupt masks. Registered callbacks are captured, expired into the actual queue, dispatched by the actual worker and observed rearming themselves. Physical timer behavior remains unverified.

Five compiled defects are rejected: wrong delay, wrong flag, forwarding the incoming argument, omitting registration and signaling before rearming. The normal probe passes after mutation testing.

The open-toolchain build compiles 815 units (733 application, 82 bootloader), with the same 70 application imports and no new failures or duplicate strong symbols. This fills a prerequisite of the remaining NFC/charging flag dispatcher; it does not claim that dispatcher is implemented. All 814 prior source inputs are unchanged; 812 object hashes match and two generated boot objects differ with build paths. No G2 source or qualification selection is changed. Final application linking, startup RAM layout and device boot remain open.

Reproduction inputs: [pmic-retry-c-review.json](pmic-retry-c-review.json).
