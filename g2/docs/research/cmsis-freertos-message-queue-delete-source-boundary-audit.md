# G2 CMSIS-FreeRTOS message-queue-delete source boundary

Status: source-integrated in the Apollo-main production overlay  
Target: official G2 `s200_v2.2.6.10`

## Result

`osMessageQueueDelete` at `[0x00449BEC,0x00449C14)` is now production
source-owned. The complete 40-byte stock entry has SHA-256
`dc66684591191cbe28c76ffd3154eef13bd038db3bde6184e65b4cca6a336212`
and six external callers. Its disassembly proves `configQUEUE_REGISTRY_SIZE ==
0`: the only calls are private `IRQ_Context` and `vQueueDelete`; no queue
registry unregister call survives.

The 2,254-byte Apache-2.0 adapter
`components/apollo_main/core_overlay/runtime_cmsis_message_queue_delete.c`
has SHA-256
`2a58f7ecbbc10e3a36430c5afbbd78483475afa68baf0023cd6d587c10846994`.
It preserves the upstream validation order: interrupt context returns
`osErrorISR` even for a null handle, task-context null returns
`osErrorParameter`, and a valid task-context handle is deleted once and
returns `osOK`.

## Closed dependencies

Apple Clang 21 emits a 36-byte unrelocated leaf with SHA-256
`2630db26e0e251aae8f4e6548ee2e318a3a81a708fbfc281145d104023ec6282`.
Its only relocations are a Thumb call at `+4` to
`open_cfw_cmsis_irq_context` and a Thumb call at `+22` to
`open_cfw_freertos_queue_delete`. Both providers were already production
source-owned. The wrapper treats the queue handle as opaque, reads no Queue_t
or TCB field, and introduces no hardware dependency.

## Reproducible promotion-milestone outputs

| Profile | Overlay | Apollo-main provider | Core-source package |
|---|---|---|---|
| Apple Clang 21 | 132,152 / `03038b536d313071be3e7f1423f7a36807908d7c9279b3ede50b11361989197b` | 3,655,548 / `9598dd9b51bb2cb614a4a901d2eddbe45becf3daeab875f65e1496cfcbbe327a` | 4,434,042 / `0c432b329a45a965931f0ea72e119fc19eb7d89b2f0dbcb688c27e772676f5a1` |
| Linux Clang 22.1.8 | 134,020 / `a2d42c2920c61bfaf4f14386edac09242575aa711051f229f77e05f5ccd90184` | 3,657,416 / `efd03e54e0b88c5612458778a84cd5a23a23f15cbdb18327ea87b3a84620e009` | 4,435,910 / `5d117e80538dd212448a3b8f9e999893b2bdc51aae426e4943b2bfb7b02a5148` |

Apple package accounting is 132,881 source, 93,430 generated, and 4,207,731
opaque bytes. Linux accounting is 134,901 source, 93,278 generated, and
4,207,731 opaque bytes. No package was signed or flashed and no hardware was
accessed.

## Verification and next seam

`tests/test_runtime_cmsis_message_queue_delete.py` authenticates source,
fixture, upstream and stock bytes; pins both target relocations; host-executes
all three validation paths; and checks atomic production registration.

Run `make -C openCFW cmsis-freertos-message-queue-delete`.

At the four-leaf promotion milestone, CMSIS production ownership reached
thirteen public APIs plus private `IRQ_Context`; 25 public APIs and four
private helpers remained stock-backed.
`osThreadYield`, `osKernelGetState`, `osMutexDelete`, and
`osTimerIsRunning` were subsequently promoted as one dual-profile tranche.
