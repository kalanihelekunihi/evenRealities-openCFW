# R1 BC receive consumer and stop hook in C

The receive queue now has C candidates for its stock drain at `0x450cc`
(178 bytes) and thread stop at `0x4503c` (20 bytes), in
`runtime/native_bae8_consumer.c`. The existing connection-field owner supplies
the drain's setter at `0x4d584` (6 bytes). There is one implementation per
function. [Machine receipt](bae8-consumer-c-review.json).

The drain repeatedly calls QueueGet with zero priority pointer and zero timeout,
using the current RX queue handle. A successful null entry is skipped. A
non-null message updates the connection field unless the full 32-bit handle is
exactly `0xffff`; the setter stores the low halfword while preserving the full
input return value. Other high-word handles whose low halfword is `0xffff`
still invoke the setter.

Channel two dispatches on the first payload byte, including for length zero.
Values below 100 arm the RX watchdog, call the export command handler with
16-bit handle and length, then disarm the current watchdog handle. Other
values call the existing protocol receive validator with the full handle and
16-bit length. Channel one recognizes `AT^` only when the full length exceeds
three, writes a terminator at payload plus the full length using 32-bit address
arithmetic, and calls the tokenizer. Other channel-one frames call the legacy
command handler with 16-bit handle and length. Unknown channels are freed.
Each handled message is freed through the current pointer-slot value and the
slot is cleared before the next QueueGet. Callback mutations of that slot,
message header, queue and watchdog are covered by replay.

The stop hook reads the current RX thread once, calls ThreadTerminate when it
is nonzero, and clears the handle after the call regardless of termination
status or provider changes to the shared handle. It preserves the native
8-byte provider frame. The new watchdog owner at `0x2000658c` is separate from
the existing thread and queue owners. The stock RW initializer executed over
poisoned RAM proves all three start at zero; initialization guards survive.

Verification passed 11,520 paired drain cases, ten paired stop cases and
1,544 paired setter cases. Drain cases include null queue entries, multiple
messages, both interrupt-mask states, channel and prefix boundaries, full-width
invalid-handle checks, length narrowing, large lengths, wrapped terminator
addresses and callback mutations. Five deliberately incorrect candidates were
rejected: narrowing the invalid-handle check, using the wrong channel, accepting
three-byte AT prefixes, skipping free, and clearing the thread before termination.
The setter executes actual stock/C bodies within the drain replays.

The drain retains an explicit ABI gap: stock providers see a 24-byte frame and
QueueGet output slot at caller SP minus 24; the tested C candidate uses 32 bytes
and caller SP minus 28. A strict native-frame check rejects the candidate. The
behavior comparison normalizes that private output-slot address, not any
application message or callback payload address. The participating CMSIS
`osMessageQueueGet` implementation forwards it to synchronous queue receive
with zero timeout; no retained pointer is established for this call. This
normalization does not establish native stack identity, timing or byte equality.

All 600 manifest units compile and both relocatable compositions pass with no
failures or duplicate strong symbols. Of the preceding 599 objects, 598 remain
identical; only the connection-field owner changes, to add its setter. The new
drain exposes three missing command implementations as imports: export command,
legacy command routing and AT tokenization. Application imports are therefore
160; bootloader imports remain 34. These explicit dependencies are unfinished
source work, rather than substituted command behavior.

Queue/thread APIs, command/protocol handlers, watchdog operations and free are
modeled in this verification. The underlying allocator, scheduler, actual queue
operation and physical BLE behavior have not been validated here. The RX task
creation, queue startup and outer worker loop remain unfinished. No executable
bytes from these candidates qualify for the canonical source plan. The fresh
hybrid still reproduces the locked application using 4,271 source-built bytes,
641,889 bytes of executable pull-through and 248 resource bytes; this is not a
source-only firmware build.

The subsequent [receive worker](bae8-worker-c-review.md) supplies queue startup
and the outer flag-driven loop. Thread creation and its failure transition remain
open. The import counts above describe this consumer step historically.
