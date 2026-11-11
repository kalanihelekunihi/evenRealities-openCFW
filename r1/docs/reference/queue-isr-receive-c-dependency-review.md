# Interrupt-safe queue receive in C

The selected queue/mutex provider now includes pinned FreeRTOS 10.5.1
`xQueueReceiveFromISR`, its private copy-from-queue helper and the receive-lock
increment macro. They share the admitted 80-byte queue owner and existing native
memory-movement provider. REA instruction views confirm stock ISR entry
`0x9807c` and copy helper `0x84ea4`.

The function validates queue/buffer arguments and interrupt priority, saves and
raises BASEPRI, and checks the captured message count. Successful reads capture
the signed receive lock before copying, advance/wrap the ring pointer, copy an
item and decrement the captured count. An unlocked queue may remove a waiting
sender and set a nonnull wake flag to one. Locked queues increment only below
the task-count limit, asserting at signed lock 127 rather than wrapping. The
function restores the saved mask; it does not itself pend a context switch.

All 7,884 paired native/C cases pass (15,768 executions). They cover empty/nonempty
queues, zero/byte/word-sized items, ring wrap, every signed lock byte, task-count
limits, waiting senders, raw wake results, four initial masks, null queue/buffer
arguments and aliases among output buffers, queue fields and wake flags. Priority,
copy and scheduler boundaries can change queue fields or BASEPRI. Tests check
that count/lock snapshots survive copying, untouched wake flags remain intact,
and the mask saved after priority validation is restored.

Both native and C copy helpers and memory movement execute, including the C
native-return adapter, musl memmove and memcpy. Only priority validation, task
count and event-list removal are modeled. Descriptor, ring, output and wake bytes,
guards, boundary snapshots, return, SP, callee-saved registers and masks agree.
Negative controls reject reloading count/lock after copy, clearing an untouched
wake flag and omitting mask restoration.

All 6,144 counting-semaphore regressions pass again. All seventeen preexisting
function bodies remain byte-unchanged. All 573 R1 units compile and compose
without failures or duplicate strong symbols; application imports fall from 192
to 191, removing only `xQueueReceiveFromISR`, with bootloader imports still 34.
`make sources-check` and `git diff --check` pass. Five official qualifier
configurations compiled; only two already-covered BASEPRI copies matched.
Recorded C sizes are 182/32 bytes versus stock 164/38; these bodies remain
unqualified.

The unchanged canonical plan builds a stock-identical hybrid application,
SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 3,833 source-built and 642,327 unclassified binary-pull-through bytes.
Source completeness remains false.

Private frames, caller-clobbered outputs/flags and every internal access order
are outside these receipts. Assertion checks cover mask, fault address, width
and value without full processor exception-state proof. Physical ISR nesting,
priority validation, scheduling and concurrency remain unverified. No G2 gate
advances. Source, REA, probe, qualifier and build hashes are bound in
`queue-isr-receive-c-dependency-review.json`.
