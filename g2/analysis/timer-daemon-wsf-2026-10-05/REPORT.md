# Source-defined timer callback receive and dispatch

The new `timer-daemon-wsf-simulator` links a nonblocking receive reconstruction, the pinned copy-out helper, task-port critical helpers, and a negative-command daemon drain with the previous ISR queue, EventGroup, WSF, radio pin117 and GPIO sources. `g2/components/foundation/freertos_daemon/` contains ordinary C, not retained firmware opcodes. No firmware image was changed.

## Actual stock caller and source lineage

The timer task loop at `0x47e878` calls `0x47e97a` at `0x47e886`. This 278-byte command processor was omitted from the old Ghidra function census, but its raw code is authenticated against the locked image. At `0x47e992`, it loads the timer queue through the shared literal `0x47eb6c = 0x20074ab0`, passes its stack buffer and timeout zero, then calls `xQueueReceive` at `0x441b0a`. The producer's literal was not the only instruction referencing this shared literal pool; the missing census entry hid the caller.

When the signed command is negative, `0x47e9b0` calls the pointer at stack+4 with stack+8 and stack+12 as arguments, then loops back to receive. A zero receive result exits via `0x47ea8c`. Every negative ID is dispatched as a callback; there is no restriction to -2 or callback-pointer validation in this branch. The actual producer uses -2. Positive timer processing begins at `0x47e9b8` and is an explicit unsupported boundary in this module.

`receive_copy.c` copies `prvCopyDataFromQueue` from MIT-licensed FreeRTOS V10.5.1 commit `def7d2df2b0506d3d249334974f51e427c17a41c`; only static visibility is removed, and the body is unchanged. The full Amazon MIT notice is retained. `daemon.c` is a bounded reconstruction of the pinned `queue.c` zero-timeout receive and `timers.c` negative-command branch, not an unchanged complete xQueueReceive/prvProcessReceivedCommands implementation. Blocking receives and positive timer commands are not provided. SOURCE_PROVENANCE.json distinguishes these categories.

## End-to-end ownership

| Stage | Storage and owner | Demonstrated boundary |
| --- | --- | --- |
| ISR timer-pend caller | Stack-local 16-byte command; caller owns it | Send copies synchronously before return |
| Queued command | Queue-owned slot holds ID, callback, group pointer and bits | FIFO storage survives caller stack clobber |
| Nonblocking receive | Copies item bytes into receiver-owned stack buffer | Advances/wraps read pointer and decrements count before callback |
| Negative-command callback | Receives copied group pointer and bits by argument | Runs after receive has left task critical section; source setter executes |
| Event group | Still borrowed from producer through callback | Neither receive nor dispatch frees, retains or validates its lifecycle |

Read pointer advances by item size before copying and wraps to head at tail. Empty receive returns zero without changing the output buffer. A successful receive can call the sender-waiter removal provider and request PendSV if that provider reports a higher-priority task. Queue slot release occurs before callback invocation, so producers may reuse that slot; dispatch uses the copied stack command, not the old queue slot. Exact producer/consumer queue geometry and valid initialized objects are preconditions, not recovered boot-state facts. Only the used queue-prefix offsets are proven by these paths; the compatibility declaration's 80-byte configured size is not proof of every unused field or allocation size.

An invalid event-group handle/reserved mask may be enqueued and copied out successfully before the callback reaches its task setter's invalid branch. Queue acceptance is not validation of the pointed-to object. The caller must keep the group valid through callback completion. This batch supplies no deletion, epoch, drain/quiescence or cancellation guarantee.

## Distinct interrupt-mask contracts

| Provider | Observed behavior |
| --- | --- |
| Queue FromISR | Saves BASEPRI, sets 0x30, restores the saved value |
| FreeRTOS task port | Sets BASEPRI 0x30 and increments the 32-bit nesting cell at 0x2000309c; exit decrements and clears BASEPRI to zero at outermost exit |
| WSF | Uses an 8-bit nesting byte with PRIMASK; exit reaching zero enables interrupts, without preserving prior PRIMASK |
| Ambiq | Saves/restores PRIMASK through its separate provider |

Task critical entry/exit are reconstructed from actual `0x4420d0`/`0x4420e8`, with their shared literal at `0x442210`. Task exit does not restore an incoming nonzero BASEPRI at depth zero. Nesting wrap and the invalid exit branch are preserved, not repaired into safe behavior. The zero-timeout receive queries scheduler state through a fixture even though blocking is never requested. No full ready-list or physical interrupt policy is established.

WSF still uses handler_id&15 and 8-bit mask truncation with only ten dispatch handlers. Radio uses ID7. The linked radio cases retain WSF nesting/PRIMASK behavior and do not substitute Ambiq or task-port critical semantics. Stock invalid IDs and overflow behavior remain faithful; this is not a checked app-facing adapter.

## Validation

Fresh `comparison-final.json`: PASS 204 cases and 1,714 distinct original instruction bytes including prior bodies. Independent expectations verify FIFO callback arguments/order and decreasing queue counts, received packet content, empty-buffer immutability, accepted/full send counts, resulting event bits, task nesting and final mask. Actual queue storage writes and waiter-removal boundaries require BASEPRI 0x30 in the verifier.

Cases include capacities 1/2/4, every empty starting slot, wraparound, capacity-plus-one sends (full rejection), repeated copied callbacks, preloaded FIFOs, empty receives, optional sender/receiver waiter providers and yield results, initial BASEPRI 0/0x20/0x60, task nesting 0/1/3/FFFFFFFE/FFFFFFFF, zero-size items/null buffer, invalid arguments, negative IDs -1/-2/-3, unsupported positive IDs 0/1/5, deferred invalid group/mask and radio disable -> pending IRQ -> callback -> WSF dispatch. A malformed preload fixture initially pointed at an uninitialized slot and faulted; it was corrected, and the verifier now asserts coherent preload geometry. No failed run contributes coverage.

New disjoint execution evidence is 276 bytes: receive 128/314 at 0x441b0a, copy-out 42/42 at 0x441f5e, task critical entry 24/24 at 0x4420d0, task critical exit 34/44 at 0x4420e8, and selected negative/empty command-processor paths 48/278 at 0x47e97a. Blocking/positive/fault-loop branches are excluded. Cumulative deduplicated evidence is 3,250 bytes (touch 234, Apollo 3,016); shared ISR queue, EventGroup, WSF, GPIO, memcpy and mask helper bodies count once.

Fresh focused suite: 50 passing tests. Fresh aggregate: 38 modules, 206 tests_run, 201 passing methods, zero failures/errors, six skips (including class setup). Native source uses the existing Cortex-M4 compatible Thumb2 compilation subset for Unicorn; the firmware target remains Cortex-M55. Neither compiler-byte equality nor source-complete firmware is claimed. Firmware, manifest, workflow state and open_cfw.py remain unchanged.

The independent review is in review/report.md; original authentication/pseudocode in original/; hash-bound results/ELF in g2/build/foundation/timer-daemon-wsf-simulator/. The build tree is ignored; the reconstructed source and analysis are Git-visible.

## Remaining boundary and next work

The harness explicitly invokes the actual stock/source command processor. It does not run the timer task's preceding wait/expiry loop, daemon activation, actual scheduler state/ready transitions or blocking receive. Scheduler suspend/resume/unblock, task-count/event-list removal, context/wait/ticks and app handlers are fixtures. Positive timer operations, queue allocation/deletion/unlock and event-group destruction remain external. Invalid argument/overflow cases stop at mask-helper/assert-provider entry before the fault store/loop; unsupported positive commands stop before their timer-object dereferences. No physical ISR, destruction safety or whole-system liveness claim follows.

The next justified provider is the bounded task event-list removal/ready insertion family, with coherent ready/delayed/pending lists and current-task state supplied explicitly. Alternatively, the positive timer commands can be reconstructed as a separate function family. Neither should be hidden behind the completed FIFO contract.

Previous linked reports: ../timer-queue-wsf-2026-10-05/REPORT.md for enqueue, ../event-group-wsf-2026-10-05/REPORT.md for SetBits, ../wsf-radio-handoff-2026-10-05/REPORT.md for dispatch and ../radio-gpio-consumer-2026-10-05/REPORT.md for pin117. Each retains its own validation limits.
