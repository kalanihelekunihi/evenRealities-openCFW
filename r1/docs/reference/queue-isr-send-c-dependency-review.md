# Interrupt-safe queue send in C

The selected queue/mutex provider now includes pinned FreeRTOS 10.5.1
`xQueueGenericSendFromISR` and private `prvCopyDataToQueue`. They share the
admitted 80-byte queue owner and native memory-movement provider. REA instruction
views confirm stock ISR entry `0x97da4` and copy helper `0x84eca`.

The function validates queue/buffer and overwrite-capacity arguments, validates
interrupt priority, saves/raises BASEPRI and admits a send when space exists or
overwrite is requested. It captures the signed transmit lock before copying.
Back sends advance/wrap the write pointer; front sends retreat/wrap the read
pointer; overwriting a nonempty data queue retains its recorded count. Unlocked
queues can remove a waiting receiver and set a nonnull wake flag. Locked queues
increment only below the task-count limit and assert rather than wrapping at
127. The saved interrupt mask is restored without directly pending a switch.

All 9,528 paired native/C cases pass (19,056 executions). They cover back, front,
overwrite and other raw position words; empty/full/overfull counts; zero/byte/word
items; ring wrap; every signed transmit-lock byte; task-count limits; raw wake
results; masks; null/invalid arguments; overlapping sources; queue/flag aliases;
and callback changes to count, lock and BASEPRI. Actual native/C copy and memory
movement execute, including the native-result adapter, musl memmove and memcpy.
Priority validation, task count, event-list removal and disinherit are modeled.

The zero-item-size/null-head descriptor branch is also compared: the helper calls
disinherit, clears the holder and increments count while the ISR caller ignores
the helper's yield return. This preserves observed behavior and does not establish
that mutex use from an ISR is safe. The copy helper retains its pre-copy count,
and the ISR retains its pre-copy lock across callbacks.

All 7,884 receive regressions pass again. All nineteen preexisting function bodies
remain byte-unchanged. Negative controls reject losing overwrite count correction,
reloading the transmit lock after copy, treating front sends as back sends and
omitting mask restoration. Descriptor/ring/source/flag bytes, guard bytes,
boundary snapshots, return, SP, callee-saved registers and masks agree.

All 573 R1 units compile and compose without failures or duplicate strong symbols.
Application imports fall from 191 to 190, removing only
`xQueueGenericSendFromISR`; bootloader imports remain 34. `make sources-check`
and `git diff --check` pass. Five official qualifier configurations compiled;
only two already-covered BASEPRI copies matched. Recorded C sizes are 218/114
bytes versus stock 200/108; these new bodies remain unqualified.

The unchanged canonical plan builds a stock-identical hybrid application,
SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 3,833 source-built and 642,327 unclassified binary-pull-through bytes.
Source completeness remains false.

Private frames, caller-clobbered outputs/flags and every internal access order
are outside these receipts. Assertions cover mask, fault address, width and
value without full processor exception-state proof. Physical ISR nesting,
priority validation, scheduling and concurrency remain unverified. No G2 gate
advances. Source, REA, probe, qualifier and build hashes are bound in
`queue-isr-send-c-dependency-review.json`.
