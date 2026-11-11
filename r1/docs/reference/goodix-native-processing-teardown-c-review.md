# Native Goodix processing teardown and dispatch in C

The [HR constructor review](goodix-hba-initialize-c-review.md) extends the canonical workspace owner from4 to16 bytes for the four native initialization writes. Destruction still uses cell0;128 complete C allocator/constructor/teardown lifecycles cover the expanded owner.

The [machine-readable receipt](goodix-native-processing-teardown-c-review.json) pins the source, stock REA bytes, normal build, fixtures and results. `native_processing_teardown.c` connects the existing C workspace, record and cell destructors to the native processing parent. No stock executable pointer or inline assembly is retained.

At `0x6cc60`, stock destroys the current workspace, reloads its owner and frees that allocation. It then reloads the processing owner before dispatching each record at `6c,70,84`, reloads it before releasing/clearing each cell at `b0,bc,cc,d8`, and frees the final live processing context. It returns zero and leaves both owner cells uncleared. Two canonical four-byte owners are exposed in `native_processing_teardown.h`; future initialization must share them.

The dispatcher at `0x29c74` reads the record type. Its seven-entry stock table contains extended destruction for type0, common destruction for types1/2 and nullable release for type6. Those entries now reference ordinary C providers. Stock entries3/4/5 are null; these and out-of-range indices remain outside the supported contract. The private ROM-table copy is unnecessary in C for this immutable table. The release-cell entry at `0x6629e` reuses the already implemented canonical helper, preserving release-then-clear timing.

Direct verification passes 2,048 parent type/mask, 328 single-field, 368 live-owner/field mutation, 256 dispatch and eight shared-helper comparisons. All 138 native entry instruction bytes execute. Free callbacks capture call-time field snapshots and clobber caller scratch registers. The independent normal-path oracle checks release order and arguments. Four initial-null access shapes are checked at8,0,0,6c; these are emulator observations, not claims of a physical MCU fault.

A further 2,048 comparisons execute the actual C initializer, allocator and every teardown descendant across all64 supported type triples, roots before/after children, field masks and optional unrelated live allocations. Complete heap bytes, owner cells and write widths/order/values match. Source execution cannot enter stock code. Twelve compiled defects are rejected, including cached owners, owner clearing, reordered/missing fields, incorrect dispatch providers, retained workspace, changed status and a fabricated initial-null guard.

Saved integer/FP registers, SP, interrupt masks, FPSCR and caller guards are checked. Caller scratch, APSR and private frames are excluded. Typed contexts are fixture setup rather than recovered algorithm initialization; concurrency and physical memory behavior remain unverified.

The fresh serial source build compiles 872 units (790 application,82 bootloader), with no duplicate strong symbols and unchanged62/22 imports. The tested object equals the normal object and all861 prior nongenerated objects remain identical. Two existing generated objects differ with build directory paths. Source plan and existing cache linker layout remain unchanged. Eight bytes of canonical owner state are added.

Algorithm initialization/computation and remaining lifecycle dependencies, final executable linking/startup, physical hardware and boot remain open. Relocatable composition is not bootable firmware.
