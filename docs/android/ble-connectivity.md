# Even BLE Connectivity — Complete Reference

> Comprehensive documentation of all Bluetooth connectivity between the Even app and Even Realities G2 Glasses, G2 Case, and R1 Ring, extracted from the Android APK (com.even.sg v2.0.8).

## Device Types and Identification

### Device Type Detection
The app identifies devices via `BleMatchDevice`:

| Accessor | Returns | Purpose |
|----------|---------|---------|
| `isG1` | bool | Even G1 glasses (legacy) |
| `isG2` | bool | Even G2 glasses |
| `isGlasses` | bool | Any glasses (G1 or G2) |
| `isRing` | bool | Any ring device |
| `isRing1` | bool | Even R1 Ring |
| `matchModel` | string | Model identifier |
| `matchRemark` | string | User-assigned nickname |
| `evenSNName` | string | Serial number as display name |

### Device Matching Rules
- `BleMacRule` — MAC address matching rules (JSON-serializable)
- `BleSnRule` — Serial number matching rules (JSON-serializable)
- `BleDeviceSn` — Serial number model
- `BleDeviceHardware` — Hardware revision info

### G2 Hardware Revisions
Device images confirm **two hardware revisions** (G2-A and G2-B), each in 3 colors:
- G2-A: Brown, Green, Grey
- G2-B: Brown, Green, Grey

## BLE Service Architecture

### Class Hierarchy

```
EvenDeviceService (base)
├── BleG1Service (G1 glasses)
│   └── with McuOtaUpgrade, EvenDeviceReconnectMixin
├── BleG2Service (G2 glasses)
│   └── with EvenDeviceReconnectMixin
│       └── BleG2CmdService (command layer)
│           └── with EvenCmdService, BleG2OtaUpgradeMixin, BleG2FileServiceMixin
│               └── BleG2CmdProto (packet construction)
│                   ├── BleG2CmdProtoExt (20 data package creators)
│                   ├── BleG2CmdProtoDeviceSettingsExt (pair/heartbeat/file/etc.)
│                   └── BleG2CmdProtoRingExt (ring relay)
└── BleRing1Service (R1 Ring)
    └── with EvenDeviceReconnectMixin
        └── BleRing1CmdService (command layer)
            └── with EvenCmdService, BleRing1FileServiceMixin
                └── BleRing1CmdProto (packet construction)
```

### Low-Level BLE Driver (flutter_ezw_ble)
Platform channel to native Kotlin:
- `BleConfig` — BLE configuration (JSON-serializable)
- `BleDevice` — Discovered device model
- `BlePrivateService` — Custom GATT service definition
- `BleConnectModel` — Connection parameters
- `BleScan` — Scan configuration
- `BleStatus` — BLE adapter status
- `BleConnectState` — Connection state enum
- `BleEventChannel` — Event channel for BLE notifications

## G2 Glasses BLE Profile

### GATT Services (Full 128-bit UUIDs)

All Even-specific UUIDs share base `00002760-08C2-11E1-9073-0E8AC72Exxxx`:

#### Even UART Service (EUS) — Protobuf Control
| Role | UUID Short | Full UUID | Properties |
|------|-----------|-----------|------------|
| Service | 0x5450 | 00002760-08C2-11E1-9073-0E8AC72E5450 | GATT service declaration |
| TX (phone→glasses) | 0x5401 | 00002760-08C2-11E1-9073-0E8AC72E5401 | Write Without Response |
| RX (glasses→phone) | 0x5402 | 00002760-08C2-11E1-9073-0E8AC72E5402 | Notify |

#### Even File Service (EFS) — File Transfer & OTA
| Role | UUID Short | Full UUID | Properties |
|------|-----------|-----------|------------|
| Service | 0x7450 | 00002760-08C2-11E1-9073-0E8AC72E7450 | GATT service declaration |
| TX (phone→glasses) | 0x7401 | 00002760-08C2-11E1-9073-0E8AC72E7401 | Write Without Response |
| RX (glasses→phone) | 0x7402 | 00002760-08C2-11E1-9073-0E8AC72E7402 | Notify |

#### Even Sensor Service (ESS) — Display Telemetry
| Role | UUID Short | Full UUID | Properties |
|------|-----------|-----------|------------|
| Service | 0x6450 | 00002760-08C2-11E1-9073-0E8AC72E6450 | GATT service declaration |
| TX (phone→glasses) | 0x6401 | 00002760-08C2-11E1-9073-0E8AC72E6401 | Write Without Response |
| RX (glasses→phone) | 0x6402 | 00002760-08C2-11E1-9073-0E8AC72E6402 | Notify |

#### Additional Characteristics
| UUID Short | Full UUID | Description |
|-----------|-----------|------------|
| 0x0001 | 00002760-08C2-11E1-9073-0E8AC72E0001 | Primary service declaration |
| 0x0002 | 00002760-08C2-11E1-9073-0E8AC72E0002 | Service characteristic |
| 0x1001 | 00002760-08C2-11E1-9073-0E8AC72E1001 | Unknown function |

#### Nordic UART Service (NUS) — Gestures, Mic, Text
| Role | UUID |
|------|------|
| Service | 6E400001-B5A3-F393-E0A9-E50E24DCCA9E |
| TX (phone→glasses) | 6E400002-B5A3-F393-E0A9-E50E24DCCA9E |
| RX (glasses→phone) | 6E400003-B5A3-F393-E0A9-E50E24DCCA9E |

NUS carries raw (non-protobuf) data: gesture events, microphone PCM audio, text display commands, heartbeat.

### BLE Pipe System (BleG2PsType)

Three logical pipes multiplex over the GATT services:

| Pipe | BleG2PsType | Characteristics | Purpose |
|------|-------------|----------------|---------|
| EUS | 0 | 5401/5402 | Protobuf command/response |
| EFS | 1 | 7401/7402 | File transfer, OTA |
| ESS | 2 | 6401/6402 | Display sensor telemetry |

**Pipe switching**: `selectPipeChannel` / `PipeRoleChange` / `PIPE_ROLE_CHANGE`

The pipe system enables dynamic routing — a characteristic pair can switch between roles using the PipeRoleChange protobuf message (part of the DevPairManager protocol).

## R1 Ring BLE Profile

### GATT Service
| Role | UUID |
|------|------|
| Service | BAE80001-4F05-4503-8E65-3AF1F7329D1F |
| TX (phone→ring) | BAE80012-4F05-4503-8E65-3AF1F7329D1F |
| RX (ring→phone) | BAE80013-4F05-4503-8E65-3AF1F7329D1F |

### Ring Communication Modes
1. **Direct**: Phone ↔ Ring (via BAE8xxxx service)
2. **Relay via Glasses**: Phone → G2 (0x91-20 Ring service) → Inter-eye UART → R1

### Ring Connection Constants
- `RING_CONNECT_INFO` — Connection info message
- `RING_CONNECT_TIMEOUT` — Connection timeout
- `RING_GLASSES` — Ring-glasses binding state

### Ring Bind Status
- `BleGlassesRingBindStatus` — Tracks binding between glasses and ring
- Ring can be bound/unbound from glasses independently of phone pairing

## Connection Lifecycle

### 1. Discovery (BLE Scan)

```
EvenDeviceDiscovery
  ├── _startScan → startScan (native BLE)
  ├── stopScan
  ├── updateFoundDevices → DeviceDiscoveryWidgetPanel|assembleFoundDevicesList
  ├── _cancelScanningStopTimer / _setupScanningStopTimer
  └── _handleDeviceConnectStatus
```

**BleDiscoveryConnectState** tracks scan/connect state:
- Scanning, Found, Connecting, Connected, Error

**BleDiscoveryController actions:**
- `clearFoundDevicesAndReSearch` — Clear cache, restart scan
- `connectFoundDevice` — Connect to discovered device
- `connectMyDevice` — Reconnect to known device
- `showDfuUpdateDialog` — Prompt firmware update
- `_sortLastConnectDevices` — Sort by last connection time
- `_syncMyDevices` — Sync device list

### 2. Connection

**BleConnectState** enum (with extensions):
- `isConnecting` — Currently connecting
- `isError` — Connection error state

**Device connect state tracking:**
- `DeviceConnectState` — Current connection state
- `DeviceReconnectState` — Reconnection state
- `DisconnectState` — Disconnect state

### 3. Pairing/Authentication

After BLE connection, the auth handshake runs on service 0x80:

**DevPairManager** protobuf messages:
- `AuthMgr` — Authentication manager (7-packet auth sequence)
- `BleConnectParam` — Connection parameters
- `PipeRoleChange` — Pipe role assignment after auth
- `RingInfo` — Ring info if ring is connected
- `UnpairInfo` / `DisconnectInfo` — Cleanup messages

**Auth commands:**
- `BleG2CmdProtoDeviceSettingsExt|startPair` — Initiate pairing
- `BleG2CmdProtoDeviceSettingsExt|unpair` — Remove pairing

### 4. Time Sync

Immediately after auth:
- `BleG2CmdProtoDeviceSettingsExt|createTimeSyncCommand` — Unix timestamp + timezone offset
- Uses `flutter_timezone` for local timezone detection

### 5. Heartbeat

**Two heartbeat layers:**

#### a) BLE Connection Heartbeat (type 0x0E on 0x80-00)
- `BleG2ServicePrivateExt|_executeBleConnectHeartBeat` — Low-level BLE keepalive
- `BleG2ServicePrivateExt|_executeHeartbeat` — Heartbeat execution
- `BleG2ServicePublicExt|startBleHeartbeat` / `resetHeartbeat`
- `_heartbeatManager` — Manages heartbeat timer
- `_monitorHeartbeat` / `_startHeartbeatMonitor` / `_stopHeartbeatMonitor`
- `_incrementHeartbeatFailureCount` — Tracks missed heartbeats

#### b) Service-Specific Heartbeats
Each active feature has its own heartbeat:
- `ConversateHeartBeat` — Conversate keepalive
- `TelepromptHeartBeat` — Teleprompter keepalive
- `TranslateHeartBeat` — Translate keepalive
- `TranscribeHeartBeat` — Transcribe keepalive
- `EvenAIHeartbeat` — EvenAI keepalive
- `OnboardingHeartbeat` — Onboarding keepalive
- `HeartBeatPacket` — EvenHub keepalive

**Heartbeat loss handling:**
- `closeConverse by loss glass HeartBeat` — Auto-close Conversate
- `telepromtHeartBeat---beatHeartLostCount--` — Track Teleprompter heartbeat misses
- `_handleHeartBeat bearBeat is null` — Missing heartbeat handling
- `{"pkg_type":"heartbeat"}` — WebSocket heartbeat (for Conversate cloud)

### 6. Reconnection

All three device types use `EvenDeviceReconnectMixin`:
- G2: `_BleG2Service&EvenDeviceService&EvenDeviceReconnectMixin`
- G1: `_BleG1Service&EvenDeviceService&McuOtaUpgrade&EvenDeviceReconnectMixin`
- Ring: `_BleRing1Service&EvenDeviceService&EvenDeviceReconnectMixin`

**Reconnection methods:**
- `_attemptReconnect` — Try reconnection
- `_calculateReconnectDelay` — Exponential backoff
- `_reconnectWithDelay` — Delayed reconnect
- `_startReconnectTimer` / `_clearReconnectTimer` — Timer management
- `_triggerReconnect` — Trigger reconnect cycle
- `_cancelBleReconnectTimer` / `_startBleReconnectTimer` — BLE-specific timers
- `_startReconnectionTimeoutTimer` / `_cancelReconnectionTimeoutTimer` — Max reconnect timeout
- `_resetReconnectState` — Reset reconnect state machine
- `need reconnect` — Reconnection flag
- `_reconnectWithDelay return with already reconnectTimer` — Debounce duplicate reconnects

**Connection loss strings:**
- `app_lost_connection_to_glasses` — Glasses disconnected notification
- `app_lost_connection_to_ring` — Ring disconnected notification

### 7. Disconnect

**Disconnect methods:**
- `BleG2CmdProtoDeviceSettingsExt|disconnect` — Graceful disconnect
- `_unpairDevice` — Full unpair with data cleanup
- `_clearConnectTempData` — Clear temporary connection data

## G1 Glasses — Dual-Eye Protocol

The G1 uses a different model: **left and right eye are separate BLE peripherals**:

- `BleG1CmdServicePublicExt|sendLeftData` — Send to left eye only
- `BleG1CmdServicePublicExt|sendRightData` — Send to right eye only
- `BleG1CmdServicePublicExt|sendBothData` — Send to both eyes

The G2 does NOT have separate left/right sending — it uses a single BLE connection with inter-eye UART relay (L=master, R=slave).

## Packet Transport (G2)

### EvenBleTransport Packet Format
```
AA [direction] [seq] [len] [total] [current] [svcId_hi] [svcId_lo] [payload] [CRC16-LE]
```

- Header: 8 bytes (headId=0xAA, direction, sequenceNo, dataLength, totalCount, currentNo, serviceId×2)
- `dataLength` = payload_size + 2 (includes serviceId bytes)
- CRC-16/CCITT over payload only (init=0xFFFF, poly=0x1021)
- Direction: `0x21` = TX (phone→glasses), `0x12` = RX (glasses→phone)

### Multi-Packet Assembly
- `_splitDataIntoPackets` — Split large payloads
- `EvenBleMultiPacketItem` — Reassembly buffer
- `totalCount` / `currentNo` — Track fragment position
- CRC32 verification on reassembled data: `check big package crc32 is success`

### Transport Queue
```
BleG2CmdTransportPublicExt|sendData
  → _processPacketQueue (sequential dispatch)
    → _sendPacketInternal (BLE write)
    → _waitForPacketResponse (ACK wait)
    → _handleStreamResponse (RX processing)
```

- `removeCmdQueueByServiceId` — Cancel pending commands for a service
- `clearCmdQueue` — Clear all pending commands
- `_waitForFileServiceIdle` — Mutex for file service (EFS pipe)
- `_completePacketItemAsCanceled` — Cancel on timeout
- `_parseRetryPackets` — CRC retry logic

### CRC Error Handling
```
"crc error, will retry"
"crc error, retry count > "
"crc failed"
"file crc error"
"EVEN_FILE_SERVICE_RSP_DATA_CRC_ERR"
```

## File Transfer Protocol (EFS Pipe)

### Send (Phone → Glasses)
```
BleG2SendFileExt|sendFile
  → _sendFileCmd (command)
  → _sendFileData (data chunks)
  → _sendFilePackets (packet stream)
```

- `EvenSendFileCmd` — Send command
- `EvenSendFileBigPackage` — Large file assembly

### Receive (Glasses → Phone)
```
BleG2ReceiveFileExt|receiveFile
  → EvenReceiveFileBigPackage (assembly)
```

- `EvenExportFileCmd` — Export command
- `EvenReceiveFileBigPackage` — Received file assembly
- `receiveFileCrc32` — CRC32 verification

### File Service Commands
| Phase | Send | Export |
|-------|------|--------|
| Start | `EVEN_FILE_SERVICE_CMD_SEND_START` | `EVEN_FILE_SERVICE_CMD_EXPORT_START` |
| Data | `EVEN_FILE_SERVICE_CMD_SEND_DATA` | `EVEN_FILE_SERVICE_CMD_EXPORT_DATA` |
| Check | `EVEN_FILE_SERVICE_CMD_SEND_RESULT_CHECK` | `EVEN_FILE_SERVICE_CMD_EXPORT_RESULT_CHECK` |

### File Service Response Codes
| Code | Description |
|------|-------------|
| `RSP_SUCCESS` | Success |
| `RSP_FAIL` | General failure |
| `RSP_DATA_CRC_ERR` | CRC mismatch |
| `RSP_FLASH_WRITE_ERR` | Flash write error |
| `RSP_NO_RESOURCES` | Out of resources |
| `RSP_RESULT_CHECK_FAIL` | Final check failed |
| `RSP_START_ERR` | Start command error |
| `RSP_TIMEOUT` | Timeout |

## Wear Detection and Display Activation

### Wear Detection
- `GLS_WEAR_STATUS` — Glasses wear status
- `Wear_Detection_Setting` — Enable/disable wear detection
- `isSendAllow isWearing = false` — **BLE TX gated by wear status**
- `deviceReceiveWearDetection` — Wear status change notification

### Display Wake
- `DEVICE_WAKEUP_ANGLE` — Configurable wake angle
- `IWakeUpHandler` — Wakeup handler interface
- AI agent state: `enter -> WakeUp state` / `exit <- WakeUp state`

## Device Configuration over BLE

### DevConfig Settings (0x0D-20)
| Setting ID | Constant | Description |
|-----------|----------|-------------|
| Brightness | `DEVICE_BRIGHTNESS` | Display brightness level |
| Anti-shake | `DEVICE_ANTI_SHAKE_ENABLE` | Anti-shake toggle |
| Display mode | `DEVICE_DISPLAY_MODE` | Full/dual/minimal |
| Work mode | `DEVICE_WORK_MODE` | Device work mode |
| Wakeup angle | `DEVICE_WAKEUP_ANGLE` | Display activation angle |
| BLE MAC | `DEVICE_BLE_MAC` | BLE MAC address |
| Device SN | `DEVICE_DEVICE_SN` | Device serial number |
| Glasses SN | `DEVICE_GLASSES_SN` | Glasses serial number |
| Logger data | `DEVICE_SEND_LOGGER_DATA` | Send log data |

### G2 Settings (0x0D-00)
Bidirectional settings via `G2SettingPackage`:
- **Brightness**: `setBrightness`, `setBrightnessAuto`, `setBrightnessCalibration`
- **Display Position**: `setGlassGridDistance`, `setGlassGridHeight`
- **Coordinates**: `DeviceReceive_X_Coordinate`, `DeviceReceive_Y_Coordinate`
- **Head-Up**: `DeviceReceive_Head_UP_Setting`, `headUpSetting`
- **Silent Mode**: `DeviceReceive_Silent_Mode_Setting`, `setSilentMode`
- **Wear Detection**: `setWearDetection`
- **Gestures**: `setGestureControlList`, `APP_Send_Gesture_Control_List`
- **Hand**: `APP_Send_Dominant_Hand`
- **Screen Off**: `requestScreenOffInterval`, `updateScreenOffInterval`
- **Onboarding**: `setOnBoardingStartUp`, `setOnBoardingStart`, `setOnBoardingEnd`
- **Language**: `sendSysLanguageChangeEvent`
- **Query**: `getGlassesCaseInfo`, `getGlassesConfig`, `getGlassesIsWear`, `getBoardingIsHeadup`

## Ring Protocol Details

### R1 Ring Command Extensions
| Extension | Methods |
|-----------|---------|
| `BleRing1CmdHealthExt` | `getDailyData`, `ackNotifyData` |
| `BleRing1CmdSettingsStatusExt` | `getHealthSettingsStatus`, `getSystemSettingsStatus`, `setHealthEnable`, `setHealthSettingsStatus`, `setSystemSettingsStatus` |
| `BleRing1CmdWearStatusExt` | `getWearStatus` |
| `BleRing1CmdGoMoreExt` | `getAlgoKeyStatus`, `setAlgoKey` |
| `BleRing1CmdOldExt` | `unpair` (legacy) |

### Ring Relay via Glasses (0x91-20)
| Command | Description |
|---------|-------------|
| `controlDevice` | Control ring through glasses |
| `openRingBroadcast` | Enable ring BLE advertising (for pairing) |
| `switchRingHand` | Change wearing hand (isLeft=true/false) |

### Ring Events
- `eRingEvent` — Ring event enum
- `RingEvent` / `RingEventDto.fromPb` — Event data with DTO conversion
- `RingRawData` — Raw data relay from ring through glasses
- `onListenOsRingEvent` — Ring event listener

### Ring Health Data (via BLE)
| Model | Data |
|-------|------|
| `BleRing1HealthPoint` | Real-time sensor data |
| `BleRing1HealthActivityAllDay` | Full day activity |
| `BleRing1HealthActivityDaily` | Daily breakdown |
| `BleRing1HealthCommonDaily` | Common daily metrics |
| `BleRing1HealthSleep` | Sleep analysis |
| `BleRing1HealthHourItem` | Hourly granularity |
| `BleRing1ChargeInfo` / `ChargeStatus` | Battery level and charging |

### Ring System Info (via BLE)
| Model | Data |
|-------|------|
| `BleRing1SystemInfo` | Device info |
| `BleRing1SystemStatus` | Current status |
| `BleRing1SystemDeviceSn` | Serial number |
| `BleRing1SystemAlgoKey` | GoMore algorithm key |
| `BleRing1SystemNvRecover` | NV data recovery |
| `BleRing1SystemPackageAck` | Package ACK |
| `BleRing1SystemSettingsStatus` | Settings state |
| `BleRing1SystemUserInfo` | User profile on ring |
| `BleRing1SystemWearStatus` | Wearing detection |

### Ring File Transfer
- `BleRing1FileServiceMixin` — File transfer over BLE
- `BleRing1FileCmdRequest` / `BleRing1FileData` / `BleRing1FileDataReceive`
- `BleRing1FileModel.fromBytes` / `BleRing1FileOriginalData.fromBytes`
- `BleRing1FileExportCmd` / `BleRing1FileRsp` / `BleRing1FileType`
- `startReceiveFile` / `resetFileReceiveState` — Receive lifecycle

## Glasses Case (0x81-20)

The G2 case communicates with glasses via internal UART (not direct BLE to phone):

- `GlassesCaseDataPackage` — Case data wrapper
- `GlassesCaseInfo` — Case state: SOC, charging, lid open, in-case
- `UX_GLASSES_CASE_APP_ID` — App ID for case service
- `inCaseStatus` — Whether glasses are in case
- `glasses_in_case_reminder_during_updating` — Warning: don't put in case during OTA

## DFU/OTA BLE Details

### G2 Glasses OTA (EVENOTA)
- Uses EFS pipe (0xC4/0xC5)
- 4-phase: START → INFORMATION → FILE → RESULT_CHECK
- `BleG2OtaUpgradeMixin` mixed into BleG2CmdService
- `UX_OTA_TRANSMIT_CMD_ID` / `UX_OTA_TRANSMIT_RAW_DATA_ID`

### R1 Ring DFU (Nordic)
- 8 parallel `DfuService` instances in Android manifest
- `_calculateAndroidDfuMac` — Calculate DFU-mode MAC address
  - `DFU address mapping: ` — Log of MAC calculation
  - `DFU address mapping skipped (invalid mac): ` — Invalid MAC handling
- DFU states: starting → started → upgrading → completed/error/aborted/disconnected

### Case MCU Update
- `McuOtaUpgrade` mixin
- `mcumgr_flutter` package (Nordic MCU Manager SMP protocol)
- `McuManifest` / `McuManifestFile` — Update manifest

## BLE Audio Path (Glasses Mic → Phone)

### LC3 Codec (Decode Only)
The glasses encode microphone audio with LC3 and send it over NUS. The phone decodes:

```
Glasses Mic → LC3 encode (GX8002B chip) → NUS BLE → Phone LC3 decode → PCM
```

**LC3 FFI bindings** (via `liblc3.so`, 173KB):
- `lc3_setup_decoder` — Initialize decoder with sample rate and frame duration
- `lc3_decoder_size` — Query decoder memory requirement
- `lc3_frame_samples` — Query output sample count
- `lc3_decode` — Decode one LC3 frame to PCM

Note: **Decode only** — the phone never sends LC3 audio to glasses.

### Audio Source Management
The app switches between phone microphone and glasses BLE microphone:

```
"App is in foreground with microphone setting, will attempt to use microphone.
 If startup fails, will automatically switch to bluetooth."
"App is in background, forcing bluetooth audio source to avoid foreground service"
"Audio manager start timeout after 3 seconds (bluetooth retry)"
```

**AndroidAudioSource** enum controls the source selection:
- Foreground: Prefers phone mic, falls back to BLE
- Background: Forces BLE audio to avoid needing foreground mic service
- `_initAudioInputSource` — Initialize based on app state
- `Audio input source switched to:` — Log when source changes

### Audio Pipeline
```
LC3 Decode → Speech Enhancement (libeven.so) → AGC → ASR/VAD
```

## MTU and Payload Size

- `currentMtu` — Current negotiated MTU
- `realMtu` — Actual usable MTU (after protocol overhead)
- `_maxPayloadSize` — Maximum payload per BLE write
- MTU affects `_splitDataIntoPackets` — larger MTU = fewer packets

## TX Gating (Send Permission)

BLE transmission is gated by multiple conditions:

```dart
get:isSendAllow  // Master gate
```

**Checks performed:**
1. `isSendAllow isDeviceConnected = false` — Device must be connected
2. `isSendAllow isWearing = false` — Glasses must be worn (wear detection)
3. `isSendingCmd` — Not already sending (mutex)
4. `_checkCanSendData` (G1) — G1-specific send check
5. `isSendFileResponse` — File transfer mutex
6. `_doUpdateNews not SendAllow` — News blocked when send not allowed

**Implication**: Features like Conversate, Teleprompter, and EvenAI will not send data to glasses that are not being worn.

## Ring Multi-Packet Protocol

The R1 Ring uses a **different multi-packet protocol** from G2:

- **UUID-based tracking** (not sequence number): `Ring1 Receive multi packet - uuid:`
- **CRC32 verification**: `Ring1 Receive multi packet - crc32 not match`
- `_handleMultiPacket` — Assembly in `BleRing1CmdPrivateExt`
- `Ring1 Receive multi packet finish -` — Assembly complete
- `Ring1 Send Cmd - uuid is empty` — Error: missing UUID

### Ring Transfer
- `BleRing1Transfer` — Transfer state machine
- `BleRing1TransferDelegate` — Transfer delegate/callback
- `Ring1 Process is sending:` — Active transfer indicator
- `Ring1 File Service - Handle receive: uuid =` — File receive routing

## DFU BLE Specifics

### G2 DFU Mode
- Glasses advertise with **alternative name** in DFU mode
- `alternativeAdvertisingName` / `alternativeAdvertisingNameEnabled`
- `enableScanningForNewAddress` — Scan for new DFU address
- `forceScanningForNewAddressInLegacyDfu` — Legacy DFU compat

### Android DFU MAC Calculation
Nordic DFU on Android changes the device MAC address:
```
_calculateAndroidDfuMac — Derive DFU-mode MAC from normal MAC
_setupAndroidDfuAddressMapping — Map normal→DFU address
"DFU address mapping: " — Log the mapping
"DFU address mapping skipped (invalid mac): " — Skip if invalid
```

### DFU State Machine
```
starting → started → upgrading → completed
                         ↓
                    error / aborted / disconnected
```

All states logged with `originalAddress:` for tracking.

## Connection Flow Events

### Sequence
```
scan (startScan) → found (updateFoundDevices)
  → onDeviceConnecting → BLE connect
    → onDeviceConnected → afterConnected
      → Auth (0x80 service) → TimeSync → startBleHeartbeat
        → Ready (isReady)
```

### Disconnect
```
onDeviceDisconnecting → _cleanupBluetoothResources
  → onDeviceDisconnected → _showBluetoothDisconnectedToast
    → _attemptReconnect (if auto-reconnect enabled)
```

### Event Handlers
- `BleG2ServicePrivateExt|_handleConnectedNotify` — Post-connect init
- `_subscribeBluetoothPush` — Subscribe to BLE push events
- `_subscribeDeviceConnect` — Subscribe to connect state changes
- `_listenBluetoothConnection` — Monitor connection state
- `_recheckBluetoothConnection` — Re-verify connection
- `_dismissBluetoothToast` — Dismiss disconnect toast on reconnect

### Bluetooth Disconnect Handling
```
" ignored due to Bluetooth disconnection"  — Operations skipped
"Bluetooth reconnect timeout ("  — Reconnect timed out
_cleanupBluetoothResources  — Free BLE resources
_showBluetoothDisconnectedToast  — User notification
_dismissBluetoothToast  — Clear on reconnect
```

## Navigation BLE Service Layer

Navigation has a dedicated BLE service wrapper (`NavigateBleService`) with command and listener halves:

### NavigateBleServiceCommand (App → Glasses)
| Method | Description |
|--------|-------------|
| `_sendNavigationStart` | Start navigation on glasses |
| `_sendNavigationStop` | Stop navigation |
| `_sendNavigationArrive` | Arrival notification |
| `_sendNavigationBasicInfo` | Send distance, time, street info |
| `_sendNavigationMiniMap` | Send mini map image |
| `_sendNavigationOverviewMap` | Send overview map image |
| `_sendNavigationHeartbeat` | Navigation keepalive |
| `_sendNavigationRecalculating` | Rerouting notification |
| `_sendNavigationFavoriteList` | Send favorite locations |
| `_sendNavigationDeviceStartError` | Report start error |
| `_updateNavigationProgress` | Update progress data |
| `_updateLatestMiniMapData` | Update mini map data |
| `_updateLatestOverviewMapData` | Update overview map |
| `_transformMapData` | Transform map for glasses display |
| `_processDataInIsolate` | Process map data in isolate (background thread) |

### NavigateBleServiceListener (Glasses → App)
| Method | Description |
|--------|-------------|
| `_initListener` | Initialize glasses event listener |
| `_showGlassesNavigationLoading` | Show loading on glasses |
| `_hideGlassesNavigationLoading` | Hide loading |
| `_ensureNavigationPageAndShowLoading` | Ensure nav page active |
| `_buildGlassesNavigationLoadingWidget` | Build loading widget |
| `checkAndHideGlassesNavigationLoading` | Check and clean up |

### Navigation Data Flow
```
Mapbox SDK → EvenNavigationProgress → NavigateBleServiceCommand
  → _createNavigationDataPackage → BLE (0x08-20)
    → basic_info_msg / compass_info_msg / mini_map_msg / max_map_msg
```

### Navigation Exit
- `EvenNavigationExitReason` — Enum for why navigation ended

## Feature BLE Callback Architecture

Features use a two-layer callback pattern to bridge BLE and UI:

### ActionCallback (UI → BLE)
| Feature | Callback | Implementation |
|---------|----------|---------------|
| Conversate | `ConversateActionCallback` | `ConverseActionCallbackImpl` |
| Dashboard | `DashBoardActionCallback` | `DashBoardActionCallbackImpl` |
| Teleprompter | `TeleprompterActionCallback` | `TeleprompterActionCallbackImpl` |

### ProtoCallback (BLE → Feature)
| Feature | Callback | Implementation |
|---------|----------|---------------|
| Conversate | `ConverseProtoCallback` | `ConverseProtoCallbackImpl` |
| Dashboard V2 | `DashboardSendProV2Callback` | `DashBoardSendProV2CallbackImpl` |
| Dashboard V3 | `DashboardSendProV3Callback` | `DashBoardSendProV3CallbackImpl` |
| Teleprompter | `TeleprompterSendProtoV2Callback` | `TeleprompterSendProtoV2CallbackImpl` |

Accessed via `getActionCallback` / `getProtoCallback` on the service instances.

## Ring Low Performance Mode

The R1 Ring supports a **low performance mode** for power saving:
- `setRingLowPerformanceMode` — Toggle low-power mode
- `_refreshRingLowPerformanceMode` — Query current state
- `_applyRingLowPerformanceMode` — Apply setting
- Error handling: "not connected", "Failed to get ring settings", "Failed to set low performance mode"

## Android Notification Forwarding

Android uses `NotificationListenerService` to intercept all device notifications:
- `EvNLService` — The listener service (foregroundServiceType=specialUse)
- `startNotificationListener` / `isNotificationListenerEnabled`
- `openNotificationListenerSetting` — Open system settings to grant permission
- Notifications are forwarded via `NotificationDataPackage` (0x02-20) with `NotificationIOS` format (even on Android)

## R1 Charger Identification

The R1 Ring Charger (cradle) has its own regulatory info:
- Model: "Even R1 Charger"
- FCC ID: `2BFKR-R1C`
- IC: `32408-R1C`

## BLE Disconnect Resilience (Translation)

Translation has special handling for BLE disconnect — it **continues using the phone microphone** instead of stopping:

```
"Resuming translation from bleDisconnected state (continuing with phone microphone)"
"Cannot pause translation in bleDisconnected state, translation continues"
"Resetting from bleDisconnected to idle before starting translation"
"Pause button clicked in bleDisconnected state, ignoring"
```

States: `bleDisconnected`, `bleError`, `bleState`, `bleStateConfig`

This is the only feature with BLE disconnect resilience — Conversate and Teleprompter close on heartbeat loss.

## BLE Logger Transport

The logger service (0x0F-20) has BLE-level transport configuration:
- `ble_trans_level_msg` — Set BLE transport log level
- `bleTransLevel` — Current transport log level
- `bleTransEn` — Transport logging enabled flag
- `BLE_LOGGER_LEVEL_SET` — Level set command
- `BLE_LOGGER_SWITCH_SET` — Enable/disable toggle

## BLE Audio Input Source

- `ble_audio_input_source` — Audio source identifier for BLE mic input
- `ble_audio_input_source_` — Prefix for source configuration
- Used by the audio source management system to select between phone mic and glasses BLE mic

## BLE Hardware Version

- `bleHwVer` — BLE hardware version field (from DeviceInfo)
- Identifies the EM9305 BLE chip hardware revision

## BLE Plugin Origin

The low-level BLE plugin (`flutter_ezw_ble`) is by **fzfstudio** (`com.fzfstudio.ezw_ble`):
- `FlutterEzwBlePluginKt` — Plugin entry point
- `BleChannelKt` — Method/event channel bridge
- `BluetoothDeviceExtKt` — Device Kotlin extensions
- "ezw" = Even's internal framework name (also in `flutter_ezw_asr`, `flutter_ezw_audio`, `flutter_ezw_utils`)

## Device Info Over BLE (0x09-xx)

The `DeviceInfo` protobuf message provides these BLE-accessible fields:
| Sub-message | Description |
|-------------|-------------|
| `ALSInfo` | Ambient light sensor reading |
| `HeadAngle` | Current head tilt angle |
| `BleMac` | BLE MAC address |
| `SnInfo` | Serial number |
| `Mode` | Current device mode |
| `DeviceInfoValue` | Generic key-value pairs |

## BleDeviceWorkInfo

Aggregated device state model:
```
BleDeviceWorkInfo(maxBrightness: ..., workMode: ...)
```
- `maxBrightness` — Per-eye max brightness (DAC scale 0-42)
- `workMode` — Current device work mode (`BleDeviceWorkMode` enum)

## BleG2MainPb

Top-level protobuf wrapper for all G2 commands:
- `BleG2MainPb` — Main protobuf container class
- `BleG2MainPb.empty` — Factory for empty/default instance
- Routes to specific DataPackage based on service ID

## BleG2GlassesFilePath

Model for glasses-side file system paths:
- Used by teleprompter file management (FileList/FileSelect)
- Used by logger file management (request_filelist_msg)
- Represents paths on the glasses' LittleFS filesystem

## Summary: What Connects to What

```
Phone ←──BLE──→ G2 Glasses (Left=Master)
  │                 │
  │                 ├── Inter-eye UART ──→ G2 Glasses (Right=Slave)
  │                 │
  │                 └── Ring Relay (0x91-20) ──→ R1 Ring
  │                        (via glasses internal radio)
  │
  ├──BLE──→ R1 Ring (direct, BAE8xxxx)
  │           └── Health data, System info, File transfer
  │
  └──BLE──→ G2 Case (indirect, via glasses 0x81-20)
              └── SOC, Charging, Lid state, In-case detect
```

### BLE Connections Summary
| Device | Service UUIDs | Packet Format | Auth |
|--------|--------------|---------------|------|
| G2 Glasses | Even (5450/6450/7450) + NUS (6E40xxxx) | 0xAA protobuf + CRC16 | 7-packet on 0x80 |
| R1 Ring | BAE8xxxx | Custom ring protocol | Init: 0xFC, 0x11 |
| G2 Case | Not direct BLE — via glasses | Via 0x81-20 service | N/A (through glasses) |
| G1 Glasses | Even (5450/6450/7450) + NUS | Same as G2 but dual-connection (L+R) | Similar |
