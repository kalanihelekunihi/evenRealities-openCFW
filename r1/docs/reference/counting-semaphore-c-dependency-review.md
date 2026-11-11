# Counting-semaphore constructors in C

The selected queue/mutex provider now includes pinned FreeRTOS 10.5.1
`xQueueCreateCountingSemaphore` and `xQueueCreateCountingSemaphoreStatic`.
They use the existing 80-byte queue owner and actual selected queue creation,
initialization, reset and list routines. The duplicate full upstream queue unit
remains excluded. REA instruction views confirm stock entries `0x97a88` and
`0x97ab0`.

Both constructors require a nonzero maximum and an unsigned initial count no
greater than that maximum. They create a zero-item-size queue with counting
semaphore type 2, then write the requested initial count after queue creation
returns. Dynamic allocation failure returns null without writing through it;
static descriptor validation remains with the shared static creator. Invalid
count arguments retain the configured logical assertion fault.

All 6,144 paired native/C constructor cases pass (12,288 executions). They cover
static/dynamic creation, full-word maxima and initial counts including high-bit
values, equal and excessive initial counts, zero maxima, allocation failure,
null static descriptors, four interrupt masks and critical-section mutations.
The latter include overwriting the message count before returning from reset;
the constructor restores the requested initial count afterward. Actual queue
creation, initialization, reset and list initialization execute; heap and
critical entry/exit are modeled. Boundary snapshots, descriptor/guard bytes,
call order, return, SP, callee-saved registers and masks agree.

All 8,248 queue-creation regression cases pass again. All fifteen preexisting
function bodies in the selected object remain byte-unchanged. Negative controls
reject disallowing an initial count equal to the maximum, forcing a zero initial
count and writing through null after allocation failure.

All 573 R1 units compile and compose without failures or duplicate strong symbols.
Application imports fall from 194 to 192, removing only these two constructor
imports; bootloader imports remain 34. `make sources-check` and
`git diff --check` pass. Five official qualifier configurations compiled; only
two already-covered BASEPRI helper copies matched. Recorded C constructor sizes
are 42/58 bytes versus stock 40/46, and remain unqualified.

The unchanged canonical plan still builds a stock-identical hybrid application,
SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 3,833 source-built and 642,327 unclassified binary-pull-through bytes.
Source completeness remains false.

Private frames, caller-clobbered output registers/flags and every internal
ordinary-memory access are outside these receipts. Logical assertion checks
cover mask, fault address, width and value without full processor exception-state
proof. Heap internals, physical semaphore scheduling, interrupts and concurrency
remain unverified. This does not validate all CMSIS semaphore frontend paths.
No G2 gate advances. Source, REA, probe, qualifier and build hashes are bound in
`counting-semaphore-c-dependency-review.json`.
