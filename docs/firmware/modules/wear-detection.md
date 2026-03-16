# Wear Detection Module (0x0D / 0x10)

## Scope
- Settings/config path: `0x0D-20` (command), `0x0D-00` (response)
- Onboarding path: `0x10-20` (command), `0x10-00` (response)
- Runtime gating linkage: settings + display/input gating logic (`service.settings`, `wear.detect`)

## Firmware Evidence (Binary)
- `WearDetect_SetEnable` at `ota_s200_firmware_ota.bin:0x002F56CC`
- Settings dispatcher linkage to wear-enable:
  - selector dispatch table at `0x46468E`
  - selector `5` stub at `0x464D04`
  - `0x464D04` calls `0x4AB196` (`WearDetect_SetEnable`)
- `WearDetect_DataHandler` at `0x002F572C`
- `WearDetect_HandleStatusChange` at `0x002E2698`
- `get_wear_status` at `0x002FF710`
- `onboarding_notify_wear_status_to_app` at `0x002C95D0`
- `[wear.detect]wear detect enable=%d` at `0x002F56E4`
- `[wear.detect]WEAR!!!` at `0x002F56FC`
- `[wear.detect]UNWEAR!!!` at `0x002F5714`
- `[wear.detect]Invalid wear detect data` at `0x002CDB08`
- `[service.settings]wear_detection_switch: %d` at `0x002C2738` / `0x002EAA0C`
- `[service.settings]wear detect input not enabled, input event not allowed` at `0x00282AD8`
- `[service.settings]wear detect input not enabled, jbd4010 ctrl not allowed` at `0x00282B24`
- `[pt_protocol_procsr]join in get_wear_status` at `0x002C1500`
- `[pt_protocol_procsr]wear status: %d` at `0x002D47E8`
- Onboarding wear notify logs:
  - `Onboarding: wear status notified to app, status=%d` at `0x002871F8` / `0x002AE210`
  - `Onboarding: failed to notify wear status to app, ret=%d` at `0x0027CC28` / `0x002A5898`
- Sensor-state labels present across versions: `PROXIMITY_WEAR`, `PROXIMITY_UNWEAR`
- CLI evidence in firmware strings:
  - `set weardetect <enable|disable>`
  - `weardetect 0 or 1`

## Current Simulator Behavior (`g2-mock-firmware/src/ble_core.cpp`)
- Maintains explicit wear state:
  - `wear_detection_enabled` (switch)
  - `wear_status` (`1=wear`, `0=unwear`)
- `SETTING_CMD_APP_REQUIRE_BASIC` (`cmdId=0`) now responds with a wear snapshot on `0x0D-00`:
  - `f1 = wear_detection_enabled`
  - `f2 = wear_status`
  - `f3/f4 = legacy placeholder zeros (simulator compatibility)`
- Added firmware-selector lane in settings handler:
  - selector `1` returns wear snapshot
  - selector `5` applies wear enable state and returns wear snapshot
  - selector `7` no-op
  - selector runtime context tracking for `2/3/4/6/8` is now present in simulator shadow state (see settings runtime context module), while wear logic remains bound to selector `5`
  - unmapped selectors fall back to legacy `cmdId` handling
- Onboarding side-channel on `0x10-00` can report current wear status as raw `[0x0D, wear_flag]`.
- Added simulator compatibility path for bare `cmdId=1` on `0x0D-20` to re-enable wear detection (for existing local app helper behavior).
- Added simulator-only deterministic control command:
  - `cmdId=250` (`SETTING_CMD_SIM_WEAR_STATE`)
  - payload shape: `f2={f1=enable(0/1), f2=status(0/1)}`
  - response: same wear snapshot fields (`f1..f4`) on `0x0D-00`
- Added serial console controls:
  - `wear on`, `wear off`
  - `wear detect on`, `wear detect off`
  - `wear status`

## Notes
- `cmdId=250` is a simulator test harness shim only, not firmware-confirmed behavior.
- Bare `cmdId=0` is treated as query/snapshot, so disabling wear detection requires either:
  - simulator shim (`cmdId=250`), or
  - serial console control.

## Next Actionable Improvements
1. Recover exact selector wire format for wear-enable (`selector=5`) so simulator can remove fallback heuristics and parse only firmware-authentic fields.
2. Recover the real `get_wear_status` request path and its response envelope (service + field mapping) from deeper binary control-flow analysis near `APP_PbRxSettingFrameDataProcess`.
3. Correlate selector `5` writes with neighboring selector context bytes (`+0x08/+0x09/+0x0A..+0x0C/+0x15`) to distinguish wear-local vs shared-settings side effects.
4. Add capture fixtures with explicit wear transitions (WEAR→UNWEAR and switch enable/disable) and assert simulator parity on both `0x0D-00` and raw onboarding side-channel traffic on `0x10-00`.
