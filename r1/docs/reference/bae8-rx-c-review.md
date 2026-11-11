# R1 BC receive queue in C

The stock application function at `0x33dbc` (354 bytes) now has one C candidate,
`r1_bae8_bc_rx_enqueue`, in `runtime/native_bae8_rx.c`. The manifest includes
it in the normal Clang application build. [Machine receipt](bae8-rx-c-review.json).

The function rejects a null payload, including at zero length, then checks the
RX queue. It allocates `(length + 15u) & ~3u` with native unsigned wraparound,
clears payload storage before writing the three-word header, and performs an
overlap-safe copy. Count and capacity queries execute before queue put even
though their results are ignored. The queue pointer is reloaded for each call.
A failed handoff logs the original status, frees the current pointer-slot value,
clears the slot and returns `UINT32_MAX`. Success transfers ownership and signals
the current RX thread with `0x400000`, returning zero regardless of flag status.

The RX thread at `0x20006598` and queue at `0x2000659c` have separate C owners.
They are distinct from the existing encoder's thread/queue at `0x20006570` and
`0x20006574`. Native literal references establish both context bases. Executing
the stock RW initialization handler over poisoned memory proves the RX handles
start at zero, with surrounding initialization guards preserved. These owners
do not implement the still-missing RX task/queue initialization lifecycle.

The compiled candidate preserves the native 56-byte frame and queue input slot
at caller SP minus 56 through an aligned C frame object. There is no inline
assembly in this source. The padding is private and is not compared as data.
Full-width handle, channel and length are retained.

Verification passed 3,606 paired stock/C cases, including logging modes,
interrupt-mask preservation, large bounded payloads, wrapped allocation sizes,
payload aliases, provider mutations, and failed-handoff cleanup. Another 200
paired cases execute the actual C memory-move wrapper and upstream memory
primitives against stock bodies. Five mutants were rejected: accepting null at
zero length, skipping the count query, reversing handoff status, changing
allocation rounding, and changing the frame size.

All 599 source units compile and both relocatable compositions pass without
failures or duplicate strong symbols. All 598 preceding objects are identical.
The application has 157 unresolved imports; the bootloader retains 34. This step
resolves the BC RX import without introducing another import.

Allocator/free, CMSIS queue/thread APIs and log providers remain modeled in the
replays. Packet-construction instruction granularity, private registers, flags,
primitive internal frames and timing are outside the comparison. Lengths too
large for emulated RAM are exercised only with allocation failure. These checks
do not establish a final source-only link, actual RTOS queue operation or
physical BLE behavior. No bytes from this candidate were admitted to the source
plan. The fresh hybrid retains 4,271 source-built bytes and reproduces the locked
application using 641,889 bytes of executable pull-through and 248 resource bytes.

The subsequent [receive consumer](bae8-consumer-c-review.md) supplies the drain,
thread-stop hook and connection setter, while task and queue startup remain open.
