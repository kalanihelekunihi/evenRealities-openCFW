# Even G2 Service IDs

## Service ID Format

Service IDs are 2 bytes in the packet header (bytes 6-7):

```
AA 21 01 0C 01 01 [hi] [lo] ...
                   ↑    ↑
              Service ID
```

## Known Services

### Consolidated Service Registry

All confirmed services with iOS implementation mapping. Firmware handler names from dispatch
table at v2.0.6.14 offset 0x0023DC88 (36 entries, 16 bytes each).

| Service ID | Name | Dir | iOS Sender | iOS Protocol | FW Handler | Status |
|-----------|------|-----|------------|-------------|------------|--------|
| `0x01-20` | Dashboard | TX+RX | G2DashboardStateSender | G2DashboardStateProtocol | `dashboard.c` | Implemented |
| `0x01-01` | Gesture Status | RX | — (callback) | G2ResponseDecoder | — | Implemented |
| `0x02-20` | Notification | TX | G2NotificationSender | — | — | Implemented |
| `0x02-00` | Notification Response | RX | — | G2ResponseDecoder | — | Implemented |
| `0x03-20` | Menu | TX+RX | G2MenuSender | G2MenuProtocol | `menu.page` | Implemented |
| `0x04-20` | Display Wake | TX | G2BrightnessSender | — | — | Implemented |
| `0x04-00` | Display Wake Response | RX | — | G2ResponseDecoder | — | Implemented |
| `0x04-01` | Notify/DevInfo Response | RX | — | G2ResponseDecoder | — | Implemented |
| `0x05-20` | Translate | TX+RX | G2TranslateSender | G2TranslateProtocol | `translate.c` | Implemented |
| `0x06-20` | Teleprompter | TX+RX | G2TeleprompterSender | G2TeleprompterProtocol | — | Implemented |
| `0x06-00` | Teleprompter ACK | RX | — | G2ResponseDecoder | — | Implemented |
| `0x06-01` | Teleprompter Progress | RX | — | G2ResponseDecoder | — | Implemented |
| `0x07-20` | EvenAI | TX+RX | G2EvenAISender | G2EvenAIProtocol | — | Implemented |
| `0x07-00` | EvenAI Response | RX | — | G2ResponseDecoder | — | Implemented |
| `0x07-01` | EvenAI Status | RX | — | G2ResponseDecoder | — | Implemented |
| `0x08-20` | Navigation | TX+RX | G2NavigationSender | G2NavigationProtocol | — | Implemented |
| `0x09-00` | Device Info | TX+RX | G2BLESendHelper | G2ResponseDecoder | — | Implemented |
| `0x09-01` | Device Info Response | RX | — | G2ResponseDecoder | — | Implemented |
| `0x0A-20` | Session Init | TX | G2SessionInitProtocol | — | — | Implemented |
| `0x0B-20` | Conversate | TX+RX | G2ConversateSender | G2ConversateProtocol | — | Implemented |
| `0x0B-00` | Conversate ACK | RX | — | G2ResponseDecoder | — | Implemented |
| `0x0B-01` | Conversate Notify | RX | — | G2ResponseDecoder | — | Implemented |
| `0x0C-20` | Quicklist + Health | TX+RX | G2TasksSender / G2HealthDataSender | G2QuicklistProtocol / G2HealthDataProtocol | `quicklist.c` + `health.c` | Implemented |
| `0x0D-00` | Configuration | TX/RX | G2ConfigurationReader | G2DeviceConfigProtocol | — | Partial+ |
| `0x0D-20` | Device Config | TX | G2DeviceConfigProtocol | — | — | Implemented |
| `0x0D-01` | Config/Gesture Events | RX | — | G2ResponseDecoder | — | Implemented |
| `0x0E-20` | Display Config | TX | G2DisplayTriggerSender | — | — | Implemented |
| `0x0F-20` | Logger | TX+RX | G2LoggerSender | G2LoggerProtocol | `logger_setting.c` | Implemented |
| `0x10-20` | Onboarding | TX+RX | G2OnboardingSender | G2OnboardingProtocol | `onboarding.c` | Implemented |
| `0x20-20` | ModuleConfigure | TX+RX | G2ModuleConfigureSender | G2ModuleConfigureProtocol | both registered | Implemented |
| `0x21-20` | SystemAlert | RX | — | G2SystemProtocols | `system_alert.c` | Implemented |
| `0x22-20` | SystemClose | TX+RX | G2SystemCloseSender | G2SystemProtocols | `systemClose.c` | Implemented |
| `0x80-xx` | Auth | TX+RX | G2ConnectionHelper | G2ResponseDecoder | — | Implemented |
| `0x81-20` | BoxDetect / Display Trigger | TX+RX | G2DisplayTriggerSender | G2ResponseDecoder | `service_box_detect.c` | Implemented |
| `0x91-20` | Ring Relay | TX+RX | G2RingRelaySender | — | `pb_service_ring.c` | Implemented |
| `0xC4-00` | File Transfer Cmd | TX+RX | G2FileTransferClient | — | — | Implemented |
| `0xC5-00` | File Transfer Data | TX+RX | G2FileTransferClient | — | — | Implemented |
| `0xE0-20` | EvenHub | TX+RX | G2EvenHubSender | G2EvenHubProtocol | `evenhub_main.c` | Implemented |
| `0xFF-20` | SystemMonitor | RX | G2SystemMonitorSender | G2SystemProtocols | `system_monitor.c` | Implemented |

### Unresolved / Experimental Services

| Service ID | Name | Source | Notes |
|-----------|------|--------|-------|
| `0x90-??` | Unknown | Firmware RE | 14-byte stub handler, no identifying strings. Possibly reserved/unused |
| TBD | Transcribe | Android 2.0.8 | Types: CTRL(1), HEARTBEAT(2), NOTIFY(3), RESULT(4). Separate from Conversate. Service ID unconfirmed via hardware |
| TBD | SyncInfo | Android 2.0.8 | Types: SYNC_REQUEST(1), SYNC_RESPONSE(2), SYNC_UPDATE(3). Likely routes through 0x0A-20 |
| `0x0A-20` | Session Init Trigger | iOS code | **SPECULATIVE** — registered in code but zero traffic in all captures. No dispatch table entry |
| `0x11-20` | Conversate (alt) | Probe | **INVALID** — confirmed no responses (probe 2026-02-27). No dispatch table entry |

### Name Corrections (firmware RE 2026-03-03)

| Old Name | New Name | Service ID | Reason |
|----------|----------|------------|--------|
| Tasks | **Quicklist** (+Health) | `0x0C-20` | Firmware handler is `quicklist.c` + `health.c` |
| Controller | **Onboarding** | `0x10-20` | Firmware handler is `onboarding.c` |
| Commit | **ModuleConfigure** (+SyncInfo) | `0x20-20` | Firmware handler is `ModuleConfigureService_common_data_handler` |
| Display Trigger | **BoxDetect / Glasses Case** | `0x81-20` | Firmware handler is `service_box_detect.c` |

### Service ID Breakdown

The service ID appears to encode:
- **High byte**: Service category/type
- **Low byte**: Sub-service or mode
  - `0x00` = Control/query
  - `0x01` = Response
  - `0x20` = Data/payload

## Service Details

### 0x80-00 / 0x80-20 / 0x80-01 / 0x80-02 (Authentication)

Used for session establishment and keepalive:

| Type | Service | Direction | Purpose |
|------|---------|-----------|---------|
| `0x04` | 0x80-00 | TX | Capability query |
| `0x05` | 0x80-00 | TX | Capability response-request |
| `0x80` | 0x80-20 | TX | Time sync with transaction ID + timezone offset |
| `0x04` | 0x80-01 | RX | Auth success (f3={f1=1} = success) |
| `0x06` | 0x80-01 | RX/TX | Keepalive heartbeat (bidirectional, ~1-2s on real HW) |
| — | 0x80-02 | RX | Transport ACK (8-byte header-only, no payload/CRC) |

Auth modes:
- **Full auth** (7-packet): msg_ids 0x0C..0x13, capability mode `0x01`
- **Fast auth** (3-packet): msg_ids 0x0D..0x0F, capability mode `0x02`

### 0x02-20 (Notification)

Notification command types (from Android eNotificationCommandId):

| Type | Name | Direction | Description |
|------|------|-----------|-------------|
| 1 | NOTIFICATION_CTRL | TX | Control command (enable/disable) |
| 2 | NOTIFICATION_COMM_RSP | RX | Communication response/ACK |
| 3 | NOTIFICATION_IOS | TX | iOS notification JSON payload |
| 4 | NOTIFICATION_JSON_WHITELIST | TX | Upload JSON whitelist |
| 5 | NOTIFICATION_WHITELIST_CTRL | TX | Enable/disable whitelist filtering |

**JSON payload key**: `"android_notification"` — even on iOS, firmware expects this key (hardcoded in `SVC_ANDROID_ParseNotification()`).
**Whitelist file**: `user/notify_whitelist.json` on LittleFS.

### 0x06-20 (Teleprompter)

Text display service with complete command set (from TelepromptCommandId enum):

| Type | Name | Purpose | Our Status |
|------|------|---------|------------|
| `0x01` | `INIT` | Init/select script | Implemented |
| `0x02` | `SCRIPT_LIST` | Script list management | Not implemented |
| `0x03` | `CONTENT_PAGE` | Content page | Implemented |
| `0x04` | `CONTENT_COMPLETE` | Content complete / start scroll | Implemented |
| `0x05` | `PAUSE` | Pause scrolling | Not implemented (RE 2026-03-01) |
| `0x06` | `RESUME` | Resume scrolling | Not implemented (RE 2026-03-01) |
| `0x07` | `EXIT` | Exit teleprompter mode | Not implemented (RE 2026-03-01) |
| `0x08` | `SPEED` | Set scroll speed | Not implemented (RE 2026-03-01) |
| `0x09` | `HEARTBEAT` | Keepalive heartbeat | Not implemented (RE 2026-03-01) |
| `0x0A` | `AI_SYNC` | AI Sync (scroll-follows-speech) | Not implemented (RE 2026-03-01) |
| `0x0B` | `PLAYING` | Playing state notification | Not implemented (RE 2026-03-01) |
| `0x0C` | `PREVIOUS` | Previous script/page | Not implemented (RE 2026-03-01) |
| `0x0D` | `NEXT` | Next script/page | Not implemented (RE 2026-03-01) |
| `0x0E` | `FONT_SIZE` | Set font size | Not implemented (RE 2026-03-01) |
| `0x0F` | `MIRROR` | Mirror/flip display | Not implemented (RE 2026-03-01) |
| `0x10` | `RESET` | Reset teleprompter state | Not implemented (RE 2026-03-01) |
| `0xFF` | `MARKER` | Mid-stream marker | Implemented |

**Response services:**
- `0x06-00`: Per-page ACK (f1=166/0xA6, f2=msgId echo, f12={f1=1}=replacing active session)
- `0x06-01`: Scroll progress (f1=164/0xA4, f10={f1=count}) + completion (f1=161/0xA1, f7={f1=4})

### 0x0E-20 (Display Config)

Display configuration sent before content:

```
08-02         Type = 2
10-XX         msg_id
22-6A         Field 4, length 106
  [config]    Display parameters
```

### 0x07-20 / 0x07-00 / 0x07-01 (Even AI / Assistant)

Assistant and UI control envelopes. Complete command set from RE 2026-03-01:

| CommandId | Name | Direction | Purpose | Our Status |
|-----------|------|-----------|---------|------------|
| `0` | `NONE_COMMAND` | — | No-op/placeholder | Not implemented |
| `1` | `CTRL` | TX | Enter/exit AI mode | Implemented |
| `2` | `VAD_INFO` | TX/RX | Voice activity detection info | Not implemented |
| `3` | `ASK` | TX | Send question to AI | Implemented |
| `4` | `ANALYSE` | TX | Send analysis request | Not implemented |
| `5` | `REPLY` | TX | Send AI response to glasses | Implemented |
| `6` | `SKILL` | TX | Activate a named skill | Implemented |
| `7` | `PROMPT` | TX | Send prompt text | Not implemented |
| `8` | `EVENT` | TX/RX | Event notification | Not implemented |
| `9` | `HEARTBEAT` | TX | EvenAI keepalive | Not implemented |
| `10` | `CONFIG` | TX | Stream speed, text mode config | Not implemented |
| `161` | `COMM_RSP` | RX | Universal completion marker | Implemented |

**CTRL sub-types** (field 3):
- `ctrlEnter`: Enter AI mode (field3={f1=magicRandom})
- `ctrlExit`: Exit AI mode (field3={f1=magicRandom})

**Even AI status codes** (field 3 inner f1, confirmed Phase 3):
- `0` = STATUS_UNKNOWN
- `1` = EVEN_AI_WAKE_UP
- `2` = EVEN_AI_ENTER
- `3` = EVEN_AI_EXIT

**Even AI protobuf field structure** (confirmed Phase 3):
- f1 = command (varint, one of 0-10 or 161)
- f2 = magic (varint, random per session)
- f3 = ctrl nested (f1=status code)
- f5 = ask nested (f4=text bytes)
- f7 = reply nested (f4=text bytes)

**SKILL indices** (0-indexed):
- 0=Brightness, 1=Translate, 2=Notification, 3=Teleprompt, 4=Navigate, 5=Conversate, 6=Quicklist, 7=Auto_brightness

**Response services:**
- `0x07-00`: Command echo (f1=1/3/5 = CTRL/ASK/REPLY echoed back) + completion (f1=161, f12={f1=7})
- `0x07-01`: Mode status notification (f1=1, f3={f1=2}=entered, f3={f1=3}=exited)

### 0xC4-00 (File Command)

File transfer control on 0x74xx characteristics:

| Payload | Command | Description |
|---------|---------|-------------|
| 93-byte header | FILE_CHECK | Announce file with CRC32C checksum |
| `0x01` | START | Begin data transfer |
| `0x02` | END | Complete transfer |

FILE_CHECK header structure:
```
[4] mode      - 0x00010000 (little-endian)
[4] size      - len(data) * 256
[4] checksum  - (CRC32C << 8) & 0xFFFFFFFF
[1] extra     - (CRC32C >> 24) & 0xFF
[80] filename - Null-padded string
```

### 0xC5-00 (File Data)

Raw file content transfer:

```
[json_bytes]  UTF-8 JSON payload
```

Used for notifications (JSON) and potentially other file types.

**Response codes** (non-protobuf 2-byte LE status word on both 0xC4-00 and 0xC5-00):

| Code | Name | Description |
|------|------|-------------|
| 0 | SUCCESS / fileCheckOK | Transfer phase complete |
| 1 | dataReceived | Data received (NORMAL, not an error) |
| 2 | transferComplete | Transfer complete |
| 3+ | Error | 3=START_ERR, 4=DATA_CRC_ERR, 5=RESULT_CHECK_FAIL, 6=FLASH_WRITE_ERR, 7=NO_RESOURCES |

### File Service (Bidirectional — RE 2026-03-01)

The file service supports both phone→glasses (SEND) and glasses→phone (EXPORT):

| Direction | Command | Description |
|---|---|---|
| SEND | `EVEN_FILE_SERVICE_CMD_SEND_START` | Begin sending file to glasses |
| SEND | `EVEN_FILE_SERVICE_CMD_SEND_DATA` | Send file data chunk |
| SEND | `EVEN_FILE_SERVICE_CMD_SEND_END` | Complete file send |
| EXPORT | `EVEN_FILE_SERVICE_CMD_EXPORT_START` | Begin receiving file from glasses |
| EXPORT | `EVEN_FILE_SERVICE_CMD_EXPORT_DATA` | Receive file data chunk |
| EXPORT | `EVEN_FILE_SERVICE_CMD_EXPORT_END` | Complete file export |

**SEND** is used for: notifications (JSON), navigation maps (BMP), firmware (OTA), config.
**EXPORT** is used for: diagnostic logs, captured data. Local tooling now includes an inferred export client and simulator shim; command-byte confirmation remains pending.

### 0x0B-20 / 0x0B-00 / 0x0B-01 (Conversate/ASR)

Speech transcription display with 2-packet init sequence:

| Type | Name | Purpose | Our Status |
|------|------|---------|------------|
| `0x01` | `INIT` | Init conversate mode (display config inside) | Implemented |
| `0x05` | `TRANSCRIPT` | Transcript text update (30-byte fixed field) | Implemented |
| `0xFF` | `MARKER` | Mid-stream marker (same convention as teleprompter) | Implemented |

**Transcript update fields**: type=5, update_id (incrementing from 0x41), 30-byte space-padded text, partial/final flag.

**Response services:**
- `0x0B-00`: ACK (f1=162/0xA2, f2=msgId, f9={f1=1}=mode activated one-time signal)
- `0x0B-01`: Auto-close notification (f1=161/0xA1, f8={f1=2}=timeout after ~60s idle)

**Note (RE 2026-03-01)**: Transcribe and Translate are SEPARATE protocols with independent heartbeat/control — not sub-modes of Conversate. Service IDs TBD.

### 0x08-20 (Navigation)

Turn-by-turn navigation with 10 sub-commands:

| SubCmd | Name | Purpose | Our Status |
|--------|------|---------|------------|
| `1` | `start` | Start navigation session | Implemented |
| `2` | `basicInfo` | Turn-by-turn instruction (distance, icon, text) | Implemented |
| `3` | `miniMap` | Mini map image (BMP via file service 0xC4/0xC5) | Partial (subcmd echoed; file-map UX not yet modeled) |
| `4` | `overviewMap` | Overview map image (BMP via file service) | Partial (subcmd echoed; file-map UX not yet modeled) |
| `5` | `heartbeat` | Navigation keepalive | Partial (echo + mode keepalive) |
| `6` | `recalculating` | Route recalculation notification | Partial (echo + mode notify) |
| `7` | `arrive` | Arrival at destination | Partial (echo + close sequence) |
| `8` | `stop` | Stop navigation session | Partial (echo + close sequence) |
| `9` | `startError` | Navigation start error | Partial (echo + close sequence) |
| `10` | `favoriteList` | Favorite locations list | Partial (subcmd echoed) |

**States**: 7=active navigation, 2=dashboard widget mode.

**Map pipeline (RE 2026-03-01)**: Maps are BMP images rendered from Mapbox, sent via file transfer service with mini-map timer, fragment protocol, and deduplication.

### 0x0D-00 (Configuration)

Device configuration service with bidirectional traffic:

| Direction | Purpose | Description |
|-----------|---------|-------------|
| TX | Config query | Query current settings |
| TX | Brightness set | Two candidate formats — see below |
| RX | Config response | Current settings values |
| RX | Config mode notification | Asynchronous mode-change broadcasts (f3={f1=mode, f2=feature}) |

**Config mode values**: RENDER=6, CONVERSATE=11, TELEPROMPTER=16. See magic-numbers.md for full table.

**Brightness**: G2 uses protobuf `G2SettingPackage` with `commandId=DEVICE_BRIGHTNESS` via `ProtoBaseSettings|setBrightness`. The G1-era raw byte format `[0x01, level, auto]` does NOT work on G2 (expects protobuf). Protobuf field numbers still TBD. See [brightness.md](../features/brightness.md) for all paths.

**Wear detection (current simulator parity)**:
- Firmware strings confirm wear module linkage: `WearDetect_SetEnable`, `get_wear_status`, `wear_detection_switch`.
- Firmware dispatch evidence: settings selector `5` routes `0x464D04 -> 0x4AB196 (WearDetect_SetEnable)`.
- Simulator responds to `cmdId=0` with wear snapshot fields:
  - `f1`: wear detection enable switch
  - `f2`: current wear status (`1=wear`, `0=unwear`)
- Simulator selector lane also supports:
  - selector `1`: wear snapshot query (+ sub-type context tracking for `ctx+0x16/+0x17`)
  - selector `2`: scalar context write (`ctx+0x08`)
  - selector `3`: scalar context write (`ctx+0x09`)
  - selector `4`: `(subtype,value)` context write (`ctx+0x0A/+0x0B/+0x0C`) + gate shadow
  - selector `5`: wear-enable write
  - selector `6`: scalar context write (`ctx+0x15`) with `0x10A` parity logging
  - selector `7`: no-op
  - selector `8`: conditional gate parity path
- Onboarding `type=4` (service `0x10-20`/`0x10-00`) mirrors wear status in `f3`.
- Simulator-only deterministic control exists on `cmdId=250` (`f2={f1=enable,f2=status}`) until exact selector wire schema is recovered.
- Runtime-context details: [settings-runtime-context.md](../firmware/modules/settings-runtime-context.md).

### 0x07-20 Shared: EvenAI + Dashboard (RE 2026-03-01)

The `0x07-20` service is shared by EvenAI and Dashboard. Both use the same BLE service ID but different protobuf command types. The i-soxi proto schema confirms this: Dashboard data packages route through the same service endpoint, with the top-level `type` field discriminating between AI commands and dashboard widget updates.

## BLE Connection State Machine (from flutter_ezw_ble — Phase 3)

The Even.app's BLE connection follows this state sequence:

```
connecting → contactDevice → searchService → searchChars → startBinding → connectFinish
```

**Error states**: `emptyUuid`, `noBleConfigFound`, `noDeviceFound`, `alreadyBound`, `boundFail`, `serviceFail`, `charsFail`, `timeout`, `bleError`, `systemError`

**Disconnect states**: `disconnectByUser`, `disconnectFromSys`

**BLE config model** (from BlePrivateService): first private service type MUST be 0 (basic/control). The `selectPipeChannel` method dynamically routes traffic to different characteristics at runtime.

**Upgrade mode**: `enterUpgradeState` / `quiteUpgradeState` — non-OTA commands are blocked during firmware upgrade.

**Manufacturer data**: Even.app reads `kCBAdvDataManufacturerData` from advertisement packets.

## API Endpoints (from Even.app — Phase 3)

| URL | Purpose |
|---|---|
| `https://api2.evenreal.co` | Production API |
| `https://api2.ev3n.co` | Production alternate |
| `https://pre-g2.evenreal.co` | Staging/pre-production |
| `https://cdn.evenreal.co` | CDN for assets |
| `https://cdn2.evenreal.co` | CDN secondary (privacy docs) |

**Firmware endpoints**: `/v2/g/check_firmware`, `/v2/g/check_latest_firmware` (see [firmware-updates.md](../firmware/firmware-updates.md))

## Service Discovery

Services can be enumerated by observing traffic patterns:

1. **Auth services** (0x80-xx): Always first in session
2. **Config services** (0x0D-xx, 0x0E-xx): After auth
3. **Feature services**: On-demand based on user action

## Protobuf Extension to Service Routing (RE 2026-03-01)

Each `Proto*Ext` extension in Even.app creates a data package via a corresponding `BleG2CmdProtoExt._create*DataPackage` method and sends via `sendDataPackage2`:

| Extension | Package Creator | BLE Service | Our Status |
|-----------|----------------|-------------|------------|
| `ProtoBaseSettings` | `_createG2SettingDataPackage` | g2_setting (0x0D-00) | Partial |
| `ProtoNavigationExt` | `_createNavigationDataPackage` | navigation (0x08-20) | Partial |
| `ProtoAiExt` | `_createEvenAiDataPackage` | even_ai (0x07-20) | Implemented |
| `ProtoDashboardExt` | `_createDashboardDataPackage` | dashboard (**0x01-20**) | Partial (ACK + sync-info state path) |
| `ProtoTeleprompterExt` | `_createTelepromptDataPackage` | teleprompt (0x06-20) | Implemented |
| `ProtoNotificationExt` | `_createNotificationDataPackage` | notification (0x02-20) | File-only |
| `ProtoHealthExt` | `_createHealthDataPackage` | health (**0x0C-20**, shared with Quicklist) | Implemented (stateful cmd 10/11/12 simulation) |
| `ProtoQuicklistExt` | `_createQuickListDataPackage` | quicklist (**0x0C-20**, shared with Health) | Implemented (CRUD/toggle/delete/paging) |
| `ProtoRingExt` | `_createRingDataPackage` | ring (**0x91-20**) | Partial+ (command envelope with event/raw-data payload simulation) |
| `ProtoTranslateExt` | `_createTranslateDataPackage` | translate (**0x05-20**) | Implemented (echo + completion path) |
| `ProtoLogExt` | `_createLoggerDataPackage` | logger (**0x0F-20**) | Implemented (file ops + live switch/level/heartbeat ACK/state) |
| `ProtoTaskManagerExt` | `_createSyncInfoDataPackage` | sync_info (**0x20-20**, shared with ModuleConfigure) | Partial (typed ACK + module/system/dashboard subset) |

**Key insight**: Dashboard shares service 0x07-20 with EvenAI, differentiated by the command type field in the protobuf payload (confirmed by i-soxi proto schema). The Conversate extension appears to share routing with Teleprompter (further RE needed to confirm). EvenHub has its own dedicated service 0xE0-20 with handler `evenhub_common_data_handler` — it does NOT share with displayConfig (0x0E-20).

## Adding New Services

When you discover a new service ID:

1. Note the packet context (what triggered it)
2. Capture the full packet sequence
3. Identify the payload structure
4. Document the message types within the service

## Inferred OTA/File Service Vocabulary (Static RE)

Beyond currently-confirmed `0xC4-00`/`0xC5-00` notification transfer behavior, Even.app binary symbols expose a broader OTA command dictionary:

- OTA transmit: `OTA_TRANSMIT_START`, `OTA_TRANSMIT_INFORMATION`, `OTA_TRANSMIT_FILE`, `OTA_TRANSMIT_NOTIFY`, `OTA_TRANSMIT_RESULT_CHECK`
- OTA receive responses: `OTA_RECV_RSP_SUCCESS`, `OTA_RECV_RSP_FAIL`, `OTA_RECV_RSP_HEADER_ERR`, `OTA_RECV_RSP_CRC_ERR`, `OTA_RECV_RSP_FLASH_WRITE_ERR`, `OTA_RECV_RSP_TIMEOUT`, `OTA_RECV_RSP_SYS_RESTART`, etc.
- Generic file service commands: `EVEN_FILE_SERVICE_CMD_SEND_*`, `EVEN_FILE_SERVICE_CMD_EXPORT_*`
- Generic file service responses: `EVEN_FILE_SERVICE_RSP_*`

These are currently treated as **inferred** until full on-wire OTA sessions are captured.

See [firmware-updates.md](../firmware/firmware-updates.md) for the evidence map and state-machine reconstruction.
