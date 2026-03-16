# Settings Local-Data Status Lanes (Case4 Tags 11/12/13/17)

## Scope
- Firmware-only analysis of root case4 local-data status fields sourced from service-settings offsets:
  - `tag11 <- settings+0x20`
  - `tag12 <- settings+0x24`
  - `tag13 <- settings+0x28`
  - `tag17 <- settings+0x2C`
- Evidence target: `ota_s200_firmware_ota.bin` v2.0.7.16.
- Goal: tighten simulator parity for app automation fields used in local-data snapshots (`0x0D-00` root case4).

## Firmware Evidence (v2.0.7.16, Raw Disassembly Base `0x200000`)

### Settings struct pointer and status refresh writer
- `0x22F274` returns service settings pointer literal `0x200717CC`.
- `0x22F20C` refresh path:
  - guards: `r1 != 0`, `r0 in {0,1}`
  - writes:
    - `[settings + 0x24] = 0x27D13C()`
    - `[settings + 0x28] = 0x27D142()`
  - then calls `0x272F04` (device-status notify path used by settings service lanes).

### Source of `settings+0x24` / `settings+0x28`
- `0x27D13C`:
  - `ldr r0, [0x2007206C]`
  - `ldr r0, [r0, #8]`
- `0x27D142`:
  - `ldr r0, [0x2007206C]`
  - `ldrsb r0, [r0, #0x0C]`
- This establishes:
  - `settings+0x24` is an unsigned scalar lane from source `+0x08`
  - `settings+0x28` is a signed scalar lane from source `+0x0C`

### Behavioral evidence for `settings+0x24` as battery-percent lane
- Wrapper `0x2BE636` returns `uxtb(0x27D13C())`.
- Multiple UI/reporting paths bucket this value with threshold ranges:
  - `<11`, `11..30`, `31..50`, `51..80`, `>=81`
  - seen at `0x2793A0..0x279416`, `0x329DDA..0x329E50`, `0x32AEB4..0x32AF2A`.
- This threshold pattern matches battery percentage bucket rendering semantics.

### Runtime toggles for `settings+0x20` / `settings+0x2C`
- `settings+0x20` (`tag11`) writes:
  - set `1` at `0x30B1FA` in handler `0x30B1A0` when `event_type == 2`
  - set `0` at `0x30B4DC` in same handler when `event_type == 5`
- `settings+0x2C` (`tag17`) writes:
  - clear `0` at `0x22CCCC`
  - set `1` at `0x22D294`
  - clear `0` at `0x22D2A8`
  - these writes occur in command-dispatch function `0x22D228` (switch over command/event values `2..5`).

### Device-status wrapper linkage (`0x4AAF04` / `0x4AA60E`)
- Wrapper `0x4AAF04`:
  - zeroes a `0x68`-byte staging struct
  - calls helper `0x4AA60E`
  - on success forwards staged struct to shared notify/parser path `0x4AACB4`
- Helper `0x4AA60E` writes header lanes:
  - `byte[0]=2` (`0x4AA66C`)
  - `halfword[8]=4` (`0x4AA670`)
- Helper `0x4AA60E` copies settings lanes used by case4 status interpretation:
  - `[settings+0x20] -> wrapper+0x44`
  - `[settings+0x24] -> wrapper+0x48`
  - `[settings+0x28] -> wrapper+0x4C`
  - `[settings+0x2C] -> wrapper+0x5C`
- Caller-context evidence (all call `0x4AAF04` after status-lane update/gate):
  - `0x465296`: sets `settings+0x2C=1`
  - `0x4652B6`: sets `settings+0x2C=0`, then emits case5/subcase1 and calls `0x4AAF04`
  - `0x46726E`: refreshes `settings+0x24/+0x28` via `0x4B513C/0x4B5142`
  - `0x5431FC` / `0x5434DE`: set `settings+0x20` to `1/0`
- Repro artifact:
  - `captures/firmware/analysis/2026-03-05-settings-device-status-wrapper-case4-map.md`

### String-anchored function context for unresolved lanes
- `0x30B1A0` string literals resolve to dashboard callback names:
  - `BleConnectStatusNotifyCallback eventType = %d`
  - `dashboard_async_update_data`
  - `Dashboard_ui_event_handler UI_EVENT_TYPE_INIT`
  - calendar/stock async-update send logs.
- This narrows `tag11/settings+0x20` to a dashboard callback/session lane; exact event enum labels remain unresolved.
- `0x22D228` literal table resolves to head-up calibration labels:
  - `setting_handle_head_up_setting`
  - `[setting]head_up_data is NULL`
  - `[setting]setting DISPLAY_STARTUP`
  - `ID_HEADUP_CALIBRATION_SUCCESSFUL_1`
- A nearby helper at `0x22D2D1` reads byte flag `*(uint8_t*)0x20073004`.
  - callers: `0x26DB1F/0x26DB2F/0x26DB5D` (ANCC flow), `0x26E2FF/0x26E31D/0x26E36D` (EvenAI gating), and `0x209FEB`.
  - firmware strings in these callers include calibration gating phrases (`calibration_ui_status`, notification suppression conditions).

## Case4 Tag Interpretation Update
- `tag12` (`settings+0x24`): inferred **device battery percent** lane.
- `tag13` (`settings+0x28`): inferred **device charge-state/trend** lane (signed source).
- `tag11` (`settings+0x20`): inferred **dashboard callback/session boolean lane** (event-driven toggle `2->1`, `5->0` in `BleConnectStatusNotifyCallback` path; exact enum mapping pending).
- `tag17` (`settings+0x2C`): inferred **head-up calibration UI showing lane** (set/clear in `setting_handle_head_up_setting`, correlated with `0x20073004` calibration UI flag readers).

## Simulator Parity (`g2-mock-firmware/src/ble_core.cpp`)
- Local-data case4 encode now refreshes `tag12/tag13` via a power-shadow helper before emitting root case4 payload:
  - `tag12`: battery percent inferred from simulator state (`case_state` first, ring shadow fallback).
  - `tag13`: charge-state inferred from simulator state (`case_state` first, ring shadow fallback).
- Local-data case4 now also refreshes `tag17` from simulator calibration-UI shadow state.
- Selector4 subtype3 transitions now mirror recalibration notify behavior for start/end:
  - rising edge (`value=1`) -> `tag17=1`, case5/subcase1 notify `status=0`, then case4 local-data status notify (`0x4AAF04` parity)
  - falling edge (`value=0`) -> `tag17=0`, case5/subcase1 notify `status=1`, then case4 local-data status notify (`0x4AAF04` parity)
- `tag11` remains a shadow lane pending exact dashboard event enum recovery.

## Next Actionable Improvements
1. Trace writer callgraph into source struct `0x2007206C` (`+0x08/+0x0C`) to recover canonical field names and enum domain.
2. Recover upstream dispatcher/registration path for `0x30B1A0` and map concrete event enum names behind `event_type 2/5` (`BleConnectStatusNotifyCallback` lane).
3. Recover full producer state machine for `0x22D228` (`setting_handle_head_up_setting`) to map command values `2/3/5` to canonical calibration lifecycle names.
4. Decode `0x4AACB4 -> 0x46F6EA` routing details for `0x4AAF04`-origin packets and lock ordering/channel assertions for paired case5+case4 transition emits.
5. Add replay fixtures that assert case4 tags `12/13/17` follow simulated battery/charge/calibration transitions while preserving unresolved `tag11` semantics.
