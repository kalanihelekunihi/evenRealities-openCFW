# Health configuration change detection in C

Native `r1_record12_apply` at `0x6c53c` is now ordinary C in
`runtime/native_record_providers.c`, with no frame bridge. Null inputs
return immediately. For valid inputs it reads every updated byte followed
by its corresponding previous byte. Byte zero accepts differences within
two, byte one requires equality, and bytes two and three accept differences
within nine. Unsigned delta arithmetic preserves the native comparisons
without treating byte wraparound as a small difference.

After all eight reads, the routine tests the changed flag against bit zero
of `r1_device_id_once_status`. It preserves the fresh log-mode reads and
short-circuit behavior: structured severity `0x0c000000`, then SDK code
`0x001c0003`, followed by the native reinitialization tail call. Both log
strings are now readonly C arrays matching the stock 56/50 bytes. The SDK
code matches the native bounds at `0xc44fc` and `0xc441c`.

REA agrees with the raw detector instructions and identifies the
reinitialization entry without parameters. Logging, mode queries and
reinitialization are modeled in the execution probe. Actual algorithm
reset and sensor behavior remain separate dependencies.

The two-byte placement passes 265,731 stock/C comparisons, including all
262,144 byte pairs across the four fields, varying one field at a time.
A further 3,587 comparisons pass at four-byte placement. The linker script
and linked symbol checks enforce those placements. Total: 269,318 passes.
Additional cases exercise every low-three-bit mode triple, status values
0/1/2/3/128/255, null pointers, overlapping records, full-width random
modes and changes during reads/callbacks. This is not an exhaustive sweep
of all combined record values.

Checks compare exact byte-read addresses/order/values, callback sequence
and owned log arguments, record/status bytes, callee-saved registers, SP
and interrupt masks. Callbacks clobber caller-saved registers. Callback
stack alignment is checked; reinitialization receives the original caller
SP and LR. Early-return R0 is unowned because the public routine is void.

The existing persistence body and its ten-byte bridge retain exact section
bytes and relocation identities. The other 561 source units are unchanged.
All 562 R1 units compile without failures or duplicate strong symbols;
imports remain 211 application / 34 bootloader. Eligibility is unchanged
and `make sources-check` passes.

The C detector occupies 190 bytes versus 138 native instruction bytes.
Complete private-stack/fault/exception identity, timing, concurrency,
physical operation, final firmware linking, qualification and whole-image
byte identity remain unproven. No G2 gate or source-plan selection changes.

Exact bindings are in [the machine-readable review](health-c-change-review.json).
