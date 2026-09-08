# GX8002 upstream queue recovery

The pinned NationalChip `lvp/common/lvp_queue.c` builds unmodified with the
native macOS C-SKY compiler. The verifier authenticates that C file, its header
and `lvp_attr.h` against their Git blobs. Three sections match stock exactly:
initialization at package `0x10528` (20 bytes), empty check at `0x10588`
(10 bytes), and full check at `0x10594` (24 bytes).

The [verification record](gx8002-queue-source-verification.json) pins the
upstream inputs and emitted sections. These three functions are now integrated in the experimental builder. Other functions
in the translation unit do not match stock and are not qualified merely
because they compile. Only explicitly selected sections may be emitted.

The layout is tail, head, buffer pointer, byte size, member size. Initialization
rounds byte size down to a whole member count. The ring reserves one slot to
distinguish full from empty: the application's 64-byte buffer and eight-byte
events provide seven usable event slots, although GetCapacity returns eight.
Callers must supply valid positive dimensions and serialize queue access.

12,000 randomized host operations across member sizes 1, 3 and 8 pass FIFO,
wraparound, full/empty and count checks against a deque model. The host test
uses an empty placement-attribute shim because ELF section names are invalid
on Mach-O; target verification uses the authenticated real attribute header.
The target build uses an empty stdio header because this translation unit
uses no stdio declarations. Host tests also exercise Get/Put but do not qualify
the stock implementations of those functions.

The integration removes 54 retained bytes while preserving package bytes.
Six relevant tests pass. The complete firmware remains a hybrid; no other
queue sections are implicitly admitted from the compiled object.

A follow-up compiler comparison finds that upstream QueueGet emits 70 bytes
at `-Os`, fitting the 74-byte stock body at `0x1053C`, but it is not byte-exact.
Default `-O2` emits 104 bytes; disabling loop optimization emits 80. Target
control-flow and data-access comparison is therefore the next step for Get,
not acceptance based on fitting alone. These experiments do not replace the
verified `queue.o` or change the admitted function set.

QueueGet compiled at `-Os -fno-ivopts` now passes 2,196 restricted target
comparisons across member sizes 1, 2, 3, 4, 8 and 16, with 2, 3, 8 and 17
slots and every aligned head/tail pairing. Stock and compiled code match
return values, final memory and exact access traces. An independent FIFO
oracle also checks each result. Three interpreter tests cover signed division,
indexed/post-increment byte access and rejection paths. The
[comparison report](gx8002-queue-get-comparison.json) records this evidence.
Concurrent mutation, aliasing, invalid dimensions and hardware execution are
not modeled. The 70-byte candidate is now integrated in the experimental codec, with four
trailing bytes counted as unreachable fill. The next stock function and its
preceding alignment word remain untouched. The builder replays the comparison
and requires the reviewed report and object hash before emission.

QueuePut is identified at package `0x181CC`, mapping to image-A SRAM
`0x100261B8`, through the application trigger call and the known SRAM mapping.
Its body ends at `0x18226` before alignment fill. The unmodified upstream
`.sram_text` section emits 86 bytes with the same size-oriented flags used for
Get, fitting the 90-byte stock body. The
[write comparison](gx8002-queue-put-comparison.json) passes 2,196 valid states
with exact read/write traces, final memory and return values, plus an independent
FIFO oracle for successful insertion and full-queue rejection. Source input
preservation is covered by whole-memory comparison. A post-increment-load test
was added to the shared interpreter; five relevant tests pass and Get's prior
2,196-state comparison still passes. Put is now admitted to the experimental builder. The reviewed report names
the upstream `.sram_text` section explicitly; it is authenticated and compared
before those 86 bytes are emitted. Four trailing bytes are generated fill.

The event-trigger wrapper is also reconstructed using the SDK event and queue
headers. Linking at `0x10208CC0` with queue storage at `0x2002ECD8` and the
source-built QueuePut entry at `0x100261B8` reproduces all 20 stock bytes at
package `0x1224C`. Its [verification](gx8002-trigger-event-verification.json)
requires exact linked bytes and authenticated headers. The wrapper ignores
QueuePut's result and always returns zero; it must not be changed to propagate
queue-full failure during faithful reconstruction.

A host integration test links this wrapper with the unmodified upstream queue,
executes 64 fill/drain cycles, and checks that the eighth event is rejected
while all wrapper calls return zero. It verifies FIFO results, source input
preservation and empty state. The wrapper is now admitted to the experimental builder.
