# Experimental Main extended logger runtime helpers

`runtime.c` supplies `g2_log_exception_number`, `g2_log_is_privileged`, and
`g2_log_fatal_idle`. The stock outer logger reads IPSR at `0x43d580`; the
source helper also checks CONTROL to preserve the architectural distinction
between privileged thread and handler mode. On every modeled CONTROL/IPSR
combination, the outer expression still equals stock `IPSR & 0x1ff`.

The stock fatal child `0x44ab24` executes DSB, writes
`(*AIRCR & 0x700) | 0x05fa0004` to `0xe000ed0c`, executes DSB and loops.
`g2_log_fatal_idle` follows that nonreturning behavior. The bounded oracle
compares the first AIRCR write and stops before reset. It does not prove a
physical reset or whole logger fatal callback behavior.

`locks.c` supplies the guard's lock enter/exit wrappers. Stock entries
`0x44aa98`/`0x44aaa0` call `0x44aa40`/`0x44aa56`, which read the mutex cell
at `0x20074578`; if nonzero they call CMSIS mutex acquire with 1000 ticks or
release. The C wrappers use the selected Audio `audio_mutex_acquire/release`
with matching tagged-handle ABI. A 24-case oracle compares the wrapper call
arguments and return boundaries with those mutex children cut; real kernel
mutex effects remain under the selected lower provider.

`transport.c` implements the stock outer transport entries `0x448d4e` and
`0x4495e4`. Submit copies at most 255 bytes to the 13-byte packet header,
terminates the payload, sets length/level/mode, and invokes typed allocation,
enqueue, free and failure contracts. Signal validates the event arguments,
uses the selected IRQ-context provider, chooses task or ISR event-group set,
and requests PendSV if the ISR wakes a higher-priority task. `event_get.c`
implements stock `xEventGroupGetBits` entry `0x47ed64` under the selected
BASEPRI save/restore providers.

Bounded original/source oracles pass 34/34 submit, 8/8 signal, and 16/16
event-get cases. Queue and event-group mutation children are cut in the first
two; event-get executes the selected mask children. The three new C units
compile for Cortex-M55 and link with the integrated Apollo candidate without
duplicate strong symbols. At this intermediate cut, seven lower/data imports
remain: node allocate,
enqueue, free, queue failure handler and its product message, task event set,
and ISR event set. The product queue pool, event handle initialization,
ownership and concurrency remain unproved. These units are experimental and
do not constitute complete transport delivery.

`transport_queue.c` now implements the three node operations from stock
`0x448a0c`, `0x448a8e`, and `0x448af0` using aligned 32-bit atomic loads and
compare/exchange. The node has next/state/length/level/mode fields at offsets
0/4/8/10/12, payload at 13, and a 272-byte C stride (269 meaningful bytes).
The free head and pending tail are product RAM cells. A four-case original/
source oracle covers uncontended empty/allocation/free/enqueue transitions;
concurrent CAS retries and consumer dequeue still need composition.

The former `event_set.c`, `event_scheduler_adapters.c` and `event_unblock.c`
shims (event-set, scheduler suspend/resume and event-list unblock lowers) were
retired when the pinned FreeRTOS kernel units were integrated:
`xEventGroupSetBits`/`xEventGroupSetBitsFromISR` (event_groups.c),
`xTimerPendFunctionCallFromISR` (timers.c) and `vTaskSuspendAll`,
`xTaskResumeAll`, `vTaskRemoveFromUnorderedEventList` (tasks.c) now come from
those units.

`transport_failure.c` now provides the exact authenticated string at stock
`0x71e990` and the `0x4733ee` variadic error wrapper. It uses the stock
callback cell `0x200742f0` and buffer `0x2006b930`; stock formatter
`0x473036` remains a typed import. A three-case original/source oracle covers
callback absent/present and variadic argument placement.

`transport_init.c` implements stock `0x44895e`, `0x4489e8`, and `0x448c74`.
It initializes 254 chained free nodes at pool base `0x202d3fc8` with a
272-byte stride, then two terminal/sentinel nodes; node 255 is the pending
sentinel at `0x202e4eb8`. It installs heads, zeroes 48 stats bytes, sets
default level 1, then enables the queue. Two original/source cases compare
the complete 256-node pool and product cells for disabled and already-enabled
entry. The final integrated link has 79 undefined names, with exactly one
direct transport import: the full `0x473036` formatter body. Real concurrent
initialization, queue consumption, and hardware delivery are not verified.

`transport_formatter_adapter.c` now binds `0x473036` to the already selected
Ambiq-derived `audio_heap_formatter`. The authenticated three-word ABI is
destination, format, ARM32 `va_list`; Clang emits one direct Thumb branch for
each of `g2_log_transport_vformat_unbounded` and the Main FlashDB
`g2_flashdb_vformat` adapter. The latter matches the previously isolated
FlashDB print wrapper's R0–R2 call. Integrated undefined names become 77,
with no duplicate symbols. The pinned formatter has 88 selected original/
source comparisons, including integer/string/long-long/finite-float samples;
its complete format grammar, malformed formats, buffer bounds, and physical
sink still lack proof. `g2_log_vformat` is a separate four-argument bounded
formatter contract and is not aliased here.
