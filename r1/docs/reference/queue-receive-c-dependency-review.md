# Task-context queue receive in C

The selected queue/mutex provider now includes pinned FreeRTOS 10.5.1
`xQueueReceive`. It reuses the existing queue owner, empty predicate, copy-from-
queue helper, unlock helper and native memory providers. REA's complete
instruction view confirms stock entry `0x97f50` (296 bytes).

The function validates arguments and scheduler/wait state, receives immediately
when data exists, decrements the captured count and wakes a waiting sender when
required. Empty queues return failure when no wait remains. Blocking initializes
the timeout once, suspends scheduling, locks the queue and checks whether to
wait, retry or time out. After timeout it unlocks/resumes and checks for data
again: a late arrival is received even when the wait has expired. Required
wakeups retain native PendSV, SEV, DSB and ISB ordering.

All 2,952 paired native/C cases pass (5,904 executions). They cover zero/byte/word
items, empty/nonempty/full-word counts, sender wakeups, raw results, four masks,
scheduler states, null arguments, critical/copy mutations, timeout expiry,
repeated waits, data arriving before a block and data arriving after timeout.
Timeout buffers are initialized and compared by role across retries. Actual
queue copy, unlock and memory providers execute. Scheduler, critical, timeout
and event boundaries are modeled. Descriptor/ring/output bytes, boundary
snapshots, return, SP, callee-saved registers, masks and yield events agree.

All 5,268 task-send and 7,884 ISR-receive regressions pass again. All twenty-three
preexisting function bodies remain byte-unchanged. Negative controls reject
ignoring the late-arrival recheck, waking the wrong event list, omitting timeout
initialization and reloading the count after copying.

All 573 R1 units compile and compose without failures or duplicate strong symbols.
Application imports fall from 189 to 188, removing only `xQueueReceive`;
bootloader imports remain 34. `make sources-check` and `git diff --check` pass.
Five official qualifier configurations compiled; only two already-covered
BASEPRI copies matched. Recorded C receive size is 362 bytes versus stock 296,
and remains unqualified.

The unchanged canonical plan builds a stock-identical hybrid application,
SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 3,833 source-built and 642,327 unclassified binary-pull-through bytes.
Source completeness remains false.

Finite scheduler scripts do not establish physical scheduling, interrupt delivery
or concurrency. Private frames, caller-clobbered outputs/flags and every ordinary
internal access order are excluded. Logical assertions cover mask, fault address,
width and value; fault-path barriers and full processor exception state remain
unverified. No G2 gate advances. Source, REA, probe, qualifier and build hashes
are bound in `queue-receive-c-dependency-review.json`.
