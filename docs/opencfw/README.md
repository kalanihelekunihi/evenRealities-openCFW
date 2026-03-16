# openCFW Docs

Clean-room documentation set for the custom firmware effort. Everything here is derived from the local reverse-engineering corpus already stored in this repository.

## Coverage

- [bundles-and-hardware.md](bundles-and-hardware.md)
  Inventory of the firmware bundles, target ICs, wrapper formats, and custom-firmware relevance.
- [bundle-re-status.md](bundle-re-status.md)
  Bundle-by-bundle reverse-engineering closure status, separated into identified, inferred, and blocked/unknown areas.
- [device-firmware-ownership-model.md](device-firmware-ownership-model.md)
  Per-device image ownership for G2-L, G2-R, G2-Case, R1 Ring, and the passive R1 cradle.
- [r1-nordic-bundle-model.md](r1-nordic-bundle-model.md)
  Clean-room split of the in-corpus R1 Nordic bootloader and SoftDevice bundles versus the still-missing standalone ring app runtime.
- [peripheral-interface-model.md](peripheral-interface-model.md)
  Apollo-side boundary model for EM9305, codec, touch, peer-sync, case relay, and ring integration.
- [service-map.md](service-map.md)
  Runtime service/lane map for the Apollo510b main firmware and adjacent transport lanes, with confidence states.
- [transport-and-packet-formats.md](transport-and-packet-formats.md)
  Clean-room transport baseline for lane UUIDs, G2 packet framing, auth, file transfer, and known ambiguities.
- [connection-and-identity-model.md](connection-and-identity-model.md)
  BLE identity, app-layer auth, per-connection routing, keepalive, and discoverability model.
- [image-formats-and-boot-path.md](image-formats-and-boot-path.md)
  Clean-room image/container format notes and the Apollo boot handoff path.
- [memory-and-persistence-model.md](memory-and-persistence-model.md)
  Apollo internal-flash, SRAM, external-flash, LittleFS, OTA staging, and persistent-object model.
- [update-and-recovery-model.md](update-and-recovery-model.md)
  Clean-room OTA session, staging, install, reboot, box-update, and ring-DFU model.
- [device-state-and-role-model.md](device-state-and-role-model.md)
  Peer-role, battery, charging, wear, case, and ring-state model for the clean-room runtime.
- [input-and-gesture-model.md](input-and-gesture-model.md)
  Touch-controller boundary, gesture planes, wear-gated input policy, and ring gesture model.
- [sensor-and-calibration-model.md](sensor-and-calibration-model.md)
  Sensor inventory, ALS/brightness sync, display telemetry, and calibration/config-sync model.
- [lifecycle-and-orchestration-model.md](lifecycle-and-orchestration-model.md)
  Idle/runtime mode transitions, onboarding, head-up wake policy, timeout/auto-close, and alert/close orchestration model.
- [feature-and-presentation-model.md](feature-and-presentation-model.md)
  Display bring-up, feature-mode transitions, and user-facing service model for the clean-room runtime.
- [audio-and-voice-model.md](audio-and-voice-model.md)
  Codec host boundary, NUS microphone path, audio-owner arbitration, and phone-side speech model.
- [diagnostics-and-observability-model.md](diagnostics-and-observability-model.md)
  Logger, export, system-monitor, crash-artifact, and debug-shell model for the clean-room runtime.
- [runtime-startup-and-task-model.md](runtime-startup-and-task-model.md)
  Reset-to-idle runtime chain, descriptor object model, worker/task ownership, and remaining startup unknowns.
- [settings-and-state-model.md](settings-and-state-model.md)
  Clean-room view of `0x0D` settings roots, selectors, local-data lanes, and unresolved state writers.
- [identified-functionality.md](identified-functionality.md)
  Confirmed functionality recovered strongly enough to drive implementation.
- [inferred-functionality.md](inferred-functionality.md)
  High-confidence behavior that is real but not yet closed at the symbol, field, or ownership level.
- [unidentified-functionality.md](unidentified-functionality.md)
  Remaining unknowns, missing artifacts, and unresolved protocol/firmware behavior.
- [assumption-log.md](assumption-log.md)
  Explicit clean-room assumptions promoted from RE into implementation planning, with validation notes.
- [evidence-index.md](evidence-index.md)
  Source-document spine grouped by identified, inferred, and unresolved coverage.
- [custom-firmware-roadmap.md](custom-firmware-roadmap.md)
  Phase plan for implementing clean-room custom firmware in `openCFW/src`.

## Read Order

1. `bundles-and-hardware.md`
2. `bundle-re-status.md`
3. `device-firmware-ownership-model.md`
4. `r1-nordic-bundle-model.md`
5. `peripheral-interface-model.md`
6. `transport-and-packet-formats.md`
7. `connection-and-identity-model.md`
8. `image-formats-and-boot-path.md`
9. `memory-and-persistence-model.md`
10. `update-and-recovery-model.md`
11. `device-state-and-role-model.md`
12. `input-and-gesture-model.md`
13. `sensor-and-calibration-model.md`
14. `lifecycle-and-orchestration-model.md`
15. `feature-and-presentation-model.md`
16. `audio-and-voice-model.md`
17. `diagnostics-and-observability-model.md`
18. `runtime-startup-and-task-model.md`
19. `settings-and-state-model.md`
20. `service-map.md`
21. `identified-functionality.md`
22. `inferred-functionality.md`
23. `unidentified-functionality.md`
24. `assumption-log.md`
25. `evidence-index.md`
26. `custom-firmware-roadmap.md`

## Confidence Model

- `Identified`: strong enough to guide clean-room implementation directly.
- `Inferred`: real enough to plan around, but still requires feature flags, instrumentation, or further closure.
- `Unidentified`: not safe to implement beyond scaffolding and trace capture.

## Primary Evidence

- `../firmware/firmware-files.md`
- `../firmware/firmware-reverse-engineering.md`
- `../firmware/s200-firmware-ota.md`
- `../firmware/s200-bootloader.md`
- `../firmware/device-boot-call-trees.md`
- `../firmware/firmware-communication-topology.md`
- `../firmware/ota-protocol.md`
- `../firmware/firmware-updates.md`
- `../protocols/authentication.md`
- `../protocols/connection-lifecycle.md`
- `../features/display-pipeline.md`
- `../features/eventhub.md`
- `../features/teleprompter.md`
- `../features/even-ai.md`
- `../features/navigation.md`
- `../features/conversate.md`
- `../features/brightness.md`
- `../features/gestures.md`
- `../firmware/even-app-reverse-engineering.md`
- `../firmware/modules/settings-sync-module-config.md`
- `../firmware/modules/settings-headup-calibration.md`
- `../firmware/modules/logger.md`
- `../firmware/modules/file-transfer.md`
- `../firmware/modules/display-config.md`
- `../firmware/modules/quicklist-health.md`
- `../firmware/modules/settings-compact-notify.md`
- `../firmware/modules/ble-multi-connection.md`
- `../firmware/modules/settings-local-data-status.md`
- `../firmware/modules/settings-runtime-context.md`
- `../firmware/modules/wear-detection.md`
- `../firmware/ble-em9305.md`
- `../firmware/codec-gx8002b.md`
- `../firmware/touch-cy8c4046fni.md`
- `../firmware/box-case-mcu.md`
- `../firmware/g2-service-handler-index.md`
- `../firmware/re-gaps-tracker.md`
- `../protocols/services.md`
- `../protocols/nus-protocol.md`
- `../devices/g2-glasses.md`
- `../devices/g2-case.md`
- `../devices/r1-ring.md`
- `../devices/r1-cradle.md`
- `../protocols/notification.md`
- `../firmware/analysis/2026-03-05-g2-nav-devinfo-descriptor-lanes.md`
- `../firmware/analysis/2026-03-05-g2-ring-relay-callchain.md`
- `../firmware/analysis/2026-03-05-g2-system-monitor-callchain.md`
- `../firmware/analysis/2026-03-05-r1-nordic-dfu-startup-chain.md`
- `../firmware/analysis/2026-03-05-r1-nordic-stage2-idle-paths.md`

## Documentation Rule

Any new reverse-engineering result that changes implementation assumptions should update at least one of:

- `identified-functionality.md`
- `inferred-functionality.md`
- `unidentified-functionality.md`
- `service-map.md`
- `memory-and-persistence-model.md`
- `update-and-recovery-model.md`
- `r1-nordic-bundle-model.md`
- `device-state-and-role-model.md`
- `input-and-gesture-model.md`
- `sensor-and-calibration-model.md`
- `lifecycle-and-orchestration-model.md`
- `device-firmware-ownership-model.md`
- `connection-and-identity-model.md`
- `feature-and-presentation-model.md`
- `audio-and-voice-model.md`
- `diagnostics-and-observability-model.md`
- `evidence-index.md`
