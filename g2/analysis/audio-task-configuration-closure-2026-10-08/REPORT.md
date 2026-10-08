# Audio task configuration and static ownership

**Three bounded PASS original/independent wrapper comparisons**: actual thread creation, dynamic queue allocation entry, and noncurrent static-task termination. Actual original CMSIS/kernel peers run as shared dependencies; independent C covers first-party wrapper logic, not an independent task allocator/scheduler. [Source](../../components/audio/task_configuration_offline/config.c), [results](results.json), [instructions](original-disassembly.txt).

## Authenticated thread parameters

Initializer0x53C344 calls osThreadNew0x4490E2 with handler0x53C52D, argumentNULL and attribute record **0x75B8C8**. Attributes in locked bytes:

| Field | Value |
| --- | --- |
| Name | pointer0x78EBB4, string `audio` |
| Attribute bits | 0 |
| Control-block memory / bytes | **0x20072300 /112 (0x70)** |
| Stack memory / bytes | **0x20360E18 /8192 (0x2000)** |
| Priority | **47**, passed unchanged to kernel |
| TrustZone module / reserved | 1 /0 |

CMSIS wrapper accepts supplied CB+stack and calls actual static-task creation0x454820 with stack depth2048 words, priority47, the supplied memory and authentic handler/name. It does not allocate this task's TCB/stack dynamically. Recorded initial audio context0x20003F98 begins with initializer0x53C345 and terminator0x53C4F3, followed by NULL task/queue handles. Those fields come from authenticated compressed startup data, not guessed live RAM.

## Initialized scheduler evidence and limits

The fixture installs all17,752 previously verified startup-data bytes and starts mapped BSS at zero. Actual task creation completes, stores task handle0x20072300, sets task count1/current TCB, highest priority47 and ready-list47 count1; the TCB state-item container is that ready list. Notification value/state remain0. Scheduler-running global0x20074A3C remains0. These independent expectations verify **a real isolated initialization path**; no thread handler, scheduler start, context switch or exception delivery executes. Zeroed BSS is inferred from authentic initialization records and modeled initial RAM, not a hardware RAM snapshot. Whole-system task population/priorities/order are not recovered here.

For termination, fixture creates audio and a second higher-priority48 static task through actual kernel creation; the latter becomes current while scheduler remains unstarted. Actual audio terminator0x53C4F2 → osThreadTerminate0x4491FE → state/delete peers removes **noncurrent** audio from ready list47, decrements task count2→1, retains current second task/ready list48, clears audio state-item container and finally global handle. No vPortFree entry is allowed: static TCB/stack storage is retained. This is not self-delete, live scheduling, idle deferred reclamation or proof that peripherals/callbacks no longer reference audio resources.

## Queue configuration

Resource initializer0x53C3EE calls osMessageQueueNew0x449A32 with **50 entries,12 bytes each,NULL attributes**. Actual wrapper selects dynamic kernel queue creation0x441636. It requests **680 bytes** at original malloc0x456110:80-byte queue object+600-byte item storage. Test stops **before malloc's first instruction**; no fake allocation return, queue handle store or timer continuation. Separate successful cleanup tests initialize this actual50×12 queue layout in synthetic storage, not a malloc-derived runtime queue.

Original thread handler statically runs counter-reset/codec-mode/resource initialization before waiting for low24-bit flags with timeout0xFFFFFFFF, then routes bit22 drain and bit23 exit. Handler resource order is static evidence, not executed in these creation comparisons. The watchdog timer and whole boot sequencing remain open dependencies.

Reproduce build_offline.py then opencfw venv verify.py. Decoder result hash is checked against sealed startup proof. Passive RAM and Cortex-M4-compatible Thumb execution do not model full M55/peripheral behavior. Prior945 seals,110 audit inputs and four checkpoints remain intact. No production/index/commit/device changes. Next source leads: task configuration for other fanout contexts, actual timer commands, queued counter-control callbacks and producer-deinit gates; actual runtime synchronization needs initialized live scheduler/ISR evidence beyond these isolated fixtures.
