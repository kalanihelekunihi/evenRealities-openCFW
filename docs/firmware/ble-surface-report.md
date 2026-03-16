# Firmware BLE Surface Report

## Transport Baseline

- The firmware exposes three BLE transport pipes, not one: control/EUS `0x5401/0x5402`, file/EFS `0x7401/0x7402`, and sensor/ESS `0x6401/0x6402`. See `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/transport_protocol.c:1-27`.
- Shared protocol helpers such as inter-eye sync, display reflash/startup, auth lifecycle, time sync, audio control, and ring relay sit below the per-service handlers in `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/protocol_common.c:1-25` and `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/protocol_common.c:151-176`.

## BLE-Exposed Service Inventory

| Area | Firmware entrypoint | BLE surface | Current iOS app state |
|---|---|---|---|
| Auth / pairing | `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_service_pair_mgr.c:1-32` | `0x80` auth handshake, heartbeat, pipe role, ring-connect relay | Implemented in the app auth/session layer; constants live in `Sources/EvenG2Shortcuts/ProtocolConstants.swift:108-145`. |
| Notifications | `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_service_notification.c:1-27` and `openCFW/src/platform/apollo510b/main_firmware/app/gui/notification/msg_notification_ui.c:13-28` | `0x02` notification control, whitelist, render pipeline; requires `displayWake` + `displayConfig`; JSON key must be `android_notification` | Implemented. The app matches the required JSON key in `Sources/EvenG2Shortcuts/G2NotificationPayload.swift:21` and supports whitelist upload in `Sources/EvenG2Shortcuts/G2NotificationWhitelist.swift:49-64`. |
| Dashboard | `openCFW/src/platform/apollo510b/main_firmware/app/gui/dashboard/dashboard.c:1-23` and `openCFW/src/platform/apollo510b/main_firmware/app/gui/dashboard/dashboard.c:52-69` | `0x01-20` dashboard data packages, widget updates, gesture ACKs | Partially implemented. The app models dashboard state via `0x0D` sync/config (`Sources/EvenG2Shortcuts/G2DashboardStateSender.swift:10-12`) but I did not find a production sender for full `0x01-20` dashboard content pushes. |
| Menu | `openCFW/src/platform/apollo510b/main_firmware/app/gui/menu/menu_page.c:1-25` and `openCFW/src/platform/apollo510b/main_firmware/app/gui/menu/menu_page.c:84-99` | `0x03-20` menu item list / launcher config | Implemented in `Sources/EvenG2Shortcuts/G2MenuSender.swift:3-10` and `Sources/EvenG2Shortcuts/G2MenuSender.swift:21-86`. |
| Teleprompter | `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_teleprompter_handler.c:1-27` | `0x06-20` teleprompter control plus file-list, file-select, page-data, scroll-sync flows | Core live teleprompter is implemented in `Sources/EvenG2Shortcuts/G2TeleprompterSender.swift:11-42`, but file-based/list mode is not. The protocol file explicitly says type `2` list mode is undocumented and unimplemented in `Sources/EvenG2Shortcuts/G2TeleprompterProtocol.swift:3-8`. |
| EvenAI | `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_service_even_ai.c:1-29` | `0x07-20` CTRL, VAD, ASK, REPLY, SKILL, PROMPT, EVENT, HEARTBEAT, CONFIG | Implemented in `Sources/EvenG2Shortcuts/G2EvenAISender.swift:8-33` and skill paths in `Sources/EvenG2Shortcuts/G2EvenAISender.swift:69-160`. |
| Navigation | `openCFW/src/platform/apollo510b/main_firmware/app/gui/navigation/navigation_data_handler.c:1-30` and `openCFW/src/platform/apollo510b/main_firmware/app/gui/navigation/navigation.c:2592-2668` | `0x08-20` for incoming nav content; `0x08` notify-back path for view-changed / compass-changed events | Mostly implemented on the send side in `Sources/EvenG2Shortcuts/G2NavigationSender.swift:3-20` and `Sources/EvenG2Shortcuts/G2NavigationProtocol.swift:112-260`. Notify-back events are only generically logged in `Sources/EvenG2Shortcuts/G2BluetoothClient.swift:617-619`. |
| Conversate | `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_conversate_handler.c:1-18` | `0x0B-20` live captioning / transcript ACK + notify | Implemented in `Sources/EvenG2Shortcuts/G2ConversateSender.swift:3-12` and `Sources/EvenG2Shortcuts/G2ConversateSender.swift:25-99`. |
| Quicklist + health | `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_service_quicklist.c:1-23` and `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_health_handler.c:1-18` | Shared `0x0C-20` quicklist CRUD plus health record/highlight commands | Implemented in `Sources/EvenG2Shortcuts/G2TasksSender.swift:3-8`, `Sources/EvenG2Shortcuts/G2TasksSender.swift:11-68`, and `Sources/EvenG2Shortcuts/G2HealthDataSender.swift:3-12`. |
| Settings / config | `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_service_setting.c:1-25` | `0x0D` config queries, notifications, ring compact notify | Broadly implemented in the app config layer; app constants are in `Sources/EvenG2Shortcuts/ProtocolConstants.swift:164-170`, and command IDs are modeled in `Sources/EvenG2Shortcuts/G2DeviceConfigProtocol.swift:6-35`. |
| Onboarding | `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_service_onboarding.c:1-27` and `openCFW/src/platform/apollo510b/main_firmware/app/gui/onboarding/onboarding.c:15-30` | Dedicated `0x10-20` protobuf service plus raw subcommands for head-up / wear / flag sync | Partially and likely incorrectly modeled. The app still sends onboarding start/startup/end through `0x0D-20` config in `Sources/EvenG2Shortcuts/G2OnboardingProtocol.swift:58-74` and `Sources/EvenG2Shortcuts/G2OnboardingProtocol.swift:118-190`, while the firmware’s authoritative onboarding service is `0x10-20`. |
| Module configure | `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_service_dev_config.c:1-19` | `0x20-20` module config / brightness calibration / config ACK | Implemented in `Sources/EvenG2Shortcuts/G2ModuleConfigureSender.swift:6-13` and `Sources/EvenG2Shortcuts/G2ModuleConfigureSender.swift:41-118`. |
| EvenHub | `openCFW/src/platform/apollo510b/main_firmware/app/gui/EvenHub/evenhub_data_parser.c:1-34` and `openCFW/src/platform/apollo510b/main_firmware/app/gui/EvenHub/evenhub_main.c:572-610` | `0xE0-20` startup, content, rebuild, reflash, config, audio-config | Implemented. The app now uses explicit `0xE0-00` response handling and startup confirmation in `Sources/EvenG2Shortcuts/G2EvenHubSender.swift:160-220`. |
| Box / case detect | `openCFW/src/platform/apollo510b/main_firmware/platform/service/box_detect/service_box_detect.c:1-32` | `0x81-20` case SOC / charging / lid / in-case data, plus peer relay | Implemented for the main case-status probe path in `Sources/EvenG2Shortcuts/G2DisplayTriggerSender.swift:3-18`. |
| Ring relay | `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_ring_handler.c:1-16` | `0x91-20` G2-to-R1 ring bridge | Implemented in `Sources/EvenG2Shortcuts/G2RingRelaySender.swift:3-13` and `Sources/EvenG2Shortcuts/G2RingRelaySender.swift:18-79`. |
| System close | `openCFW/src/platform/apollo510b/main_firmware/app/gui/SystemClose/systemClose.c:1-34` | `0x22-20` YES / NO / MINIMIZE close dialog | Implemented in `Sources/EvenG2Shortcuts/G2SystemCloseSender.swift:6-13` and `Sources/EvenG2Shortcuts/G2SystemCloseSender.swift:17-74`. |
| System alert | `openCFW/src/platform/apollo510b/main_firmware/app/gui/SystemAlert/systemAlert.c:1-18` | `0x21-20` receive-only alert/banner injection | Only partially modeled. The app decodes `0x21-00` in `Sources/EvenG2Shortcuts/G2ResponseDecoder.swift:1412-1418`, but the firmware description says this service is receive-only and does not send alerts back to the phone. |
| System monitor | `openCFW/src/platform/apollo510b/main_firmware/app/gui/system/system_monitor.c:1-18` and `openCFW/src/platform/apollo510b/main_firmware/app/gui/system/system_monitor.c:87-140` | `0xFF-20` remote reset via magic sequence; non-reset commands ignored | Mis-modeled in the app. `Sources/EvenG2Shortcuts/G2SystemMonitorSender.swift:3-12` still treats it as a pollable query service. |
| File transfer / export | `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/efs_service/efs_service.c:1-18` | `0xC4/0xC5/0xC6/0xC7` send + export surfaces | Partially implemented. The app only exposes `0xC4` and `0xC5` in `Sources/EvenG2Shortcuts/ProtocolConstants.swift:277-279`; its export path is still inferred over those same two services in `Sources/EvenG2Shortcuts/G2FileExportClient.swift:15-21`. |

## Internal-Only Or Mostly Internal Firmware Features

- Inter-eye display sync and peer relays are internal plumbing, not separate phone APIs: `RequestDisplayReflash`, `SendDataToBoth`, and peer event transport in `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/protocol_common.c:8-19` and `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/protocol_common.c:151-176`.
- Most LVGL page rendering is internal-only once a BLE handler has accepted data: dashboard, menu, EvenHub, onboarding, system alert, and system close all expose BLE entrypoints but do the real work inside local UI/event code (`dashboard.c`, `menu_page.c`, `evenhub_main.c`, `onboarding.c`, `systemAlert.c`, `systemClose.c`).
- Wear/case gating is largely internal service logic rather than a clean standalone BLE API. Example: launch/ULED checks require BLE not pairing, OTA idle, wear active, and not-in-case in `openCFW/src/platform/apollo510b/main_firmware/platform/service/settings/service_settings.c:225-234` and `openCFW/src/platform/apollo510b/main_firmware/platform/service/settings/service_settings.c:245-299`.
- Case handling also has internal peer-merge logic across eyes in `openCFW/src/platform/apollo510b/main_firmware/platform/service/box_detect/service_box_detect.c:13-32`; the phone only sees the summarized case state.

## Likely Missing Or Incorrect In EvenG2Shortcuts

1. Full dashboard content on `0x01-20` is likely still missing.
   The firmware’s real dashboard service handles weather, stock, calendar, news, and widget packages on `0x01`, but the app mostly uses `0x0D`, `0x0C`, and `0x20` for dashboard-related state/config. See `openCFW/src/platform/apollo510b/main_firmware/app/gui/dashboard/dashboard.c:1-23` versus `Sources/EvenG2Shortcuts/G2DashboardStateSender.swift:10-12`.

2. Onboarding is probably routed to the wrong service.
   Firmware makes onboarding a dedicated `0x10-20` protocol with config/heartbeat/event messages and raw subcommands; the app still sends startup/start/end/head-up through `0x0D-20`. See `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_service_onboarding.c:1-27` and `Sources/EvenG2Shortcuts/G2OnboardingProtocol.swift:118-190`.

3. `SystemMonitor` query/poll behavior is likely wrong.
   The firmware handler ignores non-reset commands and only acts on a magic reset payload, but the app still exposes `queryStatus()`. See `openCFW/src/platform/apollo510b/main_firmware/app/gui/system/system_monitor.c:87-140` and `Sources/EvenG2Shortcuts/G2SystemMonitorSender.swift:18-63`.

4. `SystemAlert` is over-modeled on the iOS side.
   The firmware explicitly documents `0x21-20` as receive-only, but the app treats `0x21-00` as a normal response/event stream. See `openCFW/src/platform/apollo510b/main_firmware/app/gui/SystemAlert/systemAlert.c:15-18` and `Sources/EvenG2Shortcuts/G2ResponseDecoder.swift:1412-1418`.

5. Teleprompter list/file mode is not implemented.
   Firmware exposes file-list, file-select, page-data request, and scroll-sync paths, but the app only implements the direct text/session flow. See `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/pb_teleprompter_handler.c:4-18` and `Sources/EvenG2Shortcuts/G2TeleprompterProtocol.swift:3-8`.

6. File export is probably incomplete.
   The firmware EFS handler names four service IDs (`0xC4`..`0xC7`), but the app only models `0xC4/0xC5` and marks export command bytes as inferred. See `openCFW/src/platform/apollo510b/main_firmware/platform/protocols/efs_service/efs_service.c:10-18` and `Sources/EvenG2Shortcuts/G2FileExportClient.swift:15-21`.

7. Dedicated logger service support remains unverified.
   The app models a standalone `0x0F-20/0x0F-00` logger service in `Sources/EvenG2Shortcuts/G2LoggerSender.swift:3-12`, but during this pass I did not locate a matching openCFW handler file. The more defensible path in the current app is the `0x0D`/cmd `20` route in `Sources/EvenG2Shortcuts/G2FirmwareLogManager.swift:108-120`.

8. Navigation notify-back events are underused.
   Firmware sends view-changed and compass-changed notifications back on navigation service `0x08`, but the app currently only logs generic navigation responses. See `openCFW/src/platform/apollo510b/main_firmware/app/gui/navigation/navigation.c:2592-2668` and `Sources/EvenG2Shortcuts/G2BluetoothClient.swift:617-619`.

9. Translate is implemented, but still marked speculative by the app itself.
   See `Sources/EvenG2Shortcuts/G2TranslateSender.swift:11-15`. That is not proof it is wrong, but it is still lower-confidence than services like EvenAI, teleprompter, or settings.
