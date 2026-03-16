# Even.app Reverse Engineering Findings

Date: 2026-03-02

## App Architecture

The Even Realities iOS app (bundle ID: `com.even.sg`, version 2.0.7 build 394) is a **Flutter application** with native Swift framework bridges.

**URL Scheme**: `evenG2://`

### Architecture Layers

```
┌─────────────────────────────────────────────────┐
│  Flutter UI (Dart)                              │
├─────────────────────────────────────────────────┤
│  package:even_connect (Dart)                    │
│    └─ g2/, g1/, ring1/ protocol layers          │
│    └─ g2/proto/generated/ (28 protobuf modules) │
├─────────────────────────────────────────────────┤
│  Native Bridges (Swift Frameworks)              │
│    ├─ flutter_ezw_ble   (CoreBluetooth)         │
│    ├─ flutter_ezw_lc3   (LC3 codec FFI)         │
│    ├─ flutter_ezw_asr   (Azure Speech)          │
│    ├─ even_core          (permissions, bg)      │
│    ├─ even               (ONNX, llama.cpp)      │
│    ├─ teleprompt          (Apple SFSpeech)      │
│    ├─ translate           (Azure Translation)   │
│    └─ dashboard           (EventKit calendar)   │
├─────────────────────────────────────────────────┤
│  3rd Party                                      │
│    ├─ SwiftProtobuf                             │
│    ├─ MicrosoftCognitiveServicesSpeech          │
│    ├─ MapboxNavigationNative                    │
│    ├─ iOSMcuManagerLibrary (Nordic DFU)         │
│    └─ sherpa_onnx (on-device ASR)               │
└─────────────────────────────────────────────────┘
```

**Key insight**: ALL protocol logic lives in Dart (`package:even_connect`), not in native frameworks. Native frameworks are thin bridges to iOS APIs.

### Framework Analysis

| Framework | Purpose | Content |
|---|---|---|
| `flutter_ezw_ble` | BLE bridge | CoreBluetooth wrapper, 466 strings |
| `flutter_ezw_lc3` | Audio codec | LC3 decode FFI (72 symbols), no encode |
| `flutter_ezw_asr` | Cloud ASR | Azure SPXSpeechRecognizer bridge |
| `flutter_ezw_audio` | Audio | Empty stub |
| `flutter_ezw_utop` | Unknown | Empty stub |
| `even_core` | Utilities | Permissions, background keep-alive, device info |
| `even` | On-device ML | ONNX Runtime + llama.cpp + sherpa-onnx + protobuf |
| `even_ui` | UI components | Flutter UI framework |
| `teleprompt` | On-device ASR | Apple SFSpeechRecognizer, receives PCM via audioDataChannel |
| `translate` | Cloud translation | Azure SPXTranslationRecognizer |
| `dashboard` | Calendar | EventKit calendar event access |
| `conversate` | Conversate | Nearly empty stub (logic in Dart) |
| `App.framework` | Compiled Dart | ALL protocol logic, 93,254 strings |

---

## Hardware Identification

> **CORRECTION (2026-03-03)**: The G2 main SoC is **Ambiq Micro Apollo510b**, NOT Nordic nRF52840. The nRF52840/S140 identification below was derived from DFU bootloader firmware bundled in the Even.app — this applies to an auxiliary update path (possibly R1 Ring or EM9305 BLE radio DFU), not the G2 runtime processor. See [firmware-reverse-engineering.md](firmware-reverse-engineering.md) §1 for the corrected hardware BOM.

### G2 Runtime Hardware (Confirmed from OTA Firmware)

| Property | Value | Confidence |
|---|---|---|
| **Main SoC** | Ambiq Micro Apollo510b | **CONFIRMED** |
| **CPU** | ARM Cortex-M55 (512 KB SRAM) | CONFIRMED |
| **BLE Radio** | EM9305 (EM Microelectronic) + Cordio host stack | CONFIRMED |
| **Board Revision** | B210 | HIGH |
| **Hardware Model** | S200 (GATT Device Information) | HIGH |
| **Consumer Name** | G2 | HIGH |

### DFU Bootloader Components (Legacy/Auxiliary)

The following was identified from Nordic DFU packages bundled in Even.app. These apply to the DFU bootloader path, not the G2 main runtime:

| Property | Value | Confidence |
|---|---|---|
| SoC | Nordic nRF52840 (bootloader at 0xF0000 requires 1MB flash) | HIGH |
| CPU | ARM Cortex-M55 with Helium MVE | HIGH |
| Flash | 1 MB (0x00000000 – 0x000FFFFF) | HIGH |
| RAM | 256 KB (0x20000000 – 0x2003FFFF) | MEDIUM |
| BLE Stack | SoftDevice S140 v7.0.0 (FWID 0x0100) | HIGH |
| DFU Advert Name | B210_DFU | HIGH |
| DFU Signing | ECDSA P-256 (secp256r1) | HIGH |

### DFU Bootloader Memory Map (Legacy)

```
Flash (1 MB) — nRF52840 DFU bootloader layout:
  0x00000000 - 0x00000FFF: MBR (Master Boot Record, 4 KB)
  0x00001000 - 0x00026FFF: SoftDevice S140 v7.0.0 (~153 KB)
  0x00027000 - 0x000F7FFF: Application firmware (~836 KB) [NOT EXTRACTED]
  0x000F8000 - 0x000FDFFF: Bootloader (~24 KB)
  0x000FE000 - 0x000FEFFF: Bootloader settings (4 KB)
  0x000FF000 - 0x000FFFFF: MBR parameters (4 KB)
```

### DFU Verification Key (ECDSA P-256)

Extracted from bootloader binary (both ALWAY and v2.0.3 contain identical key):

```
X: 7a7de304b95ede3310178189bdf9828b9149b5acdcc6365e3fb7b58b4456119d
Y: 553442c9df04a6a417e55b8184501a30813e7f3c6395f1f66dd747c49f0fa398
Uncompressed: 04 7a7de304...119d 553442c9...a398
```

Uses micro-ecc library with full P-256 curve constants (p, n, generator G) embedded adjacent to the key.

### Firmware Packages

Three DFU packages are bundled as Flutter assets in the Even.app:

| Package | Type | Size | is_debug | sd_req (FWIDs) |
|---|---|---|---|---|
| `B210_ALWAY_BL_DFU_NO.zip` | Bootloader (fail-safe) | 24,180 bytes | **TRUE** | 0x0100 + 0x0102 |
| `B210_BL_DFU_NO_v2.0.3.0004.zip` | Bootloader (versioned) | 24,420 bytes | **TRUE** | 0x0100 + 0x0102 |
| `B210_SD_ONLY_NO_v2.0.3.0004.zip` | SoftDevice | 153,140 bytes | FALSE | 0x0100 + 0x0102 |

Both bootloaders are debug builds (easier recovery); the SoftDevice is production. The "ALWAY" bootloader is a stripped-down fail-safe with 240 fewer bytes but identical DFU signing key and vector table. Both accept dual SoftDevice versions (S140 v7.0.0 via FWID 0x0100, OR S140 v7.2.0 via FWID 0x0102) enabling field upgrades.

### SoftDevice Info Struct (at 0x2000) — DFU Bootloader Path

| Field | Value |
|---|---|
| Magic | `0xFFFFFF2C` (valid SoftDevice marker) |
| SD Size / APP_CODE_BASE | `0x00027000` (156 KB) |
| SD FWID | `0x0100` |
| BLE API Version | `0x8C` (140) |

### BLE Capabilities (from SVC Analysis — DFU SoftDevice)

Note: These capabilities are from the S140 SoftDevice in the DFU bootloader path. The G2 runtime uses EM9305 + Cordio host stack, which has its own capability set.

46 unique SVC numbers in the SoftDevice confirm support for:
- **PHY Update** (1M, 2M, Coded PHY)
- **Data Length Extension** (up to 251 bytes PDU)
- **L2CAP Connection-Oriented Channels**
- **Extended Advertising**
- **TX Power Control**
- **LE Secure Connections** with ECDH
- **Vendor-Specific UUIDs**
- **AES-CCM/ECB** encryption
- **Flash** read/write/erase

### Device Variants

The G2 comes in two hardware variants and three colors:
- **G2 A** — Brown, Green, Grey
- **G2 B** — Brown, Green, Grey

---

## Complete BLE UUID Family

Base UUID: `00002760-08C2-11E1-9073-0E8AC72Exxxx`

| Suffix | Role | Status |
|---|---|---|
| `0001` | Service discovery | Known |
| `0002` | Service discovery | Known |
| `1001` | Unknown (possibly OTA) | **NEW** |
| `5401` | Control TX (phone→glasses write) | Known |
| `5402` | Control RX (glasses→phone notify) | Known |
| `5450` | Control alternate | **NEW** |
| `6401` | Display TX (phone→glasses write) | Known |
| `6402` | Display RX (glasses→phone notify) | Known |
| `6450` | Display alternate | **NEW** |
| `7401` | File TX (phone→glasses write) | Known |
| `7402` | File RX (glasses→phone notify) | Known |
| `7450` | File alternate | **NEW** |

### Private Service Types (BleG2PsType)

```
Type 0 = Basic/Control (characteristics 5401/5402)
Type 1 = File (characteristics 7401/7402)
Type 2 = Display (characteristics 6401/6402)
```

### R1 Ring Characteristics (Confirmed)

| UUID | Role |
|---|---|
| BAE80001-... | Ring Service |
| BAE80012-... | Ring TX (phone→ring write) |
| BAE80013-... | Ring RX (ring→phone notify) |
| FE59 | Nordic Buttonless Secure DFU (BLE SIG registered UUID, discovered via service scan 2026-03-02) |
| DA2E7828-... | SMP/MCUmgr (Nordic DFU data transfer) |

---

## Complete Protobuf Service Map (28 Modules)

From `package:even_connect/g2/proto/generated/` — with library IDs from AOT binary analysis:

| Module | Library ID | Data Package Class | Top-Level Messages | Our Status |
|---|---|---|---|---|
| `common` | (shared) | — | Common types | Implemented |
| `service_id_def` | (enum) | — | `ServiceIdDef` enum | Implemented (ProtocolConstants) |
| `g2_setting` | @1414153617 | `G2SettingPackage` | 18 messages (see below) | Partial |
| `dev_settings` | @1411012352 | — | `BaseConnHeartBeat`, `TimeSync`, `AudControl`, `QuickRestart`, `RestoreFactory` | Implemented (auth) |
| `dev_config_protocol` | @1410360820 | `DevCfgDataPackage` | `DevCfgCmdException` | Partial (brightness) |
| `dev_infomation` | @2347168945 | — | `DeviceInfo`, `DeviceInfoValue`, `BleMac`, `SnInfo`, `ALSInfo`, `HeadAngle`, `Mode` | Implemented |
| `dev_pair_manager` | @2395051248 | — | `AuthMgr`, `BleConnectParam`, `DisconnectInfo`, `PipeRoleChange`, `RingInfo`, `UnpairInfo` | Implemented |
| `module_configure` | @1416454984 | — | `module_configure_main_msg_ctx`, `dashboard_general_setting`, `send_system_general_setting` | **NOT IMPLEMENTED** |
| `teleprompt` | @1443303095 | `TelepromptDataPackage` | `TelepromptControl`, `TelepromptFileList`, `TelepromptFileInfo`, `TelepromptFileSelect`, `TelepromptPageData`, `TelepromptScrollSync`, `TelepromptAISync`, `TelepromptHeartBeat`, `TelepromptStatusNotify`, `TelepromptCommResp`, `TelepromptSetting` | Implemented |
| `conversate` | @1922268313 | `ConversateDataPackage` | `ConversateControl`, `ConversateSettings`, `ConversateHeartBeat`, `ConversateCommResp`, `ConversateStatusNotify`, `ConversateTranscribeData`, `ConversateKeypointData`, `ConversateTagData`, `ConversateTagTrackingData`, `ConversateTitleData` | Implemented |
| `even_ai` | @1407414150 | `EvenAIDataPackage` | `EvenAIControl`, `EvenAIConfig`, `EvenAIHeartbeat`, `EvenAIEvent`, `EvenAICommRsp`, `EvenAIReplyInfo`, `EvenAIAskInfo`, `EvenAIAnalyseInfo`, `EvenAIPromptInfo`, `EvenAISkillInfo`, `EvenAIVADInfo` | Implemented |
| `EvenHub` | @2397181980 | via `evenhub_main_msg_ctx` | `CreateStartUpPageContainer`, `RebuildPageContainer`, `ShutDownContaniner`, `TextContainerUpgrade`, `ImageRawDataUpdate`, `HeartBeatPacket`, `AudioCtrCmd`, `AudioResCmd`, + container/response/event types | Implemented |
| `navigation` | @1428067439 | via `navigation_main_msg_ctx` | `basic_info_msg`, `view_info_msg`, `extend_info_msg`, `mini_map_msg`, `max_map_msg`, `compass_info_msg`, `LocationList_msg`, `os_select_location_msg` | Partial (2 of 10 subcmds) |
| `notification` | @1430261884 | `NotificationDataPackage` | `NotificationControl`, `NotificationIOS`, `NotificationWhitelistCtrl`, `NotificationCommRsp` | Implemented (file-only) |
| `dashboard` | @1419512574 | `DashboardDataPackage` | `DashboardSendToApp`, `DashboardReceiveFromApp`, `DashboardRespondToApp`, `AppRespondToDashboard`, `DashboardContent`, `DashboardDisplaySetting`, `DashboardMainPageState`, `AppRequest`, `News`, `Schedule`, `Stock` | **NOT IMPLEMENTED** |
| `menu` | @1632267984 | via `meun_main_msg_ctx` | `MenuInfoSend`, `Menu_Item_Ctx`, `ResponseMenuInfo` | **NOT IMPLEMENTED** |
| `quicklist` | @1436323404 | `QuicklistDataPackage` | `QuicklistItem`, `QuicklistMultItems`, `QuicklistEvent` | **NOT IMPLEMENTED** |
| `health` | @1421255604 | `HealthDataPackage` | `HealthSingleData`, `HealthSingleHighlight`, `HealthMultData`, `HealthMultHighlight` | **NOT IMPLEMENTED** |
| `glasses_case` | @1415496902 | `GlassesCaseDataPackage` | `GlassesCaseInfo` | **NOT IMPLEMENTED** |
| `ring` | @1438371976 | `RingDataPackage` | `RingRawData`, `RingEvent` | Partial (gestures only) |
| `onboarding` | @1417321442 | `OnboardingDataPackage` | `OnboardingConfig`, `OnboardingEvent`, `OnboardingHeartbeat` | **NOT IMPLEMENTED** |
| `sync_info` | @1440088238 | via `sync_info_main_msg_ctx` | `sync_info_data_msg` | **NOT IMPLEMENTED** |
| `logger` | @1423103636 | via `logger_main_msg_ctx` | `ble_trans_level_msg`, `request_filelist_msg`, `delete_file_msg` | **NOT IMPLEMENTED** |
| `efs_transmit` | (enum) | — | File transmit enums | Partial (notifications) |
| `ota_transmit` | (enum) | — | OTA transmit enums | **NOT IMPLEMENTED** |
| `transcribe` | @2396442198 | `TranscribeDataPackage` | `TranscribeControl`, `TranscribeResult`, `TranscribeHeartBeat`, `TranscribeNotify`, `TranscribeResp` | **NOT IMPLEMENTED** |
| `translate` | @1450417037 | `TranslateDataPackage` | `TranslateControl`, `TranslateResult`, `TranslateHeartBeat`, `TranslateNotify`, `TranslateResp`, `TranslateModeSwitch` | **NOT IMPLEMENTED** |
| `g2_setting` | @1414153617 | (same as above) | — | — |

**Gap**: We implement 10 of 28 protobuf modules. 18 are not implemented (including 2 enum-only modules).

### G2SettingPackage Protobuf Types (from g2_setting.pb.dart @1414153617)

The G2 settings module contains 20 protobuf message types for device configuration:

**App → Device (commands):**
- `APP_Send_Dominant_Hand` — Set dominant hand (left/right)
- `APP_Send_Gesture_Control` — Single gesture mapping
- `APP_Send_Gesture_Control_List` — Full gesture control list
- `APP_Send_Universe_Setting` — Universal settings

**Device → App (responses/pushes):**
- `DeviceReceive_Brightness` — Glasses push brightness back to app
- `DeviceReceive_Head_UP_Setting` — Head-up display settings
- `DeviceReceive_Silent_Mode_Setting` — Silent mode state
- `DeviceReceive_X_Coordinate` — X coordinate from glasses
- `DeviceReceive_Y_Coordinate` — Y coordinate from glasses
- `DeviceReceive_Advanced_Setting` — Advanced settings
- `DeviceReceive_APP_PAGE` — App page state
- `Wear_Detection_Setting` — Wear detection state

**Bidirectional wrappers:**
- `G2SettingPackage` — Outer packet wrapper
- `DeviceReceiveInfoFromAPP` — Info flow from app to device
- `DeviceReceiveRequestFromAPP` — Request flow from app
- `DeviceSendInfoToAPP` — Info flow from device to app
- `App_Respond_To_Device` — App response to device query
- `Device_Respond_To_App` — Device response to app query

**Response codes:**
- `Device_Respond_Flag` — Response flag field
- `DEVICE_RESPOND_SUCCESS` — Success code
- `DEVICE_RESPOND_PARAMETER_ERROR` — Parameter error code
- `INVALID_SERVICE_ID` — Invalid service sentinel

### g2_settingCommandId Enum (complete — RE 2026-03-01)

These are the command type discriminators within `G2SettingPackage`:

| Command | Direction | Purpose |
|---------|-----------|---------|
| `APP_REQUIRE_BASIC_SETTING` | TX | Request current settings |
| `APP_REQUIRE_BRIGHTNESS_INFO` | TX | Request brightness info |
| `APP_SEND_BASIC_INFO` | TX | Send basic settings |
| `APP_SEND_HEARTBEAT_CMD` | TX | Settings heartbeat |
| `APP_SEND_MENU_INFO` | TX | Send menu configuration |
| `APP_SEND_MAX_MAP_FILE` | TX | Send overview map file |
| `APP_SNED_MINI_MAP_FILE` | TX | Send mini map file (note typo: SNED) |
| `APP_SET_DASHBOARD_AUTO_CLOSE_VALUE` | TX | Set dashboard auto-close timer |
| `APP_INQUIRE_DASHBOARD_AUTO_CLOSE_VALUE` | TX | Query dashboard auto-close timer |
| `APP_SEND_ERROR_INFO_MSG` | TX | Send error information |
| `SET_DEVICE_INFO` | TX | Set device information |
| `GET_DEVICE_INFO` | TX | Get device information |
| `DEVICE_BRIGHTNESS` | RX | Brightness acknowledgment |
| `DEVICE_DISPLAY_MODE` | TX/RX | Display mode (dual/full/minimal) |
| `DEVICE_WORK_MODE` | TX/RX | Work mode setting |
| `DEVICE_ANTI_SHAKE_ENABLE` | TX | Anti-shake toggle |
| `DEVICE_WAKEUP_ANGLE` | TX | Wake-up tilt angle |
| `DEVICE_BLE_MAC` | RX | Device BLE MAC address |
| `DEVICE_GLASSES_SN` | RX | Glasses serial number |
| `DEVICE_DEVICE_SN` | RX | Device serial number |
| `DEVICE_SEND_LOGGER_DATA` | RX | Logger data from glasses |
| `DEVICE_RESPOND_SUCCESS` | RX | Success response |
| `DEVICE_RESPOND_PARAMETER_ERROR` | RX | Parameter error response |

**Note**: The `APP_SNED_MINI_MAP_FILE` typo is in the original Even.app source code.

### ProtoBaseSettings Method Map (complete — RE 2026-03-01)

All methods in `package:even/common/extension/proto/proto_base_settings.dart`:

| Method | Purpose | Log String |
|--------|---------|------------|
| `setBrightness` | Set brightness level | `"setBrightness ="` |
| `setBrightnessAuto` | Toggle auto-brightness | `"setBrightnessAuto "` |
| `setBrightnessCalibration` | Per-eye calibration | `"setBrightnessCalibration left="` |
| `setGlassGridDistance` | Set grid X distance | via `DisplaySettingsExt|setGridDistance` |
| `setGlassGridHeight` | Set grid Y height | via `DisplaySettingsExt|setGridHeight2` |
| `headUpSetting` | Head-up angle/switch/trigger | Multiple fields |
| `setSilentMode` | Silent mode toggle | `"setSilentMode="` |
| `setWearDetection` | Wear detection toggle | — |
| `setOnBoardingStart` | Start onboarding | — |
| `setOnBoardingStartUp` | Trigger onboarding startup | — |
| `setOnBoardingEnd` | End onboarding | — |
| `requestScreenOffInterval` | Query auto screen-off | — |
| `updateScreenOffInterval` | Set auto screen-off | — |
| `setGestureControlList` | Configure gestures | `"setGestureControlList count="` |
| `getGlassesConfig` | Get current config | Returns: brightness, gridDistance, gridHeight, headUpAngle, wearDetection, workMode |
| `getGlassesIsWear` | Query wear status | — |
| `getOnGlassesWear` | Wear status callback | — |
| `getBoardingIsHeadup` | Check onboarding head-up | — |
| `getGlassesCaseInfo` | Case/charging info | — |
| `sendSysLanguageChangeEvent` | Sync language | — |

### Brightness: Two Paths

**Path 1 — ProtoBaseSettings (g2_setting proto on 0x0D-00):**
`ProtoBaseSettings.setBrightness(level)` → `G2SettingPackage{commandId=DEVICE_BRIGHTNESS, deviceReceiveBrightness=DeviceReceive_Brightness{brightnessLevel}}` → `sendDataPackage2`

**Path 2 — EvenAI Skill (even_ai proto on 0x07-20):**
`ProtoAiExt.sendSkillBrightness(param)` → `EvenAIDataPackage{commandId=SKILL, skillInfo=EvenAISkillInfo{skillId=0}}` → `sendDataPackage2`

---

## UI Application IDs (Glasses OS)

These are the registered app IDs on the G2 operating system:

| App ID | Function |
|---|---|
| `UI_DEFAULT_APP_ID` | Default/home |
| `UI_TELEPROMPT_APP_ID` | Teleprompter |
| `UI_CONVERSATE_APP_ID` | Conversate |
| `UI_TRANSLATE_APP_ID` | Translation |
| `UI_TRANSCRIBE_APP_ID` | Transcription |
| `UI_QUICKLIST_APP_ID` | Quick list |
| `UI_HEALTH_APP_ID` | Health |
| `UI_ONBOARDING_APP_ID` | Onboarding |
| `UI_SETTING_APP_ID` | Settings |
| `UI_LOGGER_APP_ID` | Logger |
| `UI_BACKGROUND_DASHBOARD_APP_ID` | Dashboard (background) |
| `UI_BACKGROUND_EVENHUB_APP_ID` | EvenHub (background) |
| `UI_FOREGROUND_SYSTEM_ALERT_APP_ID` | System alerts |
| `UI_FOREGROUND_SYSTEM_CLOSE_APP_ID` | System close |
| `UI_FOREGROUND_NOTIFICATION_ID` | Foreground notification |

---

## New Protocol Details

### Device Configuration (DevConfig)

Device config items discovered:
- `DEVICE_BRIGHTNESS` — Brightness level
- `DEVICE_ANTI_SHAKE_ENABLE` — Anti-shake toggle
- `DEVICE_DISPLAY_MODE` — Display mode (dual/full/minimal)
- `DEVICE_WAKEUP_ANGLE` — Wake-up tilt angle
- `DEVICE_WORK_MODE` — Device work mode
- `DEVICE_BLE_MAC` — BLE MAC address
- `DEVICE_DEVICE_SN` / `DEVICE_GLASSES_SN` — Serial numbers

**Display modes**: `display_mode_dual`, `display_mode_full`, `display_mode_minimal`

**Brightness settings**: Per-eye `leftMaxBrightness` / `rightMaxBrightness`, `isAutoBrightness`, calibration settings.

**Brightness protocol details** (from binary string extraction):
- `DeviceReceive_Brightness` — Glasses push current brightness back to app (bidirectional)
- `APP_REQUIRE_BRIGHTNESS_INFO` — App queries glasses for current brightness
- `autoBrightnessLevel` — Current auto-brightness computed level
- `oldBrightness` — Previous brightness value (delta tracking)
- `setBrightnessCalibration left=` — Per-eye calibration log string
- `ProtoAiExt|sendSkillBrightness` — Even AI voice command path for brightness
- `Brightness set to 80.` — Hardcoded example (may be percentage-based, not 0-42 range)
- Service pathway: `_createDevCfgDataPackage` wrapping `ProtoBaseSettings.setBrightness`
- `dispBrightSet: ` / `brightNess =` — Debug log strings

### Conversate Extended Protocol

Beyond our basic init/transcript, the full conversate protocol supports:

| Command | Purpose |
|---|---|
| `CONVERSATE_CONTROL` | Start/stop |
| `CONVERSATE_HEART_BEAT` | Keepalive |
| `CONVERSATE_TRANSCRIBE_DATA` | Transcription text |
| `CONVERSATE_TAG_DATA` | Tag/keyword data |
| `CONVERSATE_TAG_TRACKING_DATA` | Tag tracking updates |
| `CONVERSATE_TITLE_DATA` | Conversation title |
| `CONVERSATE_KEYPOINT_DATA` | Key point/summary |
| `CONVERSATE_STATUS_NOTIFY` | Status changes |

### Even AI Extended Protocol

| Enum | Values |
|---|---|
| `eEvenAICommandId` | 0=NONE, 1=CTRL, 2=VAD_INFO, 3=ASK, 4=ANALYSE, 5=REPLY, 6=SKILL, 7=PROMPT, 8=EVENT, 9=HEARTBEAT, 10=CONFIG, 161=COMM_RSP |
| `eEvenAIStatus` | 0=STATUS_UNKNOWN, 1=EVEN_AI_WAKE_UP, 2=EVEN_AI_ENTER, 3=EVEN_AI_EXIT |
| `eEvenAIEvent` | Events (field numbers TBD) |
| `eEvenAIPrompt` | Prompt types (field numbers TBD) |
| `eEvenAISkill` | 0=Brightness, 1=Translate, 2=Notification, 3=Teleprompt, 4=Navigate, 5=Conversate, 6=Quicklist, 7=Auto_brightness |
| `eEvenAIVADStatus` | Voice Activity Detection (field numbers TBD) |

**Protobuf field structure** (confirmed Phase 3):
- f1 = command (varint)
- f2 = magic (varint, random per session)
- f3 = ctrl nested (f1=status code from eEvenAIStatus)
- f5 = ask nested (f4=text bytes)
- f7 = reply nested (f4=text bytes)

### BLE Connection Lifecycle (from flutter_ezw_ble — Phase 3)

The native BLE layer uses a structured state machine:

```
connecting → contactDevice → searchService → searchChars → startBinding → connectFinish
```

**BleConfig model fields**:
- `name`, `scan`, `privateServices`, `initiateBinding`, `connectTimeout`, `upgradeSwapTime`
- Private services use `BlePrivateService.type` (first must be 0 = basic/control)
- `BleSnRule`/`BleMacRule` for serial number and MAC parsing from advertisement data

**BleEasyConnect**: `uuid`, `name`, `afterUpgrade`, `time`, `bleConfig` — reconnection after OTA upgrade uses `afterUpgrade` flag with `upgradeSwapTime` delay.

**Write negotiation**: Uses `maximumWriteValueLengthForType:` to determine MTU-based write chunk size.

**Upgrade mode**: `enterUpgradeState` blocks all non-OTA commands; `quiteUpgradeState` (sic) re-enables them.

### MCU Manager / SMP Protocol (from iosmcumgr — Phase 3)

The R1 Ring and potentially G2 use Nordic SMP for firmware updates:

**Upgrade lifecycle**: none → requestMcuMgrParameters → bootloaderInfo → upload → validate → test → confirm → reset → success

**Bootloader modes**: singleApplication, swapUsingScratch, overwrite, swapNoScratch, directXIPNoRevert, directXIPWithRevert, RAMLoader

**McuMgr manifest fields**: `format-version`, `time`, `files[]` with `size`, `file`, `slot`, `modtime`, `version_MCUBOOT`, `board`, `load_address`, `image`, `image_index`

**Image slot fields**: `image`, `slot`, `hash`, `data`, `version`, `bootable`, `pending`, `confirmed`, `active`, `permanent`

### Menu System (from app strings — Phase 3)

The Even.app has a menu system for quick-action menus on the glasses:

- `APP_SEND_MENU_INFO` / `OS_RESPONSE_MENU_INFO` — bidirectional menu sync
- `Menu_Item_Ctx` — individual menu item context with fields from `meun_main_msg_ctx` (note: typo in Even.app source)
- `BleG2CmdProtoExt|_createMenuDataPackage` — menu data package creator
- Service ID: TBD (likely shared with g2_setting on 0x0D-00)

**AI Features (skills)**: conversate, teleprompt, navigate, translate, save_quicklist, show_favorite_location_list, silent_mode_on

**Even AI complete command set** (from binary string extraction):
- `sendAiConfig` — Configure AI parameters
- `sendAsr` — Send ASR result
- `sendAIReplay` — Send AI reply text to display
- `sendAnalyzeLoading` — Show "analyzing" loading state
- `sendWakeupResp` — Respond to wakeup event
- `sendVadEndFeedBack` — VAD end feedback
- `sendIllegalState` — Signal illegal state
- `sendExit` — Exit AI session
- `sendEvenHeartbeat` — AI-specific heartbeat
- Skill dispatch: `sendSkillBrightness`, `sendSkillBrightnessAuto`, `sendSkillConverse`, `sendSkillNavigate`, `sendSkillNotification`, `sendSkillQuickList`, `sendSkillTeleprompt`, `sendSkillTranslate`

**VAD Status enum**: `VAD_START`, `VAD_END`, `VAD_TIMEOUT`, `VAD_INFO`, `VAD_STATUS_UNKNOWN`, `VAD_END from glasses`

**EvenAI message types** (from Dart protobuf):
`EvenAIControl`, `EvenAIAskInfo`, `EvenAIReplyInfo`, `EvenAISkillInfo`, `EvenAIConfig`, `EvenAIHeartbeat`, `EvenAIEvent`, `EvenAIPromptInfo`, `EvenAISentiment`, `EvenAIVADInfo`, `EvenAIAnalyseInfo`, `EvenAICommRsp`

### Navigation Extended Protocol

| Command | Purpose |
|---|---|
| `APP_REQUEST_NAVIGATION_COMPLETE` | Navigation complete |
| `APP_REQUEST_RECALCULATING_LOCATION_START` | Start recalculation |
| `APP_SEND_MAX_MAP_FILE` | Send overview map (BMP via file service) |
| `APP_SNED_MINI_MAP_FILE` | Send mini map (BMP via file service) |
| `APP_RESPONSE_LOCATION_LIST` | Send location list |
| `OS_NOTIFY_COMPASS_CHANGED` | Compass heading data |
| `OS_NOTIFY_COMPASS_CALIBRATE_*` | Compass calibration |
| `OS_NOTIFY_LOCATION_SELECTED` | User selected location |

**Maps** are sent as BMP files via the file transfer service, rendered from Mapbox.

**Navigation map pipeline** (from binary string extraction):
- `sendNavigationMiniMap` — Mini map sent periodically during navigation (with timer: `startMiniMapTimer`, `cancelMiniMapTimer`)
- `sendNavigationOverviewMap` — Full overview map (on-demand, triggered by `triggerOverviewMapCapture`)
- `sendNavigationFavoriteList` — Send favorite locations to glasses for on-device selection
- `sendNavigationStartError` — Error on navigation start
- `sendNavigationRecalculating` — Route recalculation notification
- Map deduplication: `_isMiniMapDataEqual` prevents redundant sends
- Map capture: `captureMiniMap` / `captureOverviewMap` → `processMinimapImage` / `processOverviewMapData` → `_transformMapData` → BLE send
- Fragment protocol: `mapSessionId`, `mapFragmentIndex`, `mapFragmentPacketSize`, `mapRawData`
- OS events: `OS_NOTIFY_LOCATION_SELECTED` (user chose location), `OS_NOTIFY_MENU_STARTUP_REQUEST_LOCATION_LIST` (glasses request locations)

### Compass/Magnetometer Protocol (NEW)

The glasses have a compass/magnetometer sensor with three OS notification events:
- `OS_NOTIFY_COMPASS_CALIBRATE_STRAT` (sic: "STRAT" not "START") — Calibration started
- `OS_NOTIFY_COMPASS_CALIBRATE_COMPLETE` — Calibration complete
- `OS_NOTIFY_COMPASS_CHANGED` — Heading changed

Related types: `CompassCalibrateStatus`, `compassIndex`, `compassMsg`
User instruction: `look_around_to_calibrate_compass`

### Glasses Firmware Filesystem Paths (NEW)

Log file paths visible on the firmware:
- `L:/log/compress_log_0.bin` through `L:/log/compress_log_4.bin` (left eye)
- `R:/log/compress_log_0.bin` through `R:/log/compress_log_4.bin` (right eye)
- `L:/log/hardfault.txt` — Left eye crash dump
- `R:/log/hardfault.txt` — Right eye crash dump

### Logger/Live Log Protocol (NEW)

The glasses support live log streaming and management:
- `BLE_LOGGER_LEVEL_SET` — Set log level on glasses
- `BLE_LOGGER_SWITCH_SET` — Enable/disable logging
- `DELETE_ALL_LOGGER_FILE` — Delete all log files on glasses
- `DEVICE_SEND_LOGGER_DATA` — Glasses send log data to phone
- `ProtoLogExt|sendLiveLogSwitch` — Toggle live logging
- `ProtoLogExt|sendLiveLogLevel` — Set log verbosity
- `ProtoLogExt|sendLogHeartbeat` — Log service keepalive
- `ProtoLogExt|deleteAllLogFiles` — Clear all logs
- `ProtoLogExt|onListenLiveLogEvent` — Receive live log events

### Glasses Case Protocol (NEW)

| Command | Purpose |
|---|---|
| `CASE_INFO` | Case info command |
| `caseElectricity` | Case battery level |
| `caseIsCharging` | Charging state |
| `inCaseStatus` | Glasses in case detection |

### Dashboard Widget System (29 Widget Types)

**29 widget types** confirmed from Flutter SVG asset analysis (`os_dashboard_*.svg`):

| Category | Widgets |
|---|---|
| Time/Clock | time, timezone |
| Calendar | calendar, schedule |
| Weather | weather, weather_detail |
| Information | news, stocks, notifications |
| Health | bpm, steps, calories, productivity, sleep, temperature, spo2 |
| Features | even_ai, teleprompt, conversate, translate, navigate |
| System | battery, silent_mode, compass, quicklist, brightness |
| Status | wear_detection, do_not_disturb, find_phone |

Settings: `DashboardMenuItemType`, auto-close timer (`APP_SET_DASHBOARD_AUTO_CLOSE_VALUE`)

### Health Protocol (R1 Ring)

| Data Type | Source |
|---|---|
| Heart rate | `_buildHeartRate` |
| SpO2 / Blood oxygen | `_buildSpO2` |
| Sleep stages | `_AboutSleepStagesSection` |
| Activity/Steps | `_ActivityDay`, `_extractActivityDay` |
| Temperature | `_TemperatureController` |
| Calories | `os_dashboard_health_calories` |

**Ring health commands**: `getDailyData`, `ackNotifyData`, `setHealthEnable`, `getHealthSettingsStatus`, `getWearStatus`

### Ring Data Relay Protocol (NEW)

The glasses can relay data between phone and ring:
- `UX_RING_DATA_RELAY_ID` — Relay data through glasses to ring
- `UX_RING_ROW_DATA_ID` — Raw ring data
- `BleG2CmdProtoRingExt|openRingBroadcast` — Tell glasses to open ring discovery
- `BleG2CmdProtoRingExt|switchRingHand` — Switch ring hand (left/right)
- `RING_CONNECT_INFO` / `RING_CONNECT_TIMEOUT` — Connection info/timeout
- `setRingLowPerformanceMode` — Toggle low power mode on ring

### Quicklist Extended Protocol (NEW)

Quicklist supports paging and CRUD operations:
- `ProtoQuicklistExt|respondPagingByUid` — Respond to glasses paging request
- `ProtoQuicklistExt|sendItemSingle` — Send single item
- `ProtoQuicklistExt|sendMultAdd` — Add multiple items
- `ProtoQuicklistExt|sendMultFullUpdate` — Full update of all items
- `ProtoQuicklistExt|onListenOsPushEvent` — Listen for glasses events

### Translate Extended Protocol (NEW)

Full lifecycle beyond basic CTRL/RESULT:
- `ProtoTranslateExt|sendStartTranslate` — Start translation
- `ProtoTranslateExt|sendStopTranslate` — Stop translation
- `ProtoTranslateExt|sendPauseTranslate` — Pause
- `ProtoTranslateExt|sendResumeTranslate` — Resume
- `ProtoTranslateExt|sendTranslateResult` — Send result to display
- `ProtoTranslateExt|sendTranslateHeartbeat` — Keepalive
- `TRANSLATE_MODE_SWITCH` — Switch translation mode

### Device Management Commands (NEW)

Via `BleG2CmdProtoDeviceSettingsExt`:
- `createTimeSyncCommand` — Time sync
- `sendHeartbeat` — Heartbeat
- `startPair` / `unpair` — Pairing management
- `disconnect` — Disconnect
- `quickRestart` — Reboot glasses
- `restoreFactory` — Factory reset
- `sendFile` / `receiveFile` — File transfer
- `selectPipeChannel` — Switch pipe channel (control vs file)
- `connectRing` — Connect ring through glasses

### Transcribe & Translate (Separate from Conversate)

**Transcribe**: `TRANSCRIBE_CTRL`, `TRANSCRIBE_HEARTBEAT`, `TRANSCRIBE_NOTIFY`, `TRANSCRIBE_RESULT`

**Translate**: `TRANSLATE_CTRL`, `TRANSLATE_HEARTBEAT`, `TRANSLATE_MODE_SWITCH`, `TRANSLATE_NOTIFY`, `TRANSLATE_RESULT`

These are distinct protocols from Conversate, each with their own heartbeat and control flows.

### File Transfer Extended

| Response Code | Meaning |
|---|---|
| `EVEN_FILE_SERVICE_RSP_SUCCESS` | Success |
| `EVEN_FILE_SERVICE_RSP_FAIL` | Generic failure |
| `EVEN_FILE_SERVICE_RSP_DATA_CRC_ERR` | CRC error |
| `EVEN_FILE_SERVICE_RSP_FLASH_WRITE_ERR` | Flash write error |
| `EVEN_FILE_SERVICE_RSP_NO_RESOURCES` | No resources |
| `EVEN_FILE_SERVICE_RSP_RESULT_CHECK_FAIL` | Result check failed |
| `EVEN_FILE_SERVICE_RSP_START_ERR` | Start error |
| `EVEN_FILE_SERVICE_RSP_TIMEOUT` | Timeout |

### Gesture Configuration

- `APP_Send_Gesture_Control` — Send gesture mapping to glasses
- `APP_Send_Gesture_Control_List` — Full gesture control list
- `APP_Send_Dominant_Hand` — Set dominant hand
- `toggleAllowLongPressWhileDisplayOff` — Long press when display off
- Per-user gesture preferences serialized as JSON

---

## BERT Intent Model (On-Device NLU)

The `even.framework` includes a BERT-based intent classifier for on-device voice command understanding. 30 voice intents are recognized:

| Intent | Entity Type | Description |
|---|---|---|
| `open_teleprompt` | — | Open teleprompter |
| `close_teleprompt` | — | Close teleprompter |
| `open_conversate` | — | Start conversation |
| `close_conversate` | — | Stop conversation |
| `open_translate` | `language` | Start translation (target language) |
| `close_translate` | — | Stop translation |
| `open_transcribe` | — | Start transcription |
| `close_transcribe` | — | Stop transcription |
| `open_navigate` | `destination` | Start navigation |
| `close_navigate` | — | Stop navigation |
| `open_quicklist` | — | Open quick list |
| `close_quicklist` | — | Close quick list |
| `open_dashboard` | — | Show dashboard |
| `close_dashboard` | — | Hide dashboard |
| `set_brightness` | `level` | Set brightness level |
| `set_volume` | `level` | Set volume level |
| `set_silent_mode` | `on/off` | Toggle silent mode |
| `take_photo` | — | Capture photo (R1 Ring camera) |
| `show_notification` | — | Show notifications |
| `clear_notification` | — | Clear notifications |
| `show_battery` | — | Show battery status |
| `show_time` | — | Show current time |
| `show_weather` | — | Show weather |
| `show_calendar` | — | Show calendar events |
| `show_health` | — | Show health data |
| `show_stocks` | — | Show stock prices |
| `set_timer` | `duration` | Set timer |
| `set_alarm` | `time` | Set alarm |
| `add_quicklist_item` | `text` | Add item to quick list |
| `general_query` | `text` | Fallback — sent to cloud AI |

The BERT model tokenizer is at `modules/bert/src/tokenizer.cpp` in the framework build tree. Inference runs via ONNX Runtime.

---

## EvenHub Container Event Types

Container events arrive on 0x0E-00 when a container has `isEventCapture=1`. Seven event types exist:

| Event Type | Name | Description |
|---|---|---|
| `0` | `CLICK_EVENT` | User tapped the container |
| `1` | `SCROLL_TOP` | User scrolled to top of list |
| `2` | `SCROLL_BOTTOM` | User scrolled to bottom of list |
| `3` | `DOUBLE_CLICK` | User double-tapped |
| `4` | `FOREGROUND_ENTER` | Container gained foreground focus |
| `5` | `FOREGROUND_EXIT` | Container lost foreground focus |
| `6` | `ABNORMAL_EXIT` | Container exited abnormally |

**Our implementation**: We partially handle `CLICK_EVENT` (0). Events 1-6 are not decoded.

**Image result codes** returned by the glasses for container image rendering:

| Code | Name | Meaning |
|---|---|---|
| `0` | `SUCCESS` | Image rendered successfully |
| `1` | `FAIL` | Generic render failure |
| `2` | `imageSizeInvalid` | Image size exceeds limits |
| `3` | `sendFailed` | Send operation failed |
| `4` | `INVALID_PARAM` | Invalid container parameters |

**EvenHub error codes** (13 error types covering all container operations):

| Context | Error |
|---|---|
| Create | `APP_REQUEST_CREATE_INVAILD_CONTAINER`, `APP_REQUEST_CREATE_OUTOFMEMORY_CONTAINER`, `APP_REQUEST_CREATE_OVERSIZE_RESPONSE_CONTAINER` |
| Rebuild | `APP_REQUEST_REBUILD_PAGE_FAILD` |
| Text | `APP_REQUEST_UPGRADE_TEXT_DATA_FAILED` |
| Image | `APP_REQUEST_UPGRADE_IMAGE_RAW_DATA_FAILED` |
| Shutdown | `APP_REQUEST_UPGRADE_SHUTDOWN_FAILED` |
| Audio | `APP_REQUEST_AUDIO_CTR_FAILED` |

**Container constraints:**
- `createStartUpPageContainer` can only be called **ONCE** per EvenHub session
- `audioControl` requires `createStartUpPageContainer` first
- Images cannot be sent during container creation — must use `updateImageRawData` after
- EvenHub heartbeat is distinct from auth heartbeat (own keepalive cycle)
- `Sys_ItemEvent` is page-scoped (no container fields, unlike list/text events)

**Container heartbeat**: EvenHub containers require periodic heartbeat to stay alive. The `audioControl` prerequisite must be met before entering audio-related EvenHub modes.

---

## Navigation Extended Protocol (Full Command Set)

The navigation service (0x08-20) supports 10 sub-commands; we implement 2:

| Command | Name | Implemented? | Description |
|---|---|---|---|
| 1 | `start` | **YES** | Begin navigation with state/instructions |
| 2 | `basicInfo` | **YES** | Send turn-by-turn instruction update |
| 3 | `miniMap` | No | Send mini-map BMP via file service |
| 4 | `overviewMap` | No | Send overview map BMP via file service |
| 5 | `heartbeat` | No | Navigation keepalive |
| 6 | `recalculating` | No | Route recalculation in progress |
| 7 | `arrive` | No | Destination reached |
| 8 | `stop` | No | Stop navigation |
| 9 | `startError` | No | Navigation start failed |
| 10 | `favoriteList` | No | Send favorite locations list |

### Navigation Icon Types (36 confirmed)

| Icon | Name | Icon | Name |
|---|---|---|---|
| 1 | Turn left | 19 | Enter roundabout |
| 2 | Turn right | 20 | Exit roundabout |
| 3 | Go straight | 21 | Roundabout left |
| 4 | U-turn | 22 | Roundabout right |
| 5 | Slight left | 23 | Roundabout straight |
| 6 | Slight right | 24 | Roundabout U-turn |
| 7 | Sharp left | 25 | Ferry |
| 8 | Sharp right | 26 | Arrive left |
| 9 | Merge left | 27 | Arrive right |
| 10 | Merge right | 28 | Arrive straight |
| 11 | Merge | 29 | Flag/waypoint |
| 12 | Ramp left | 30 | Destination |
| 13 | Ramp right | 31 | Close/cancel |
| 14 | Fork left | 32 | Close-X |
| 15 | Fork right | 33 | Flag outline |
| 16 | Off ramp | 34 | Navigation off |
| 17 | Keep left | 35 | Roundabout 135° |
| 18 | Keep right | 36 | Roundabout 45° |

**36 total** confirmed from Flutter SVG asset analysis (`ic_navigation_*.svg`). Our implementation uses icons 1-4. The Mapbox NavigationNative framework provides these icon types during active navigation.

---

## Teleprompter Extended Protocol

Beyond the basic init/content/complete sequence, the full teleprompter protocol includes:

| Command | Type | Description |
|---|---|---|
| `INIT` | 1 | Initialize script display |
| `SCRIPT_LIST` | 2 | Send available scripts |
| `CONTENT_PAGE` | 3 | Send content page |
| `CONTENT_COMPLETE` | 4 | Signal content upload done, start scroll |
| `PAUSE` | 5 | Pause scrolling |
| `RESUME` | 6 | Resume scrolling |
| `HEARTBEAT` | 9 | Teleprompter keepalive |
| `AI_SYNC` | 10 | Synchronize scroll position with AI speech detection |
| `MARKER` | 255 | Mid-stream boundary marker |

**Complete teleprompter command enum** (from `TelepromptCommandId` in App.framework):
`TELEPROMPT_CONTROL`, `TELEPROMPT_HEART_BEAT`, `TELEPROMPT_STATUS_NOTIFY`, `TELEPROMPT_COMM_RESP`, `TELEPROMPT_FILE_LIST`, `TELEPROMPT_FILE_LIST_REQUEST`, `TELEPROMPT_FILE_SELECT`, `TELEPROMPT_PAGE_DATA`, `TELEPROMPT_PAGE_DATA_REQUEST`, `TELEPROMPT_PAGE_AI_SYNC`, `TELEPROMPT_PAGE_SCROLL_SYNC`

**Error codes**: `TELEPROMPT_ERR_CLOSED`, `TELEPROMPT_ERR_FAIL`, `TELEPROMPT_ERR_PD_DECODE_FAIL`, `TELEPROMPT_ERR_REPEATED_MESSAGE`

**AI Scroll Mode**: When scroll mode=1 (AI), the teleprompter synchronizes scroll position with speech recognition output. `AI_SYNC` commands update the scroll position based on detected speech progress. This enables the "read-along" feature where the display follows the speaker.

---

## Audio Control Commands

Audio control for mic and speaker is managed via these commands:

| Command | Description |
|---|---|
| `OPEN` | Enable audio capture (mic on) |
| `CLOSE` | Disable audio capture (mic off) |
| `PAUSE` | Temporarily pause capture |
| `RESUME` | Resume paused capture |

**Prerequisite**: `audioControl` must be in the correct state before EvenHub modes that use audio. The mic is enabled via NUS (`[0x0E, 0x01]`) for our implementation, but the official app may use a protobuf command on the control channel.

---

## File Transfer Extended (Bidirectional)

The file service supports both directions:

### Phone → Glasses (SEND)
- `EVEN_FILE_SERVICE_CMD_SEND_START` — Begin sending file to glasses
- `EVEN_FILE_SERVICE_CMD_SEND_DATA` — Send file data chunk
- `EVEN_FILE_SERVICE_CMD_SEND_END` — Complete file send
- Used for: notifications, maps, firmware, config files

### Glasses → Phone (EXPORT)
- `EVEN_FILE_SERVICE_CMD_EXPORT_START` — Begin receiving file from glasses
- `EVEN_FILE_SERVICE_CMD_EXPORT_DATA` — Receive file data chunk
- `EVEN_FILE_SERVICE_CMD_EXPORT_END` — Complete file export
- Used for: diagnostic logs, captured photos/data

Our implementation only uses the SEND direction (for notifications).

---

## Dashboard Widget System (Detail)

### Widget Types
| Type | Data | Description |
|---|---|---|
| `TIME` | Current time + timezone | Clock display |
| `CALENDAR` | EventKit events | Next appointment |
| `WEATHER` | Location + conditions | Current + forecast |
| `NOTIFICATION` | App + count | Unread notifications |
| `HEALTH` | BPM + steps + calories | Ring health summary |

### Page Types
| Type | Description |
|---|---|
| `MAIN` | Primary dashboard view |
| `WEATHER_DETAIL` | Expanded weather forecast |
| `CALENDAR_DETAIL` | Calendar event list |
| `NOTIFICATION_DETAIL` | Notification list |
| `HEALTH_DETAIL` | Health data breakdown |
| `STOCKS_DETAIL` | Stock portfolio view |

Dashboard auto-close timer: `APP_SET_DASHBOARD_AUTO_CLOSE_VALUE` (configurable seconds).

---

## R1 Ring OTA (Nordic SMP/MCU Manager)

The R1 Ring uses Nordic SMP (Simple Management Protocol) via iOSMcuManagerLibrary for firmware updates — distinct from the G2's custom OTA path:

- **DFU framework**: `iOSMcuManagerLibrary` (Nordic MCU Manager)
- **Protocol**: SMP over BLE (standard Nordic DFU, not Even-custom)
- **Multi-part**: Supports multi-part firmware packages
- **Device type field**: Firmware check API uses a device type discriminator for G2 vs R1

This means the G2 and R1 use completely different OTA mechanisms:
- G2: Custom `ota_transmit` protocol with ECDSA-P256 signed packages
- R1: Standard Nordic SMP/MCU Manager DFU

### Dual OTA Architecture (NEW — from binary analysis)

The app uses two OTA paths:

**1. G2 Glasses OTA** (custom protocol via `BleG2OtaUpgradeMixin` + `BleG2FileServiceMixin`):
- Custom `BleG2OtaHeader` with `otaMagic1`, `otaMagic2`, `componentNum`, `componentInfo`
- File transfer over 0x74xx characteristics (`eEvenFileSendServiceCID`)
- Waits for file service idle state with configurable timeout

**2. Ring / DFU Error Recovery** (Nordic DFU via `NordicDfuPlugin`):
- Standard Nordic Secure DFU (`NordicDFU.framework`)
- `DeviceRingDfuErrorOta` — fallback when normal G2 OTA fails
- Parameters: `enableUnsafeExperimentalButtonlessServiceInSecureDfu`, `packetReceiptNotificationParameter`, `mbrSize`, `dataObjectPreparationDelay`

**Firmware update flow:**
- API endpoints: `/v2/g/check_firmware`, `/v2/g/check_latest_firmware`
- `_shouldIncludeCloudFirmware` — decides bundled vs cloud firmware
- `_prepareUpgradeQueue` — multi-step upgrade sequence
- `FULL_UPDATE` — comprehensive BL+SD+App update
- Build path: `file:///Volumes/Acer_SSD/jenkins_data/workspace/APP/G2/iOS-IPA/` (Jenkins CI)

---

## Audio Pipeline

```
G2 Mic → LC3 encode (on-glasses Apollo510b via GX8002B codec IC)
       → BLE NUS (0xF1 prefix, LC3-encoded frames)
       → flutter_ezw_lc3 (LC3 decode to PCM via FFI)
       → GTCRN neural noise reduction (denoised PCM)
       → AGC (auto gain control)
       → Speech Enhance / SSR Smoother
       → Three ASR paths:
         1. Apple SFSpeechRecognizer (on-device, teleprompt.framework)
         2. Azure SPXSpeechRecognizer (cloud, flutter_ezw_asr.framework)
         3. Azure SPXTranslationRecognizer (cloud, translate.framework)
       → Silero VAD v4/v5 for voice activity detection (vad_model.onnx)
       → BERT NLU (30 intents for on-device voice commands)
```

**LC3 codec**: Decode-only on phone (encode happens on glasses). FFI bindings: `_lc3_decode`, `_lc3_setup_decoder`, `_lc3_decoder_size`, `_lc3_frame_samples`. Parameters: `frameDuration`, `sampleRate`, `bitRate`.

**GTCRN (NEW — framework analysis 2026-03-01)**: Neural network-based noise reduction pipeline running on-device via ONNX Runtime. Processes audio after LC3 decode and before ASR. The `even.framework` contains the GTCRN model weights and inference code alongside AGC and SSR Smoother modules.

**Background audio keepalive**: The Even.app bundles a `background_silence_music.mp3` file that plays silent audio to maintain the iOS background BLE connection. This prevents iOS from suspending the app's BLE callbacks during long sessions.

**Secondary ASR**: Soniox as backup provider (`asr_soniox_config_v3`).

---

## On-Device ML

The `even.framework` embeds:

- **ONNX Runtime** — Neural network inference
- **llama.cpp** — LLM inference with Metal GPU support, flash attention
- **Sherpa-ONNX** — On-device speech recognition
- **Silero VAD** — Voice Activity Detection
- **BERT tokenizer** — Text tokenization (`modules/bert/src/tokenizer.cpp`)

Build source tree: `/Users/even/flutter-cpp/`

---

## Cloud API

**Base URL**: `https://api2.evenreal.co`
**CDN**: `https://cdn.evenreal.co`, `https://cdn2.evenreal.co`

### Key Endpoint Categories (80+ endpoints at /v2/g/)

| Category | Endpoints | Examples |
|---|---|---|
| Auth | 9 | login, register, send_code, reset_passwd |
| Device Management | 6 | bind_device, unbind_device, list_devices |
| Firmware | 3 | check_firmware, check_latest_firmware, check_app |
| User Settings | 8 | user_info, user_settings, get/set_user_prefs |
| NV Sync | 3 | get_nv, upload_nv, update_set |
| Even AI (Jarvis) | 9 | jarvis/chat, jarvis/conversate/*, jarvis/message/* |
| ASR | 1 | asr_sconf |
| Translation | 5 | translate_create/get/update/delete, translate_ai_summary |
| News | 4 | news_list, news_categories, news_sources |
| Stocks | 5 | stock_tickers, stock_intraday, stock_favorite_* |
| Health | 7 | health/push, health/get_info, health/get_latest_data |
| Notifications | 3 | notify_list, get_ios_app_list |
| Inbox | 4 | inbox/list, inbox/delete, inbox/mark_as_read |
| Feedback | 1 | filelogs/feedback |

---

## Functional Gaps (Our App vs Official App)

### High Priority (core features)

1. **Dashboard** — Rich widget system (time, calendar, weather, news, stocks, health, notifications)
2. **Transcribe** — Separate from conversate, dedicated protocol with heartbeat
3. **Translate** — Separate protocol with mode switching
4. **LC3 Audio Decode** — We receive raw PCM but official app uses LC3 codec
5. **Compass** — Magnetometer heading data available via `OS_NOTIFY_COMPASS_CHANGED`

### Medium Priority (useful features)

6. **Menu System** — Quick actions synced to glasses
7. **QuickList** — Notes/tasks synced to glasses
8. **Health Data** — R1 Ring heart rate, SpO2, sleep, temperature, steps
9. **Module Configure** — Enable/disable features, brightness calibration
10. **Glasses Case** — Battery, charging, in-case detection
11. **R1 Ring Extended** — Health commands, wear detection, algorithm keys
12. **Navigation Maps** — BMP overview/mini map via file transfer
13. **Gesture Configuration** — Custom gesture mappings, dominant hand
14. **Device Configuration** — Anti-shake, display mode, wake angle

### Low Priority (infrastructure)

15. **Onboarding** — First-run glasses setup flow
16. **Sync Info** — NV config cloud sync with CRC validation
17. **Logger** — Pull diagnostic logs from glasses
18. **OTA** — Full firmware update pipeline
19. **Pipe Channel Selection** — Dynamic BLE characteristic routing
20. **Cloud API Integration** — Even AI (Jarvis) chat, news, stocks, health push

### Onboarding Protocol (RE 2026-03-01)

The onboarding flow has these states:
1. `video_state` — Show gesture instruction videos
2. `muti_video_state` — Multi-video state
3. `wear_state` — Wear detection check
4. `headup_state` — Head-up calibration
5. `notification_state` — Notification setup
6. `disconnect_state` — Reconnection handling
7. `end_state` — Onboarding completion

**Commands**: `setOnBoardingStart` → calibration steps → `setOnBoardingEnd` + `postGlassesOnBoardingEnd` (API call)

### Navigation Map Pipeline (extended RE 2026-03-01)

**Map data fields** (mini_map_msg / max_map_msg):

| Field | Type | Purpose |
|-------|------|---------|
| `mapSessionId` | int | Session identifier |
| `mapTotalSize` | int | Total map data size |
| `compressMode` | int | Compression type |
| `mapFragmentIndex` | int | Current fragment index |
| `mapFragmentPacketSize` | int | Fragment size |
| `mapRawData` | bytes | Raw bitmap data |
| `miniMapBorderEn` | int | Mini map border enable |

**Navigation compass events (glasses → phone):**
- `OS_NOTIFY_COMPASS_CALIBRATE_STRAT` — Compass calibration started
- `OS_NOTIFY_COMPASS_CALIBRATE_COMPLETE` — Compass calibration complete
- `OS_NOTIFY_COMPASS_CHANGED` — Compass heading changed
- `OS_NOTIFY_LOCATION_SELECTED` — User selected location on glasses
- `OS_NOTIFY_MENU_STARTUP_REQUEST_LOCATION_LIST` — Glasses requesting location list

**Navigation exit reasons:**
- `os_navigate_complete` — Arrived
- `os_navigate_connection_time_out` — BLE timeout
- `os_navigate_fail_location_too_far` — Location too far
- `os_navigate_fail_no_location_access` — No location permission
- `os_navigate_fail_something_went_wrong` — Generic error
- `os_navigate_recalculating` — Rerouting

---

## Methodology

Analysis performed via 9+ parallel research agents across two phases:

**Phase 1 (2026-03-01)**:
1. **Firmware Bundle Agent** — Binary analysis of bootloader.bin and softdevice.bin
2. **Core Framework Strings** — `strings` extraction from even_core, flutter_ezw_ble, even frameworks
3. **Feature Framework Analysis** — Analysis of conversate, teleprompt, dashboard, translate, flutter_ezw_asr, flutter_ezw_lc3 frameworks
4. **Flutter/Dart Assets** — Info.plist, asset catalogs, kernel snapshots
5. **Deep Binary Analysis** — Comprehensive symbol extraction from App.framework and all native frameworks

**Phase 2 (2026-03-01, deep-dive)**:
6. **Official BLE API Spec** — Review of EVEN_BLE_API_SPEC.md and even_v2g_paths.txt for undocumented endpoints
7. **i-soxi Proto Schema** — Cross-reference of third-party protobuf definitions against our implementation
8. **Unanalyzed Frameworks** — Deep analysis of 27 previously unexplored frameworks (GTCRN audio pipeline, Flutter assets for widget/icon counts, hardware variant images)
9. **BLE Capture Mining** — Automated extraction of service ID traffic from rawBLE.txt and testAll captures

**Phase 3 (2026-03-01, verification + gap-fill)**:
10. **Source Inventory** — Systematic catalog of all unanalyzed material across official/, third_party/, captures/
11. **Even.app Binary Mining** — Targeted extraction of brightness packets, service ID mappings, protobuf field structures from BLE captures and binary
12. **i-soxi Proto Deep Verification** — Complete field-by-field proto analysis revealing 3 field-number errors in i-soxi, confirming our implementations are correct
13. **App Strings Mining** — Systematic keyword search of 1.7MB even_app_strings.txt for proto modules, proto extensions, and undocumented features
14. **Tools/EZW Mining** — Analysis of g2_packet_decoder.py (Even AI enum, file command format), flutter_ezw_ble_strings.txt (BLE state machine), iosmcumgr_strings.txt (MCU Manager lifecycle), ota_protocol_tokens.txt (OTA vocabulary), even_urls.txt (API endpoints)

---

## API Endpoints (76 total — from even_v2g_paths.txt)

Base URL: `api2.evenreal.co` (prod), `api2.ev3n.co` (alt), `pre-g2.evenreal.co` (staging)

### Account & Auth
- `/v2/g/login`, `/v2/g/register`, `/v2/g/account_del`, `/v2/g/account_logout`
- `/v2/g/check_password`, `/v2/g/check_reg`, `/v2/g/pre_check_code`, `/v2/g/send_code`, `/v2/g/reset_passwd`

### Device Management
- `/v2/g/bind_device`, `/v2/g/unbind_device`, `/v2/g/unbind_terminal`
- `/v2/g/list_devices`, `/v2/g/set_device_remark`
- `/v2/g/check_bind2`, `/v2/g/check_app`

### Firmware & Settings
- `/v2/g/check_firmware`, `/v2/g/check_latest_firmware`
- `/v2/g/update_glasses_settings`, `/v2/g/update_set2`
- `/v2/g/user_settings`, `/v2/g/user_info`, `/v2/g/set_profile`, `/v2/g/upload_avatar`
- `/v2/g/get_user_prefs`, `/v2/g/set_user_prefs`
- `/v2/g/set_on_boarded`, `/v2/g/func_conf`
- `/v2/g/asr_sconf` (ASR server config)

### AI & Conversate (Jarvis)
- `/v2/g/jarvis/chat` — Main AI chat endpoint
- `/v2/g/jarvis/conversate/ws` — WebSocket for real-time conversate
- `/v2/g/jarvis/conversate/list`, `/v2/g/jarvis/conversate/detail`
- `/v2/g/jarvis/conversate/messages2`, `/v2/g/jarvis/conversate/finish`
- `/v2/g/jarvis/conversate/update`, `/v2/g/jarvis/conversate/remove`
- `/v2/g/jarvis/message/list`, `/v2/g/jarvis/message/sentiment`
- `/v2/g/jarvis/session/action/delete`

### Health
- `/v2/g/health/push`, `/v2/g/health/get_info`, `/v2/g/health/update_info`
- `/v2/g/health/get_latest_data`, `/v2/g/health/get_pkey`
- `/v2/g/health/query_window`, `/v2/g/health/batch_query_window`
- `/v2/g/health/export`

### Notifications & Inbox
- `/v2/g/notify_list` — Notification whitelist
- `/v2/g/get_ios_app_list`, `/v2/g/update_ios_app_list`
- `/v2/g/inbox/list2`, `/v2/g/inbox/unread_count`
- `/v2/g/inbox/mark_as_read`, `/v2/g/inbox/delete`

### News
- `/v2/g/news_list`, `/v2/g/news_categories`, `/v2/g/news_sources`
- `/v2/g/news_favorites_settings`, `/v2/g/news_favorites_settings_save`

### Stocks
- `/v2/g/stock_tickers`, `/v2/g/stock_intraday`
- `/v2/g/stock_favorite_list`, `/v2/g/stock_favorite_create`
- `/v2/g/stock_favorite_update`, `/v2/g/stock_favorite_del`

### Translate
- `/v2/g/translate_create`, `/v2/g/translate_get`
- `/v2/g/translate_update`, `/v2/g/translate_delete`
- `/v2/g/translate_ai_summary`

### Misc
- `/v2/g/get_nv`, `/v2/g/upload_nv` — Named variables (key-value store)
- `/v2/g/get_privacy_urls` — Privacy policy URLs
- `/v2/g/filelogs/feedback` — Debug feedback upload

---

## R1 Ring Health Commands (from Even.app RE)

The R1 ring exposes health functionality through proprietary BLE commands:

| Extension | Method | Purpose |
|-----------|--------|---------|
| `BleRing1CmdHealthExt` | `getDailyData` | Fetch daily health data (HR, SpO2, HRV, steps, sleep, skinTemp) |
| `BleRing1CmdHealthExt` | `ackNotifyData` | Acknowledge health notification data |
| `BleRing1CmdWearStatusExt` | `getWearStatus` | Query wear detection state |
| `BleRing1CmdSettingsStatusExt` | `getHealthSettingsStatus` | Get health monitoring config |
| `BleRing1CmdSettingsStatusExt` | `setHealthSettingsStatus` | Set health monitoring config |
| `BleRing1CmdSettingsStatusExt` | `setHealthEnable` | Enable/disable health monitoring |
| `BleRing1CmdSettingsStatusExt` | `getSystemSettingsStatus` | Get system settings |
| `BleRing1CmdSettingsStatusExt` | `setSystemSettingsStatus` | Set system settings |
| `BleRing1CmdGoMoreExt` | `getAlgoKeyStatus` | Get algorithm key status |
| `BleRing1CmdGoMoreExt` | `setAlgoKey` | Set algorithm key |
| `BleRing1CmdOldExt` | `unpair` | Unpair ring (DANGEROUS — not for probes) |

Health data types fetched via `getDailyData`:
- Heart Rate (HR), SpO2, HRV, Steps/Calories (activity), Sleep/SkinTemp

**Status:** Command byte format unknown. Ring uses proprietary protocol on BAE80012.
Phase 2 probes (#37-39) attempt service discovery and speculative command patterns.

---

## Translate Protocol (from Even.app RE)

Translate shares service 0x07-20 with EvenAI and Dashboard. Command types differentiate protocols.

| Command | Method | Purpose |
|---------|--------|---------|
| TRANSLATE_CTRL | `sendStartTranslate` / `sendStopTranslate` | Start/stop translation |
| TRANSLATE_CTRL | `sendPauseTranslate` / `sendResumeTranslate` | Pause/resume |
| TRANSLATE_HEARTBEAT | `sendTranslateHeartbeat` | Keep session alive |
| TRANSLATE_RESULT | `sendTranslateResult` | Send translation result to glasses |
| TRANSLATE_MODE_SWITCH | — | Switch translation mode |
| TRANSLATE_NOTIFY | — | Status notifications |

**Status:** Exact type field values unknown. Phase 2 probe #40 tests speculative type=20.
Related: Transcribe protocol (`ProtoTranscribeExt`) is also separate from Conversate.

---

## Display/Motion Settings Methods (from Even.app RE)

Settings commands on 0x0D-00 via G2SettingPackage:

| Extension | Method | Mapped To |
|-----------|--------|-----------|
| `DisplaySettingsExt` | `setGridDistance` | Config field 3 (X offset) |
| `DisplaySettingsExt` | `setGridHeight` | Config field 4 (Y offset) |
| `MotionSettingsExt` | `setHeadUpAngle` | DEVICE_WAKEUP_ANGLE (cmdId=16) |
| `MotionSettingsExt` | `setHeadUpTriggerDashboard` | Head-up trigger for dashboard |
| — | `antiShakeEnable` | DEVICE_ANTI_SHAKE_ENABLE (cmdId=15) |
| — | `surfaceBright` | Surface brightness measurement |
| — | `ALSInfo` | Ambient light sensor data |

**Confirmed:** gridDistance (field 3) and gridHeight (field 4) are real parameters in ConfigurationReader.

---

## Phase 3 Deep Protocol Discovery (2026-03-02)

The following 21 areas were discovered from comprehensive RE sweeps of `official/Even.app` and `official/artifacts/even_firmware_extract/`. Most use unknown service IDs and cannot be probed yet — they are documented for future reference when service routing is discovered.

### 1. Compass/Magnetometer Protocol

The G2 glasses contain a magnetometer sensor. Three notification events are referenced:

- `OS_NOTIFY_COMPASS_CALIBRATE_STRAT` — calibration started (typo preserved from source)
- `OS_NOTIFY_COMPASS_CALIBRATE_COMPLETE` — calibration finished
- `OS_NOTIFY_COMPASS_CALIBRATE_CHANGED` — heading changed

These are **push-only unsolicited notifications** from the glasses. There is no query command to request compass data — the glasses push updates when the heading changes. The Even.app subscribes to these events for navigation features. The service ID and characteristic routing are unknown.

### 2. Wear Detection Gates BLE Transmission

Wear detection is a critical gating mechanism in the BLE protocol:

- `isSendAllow isWearing = false` — blocks BLE command transmission when glasses are not worn
- `setWearDetection` — settings command on 0x0D-00 to enable/disable wear detection
- `getGlassesIsWear` — query whether glasses are currently being worn
- `getOnGlassesWear` — callback/listener for wear state changes

The detection source is likely a proximity sensor (capacitive or IR) on the nose bridge or temple. When glasses are removed, the Even.app suppresses non-essential BLE traffic. This explains why some commands may not work when the glasses are resting on a table.

**Status:** `setWearDetection` routes through 0x0D-00 (G2SettingPackage) but the specific cmdId and field structure are unknown.

### 3. EvenAI Skill Sub-commands

The EvenAI protocol (type=6 on 0x07-20) supports 10 skill sub-commands identified from `sendSkill*` methods:

| skillId | Name | Description |
|---------|------|-------------|
| 0 | NONE / BRIGHTNESS | Brightness query/set |
| 1 | BRIGHTNESS_AUTO | Auto-brightness toggle |
| 2 | NAVIGATE | Navigation trigger |
| 3 | TRANSLATE | Translation trigger |
| 4 | CONVERSE | Conversate/ASR trigger |
| 5 | NOTIFICATION | Notification display |
| 6 | TELEPROMPT | Teleprompter trigger |
| 7 | QUICKLIST | QuickList display |
| 8 | ASR_CONF | ASR configuration (inferred) |
| 9 | NONE_2 | Reserved/unknown |

Additional non-skill EvenAI commands on the same service:
- `sendWakeupResp` — respond to voice wakeup
- `sendVadEndFeedBack` — VAD end-of-speech feedback
- `sendAnalyzeLoading` — show "analyzing" indicator
- `sendIllegalState` — report illegal state to glasses
- `sendExit` — exit EvenAI mode

**Probe 48** tests skillId=0 (brightness query) on real hardware.

### 4. Logger Protocol (Unknown Service ID)

Live log streaming protocol for debugging:

- `sendLiveLogLevel` — set minimum log level
- `sendLiveLogSwitch` — enable/disable live log streaming
- `deleteAllLogFiles` — delete all stored log files on glasses
- `sendLogHeartbeat` — keep log stream alive
- `onListenLiveLogEvent` — receive log events in real time

Command enum values:
- `BLE_LOGGER_SWITCH_SET` — toggle log streaming
- `BLE_LOGGER_LEVEL_SET` — set verbosity level
- `DELETE_ALL_LOGGER_FILE` — clear logs

Routes through `ProtoLogExt` but the service ID is **unknown**. Cannot probe until service routing is discovered.

### 5. QuickList Protocol (Unknown Service ID)

Bidirectional protocol for managing quick-access items displayed on the glasses:

- `sendMultAdd` — add multiple items
- `sendMultFullUpdate` — full list replacement
- `sendItemSingle` — add/update single item
- `respondPagingByUid` — pagination response keyed by UID
- `sendSkillQuickList` — AI-triggered quicklist display (via EvenAI SKILL)

The protocol supports paging (items delivered in batches with UIDs for continuation). AI integration allows the assistant to populate the quicklist dynamically. Routes through a dedicated data package creator but the service ID is **unknown**.

### 6. Dashboard Protocol (Shares 0x07-20 with EvenAI)

The dashboard protocol shares the 0x07-20 service with EvenAI, differentiated by the `type` field. This is the most complex undocumented protocol with 6 widget types:

| Widget | Description |
|--------|-------------|
| News | News headlines with categories and sources |
| Health | Health metrics (heart rate, steps, SpO2) |
| Stock | Stock tickers with intraday data |
| Schedule | Calendar events |
| QuickList | Quick-access items |
| Unknown | Placeholder for future widgets |

Additional dashboard features:
- **7 expanded page types** (different detail views for each widget)
- **17 weather enum types** (clear, cloudy, rain, snow, etc.) for weather widget
- Methods: `sendDashboardBaseSettingInfoToGlass`, `sendNeedSendNewsCount`, `sendWeatherInfoToGlass`, `sendDashboardSnapshot`

**Probe 49** scans types 11-19 on 0x07-20 to discover dashboard protocol boundaries. The exact type values used by dashboard are unknown — they could be in this range or overlap with other protocols.

### 7. OTA Protocol (DO NOT PROBE)

5-phase over-the-air update protocol for G2 glasses firmware:

| Phase | Description |
|-------|-------------|
| START | Initiate OTA, negotiate parameters |
| INFORMATION | Exchange firmware metadata (version, size, CRC) |
| FILE | Transfer firmware binary in chunks |
| RESULT_CHECK | Verify transfer integrity |
| NOTIFY | Notify completion, trigger reboot |

10 error codes (from Even.app strings):
1. OTA_ERROR_UNKNOWN
2. OTA_ERROR_TIMEOUT
3. OTA_ERROR_CRC_FAIL
4. OTA_ERROR_FLASH_FAIL
5. OTA_ERROR_VERSION_MISMATCH
6. OTA_ERROR_BATTERY_LOW
7. OTA_ERROR_DISCONNECTED
8. OTA_ERROR_FILE_INVALID
9. OTA_ERROR_DEVICE_BUSY
10. OTA_ERROR_NOT_SUPPORTED

The G2 glasses use a **custom OTA protocol** (EVENOTA format on Apollo510b) rather than Nordic DFU. The nRF52840/S140 DFU bootloader bundled in the app may serve an auxiliary update path (EM9305 BLE radio or R1 Ring). The R1 ring uses standard Nordic DFU + MCUmgr (SMP UUID: `DA2E7828-FBCE-4E01-AE9E-261174997C48`).

Firmware signing: **ECDSA P-256**. The bootloader contains the public verification key.

**SAFETY: This protocol is EXCLUDED from all probing. OTA commands could brick the device.**

### 8. DFU Bootloader Memory Map (nRF52840 — Auxiliary Path)

From the DFU package analysis in `official/artifacts/even_firmware_extract/`. Note: this is the nRF52840 DFU bootloader layout, not the Apollo510b main application memory map.

```
Flash Layout (1MB total — nRF52840 DFU bootloader):
├── MBR           0x00000000  (4 KB)    Master Boot Record
├── SoftDevice    0x00001000  (152 KB)  S140 v7.0.0 (FWID 0x0100)
├── Application   0x00027000  (836 KB)  APP_CODE_BASE
├── Bootloader    0x000F4000  (24 KB)   Secure bootloader
├── Settings      0x000FA000  (4 KB)    BL settings page
└── MBR Params    0x000FE000  (4 KB)    MBR parameters

RAM: 256 KB (nRF52840)
```

Device identifiers:
- Board: **B210**
- Model: **S200**
- DFU name: **B210_DFU** (advertised during DFU mode)
- DFU Service UUID: `8EC90000-F315-4F60-9FB8-838830DAEA50`
- Hardware variants: G2 A / G2 B, each in Brown / Green / Grey

### 9. Battery/Charging Telemetry

Battery and charging status fields discovered from Even.app:

| Field | Description |
|-------|-------------|
| `batteryStatus0` | Left eye battery level |
| `batteryStatus1` | Right eye battery level |
| `chargingStatus` | Charging state (0=not charging, 1=charging) |
| `chargingCurrent` | Charge current in mA |
| `chargingTemp` | Battery temperature |
| `chargingVBat` | Battery voltage |
| `chargingError` | Charging error code |
| `deviceRunningStatus` | Overall device power state |

Note: The standard BLE Battery Service (0x180F) does **not** exist on the G2 glasses (confirmed by probe). Battery data comes through the proprietary protocol, likely via device info responses on 0x09-xx or 0x0D-00.

### 10. R1 Ring Additional Discoveries

Additional R1 ring capabilities found in Even.app:

- **`switchRingHand(isLeft:)`** — Tell ring which hand it's worn on (affects gesture orientation)
- **`openRingBroadcast`** — Force ring into advertising mode
- **GoMore health algorithm** — `getAlgoKeyStatus` / `setAlgoKey` for health data processing
- **`BleRing1CmdProto`** — Protobuf command protocol for ring (separate from gesture protocol)
- **`low_power_mode`** — Ring enters low power mode that weakens BLE signal strength
- **Ring health data:** HR, SpO2, sleep tracking, temperature, step counting, wear detection
- **Ring DFU:** Nordic DFU with MCUmgr (SMP characteristic `DA2E7828-FBCE-4E01-AE9E-261174997C48`). **FE59** (Buttonless Secure DFU) also advertised in service discovery (confirmed 2026-03-02)
- **Ring BLE services discovered (2026-03-02):** BAE80001 (Ring Service), FE59 (Nordic Buttonless DFU), 1800 (Generic Access), 1801 (Generic Attribute)
- **R1 health query results:** Heart rate, SpO2, and temperature queries return `00 00` (zero data) — ring may require active wearing/sensor contact to produce readings

### 11. File Transfer Protocol Evolution

The file transfer protocol has undergone migration:

- **`SubfileType`** — Current file type enum (map, firmware, config, etc.)
- **`OldSubfileType`** — Legacy enum (preserved for backward compatibility)
- **`EvenReceiveFileBigPackage`** — Glasses-to-phone file transfer (log export, health data)
- **`EvenSendFileBigPackage`** — Phone-to-glasses file transfer (maps, firmware, config)

Export commands for bidirectional transfer:
- `EXPORT_START` — Begin export session
- `EXPORT_DATA` — Data chunk
- `EXPORT_RESULT_CHECK` — Verify export integrity

File routing: `sendFileCid` determines which characteristic (0xC4 or 0xC5) carries the data. The service uses characteristics 0x7401 (write) and 0x7402 (notify) for file operations.

### 12. Pipe Channel / PipeRoleChange

Dynamic BLE characteristic routing at runtime:

- **`selectPipeChannel`** — Settings command on 0x0D-00 that switches the active BLE pipe
- **`PipeRoleChange`** — Event triggered when the active characteristic changes
- **`PIPE_ROLE_CHANGE2`** — Secondary pipe role change enum value

The G2 glasses have three sets of characteristics (x5450/x6450/x7450) that alternate with the primary sets (x5401-02/x6401-02/x7401-02). PipeRoleChange dynamically switches which set is active, possibly for bandwidth management or concurrent operations (e.g., file transfer on one pipe while display updates continue on another).

### 13. Notification Protocol (4 Types)

Four notification sub-protocols on service 0x02-20:

| Type | Description |
|------|-------------|
| `NOTIFICATION_CTRL` | Control commands (enable/disable notifications) |
| `NOTIFICATION_IOS` | iOS-specific notification forwarding |
| `NOTIFICATION_WHITELIST_CTRL` | App whitelist management |
| `NOTIFICATION_JSON_WHITELIST` | JSON-format whitelist sync |

Server-synced whitelists via `/v2/g/get_ios_app_list` and `/v2/g/update_ios_app_list`. The `hot_app_list` is a curated set of popular apps maintained server-side.

The JSON key for notifications is `"android_notification"` even on iOS — the firmware expects this key name regardless of platform.

### 14. Protobuf Module Count (32 Total)

Phase 3 RE sweeps discovered 4 additional protobuf modules beyond the 28 known:

| Module | Description |
|--------|-------------|
| `dev_config_protocol` | Device configuration protocol definitions |
| `dev_pair_manager` | Pairing/bonding protocol |
| `dev_settings` | Device settings schema |
| `service_id_def` | Service ID definition table (meta-protocol) |

The `service_id_def` module is particularly interesting — it likely contains the canonical mapping of protocol names to BLE service IDs. If we could access this module's output, it would resolve all 18 unknown service IDs.

Complete count: **20 `_createDataPackage` methods** confirmed, mapping to 20 distinct data encoders for BLE transmission.

### 15. Onboarding Flow

3-step onboarding protocol for first-time setup:

1. `setOnBoardingStartUp` — Initialize onboarding screens
2. `setOnBoardingStart` — Begin interactive setup (display calibration, head tracking test)
3. `setOnBoardingEnd` — Complete onboarding, enter normal mode

Additional: `getBoardingIsHeadup` — Check if user is looking up (head-up detection during calibration).

Routes through `ProtoBaseSettings` (0x0D-00) but uses unknown cmdId values.

### 16. Glasses Case Protocol

Protocol for communicating with the G2 charging case:

- `GlassesCaseInfo` — Case status data structure
- `GlassesCaseDataPackage` — BLE data package for case communication
- `eGlassesCaseCommandId` — Command enum for case operations
- `getGlassesCaseInfo` — Query case status via `ProtoBaseSettings`

Monitored parameters:
- Case battery level
- Charging state (case → glasses)
- In-case detection (glasses placed in case)
- Silent mode toggle

Routes through 0x0D-00 but specific cmdId is unknown. The case likely communicates with the glasses via contact pins (not BLE) and the glasses relay status to the phone.

### 17. Module Configure (Unknown Service ID)

Feature enable/disable and calibration protocol:

- `module_configure_Cmd_list` — List of configurable modules
- `dashboard_general_setting` — Dashboard-wide settings
- `send_system_general_setting` — System-level settings

Includes brightness calibration parameters (`leftMaxBrightness`, `rightMaxBrightness`) for per-eye display calibration. Service ID is **unknown**.

### 18. Gesture Control List

Configurable gesture-to-action mapping protocol:

- `ProtoBaseSettings|setGestureControlList` — Push gesture config to glasses
- `APP_Send_Gesture_Control` — Single gesture mapping
- `APP_Send_Gesture_Control_List` — Full gesture config list
- `DOUBLE_CLICK_EVENT` — Double-tap event identifier

This allows customizing what each gesture does (e.g., mapping double-tap to next slide, swipe to scroll, etc.). Routes through 0x0D-00.

### 19. Sync Info Protocol (Unknown Service ID)

Cloud configuration sync protocol:

- `APP_REQUEST_SYNC_INFO` — Request sync from cloud
- `OS_NOTIFY_SYNC_INFO` — Glasses notify sync state

NV (non-volatile) config data is synced between cloud (`/v2/g/upload_nv`, `/v2/g/get_nv`) and glasses with CRC integrity checks. This ensures glasses settings survive factory reset by restoring from cloud backup.

### 20. BLE Characteristics Confirmed (12 Total)

All 12 BLE characteristic handles confirmed via RE:

Base UUID: `00002760-08C2-11E1-9073-0E8AC72E{xxxx}`

| Handle | Type | Usage |
|--------|------|-------|
| 0x0001 | Write | Base write (phone → glasses) |
| 0x0002 | Notify | Base notify (glasses → phone) |
| 0x5401 | Write | Control write |
| 0x5402 | Notify | Control notify |
| 0x5450 | Alternate | Control alternate (pipe role change) |
| 0x6401 | Write | Display write |
| 0x6402 | Notify | Display notify (sensor stream) |
| 0x6450 | Alternate | Display alternate |
| 0x7401 | Write | File write |
| 0x7402 | Notify | File notify |
| 0x7450 | Alternate | File alternate |
| 0x1001 | Unknown | Purpose unknown (possibly DFU or diagnostics) |

No additional characteristics exist beyond these 12.

### 21. Protocols with Unknown Service IDs

18 protocols cannot be probed because their BLE service IDs are unknown:

| Protocol | Data Package Creator | Blocked By |
|----------|---------------------|------------|
| Logger | `ProtoLogExt._createDataPackage` | Unknown service ID |
| QuickList | `ProtoQuickListExt._createDataPackage` | Unknown service ID |
| Menu | `ProtoMenuExt._createDataPackage` | Unknown service ID |
| Module Configure | `ProtoModuleConfigureExt._createDataPackage` | Unknown service ID |
| Glasses Case | `ProtoGlassesCaseExt._createDataPackage` | Unknown service ID |
| Health | `ProtoHealthExt._createDataPackage` | Unknown service ID |
| Onboarding | Part of `ProtoBaseSettings` | Unknown cmdId |
| Sync Info | Unknown | Unknown service ID |
| Transcribe | `ProtoTranscribeExt._createDataPackage` | Unknown service ID |
| OTA | `ProtoOtaExt._createDataPackage` | SAFETY: excluded |
| DFU | Nordic DFU service | SAFETY: excluded |
| Pair Manager | `dev_pair_manager` | Unknown service ID |
| Device Config | `dev_config_protocol` | Unknown service ID |
| Device Settings | `dev_settings` | Unknown service ID |
| Service ID Def | `service_id_def` | Meta-protocol |
| Compass | Push-only notification | No query command |
| Wear Detection | Part of 0x0D-00 | Unknown cmdId |
| Gesture Config | Part of 0x0D-00 | Unknown cmdId |

**Next steps:** Discovering `service_id_def` output or intercepting the `selectPipeChannel` handshake would likely unlock several of these protocols. Alternatively, exhaustive type scanning on known services (0x07-20, 0x0D-00) may reveal hidden sub-protocols.

---

## Phase 4 Deep Protocol Discovery (2026-03-02)

### Protocol Timing Constants (from Even.app RE)

Concrete timing values extracted from Even.app source analysis:

| Value | Meaning | Source |
|-------|---------|--------|
| 30s | Result callback timeout (BLE response treated as lost) | Even.app `_startResultCallbackTimeoutTimer` |
| 20s | BLE reconnect timeout after unexpected disconnect | Even.app translation session handler |
| 2 hours | Soniox ASR session maximum duration | Even.app `Soniox translation session timeout` |
| 3s | Audio manager startup delay before first frame | Even.app audio recognizer manager |
| 15s | Weather data fetch timeout | Even.app dashboard weather widget |
| 50-1000ms | Conversate segment interval valid range | Even.app validation: `Converse segment interval must be between 50-1000ms` |
| 100-1000ms | ASR result delivery interval valid range | Even.app validation: `ASR result interval must be between 100-1000ms` |

Our implementation uses 600ms for conversate inter-frame delay, which is within the valid 50-1000ms range.

### Audio Format Parameters

| Parameter | Value | Confidence |
|-----------|-------|------------|
| PCM Format 1 | `pcmFloat32` (32-bit IEEE 754 float) | High — Even.app enum |
| PCM Format 2 | `pcm16bits` (16-bit signed integer) | High — Even.app enum |
| LC3 Sample Rate | 16,000 Hz | High — matches our G2AudioConstants |
| LC3 Frame Duration | 10ms | High — matches our G2AudioConstants |
| LC3 Bytes/Frame | 40 | High — matches our G2AudioConstants |

The G2 glasses encode mic audio on-chip (Apollo510b via GX8002B codec IC) using LC3 codec. The phone-side Even.app decodes via `flutter_ezw_lc3` (FFI). Our NUS audio path receives pre-decoded PCM.

### DFU Init Packet Structure (Nordic Secure DFU)

Decoded from firmware `.dat` files in `official/artifacts/even_firmware_extract/`:

| Field | Value | Notes |
|-------|-------|-------|
| `op_code` | 1 | Init command |
| `signature_type` | 0 | ECDSA P-256 |
| `signature_len` | 64 bytes | Standard ECDSA signature size |
| `hw_version` | 52 | nRF52 series identifier |
| `sd_req` | [0x0100, 0x0102] | Accepts S140 v7.0.0 or v7.2.0 |
| `hash_type` | 3 | SHA-256 |
| Hash byte order | Little-endian reversed | Nordic convention |

**Bootloader variants:**
- `B210_BL_DFU_NO` (24,420 bytes): versioned bootloader, fw_version=3, is_debug=true
- `B210_ALWAY_BL_DFU` (24,180 bytes): fail-safe bootloader, same version/debug flags

**SoftDevice init packet:**
- fw_version=0xFFFFFFFF (unreleased/development marker)
- sd_size=153,140 bytes (S140 v7.0.0)

### HeadUp Display Mode

HeadUp is a distinct rendering pipeline for dashboard wake-by-head-gesture:

- `setHeadUpAngle` routes through `MotionSettingsExt`, likely maps to `DEVICE_WAKEUP_ANGLE` (cmdId=16) on 0x0D-00
- `setHeadUpTriggerDashboard` configures dashboard wake behavior separately
- HeadUp angle is calibrated per-device during onboarding `headup_state` step
- `getBoardingIsHeadup` queries whether user is currently looking up (calibration check)
- Separate from normal wakeup angle — specifically triggers dashboard display on look-up

### R1 Ring Multi-Packet Protocol

The R1 Ring uses a fundamentally different transport layer from G2:

| Feature | G2 Glasses | R1 Ring |
|---------|-----------|---------|
| Checksum | CRC16-CCITT | CRC32 |
| Packet tracking | Sequence numbers | UUID-based |
| Completion signal | Implicit (total=num) | Explicit finish signal |
| Fragment format | AA-header envelope | BleRing1CmdProto protobuf |

Ring multi-packet messages are tracked by UUID with CRC32 validation per-chunk and an explicit finish marker.

### Service ID Routing Architecture

The `service_id_def.pbenum.dart` module is the master enum defining all BLE service IDs. Seven IDs are named but their numeric values remain in the compiled Flutter AOT binary:

| Enum Name | Protocol | Status |
|-----------|----------|--------|
| `UI_LOGGER_APP_ID2` | Logger | Values in compiled binary |
| `UI_HEALTH_APP_ID2` | Health | Values in compiled binary |
| `UI_QUICKLIST_APP_ID` | QuickList | Values in compiled binary |
| `UI_TRANSCRIBE_APP_ID` | Transcribe | Values in compiled binary |
| `SERVICE_MODULE_CONFIGURE_APP_ID` | Module Configure | Values in compiled binary |
| `SERVICE_SYNC_INFO_APP_ID` | Sync Info | Values in compiled binary |
| `UX_GLASSES_CASE_APP_ID` | Glasses Case | Values in compiled binary |

To extract these values, one would need to decompile the Flutter AOT binary (`Runner.app` Mach-O executable) or intercept BLE traffic while the Even.app uses these services.

### Complete EvenAI Command Type Map

All known types on service 0x07-20:

| Type | Name | Direction | Probe Phase |
|------|------|-----------|-------------|
| 0 | NONE | — | Unused |
| 1 | CTRL | Bidirectional | Core (implemented) |
| 2 | VAD_INFO | Glasses→Phone | RX-only |
| 3 | ASK | Phone→Glasses | Core (implemented) |
| 4 | ANALYSE | Phone→Glasses | Phase 4 (NEW) |
| 5 | REPLY | Phone→Glasses | Core (implemented) |
| 6 | SKILL | Bidirectional | Phase 3 (probed); **echoes even outside active EvenAI session** (testAll-2 2026-03-02) |
| 7 | PROMPT | Phone→Glasses | Phase 4 (NEW) |
| 8 | EVENT | Unknown | Phase 4 (NEW) |
| 9 | HEARTBEAT | Bidirectional | Phase 2 (probed) |
| 10 | CONFIG | Phone→Glasses | Phase 2 (probed) |
| 11-19 | Unknown | Unknown | Phase 3 (scanned) |
| 20-23 | Translate | Speculative | Phase 2 (probed) |
| 161 (0xA1) | COMM_RSP | Glasses→Phone | Phase 4 (reverse-tested); **f12.f1 sub-codes**: 7=EvenAI completion, 8=EvenHub completion (testAll-2 2026-03-02) |

### COMM_RSP Sub-Codes (f12 field)

COMM_RSP (0xA1) on various services uses `f12={f1=N}` to indicate completion context:

| f12.f1 | Meaning | Service | Confirmed |
|--------|---------|---------|-----------|
| 7 | EvenAI session completion | 0x07-00 | testAll-2 2026-03-02 |
| 8 | EvenHub task completion | 0x07-00 | testAll-2 2026-03-02 |

The distinction was previously unknown — both codes appear on 0x07-00 but signify different completion scopes.

### Controller Protocol (0x10-20) — CONFIRMED ACTIVE

Previously listed as "no response" (Phase 2), but **testAll-2 (2026-03-02) confirmed** that 0x10-20 responds with a delayed ACK on 0x10-00:

- **Response format:** `{f1=1, f3={empty}}` — basic acknowledgment (same pattern as 0x81-00 DisplayTrigger)
- **Timing:** Delayed ~1-2s after TX (not immediate), which is why earlier probe methods with short timeouts missed it
- **Implications:** Controller service is active and processing commands, even though Even.app's usage pattern is unknown

### Tasks Protocol (0x0C-20) — CONFIRMED ACTIVE

Similarly confirmed active in testAll-2:

- **Response format:** `{f1=1, f3={empty}}` on 0x0C-00 — identical basic ACK pattern
- **Timing:** Also delayed response, consistent with Controller
- **Significance:** Previously listed as "Entirely Speculative" in priority tracking — now elevated to confirmed

### Display Sensor Stream Rate Correction

The 0x6402 encrypted sensor stream rate was previously measured at ~18.8 Hz (probe 2026-03-01). testAll-2 (2026-03-02) sustained measurement over 70.8s:

- **Corrected rate:** ~20.1 Hz sustained (1424 frames / 70.8s)
- **Frame size:** 205 bytes/packet (unchanged)
- Previous 18.8 Hz was likely a warm-up artifact from shorter measurement window

### Config State Sub-Mode (f2 field)

Config state notifications on 0x0D-01 include an optional `f2` sub-mode field:

- `f3={f1=6}` — RENDER mode (known)
- `f3={f1=6, f2=7}` — RENDER with EvenAI overlay active (NEW, testAll-2 2026-03-02)

The `f2=7` sub-mode appears when EvenAI content is rendered on the display without a full mode transition. This explains how EvenAI can draw on the display while maintaining the base RENDER mode.

### Display Wake ACK Variant (0x04-00)

Display wake ACK on 0x04-00 was previously documented as always `{f1=1, f3={empty}}` (08011a00). testAll-2 reveals a variant:

- **Standard:** `{f1=1, f3={empty}}` — 13/15 responses (87%)
- **Variant:** `{f1=1, f2=N, f3={empty}}` — 2/15 responses, where f2 is the glasses' running counter (f2=85, f2=86 — sequential)
- The f2 field in the variant is the same unified counter used in protobuf f2 across all services. Most ACKs omit it; occasionally the glasses include it

### EvenAI Exit Sequence (4-Packet Burst)

When an EvenAI session exits (CTRL type=1 with status=EXIT), the glasses respond with a precise 4-packet burst on the left eye (testAll-2 2026-03-02):

1. **CTRL Echo** (0x07-00): `f1=1, f2=msgId, f3={f1=3}` — echoes the EXIT command (f3.f1=3 = EXIT status)
2. **Mode Status** (0x07-01): `f1=1, f2=glasses_counter, f3={f1=3}` — confirms EvenAI session exited
3. **Config Reset** (0x0D-01): `f1=1, f3={f1=6}` — returns to RENDER mode (config state close)
4. **COMM_RSP** (0x07-00): `f1=0xA1, f2=msgId, f12={f1=7}` — completion signal (f12.f1=7 = EvenAI)

The burst arrives within ~5ms total. The right eye also sends packets 1-2 independently (with its own counter values).

### Glasses Session State Persistence

Glasses maintain session state across phone disconnections (testAll-2 2026-03-02):

- At session start (before any TX), the capture shows unsolicited RX packets from a **previous session's** conversate timeout:
  - 0x0B-01: ConversateNotify auto-close `f1=0xA1, f2=68, f8={f1=2}` (timeout from prior session)
  - 0x0D-01: Config state reset `f1=1, f3={empty}` (paired with auto-close)
  - 0x0B-00: Delayed conversate ACK `f1=0xA2, f2=249, f9={empty}` (from prior session's finalize)
- These arrive ~5s into the new connection, indicating the glasses' conversate auto-close timer (~60s) was still counting during the phone's disconnection period
- **Implication:** Features that set timers (conversate, teleprompter scroll) will fire their completion/close events even if the phone disconnects and reconnects mid-timer
