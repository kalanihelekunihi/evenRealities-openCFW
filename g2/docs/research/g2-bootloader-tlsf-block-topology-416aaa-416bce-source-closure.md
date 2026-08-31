# G2 bootloader TLSF physical-block and alignment source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

## Result

The eight complete authenticated entries at `[0x00416AAA,0x00416BCE)` now route to compilable freestanding C in `components/bootloader/core_overlay/runtime_tlsf_block_topology_416aaa.c`. The 7,601-byte source file has SHA-256 `548353fa534c11a1c354c7d0e95f691ef2dd4634b4c421440814af17b91974e0` and is a bounded BSD-3-Clause adaptation of Matthew Conte TLSF v3.1 for the recovered G2 ILP32 block layout.

| Function | Stock span | Stock bytes | Direct callers | Apple compiled bytes | Strict relocations |
|---|---:|---:|---:|---:|---:|
| previous physical block | `[0x00416AAA,0x00416AD0)` | 38 | 1 | 36 | 1 |
| next physical block | `[0x00416AD0,0x00416B14)` | 68 | 3 | 60 | 4 |
| link next block | `[0x00416B14,0x00416B22)` | 14 | 4 | 12 | 1 |
| mark block free | `[0x00416B22,0x00416B38)` | 22 | 2 | 22 | 3 |
| mark block used | `[0x00416B38,0x00416B4E)` | 22 | 1 | 22 | 3 |
| align integer up | `[0x00416B4E,0x00416B7A)` | 44 | 1 | 44 | 0 |
| align integer down | `[0x00416B7A,0x00416BA4)` | 42 | 1 | 40 | 0 |
| align pointer up | `[0x00416BA4,0x00416BCE)` | 42 | 2 | 44 | 0 |

The tranche closes 292 authenticated stock bytes with 280 compiled bytes and 12 strict source-to-source relocations. It preserves physical-neighbor calculation, previous-block linking, free/used state propagation, power-of-two alignment, and the recovered assertion seam at Thumb address `0x00415735`. The authenticated file/expression pointers `0x00431A04`, `0x0043188C`, `0x004319C8`, and `0x00433A84` and source lines 433, 442, 471, 477, and 485 are pinned.

## Verification

`tests/test_runtime_bootloader_tlsf_block_topology_416aaa_416bce.py` authenticates every stock span, exercises neighbor/link/state behavior and the assertion contracts on the host, and requires a warning-clean Cortex-M55 freestanding compile. `tools/analyze_g2_bootloader_numeric.py` independently pins all eight compiled leaves, caller sets, relocation targets, both compiler profiles, exact patch spans, provider ownership, and unsigned deployment packages.

The current aggregate is 103 routed functions and 61 runtime functions: 4,952 authenticated runtime stock bytes, 4,200 compiled runtime bytes, 229 direct callers, two registered-pointer ingress paths, and 107 strict relocations. Provider accounting is 5,305 source-owned bytes, 6,404 generated patch bytes, 12 alignment bytes, and 142,195 retained official bytes.

The Apple profile produces a 5,316-byte overlay (`e970a788f4c77773eaa5dbe64cfdaf82f4b86d02f7335f058cafa615e88ef2d3`), a 153,916-byte provider (`0efeae40fa56e6db923b8805ca7d77210a15e1ad08355730a7ebd1e1b8a325fb`), and a 4,735,494-byte unsigned package (`a22ab2087160d879f61d2aef26f86d491d4c13d28cd3d78d80745018b26b46c8`). The Linux profile produces a 5,300-byte overlay (`06fe1d6ebde3d7df35cde5caf4ebb7679ec51c85a1b58206b3c143ab0eefa691`), a 153,900-byte provider (`066d5f7ac4facdb9cc66580eae181bbcf3533298cb6fd3d19ebe8ae64d9a8f92`), and a 4,511,488-byte unsigned package (`1b9ba6ad77cb8b45e8148a29c1998eeb3807aca2c6d82eec666f8f37ddf61cc1`).

## Remaining boundary and hardware evidence

The next distinct complete callable body begins at `0x00416BCE`; `[0x00416BCE,0x00417AD4)` remains a 3,846-byte software gap before the already routed EasyLogger entries. No image was signed, flashed, installed, reset, or booted. Live heap mutation, fragmentation/coalescing, allocator-caller, and boot validation remain explicitly blocked because no authorized responsive G2 right temple is available. This tranche is software-closed, but firmware-wide functional completeness is not claimed.
