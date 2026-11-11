# FAL partition device lookup uses its existing C state owner

The symbolic assembly lookup at `0x64f74` was removed along with its obsolete
source unit. Its sole active implementation now lives in
`r1/src/application/board/fal-native/native_lookup.h`, included at the pinned
FAL helper's definition in generated `fal_partition_r1_lookup.c`. A C alias
exports that private helper as `r1_fal_native_device_by_partition`, with no
forwarding frame or duplicate state. The upstream template is unmodified.

The generated unit retains FAL's private partition-table pointer, length and
cache, so initialization and lookup share the existing objects. This resolves
`r1_fal_partition_table` and `r1_fal_partition_cache` without manufacturing
standalone replacements. Application imports decrease from 201 to 199, with
no new imports. One superseded C unit is removed: the build is 566 R1 units.

REA confirms the native table pointer at `0x200077b8`, count at `0x200077bc`,
and seven-word cache at `0x2001e544`. The bounds are unsigned machine addresses:
lower bound is the table base; upper bound is the **start** of the final
64-byte partition. After passing both checks, native arithmetic-shifts the
32-bit difference by six and reads the corresponding cache word. Interior
unaligned addresses below the final start are not independently rejected.

The R1 C helper keeps this behavior using explicit integer arithmetic and
ordered volatile state reads. Static assertions check partition/cache strides.
It also preserves native error handling, which the previous generic build's
disabled assertion macro did not provide: one `r1_native_printf` diagnostic
with the matching expression and `flash_device_find_by_part` name, followed
by a constant nonreturning loop. These are stock failure paths, not substitutes
for unimplemented lookup behavior.

`build/goal-r1-fal-c-cache/verify.py` passes 2,765 paired cases (5,530 executions).
It crosses two table bases and counts one through seven, every byte offset
within valid spans, both invalid bounds, arbitrary cache words and selected
zero-base/count-underflow states. It compares ordered table/count/cache reads,
return values, cache preservation, diagnostic strings and bounded nonreturn,
plus stack restoration, callee-saved registers and interrupt masks on return.
Native and C private-state addresses are normalized by role; their final
firmware placement is not inferred from the test layout.

A deliberate variant widening the upper bound to include the final record's
remaining bytes is rejected for base `0x20010000`, count one, address
`0x20010001`: stock diagnoses and spins, while the variant returns a cache word.
This guards against replacing native pointer-range behavior with a conventional
whole-record range.

The final build `build/sources-goal-r1-fal-c-cache-owned/report.json` compiles
all 566 units without failures or duplicate strong symbols; imports are
199 application and 34 bootloader. `make sources-check` passes.
[Machine evidence](fal-cache-c-lookup-review.json) binds the R1 header,
generated unit/template, REA snapshot, execution probe, negative control and
normal build report by hash.

The compiled lookup is 118 bytes and is not byte-qualified. The canonical
source plan is unchanged. Full partition initialization, arbitrary corrupted
table spans, actual diagnostic output, concurrency, electrical flash behavior,
final source placement/linking and whole-image source completeness remain
unproven. G2 workflow gates are unchanged.
