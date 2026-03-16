# Custom Firmware Roadmap

This is the initial execution plan for building custom firmware in `openCFW/src`.

## Principles

- Keep all implementation clean-room.
- Use only local reverse-engineering evidence already stored in this repo.
- Treat anything listed in `inferred-functionality.md` as provisional.
- Treat anything listed in `unidentified-functionality.md` as out of scope until closed.

## Phase Plan

### Phase 1: Documentation Freeze

- Keep `bundles-and-hardware.md`, `service-map.md`, `evidence-index.md`, and the identified/inferred/unidentified docs current.
- Keep transport/image-format docs and machine-readable manifests aligned with the same confidence model.
- Add a per-build assumption log under `openCFW/docs/` before code starts.

### Phase 2: Minimal Apollo Runtime Skeleton

- Establish target-specific source tree under `openCFW/src/`.
- Keep one Apollo image family for both G2-L and G2-R and leave per-eye identity/role to runtime provisioning.
- Define boot handoff assumptions from the recovered Apollo510b image and bootloader docs.
- Stand up endpoint identity, auth, and per-connection session scaffolding before feature-complete BLE behavior.
- Stub staged startup/task ownership for BLE RX/TX, display, audio, input, ring, and notification lanes.
- Stand up Apollo-side `peripherals/` scaffolding for EM9305, codec, touch, and peer-sync boundaries.
- Keep case and ring as external compatibility domains in the platform tree until their standalone runtime stories close further.
- Keep ring-side work limited to FE59, SMP or MCUmgr, and Nordic bundle validation until the standalone ring application image is recovered.

### Phase 3: Bring-Up Services

- Implement minimal control-lane framing for `0x5401/0x5402`.
- Implement the `0x80` auth family and endpoint-local keepalive or sequence context before richer service traffic.
- Implement `0x04` display wake, `0x09` device-info/dev-config bridge, `0x0D` settings, and `0xFF` system monitor first.
- Instrument every unverified field write so behavior can be compared against future captures.
- Preserve the split between settings selector writes, local-data reads, and notify-group emissions.
- Preserve proprietary status handling for battery, charging, wear, case, and peer-role state before considering generic BLE-profile shortcuts.
- Preserve touch protobuf gestures, NUS gesture bytes, and wear-gated input policy as separate layers before feature-specific shortcuts.
- Preserve ALS-driven brightness sync, `0x6402` telemetry, and calibration state as sensor-layer behavior before feature/UI shortcuts.
- Preserve compact modes, onboarding, head-up/dashboard wake, timeout/auto-close, alert/close, and idle-monitor behavior as a dedicated lifecycle plane before broader UI unification.
- Keep codec-host boot, NUS mic or audio transport, and explicit microphone-owner arbitration separate from feature-lane control.
- Keep logger and system-monitor behavior available as an early observability plane, but leave export and live-stream details instrumented until their bytes close.

### Phase 4: Display and Filesystem

- Implement enough filesystem support to host config/log/user payload paths.
- Preserve compatibility for `/firmware`, `/ota`, `/user`, and `/log` plus the known `notify_whitelist` and crash-log objects.
- Implement display wake/config/render handoff with explicit compact mode tracking (`0x04`, `0x0E`, `0x0D-01`, `0x6402` observations).
- Add notification whitelist and log namespace support as early persistence tests.
- Stand up logger control, crash-log access, and diagnostic export scaffolding before broader lab tooling.

### Phase 5: User Features

- Add menu, teleprompter, conversate, quicklist, health, and notification paths.
- Add navigation only after the `0x08` field map is tighter.
- Keep gesture decode, gesture policy, and wear gating separate before wiring gestures deeply into user features.
- Keep sensor acquisition, calibration, and brightness policy separate before wiring them deeply into user-visible features.
- Keep feature lifecycle orchestration explicit instead of collapsing onboarding, head-up wake, or timeout/close behavior into feature payload handlers.
- Keep EvenAI minimal at first: mode entry/exit and basic status plumbing only.
- Keep EvenAI, Conversate, and any future voice features behind explicit microphone-owner requests instead of direct capture access.
- Keep feature-mode transitions explicit (`0`, `6`, `11`, `16`) and instrument empty companion packets until their producer path closes.

### Phase 6: Peripheral and Relay Paths

- Keep HCI, TinyFrame, I2C, UART, and ring-relay adapters separate from protobuf service handlers.
- Add case relay after the case UART grammar is better closed.
- Add ring relay after `0x91` enum tables are lifted or live-capture correlated.
- Defer direct EM9305 patch ownership until the patch format is functionally decoded.

### Phase 7: Packaging and Recovery

- Add reproducible image packaging for test builds.
- Define a safe update/recovery story that does not depend on redistributing vendor binaries.
- Keep runtime staging, bootloader install, case relay update, and ring DFU as distinct flows in code.
- Keep bootloader interaction conservative until the Apollo update path is closed further.
- Keep the in-corpus ring bootloader and SoftDevice bundles as validation targets only; do not treat them as sufficient input for a ring runtime rewrite.

## Immediate Next Work Inside openCFW

1. Keep the platform tree centered on one Apollo image family for both G2-L and G2-R.
2. Turn `transport-and-packet-formats.md` into a packet builder/parser skeleton under `openCFW/src/transport/`.
3. Add `connectivity/` scaffolding for endpoint identity, `0x80` auth, per-connection sequence state, and keepalive routing.
4. Define a boot-image/header writer and validator for the Apollo app format from `image-formats-and-boot-path.md`.
5. Add the first real Apollo510b runtime skeleton under `openCFW/src/` using the staged startup/task model.
6. Add Apollo-side `peripherals/` host scaffolding for EM9305, codec, touch, peer-sync, case relay, and ring relay boundaries.
7. Add `storage/` scaffolding for LittleFS namespaces, OTA staging, and future FlashDB compatibility.
8. Add `update/` scaffolding for OTA staging, reboot/install coordination, and recovery-state tracking.
9. Add `state/` scaffolding for peer-role, wear, power, case, and ring-state compatibility.
10. Add `input/` scaffolding for touch-controller ingress, gesture normalization, wear gating, and ring-input adaptation.
11. Add `sensors/` scaffolding for ALS, IMU/orientation, `0x6402` telemetry, and calibration/config-sync behavior.
12. Add `lifecycle/` scaffolding for compact modes, onboarding, head-up wake policy, timeout/close handling, alert/close dialogs, and monitor traces.
13. Add `ui/` scaffolding for display wake/config/content sequencing, compact mode tracking, and user-feature protocol adapters.
14. Add `diagnostics/` scaffolding for logger, file export, system monitor, crash-artifact, and lab-debug boundaries.
15. Add `audio/` scaffolding for GX8002B boot and runtime control, NUS mic or audio streaming, and explicit microphone-owner arbitration.
16. Add capture-comparison hooks for `0x01-01`, `0x0D-01`, `0x09`, `0x0D`, `0x0F`, `0x10`, `0x20`, `0x21`, `0x22`, `0x80`, `0x81`, `0x6402`, `0xFF`, NUS audio sessions, and codec-host runtime traffic.
17. Add an instrumented settings lane model that distinguishes root `case3/case4/case5`.
18. Keep the bundle, device-firmware, service, format, connectivity, runtime, interface, memory, update, state, input, sensor, lifecycle, feature, audio, and diagnostics manifests synchronized with every new RE closure.

## Source Documents

- `../firmware/s200-firmware-ota.md`
- `../firmware/s200-bootloader.md`
- `../firmware/g2-service-handler-index.md`
- `../firmware/re-gaps-tracker.md`
