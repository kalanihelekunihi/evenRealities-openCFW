# FreeRTOS event groups in the radio/WSF handoff

This is a source-backed provider increment, linked by `event-group-wsf-simulator` with the existing radio/GPIO and WSF modules. The WSF handle at0x20074ef0 is an EventGroupHandle_t, not a TCB. Earlier generic provider names `opencfw_wsf_notify_task/isr` are retained as adapter interfaces; they now call actual event-group APIs. Older targets/evidence remain preserved.

Four API texts are copied unchanged from MIT-licensed FreeRTOS Kernel V10.5.1 commitdef7d2df2b0506d3d249334974f51e427c17a41c: xEventGroupSetBits, vEventGroupSetBitsCallback, xEventGroupSetBitsFromISR and xTimerPendFunctionCallFromISR. Full Amazon MIT notices are retained. SOURCE_PROVENANCE.json pins public files, Gitblob identities, exact function text hashes, stock ranges and sparse ABI adaptations. This is semantic source correspondence, not byte-equal compiler output or complete kernel implementation.

The task-context setter suspends scheduling, ORs low24 event bits, visits each waiter using its saved next pointer, records pre-clear bits in matched waiters, then clears the union requested by matched clear-on-exit waiters. It resumes scheduling and returns the final event bits. A return of zero can mean successful consumption by a matched waiter; it is not a failure status. Invalid handle/reserved high control bits trigger the task-context assertion path.

The ISR wrapper performs no immediate event-group validation or bit mutation. It sends a16-byte daemon command(-2,callback,borrowed group pointer,bits) through the timer queue at pointer cell0x20074ab0. Its return is the queue result. A successful enqueue of an invalid group/mask can therefore fail later in the callback. The event group must remain valid through deferred execution. Production queue-send must synchronously copy the stack-local packet; this batch tests that contract with a synthetic copy provider but does not implement or prove the real queue copy.

Build: `make -C g2 event-group-wsf-simulator`. Compare: `make -C g2 event-group-wsf-simulator-test EVENT_GROUP_SIM_REPORT=build/foundation/event-group-wsf-simulator/new.json` (fresh output required). Installed native OpenCFW Python/Unicorn is required on this host.

The sparse ABI is32-byte EventGroup,20-byte List/Item,16-byte daemon packet. Scheduler suspend/resume/unblock, real queue-send/copy, wait, context, timer tick and application handlers remain production boundaries. The owned fixture provider object replaces the two old notification stubs while preserving other providers; the actual event-group/WSF/radio code executes. No TCB ready-list insertion, timer-daemon scheduling, blocking wait, object destruction/quiescence or physical IRQ safety is claimed.

See ../../../analysis/event-group-wsf-2026-10-05/REPORT.md for original instruction comparisons, practical implications and exact remaining requirements.
