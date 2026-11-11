# R1 FlashDB write frame review

The C `_fdb_flash_write` adapter now preserves the native 16-byte R4/R5/R6/LR save frame and provider-entry register state. REA confirmed the stock body at `0x3f05a..0x3f075` in the locked application (SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`). This is bounded behavior evidence, not byte qualification or physical flash validation.

The implementation is `r1/src/application/board/fal-native/native_flash_write.h`. One exact generator replacement in `r1/src/sources.json` substitutes the upstream function definition with that header in `{gen}/fdb_utils_r1.c`; the pinned FlashDB source stays unchanged. The public five-argument SDK signature and short-enum ABI remain intact. Stock reads the file-mode byte before clearing R4, returns error 2 for file mode, forwards four full-word FAL arguments, returns error 3 on a signed negative provider result, and otherwise returns zero. The unused sync argument is not read. Empty compiler constraints and fixed-register bindings preserve the frame/register contract; no executable assembly instructions or opcode arrays were added. This is not fully portable ISO C.

Verification against `build/sources-goal-r1-flash-write-frame-final/report.json`:

- 4,526 paired stock/C cases cover mode bytes, signed results, full-word arguments, unaligned addresses, caller-frame/buffer aliases, provider mutations, null-DB fault ordering and live saved registers, interrupt masks, and the ignored sync argument. FAL write is modeled at this boundary.
- 1,728 paired cases execute the actual C adapter, FAL write and cache lookup together, with the final flash driver and diagnostics modeled. They cover wrapping bounds, lookup failures, forwarding, and native error mapping. The partition cache is seeded; initialization and concurrency are outside this check.
- Two deliberately incorrect variants (mode error and saved-register ownership) are rejected.
- All 574 other objects, ten other utility function bodies, utility data ownership and unresolved-import sets remain unchanged. All 575 units compile with no failures or duplicate strong symbols; unresolved imports remain 175 application and 34 bootloader. `make sources-check` passes.

Official qualification compiles four profiles, but does not admit this write body: branch/layout and enum-return instructions differ from stock. The only selected region is the already-covered six-byte `fdb_blob_make`; no duplicate coverage is added to `tools/build/source-plan.json`.

This check also exposed missing compiler fingerprints on manifest units already using the GCC wrapper. `tools/build/qualify_sources.py` now records their compiler path and actual SHA-256. Qualification objects and selected spans are unchanged across that metadata fix. The generated selected-provider plan passes the production firmware builder and reconstructs the locked application using six selected source bytes plus fallback. The canonical plan also reconstructs the same application with its existing 3,881 source-built bytes, 642,279 fallback bytes and 248 resource bytes. Neither establishes source completeness. G2 gates remain unchanged.

Machine-readable hashes, REA capture, probe references, qualification results and build receipts: [flash-write-frame-review.json](flash-write-frame-review.json). Probes live under ignored `build/goal-r1-flash-write-frame/`; they are not additional reconstruction units.
