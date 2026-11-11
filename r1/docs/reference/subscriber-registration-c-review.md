# R1 subscriber registration in C

`native_subscriber_registration.c` now expresses stock registration at
`0x8af8c` in C. REA instruction evidence covers the contiguous 146-byte native
body in the stock-derived analysis ELF; the locked application SHA-256 is
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
The existing root table and route records retain their bytes, alignment,
flags and relocations. No second implementation or manifest unit was added.

Registration rejects unsigned selectors above four before locking, allocates
12-byte roots and entries, and rejects duplicates by callback address alone.
Zero callbacks are accepted. A missing thread reference binds to the address
of the sensor thread cell, `0x20006694`, so future consumer dispatch reads the
current thread value. After allocation, head and tail are read again from the
captured root; allocator changes to the global root slot do not replace that
captured pointer. Native allocation failure retains the lock and any partial
root publication, sets BASEPRI to 64, and writes to `0xffffffff`. The required
BASEPRI instruction remains assembly. The prior raw callback gateway also
remains unchanged.

The [machine-readable receipt](subscriber-registration-c-review.json) binds
the source, build, REA, comparison, startup and qualification evidence:

- 2,496 paired stock/C cases, including allocation failures, lock and allocator
  mutations, duplicate and zero callbacks, unaligned records, null-tail faults,
  saved registers, masks, ordered shared accesses and guards.
- 96 registration-to-consumer runs execute the actual C lock, registration,
  consumer, CMSIS thread getter and FreeRTOS current-task getter together.
- Two incorrect variants (thread-sensitive duplicates and binding the current
  thread value) are rejected by the same probe.
- Stock RW/ZI initialization and an independent RW decoder agree; all 20 root
  bytes match cold stock state. All other 574 object hashes are unchanged.
- All 575 R1 units compile; application imports remain 175 and bootloader
  imports remain 34. There are no compilation failures or duplicate strong
  symbols. `make sources-check` passes.

All five qualification variants compile, but none qualifies a byte-identical
region. The canonical plan is unchanged: 3,881 source-built application bytes,
642,279 binary pull-through bytes and 248 resource bytes. The fresh hybrid
application equals locked stock, with source completeness explicitly false.

Allocator returns, mutex APIs and opaque callbacks are modeled. These checks
do not establish real scheduling, physical sensor operation, arbitrary corrupt
pointers, private frame identity, a complete source executable link or a full
source rebuild. G2 gates were not advanced. The goal remains active.
