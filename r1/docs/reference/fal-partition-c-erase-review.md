# FAL partition erase policy reconstructed in C

`native_partition_erase.h` owns the public erase policy in the generated pinned
FAL unit, sharing its private C cache lookup with read and write. It replaces
the generic SDK implementation whose configured assertions and error logging
were disabled. The pinned upstream file remains unchanged. No inline assembly
or scratch-frame bridge is required by this body.

REA analysis of stock entry `0x62ff4` confirms a null-partition assertion and
nonreturn, wrapping 32-bit address-plus-size bounds, cache lookup, then fresh
partition-offset and erase-driver pointer loads. The driver receives wrapping
offset-plus-address and the full size word. Its signed result is returned
unchanged. C volatile accesses retain observed field ordering; static assertions
bind length/offset/driver fields to native offsets 56/52/48.

All diagnostic sequences retain their native formats and arguments, including
line words 494/501/508, the missing-device message's single space after
`error!`, and ANSI prefix/suffix. No alignment, zero-size or overflow rejection
absent from stock was introduced.

The probes pass 4,608 paired stock/C cases (9,216 executions), plus 3,072 cases
executing the actual native/C cache lookup. They compare ordered field reads,
diagnostic formats and arguments, driver calls, return words, modeled shadow
flash changes, preserved registers, stack and interrupt masks. Lookup mutations
exercise late offset and driver reads; diagnostic mutations exercise name
reads. The driver model can alter shadow flash even when returning failure.
A negative control replacing wrapping bounds with an overflow-rejecting guard
fails at address `0xffffffff`, size 1, limit 16: stock calls the driver while
the variant rejects the request.

Read and write each pass 9,216 regression cases; cache lookup passes 2,765.
The full report `build/sources-goal-r1-fal-c-erase/report.json` compiles all 565
R1 units without failures or duplicate strong symbols. Imports remain 199
application and 34 bootloader. `make sources-check` passes.
[Machine evidence](fal-partition-c-erase-review.json) binds REA, source, generated
unit, probes, negative control and normal build by hash.

The C body is 216 bytes versus 150 native instruction bytes and is not
byte-qualified. The canonical source plan is unchanged. Driver and diagnostic
I/O are modeled; physical flash, concurrency, arbitrary pointer/alias faults,
final placement and complete source-only byte identity remain unproven. G2
gates are unchanged.
