# Locked-byte evidence and validation boundary

The source is bounded against `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`, load base `0x410000`, SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

| Stock entry | Verified extent | Size | Readable source | Behavior from the locked instructions |
|---|---:|---:|---|---|
| `0x42f41a` | `[0x42f41a,0x42f4b2)` | 152 bytes | `opencfw_ton_trim_cache` | Reads revision byte at `0x4002000c` and word `0x20000098`. Copies six 5-bit trim fields from `0x40020344`, `0x40020358`, `0x40020354`, and `0x4002034c` to bytes `0x20000554..0x20000559` when revision is at least 34, or revision is 33 and `0x20000098` is nonzero. For all other cases it writes defaults `14,31,11,11,21,31` in increasing byte-address order. Returns zero and has no calls. |
| `0x42f4b2` | `[0x42f4b2,0x42f5f0)` | 318 bytes | `opencfw_ton_trim_apply` | Uses the two arguments after byte narrowing to select row 0, 1, or 2 of the locked table at `0x433f20`; its bytes are `01 01 02`, `01 01 02`, `01 02 02`. Sets bit 31 at `0x40020340`, then updates six five-bit fields across `0x40020344`, `0x40020358`, `0x40020354`, and `0x4002034c` from cached trim bytes. If bit 0 of `0x40021100` was set, it calls `0x41c838(0)`, `0x41d1c0(5)`, clears that bit, and after applying fields restores it before `0x41d1c0(5)`, `0x41c838(1)`. Returns zero. |

The supplied runtime-hook inventory associates these routines with table `0x20026e38` offsets `0x20` and `0x24` under the revision-33/trim-below-2 selection. This worker recovers and tests the callback bodies; it does not claim to prove the installer or all callers. The `opencfw_ton_trim_apply` calls at `0x41c838` and `0x41d1c0` remain explicit synthetic cuts in the tests. No body for either callee is included in this source candidate.

## Validation

`make test` independently compiles `ton_hooks.c` for Thumb Cortex-M33 at `0x10000`, then compares stock and source executions in Unicorn across 124 cases: 24 cache cases across six revision values and four `0x20000098` values, plus 100 apply cases across argument truncation, all three table rows, both prior state-bit values, two trim-byte sets, and nonzero cut status. Results include the ordered MMIO/SRAM write log, final relevant memory, cut-call argument order, input hashes, exact per-function stock-byte hashes, and instruction-coverage ranges in `result.json`.

The first function's entire 152-byte body is executed across the matrix. The second has 318 bytes in its verified function extent; some conditional-arm instruction bytes remain unvisited because the locked three-row table contains only the values `1` and `2`. The receipt lists these exact ranges. The test establishes behavioral agreement for covered paths with synthetic MMIO and synthetic callees. It does not establish real peripheral semantics, safety of the state-bit transition, identity with an Apollo HAL release, whole-firmware completeness, or physical hardware behavior.

The local Apollo510 HAL 5.1 replay has the TON enum definitions in `g2/analysis/bootloader-completion-2026-10-06/upstream-worker/ambiqhal-apollo510/ambiqhal/mcu/apollo510/hal/mcu/am_hal_sysctrl_ton_config.h` and declares `am_hal_spotmgr_ton_config_init/update` in `.../hal/am_hal_spotmgr.h`. Those API/type declarations provide context but no implementation bodies for these exact callbacks. This reconstruction follows the locked instructions; it is not copied from that replay, and no source-version or license equivalence is asserted.
