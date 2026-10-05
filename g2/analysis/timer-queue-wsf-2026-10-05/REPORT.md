# Timer-command queue producer integrated with radio/WSF

The callable timer-queue-wsf-simulator now links actual FreeRTOS xQueueGenericSendFromISR and prvCopyDataToQueue, unchanged function texts from pinned MIT-licensed V10.5.1 queue.c, with the existing EventGroup, WSF, radio pin117 and GPIO sources. Sparse compatibility config disables queue sets and retains the mutex branch with an explicit unimplemented priority-disinherit provider. Reconstructed byte-copy and BASEPRI helpers are ordinary executable C/inline assembly, not opcode arrays. No production firmware was modified.

## What the ISR handoff actually owns

Radio GPIO IRQ/callback -> WsfSetEvent(ID7,event1) -> WsfSetOsSpecificEvent -> xEventGroupSetBitsFromISR -> xTimerPendFunctionCallFromISR -> xQueueGenericSendFromISR -> prvCopyDataToQueue -> memcpy.

The timer-pend wrapper passes a stack-local16-byte command {-2, callback47ee1f, borrowed EventGroupHandle_t, bits}. Queue producer copies uxItemSize bytes synchronously to pcWriteTo before incrementing count and returning; its write pointer advances and wraps at pcTail. Stack reuse after return no longer relies on an intercepted copy fixture. The command bytes are queue-owned; the pointed-to group is still borrowed. Successful enqueue does not establish group validity or grant ownership to delete it.

If full, send returns0 without changing storage/count or clearing the caller's higherPriorityTaskWoken. On success with cTxLock==-1, a nonempty receive wait list calls xTaskRemoveFromEventList. Only a nonzero provider result with a nonnull output sets *higherPriorityTaskWoken=1; it is otherwise preserved. This is the timer-queue receiver wake indication, not proof that the WSF task executes immediately. Locked queues skip receiver removal and increment cTxLock only below uxTaskGetNumberOfTasks;127 overflow is an assertion when taskcount exceeds127. Unlock and deferred wake processing are not implemented here.

Explicit synthetic dequeue reads the copied packet, updates a fixture count/read pointer, then invokes the real callback and real task setter. That validates packet retention, callback arguments and downstream event behavior but does not execute xQueueReceive or the production timer daemon. Native valid receive-list manipulation/ready insertion, actual daemon scheduling and destruction/quiescence remain external boundaries.

## ABI and masking

Recovered Queue fields: head+0,write+4,tail+8,read+12; send waitlist+16,receive waitlist+36; messages+56,length+60,itemsize+64; rxlock+68,txlock+69. The sparse configured structure is80bytes, but producer execution does not independently prove every unused trace/allocation field. The16-byte timer packet is fixed by its original caller; arbitrary queue layout/construction is not recovered in full.

Original0x5fa0a4 saves BASEPRI and writes0x30 with DSB/ISB;0x5fa0ba restores saved BASEPRI. All three initial masks0/20/60 execute and restore. This differs from WSF's nesting-byte critical exit, which enables interrupts when depth reaches zero and does not restore prior PRIMASK. Ambiq's separate critical provider restores PRIMASK. They are intentionally not interchanged.

WSF stock SetEvent aliases handler_id&15 and truncates masks to8bits; only10handler slots dispatch. IDs10/11 affect padding,12..15 affect queue-head bytes. ID23 aliases radio7; this is faithful stock behavior, NOT a checked public adapter. Nested depths0/1/254/255 and prior PRIMASK0/1 are exercised, including byte wrap. Applications should use documented IDs0..9 and byte event masks; no added bounds-checking changes the stock API.

## Validation and limits

Fresh comparison-reviewed.json: PASS569cases,1554distinct original instruction bytes. Independent expectations check producer counts, full/failure storage immutability, back-copy content/wrap, higher output preservation and lock count; direct front/overwrite cases also compare stock/source. Tests include empty/full queues, capacities1/2/4, pointer wrap, locked/unlocked state, receiver results/null output, zero-size nonmutex items, invalid queue/item/overwrite arguments, deferred invalid group/mask, and radio disable->pending IRQ->dispatch. Exact API/source hashes and ELF are bound by the result manifest. Source compiler uses the existing Thumb2 Cortex-M4 compatible subset for native emulation; actual target remains Cortex-M55, and compiler-byte equality is not claimed.

New disjoint original bytes404: send200/240 at441952,copy120/134 at441ed8,memcpy48 traced bytes within the166-byte contiguous hash envelope at439be4 (Ghidra body104bytes; the envelope includes adjacent/fallthrough code),setmask22/22 at5fa0a4,restoremask14/14 at5fa0ba. Omitted branches include assertion fault/loop tails and the copy-helper mutex priority-disinherit path. Declared body sizes do not become executed coverage. Deduplicated cumulative evidence is2974bytes (touch234,Apollo2740); shared prior WSF/EventGroup/GPIO code counted once.

Fresh foundation-test:47passing tests. Fresh aggregate:37modules,203tests_run,198passing methods,0failures/errors,6skips. The previous font-generator class setup skip now passes4methods; the three new queue tests account for the other increase. Saved native and aggregate artifacts are in g2/build/foundation/timer-queue-wsf-simulator/ and are ignored build output. Versionable source/contracts/review/evidence are under components/foundation/freertos_queue and this analysis directory.

Correction: older EventGroup reports called0x5fa0a4 a diagnostic; it is the BASEPRI mask helper. Invalid cases stop at that helper entry before fault store/endless branch; they do not execute a full fatal hardware path. Current normal enqueue executes both actual mask helpers. Actual scheduler receivers/taskcount remain stubs, as do EventGroup unblock/resume and context/wait/ticks/app handling. Queue sets, actual receiver/daemon, allocation/deletion, concurrency and hardware behavior remain unverified. No source-complete or byte-identical firmware claim is made.

The next useful bounded increment is xQueueReceive's nonblocking timer-message path and negative-command callback dispatch, followed by actual event-list removal/ready insertion only with coherent scheduler state. Preserve group lifetime until the real daemon drains; this batch does not certify an epoch or owned-buffer firmware patch safe.

## Navigation through the linked foundation work

| Evidence directory | Implemented/understood area | Remaining runtime boundary |
| --- | --- | --- |
| ../touch-mmio-cycle-2026-10-05/ | Touch SCB RX/TX/trigger and FIFO | MMIO/device timing; trapped BKPT observation |
| ../ambiq-mspi-cycle-2026-10-05/ and ../ambiq-mspi-lifecycle-2026-10-05/ | MSPI interrupts/enable/disable | CQ/delay and hardware |
| ../ambiq-cmdq-disable-2026-10-05/ and ../ambiq-critical-2026-10-05/ | CMDQ and PRIMASK critical provider | Some lifecycle/provider fixtures |
| ../ambiq-gpio-irq-2026-10-05/ | GPIO registration/IRQ status/clear/service | W1C/callback/hardware publication |
| ../radio-gpio-consumer-2026-10-05/ | Pin117 callback and radio event consumer | Physical ISR delivery |
| ../wsf-radio-handoff-2026-10-05/ | WSF pending/dispatch/nesting/sleep | Timers/messages/app handlers |
| ../event-group-wsf-2026-10-05/ | SetBits, ISR wrapper, timer pend, callback | Waiter scheduler/lifecycle |
| This directory | ISR queue producer, data copy, BASEPRI helpers | Actual receive/daemon/ready insertion |

Counts are disjoint original execution evidence across these profiles, not implementation completeness. The earlier broad knowledge batches retain their own evidence and are not newly counted by this foundation ledger.

Independent review identified and corrected a verifier storage-range guard that used the memory-write width instead of queue item size. The final comparison-reviewed.json reruns all569cases with full storage-range BASEPRI checks. Earlier first/model/final outputs remain historical and are superseded by this reviewed result.
