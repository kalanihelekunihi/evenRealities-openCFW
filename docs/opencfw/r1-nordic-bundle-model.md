# R1 Nordic Bundle Model

This document is the clean-room model for the R1-side Nordic bundle family currently present in the local corpus. It separates the identified bootloader and SoftDevice artifacts from the still-missing standalone ring application runtime.

## In-Corpus Bundle Matrix

| Bundle | Kind | Current State | Identified | Inferred | Unidentified / Blocked |
|---|---|---|---|---|---|
| `B210_ALWAY_BL_DFU_NO` | failsafe bootloader | Partial but executable | Nordic Secure DFU package, `bootloader.bin` startup chain, stage1 init walker, stage2 entry `0x000FADBC` | emergency or recovery bootloader role | exact field deployment policy, exact production target selection |
| `B210_BL_DFU_NO_v2.0.3.0004` | versioned bootloader | Partial but executable | Nordic Secure DFU package, `bootloader.bin` startup chain, stage1 init walker, stage2 entry `0x000FADC8` | normal bootloader update path for the ring-side Nordic domain | exact rollout policy versus failsafe bootloader |
| `B210_SD_ONLY_NO_v2.0.3.0004` | SoftDevice-only bundle | Partial but executable | Nordic Secure DFU package, `softdevice.bin` vector table, reset dispatch, `wfe` idle loop | ring-side BLE stack update independent of the missing app runtime | exact target SoC and exact pairing with bootloader/runtime versions |
| Standalone R1 application runtime image | application runtime | Blocked | Separate ring runtime clearly exists at the system/protocol level | must be a Nordic application image outside the current corpus | actual app binary, symbols, runtime call tree, package contract |

## Identified Artifacts

### Bootloader Family

The local corpus now contains two distinct bootloader artifacts for the R1 Nordic domain:

| Bundle | Primary Binary | Size | SHA-256 | Vector Base | SP | Reset |
|---|---|---:|---|---:|---:|---:|
| `B210_ALWAY_BL_DFU_NO` | `bootloader.bin` | 24180 | `67cc2e9d3f70ea00e8246fe5715fd48067d6825a11425fa2a3c73bc9fc383714` | `0x000F8000` | `0x2000CFA0` | `0x000F83D9` |
| `B210_BL_DFU_NO_v2.0.3.0004` | `bootloader.bin` | 24420 | `e049131a92c203e1c1f0abb067653e046c6955157e522914556004402f29ac60` | `0x000F8000` | `0x2000CFA0` | `0x000F83D9` |

Shared identified behavior:

- both bootloaders use the same reset prefix `0x000F83D8 -> 0x000F8200`
- both walk an init table via `0x000F8204 -> 0x000F84C8` with loop backedge `0x000F84DE -> 0x000F84CE`
- both then hand off into deeper stage2 logic, but at different targets:
  - failsafe bootloader: `0x000F820A -> 0x000FADBC`
  - versioned bootloader: `0x000F820A -> 0x000FADC8`

Clean-room implication: `openCFW` can safely treat these as real, distinct ring-side bootloader bundles rather than as one generic Nordic placeholder.

### SoftDevice Bundle

| Bundle | Primary Binary | Size | SHA-256 | Vector Base | SP | Reset |
|---|---|---:|---|---:|---:|---:|
| `B210_SD_ONLY_NO_v2.0.3.0004` | `softdevice.bin` | 153140 | `192af010d0c5ca2111e14e644c02f79ac149f980c5ce7c729b006b1cf70eafd2` | `0x00001000` | `0x200013C0` | `0x00025FE1` |

Identified behavior:

- pre-reset low-power wait loop at `0x00025FDC (wfe)` with backedge `0x00025FDE -> 0x00025FDC`
- reset dispatch from `0x00025FE0` into helper calls and stage2 entry `0x00001108`
- separate signed init packet and standalone `softdevice.bin` confirm this is a BLE-stack artifact, not the ring application runtime

Clean-room implication: `openCFW` can recognize and validate this bundle family as part of the ring-side Nordic deployment domain, but not as the missing ring app.

## Inferred Deployment Model

### The Three Bundles Belong to One Nordic Recovery/Install Family

- All three bundles are distributed as Even.app Nordic DFU assets rather than G2 EVENOTA components.
- The bootloader pair plus SoftDevice strongly suggest a ring-side Nordic install or recovery family with separate responsibilities:
  - one normal/versioned bootloader path
  - one always-available or failsafe bootloader path
  - one BLE stack update path

### The Missing Runtime Is Separate

- System-level evidence still shows ring runtime behavior beyond what the bootloader and SoftDevice can explain.
- The ring application runtime therefore remains a separate artifact class, not merely hidden inside the present bootloader or SoftDevice bundles.

### The Deployment Route Is Still Not Fully Closed

- `firmware-files.md` and the tagged corpus close the existence of these assets.
- What is still not closed is the exact product-path split:
  - production ring updates
  - recovery-only use
  - auxiliary or legacy Nordic deployment

## Unidentified / Blocked Areas

| Area | Why It Matters |
|---|---|
| Standalone R1 application runtime image | blocks any serious ring clean-room runtime implementation |
| Exact selection policy between `B210_ALWAY_BL_DFU_NO` and `B210_BL_DFU_NO_v2.0.3.0004` | needed before modeling ring-side boot recovery behavior |
| Exact production SoC SKU for the ring | needed before treating SoftDevice/bootloader pairing as authoritative hardware truth |
| Exact public or app-internal distribution contract for the ring bundles | needed for any future clean-room packaging or update tooling |

## Clean-Room Guidance

- Treat the R1 Nordic family as a separate device domain outside the Apollo rewrite target.
- Track the failsafe bootloader, versioned bootloader, and SoftDevice as separate bundles with separate validation and policy.
- Do not start a ring runtime rewrite from these artifacts alone.
- Keep ring-side work limited to FE59, SMP or MCUmgr, bundle validation, and protocol compatibility until the standalone application image is recovered.

## Source Documents

- `../firmware/firmware-files.md`
- `../firmware/device-boot-call-trees.md`
- `../devices/r1-ring.md`
- `../firmware/analysis/2026-03-05-r1-nordic-dfu-startup-chain.md`
- `../firmware/analysis/2026-03-05-r1-nordic-stage2-idle-paths.md`
- `../../captures/firmware/tagged/r1-ring/bootloader-2.0.3.0004/artifact.json`
- `../../captures/firmware/tagged/r1-ring/failsafe-bootloader/artifact.json`
- `../../captures/firmware/tagged/r1-ring/softdevice-2.0.3.0004/artifact.json`
