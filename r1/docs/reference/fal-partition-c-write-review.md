# FAL partition write policy reconstructed in C

`native_partition_write.h` supplies `fal_partition_write` inside the generated
pinned FAL unit, using the existing private C cache lookup. It replaces the
generic SDK body whose configured assertion/logging macros suppressed native
failure behavior. The pinned upstream source is unchanged. The new body uses
C throughout, with no assembly or scratch-frame bridge.

REA analysis of stock entry `0x63358` confirms null partition/buffer assertions
followed by nonreturn, a wrapping 32-bit address-plus-size bounds comparison,
cache lookup, then fresh partition-offset and driver-pointer reads. Volatile
field accesses preserve this order. Static assertions verify the native field
offsets and size word. The original const input buffer and full size word reach
the write driver; its signed return word is preserved.

Diagnostics retain native line words 455/462/469, argument order, ANSI prefix
and suffix, and the two spaces after `error!` in the missing-device message.
Zero-length requests still assert on a null buffer. No overflow rejection
absent from stock was introduced.

The execution probes pass 9,216 paired stock/C cases (18,432 executions), plus
6,144 cases executing the actual native/C cache lookup. They compare ordered
field reads, driver arguments, diagnostic formats/arguments, result words,
preserved registers, stack and interrupt masks. Modeled driver writes affect
a shadow flash region, including partial effects on error; the caller input
buffer remains unchanged. Callback mutations exercise late offset/driver and
name reads. A negative control replacing wrapping bounds with overflow-rejecting
bounds fails at address `0xffffffff`, size 1, partition length 16: stock calls
the driver while the variant rejects the request.

Read (9,216 cases) and cache lookup (2,765 cases) regressions pass against the
current object. `build/sources-goal-r1-fal-c-write/report.json` compiles all 565
R1 units without failures or duplicate strong symbols. Imports remain 199
application and 34 bootloader. `make sources-check` passes.
[Machine evidence](fal-partition-c-write-review.json) binds the source, REA
snapshot, probes, negative control and normal build by hash.

The C write body is 260 bytes versus 172 native instruction bytes; it is not
byte-qualified. The canonical source plan is unchanged. Driver and diagnostic
I/O are modeled; physical flash, concurrency, arbitrary pointer/alias faults,
final placement and complete source-only byte identity remain unproven. G2
gates are unchanged.
