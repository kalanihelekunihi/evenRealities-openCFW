# G2 bootloader TLSF block-header primitive source closure

Status: implemented in production source; offline verification green; physical boot and heap validation blocked by unavailable authorized hardware evidence.

## Boundary and provenance

The authenticated G2 2.2.6.10 S200 bootloader contains twelve consecutive complete callable bodies at `[0x004169FC,0x00416AAA)`. Their structure and ILP32 block layout match Matthew Conte TLSF v3.1 from the repository's authenticated BSD-3-Clause snapshot. The production implementation is the bounded freestanding adaptation in `components/bootloader/core_overlay/runtime_tlsf_block_primitives_4169fc.c`; it uses a 16-byte header, status bits 0 and 1 in the size word, and an eight-byte user-pointer offset.

| Primitive | Stock range | Stock B | Stock SHA-256 | Direct callers | Compiled B |
|---|---:|---:|---|---:|---:|
| block size | `0x004169FC..0x00416A10` | 20 | `a67ca544…0db38` | 10 | 8 |
| set size | `0x00416A10..0x00416A2C` | 28 | `6d72ee9f…f9b3c` | 4 | 12 |
| is last | `0x00416A2C..0x00416A40` | 20 | `7a70a168…4581` | 3 | 10 |
| is free | `0x00416A40..0x00416A4C` | 12 | `1f486b8f…3d4e` | 4 | 8 |
| set free | `0x00416A4C..0x00416A5A` | 14 | `909bbd0a…a040` | 2 | 10 |
| set used | `0x00416A5A..0x00416A68` | 14 | `766e7c84…045d` | 2 | 10 |
| previous is free | `0x00416A68..0x00416A74` | 12 | `c534389c…402d` | 2 | 8 |
| set previous free | `0x00416A74..0x00416A82` | 14 | `188a5913…d7c8` | 3 | 10 |
| set previous used | `0x00416A82..0x00416A90` | 14 | `552a382a…3698` | 2 | 10 |
| block from pointer | `0x00416A90..0x00416A9C` | 12 | `57d962b3…cc3a` | 1 | 4 |
| block to pointer | `0x00416A9C..0x00416AA6` | 10 | `9d79408f…687c` | 7 | 4 |
| offset to block | `0x00416AA6..0x00416AAA` | 4 | `29bce340…3434` | 3 | 4 |

The 174 stock bytes have 43 direct callers and no authenticated stored-function-pointer ingress. Apple clang 21 and exact-root Linux clang 22.1.8 emit the same 98 relocation-free Thumb bytes, with every individual leaf hash pinned by `tools/analyze_g2_bootloader_numeric.py`.

## Functional and production gates

Host tests authenticate every stock span and exercise size masking, preservation and mutation of both status flags, last-block detection, user-pointer round trips, and offset arithmetic. Freestanding Cortex-M55 compilation, isolated section extraction, exact full-span redirects, dual-profile provider contracts, manifest ownership, package generation, flash-plan generation, and all legacy bootloader analyzers pass. The authoritative gate is `make bootloader-numeric-closure`.

The resulting canonical Apple artifacts are a 5,036-byte overlay, a 153,636-byte provider, and a 4,735,214-byte unsigned package. Aggregate bootloader accounting is 95 routed functions, 53 runtime functions, 214 direct callers, 4,660 authenticated runtime stock bytes, 3,920 compiled runtime bytes, 95 strict relocations, 5,025 source-owned bytes, 6,112 generated patch bytes, 12 alignment bytes, and 142,487 retained official bytes. The next distinct complete executable body starts at `0x00416AAA`; `[0x00416AAA,0x00417AD4)` remains a 4,138-byte software gap.

## Physical evidence block

No signing, flashing, installation, reset, boot, heap mutation, or hardware operation was performed. Live TLSF allocation/free/coalescing behavior and boot-path caller validation require an authorized responsive G2 right temple. That physical evidence is unavailable; the authorized left temple remains stock. This tranche is software-complete only, and neither the remaining bootloader nor the firmware is declared functionally complete.
