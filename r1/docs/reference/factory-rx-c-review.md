# R1 factory receive enqueue in C

The stock function at `0x33af8` (342 code bytes) now has one C candidate,
`r1_factory_thread_message_encode`, in `runtime/native_factory_rx.c`.
The BAE8 router's factory-message dependency resolves to this implementation.
[Machine receipt](factory-rx-c-review.json).

The factory receive thread at `0x200066b8` and queue at `0x200066bc` have separate
C owners. They are distinct from BC RX at `0x20006598/0x2000659c` and the existing
BLE encoder's thread/queue at `0x20006570/0x20006574`. The stock context literal
at `0x33c58` points to `0x200066b0`. Executing the stock RW initializer over
poisoned memory proves both factory handles start at zero, with initialization
guards preserved. Factory thread and queue creation remain unfinished work.

The candidate rejects a null payload even at length zero, then checks the
factory queue. Allocation uses unsigned `(length + 15u) & ~3u`, including
wraparound. It clears payload storage before writing the full-width handle,
channel and length header and performing an overlap-safe copy. It calls
QueuePut directly with zero priority and timeout: unlike BC RX, there are no
count or capacity queries. A failed handoff logs its returned status, frees
the current pointer-slot value, clears that slot and returns `UINT32_MAX`.
Success signals the current factory thread with `0x400000` and returns zero,
ignoring the thread-flag API result. Handle accesses reload shared state at
the stock provider boundaries.

The aligned C frame preserves the native 56-byte provider frame and QueuePut
input slot at caller SP minus 56. There is no inline assembly in this source.
Verification passed 3,606 paired cases including null/zero-length policy,
allocation failure and size wraparound, logging modes, payload aliases,
large bounded payloads, interrupt masks and provider mutations of shared
handles and the live pointer slot. Another 200 paired cases execute the actual
C memory-move wrapper and upstream copy/clear implementations against native
bodies. Five mutants were rejected: accepting null at zero length, adding a
count query, reversing handoff status, changing allocation rounding and
changing frame size. Production replay passed again after the negative controls.

All 604 manifest units compile and both relocatable compositions pass without
failures or duplicate strong symbols. All preceding 603 objects remain
identical. The factory-message import is resolved without new imports:
159 application imports and 34 bootloader imports remain. The scoped qualifier
selects no executable bytes, so the canonical source plan remains unchanged.
The fresh hybrid matches the locked application using 4,271 source-built bytes,
641,889 executable pull-through bytes and 248 resource bytes.

Allocator/free, CMSIS queue/thread APIs and logging providers remain modeled.
Memory primitives execute in the additional chain cases, with their internal
frames and return-register differences outside the comparison. Packet
construction at individual instruction granularity, private padding, timing
and unbounded memory lengths are not covered; impossible RAM-sized requests
are tested only through allocation failure. These results do not establish
actual queue operation, factory task startup, physical BLE delivery, a final
source-only firmware link or candidate byte identity.

The subsequent [factory task lifecycle](factory-task-c-review.md) supplies the
creator, stop hook, startup queue and worker loop. Its deeper initialization
and record-dispatch dependencies remain open.
