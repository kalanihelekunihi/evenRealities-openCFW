# Settings Dispatch Core (0x0D)

## Scope
- Service envelope: `0x0D` settings/config path (`0x0D-00`, `0x0D-20`)
- Reverse-engineered dispatch internals in firmware parser/handler chain
- Simulator parity strategy for selector dispatch vs legacy `cmdId` payloads

## Firmware Evidence (Binary, firmware-only)
- Settings frame process entry validates input and routes into parser:
  - `APP_PbRxSettingFrameDataProcess` region at `0x4644D0` (v2.0.7.16 image rebased to `0x438000`)
- Parser call and handoff:
  - parse function at `0x4AA30C`
  - dispatch hub at `0x464548`
- Common notify/parse lane used by settings wrappers:
  - `0x4AACB4` loads root descriptor literal `0x727E44` (`[0x4AB134]`)
  - decode destination global `0x20070908`
  - global magic/random counter at `0x20072948` is incremented before parse/dispatch
  - success path routes through `0x46F6EA(r0=1, r1=9, r2=0x2006E804, r3=[sp+0x18])`
  - BL-target sweep shows 3 callers in v2.0.7.16: `0x4AAFA0`, `0x4AB016`, `0x4AB098` (`0x4AB098` resolved as internal callsite inside wrapper `0x4AB02C`)
  - wrapper evidence artifacts:
    - `captures/firmware/analysis/2026-03-05-settings-notify-wrapper-callgraph-resolution.*`
    - `captures/firmware/analysis/2026-03-05-settings-device-status-wrapper-case4-map.*`
- Root oneof receive dispatch in `0x464548`:
  - case `3` -> selector dispatcher `0x46468E` then `0x4AA906`
  - case `4` -> local-data responder `0x4AAAAE`
  - cases `5..7` are not dispatched from this app-receive path
- Notify-side root case `5` producers:
  - `0x4AAF94` (`setting_notify_recalibration_status_to_app`) builds case5/subcase1
    - observed callers: `0x464CD2`, `0x465292`
  - `0x4AB00C` (`notify_silent_mode_to_app`) builds case5/subcase2
    - observed callers: `0x466834`, `0x466C66`, `0x466DC4`
  - both serialize through `0x4AAC94` (`setting_notify_common`)
- Selector read:
  - `ldrh r0, [r4, #0x0C]` at `0x4646DA` (selector field in parsed struct)
- Selector wire schema root recovered from descriptor tables:
  - root descriptor: `0x727E44`
  - selector oneof descriptor: `0x727F1C`
  - selector submessage pointer table: `0x6ED668` (`1..11`)
- Dispatch ladder (`0x4646DA..0x46475C`) routes selector `1..11`:
  - `1 -> 0x4647B0` (arg `r4 + 0x10`)
  - `2 -> 0x4649DC` (arg `[r4 + 0x10]`)
  - `3 -> 0x464A64` (arg `[r4 + 0x10]`)
  - `4 -> 0x464AEC` (arg `r4 + 0x10`)
  - `5 -> 0x464D04` (arg `[r4 + 0x10]`)
  - `6 -> 0x464D0E` (arg `[r4 + 0x10]`)
  - `7 -> no-op branch`
  - `8 -> 0x464D72` (arg `[r4 + 0x10]`)
  - `9 -> 0x464DD6` (arg `r4 + 0x10`)
  - `10 -> 0x464EC8` (arg `r4 + 0x10`)
  - `11 -> 0x465078` (arg `r4 + 0x10`)
- Confirmed wear linkage:
  - selector `5` stub (`0x464D04`) does `uxtb` and calls `0x4AB196` (`WearDetect_SetEnable`)
- Recovered branch internals:
  - selector `1` (`0x4647B0`) has sub-dispatch on `ldrh [r4]` (`1..4`), calls `0x467A10`/`0x467A80`, writes context `+0x16/+0x17`, then calls `0x467A40`
  - selector `2` (`0x4649DC`) writes context byte `+0x08`
  - selector `3` (`0x464A64`) writes context byte `+0x09`
  - selector `4` (`0x464AEC`) uses `(subtype=[r4], value=[r4+4])`:
    - subtype `1` (`head_up_switch`) writes context byte `+0x0A`
    - subtype `2` (`head_up_angle`) writes context word `+0x0C`
    - subtype `3` (`head_up_angle_calibration`) mutates global byte at literal `0x2D320`
      - rising-edge path (`value=1` and previous gate `0`) calls `0x4AAF94(0)` (`setting_notify_recalibration_status_to_app`)
      - non-rising paths still branch through `0x462996` / `0x46288E` side-effect lanes
  - selector `6` (`0x464D0E -> 0x46651C`) updates context `+0x15`, emits `0x462C74` with constant `0x10A`, and conditionally calls `0x462996`
  - selector `8` (`0x464D72`) checks input `==1` and conditionally calls `0x462A0A` through guard `0x45E6A8`
  - selector `9` (`0x464DD6`) writes context bytes `+0x01/+0x02/+0x03/+0x04`, writes word `+0x14`, then calls `0x463F0E`
  - selector `10` (`0x464EC8`) reads `count=ldrh [r4]`, loops records (`stride=0x0C`) and calls `0x4641EE(bank,index,value)` per item, then calls `0x463F0E`
  - selector `11` (`0x465078`) writes context byte `+0x0B` then calls `0x463F0E`
- Descriptor-level selector schema details are documented in [settings-selector-schema.md](settings-selector-schema.md).
- Detailed runtime context mapping is documented in [settings-runtime-context.md](settings-runtime-context.md).

## Simulator Implementation (`g2-mock-firmware/src/ble_core.cpp`)
- Added selector-dispatch lane in `handle_settings_service()`:
  - selector decode supports:
    - explicit field-12 selector (`f12=1..11`) for helper compatibility
    - firmware oneof selector envelope (top-level field `3` wrap + inner selector field `1..11`)
- Added root oneof routing guard:
  - root case `4` emits local-data snapshot response envelope
  - root case `5` now decodes `subcase/status` and applies shadow state updates (calibration/silent-mode lanes) without entering legacy `cmdId` fallback
  - root cases `6/7` now skip legacy `cmdId` fallback and record first-field capture telemetry (field/wire/scalar/blob/seen-count) for iterative RE
- Local-data (root case `4`) parity now follows descriptor offsets from `0x727F34`:
  - full tag coverage `1..19`
  - tag `6` mirrors tag `5` with firmware version blob (`2.0.7.16` source pattern in `0x4AA5EE`)
  - tags `12/13` now map to inferred power lanes (`settings+0x24` battery-percent, `settings+0x28` charge-state/trend) and refresh before case4 encode
  - tag `18` maps to auto-brightness enable state
  - tag `19` maps to unread-message-count lane (`0x4A4B72` / `unread_message_count: %d`)
- Implemented selector behavior currently confirmed by firmware:
  - selector `1`: query/basic snapshot path (`wear_detection_enabled`, `wear_status`) plus sub-type tracking to shadow context `+0x16/+0x17`
  - selector `2`: scalar write path to shadow context `+0x08`
  - selector `3`: scalar write path to shadow context `+0x09`
  - selector `4`: `(subtype,value)` write path with calibration-gate parity (`subtype=3 -> gate@0x2D320`), case4 `tag17` calibration-UI lane updates, and paired notify emission on gate transitions: case5/subcase1 (`status=0/1`) + case4 local-data status notify (`0x4AAF04` parity)
  - selector `5`: wear enable write (`WearDetect_SetEnable` parity path)
  - selector `6`: scalar write path to shadow context `+0x15` with `0x10A` parity logging and case5/subcase2 notify emission on value change
  - selector `7`: no-op (no response payload)
  - selector `8`: conditional gate parity path for guarded call pattern (`0x45E6A8 -> 0x462A0A`)
  - selector `9`: structured context update path for `+0x01/+0x02/+0x03/+0x04/+0x14` (no payload response)
  - selector `10`: record-list apply path with two 3-slot banks (mirrors `0x4641EE` constraints) and count/blob metadata shadow
  - selector `11`: single-byte context update to `+0x0B` (no payload response)
- Preserved legacy `cmdId` lane for existing app/capture compatibility:
  - packets using `f1=cmdId` continue to follow current simulator command mapping
  - selector payloads that fail confidence checks fall back to legacy command handling
- Added simulator introspection command:
  - serial console `settings status` prints selector context shadows, case4 status lanes, and root case6/7 capture counters to support iterative firmware-wave validation.
  - compact notify shadow telemetry is included in the same output.

## Compatibility Notes
- Current captures in this repo heavily use compact legacy payloads (`08xx`).
- Selector schema for firmware oneof case `3` is now descriptor-backed (root `0x727E44`, selector `0x727F1C`, selector submessages `1..11`).
- Root case `4` now has a dedicated simulator response lane (`respond_with_local_data` style envelope), while selectors remain bound to root case `3`.
- Selectors `1..11` now have firmware-backed state transition stubs; response payload semantics are intentionally conservative until field semantics are fully recovered.
- Case5 notify-group wrappers are now emitted from selector-backed runtime transitions (`recalibration` + `silent mode`) on `0x0D-01`.
- Selector4 subtype3 gate transitions now also emit a paired case4 local-data status notify (`0x4AAF04` parity) on `0x0D-01` after case5/subcase1.
- Capture-backed compact settings-status events are modeled on `0x0D-01` through shared `config_state` transitions (module/mode lane), not selector-branch direct emits.
  - envelope shape: `f1=1`, `f3={f1=event[,f2=status]}`
  - direction-aware capture correlation links events to module traffic (`0x06/0x07/0x0B`) with empty companion packet (`event=0`) still unresolved.
- Inbound root case5 payloads are now decoded/applied in simulator (`subcase1/2`) to mirror parser envelope flow before route fallback gating.
- Case4 status-lane evidence is tracked in:
  - [settings-local-data-status.md](settings-local-data-status.md) (`tag11/12/13/17`)
  - [settings-headup-calibration.md](settings-headup-calibration.md) (`tag17` calibration flow)
- Root envelope parser details are tracked in:
  - [settings-envelope-parser.md](settings-envelope-parser.md)
- Compact notify lane details are tracked in:
  - [settings-compact-notify.md](settings-compact-notify.md)
- Simulator-only wear shim (`cmdId=250`) remains available for deterministic automation.

## Next Actionable Improvements
1. Convert captured root case6/7 first-field telemetry into concrete producer/consumer path mappings and packet semantics.
2. Resolve exact on-wire emission conditions for device-status wrapper `0x4AAF04` and confirm whether compact-empty packets (`08011a00`) originate from this path or separate compact-event producer lanes.
3. Resolve remaining case4 field semantics (`tag11`, plus exact meaning of request-echo `tag1`) beyond current local-data snapshot parity.
4. Trace post-update notifier/event side effects from `0x463F0E`, `0x462986`, and `0x462A0A` into app-visible packet envelopes.
5. Add replay fixtures validating root-case routing (`case3 selector`, `case4 local-data`, `case5 notify-group`, `case6/7 capture`) and wrapped selector payloads.
