# Timer command processor source and differential

`g2/components/bootloader/thread_creation/timer_commands.c` supplies
`opencfw_bl_timer_process_commands`, the source provider for stock
`0x419546`. It drains 16-byte records from the timer queue at
`0x20027180` using `opencfw_bl_kernel_queue_get_blocking(queue, message, 0)`.

The four words are command, delay/period/call target, timer/callback argument,
and callback argument. Raw control flow dispatches commands 1, 2, 6, and 7 to
start/restart; 3 and 8 to stop; 4 and 9 to period replacement; and 5 to timer
deletion. Negative command words invoke the function pointer in word 1 with
words 2 and 3. Other nonnegative values are ignored after the common timer
sampling and any active-list removal. A zero replacement period takes the
stock fatal path.

Timer fields used here are deadline/list item at byte offsets +4 through +20,
period at +24, callback at +32, and state at +40. State bit 0 is cleared/set
for active status; bit 1 distinguishes static storage in delete; bit 2 selects
reload/catch-up. The bit-2 reload test agrees with the constructor's ORS #4 at
`0x419370`; the processor and expiry routines both implement it with `LSLS
#29` followed by a sign test.

The same source unit also provides the small helpers decoded at `0x419508`
(deadline/list insertion) and `0x4193de` (catch up elapsed periods and invoke
the timer callback once per missed period). These use the existing sorted-list
helpers and timer-list globals. In particular, the reload helper accepts
`(timer, incoming_deadline, now)` and repeatedly attempts insertion with
`(timer, deadline + timer.period, now, deadline)` before advancing the base
deadline and invoking the callback. The callback can change the period, so the
source reloads the timer period each iteration. The command's final callback
after the reload helper remains a separate call, as in the image.

## Dependencies and parent integration

The source links to `queue_receive.c` for nonblocking queue get, `timer_wait.c`
for timer sampling and list insertion/removal, `kernel_runtime.c` for masking
the fatal path, and `rtos_heap.c` for dynamic timer free. The command source
calls `opencfw_bl_rtos_free` and `opencfw_bl_mask_interrupts` as external
providers. It does not implement timer expiry `0x419406` or list rollover
`0x41965c`; `timer_wait.c` keeps those as external boundaries. Root integration
should add this translation unit and bind
`opencfw_bl_timer_process_commands` to the source symbol instead of the old
stock alias at `0x419547`.

## Validation

Run `make verify` in this directory. Clang/LLD compile the differential profile
for M33 with the actual `queue_receive.c`, `kernel_runtime.c`, `runtime_mode.c`,
and `timer_wait.c`; the standalone
processor translation unit also compiles for Cortex-M55 at the repository
`-O2` flags (`out/timer_commands-m55.o`). The fixture-only kernel critical,
scheduler, allocator-free, and rollover leaves provide the isolated runtime.
The offline Unicorn fixture compares it against the locked image
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` across
23 cases and 764 distinct executed original instruction bytes. It covers all
command values 0–10, negative callback dispatch, active timer removal,
static/dynamic deletion, bit-2 reload and non-reload state, replacement,
period mutation by a callback, wrapped tick arithmetic, and draining multiple
commands. All compared timer, list, queue, clock, callback, and free-observation
state matched.

The fixture uses synthetic tick values and coherent in-memory timer/queue
objects. The stock run executes queue-get at `0x41a114`, queue ring-copy,
runtime-mode query, and kernel critical enter/exit; the source run executes
their reconstructed providers. Dynamic free at `0x419830` is intercepted at
entry and compared with an observation stub. Scheduler wait/wakeup behavior,
rollover, timer expiry, and allocator effects are fixture boundaries. It makes
no claim about physical
timing, real hardware behavior, full firmware completeness, or byte identity.
