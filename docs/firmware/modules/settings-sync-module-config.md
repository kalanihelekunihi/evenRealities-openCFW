# Settings + SyncInfo + ModuleConfigure (0x0D / 0x20)

## Scope
- Settings/ProtoBaseSettings: `0x0D-00` / `0x0D-20`
- Sync-info and module configure: `0x20-20` / `0x20-00`
- Dashboard state sync and dashboard auto-close values span these handlers.
- Wear detection command routing (`0x0D`) is coupled to the same settings envelope.

## Firmware Evidence (Binary)
- `ModuleConfigureService_common_data_handler` at `ota_s200_firmware_ota.bin:0x002BD764`
- Settings parse/dispatch chain:
  - parser at `0x4AA30C`
  - dispatch hub at `0x464548`
  - selector load (`ldrh [r4,#0x0C]`) at `0x4646DA`
  - selector dispatch table at `0x46468E` (`1..11`)
  - selector `5` path: `0x464D04 -> 0x4AB196 (WearDetect_SetEnable)`
- `ModuleDashboardAutoCloseValueService_response_inquiry_cmd` at `0x0029AA80`
- `ModuleDashboardAutoCloseValueService_response_set_cmd` at `0x002A30F8`
- `SyncInfoService_common_data_handler` at `0x002D559C`
- `[sync_info.main]sync_info_data_handler: unknown cmd = %d` at `0x0029E338`
- `[page_state_sync]Dashboard main page state synced: tile=%d, widget=%d` at `0x00285ECC`
- `[general_configure]module_configure_data_handler receive system general setting packet from APP` at `0x002BA5CC`
- `[general_configure]module_configure_data_handler set general configure language to %d` at `0x002BA65C`
- `set_general_configure_language: language %d not supported, set to %d` at `0x002BAC3C`
- `[dashboard]dashboard_ui_event_handler Dashboard auto close value is 0xFF55, not auto close` at `0x002CDFA0`

## Current Simulator Behavior (`g2-mock-firmware/src/ble_core.cpp`)

### Settings (`0x0D-00` / `0x0D-20`)
- Accepts both channels for compatibility.
- Uses dual-lane handling:
  - firmware selector lane (`selector 1..11`, when selector-oriented payload is detected)
  - legacy `cmdId` lane (`f1=cmdId`) for existing app/capture compatibility
- Uses firmware root-oneof gating:
  - root case `3` => selector lane
  - root case `4` => local-data response envelope (descriptor `0x727F34`, tags `1..19`)
  - root case `5` => inbound notify-group decode/apply (`subcase1/2`) without legacy `cmdId` fallback
  - root cases `6/7` => capture-only telemetry lane (first field/wire/scalar/blob/seen-count), no legacy `cmdId` fallback
- Capture-backed compact settings-status events on `0x0D-01`:
  - observed packet family: `f1=1`, `f3={f1=event[,f2=status]}`
  - observed event ids in local captures: `6`, `11`, `16`
  - simulator sources compact events from shared `config_state` module transitions (not direct selector hooks), matching capture correlation to `0x06/0x07/0x0B` traffic
- `cmd=0` (`APP_REQUIRE_BASIC`) returns stateful wear snapshot fields in simulator (`f1=wear_detection_enabled`, `f2=wear_status`) for automation parity with local app query path.
- Selector parity currently implemented from firmware-confirmed behavior:
  - selector `1`: query-basic snapshot response + sub-type context tracking (`+0x16/+0x17`)
  - selector `2`: scalar context write (`+0x08`)
  - selector `3`: scalar context write (`+0x09`)
  - selector `4`: subtype `1` write (`+0x0A`), subtype `2` write (`+0x0C`), subtype `3` calibration gate shadow (`0x2D320`) + paired notify on gate transitions (case5/subcase1 and case4 local-data status via `0x4AAF04` parity)
  - selector `5`: wear-enable write path
  - selector `6`: scalar context write (`+0x15`) with event-parity logging (`0x10A`) and case5/subcase2 notify on value change
  - selector `7`: no-op branch
  - selector `8`: conditional gate parity path
- Implements dashboard auto-close persistence in simulator state:
  - `GET` (`cmd=8`) returns current value
  - `SET` (`cmd=7`) updates and echoes value
  - accepts normal range (`<=240`) and disable sentinel `0xFF55`
- `cmd=5` sync-info request triggers dashboard state push (`tile/widget/expanded`).
- Simulator-only deterministic wear control shim is available on `cmd=250` (details in wear module doc).
- Dispatch internals are detailed in [settings-dispatch.md](settings-dispatch.md).
- Descriptor-backed selector wire schema is documented in [settings-selector-schema.md](settings-selector-schema.md).
- Runtime context byte map is detailed in [settings-runtime-context.md](settings-runtime-context.md).
- Case4 local-data status-lane evidence (`tags 11/12/13/17`) is detailed in [settings-local-data-status.md](settings-local-data-status.md).
- Root envelope parser and wrapper internals are detailed in [settings-envelope-parser.md](settings-envelope-parser.md).
- Compact settings-status event lane is detailed in [settings-compact-notify.md](settings-compact-notify.md).

### ModuleConfigure (`0x20-20`)
- Command type echo on `0x20-00` with optional `msg_id`.
- `dashboardSetting` command updates dashboard auto-close value from nested payload (`f3.f1`), including sentinel `0xFF55`.
- `systemSetting` command updates language from nested payload (`f3.f1`), with unsupported values falling back to `1`.
- `moduleList` command returns stub-enabled module flags in nested `f3` (`f1..f15 = 1`).
- `brightnessCalibration` consumes left/right nested values and updates brightness baseline.

## Next Actionable Improvements
1. Promote root case6/7 capture telemetry into concrete schema + producer/consumer mappings, then connect any discovered interactions to sync/module-config flows.
2. Resolve remaining unresolved case4 mode/session lane (`tag11/settings+0x20`) and map it to sync/module-config event domains; validate whether sync/module-config triggers ever mutate calibration lane `tag17`.
3. Resolve exact emission conditions for device-status wrapper `0x4AAF04` and map empty companion payload behavior (`08011a00`) into deterministic simulator flows.
4. Trace `0x463F0E` follow-on notifications and integrate those side effects into `0x0D`/`0x20` mixed-flow simulator responses.
5. Add regression traces for mixed flows (`0x0D` selector lane + `0x0D` legacy cmd lane + `0x20` module/system setting + sync pull), including selector runtime-context assertions.
