# Current audio lifecycle conclusions

- [Stop handshake](REPORT.md): request is thread flag0x800000; audio acknowledgment is event8, posted before cleanup. Supersedes “initial request” wording in preserved audio-exit-cleanup-closure-2026-10-08/REPORT.md and earlier navigation.
- [Task configuration and initialized scheduler](../audio-task-configuration-closure-2026-10-08/REPORT.md): static112-byte TCB/8192-byte stack at priority47; dynamic50×12 queue,680-byte allocator request. Isolated creation and noncurrent static deletion execute; scheduler never starts.
- [Dispatcher initializer](../audio-dispatch-initializer-closure-2026-10-08/REPORT.md): **0x20003FBC**, eight authenticated rows; type2→0x53C6F3. Older0x20073FBC address remains superseded.
- [Valid queue deletion](../audio-queue-delete-closure-2026-10-08/REPORT.md): no message destructor/drain; allocation ownership differs for static/dynamic queues.
- [Notification wait](../audio-notification-wait-closure-2026-10-08/REPORT.md): pending waits stop before blocking; NoClear preserves bits but clears received marker.

Next actionable source work: type0/type1 queued control callbacks0x53C860/0x53C7B0; codec/PDM unregistration/deinit gates; watchdog timer command consumer; actual pending-ready resume/waiter paths. [Static producer leads](producer-boundaries.json) remain available. Full runtime producer/ISR ordering, complete boot task population and physical DMA completion remain unverified; there is no source-exhaustion claim.
