# Settings Head-Up Calibration Flow

## Scope
- Firmware-only recovery of the head-up calibration control path in `ota_s200_firmware_ota.bin` (v2.0.7.16).
- Focus: calibration UI state transitions that feed settings local-data case4 `tag17` (`settings+0x2C`).

## Firmware Evidence (Raw Disassembly Base `0x200000`)

### Head-up setting handler (`setting_handle_head_up_setting`)
- Command/event handler at `0x22D228` switches on `r0` values `2..5`.
- String literals in the same literal table resolve to:
  - `setting_handle_head_up_setting`
  - `[setting]head_up_data is NULL`
  - `[setting]setting DISPLAY_STARTUP`
  - `ID_HEADUP_CALIBRATION_SUCCESSFUL_1`
- Runtime writes in this handler:
  - `0x22D294`: `settings+0x2C = 1`
  - `0x22D2A8`: `settings+0x2C = 0`
  - `0x22CCCC`: additional explicit clear path to `settings+0x2C = 0`

### Calibration UI boolean flag (`0x20073004`)
- Helper at `0x22D2D1`:
  - `ldr r0, [0x20073004]`
  - `ldrb r0, [r0]` equivalent read of calibration UI flag byte
  - returns this boolean.
- Handler `0x22D228` case `5` clears `0x20073004` (`0x22D2AD`).
- Callers of `0x22D2D1`:
  - `0x26DB1F`, `0x26DB2F`, `0x26DB5D` (ANCC notification path)
  - `0x26E2FF`, `0x26E31D`, `0x26E36D` (EvenAI/service gating path)
  - `0x209FEB` (display/event gating helper)
- Caller strings include calibration gating semantics (`calibration_ui_status`, notification suppression paths).

### Local-data case4 linkage
- Root case4 builder (`0x4AA5EE`) reads `settings+0x2C` into case4 `tag17`.
- This links head-up calibration handler writes to app-visible local-data snapshots.

## Interpretation Update
- `settings+0x2C` / case4 `tag17` is best interpreted as a **head-up calibration UI showing/status lane**.
- `0x20073004` acts as a related calibration-UI boolean used by other services to gate outgoing behavior.

## Simulator Parity (`g2-mock-firmware/src/ble_core.cpp`)
- Added calibration-UI shadow state and case4 `tag17` refresh path.
- Selector4 subtype3 transitions now drive calibration lane updates and notify-group parity:
  - `value=1` (rising) -> `tag17=1`, case5/subcase1 `status=0`, then case4 local-data status notify (`0x4AAF04` parity)
  - `value=0` (falling) -> `tag17=0`, case5/subcase1 `status=1`, then case4 local-data status notify (`0x4AAF04` parity)

## Next Actionable Improvements
1. Recover the upstream caller/registration chain that dispatches into `0x22D228` to bind values `2/3/5` to canonical calibration lifecycle enums.
2. Map interactions between `settings+0x2C` and `0x20073004` across all writers to confirm whether they represent identical or staged states.
3. Add deterministic simulator tests that verify `tag17` and case5/subcase1 notify transitions under selector4 subtype3 toggle sequences.
