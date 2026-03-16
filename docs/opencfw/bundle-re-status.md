# Bundle RE Status

This document tracks reverse-engineering closure per firmware bundle and records what `openCFW` can safely treat as implementation input.

## Bundle Matrix

| Bundle | State | Identified | Inferred | Unidentified / Blocked | openCFW Posture |
|---|---|---|---|---|---|
| `ota_s200_firmware_ota.bin` | Partial but executable | Apollo510b runtime, lane split, service table, OTA orchestration, display/audio/input/settings topology | Some service field maps, scheduler helper naming, dashboard/widget boundaries | Full startup symbolization, `0x90`, exact `0x08`/`0x09` field maps | Primary clean-room target |
| `ota_s200_bootloader.bin` | Identified with bounded unknowns | VTOR handoff, `/ota` install flow, CRC/program/verify path, LittleFS staging | Boot metadata semantics beyond logged fields | Safe replacement/re-signing story, exact rollback metadata layout | Compatibility target, not first rewrite target |
| `firmware_ble_em9305.bin` | Identified container, partial semantics | 4-record patch layout, flash targets, update order, Apollo-side HCI ownership | Record-level functional roles beyond config/handler/main split | Function-level radio behavior inside patch | Interface boundary only |
| `firmware_codec.bin` | Identified container, partial internals | FWPK wrapper, dual BINH stages, TinyFrame host path, stable size/history | Some BINH header field meanings, internal DSP behavior beyond boot flow | Full command dictionary and codec-local control/state machine | Apollo host boundary only |
| `firmware_touch.bin` | Identified container, partial internals | FWPK + CRC32C, vector table, I2C DFU path, touch-controller ownership | Wear/proximity enhancements from string and size deltas | Internal gesture thresholds, exact row/update grammar | Apollo host boundary only |
| `firmware_box.bin` | Partial but instruction-anchored | EVEN wrapper, checksum, vector table, startup chain, scheduler handoff, some UART commands | STM32-like family, dual-bank behavior, broader case command model | Exact MCU part, full case UART opcode grammar, deeper relay semantics | Relay compatibility target after more closure |
| `B210_ALWAY_BL_DFU_NO` | Partial but executable | Failsafe bootloader package, reset chain, init-walker loop, stage2 target `0x000FADBC` | Failsafe or emergency recovery role in the ring Nordic family | Exact field deployment policy and relation to the versioned bootloader | Reference-only for now |
| `B210_BL_DFU_NO_v2.0.3.0004` | Partial but executable | Versioned bootloader package, reset chain, init-walker loop, stage2 target `0x000FADC8` | Normal ring-side bootloader update path | Exact rollout policy versus the failsafe bootloader | Reference-only for now |
| `B210_SD_ONLY_NO_v2.0.3.0004` | Partial but executable | SoftDevice package, reset dispatch, pre-reset `wfe` idle loop, stage2 entry `0x00001108` | Ring-side BLE stack update separate from the missing app runtime | Exact SoC pairing and exact version-coupling policy | Reference-only for now |
| Standalone R1 application runtime | Blocked | No app runtime image in corpus yet | Protocol and DFU behavior suggest separate Nordic app runtime | Main app binary, symbols, runtime call tree | Defer entirely |

## Apollo Main Runtime

### Identified

- Control, display, and file lanes are distinct and stable.
- Apollo510b owns BLE host logic, scheduler, UI, files, and OTA orchestration.
- The firmware contains the authoritative service routing for `0x01..0x22`, `0x81`, `0x91`, and `0xFF`.
- Descriptor-adjacent closure now anchors executable lanes for navigation `0x08`, device-info/dev-config `0x09`, ring relay `0x91`, and system monitor `0xFF`.

### Inferred

- Scheduler helper naming is still partly semantic rather than vendor-symbol backed.
- Dashboard/widget and some UI-service boundaries are visible but not field-complete.
- Device-info and navigation services are structurally real enough to stub, but not yet authoritative at the field-enum level.

### Unidentified

- Exact `0x08` command enums and final symbolic handler names.
- Exact `0x09` command field map and final symbolic handler name.
- Reserved `0x90` service semantics.
- Fully symbolized reset-to-idle runtime call graph.

## Apollo Bootloader

### Identified

- Bootloader base is `0x00410000`; main app handoff target is `0x00438000`.
- Handoff uses VTOR relocation, MSP reload, and branch to app reset.
- OTA install path stages images in LittleFS and performs CRC/program/verify before handoff.

### Inferred

- Boot metadata carries more structure than the logged `targetRunAddr` and size/CRC checks expose.
- Recovery/rollback policy is likely conservative and stable across versions.

### Unidentified

- Exact metadata structure used to validate and select images.
- Exact safe replacement requirements for a non-vendor boot image.

## Peripheral Bundles

### EM9305 BLE Patch

- Identified: patch-record container layout and Apollo-side programming boundary.
- Inferred: config/params/handler/main split corresponds to radio startup/runtime responsibilities.
- Unknown: internal controller semantics remain opaque without deeper EM9305-specific decoding.

### GX8002B Codec

- Identified: FWPK container, BINH boot stages, TinyFrame boot/download sequence.
- Inferred: some header fields, DSP feature modules, and wake-word behavior from strings.
- Unknown: authoritative codec-local control/state semantics.

### CY8C4046FNI Touch

- Identified: FWPK + CRC32C, vector table, Apollo-owned I2C DFU/update flow.
- Inferred: v2.0.6.14 growth adds proximity baseline and fast-click behavior.
- Unknown: internal gesture thresholds, calibration tables, and complete bootloader row protocol.

### Case MCU

- Identified: EVEN wrapper, additive checksum, startup chain, task map, relay/update path.
- Inferred: STM32-like family, dual-bank update behavior, wider case telemetry/control model.
- Unknown: exact part number and full UART grammar.

## Clean-Room Guidance

- Only the Apollo main runtime should be treated as a direct implementation target today.
- Bootloader, case, ring, and peripheral binaries should currently be modeled as compatibility boundaries.
- For EM9305, codec, touch, and case, `openCFW` should first emulate the Apollo-side owner behavior rather than re-implementing subordinate firmware images.

## Source Documents

- `../firmware/s200-firmware-ota.md`
- `../firmware/s200-bootloader.md`
- `../firmware/ble-em9305.md`
- `../firmware/codec-gx8002b.md`
- `../firmware/touch-cy8c4046fni.md`
- `../firmware/box-case-mcu.md`
- `../firmware/device-boot-call-trees.md`
- `../firmware/g2-service-handler-index.md`
- `../firmware/re-gaps-tracker.md`
