# Even G2 Protobuf Service Definitions (Android/Dart AOT Snapshot)

Extracted from the Even Android app's Dart AOT snapshot. Proto files are generated Dart files in `package:even_connect/g2/proto/generated/`. Service IDs cross-referenced against firmware dispatch table analysis (2026-03-03) and iOS Swift SDK implementation.

---

## Table of Contents

- [Service ID Map](#service-id-map)
- [Transport Layer](#transport-layer)
- [Service Definitions](#service-definitions)
  - [Dashboard (0x01-20)](#dashboard-0x01-20)
  - [Notifications (0x02-20)](#notifications-0x02-20)
  - [Menu (0x03-20)](#menu-0x03-20)
  - [Translate (0x05-20)](#translate-0x05-20)
  - [Teleprompter (0x06-20)](#teleprompter-0x06-20)
  - [EvenAI (0x07-20)](#evenai-0x07-20)
  - [Navigation (0x08-20)](#navigation-0x08-20)
  - [DeviceInfo (0x09-xx)](#deviceinfo-0x09-xx)
  - [SessionInit / DevPairManager (0x0A-20)](#sessioninit--devpairmanager-0x0a-20)
  - [Conversate (0x0B-20)](#conversate-0x0b-20)
  - [Quicklist + Health (0x0C-20)](#quicklist--health-0x0c-20)
  - [Configuration / Settings (0x0D-00/20)](#configuration--settings-0x0d-0020)
  - [DisplayConfig (0x0E-20)](#displayconfig-0x0e-20)
  - [Logger (0x0F-20)](#logger-0x0f-20)
  - [Onboarding (0x10-20)](#onboarding-0x10-20)
  - [ModuleConfigure (0x20-20)](#moduleconfigure-0x20-20)
  - [Auth (0x80-xx)](#auth-0x80-xx)
  - [BoxDetect / DisplayTrigger (0x81-20)](#boxdetect--displaytrigger-0x81-20)
  - [Ring (0x91-20)](#ring-0x91-20)
  - [FileTransfer (0xC4/0xC5)](#filetransfer-0xc40xc5)
  - [EvenHub (0xE0-20)](#evenhub-0xe0-20)
  - [SystemMonitor (0xFF-20)](#systemmonitor-0xff-20)
- [New Services (Not in iOS Analysis)](#new-services-not-in-ios-analysis)
  - [SyncInfo](#syncinfo)
  - [Transcribe](#transcribe)
- [OTA / DFU](#ota--dfu)
- [Shared Enums (common.pbenum.dart)](#shared-enums-commonpbenumdart)
- [Key Findings vs iOS Analysis](#key-findings-vs-ios-analysis)

---

## Service ID Map

| Service ID | Sub-ID | Name | Proto Source File | iOS Swift File |
|------------|--------|------|-------------------|----------------|
| 0x01 | 0x20 | Dashboard/Gesture | `dashboard.pb.dart` | `G2DashboardStateProtocol.swift` |
| 0x02 | 0x20 | Notifications | `notification.pb.dart` | `G2NotificationSender.swift` |
| 0x03 | 0x20 | Menu | `menu.pb.dart` | `G2MenuSender.swift` |
| 0x05 | 0x20 | Translate | `translate.pb.dart` | `G2TranslateSender.swift` |
| 0x06 | 0x20 | Teleprompter | `teleprompt.pb.dart` | `G2TeleprompterSender.swift` |
| 0x07 | 0x20 | EvenAI | `even_ai.pb.dart` | `G2EvenAISender.swift` |
| 0x08 | 0x20 | Navigation | `navigation.pb.dart` | `G2NavigationSender.swift` |
| 0x09 | 0x00/0x01 | DeviceInfo | `dev_infomation.pb.dart` | `G2ResponseDecoder.swift` |
| 0x0A | 0x20 | SessionInit | `dev_pair_manager.pb.dart` | `G2Session.swift` |
| 0x0B | 0x20 | Conversate | `conversate.pb.dart` | `G2ConversateSender.swift` |
| 0x0C | 0x20 | Quicklist + Health | `quicklist.pb.dart` + `health.pb.dart` | `G2TasksSender.swift` + `G2HealthDataSender.swift` |
| 0x0D | 0x00/0x20 | Configuration | `dev_settings.pb.dart` + `g2_setting.pb.dart` + `dev_config_protocol.pb.dart` | `G2ConfigurationReader.swift` |
| 0x0E | 0x20 | DisplayConfig | (part of `dev_config_protocol.pb.dart`) | `G2ResponseDecoder.swift` |
| 0x0F | 0x20 | Logger | `logger.pb.dart` | `G2LoggerSender.swift` |
| 0x10 | 0x20 | Onboarding | `onboarding.pb.dart` | `G2OnboardingSender.swift` |
| 0x20 | 0x20 | ModuleConfigure | `module_configure.pb.dart` | `G2ModuleConfigureProtocol.swift` |
| 0x80 | 0x00/0x01/0x02 | Auth | (not in proto; BLE transport layer) | `G2ConnectionHelper.swift` |
| 0x81 | 0x20 | BoxDetect/DisplayTrigger | `glasses_case.pb.dart` | `G2DisplayTriggerSender.swift` |
| 0x91 | 0x20 | Ring | `ring.pb.dart` | `G2ResponseDecoder.swift` |
| 0xC4/0xC5 | 0x00 | FileTransfer | `efs_transmit.pbenum.dart` | `G2FileTransferClient.swift` |
| 0xE0 | 0x20 | EvenHub | `EvenHub.pb.dart` | `G2EvenHubSender.swift` |
| 0xFF | 0x20 | SystemMonitor | (in `common.pbenum.dart`) | `G2SystemMonitorSender.swift` |

> **Note**: `dev_infomation.pb.dart` contains a typo in the original Android source (missing 'r' in "information").

---

## Transport Layer

The BLE transport is outside protobuf but defines how protobuf payloads are framed.

### Packet Format

```
AA [direction] [seq] [len] [total] [num] [svc_hi] [svc_lo] [payload] [CRC16-LE]
```

- `direction`: 0x21 (TX phone-to-glasses), 0x12 (RX glasses-to-phone)
- `len`: payload_size + 2 (includes 2-byte service ID)
- CRC16/CCITT: init=0xFFFF, poly=0x1021, over payload only (skip 8-byte header)
- Exception: Transport ACK packets are 8-byte header-only (no payload, no CRC)

### Dart Transport Classes

| Class | Role |
|-------|------|
| `EvenBleTransport` | Packet framing. Validates `headId` (0xAA), assembles header fields |
| `EvenBleMultiPacketItem` | Multi-packet assembly for payloads exceeding MTU |
| `BleG2CmdTransportPrivateExt` | Packet queue, split, retry logic, CRC computation |
| `BleDataPackage.fromServiceId` | Routes incoming packets to the correct protobuf decoder by service ID |

### BLE Profiles (BleG2PsType)

| Type | Profile | Characteristics | Purpose |
|------|---------|-----------------|---------|
| 0 | EUS (Even UART Service) | 0x5401 / 0x5402 | Protobuf control transport |
| 1 | EFS (Even File Service) | 0x7401 / 0x7402 | File transfer (OTA, images, audio) |
| 2 | ESS (Even Sensor Service) | 0x6401 / 0x6402 | Display telemetry (~20Hz, LFSR-scrambled) |

---

## Service Definitions

### Dashboard (0x01-20)

**Source**: `dashboard.pb.dart`

Manages the glasses home screen, widget layout, and gesture input routing.

#### Messages

| Message | Description |
|---------|-------------|
| `DashboardDataPackage` | Main wrapper for all dashboard commands |
| `DashboardContent` | Content payload for dashboard widgets |
| `DashboardDisplaySetting` | Display configuration (layout, brightness context) |
| `DashboardGeneralSetting` | General dashboard preferences |
| `DashboardMainPageState` | Current state of the main dashboard page |
| `DashboardMainWidgetMode` | Widget display mode selection |
| `DashboardMDFormat` | Markdown-like formatting for dashboard text |
| `DashboardReceiveFromApp` | Messages received by glasses FROM the phone app |
| `DashboardRespondToApp` | Response messages FROM glasses TO the phone app |
| `DashboardSendToApp` | Unsolicited messages FROM glasses TO the phone app |
| `DashboardReceiveFLAG` | Flag/state indicators for incoming dashboard data |

#### Protocol Notes

- Bidirectional: `ReceiveFromApp`, `RespondToApp`, and `SendToApp` form a three-way communication model. The glasses can both respond to commands and send unsolicited state updates.
- Gestures (tap, double-tap, slide) arrive on 0x01-01 as protobuf; long press arrives on 0x0D-01.

---

### Notifications (0x02-20)

**Source**: `notification.pb.dart`

Forwards phone notifications to glasses display.

#### Protocol Notes

- JSON key is `"android_notification"` even on iOS (firmware expects this exact key).
- Display activation is firmware-native: `efs_file_service` -> `SVC_ANDROID_ParseNotification()` -> `AsyncRequestDisplayStartUp(4,...)`. No host-side displayWake/displayConfig needed.
- Notification whitelist controls which apps are forwarded.

---

### Menu (0x03-20)

**Source**: `menu.pb.dart`

Controls the glasses on-device menu system.

#### Protocol Notes

- `G2MenuSender` manages display lifecycle plus `sendMenuInfo`/`sendDefaultMenu`.
- Response on 0x03-00 decoded by `G2MenuProtocol.parseResponse` -> yields type, appId, text.

---

### Translate (0x05-20)

**Source**: `translate.pb.dart`

Dedicated translation service. Separate from EvenAI (confirmed via firmware dispatch table).

#### Messages

| Message | Description |
|---------|-------------|
| `TranslateDataPackage` | Main wrapper (created via `_createTranscribeDataPackage` in Dart -- note the naming overlap) |

#### Protocol Notes

- Types 20-23 on 0x05-20.
- Response on 0x05-00: echo (f1=cmd_type) + COMM_RSP (f1=161, f12={f1=type}).
- The Dart factory function is named `_createTranscribeDataPackage` despite being for Translate, suggesting shared lineage with the Transcribe service.

---

### Teleprompter (0x06-20)

**Source**: `teleprompt.pb.dart`

Scrolling text display for speeches, scripts, presentations.

#### Messages

| Message | Description |
|---------|-------------|
| `TelepromptDataPackage` | Main wrapper for all teleprompter commands |
| `TelepromptControl` | Control commands (start, stop, pause, resume) |
| `TelepromptCtrlCmd` | Enum of control command types |
| `TelepromptCommandId` | Enum of command identifiers |
| `TelepromptCommResp` | Communication response / ACK |
| `TelepromptHeartBeat` | Teleprompter-specific keepalive |
| `TelepromptStatusNotify` | Status change notifications from glasses |
| `TelepromptErrorCode` | Error code enum |
| `TelepromptFileInfo` | Metadata for a single teleprompter file stored on glasses |
| `TelepromptFileList` | List of teleprompter files on glasses storage |
| `TelepromptFileListRequest` | Request to enumerate stored files |
| `TelepromptFileSelect` | Select a specific stored file for playback |
| `TelepromptScrollSync` | Scroll position synchronization between phone and glasses |
| `TelepromptTask` | Teleprompter session task definition |
| `TelepromptAISync` | AI-assisted teleprompter synchronization |
| `TelepromptMode` | Teleprompter operating mode enum |

#### Protocol Notes

- Response on 0x06-00: ACK with f1=166 (0xA6), f2=msgId, f12=empty.
- Progress on 0x06-01: scroll ticks with f1=0xA4, f2=msgId, f10={f1=pages}.
- Completion signal: f1=0xA1, f7={f1=4} (scroll-complete COMM_RSP).
- `TelepromptFileInfo`/`FileList`/`FileSelect` indicate the glasses can store teleprompter scripts locally and select them without phone involvement. This is not implemented in the iOS SDK.
- `TelepromptAISync` suggests AI-powered auto-scrolling or content synchronization.

---

### EvenAI (0x07-20)

**Source**: `even_ai.pb.dart`

AI assistant interface: voice commands, text queries, skill invocations.

#### Type Enum

| Value | Name | Description |
|-------|------|-------------|
| 0 | NONE | No operation |
| 1 | CTRL | Control command (enter/exit/wake) |
| 3 | ASK | User query |
| 4 | ANALYSE | Analysis request |
| 5 | REPLY | AI response text |
| 6 | SKILL | Skill invocation (brightness, auto-brightness, etc.) |
| 7 | PROMPT | Prompt/template |
| 8 | EVENT | Event notification |
| 9 | HB | Heartbeat |
| 10 | CONFIG | Configuration |
| 161 | COMM_RSP | Communication response (completion signal) |

#### Referenced Constants

- `EVEN_AI_ENTER` -- Enter AI mode
- `EVEN_AI_EXIT` -- Exit AI mode
- `EVEN_AI_WAKE_UP` -- Wake up AI from idle

#### Protocol Notes

- Response on 0x07-00: f1=2 is VAD (voice activity detection), f1=161 is completion (f12.f1=7 for AI, f12.f1=8 for EvenHub).
- Status on 0x07-01: mode status with f3={f1=2} entered, f3={f1=3} exited. Only EXIT generates a status notification.
- Echo pattern: glasses echo back with type+2.

---

### Navigation (0x08-20)

**Source**: `navigation.pb.dart`

Turn-by-turn navigation display on glasses.

#### Messages

| Message | Description |
|---------|-------------|
| `NavigationDataPackage` | Main wrapper (created via `_createNavigationDataPackage`) |

#### Protocol Notes

- State 7 = active navigation, state 2 = dashboard.
- 10 sub-commands, 36 icon types.
- Map tiles delivered via file transfer (BMP format).
- `G2NavigationFavorite` for favorite location list management.

---

### DeviceInfo (0x09-xx)

**Source**: `dev_infomation.pb.dart`

> Note: The filename contains a typo from the original Android source ("infomation" instead of "information").

Device identification, firmware version, hardware info queries.

#### Protocol Notes

- Query on 0x09-00, async response on 0x09-01.
- Also delivered on 0x04-01 (NotifyResponse) post-file-transfer.
- Long press gesture triggers proactive device info on 0x09-01.

---

### SessionInit / DevPairManager (0x0A-20)

**Source**: `dev_pair_manager.pb.dart`

Device pairing and session initialization.

#### Protocol Notes

- Handles initial connection handshake after auth completes.
- Session management (start, resume, end) for app-glasses communication.

---

### Conversate (0x0B-20)

**Source**: `conversate.pb.dart`

Live captioning / conversation transcription on glasses display.

#### Messages

| Message | Description |
|---------|-------------|
| `ConversateDataPackage` | Main wrapper for all conversate commands |
| `ConversateControl` | Control commands (start, pause, resume, close) |
| `ConversateCtrlCmd` | Enum: NONE=0, START=1, PAUSE=2, RESUME=3, CLOSE=4, CONFIG=5 |
| `ConversateCommandId` | Enum of command identifiers |
| `ConversateCommResp` | Communication response / ACK |
| `ConversateHeartBeat` | Conversate-specific keepalive |
| `ConversateSettings` | Session configuration (language, display options) |
| `ConversateStatusNotify` | Status change notifications from glasses |
| `ConversateKeypointData` | Key point extraction from conversation |
| `ConversateTagData` | Tag/label data for conversation segments |
| `ConversateTagTrackingData` | Tracking data for conversation tags over time |
| `ConversateTagType` | Enum of tag categories |
| `ConversateTitleData` | Title/header data for conversation sessions |
| `ConversateTranscribeData` | Raw transcription data from conversation |
| `ConversateErrorCode` | Error code enum |
| `ConversateActionCallback` | Callback for user actions during conversation |

#### Protocol Notes

- Response on 0x0B-00: ACK with f1=162 (0xA2), f2=msgId, f9=content status.
- Auto-close notification on 0x0B-01: f1=161, f2=msgId, f8={f1=2} = timeout.
- `magic_random` (f8={f1=counter}) is a firmware dedup counter. With it, f9={f1=1} on ALL ACKs; without it, init1 gets f9=empty.
- Text updates use type=5, 30-byte fixed-width, space-padded, with 0.6s delay between packets.
- **Rich data types not in iOS SDK**: `KeypointData`, `TagData`, `TagTrackingData`, `TitleData`, `TranscribeData` suggest the Android app supports structured conversation analysis features beyond plain captions.

---

### Quicklist + Health (0x0C-20)

**Source**: `quicklist.pb.dart` + `health.pb.dart`

Multiplexed service handling both quicklist (task) management and health data delivery.

#### Quicklist Messages

| Message | Description |
|---------|-------------|
| `QuicklistDataPackage` | Main wrapper (created via `_createQuickListDataPackage`) |

Quicklist CommandIDs: 1=fullUpdate, 2=batchAdd, 3=singleItem, 4=delete, 5=toggleComplete, 6=pagingRequest.

#### Health Messages

| Message | Description |
|---------|-------------|
| `HealthDataPackage` | Main wrapper for health data |
| `HealthDataPackage_CommandData` | Nested command data within health package |
| `HealthInfo` | Single health measurement |
| `HealthEnvelope` | Structured health data delivery container |
| `HealthMultData` | Multi-measurement health data batch |
| `HealthMultHighlight` | Highlighted/summary health metrics |
| `HealthModuleType` | Enum of health module categories |

Health CommandIDs: 10=query, 11=update, 12=configure (disjoint range from quicklist).

#### Health Module Types

| Type | Description |
|------|-------------|
| HEART_RATE | Heart rate BPM |
| BLOOD_OXYGEN | SpO2 percentage |
| TEMPERATURE | Body temperature |
| STEPS | Step count |
| CALORIES | Calorie burn |
| SLEEP | Sleep tracking data |
| PRODUCTIVITY | Productivity metrics |
| ACTIVITY_MISSING | Missing activity alert |

#### Protocol Notes

- `HealthEnvelope` and `HealthMultHighlight` are richer than the iOS SDK implementation, which uses flat data types. These suggest the Android app can display structured health summaries with highlighted key metrics.

---

### Configuration / Settings (0x0D-00/20)

**Source**: `dev_settings.pb.dart` + `g2_setting.pb.dart` + `dev_config_protocol.pb.dart`

Device configuration, user preferences, and display mode management.

#### Messages

| Message | Description |
|---------|-------------|
| `G2SettingPackage` | Main settings wrapper (protobuf on 0x0D-00) |

#### Config Mode Values

| Mode | Value | Description |
|------|-------|-------------|
| DASHBOARD | 1 | Home screen |
| RENDER | 6 | Active rendering |
| CONVERSATE | 11 | Conversation mode |
| TELEPROMPTER | 16 | Teleprompter mode |

Sub-modes: f2=7 for EvenAI overlay (on Dashboard), f2=33 for Teleprompter rendering state.

#### Protocol Notes

- `G2SettingPackage` is the protobuf envelope for settings on 0x0D-00. G1-style raw bytes (`[0x01, level, auto]`) do NOT work on G2.
- Brightness is delivered via protobuf fields, not raw DAC values.
- `magic_random` (f8) is used as a firmware dedup counter for settings commands.
- Config query on 0x0D-00 with empty payload returns 0 fields (glasses ignore bare queries).
- Settings cmdIds 30, 31, 39, 40 are confirmed false positives (coincidental heartbeat echoes).

#### Sub-protocols on 0x0D

| Reader/Protocol | Fields | Direction |
|-----------------|--------|-----------|
| `G2GlassesCaseReader` | soc, charging, lidOpen, inCase | RX |
| `G2UniversalSettingsReader` | metricUnit, dateFormat, distanceUnit, temperatureUnit, timeFormat, dominantHand | RX |
| `G2GlassesSettingsProtocol` | silentMode, screenOffInterval (15s/30s/1m/2m/5m/never) | RX/TX |
| `G2WearDetectionProtocol` | enabled, isWearing | RX |
| `G2CompassCalibration` | heading, calibrateStatus, compassMsg | RX |
| `G2GestureControlListProtocol` | gesture-to-action mappings (6 gesture types, 9 action types) | RX/TX |

---

### DisplayConfig (0x0E-20)

**Source**: Part of `dev_config_protocol.pb.dart`

Display region configuration for active rendering modes.

#### Protocol Notes

- 6 display regions, write-only from phone to glasses.
- Required ONLY for Teleprompter mode. Other features use firmware-native display activation.
- Display: 576x288 Gray4, monoscopic. Inter-eye communication via wired UART.

---

### Logger (0x0F-20)

**Source**: `logger.pb.dart`

Firmware log management and retrieval.

#### Messages

| Message | Description |
|---------|-------------|
| `LoggerDataPackage` | Main wrapper (created via `_createLoggerDataPackage`) |

#### Protocol Notes

- 12 log files available on glasses.
- 5 log levels.
- Live streaming toggle for real-time log output.
- Response on 0x0F-00 decoded by `G2LoggerProtocol.parseResponse` -> type, fileList.

---

### Onboarding (0x10-20)

**Source**: `onboarding.pb.dart`

First-time setup, head-up display calibration, wear detection initialization.

#### Messages

| Message | Description |
|---------|-------------|
| `OnboardingDataPackage` | Main wrapper (created via `_createOnboardingDataPackage`) |

#### Protocol Notes

- 7 onboarding states.
- Commands: `sendStartUp`, `sendStart`, `sendEnd`, `queryHeadUpStatus`.
- Response on 0x10-00 decoded by `G2OnboardingProtocol.parseBLEResponse` -> flag/wearStatus based on f1.

---

### ModuleConfigure (0x20-20)

**Source**: `module_configure.pb.dart`

Per-module configuration including per-eye brightness calibration.

#### Messages

| Message | Description |
|---------|-------------|
| `ModuleConfigureDataPackage` | Main wrapper (created via `_createModuleConfigureDataPackage`) |

#### Protocol Notes

- 4 command types.
- Per-eye brightness calibration via `leftMaxBrightness` / `rightMaxBrightness`.
- Response on 0x20-00.
- Legacy name in codebase: "Commit".

---

### Auth (0x80-xx)

**Source**: Not in protobuf definitions; handled in BLE transport layer.

Authentication is raw binary, not protobuf-encoded.

#### Protocol Notes

- 7-packet full auth sequence on 0x80-00/0x80-20.
- Glasses respond in ~51ms; handler MUST be registered before first TX.
- Auth success: f1=4, f3={f1=1} on 0x80-01. Both eyes echo independently (50-100ms apart).
- Keepalive (heartbeat): ONLY type 0x0E is valid. Types 0x0D and 0x0F cause **pairing removal**.
- Time sync: f128={f1=Unix timestamp, f3=timezone offset}.
- Glasses maintain their own sequence counter (RX seqs != TX seqs).

---

### BoxDetect / DisplayTrigger (0x81-20)

**Source**: `glasses_case.pb.dart`

Glasses case detection, lid state, case battery monitoring.

#### Messages

| Message | Description |
|---------|-------------|
| `GlassesCaseDataPackage` | Main wrapper for case-related data |
| `GlassesCaseInfo` | Case state information (battery, lid, charging) |

#### Protocol Notes

- DisplayTrigger f3.f1=77 consistently maps to case battery SOC (state of charge).
- Shares the ProtoBaseSettings multiplex on 0x0D for case state reads.

---

### Ring (0x91-20)

**Source**: `ring.pb.dart`

R1 Ring relay protocol over G2 glasses BLE.

#### Messages

| Message | Description |
|---------|-------------|
| `RingDataPackage` | Main wrapper (created via `_createRingDataPackage`) |

#### Protocol Notes

- R1 Ring has its own BLE service (BAE80001...) but can also be relayed through the glasses on 0x91-20.
- Ring init: write 0xFC, 200ms delay, write 0x11. Keepalive: 0x11 every 5s.
- Response on 0x91-00: `G2RingRelayResponse` (type, messageId, payload).

---

### FileTransfer (0xC4/0xC5)

**Source**: `efs_transmit.pbenum.dart`

File transfer protocol on the EFS (Even File Service) BLE profile.

#### Protocol Notes

- Uses characteristics 0x7401 (TX) / 0x7402 (RX), separate from EUS control channel.
- Non-protobuf: 2-byte LE status word in ACK packets.
- Status codes: 0=fileCheckOK, 1=dataReceived, 2=transferComplete, 3+=error.
- Used for: BMP images (navigation maps, notifications), OTA firmware, teleprompter files, audio data.

---

### EvenHub (0xE0-20)

**Source**: `EvenHub.pb.dart`

EvenHub app framework for third-party/first-party mini-apps on the glasses display.

#### Messages

| Message | Description |
|---------|-------------|
| `BleEvenHubEvent` | Hub event wrapper |

#### Protocol Notes

- Container protobuf fields follow nanopb struct order (NOT SDK JSON order). This was a critical fix (2026-03-09).
- Startup requires cleaning up overlays: EvenAI (sub=7), Conversate (mode=11), Teleprompter (mode=16) before `CreateStartUp`.
- Completion signal on 0x07-00: f1=161, f12.f1=8 indicates EvenHub (vs f12.f1=7 for AI).

---

### SystemMonitor (0xFF-20)

**Source**: Referenced in `common.pbenum.dart`

System-level event monitoring and diagnostics.

#### Protocol Notes

- 6 event types.
- Response on 0xFF-00 decoded by `G2SystemMonitorProtocol.parseResponse`.

---

## New Services (Not in iOS Analysis)

### SyncInfo

**Source**: `sync_info.pb.dart`

A previously unidentified service for state synchronization. Not present in the iOS Swift SDK or firmware dispatch table analysis.

#### Open Questions

- Service ID assignment is unknown (not in the 0x01-0xFF dispatch table from firmware RE).
- May be a phone-side-only construct for syncing state between app and cloud.
- May correspond to one of the unidentified firmware handler slots.

---

### Transcribe

**Source**: `transcribe.pb.dart`

A dedicated BLE transcription service, separate from EvenAI and Conversate.

#### Open Questions

- Service ID assignment is unknown.
- Distinct from Conversate (0x0B-20) which also handles transcription via `ConversateTranscribeData`.
- Distinct from EvenAI (0x07-20) which handles voice input.
- May share the Translate service's factory function (Dart uses `_createTranscribeDataPackage` for Translate), suggesting possible service ID sharing or evolution from Translate.
- Could be a newer service added in firmware versions beyond v2.0.7.16.

---

## OTA / DFU

Firmware update protocol extracted from the Dart snapshot. Not a protobuf service per se, but uses structured binary headers.

### OTA Messages

| Type | Description |
|------|-------------|
| `BleG2OtaHeader` | OTA packet header with `otaMagic1`, `otaMagic2` validation fields |
| `BleG2OtaEvent` | OTA state machine events |
| `BleG2OtaDevice` | Target device identification for OTA |
| `EvenOtaComponentInfo` | Component metadata within EVENOTA container (fromBytes parser) |
| `EvenOtaUpgradeCmd` | Upgrade command types |

### DFU Messages (Nordic)

| Type | Description |
|------|-------------|
| `DfuUpgrade` | DFU upgrade session |
| `DfuUpgradeState` | DFU state machine |
| `DfuUpgradeType` | DFU target type (softdevice, bootloader, application) |

### Firmware Update Infrastructure

| Type | Description |
|------|-------------|
| `FirmwareUpdateManager` | Orchestrates the full update flow |
| `FirmwareUpdateMode` | Update mode selection (full, component, DFU) |
| `FirmwareUpdateLogger` | Update-specific logging |

### OTA Wire Format

- 4-phase protocol: START -> INFORMATION -> FILE -> RESULT_CHECK
- FILE packets: 5-byte header + 1000-byte payload + CRC at byte offset 1005
- EVENOTA container: 6-entry firmware bundle (BLE EM9305, Box MCU, Codec GX8002B, Touch CY8C4046FNI, S200 bootloader, S200 firmware OTA)

---

## Shared Enums (common.pbenum.dart)

Shared enumerations used across multiple services.

### Known Shared Types

- **COMM_RSP** (value 161/0xA1): Bidirectional communication response. Used by EvenAI, Conversate, Teleprompter, Translate, and SystemMonitor. When the phone sends it, glasses respond with cleanup actions.
- **Service IDs**: Defined in `service_id_def.pbenum.dart`.
- **BleG2PsType**: BLE profile selector (0=EUS, 1=EFS, 2=ESS).

---

## Key Findings vs iOS Analysis

### 1. Conversate Has Rich Structured Data Types

The Android proto defines `ConversateKeypointData`, `ConversateTagData`, `ConversateTagTrackingData`, `ConversateTitleData`, and `ConversateTranscribeData`. The iOS SDK currently implements only plain text captions (type=5, 30-byte fixed-width). These types suggest:

- **Key point extraction**: Automatic summarization of conversation highlights.
- **Tag tracking**: Labeling and tracking conversation topics over time.
- **Structured transcription**: Richer than raw text, possibly with speaker identification or confidence scores.

### 2. Teleprompter Has On-Glasses File Management

`TelepromptFileInfo`, `TelepromptFileList`, `TelepromptFileListRequest`, and `TelepromptFileSelect` indicate the glasses can store teleprompter scripts locally. The iOS SDK sends text inline via BLE on every session. Local storage would allow:

- Offline teleprompter playback without phone connection.
- Faster session startup (select stored file vs. transmit full text).
- `TelepromptAISync` for AI-assisted scroll pacing.

### 3. Health Has Structured Envelopes

`HealthEnvelope` and `HealthMultHighlight` go beyond flat key-value health data. The iOS SDK uses simple data types per `HealthModuleType`. The envelope/highlight pattern suggests:

- Batched multi-metric health summaries.
- Highlighted/prioritized metrics for at-a-glance display.

### 4. SyncInfo Is a New Unidentified Service

`sync_info.pb.dart` has no corresponding service ID in the firmware dispatch table. It may be:

- A cloud-sync mechanism (not BLE).
- A planned future service.
- Mapped to an unidentified firmware handler slot.

### 5. Transcribe Is a Dedicated BLE Service

`transcribe.pb.dart` is separate from both Conversate and EvenAI transcription. The naming overlap with Translate's factory function (`_createTranscribeDataPackage`) suggests possible evolution from or sharing with the Translate service.

### 6. Dashboard Is Fully Bidirectional

`DashboardReceiveFromApp`, `DashboardRespondToApp`, and `DashboardSendToApp` form a three-way communication model. The iOS SDK treats Dashboard (0x01-20) primarily as gesture input. The Android proto reveals the glasses can also:

- Send unsolicited dashboard state updates to the phone.
- Respond to dashboard configuration commands with structured acknowledgments.
