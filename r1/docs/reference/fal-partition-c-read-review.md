# FAL partition read reconstructed in C

The full assembly implementation at `0x631e8` and its obsolete source unit
are removed. `native_partition_read.h` now provides the read policy inside
the generated pinned FAL unit. `fal_partition_read` and
`r1_fdb_native_partition_read` are C aliases to the same body, consolidating
the public and reconstructed names without another implementation or frame
bridge. The existing private C cache lookup remains the state provider.

REA confirms the native behavior preserved here: null partition/buffer
diagnostics followed by nonreturn; a wrapping 32-bit `addr + size` comparison
against partition length; lookup of the cached flash device; then a fresh
partition-offset load followed by the driver read-pointer load. The callback
receives wrapping `offset + addr`, the original buffer and full size word.
Its signed result is returned unchanged. No zero-length or overflow guard
absent from stock was added.

The C body preserves all three error diagnostic sequences, including native
line words 414/421/428 and the exact function/message arguments. Partial buffer
writes survive driver failure. Volatile field reads retain native ordering
across the lookup boundary. Static assertions verify the size word and native
partition/driver field offsets. No inline assembly remains in the read body.

`build/goal-r1-fal-c-read/verify.py` passes 9,216 paired cases (18,432 executions),
modeling lookup, driver and diagnostic boundaries. Cases cover both null
assertions, normal and wrapped bounds, missing devices, driver success/error,
partial writes, and callback mutations of the partition offset, driver pointer
and names. It compares field access order/width, callback arguments, diagnostics,
return words, final buffers, preserved registers, stack and interrupt masks.

A deliberate variant reads the partition offset before lookup. It fails when
lookup changes offset zero to `0x87654321`: stock passes the new address to
the driver, while the variant passes zero. This checks why a hoisted load
does not preserve the native boundary.

Another 6,144 cases execute the actual native/C read and cache lookup together,
with only driver and diagnostic output modeled. All 2,765 standalone lookup
comparisons also pass against the current object. Both aliases have identical
symbol value, size and section. The compiled read body is 258 bytes; it is
not byte-qualified against the 172-byte native body.

The full report `build/sources-goal-r1-fal-c-read/report.json` compiles 565 R1
units without failures or duplicate strong symbols. Import sets remain
199 application and 34 bootloader. `make sources-check` passes.
[Machine evidence](fal-partition-c-read-review.json) binds REA, owned headers,
generated source, execution probes, negative control and normal build by hash.

The canonical source plan is unchanged. Actual diagnostic I/O, driver/electrical
flash behavior, arbitrary pointer/alias faults, concurrency, final placement
and complete source-only byte identity remain unproven. G2 gates are unchanged.
