# Firmware Module Deep Dives

Per-module reverse engineering documentation derived from decompiled firmware analysis.
Each file covers the internal architecture, data structures, and BLE wire behavior of
a specific firmware subsystem.

## BLE Protocol Modules

| Document | Service | Description |
|----------|---------|-------------|
| [ble-multi-connection.md](ble-multi-connection.md) | Multiple | Multi-endpoint BLE identity orchestration (G2-L/G2-R/R1) |
| [display-config.md](display-config.md) | 0x0E-20 | Display viewport/config stream |
| [file-transfer.md](file-transfer.md) | 0xC4/0xC5 | Bidirectional file channel |
| [logger.md](logger.md) | 0x0F-20 | Logger command plane |
| [quicklist-health.md](quicklist-health.md) | 0x0C | Shared quicklist/health service |
| [ring-relay.md](ring-relay.md) | 0x91 | Ring relay envelope parsing |
| [wear-detection.md](wear-detection.md) | — | Wear detection state machine |

## Settings Subsystem (0x0D)

The settings service is the most complex firmware module, using a multi-level dispatch
architecture with selector-based routing:

| Document | Description |
|----------|-------------|
| [settings-dispatch.md](settings-dispatch.md) | Dispatcher internals (selector 1..11) |
| [settings-compact-notify.md](settings-compact-notify.md) | Compact settings status packets on 0x0D-01 |
| [settings-envelope-parser.md](settings-envelope-parser.md) | Root oneof envelope parser (case3..7) |
| [settings-headup-calibration.md](settings-headup-calibration.md) | Head-up calibration handler flow |
| [settings-local-data-status.md](settings-local-data-status.md) | Root case4 local-data status lanes |
| [settings-selector-schema.md](settings-selector-schema.md) | Descriptor-recovered settings protobuf schema |
| [settings-runtime-context.md](settings-runtime-context.md) | Selector runtime context byte writes and gate model |
| [settings-sync-module-config.md](settings-sync-module-config.md) | Settings + SyncInfo/ModuleConfigure coupling |

## Sequence Replay

| Document | Description |
|----------|-------------|
| [sequence-replay-assertions.md](sequence-replay-assertions.md) | Capture-backed sequence replay assertions |
