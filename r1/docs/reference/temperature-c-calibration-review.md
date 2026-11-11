# Temperature calibration record read in C

Native `r1_temperature_calibration_read` at `0x7badc` now uses a C body in
`runtime/native_temperature.c`. Its fourteen-byte bridge preserves the
128-byte raw record view at caller SP-136. The C body reads 124 cached
bytes using the live `r1_device_info_kv_handle`, ignores status, loads an
unaligned word at record offset 62, stores it to the output, then loads
the halfword at offset 66 and stores it at output offset four. That
halfword remains the R0 result. Volatile packed accesses preserve the
word-store-before-halfword-load order for aliased output pointers.

REA and raw instructions agree on these accesses. A size rejection leaves
the native scratch seed untouched; the C body uses the bridge's raw view
and does not create an uninitialized C array or supply a zero fallback.
The existing compiled 148-byte serial class and four-byte handle match
the decoded stock initial bytes at `0x20006ad8` and `0x20007dfc`.

The integration probe passed 2,496 stock/C comparisons. Actual getter,
cached-class reader and copy code execute; the source copy is the pinned
musl implementation. Only port critical callbacks are modeled. Cases
cover accepted/rejected sizes, random payload/scratch seeds, four external
output alignments, output aliases within the raw view, and callback changes
to payload, scratch, handle, size and live port selection. Checks compare
cached-read/copy arguments, callback sequence, R0, record/output/class and
handle/port bytes; and verify external guards, callee-saved registers, SP,
interrupt masks and callback alignment.

All other temperature functions and data retain their bytes and relocation
identities. The other 561 source units are unchanged. All 562 R1 units
compile without failures or duplicate strong symbols. Manifest eligibility
and import sets remain unchanged at 214 application and 34 bootloader
imports; `make sources-check` passes. This completes the move of this
temperature unit's logic into C; three small assembly bridges remain to
retain native frames and register restoration.

The C body is 40 bytes plus its fourteen-byte bridge, versus 34 native
instruction bytes. Critical callback SP changes from caller SP-160 to
SP-176 while the raw record remains at SP-136. Private C frames, arbitrary
pointer faults, exceptions, concurrency, timing, physical calibration,
flash persistence, final boot/linking, qualification and whole-image byte
identity remain unproven. No G2 gate or source-plan selection changes.

Exact bindings are in [the machine-readable review](temperature-c-calibration-review.json).
