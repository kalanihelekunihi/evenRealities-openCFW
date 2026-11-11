# R1 one-shot HR stream control in C

Stock entry 0x497cc now uses C, exported as r1_hr_once_measurement_control and the registered event-service alias. It reuses the existing four-word HR handle array, HRV timing state and session buffer. No new state owner or assembly was added.

A nonzero enable value returns immediately when the HR once handle exists. Otherwise it lazily registers the HRV/algo stream with the existing HRV producer, then registers the HR/once stream with its result callback. Both registration arguments remain one. HR registration still runs after a failed HRV registration. Disabling unregisters only HR and clears only its handle, leaving the shared HRV stream intact.

The direct handler ignores length, while the existing event adapter enforces length one and normalizes its input. Stock/C replay passes 1,512 direct, actual-adapter and mixed enable/teardown/timer-release cases, including failed registrations, preexisting handles, repeated calls and synchronous provider mutations. Eight compiled defects are rejected. Tests compare callback identities, provider arguments/order, call-time state snapshots, full guarded shared state/buffer contents, preserved registers, SP and masks.

All 752 R1 units compile without failures or duplicate strong symbols. All 751 prior objects are identical. Relocatable composition has 136 application and 34 bootloader imports: the control service closes and the HR once-result callback becomes explicit. The R1 manifest check passes; the global check currently flags the concurrent G2 resident_rom_thumb_set.S manifest gap.

Stream registration/unregistration, timer release, logging and memory clear are modeled. Registered result/producer callbacks are checked by identity and not invoked. Existing event-adapter assembly remains unchanged and executes in the replay. These checks do not establish physical streams, asynchronous scheduling, complete firmware linkage or sensor operation.

See [machine-readable evidence](hr-once-control-c-review.json) and [REA controller receipt](hr-once-control-c-rea.json).

The subsequent [HR result review](hr-once-result-c-review.md) now closes the result callback and executes mixed control/result calls with the same state owners.
