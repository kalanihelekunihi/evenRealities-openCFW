# R1 LIS2DW12 identity probe in C

The identity probe at stock `0x754DC` now uses C. It reads the write callback
slot and installs the default only if null, then does the same for the read
slot. It initializes the ID byte to zero, invokes the device-ID getter and
returns that byte without interpreting transport status. Volatile slot
accesses retain the stock read/install order. REA confirms these branches.

The FIFO and identity units now share a typed 16-byte context-prefix header.
Its write/read/delay callback and handle offsets are checked at compile time;
the existing four-byte-aligned BSS allocation remains 16 bytes. The additional
private pointer in the full pinned ST context is neither owned nor accessed.
Both source files now contain no inline assembly. Other function instruction
bodies in the two objects remain unchanged from the preceding build.

All 2,880 comparisons pass. Nine combinations of absent, custom and default
write/read slots are checked against every ID byte. Another sweep varies
transport status, callbacks that leave the byte untouched, and null/all-one
handles. Comparisons cover ordered context reads/writes, callback installation
and preservation, returned byte, and final context contents. Custom callbacks
and default adapters through the real registry dispatchers are exercised;
only the final reader/provider operation is mocked. Delay and handle words
remain unchanged. Callback mocks poison r0–r3; r4–r11, entry SP and callback
eight-byte alignment pass.

Default function addresses and stack-backed ID-byte pointers are normalized
by role. The candidate probe is 74 bytes versus stock's 40, and callback
stack depth on the default bus route differs. Private spill, complete fault
state, concurrent context mutation, timing and byte identity remain unproven.
No physical sensor, controller or startup-vector behavior is validated.

All 561 R1 units compile and both compositions pass with unchanged 238/34
application/bootloader unresolved sets and no duplicate strong symbols.
`make sources-check` passes for both device trees. No source-plan selection
or workflow gate changed.

[lis-c-identity-probe-review.json](lis-c-identity-probe-review.json) binds
source/header/build hashes, native/candidate bytes, context layout, REA
results and ignored probe artifacts in `build/goal-r1-lis-probe/`.
