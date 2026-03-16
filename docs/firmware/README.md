# Firmware & Reverse Engineering

Firmware update pipeline, binary analysis, per-component structure, and app reverse engineering.

## Overview & Analysis

| Document | Description |
|----------|-------------|
| [firmware-files.md](firmware-files.md) | **Start here** - device-to-hardware mapping, EVENOTA format, flash layouts, BLE transfer protocols |
| [firmware-reverse-engineering.md](firmware-reverse-engineering.md) | G2 firmware binary analysis - Apollo510b SoC, EM9305 BLE, hardware BOM, LVGL/NemaGFX |
| [device-boot-call-trees.md](device-boot-call-trees.md) | Per-device boot flow and runtime call trees (G2-L/R, G2-Case, R1) |
| [firmware-communication-topology.md](firmware-communication-topology.md) | Cross-device runtime communication graph: internal buses, BLE/API paths |
| [g2-service-handler-index.md](g2-service-handler-index.md) | Service IDs to handler symbols/offsets dispatch appendix |
| [g2-firmware-modules.md](g2-firmware-modules.md) | Module-by-module firmware behavior map with parity status |
| [firmware-updates.md](firmware-updates.md) | OTA firmware check APIs, CDN auth, EVENOTA format |
| [ota-protocol.md](ota-protocol.md) | BLE wire protocol for firmware transfer - chunking, ACK codes, timing |
| [even-app-reverse-engineering.md](even-app-reverse-engineering.md) | Even.app static RE - Flutter/Dart protocol internals, DFU bootloader |
| [ios-firmware-gap-report.md](ios-firmware-gap-report.md) | EvenG2Shortcuts vs firmware audit: implementation gaps |
| [re-gaps-tracker.md](re-gaps-tracker.md) | Prioritized reverse-engineering backlog with closure criteria |
| [SDKs.md](SDKs.md) | SDK inventory (TypeScript, Dart, internal) |
| [ble-surface-report.md](ble-surface-report.md) | BLE-exposed surface audit vs iOS app implementation |

## Module Deep Dives

| Document | Description |
|----------|-------------|
| [modules/ble-multi-connection.md](modules/ble-multi-connection.md) | Multi-endpoint BLE identity orchestration (G2-L/G2-R/R1) |
| [modules/sequence-replay-assertions.md](modules/sequence-replay-assertions.md) | Capture-backed sequence replay assertions |
| [modules/display-config.md](modules/display-config.md) | Display viewport/config stream (0x0E-20) |
| [modules/file-transfer.md](modules/file-transfer.md) | Bidirectional file channel (0xC4/0xC5) |
| [modules/logger.md](modules/logger.md) | Logger command plane (0x0F-20) |
| [modules/quicklist-health.md](modules/quicklist-health.md) | Shared quicklist/health service (0x0C) |
| [modules/ring-relay.md](modules/ring-relay.md) | Ring relay service (0x91) envelope parsing |
| [modules/settings-dispatch.md](modules/settings-dispatch.md) | Settings dispatcher internals (selector 1..11) |
| [modules/settings-compact-notify.md](modules/settings-compact-notify.md) | Compact settings status packets on 0x0D-01 |
| [modules/settings-envelope-parser.md](modules/settings-envelope-parser.md) | Root oneof envelope parser (case3..7) |
| [modules/settings-headup-calibration.md](modules/settings-headup-calibration.md) | Head-up calibration handler flow |
| [modules/settings-local-data-status.md](modules/settings-local-data-status.md) | Root case4 local-data status lanes |
| [modules/settings-selector-schema.md](modules/settings-selector-schema.md) | Descriptor-recovered settings selector protobuf schema |
| [modules/settings-runtime-context.md](modules/settings-runtime-context.md) | Selector runtime context byte writes and gate model |
| [modules/settings-sync-module-config.md](modules/settings-sync-module-config.md) | Settings + SyncInfo/ModuleConfigure coupling |
| [modules/wear-detection.md](modules/wear-detection.md) | Wear detection state machine |

## Per-Component Binary Structure

| Document | Binary File | Target IC |
|----------|------------|-----------|
| [s200-firmware-ota.md](s200-firmware-ota.md) | `ota_s200_firmware_ota.bin` | Apollo510b (main SoC) |
| [s200-bootloader.md](s200-bootloader.md) | `ota_s200_bootloader.bin` | Apollo510b (bootloader) |
| [ble-em9305.md](ble-em9305.md) | `firmware_ble_em9305.bin` | EM9305 (BLE radio) |
| [codec-gx8002b.md](codec-gx8002b.md) | `firmware_codec.bin` | GX8002B (audio codec) |
| [touch-cy8c4046fni.md](touch-cy8c4046fni.md) | `firmware_touch.bin` | CY8C4046FNI (touch) |
| [box-case-mcu.md](box-case-mcu.md) | `firmware_box.bin` | Case MCU |

## Decompilation (v2.0.7.16)

Detailed decompilation artifacts for firmware v2.0.7.16, including function maps,
data maps, handler maps, RTOS task analysis, and annotated pseudo-C for all 6 firmware
components. See [decompilation/ANALYSIS.md](decompilation/ANALYSIS.md).

The raw decompilation working directory with tools and binary output is at
`decompiledFW/` in the repository root.

## Firmware Version Analysis

Dated investigation logs from firmware analysis sessions (extracted from BLE captures
and binary analysis). See [analysis/](analysis/) for 37+ investigation files covering:

- Per-version firmware analysis (v2.0.1.14 through v2.0.7.16)
- Service handler call chains and dispatch tables
- Settings system deep dives
- Boot sequence and scheduler analysis
- BLE artifact extraction and string cross-references
