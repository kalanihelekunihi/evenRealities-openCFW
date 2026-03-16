# Settings Runtime Context (Selector State Bytes)

## Scope
- Firmware-only reconstruction of settings selector runtime state written by `APP_PbRxSettingFrameDataProcess`
- Context-byte/runtime write map used by selector branches (`1..11`) in the `0x0D` settings dispatcher
- Simulator parity model for stateful selector writes required by iOS automation

## Firmware Evidence (Binary, v2.0.7.16 base)
- Settings dispatch hub:
  - parser handoff `0x4AA30C -> 0x464548`
  - selector load at `0x4646DA` (`ldrh [r4,#0x0C]`)
  - selector jump table at `0x4646DA`
- Selector write/update paths recovered from disassembly:
  - selector `1` (`0x4647B0`):
    - sub-dispatch on `ldrh [r4]` (`1..4`)
    - calls `0x467A10` / `0x467A80`
    - writes context bytes at `+0x16` / `+0x17`
    - shared finalize call `0x467A40`
  - selector `2` (`0x4649DC`): writes one byte to context `+0x08`
  - selector `3` (`0x464A64`): writes one byte to context `+0x09`
  - selector `4` (`0x464AEC`):
    - reads sub-type from `[r4]`, value from `[r4+4]`
    - subtype `1` writes context byte `+0x0A` (`head_up_switch`)
    - subtype `2` writes context word `+0x0C` (`head_up_angle`)
    - subtype `3` mutates one-byte global gate at literal target `0x2D320` (`head_up_angle_calibration`)
      - rising-edge branch calls `0x4AAF94(0)` (recalibration notify wrapper)
    - side-effect call chain includes `0x462996`, `0x46288E`, `0x4AAF94`
  - selector `6` (`0x464D0E -> 0x46651C(u8)`):
    - updates context `+0x15`
    - emits event-like call through `0x462C74` with constant `0x10A`
    - conditional paths call `0x462996` with zero args
  - selector `8` (`0x464D72`):
    - compares input to `1`
    - conditionally calls `0x462A0A` when guard (`0x45E6A8`) passes
  - selector `9` (`0x464DD6`):
    - treats payload as 5-field struct at `r4+0x10`
    - writes context `+0x01`, `+0x02`, `+0x03`, `+0x04`, and word `+0x14`
    - calls `0x463F0E` after update
  - selector `10` (`0x464EC8`):
    - reads `count=ldrh [r4]`
    - iterates entries (stride `0x0C`) and calls `0x4641EE(bank,index,value)` for each record
    - calls `0x463F0E` after loop
  - selector `11` (`0x465078`):
    - writes context byte `+0x0B`
    - calls `0x463F0E` after update

## Service Settings Struct Correlation (`0x46725A`)
- `SVC_Settings_DumpSettingConfig` (`0x46725A`) logs per-offset values from the settings struct returned by `0x467254`.
- Recovered offset-to-label map from direct disassembly + literal-string decode:
  - `+0x00` -> `record_version: %d` (`0x00732E80`)
  - `+0x01` -> `brightness_level: %d` (`0x0072C0BC`)
  - `+0x02` -> `auto_brightness_enabled: %d` (`0x007229D0`)
  - `+0x08` -> `y_coordinate_level: %d` (`0x0072C0D4`)
  - `+0x09` -> `x_coordinate_level: %d` (`0x0072C0EC`)
  - `+0x0A` -> `head_up_switch: %d` (`0x00732E94`)
  - `+0x0C` -> `head_up_angle: %d` (`0x00732EA8`)
  - `+0x10` -> `head_up_angle_calibration: %d` (`0x00718058`)
  - `+0x14` -> `wear_detection_switch: %d` (`0x007229EC`)
  - `+0x15` -> `silent_mode_switch: %d` (`0x0072C104`)
  - `+0x16` -> `left_brightness_calibration_level: %d` (`0x00703630`)
  - `+0x17` -> `right_brightness_calibration_level: %d` (`0x00703658`)
  - `+0x18` -> `record_check: 0x%04x` (`0x0072C11C`)

This confirms selector-context semantic labels (coordinate/head-up/silent/wear/calibration lanes) and anchors local-data case4 field interpretations in descriptor offsets.

## Local-Data Status Offsets Beyond Dump Labels
- Additional write-path recovery (raw-disasm base `0x200000`) identifies runtime updates for offsets not labeled by `SVC_Settings_DumpSettingConfig`:
  - `+0x24` updated by `0x22F20C -> 0x27D13C` (inferred battery-percent lane from threshold-bucket use sites).
  - `+0x28` updated by `0x22F20C -> 0x27D142` (signed charge-state/trend lane).
  - `+0x20` toggled `1/0` by event handler `0x30B1A0` on event codes `2/5`.
  - `+0x2C` toggled `1/0` by `setting_handle_head_up_setting` (`0x22D228`) on command values `3/5` (with explicit clear path at `0x22CCCC`), correlated with calibration UI flag helper `0x22D2D1 -> *(uint8_t*)0x20073004`.
- These offsets map directly into root case4 local-data tags `11/12/13/17`.

## Simulator Implementation (`g2-mock-firmware/src/ble_core.cpp`)
- Added selector runtime shadow state mirroring firmware context bytes:
  - `ctx+0x01`, `ctx+0x02`, `ctx+0x03`, `ctx+0x04`, `ctx+0x08`, `ctx+0x09`, `ctx+0x0A`, `ctx+0x0B`, `ctx+0x0C`, `ctx+0x14`, `ctx+0x15`, `ctx+0x16`, `ctx+0x17`
  - global gate shadow for firmware literal target `0x2D320`
  - selector10 two-bank (`bank0`/`bank1`) 3-slot table shadow matching `0x4641EE` index bound (`index < 3`)
- Implemented selector lanes with conservative parsing and safe fallback:
  - selector `1`: existing wear snapshot response retained; sub-type parse updates `ctx+0x16/+0x17`
  - selector `2`: scalar write to `ctx+0x08`
  - selector `3`: scalar write to `ctx+0x09`
  - selector `4`: subtype `1` writes `ctx+0x0A`, subtype `2` writes `ctx+0x0C`, subtype `3` updates gate shadow (`0x2D320`) and emits case5/subcase1 notify on rising edge
  - selector `5`: wear-enable path (existing)
  - selector `6`: scalar write to `ctx+0x15` with `0x10A` parity log and case5/subcase2 notify emission on value change
  - selector `7`: explicit no-op
  - selector `8`: conditional gate parity log for guarded `0x462A0A` path
  - selector `9`: structured context update (`ctx+0x01/+0x02/+0x03/+0x04/+0x14`)
  - selector `10`: repeated-record update into selector10 bank shadow + count/blob metadata
  - selector `11`: scalar update for `ctx+0x0B`
- Parse-confidence guard:
  - firmware root-envelope packets no longer fall through to legacy `cmdId` lane for cases outside app-dispatch (`5..7`)
  - selector parse failures only use cmdId fallback when no firmware root envelope is present

## Schema Linkage
- Selector payload protobuf schema for firmware oneof case `3` is now descriptor-backed:
  - root descriptor `0x727E44`
  - selector descriptor `0x727F1C`
  - selector submessage table `0x6ED668`
- Full selector field/tag map is documented in [settings-selector-schema.md](settings-selector-schema.md).
- Case4 status-lane deep dive is documented in [settings-local-data-status.md](settings-local-data-status.md).
- Head-up calibration flow deep dive is documented in [settings-headup-calibration.md](settings-headup-calibration.md).

## Next Actionable Improvements
1. Decode unresolved root-descriptor oneof cases `6/7` (`0x727E44`) and map their runtime state side effects.
2. Trace notifier/event fan-out from `0x463F0E`, `0x462986`, and `0x462A0A` into `0x0D-00/01` app-visible responses.
3. Add deterministic replay fixtures for wrapped selector packets (`field3 -> selector fieldN`) and root case4 local-data packets (`field4`) with context-shadow assertions.
4. Correlate selector-runtime state with observed notify traffic on `0x0D-00/01` to promote parity logs into protocol-accurate async responses.
