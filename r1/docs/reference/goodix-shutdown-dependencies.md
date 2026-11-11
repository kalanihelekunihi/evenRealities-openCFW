# Remaining native Goodix shutdown dependencies

The [processing teardown admission](goodix-native-processing-teardown-c-review.md) closes the native processing parent and its descendants. The locked top-level shutdown graph now has C providers; initialization/calculation and full executable linking remain incomplete. These observations guide the next implementation work; they are not an admission of the unimplemented functions.

The pinned application is `r1-2.2.6.0009/application.bin`, SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`. REA is analyzing the immutable derived `build/goal-r1-queue-reset-c/stock.elf`, SHA-256 `25b4a29af80ec8edab5bd861ba9b74a6e22eab29dc3d7a809a16869e8a140f04`. Further REA evidence is saved in `build/goal-r1-goodix-native-processing-teardown-c/shutdown-dependency-rea.json`.

## Controller and callback table

The [shutdown-controller review](goodix-algorithm-shutdown-c-review.md) now admits this controller and its typed C callback table, including actual memory-configuration caller integration. The original instruction observations below remain its evidence basis.

Raw instructions at `0x29f9c` identify three literal values at `0x29ffc`: frame-owner base `0x20007bc8`, callback-table base **`0x9d404`**, and initialized-flag base `0x200301f0`. The started bitmap is at frame-owner base+4. REA's rendered decompiler symbol at `0x9d40c` identifies the first row's deinit column, not the table's first byte. Using it as a three-column table base would shift every callback and produce incorrect dependencies.

The twenty rows contain nonzero callbacks only for these deinit slots:

| Slot | Native deinit entry | Current state |
|---|---|---|
| 0 | `0x2b208` | Admitted `GH3x2xAdtAlgoDeinit` C byte-state reset |
| 1 | `0x2c930` | Admitted `GH3x2xHrAlgoDeinit` C adapter to the C processing parent |
| 2 | `0x2cac6` | Existing `GH3x2xHrvAlgoDeinit` C provider |
| 6 | `0x2cfd4` | Admitted C status adapter and complete `0x6eb30` teardown graph |
| 9,15 | `0x2cdbc` | Admitted C soft ADT adapter and complete `0x6e574` state reset |

The controller returns zero without changing state if the frame owner is null. Otherwise it clears the requested started bits first. For each requested slot in ascending order it loads the current frame pointer before testing the initialized flag, calls a nonnull deinit callback when initialized, stops on a nonzero result and clears the slot's initialized byte only on success. The native return uses signed-byte extension. A C controller must preserve the live frame-owner reads, callback return handling, bitmap update order and byte-clear timing. All six callback slots now bind ordinary C providers. No executable stock callback address is retained.

The stock memory-status getter at `0x2a540` reads the byte at `0x20007c18`, which already belongs to `r1_goodix_algorithm_memory`. It must share that state rather than adding a second initialized flag.

## SpO2 ownership graph

This graph is now admitted by the [native SpO2 teardown review](goodix-native-spo2-teardown-c-review.md), including all descendants, shared cell helpers and the public status adapter. Native initialization/computation remain open.

At `0x6eb30`, null owner is success. A nonnull owner is reloaded before each nested operation and before final free. Its helpers operate on the descriptor at context+`0x0c` and subrecords at `6c,88,a8,b0,d0,ac`. After final root free, the owner is cleared. The context owner is separate from the already admitted HR and HRV owners.

| Entry | Observed descendants / responsibility |
|---|---|
| `0x98ffc` | Release record+8 and record+18 unconditionally; no cell clearing |
| `0x37e8a` | `0x93e3a` on record+1c pointer, free that pointer, `0x73154` on record+4, `0x91890` on record root, then free root |
| `0x33800` | Release/clear pointer at `(*record)+4`, then free the live record root |
| `0x28ec0` | Load record+1c, tail-enter `0x2d45c` and `0x36c60`; release nonzero context+300 child then root, accepting a null context |
| `0x305d8` | If descriptor+1c is nonzero, iterate live descriptor count over 40-byte entries, release/clear entry+14, then free the live array root |
| `0x7cba0` | Release/clear the first pointer cell of the pointed record via `0x28eac`, then free and clear its root if nonzero |
| `0x93e3a` | Release/clear cells at offsets0,c via the canonical cell-helper contract |
| `0x73154` | Release/clear offsets4,10 via the already admitted helper contract |
| `0x91890` | Release/clear six cells through `0x304a0` at base and base+64, then cells atc8,d8,e8,f8 |
| `0x28eac` | Nullable release-then-clear cell; every returning path leaves R0 zero, matching the canonical uint32-return helper |

Offsets are hexadecimal. The descriptor/count loop at `0x305d8` reads the live count and array pointer each iteration; it is not an unconditional fixed-count teardown. Native ownership must be recovered at these offsets rather than inferred from older portable API names in `goodix_primitives`.

## Soft ADT reset

This reset and its public callback are now admitted by the [NADT reset review](goodix-native-nadt-reset-c-review.md), using canonical typed state/workspace and the existing C fill/allocator. The following original observations are retained as analysis context.

`0x6e574` is a 210-byte state-reset candidate in the frontier. Initial instructions clear specific byte/halfword/word fields, clear several buffers with `0x277aa`, and initialize a dual-buffer descriptor through `0x5683c`. This is not interchangeable with the simple HR/HRV heap teardown. The admission verifies the complete body, literals, shared state ownership and filter helper. Initialization/calculation and physical behavior remain open.

## Analysis limits

Direct REA callers of the processing parent identify `0x2c930`; indirect-call coverage remains incomplete. Several small callback entries are absent from Ghidra's procedure inventory. REA's batch decompiler can then report an unresolved entry while returning pseudocode from a file-offset fallback at a different address. Such pseudocode was rejected here. Use the raw Thumb instructions and exact-address bytes for those entries, or repair analysis metadata with an independently verified entry before relying on decompilation.

None of this dependency analysis proves native initialization, algorithm computation, physical sensors, executable startup/linking or boot. The current source build remains relocatable composition with 61 application and22 bootloader imports and877 compiled units after the shutdown-controller admission.
