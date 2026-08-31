# G2 bootloader TLSF free-list source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The three complete authenticated entries at `[0x00416C4E,0x00416E04)` now route to compilable freestanding C in `components/bootloader/core_overlay/runtime_tlsf_free_lists_416c4e.c`. The 8,044-byte source file has SHA-256 `e3989523b9680265fde48af650cf3bbf951209d4103f17947bca45457951100e` and is a bounded BSD-3-Clause adaptation of Matthew Conte TLSF v3.1 for the recovered G2 ILP32 allocator configuration.

| Entry | Stock span | Stock B | Direct callers | Apple text B | Relocations |
|---|---:|---:|---:|---:|---:|
| suitable-block search | `[0x00416C4E,0x00416CC6)` | 120 | 1 | 112 | 2 |
| remove free block | `[0x00416CC6,0x00416D5C)` | 150 | 2 | 124 | 0 |
| insert free block | `[0x00416D5C,0x00416E04)` | 168 | 1 | 148 | 3 |

The source fixes the recovered allocator ABI at a 16-byte block header, first-level bitmap offset `0x10`, 24 second-level bitmaps at `0x14`, and the 24×32 free-list matrix at `0x74`. Host tests cover current-class and next-class selection, exhaustion without index mutation, sentinel initialization, head/non-head removal, insertion, link rewrites, and first/second-level bitmap transitions. Assertion file, expression, and source-line identities are preserved for the authenticated stock paths. Cortex-M55 compile-time assertions fail closed if the target layout changes.

Apple clang 21 places the functions at overlay offsets 5,436, 5,548, and 5,672 with final hashes `9ce2a15b…151767`, `19f8e8dc…8d078`, and `5fc38bac…6bcea`. Homebrew clang 22.1.8 places 104, 128, and 148-byte equivalents at offsets 5,420, 5,524, and 5,652. The canonical Apple overlay/provider are 5,820/154,420 bytes with SHA-256 `b6bad044…bed2d` / `7ad8834b…adee7`; Linux is 5,800/154,400 bytes with SHA-256 `a15baed2…337f` / `da9e1158…6076`.

Unsigned Apple and Linux packages are respectively 4,735,998 bytes (`95d043d2…d427`) and 4,511,988 bytes (`d0d84198…5815`). Their flash plans are 4,417,602 bytes (`a2a0dca6…ffbc`) and 2,350,377 bytes (`7317b365…8a4c`). Apple has 6,357 placed regions; Linux has 3,374. Both retain only the two pre-existing unresolved regions.

The next complete callable body begins at `0x00416E04`; `[0x00416E04,0x00417AD4)` remains a 3,280-byte software gap before the already routed EasyLogger entries. No image was signed, flashed, installed, reset, or booted. Live heap-class selection, fragmentation/coalescing, allocation caller paths, and boot validation remain explicitly blocked because no authorized responsive G2 right temple is available. This tranche is software-closed, but firmware-wide functional completeness is not claimed.
