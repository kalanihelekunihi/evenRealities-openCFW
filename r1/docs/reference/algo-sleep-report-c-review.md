# R1 sleep result report and shared state in C

Stock report entry 0x4a7f4 now uses C. It logs the low status byte, writes that byte to sleep-active state, publishes a one-byte topic-12 event, then multicasts kind 3 using the same live payload. Only a transition from state zero to status exactly one starts the vivo probe; the decision is captured before publishing, so payload/state mutations during either call do not alter it.

Activity mode and sleep-active state both refer to native byte 0x20006ed4. The earlier C implementations allocated separate copies. The activity getter and default-mode callback now use the existing sleep/wake control owner's first byte through a shared header. The duplicate one-byte object is removed; the eight-byte sleep control, padding and timer retain their owner.

Stock/C tests pass 744 direct and mixed sequences across report, getter, default-mode callback and force-wake. Cases cover low-byte truncation, active values beyond zero/one, log mode changes, mutations of the live payload, first-transition detection and timer decisions. A further 1,264 comparisons execute the sensor-output dispatcher, activity accumulator, sleep report and shared mode getter together. Eight compiled defects are rejected.

All 747 R1 units compile with zero failures and duplicate strong symbols. Of 746 prior objects, 744 retain their hashes. The two changed callers retain allocated instruction bytes and only rename data relocations from the removed byte to the canonical owner. Application imports remain 139: the sleep-report import closes and the vivo-probe starter becomes explicit. Bootloader imports remain 34; repository-wide source checks pass.

The new probes model vivo probing, multicast/event delivery, logging, temperature and force-wake internals, timer services and relevant algorithm boundaries. They compare call order/arguments, state/payload contents, mixed-path shared state, preserved registers, SP and masks. Private payload addresses are normalized by contents; asynchronous behavior, physical sensor transitions and full firmware linkage remain unproved. Existing timer frame assembly is unchanged.

See [machine-readable evidence](algo-sleep-report-c-review.json) and [REA report-order confirmation](algo-sleep-report-c-rea.json). The existing sleep/wake initialization evidence establishes the shared owner's cold bytes; no new state allocation or initializer was added.

The subsequent [vivo probe review](sleep-vivo-probe-c-review.md) now closes the starter import and executes report/start/stop mixed transitions using the same sleep owner.
