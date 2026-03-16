# Sensor and Calibration Model

This document is the clean-room model for ALS, IMU or heading surfaces, display sensor telemetry, and calibration or config-sync behavior in the G2 runtime.

## Sensor Matrix

| Domain | State | Main Evidence | Identified Constraints | Remaining Gaps |
|---|---|---|---|---|
| Sensor inventory and Apollo-visible ownership | Identified with bounded unknowns | device docs, firmware RE, topology docs | ALS and IMU subsystems are confirmed and Apollo-visible; compass or heading behavior exists in the product stack | exact compass IC and final producer split |
| ALS-driven brightness sync | Partial but executable | display-config module, brightness docs, firmware RE | direct JBD brightness writes are deprecated; ALS polling, conversion, and inter-eye sync are real | exact lux-to-level conversion, smoothing, and final range mapping |
| Display sensor telemetry on `0x6402` | Partial | device docs, transport docs, display notes | `0x6402` is a mixed hardware-facing lane and the reliable display-active signal | full descrambling, field map, and trailer semantics |
| IMU, heading, and orientation surfaces | Partial | firmware RE, device docs, navigation-facing evidence | IMU presence, head-angle observations, and heading fetch behavior are real | exact wire/service ownership and runtime packet schema |
| Head-up and zero-position calibration state | Partial but executable | settings head-up calibration notes, settings model, firmware RE | calibration UI state is app-visible and gates other behavior | exact lifecycle enums and relation between `tag17` and `0x20073004` |
| ModuleConfigure and SyncInfo calibration plane | Partial | settings-sync-module-config notes, firmware module map | `0x20` owns brightness calibration, module flags, language, and dashboard auto-close-adjacent config | exact nested field schema and object layout |

## Identified Sensor Contracts

### Sensors Are Apollo-Visible Runtime Subsystems

- The G2 runtime has explicit ALS and IMU or sensor module evidence rather than treating sensors as hidden display internals.
- Sensor activity is visible across runtime modules such as `sensor_als`, `sensor_imu`, and a broader sensor hub.
- The product also has heading or compass behavior and calibration UX, even though the exact magnetometer IC is still unresolved.

### Auto-Brightness Is a Sensor Pipeline, Not a Direct Display Write

- Current evidence closes this architectural shift:
  - direct `JBD_CHANGE_BRIGHTNESS` is deprecated
  - ALS polling reads raw light values
  - firmware converts those values into brightness levels
  - one eye relays the brightness level to the peer through `ALSSyncHandler`
- Manual brightness, auto-brightness enable, and per-eye brightness calibration still exist, but they feed a sensor-to-display policy path rather than a raw one-shot display write.

### `0x6402` Is a Mixed Hardware Feedback Lane

- `0x6402` is not just a normal protobuf response channel.
- It carries hardware-adjacent display or sensor telemetry and is the most reliable indicator that the physical display is active.
- Current local evidence is strong enough to preserve it as a dedicated mixed-format lane in `openCFW`.

### Calibration UI State Is Real and App-Visible

- Settings selector `4` and local-data `case4 tag17` close a real calibration or head-up UI lane.
- `settings+0x2C` feeds the app-visible calibration state lane.
- A related calibration UI boolean at `0x20073004` is used by other services to gate outgoing behavior.
- Clean-room implication: calibration should remain an explicit runtime state machine, not just a single settings bit.

### `0x20` Is a Real Sensor/Calibration Bridge

- `ModuleConfigure` and `SyncInfo` are not placeholder services.
- Current evidence closes implementation-relevant behavior for:
  - brightness calibration
  - module-list or capability payloads
  - system language
  - dashboard auto-close style config
- Clean-room implication: `0x20` should remain separate from generic settings writes because it carries structured config or calibration objects.

## Inferred Sensor Behavior

### Brightness Policy Likely Has a Shared Owner

- Manual brightness, auto-brightness enable, per-eye calibration, ALS polling, and peer-eye sync likely converge on one shared brightness policy owner.
- The exact merge rules are still incomplete, so `openCFW` should keep these inputs explicit and instrumented.

### Orientation and Calibration Are Broader Than One Setting Selector

- Head-up angle, zero-position recalibration, heading fetches, and calibration UI gating likely belong to a broader orientation subsystem rather than isolated one-off settings writes.
- That subsystem boundary is real enough to preserve in the architecture, but not yet closed enough to freeze exact packet ownership.

### `0x6402` Probably Mixes Display and Sensor State

- Head-angle, render-state, and display telemetry likely coexist on the `0x6402` lane.
- The lane therefore should remain modeled as mixed hardware telemetry rather than as a pure display ACK stream.

### ModuleConfigure Likely Carries Structured Calibration Objects

- The current `0x20` evidence strongly suggests nested structured payloads rather than flat scalar writes.
- Brightness calibration is the clearest example, but other config-sync objects likely use the same family.

## Unidentified Areas

- Exact ALS lux-to-brightness conversion curve, smoothing rules, and normalization range.
- Exact `0x6402` descrambling, field map, and head-angle trailer semantics.
- Exact IMU or heading packet ownership and the authoritative runtime path for compass-facing data.
- Exact head-up calibration command enum, lifecycle events, and relationship between `settings+0x2C` and `0x20073004`.
- Exact `ModuleConfigure` and `SyncInfo` nested field schema for calibration and structured config payloads.

## Clean-Room Rules

- Keep sensor acquisition, calibration state, and feature presentation as separate layers.
- Treat `0x6402` as a mixed hardware telemetry lane from the start.
- Keep ALS-driven brightness policy separate from direct display writes.
- Keep calibration UI state explicit in code instead of inferring it from feature transitions alone.
- Treat `0x20` as a structured config/calibration bridge rather than flattening it into generic scalar settings.

## Source Documents

- `../features/brightness.md`
- `../firmware/modules/display-config.md`
- `../firmware/modules/settings-sync-module-config.md`
- `../firmware/modules/settings-headup-calibration.md`
- `../firmware/firmware-reverse-engineering.md`
- `../firmware/g2-firmware-modules.md`
- `../firmware/firmware-communication-topology.md`
- `../devices/g2-glasses.md`
