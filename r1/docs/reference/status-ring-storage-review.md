# Status ring storage closure

The normal R1 application composition now includes one C owner for the
status-event ring. `runtime/native_status_ring.c` contains only storage;
its four duplicate functions were removed in favor of the existing
`board/native_status_record.c` implementation.

Stock publisher `0x5e118`, checked through REA and raw instructions, uses
read/write indices at `0x20006938`/`0x20006939`, a halfword dropped counter
at `0x2000693c`, and sixteen eight-byte records at `0x20019bc8`. Each record
contains packed status followed by a timestamp. Layout assertions check
the record size and timestamp offset. Unused control bytes remain unowned.

The initialization probe executes the stock RW decompressor and zero-init
handler, verifies their guards, independently decodes the RW data, and
matches all 132 owned bytes against the compiled C objects. They start at
zero, with writable, non-executable sections and native field alignment.

The publisher integration probe passed 1,024 stock/C comparisons covering
all 256 read/write index pairs under four callback mutation modes. Actual
publisher, device-state, peer-count and charge-state helper code executes.
Advertising lookup, battery update, timestamp, critical-section and event
callbacks are modeled and clobber caller-saved registers. The probe compares
callback order, event arguments, control/record bytes, untouched bytes and
guards, callee-saved registers, SP and interrupt masks. Callback SP alignment
is checked. Coverage includes full-ring counter changes, index wrap and
state changes during callbacks.

All 562 R1 units compile without failures or duplicate strong symbols.
Application composition contains 454 objects and 214 unresolved imports,
down from 218 with exactly the four ring imports removed and none added.
Bootloader imports remain 34; the other 560 source units are unchanged.
Exact bindings are in [the machine-readable review](status-ring-storage-review.json).

Probe placement uses native addresses. Final placement, boot integration,
complete private-stack identity, interrupt scheduling, concurrent access,
physical event delivery, provider qualification and whole-image byte
identity remain unproven. No G2 gate or source-plan selection changes.
