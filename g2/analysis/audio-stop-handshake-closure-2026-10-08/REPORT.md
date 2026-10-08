# Audio stop handshake: request, acknowledgment, then cleanup

**72 PASS original/independent selected-first-party comparisons**:48 fanout,12 single-stop wait-entry and12 successful audio acknowledgment/cleanup cases. Actual OS notification, event-set, queue initialization/delete/free, context and critical/suspend/resume peers execute; no result stubs. Independent C reconstructs the coordinator/exit prefix and reuses original OS peers, not an independent entire kernel. [Source](../../components/audio/stop_handshake_offline/stop.c), [results](results.json), [instructions](original-disassembly.txt).

## Correction: event8 is the audio acknowledgment

This successor supersedes the earlier sealed exit report's description of 0x4C9C3C(3) as an initial stop **request**. The full static relationship is now recovered: thread-manager 0x4C96B6/0x4C95BC sends **thread flag0x800000** to the thread handle at audio context0x20003F98+8. The audio handler0x53CDAC tests bit23 and enters exit0x53CDC2. Exit calls0x4C9C3C(3), which sets event **0x08** in the manager event group from0x200040D8+0x1C. The manager waits for this corresponding bit. It is therefore an acknowledgment in this handshake. Older sealed artifacts remain unchanged.

**Audio posts its acknowledgment before timer stop/delete and before queue deletion.** Tests now use a real nonnull empty-wait-list event group: event bits are actually set before original queue-delete/free entry, then queue handle clears and the task reaches delay entry. Timer is NULL in these executed cases. This proves selected sequential call/store order and successful acknowledgment; it does not show a manager running concurrently, actual preemption, producer stopped, cleanup completed when wait returns, or a manifested hardware race. Acknowledgment must not be treated as a cleanup-completion fence without further evidence.

## Fanout and waits

Fanout ignores each osThreadFlagsSet return and accumulates its expected acknowledgment mask regardless of null handles or setter errors. All calls request0x800000. Order and masks:

| Context base | Expected acknowledgment |
| --- | --- |
| 0x200040FC | 0x02 |
| 0x20004120 | 0x40 |
| 0x20004044 | 0x800 |
| 0x20003FFC | 0x80 |
| 0x20004020 | 0x100 |
| 0x20004068 | 0x200 |
| **0x20003F98 (audio)** | **0x08** |
| 0x2000408C | 0x10 |
| 0x20003664 | 0x20 |
| 0x20000658 | 0x1000 |

Reason bit5 skips the three middle contexts0x20003FFC/4020/4068; returned mask is0x187A instead of0x1BFA. Six reason patterns, four handle-presence patterns and IPSR0/15 compare actual nonwaiting notification state and call arguments. Null-handle errors really execute; requested mask still includes that thread's bit. These are synthetic fixtures, not proof of missing handles on hardware.

Single-stop0x4C95BC sends0x800000, then calls osEventFlagsWait(group,1<<index,WaitAll=1,**20000 ticks**). Tests stop before wait entry, not after timeout or wake. Broader coordinator0x4C9778 statically waits for accumulated mask with WaitAll and **5000 ticks**, logs a mismatch, then proceeds through its function exit; this function's whole wait is not executed. No milliseconds/frequency or cleanup-success assertion follows from these literals.

## Successful selected exit and ownership

Four existing event values0/8/16/24 × queue absent/static/dynamic produce12 comparisons. A real original queue initializer0x441696 prepares50 entries×12 bytes in synthetic coherent storage. Dynamic fixture contains a688-byte heap block (680 payload/object bytes+8 header); actual free returns688 bytes to its free list. Static marker leaves allocation untouched. Actual event-set uses an empty waiter list, timerNULL, taskcount0/running1 to skip pending task processing. This is not a complete coherent live application scheduler.

No destructor/drain is called by queue-delete; the selected exit contains no producer-stop acknowledgment beyond its own early event. No explicit DMA disable appears in this selected exit. That does not prove other threads fail to stop peripherals. Queue handle clears after actual successful delete here, unlike the preceding deliberately synthetic ISR-error examples. Shared data copies, DMA status and interrupt delivery are not modeled.

The remaining producer-deinit call chain is recorded separately in producer-boundaries.json. Available static code includes codec/PDM owner unregistration, queued control messages, recording/file cleanup and encoder setup; those names/calls must not automatically be reclassified as a hardware DMA stop. Actual lifecycle reachability, ordering relative to this early acknowledgment and live producer/ISR activity remain unproven.

Reproduce build_offline.py then opencfw venv verify.py. Preserve prior945 sealed entries,110 audit inputs,four checkpoints; no commits,index,production/device changes. Next actionable source leads: follow queued stop/control messages through dispatcher callbacks0/1, execute deinit gates/providers, timer command consumer and valid event waiter/resume behavior. Missing live trace restricts scheduling/physical claims; source leads are not exhausted.
