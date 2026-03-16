# Settings Selector Wire Schema (Descriptor-Recovered)

## Scope
- Firmware-only protobuf schema recovery for settings selector dispatch (`0x0D` service path).
- Descriptor-table interpretation from `ota_s200_firmware_ota.bin` (v2.0.7.16).
- Selector payload field map used to harden simulator parsing.

## Firmware Evidence (Binary, v2.0.7.16)
- Settings parser/dispatch path:
  - `APP_PbRxSettingFrameDataProcess` lane at `0x4644D0`
  - parser call `0x4AA30C`
  - dispatch hub `0x464548`
  - selector load `ldrh [r4,#0x0C]` at `0x4646DA`
  - common parse/notify lane `0x4AACB4` loads descriptor literal `0x727E44` and routes decode success through `0x46F6EA`
- Descriptor engine (protobuf iterator/decode):
  - iterator init/advance: `0x4ECBBE`, `0x4ECD5A`, `0x4ECDF4`
  - decode entry used by settings parser: `0x4A4490 -> 0x4A4208`
- Root settings descriptor:
  - descriptor object at `0x727E44`
  - `field_info = 0x6E49C4`, `submsg_info = 0x727E2C`, `field_count = 7`
  - root oneof submessage table (`0x727E2C`):
    - case `3` -> `0x727F1C`
    - case `4` -> `0x727F34`
    - case `5` -> `0x727F4C`
    - case `6` -> `0x727FDC`
    - case `7` -> `0x727FF4`
- Selector message descriptor:
  - descriptor object at `0x727F1C`
  - `field_info = 0x6A8074`, `submsg_info = 0x6ED668`, `field_count = 11`
  - `0x6ED668` points to selector submessage descriptors `1..11`:
    - `1:0x727E5C`, `2:0x727E74`, `3:0x727E8C`, `4:0x727EA4`, `5:0x727EBC`, `6:0x727ED4`, `7:0x727EEC`, `8:0x727F04`, `9:0x727F7C`, `10:0x727FAC`, `11:0x727FC4`

## Top-Level Envelope (`0x727E44`)
- Tag `1`: scalar (offset `+0x00`, 1-byte storage class in descriptor).
- Tag `2`: scalar (offset `+0x04`).
- Tags `3..7`: oneof-style message fields sharing data offset `+0x0C` and selector/case offset `+0x08`.
- Descriptor-backed case map from `submsg_info=0x727E2C`:
  - case `3` -> `0x727F1C` (selector oneof `1..11`)
  - case `4` -> `0x727F34` (local-data payload, 19 fields)
  - case `5` -> `0x727F4C` (notify group oneof with subcases `1/2`)
  - case `6` -> `0x727FDC` (2-field scalar payload)
  - case `7` -> `0x727FF4` (2-field scalar payload)
- Runtime routing in app receive path (`0x464548`):
  - case `3` -> `0x46468E` (selector dispatch) -> `0x4AA906`
  - case `4` -> `0x4AAAAE` (`setting_respond_with_local_data`)
  - cases `5..7` are not dispatched from this app-receive function.

### Case 4 Payload (`0x727F34`)
- Field/tag layout (decoded from `field_info=0x6AB07C`):
  - scalar tags: `1..4`, `7..19`
  - bytes/string tags: `5` and `6` (12-byte class entries in descriptor)
  - data offsets: `0x00,0x04,0x08,0x0C,0x10,0x1C,0x28..0x58`
- Runtime field writes from `0x4AA5EE` (`setting_build_full_status_package`) mapped to tags:
  - tag `1` (`+0x00`) <- request-shadow byte (`r4+0x0C` from prior parsed case4 state, else `0`)
  - tag `2` (`+0x04`) <- settings `+0x01` (`brightness_level`)
  - tag `3` (`+0x08`) <- settings `+0x08` (`y_coordinate_level`)
  - tag `4` (`+0x0C`) <- settings `+0x09` (`x_coordinate_level`)
  - tag `5` (`+0x10`) <- 11-byte copy from static `2.0.7.16` blob
  - tag `6` (`+0x1C`) <- 11-byte copy from static `2.0.7.16` blob
  - tag `7` (`+0x28`) <- settings `+0x0A` (`head_up_switch`)
  - tag `8` (`+0x2C`) <- settings `+0x0C` (`head_up_angle`)
  - tag `9` (`+0x30`) <- no explicit write in `0x4AA5EE` (zero-initialized)
  - tag `10` (`+0x34`) <- settings `+0x14` (`wear_detection_switch`)
  - tag `11` (`+0x38`) <- settings `+0x20` (event-driven dashboard callback/session lane; exact enum mapping unresolved)
  - tag `12` (`+0x3C`) <- settings `+0x24` (inferred battery-percent lane)
  - tag `13` (`+0x40`) <- settings `+0x28` (inferred charge-state/trend lane; signed source)
  - tag `14` (`+0x44`) <- settings `+0x15` (`silent_mode_switch`)
  - tag `15` (`+0x48`) <- settings `+0x16` (`left_brightness_calibration_level`)
  - tag `16` (`+0x4C`) <- settings `+0x17` (`right_brightness_calibration_level`)
  - tag `17` (`+0x50`) <- settings `+0x2C` (head-up calibration UI boolean lane)
  - tag `18` (`+0x54`) <- settings `+0x02` (`auto_brightness_enabled`)
  - tag `19` (`+0x58`) <- `0x4A4B72()` return (`unread_message_count` log string at `0x007210E0`)
- Additional write-path evidence (raw-disasm base `0x200000`):
  - `0x22F20C` writes `[settings+0x24]`/`[settings+0x28]` from helpers `0x27D13C`/`0x27D142` and then calls notify path `0x272F04`.
  - helper `0x27D13C` reads `[0x2007206C + 0x08]` and is bucketed by threshold ranges in `0x2793A0..0x279416`, `0x329DDA..0x329E50`, `0x32AEB4..0x32AF2A`, matching battery-percent UI buckets.
  - helper `0x27D142` reads signed byte `[0x2007206C + 0x0C]`.
  - `settings+0x20` toggles at `0x30B1FA (set)` / `0x30B4DC (clear)`.
  - `settings+0x2C` toggles at `0x22D294 (set)` / `0x22CCCC,0x22D2A8 (clear)` in `setting_handle_head_up_setting` (`0x22D228`), with related calibration UI flag helper `0x22D2D1 -> *(uint8_t*)0x20073004`.
- Correlated log format strings used in `0x4AA5EE`:
  - `auto_brightness_switch:%d, auto_brightness_level:%d, y_coordinate_level:%d, x_coordinate_level:%d`
  - `head_up_switch:%d, head_up_angle:%d, head_up_angle_calibration:%d`
  - `unread_message_count: %d`

### Case 5 Payload (`0x727F4C`)
- Descriptor fields:
  - two-entry oneof-style notify group (`subcase 1/2`) under root tag `5`.
  - wrapper init pattern (`0x4AAF94`, `0x4AB00C`) sets:
    - root case selector: `+0x08 = 5`
    - case5 subcase selector: `+0x0C = 1|2`
    - case5 scalar status value: `+0x10 = status`
  - interpreted subcases:
    - subcase `1`: `setting_notify_recalibration_status_to_app` (`0x4AAF94`)
    - subcase `2`: `notify_silent_mode_to_app` (`0x4AB00C`)
- Both wrappers build root envelope with top-level oneof case `5` then serialize via `0x4AAC94` (`setting_notify_common`).
- Recovered callsites (v2.0.7.16):
  - recalibration notifier (`0x4AAF94`) called from `0x464CD2` and `0x465292`
  - silent-mode notifier (`0x4AB00C`) called from `0x466834`, `0x466C66`, `0x466DC4`
- Selector-trigger evidence:
  - selector4 subtype `3` calibration flow (`0x464AEC`) raises gate `0x2D320` and on rising edge calls `0x4AAF94(0)`.
  - selector6/silent-mode flow (`0x464D0E -> 0x46651C`) transitions into `0x4AB00C(status)`.

### Case 6/7 Payloads (`0x727FDC`, `0x727FF4`)
- Both descriptors are 2-field scalar schemas:
  - tag `1` offset `+0x00`
  - tag `2` offset `+0x04`
- No producer/consumer path for case `6/7` was recovered yet in current v2.0.7.16 callgraph sweep.

## Selector Payload Schema (`selector=1..11`)

| Selector | Descriptor | Schema (wire tags) | Runtime layout effect |
|---|---|---|---|
| `1` | `0x727E5C` | oneof tags `1..4` (each scalar) | subtype/case at payload `+0x00`, value at `+0x04` |
| `2` | `0x727E74` | tag `1` scalar | scalar payload |
| `3` | `0x727E8C` | tag `1` scalar | scalar payload |
| `4` | `0x727EA4` | oneof tags `1..4` (each scalar) | subtype/case at payload `+0x00`, value at `+0x04` |
| `5` | `0x727EBC` | tag `1` scalar | scalar payload |
| `6` | `0x727ED4` | tag `1` scalar | scalar payload |
| `7` | `0x727EEC` | tag `1` scalar | scalar payload |
| `8` | `0x727F04` | tag `1` scalar | scalar payload |
| `9` | `0x727F7C` | tags `1..5` scalar | offsets `+0x00/+0x04/+0x08/+0x0C/+0x10` |
| `10` | `0x727FAC` | tag `1` repeated submessage | count stored at payload `+0x00`, entries at `+0x04` stride `0x0C` |
| `11` | `0x727FC4` | tag `1` scalar | scalar payload |

### Selector 9 field-to-runtime mapping
- Descriptor field offsets map to runtime writes seen in `0x464DD6`:
  - tag `1` (`+0x00`) -> context `+0x01`
  - tag `2` (`+0x04`) -> context `+0x03`
  - tag `3` (`+0x08`) -> context word `+0x14`
  - tag `4` (`+0x0C`) -> context `+0x02`
  - tag `5` (`+0x10`) -> context `+0x04`

### Selector 10 item schema
- Item descriptor at `0x727F94` (`field_info=0x735440`, `field_count=3`):
  - tag `1` -> item offset `+0x00` (`bank`)
  - tag `2` -> item offset `+0x04` (`index`)
  - tag `3` -> item offset `+0x08` (`value`, 1-byte storage class)
- Runtime loop at `0x464EC8`:
  - reads `count=ldrh [payload+0x00]`
  - iterates `count` entries of `0x0C` bytes
  - calls `0x4641EE(bank,index,value)` per entry

## Simulator Parity Impact
- Selector decoding now unwraps firmware selector envelope from root oneof case `3` only.
- Scalar selectors (`2/3/5/6/8/11`) now prefer canonical nested payload `field1`.
- Selectors `1` and `4` now parse canonical oneof subtype (`tag 1..4`) from selector payload blob.
- Selector `9` now prefers canonical tag map (`1..5`) and limits ordered-varint fallback to non-firmware helper mode.
- Selector `10` now prefers canonical repeated `field1` item messages (`tag1/2/3`) and limits order-only fallback to helper mode.
- Root oneof case `4` now has a dedicated simulator response lane (local-data snapshot envelope) and no longer falls into legacy `cmdId` fallback.
- Root oneof case `5` now decodes inbound notify payload (`subcase/status`) and applies shadow state updates without entering legacy `cmdId` fallback.
- Root oneof cases `6/7` are blocked from legacy `cmdId` fallback and now emit structured capture telemetry (first field/wire/scalar/blob/seen-count) for continuous RE.
- Simulator now emits case5 notify-group packets on `0x0D-01` for:
  - recalibration notify (subcase `1`, status `0/1`) on selector4 calibration rising/falling transitions
  - silent-mode notify (subcase `2`, status=`value`) on selector6 value transitions
- Selector4 calibration gate transitions now also emit paired case4 local-data status notify packets (`0x4AAF04` parity) after case5/subcase1.
- Local-data case4 `tag12/tag13` now refresh from simulator power-lane state before encode (battery + charge-state inference), matching firmware write timing for settings `+0x24/+0x28`.
- Local-data case4 `tag17` now refreshes from simulator calibration-UI shadow state.

Status-lane deep dive and trace details:
- [settings-local-data-status.md](settings-local-data-status.md)
- [settings-headup-calibration.md](settings-headup-calibration.md)
- [settings-envelope-parser.md](settings-envelope-parser.md)

## Next Actionable Improvements
1. Resolve remaining case4 semantic label gaps for tag `11` (`settings +0x20`) by recovering upstream dispatcher/event enum names behind `0x30B1A0`.
2. Convert root case6/7 capture telemetry into concrete producer/consumer call paths and app-visible packet envelopes.
3. Decode canonical charge-state enum/source semantics for tag `13` (`settings+0x28`) beyond current signed-lane inference.
4. Add replay fixtures for root oneof routing (`case3 selector`, `case4 local-data`, `case5 notify-group`) and assert simulator fallback gating + async notify emission behavior.
