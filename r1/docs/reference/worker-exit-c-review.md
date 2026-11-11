# C synchronized worker exit and persistence

`native_worker_exit.c` supplies worker exit `0x46bac`, notification broadcast `0x46d10` and the persistence wrapper `0x6ad64`. REA bytes authenticate both code windows and the diagnostic literals. Existing task contexts, thread handles and the sync-event owner are reused; no mutable state is added.

Broadcast selects the factory worker only when the full configuration result equals `0x55`, otherwise the system worker. It signals that worker, storage, sensor, battery, touch, BAE8 RX, TX1, shared TX and protocol-service threads in order with flag `0x800000`. Every handle is read when needed, including null handles. Notification results are ignored. The returned mask is `0x6df` for factory or `0x6bf` for normal configuration.

Exit logs its start, broadcasts, then reloads the live sync-event handle and waits for all mask bits with timeout `0x1400` OS ticks. It reports failure whenever the full result differs from the mask, including results containing extra bits. Regardless of wait success or failure, it runs the NV idle/flush check, persists the available health-state payload, force-flushes exported records and logs its end. The persistence wrapper initializes a halfword length, calls the existing payload getter and appends only a nonnull payload using the returned 16-bit length.

**4,440 stock/C comparisons** pass: 4,320 exit-sequence cases, 72 broadcast cases and 48 persistence-wrapper cases. They cover factory admission, zero/high-bit thread handles, live handle and event-owner mutations, every log mode and changing modes, exact/partial/error acknowledgments, null payloads and partial halfword writes. Full helper/log arguments, call order, state changes, public mask, stack restoration, saved integer/FP registers and masks agree. Modeled providers return through real Thumb instructions. All **392 native instruction bytes** execute: 216 exit, 148 broadcast and 28 persistence bytes.

**576 further comparisons** execute the actual C manager dispatcher, worker exit, status publisher/ring, payload getter and CMSIS reset request. They cover repeated exits, factory/normal configuration, full/wrapping status rings, acknowledgment errors and enabled/disabled diagnostics. The actual getter supplies 736 bytes. Remaining RTOS, hardware, persistence and logging services are modeled; physical state production is not established.

Eight compiled defects are rejected: wrong factory admission, omitted protocol worker, wrong signal flag, accepting unequal acknowledgments, skipping NV flush after wait failure, wrong timeout, truncated payload length and inverted payload admission.

The normal build compiles **861 units**, completes both relocatable compositions and has no duplicate strong symbols. All **850 prior nongenerated objects** remain identical. The direct worker object matches the normal build; the manager/reset objects used by the integrated probe also match. The manifest adds one unit with the existing task-barrier profile, R1 source validation passes and source-plan selections are unchanged.

The broad worker-exit import closes and `r1_previous_state_append_native` becomes explicit, leaving **66 application / 22 bootloader imports**. That native entry takes two arguments; the existing standalone GoMore append primitive takes seven and cannot be called with the native ABI. Its native storage binding and the payload producer lifecycle remain unfinished. No vendor state bytes or substitute implementation are introduced.

Physical task acknowledgment, storage writes, reset behavior, full application linking and boot remain unverified. Private frames, incidental void register results, APSR, concurrency and faults are excluded.

[Machine receipt](worker-exit-c-review.json) binds sources, REA evidence, normal build and ignored fixtures under `build/goal-r1-worker-exit-c/`.
