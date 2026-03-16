# G2 Service Handler Index (v2.0.7.16 Anchored)

Date: 2026-03-05  
Scope: service IDs, handler symbols, offsets, and component callouts for boot-to-idle runtime dispatch.

## 1. Dispatch Baseline

Idle runtime entry points in `ota_s200_firmware_ota.bin`:

| Node | Offset (dec) | Offset (hex) |
|---|---:|---:|
| `thread_ble_msgrx` | 3127436 | `0x002FB88C` |
| `thread_ble_msgtx` | 3127476 | `0x002FB8B4` |
| `thread_ble_wsf_wait_tx_ready` | 3019064 | `0x002E1138` |
| `thread_audio` | 2718560 | `0x00297B60` |
| `thread_input` | 2719008 | `0x00297D20` |
| `thread_ring` | 3158852 | `0x00303344` |
| `display_thread` | 3133264 | `0x002FCF50` |

Service dispatch pattern:

```
BLE write (0x5401 / 0x6401 / 0x7401)
  -> *_common_data_handler
  -> subsystem/component work
  -> BLE notify (0x5402 / 0x6402 / 0x7402)
  -> back to wait state
```

## 2. BLE Lane and UUID Anchors

Source: `captures/firmware/analysis/2026-03-03-ble-artifact-extraction.json`.

| Lane | UUID (short) | Purpose |
|---|---|---|
| `0x5401/0x5402` | `...5401 / ...5402` | control/service protobuf traffic |
| `0x6401/0x6402` | `...6401 / ...6402` | display/render lane |
| `0x7401/0x7402` | `...7401 / ...7402` | file/OTA transfer lane |
| `BAE80001` | `BAE80001-4F05-...` | R1 ring primary runtime service |
| `FE59` | `FE59` | R1 buttonless DFU trigger service |

v2.0.7.16 UUID hit anchors (`ota_s200_firmware_ota.bin`):
- `g2_control_5401` @ `3126219`
- `g2_display_6401` @ `3126179`
- `g2_file_7401` @ `3126139`
- `ring_service_bae80001` @ `3142528`

## 3. Service ID -> Handler Symbol Map

Primary source anchors:
- handler strings from `ota_s200_firmware_ota.bin`
- service naming from `docs/protocols/services.md`

| Service ID | Handler Symbol(s) | Offset (dec / hex) | Component Callout |
|---|---|---|---|
| `0x01-20` Dashboard | `Dashboard_common_data_handler` | `2991064 / 0x002DA3D8` | dashboard/UI state |
| `0x02-20` Notification | `MessageNotify_common_data_handler` | `2959932 / 0x002D2A3C` | notification routing |
| `0x03-20` Menu | `Menu_common_data_handler` | `3046064 / 0x002E7AB0` | menu/page UI |
| `0x05-20` Translate | `Translate_common_data_handler` | `3020216 / 0x002E15B8` | translate UI/data |
| `0x06-20` Teleprompt | `Teleprompt_common_data_handler` | `3017304 / 0x002E0A58` | teleprompt pages/progress |
| `0x07-20` EvenAI | `EvenAI_common_data_handler` | `3036628 / 0x002E55D4` | AI command/status |
| `0x08-20` Navigation | descriptor-adjacent executable lanes `0x00588817`, `0x00588AF3` | service word `0x0067641C`, ctx `0x20002BE4` | nav UI lane; worker/commit path anchored |
| `0x09-00/20` DeviceInfo / DevConfig | descriptor-adjacent executable lanes `0x00464481`, `0x00465209` | service word `0x006764BC`, ctx `0x20003848` | dev-config/settings bridge; device info shares parser/status path |
| `0x0B-20` Conversate | `Conversate_common_data_handler` | `2988792 / 0x002D9AF8` | speech transcript/session |
| `0x0C-20` Quicklist/Health | `Quicklist_common_data_handler`, `Health_common_data_handler` | `3011864 / 0x002DF518`, `3038504 / 0x002E5D28` | list + health state |
| `0x0D-00/20` Settings | `Setting_common_data_handler`, `silent_mode_common_data_handler` | `3059448 / 0x002EAEF8`, `3015768 / 0x002E0458` | settings/wear/status |
| `0x0E-20` DisplayConfig | `display_config_handler` | — | display viewport regions (6 IEEE 754 floats) |
| `0xE0-20` EvenHub | `evenhub_common_data_handler` | `3036880 / 0x002E56D0` | container render/layout |
| `0x0F-20` Logger | `loggerSetting_common_data_handler` | `2953560 / 0x002D1158` | `/log/` operations |
| `0x10-20` Onboarding | `Onboarding_common_data_handler` | `3005240 / 0x002DDB38` | first-run flow |
| `0x20-20` ModuleConfig/Sync | `ModuleConfigureService_common_data_handler`, `SyncInfoService_common_data_handler` | `2876772 / 0x002BE564`, `2974980 / 0x002D6504` | feature/sync envelope |
| `0x21-20` SystemAlert | `system_alert_common_data_handler` | `2975160 / 0x002D65B8` | alert events |
| `0x22-20` SystemClose | `system_close_common_data_handler` | `2975376 / 0x002D6690` | close/exit decisions |
| `0x81-20` BoxDetect | `BoxDetect_common_data_handler` | `3012536 / 0x002DF7B8` | case relay path |
| `0x91-20` Ring relay | `RingDataRelay_common_data_handler`, `APP_PbRxRingFrameDataProcess` | `2964504 / 0x002D3C18`, `3008472 / 0x002DE7D8` | ring command/event relay |
| `0xFF-20` SystemMonitor | `system_monitor_common_data_handler` | `2975124 / 0x002D6594` | idle/monitor state |

## 4. File/OTA Command Plane (0xC4/0xC5)

| Command Path | Anchor | Offset (dec / hex) |
|---|---|---|
| transmit start | `pt_ota_transmit_start` | `3093364 / 0x002F3174` |
| transmit file | `pt_ota_transmit_file` | `3093388 / 0x002F318C` |
| transmit metadata | `pt_ota_transmit_information` | `3054604 / 0x002E9B2C` |
| result check | `pt_ota_transmit_result_check` | `3011608 / 0x002DF418` |
| transport module anchor | `ota.tran` | `3155216 / 0x003024F0` |
| service module anchor | `ota.service` | `3155192 / 0x003024D8` |

Case-OTA relay symbols:
- `pt_box_ota_begin` @ `3122696`
- `pt_box_ota_file_get` @ `3122716`
- `box_uart_mgr` @ `3132656`

## 5. Internal Component Callout Anchors

| Component | Anchor | Offset (dec) |
|---|---|---:|
| BLE radio DFU | `service_em9305_dfu.c` | 2631853 |
| touch path | `service_touch_dfu.c` | 2632616 |
| gesture path | `service_gesture_processor.c` | 2631999 |
| display driver | `drv_mspi_jbd4010.c` | 2644620 |
| codec path | `codec.dfu` | 2572133 |
| case detect | `service_box_detect.c` | 2589164 |

### 5.1 Service `0x81` (BoxDetect) Dispatch/Notify Closure

Instruction-level closure from runtime RE artifact:
- dispatch function `0x004B4714` branches on command selector and routes to:
  - notify path `0x004B47D2 -> 0x004B44BE`
  - state/apply path `0x004B4814/0x004B4856 -> 0x004B4526`
- BLE response send call: `0x004B451E -> 0x00463178` with recovered `r0=0x81`.
- BoxDetect handler-string xrefs: `0x004B4754`, `0x004B47A8`, `0x004B47EA`, `0x004B482C`, `0x004B4872` -> `0x00717798`.
- case-sync message xref in dispatch: `0x004B4822 -> 0x007177B8`.
- auxiliary caller-linked edge retained for follow-up lift: `0x00545866 -> 0x00543E06`.

Artifact:
- `captures/firmware/analysis/2026-03-05-g2-boxdetect-ble-chain.md`

### 5.2 Service `0x91` (Ring Relay) Descriptor/Call-Chain Closure

Instruction-level closure from runtime RE artifact:
- descriptor slot binds service to handler: `0x0067643C=0x00000091`, `0x00676440=0x005B46B1`.
- wrapper and parser chain: `0x005B46B0 -> 0x005B41FC`.
- parser string-xref anchors:
  - `APP_PbRxRingFrameDataProcess`: `0x005B421E`, `0x005B4268`, `0x005B42F6`, `0x005B434E`, `0x005B43B6`
  - ring diagnostics: `0x005B4370`, `0x005B43D8`, `0x005B44F0`, `0x005B473A`
- outbound ring send closure: `0x005B46A4 -> 0x0046F5C4` with immediate `r1=0x91`.

Artifact:
- `captures/firmware/analysis/2026-03-05-g2-ring-relay-callchain.md`

### 5.3 Service `0xFF` (System Monitor) Descriptor/Idle Closure

Instruction-level closure from runtime RE artifact:
- descriptor slot binds service to handler: `0x006764EC=0x000000FF`, `0x006764F0=0x005221D5`.
- notify sender bridge: `0x004D0972 -> 0x00522184`.
- BLE send closure: `0x005221CC -> 0x00463178` with immediate `r0=0xFF`.
- handler anchors:
  - `system_monitor_common_data_handler` xrefs: `0x005221F0`, `0x00522262`, `0x005222A2`, `0x005222E2`, `0x0052232C`, `0x0052238C`
  - idle marker xref: `0x005223A8 -> 0x006A1EB4`

Artifact:
- `captures/firmware/analysis/2026-03-05-g2-system-monitor-callchain.md`

### 5.4 Service `0x08` (Navigation) Descriptor-Adjacent Lane Closure

Instruction-level closure from runtime RE artifact:
- descriptor-adjacent words: `0x0067641C=0x00000008`, `0x00676420=0x00588817`, `0x00676424=0x00588AF3`, `0x00676428=0x20002BE4`.
- primary lane prologue `0x0058882C` is navigation-string anchored (`navigation.c`) and repeatedly dispatches to `0x00583230` (`0x00588922`, `0x0058893E`, `0x0058895A`, `0x00588976`, `0x005889D4`, `0x00588A32`, `0x00588A90`).
- secondary lane prologue `0x00588AF2` is navigation-string anchored and closes the downstream path:
  - `0x00588B4A -> 0x00580018`
  - `0x00588B58 -> 0x004B3F66`
  - `0x00588B6A -> 0x00583B9C`
- shared context write is explicit: literal load `0x00588B52 -> 0x20002BE4`, followed by store to `[ctx + 0x04]` at `0x00588B54`.

Artifact:
- `captures/firmware/analysis/2026-03-05-g2-nav-devinfo-descriptor-lanes.md`

### 5.5 Service `0x09` (DeviceInfo / DevConfig Bridge) Descriptor-Adjacent Closure

Instruction-level closure from runtime RE artifact:
- descriptor-adjacent words: `0x006764BC=0x00000009`, `0x006764C0=0x00464481`, `0x006764C4=0x00465209`, `0x006764C8=0x20003848`.
- primary lane prologue `0x00464480` carries `BLE data parsing started` / `[setting]BLE data parsing started` string xrefs and calls:
  - `0x004644DE -> 0x004AA30C` (shared settings parser bridge)
  - `0x00464540 -> 0x004676E6` (dev-info-side fallback/helper)
- secondary lane prologue `0x00465208` drives settings/runtime helpers rather than a pure read-only info handler:
  - `0x0046525A -> 0x004AF286` (`dominant_hand_reader`)
  - `0x0046526A -> 0x004AF4F8` (head-up calibration gate)
  - `0x0046526E/0x00465282 -> 0x00467254` (status context)
  - `0x00465276/0x00465296 -> 0x004AAEE4` (status notify wrapper)
  - `0x00465292 -> 0x004AAF94` (case-5 notify wrapper)
- shared context write is explicit: literal load `0x00465262 -> 0x20003848`, followed by store to `[ctx + 0x04]` at `0x00465264`.

Artifact:
- `captures/firmware/analysis/2026-03-05-g2-nav-devinfo-descriptor-lanes.md`

## 6. Known Unresolved Mappings

1. Exact handler symbol for navigation service `0x08-20` (descriptor-adjacent executable lanes are recovered, but the final symbolic/common-data-handler name is still unresolved).
2. Exact handler symbol and full command field map for device info service `0x09-*` (descriptor-adjacent dev-config bridge is recovered, but the final symbolic/common-data-handler name is still unresolved).
3. `0x90-??` reserved/unknown service from dispatch table remains unresolved.
