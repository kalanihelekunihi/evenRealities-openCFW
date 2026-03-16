# Evidence Index

This document is the clean-room source spine for `openCFW/docs/`. It records which existing repo documents currently support identified, inferred, and unresolved functionality.

## Identified Coverage Spine

### Transport, Session, and Service Routing

- `../protocol-overview.md`
- `../protocols/packet-structure.md`
- `../protocols/services.md`
- `../protocols/authentication.md`
- `../protocols/connection-lifecycle.md`

### Device Firmware Ownership and Target Scope

- `../firmware/firmware-files.md`
- `../firmware/firmware-communication-topology.md`
- `../firmware/device-boot-call-trees.md`
- `../firmware/ota-protocol.md`
- `../firmware/firmware-updates.md`
- `../devices/g2-glasses.md`
- `../devices/g2-case.md`
- `../devices/r1-ring.md`
- `../devices/r1-cradle.md`
- `../firmware/analysis/2026-03-05-r1-nordic-dfu-startup-chain.md`
- `../firmware/analysis/2026-03-05-r1-nordic-stage2-idle-paths.md`

### Connection, Auth, and Identity

- `../protocols/authentication.md`
- `../protocols/connection-lifecycle.md`
- `../firmware/modules/ble-multi-connection.md`
- `../devices/g2-glasses.md`
- `../devices/r1-ring.md`
- `../firmware/firmware-reverse-engineering.md`
- `../firmware/g2-firmware-modules.md`

### Input, Gesture, and Wear-Gated Interaction

- `../features/gestures.md`
- `../firmware/touch-cy8c4046fni.md`
- `../firmware/modules/wear-detection.md`
- `../firmware/modules/ring-relay.md`
- `../devices/g2-glasses.md`
- `../devices/r1-ring.md`
- `../protocols/nus-protocol.md`
- `../firmware/firmware-reverse-engineering.md`
- `../firmware/firmware-communication-topology.md`
- `../firmware/g2-firmware-modules.md`

### Sensors, Telemetry, and Calibration

- `../features/brightness.md`
- `../firmware/modules/display-config.md`
- `../firmware/modules/settings-sync-module-config.md`
- `../firmware/modules/settings-headup-calibration.md`
- `../devices/g2-glasses.md`
- `../firmware/firmware-reverse-engineering.md`
- `../firmware/firmware-communication-topology.md`
- `../firmware/g2-firmware-modules.md`

### Lifecycle, Modes, and Orchestration

- `../features/display-pipeline.md`
- `../firmware/modules/settings-compact-notify.md`
- `../firmware/modules/settings-sync-module-config.md`
- `../firmware/modules/settings-headup-calibration.md`
- `../firmware/device-boot-call-trees.md`
- `../firmware/firmware-reverse-engineering.md`
- `../firmware/g2-firmware-modules.md`
- `../firmware/even-app-reverse-engineering.md`
- `../protocols/services.md`
- `../firmware/analysis/2026-03-05-g2-system-monitor-callchain.md`

### Display and Render Pipeline

- `../features/display-pipeline.md`
- `../features/eventhub.md`
- `../firmware/modules/display-config.md`
- `../devices/g2-glasses.md`

### Primary Feature Protocols

- `../features/teleprompter.md`
- `../features/even-ai.md`
- `../features/navigation.md`
- `../features/conversate.md`

### Audio, Voice, and NUS Side Channel

- `../protocols/nus-protocol.md`
- `../firmware/codec-gx8002b.md`
- `../devices/g2-glasses.md`
- `../firmware/firmware-reverse-engineering.md`
- `../firmware/firmware-communication-topology.md`
- `../firmware/g2-firmware-modules.md`
- `../features/even-ai.md`
- `../features/conversate.md`

### Feature State, User Data, and Presentation Control

- `../features/brightness.md`
- `../firmware/modules/quicklist-health.md`
- `../firmware/modules/settings-compact-notify.md`
- `../protocols/notification.md`
- `../firmware/modules/logger.md`

### Settings, State, Brightness, Wear, and Calibration

- `../features/brightness.md`
- `../firmware/modules/settings-dispatch.md`
- `../firmware/modules/settings-selector-schema.md`
- `../firmware/modules/wear-detection.md`

### Peripheral, Peer, and Relay Boundaries

- `../firmware/ble-em9305.md`
- `../firmware/codec-gx8002b.md`
- `../firmware/touch-cy8c4046fni.md`
- `../firmware/box-case-mcu.md`
- `../firmware/device-boot-call-trees.md`
- `../firmware/firmware-communication-topology.md`
- `../devices/g2-glasses.md`
- `../devices/g2-case.md`
- `../devices/r1-ring.md`

### Device State, Power, and Role

- `../firmware/modules/ble-multi-connection.md`
- `../firmware/modules/settings-local-data-status.md`
- `../firmware/modules/settings-runtime-context.md`
- `../firmware/modules/wear-detection.md`
- `../firmware/device-boot-call-trees.md`
- `../devices/g2-glasses.md`
- `../devices/g2-case.md`
- `../devices/r1-ring.md`

### Input, Ring, Notifications, Files, and Diagnostics

- `../features/gestures.md`
- `../protocols/nus-protocol.md`
- `../protocols/notification.md`
- `../firmware/modules/file-transfer.md`
- `../firmware/modules/logger.md`
- `../devices/r1-ring.md`

### Firmware Packaging, Boot, OTA, and Topology

- `../firmware/firmware-files.md`
- `../firmware/firmware-updates.md`
- `../firmware/ota-protocol.md`
- `../firmware/s200-bootloader.md`
- `../firmware/firmware-communication-topology.md`
- `../devices/g2-glasses.md`
- `../devices/g2-case.md`

### Memory, Flash, and Persistence

- `../firmware/s200-firmware-ota.md`
- `../firmware/s200-bootloader.md`
- `../firmware/device-boot-call-trees.md`
- `../firmware/ota-protocol.md`
- `../firmware/modules/logger.md`
- `../protocols/notification.md`
- `../devices/g2-glasses.md`

### Update and Recovery

- `../firmware/ota-protocol.md`
- `../firmware/firmware-files.md`
- `../firmware/firmware-updates.md`
- `../firmware/s200-bootloader.md`
- `../firmware/device-boot-call-trees.md`
- `../firmware/box-case-mcu.md`
- `../devices/r1-ring.md`
- `../firmware/analysis/2026-03-05-r1-nordic-dfu-startup-chain.md`
- `../firmware/analysis/2026-03-05-r1-nordic-stage2-idle-paths.md`

### Diagnostics, Monitor, and Debug Surfaces

- `../devices/g2-glasses.md`
- `../firmware/s200-firmware-ota.md`
- `../firmware/firmware-reverse-engineering.md`
- `../firmware/g2-firmware-modules.md`
- `../firmware/modules/logger.md`
- `../firmware/modules/file-transfer.md`
- `../protocols/services.md`
- `../firmware/firmware-communication-topology.md`
- `../firmware/device-boot-call-trees.md`
- `../firmware/analysis/2026-03-05-g2-system-monitor-callchain.md`

## Inferred Coverage Spine

These documents materially inform planning, but they should not be treated as authoritative field/schema truth by themselves.

- `../firmware/even-app-reverse-engineering.md`
- `../firmware/g2-firmware-modules.md`
- `../firmware/modules/settings-sync-module-config.md`
- `../reference/unidentified-behaviors.md`
- `../firmware/analysis/2026-03-05-g2-nav-devinfo-descriptor-lanes.md`
- `../firmware/analysis/2026-03-05-g2-ring-relay-callchain.md`
- `../firmware/analysis/2026-03-05-g2-system-monitor-callchain.md`
- `../firmware/analysis/2026-03-05-r1-nordic-dfu-startup-chain.md`
- `../firmware/analysis/2026-03-05-r1-nordic-stage2-idle-paths.md`

## Active Unresolved/Gap Trackers

- `../firmware/re-gaps-tracker.md`
- `../firmware/g2-service-handler-index.md`
- `../reference/magic-numbers.md`
- `../reference/unidentified-behaviors.md`

## Clean-Room Rule

When `openCFW` code is written, use this order of trust:

1. `identified-functionality.md`
2. `service-map.md`
3. `inferred-functionality.md`
4. `unidentified-functionality.md`
5. upstream evidence docs listed above
