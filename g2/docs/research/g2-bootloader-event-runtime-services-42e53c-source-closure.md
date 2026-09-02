# G2 bootloader event runtime-services source closure

Three functions are now source-owned MIT C: runtime object/task initialization
at `0x0042E53C..0x0042E642`, the queue-driven callback loop at
`0x0042E644..0x0042E686`, and callback enqueueing at
`0x0042E686..0x0042E6F2`. Their direct ingress is limited to `0x0042E27A` and
`0x0042E79C`; no stored entry pointers target them.

Apple clang 21 and Homebrew clang 22 reproduce all 436 authenticated bytes
exactly from mnemonic-only Arm source under fourteen strict call relocations.
Portable tests cover idempotent object initialization, failed creation, task
replacement, callback dispatch, absent queues, and enqueue failures. Live
retained RAM, RTOS objects/tasks, scheduler queues, callbacks, logging, timing,
interrupt, reset, and cold-boot behavior is blocked by unavailable physical evidence.
