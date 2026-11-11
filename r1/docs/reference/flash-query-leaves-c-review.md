# R1 FlashDB database path and query-count callback in C

Two assembly helpers in `runtime/native_flashdb_query_count.c` are now C.
The outer query bridge remains unchanged: its saved argument words form the
iterator context and are restored on return. This is a partial C conversion.

`r1_fdb_native_db_path` at stock `0x3f014` tests the complete FILE_MODE byte at
+25 before loading the database's partition pointer at +8. Any nonzero mode
returns null. Otherwise the result is the partition pointer plus four, with
native 32-bit wraparound and no partition/name dereference. A packed volatile
word view preserves the native potentially unaligned load.

`r1_fdb_native_query_count_cb` at stock `0x87428` reads the record's status byte,
then the requested status byte from the context. Only equality permits a read
and increment of the context word at +4; increment wraps at 32 bits. Separate
volatile byte reads and a packed volatile word view preserve order, unaligned
contexts and record/count aliasing. The callback always returns zero.

REA/Ghidra confirms the database-path instructions. Its default analysis has no
procedure at the callback entry; that error is retained and gives no coverage
credit. Direct Thumb disassembly of the locked application and raw stock
execution establish the callback's local instruction behavior. The outer
query's callback literal is checked against the locked image.

The normal source object passes 1,740 paired stock/C emulator cases: 100 path,
1,280 callback and 360 outer-query cases. They cover whole-byte mode rejection,
pointer wrapping, status matches/mismatches, aliased status/count bytes,
unaligned counters, counter overflow, callback iteration, initialized state and
uninitialized-database diagnostics. The actual retained bridge calls the C
helpers; the iterator and diagnostic printer are modeled. Shared-memory order,
guards, R0, return SP, saved registers and interrupt masks agree, including the
outer bridge's restored R1/R2/R3 words. Each invocation resets XPSR/IT state to
avoid condition-state leakage between emulator runs. Two negative controls
(testing only mode bit zero and truncating the counter to 16 bits) are rejected.

All 573 R1 units compile, with no failures or duplicate strong symbols. Imports
remain 176 for the application and 34 for the bootloader. The manifest and every
unrelated object retain their hashes. The outer bridge's instruction-body bytes
are unchanged. Five official qualification profiles compile, but none selects
either new C helper: only the unchanged assembly bridge qualifies, and that
wrapper-only candidate was not promoted. The source plan remains unchanged.
A fresh hybrid application still equals the locked 646,408-byte image, with
3,881 source-built bytes, 642,279 binary pull-through bytes and 248 resource
bytes. Stored-byte provenance is not executable-C coverage or source completeness.

The evidence excludes actual iterator traversal, physical flash, concurrency,
arbitrary invalid memory, private frames and caller-clobbered registers/flags
apart from the explicitly checked outer saved words. No G2 implementation or
workflow gate changed. Hashes and build paths are recorded in
[flash-query-leaves-c-review.json](flash-query-leaves-c-review.json).

The outer assembly query adapter described by this historical review is now
superseded by the [ordinary C count-query adapter](flash-query-pure-c-review.md).
The canonical path and counter machine bodies remain unchanged.
