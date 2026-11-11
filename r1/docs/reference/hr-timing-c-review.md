# R1 HR timing callbacks in C

The timing callback at 0x49ae8, result callback at 0x49b60 and timeout at 0x49c64 now use C. Existing HR handle, HRV timing and result-validation owners are reused; no new state or assembly was added.

The timing callback requires a nonzero health mode and enabled configuration flag. When no timing HR stream exists, it registers one and creates a 120,000-unit timeout only after a successful new registration and when the timeout field is zero. Existing streams skip timeout creation even when their timer field is zero. Authorization slot 5 and HRV/SpO2 timing plans still run after a failed registration.

The result logs the three sample bytes and publishes an eight-byte HR/timestamp event only for a plausible value in health mode two. It then unregisters the incoming stream, clears timing handle slot 1 and invokes the existing HR timer release. Timeout logs, optionally unregisters the current timing stream, always disables slot 5, releases its incoming timer and clears the stored timeout late.

Stock/C replay passes 3,024 direct/result/timeout and mixed-sequence comparisons, including all HR byte values, gate combinations, existing handles/timers, failures and provider mutation. Eight compiled defects are rejected. Another 2,328 comparisons execute the existing configuration gate and KV record getter with failed/partial reads and poisoned fresh/mixed stacks.

Two non-inlined C helpers keep the configuration getter at the native caller depth under the normal Clang profile. The NV replay verifies the record offset and consumed flag byte. Other unwritten private scratch bytes can differ and are excluded because this getter invocation reads only the flag byte at record offset 24. Revalidate this depth contract after compiler/profile changes. Existing NV getter assembly remains unchanged.

All 755 R1 units compile with no failures or duplicate strong symbols. All 754 prior objects retain their hashes. The timing callback import closes without new imports, leaving 134 application and 34 bootloader imports. The R1 manifest check passes; the global check currently flags the concurrent G2 resident_rom_thumb_set.S manifest gap.

The NV replay models KV class reads, while direct tests model the configuration flag provider. Other boundaries include companion HRV/SpO2 plans, authorization, stream/timer services, logging, health mode, clock and event delivery. Registered callbacks are checked by identity and their bodies execute as explicit roots/mixed sequences. These checks do not establish asynchronous timer delivery, physical NV/sensor behavior, complete firmware linkage or final hardware operation.

See [machine-readable evidence](hr-timing-c-review.json) and [REA timing-callback receipt](hr-timing-c-rea.json).
