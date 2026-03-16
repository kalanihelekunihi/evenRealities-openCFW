# Even Android App — BLE Protocol Layer

> Extracted from `even_android.apk` (com.even.sg) via Dart AOT snapshot analysis, 2026-03-14.

## Overview

The BLE protocol implementation lives in the `even_connect` Dart package, with low-level BLE operations in `flutter_ezw_ble`. The architecture mirrors what we see in the iOS Flutter app (`package:even_connect`) but provides significantly more detail through string analysis of the compiled Dart snapshot.

## Package Hierarchy

```
flutter_ezw_ble/          Low-level BLE driver (platform channel to Kotlin)
  ├── core/models/        BLE primitives (device, config, scan, connect)
  └── flutter_ezw_ble.dart Platform interface

even_connect/             Protocol layer
  ├── core/               Shared services
  │   ├── cmd/            Command protocol (EvenCmdProto, EvenCmdService)
  │   ├── dfu/            DFU upgrade logic
  │   ├── mcu/            MCU firmware update (McuOtaUpgrade)
  │   ├── models/         Shared models
  │   └── mixins/         Reconnect logic
  ├── g1/                 G1 glasses (legacy)
  ├── g2/                 G2 glasses protocol
  │   ├── ble_g2_cmd_proto.dart    Packet construction
  │   ├── ble_g2_cmd_service.dart  Command dispatch
  │   ├── ble_g2_service.dart      High-level service
  │   ├── models/                  G2-specific models
  │   ├── mxins/                   File transfer, OTA extensions
  │   └── proto/generated/         Protobuf definitions (25 services)
  └── ring1/              R1 Ring protocol
      ├── ble_ring1_cmd_proto.dart
      ├── ble_ring1_cmd_service.dart
      ├── ble_ring1_service.dart
      ├── files/           File transfer
      └── models/          Ring models (health, system)
```

## Transport Layer (EvenBleTransport)

### Packet Format
Confirmed identical to iOS/firmware analysis:

```
AA [direction] [sequenceNo] [dataLength] [totalCount] [currentNo] [serviceId_hi] [serviceId_lo] [payload] [CRC16-LE]
```

| Field | Size | Description |
|-------|------|-------------|
| headId | 1 | Always `0xAA` — validated in `fromBytes()` |
| direction | 1 | `0x21` = TX (phone→glasses), `0x12` = RX (glasses→phone) |
| sequenceNo | 1 | Packet sequence number |
| dataLength | 1 | Payload size + 2 (includes service ID bytes) |
| totalCount | 1 | Total packets in multi-packet message |
| currentNo | 1 | Current packet number (0-indexed) |
| serviceId | 2 | Service ID (hi byte + lo byte) |
| payload | N | Protobuf-encoded data |
| CRC16 | 2 | CRC-16/CCITT Little-Endian over payload only |

### Validation (from error strings)
- `"headId is not 0xAA. Received: 0x"` — strict header validation
- `"Data too short for a valid BLE packet. Minimum length is "` — minimum packet size check
- `"Data length mismatch. Expected at least header ("` — length field validation

### Multi-Packet Assembly (EvenBleMultiPacketItem)
- Packets split when payload exceeds MTU
- `totalCount` / `currentNo` track reassembly
- `_splitDataIntoPackets` in BleG2CmdTransportPrivateExt handles splitting
- CRC32 check on reassembled big packages: `"check big package crc32 is success"`

### Transport Queue (BleG2CmdTransportPrivateExt)
- `_processPacketQueue` — Sequential packet dispatch
- `_sendPacketInternal` — Low-level BLE write
- `_waitForPacketResponse` — ACK waiting with timeout
- `_completePacketItemAsCanceled` — Timeout/cancel handling
- `_handleStreamResponse` — RX stream processing
- `_waitForFileServiceIdle` — File service mutex
- `removeCmdQueueByServiceId` — Cancel by service

## BLE Service UUIDs (Complete)

All UUIDs share the base `00002760-08C2-11E1-9073-0E8AC72Exxxx`:

| Short UUID | Full UUID | Description |
|------------|-----------|-------------|
| **0x0001** | 00002760-...-0001 | Primary service declaration |
| **0x0002** | 00002760-...-0002 | Service characteristic (device info?) |
| **0x1001** | 00002760-...-1001 | Unknown (previously unidentified in firmware) |
| **0x5401** | 00002760-...-5401 | EUS TX (phone→glasses control) |
| **0x5402** | 00002760-...-5402 | EUS RX (glasses→phone control) |
| **0x5450** | 00002760-...-5450 | EUS parent/service declaration |
| **0x6401** | 00002760-...-6401 | ESS TX (phone→glasses sensor) |
| **0x6402** | 00002760-...-6402 | ESS RX (glasses→phone sensor/display) |
| **0x6450** | 00002760-...-6450 | ESS parent/service declaration |
| **0x7401** | 00002760-...-7401 | EFS TX (phone→glasses file) |
| **0x7402** | 00002760-...-7402 | EFS RX (glasses→phone file) |
| **0x7450** | 00002760-...-7450 | EFS parent/service declaration |

### NUS (Nordic UART Service)
| Short UUID | Full UUID |
|------------|-----------|
| Service | 6E400001-B5A3-F393-E0A9-E50E24DCCA9E |
| TX (write) | 6E400002-B5A3-F393-E0A9-E50E24DCCA9E |
| RX (notify) | 6E400003-B5A3-F393-E0A9-E50E24DCCA9E |

### R1 Ring
| Short UUID | Full UUID |
|------------|-----------|
| Service | BAE80001-4F05-4503-8E65-3AF1F7329D1F |
| TX | BAE80012-4F05-4503-8E65-3AF1F7329D1F |
| RX | BAE80013-4F05-4503-8E65-3AF1F7329D1F |

**Key discovery**: The `x450` characteristics (0x5450, 0x6450, 0x7450) are the **GATT service declarations** for each pipe. These are the "parent services" referenced in firmware strings that we couldn't map before. Each pipe has a triplet: `x401` (TX), `x402` (RX), `x450` (service declaration).

## BLE Pipe System (BleG2PsType)

Three BLE pipe types (matching iOS analysis):

| BleG2PsType | Value | Characteristic | Description |
|-------------|-------|----------------|-------------|
| EUS | 0 | 5401/5402 | Even UART Service — protobuf control |
| EFS | 1 | 7401/7402 | Even File Service — file transfer |
| ESS | 2 | 6401/6402 | Even Sensor Service — display telemetry |

`selectPipeChannel` in BleG2CmdProtoDeviceSettingsExt — dynamic pipe switching.

## Command Protocol (BleG2CmdProto)

### Data Package Factory Methods
The Android app has 20 `_create*DataPackage` methods in `BleG2CmdProtoExt`:

| # | Method | Service |
|---|--------|---------|
| 1 | `_createDashboardDataPackage` | 0x01-20 Dashboard |
| 2 | `_createNotificationDataPackage` | 0x02-20 Notification |
| 3 | `_createMenuDataPackage` | 0x03-20 Menu |
| 4 | `_createTranscribeDataPackage` | 0x04-xx **Transcribe** (NEW!) |
| 5 | `_createTelepromptDataPackage` | 0x06-20 Teleprompter |
| 6 | `_createEvenAiDataPackage` | 0x07-20 EvenAI |
| 7 | `_createNavigationDataPackage` | 0x08-20 Navigation |
| 8 | `_createConverseDataPackage` | 0x0B-20 Conversate |
| 9 | `_createQuickListDataPackage` | 0x0C-20 Quicklist |
| 10 | `_createHealthDataPackage` | 0x0C-20 Health (shared) |
| 11 | `_createG2SettingDataPackage` | 0x0D-00 Settings |
| 12 | `_createDevCfgDataPackage` | 0x0D-20 DevConfig |
| 13 | `_createGlassesCaseDataPackage` | 0x81-20 GlassesCase |
| 14 | `_createLoggerDataPackage` | 0x0F-20 Logger |
| 15 | `_createOnboardingDataPackage` | 0x10-20 Onboarding |
| 16 | `_createModuleConfigureDataPackage` | 0x20-20 ModuleConfigure |
| 17 | `_createRingDataPackage` | 0x91-20 Ring |
| 18 | `_createFileTransmitDataPackage` | 0xC4/C5 FileTransfer |
| 19 | `_createEvenHubDataPackage` | 0xE0-20 EvenHub |
| 20 | `_createSyncInfoDataPackage` | 0x??-?? **SyncInfo** (NEW!) |

### Device Settings Commands (BleG2CmdProtoDeviceSettingsExt)
- `sendHeartbeat` — Keepalive (type 0x0E)
- `startPair` — Initiate pairing
- `unpair` — Remove pairing
- `createTimeSyncCommand` — Time sync with timezone
- `connectRing` — R1 Ring relay connect
- `disconnect` — Disconnect glasses
- `sendFile` / `receiveFile` — File transfer commands
- `selectPipeChannel` — Switch BLE pipe
- `quickRestart` — Reboot glasses
- `restoreFactory` — Factory reset

### Ring Commands (BleG2CmdProtoRingExt)
- `controlDevice` — Ring device control
- `openRingBroadcast` — Enable ring BLE advertising
- `switchRingHand` — Change wearing hand

## Response Handling (BleG2CmdPsTypeCommonExt)
- `_handleCommonCmd` — Service ID routing
- `_handlePacketResponse` — ACK processing
- `_isPacketResponse` — Check if packet is ACK vs data
- `_parseRetryPackets` — CRC retry logic

### CRC Error Handling
From extracted strings:
```
"crc error, will retry"
"crc error, retry count > "
"crc failed"
"file crc error"
"EVEN_FILE_SERVICE_RSP_DATA_CRC_ERR"
```

## Heartbeat
- `EvenBeatHearPool` — Heartbeat pool manager
- `closeConverse by loss glass HeartBeat` — Feature auto-close on heartbeat loss
- `telepromtHeartBeat---beatHeartLostCount--` — Teleprompter heartbeat tracking

## R1 Ring Protocol

### Service Classes
- `BleRing1Service` — High-level ring service
- `BleRing1CmdService` — Command dispatch
- `BleRing1CmdProto` — Protocol construction

### Command Extensions
| Extension | Commands |
|-----------|----------|
| BleRing1CmdHealthExt | `getDailyData`, `ackNotifyData` |
| BleRing1CmdSettingsStatusExt | `getHealthSettingsStatus`, `getSystemSettingsStatus`, `setHealthEnable`, `setHealthSettingsStatus`, `setSystemSettingsStatus` |
| BleRing1CmdWearStatusExt | `getWearStatus` |
| BleRing1CmdGoMoreExt | `getAlgoKeyStatus`, `setAlgoKey` |
| BleRing1CmdOldExt | `unpair` (legacy) |

### Health Data Models
- `BleRing1HealthPoint` / `BleRing1HealthPointState` — Real-time data
- `BleRing1HealthActivityAllDay` — All-day activity
- `BleRing1HealthActivityDaily` — Daily activity breakdown
- `BleRing1HealthCommonDaily` — Common daily data
- `BleRing1HealthDailyBase` / `BleRing1HealthDailyFactory` — Daily data factory
- `BleRing1HealthHourItem` — Hourly breakdown
- `BleRing1HealthSleep` — Sleep data

### Ring System Models
- `BleRing1SystemInfo` — Device info
- `BleRing1SystemStatus` — Current status
- `BleRing1SystemDeviceSn` — Serial number
- `BleRing1SystemAlgoKey` — Algorithm key (GoMore)
- `BleRing1SystemNvRecover` — NV data recovery
- `BleRing1SystemPackageAck` — Package ACK
- `BleRing1SystemSettingsStatus` — Settings status
- `BleRing1SystemUserInfo` — User info
- `BleRing1SystemWearStatus` — Wearing detection

### Ring File Transfer
- `BleRing1FileServiceMixin` — File transfer mixin
- `BleRing1FileCmdRequest` / `BleRing1FileData` / `BleRing1FileDataReceive`
- `BleRing1FileModel` / `BleRing1FileOriginalData` — File models
- `BleRing1FileExportCmd` / `BleRing1FileRsp` / `BleRing1FileType`

### Ring Charge
- `BleRing1ChargeInfo` — Charge level
- `BleRing1ChargeStatus` — Charging state

## Display Modes
From string extraction:
- `display_mode_dual` — Dual display
- `display_mode_full` — Full screen
- `display_mode_minimal` — Minimal/notification overlay
- `DashboardCombineMode` — Dashboard combination layout
- `TextDisplayMode` — Text rendering mode
- `DEVICE_DISPLAY_MODE` — Device-level display mode setting

## Gesture Control
- `APP_Send_Gesture_Control` — Single gesture action
- `APP_Send_Gesture_Control_List` — Gesture-to-action mapping list
- Gesture customization: full page with binding, controller, out model

## Key Differences from iOS Swift SDK

1. **Transcribe service** — Dedicated `_createTranscribeDataPackage` separate from EvenAI/Translate
2. **SyncInfo service** — New `_createSyncInfoDataPackage` not in iOS implementation
3. **GoMore integration** — Ring algo key for GoMore health platform
4. **Ring NV recovery** — `BleRing1SystemNvRecover` for data recovery
5. **File receive from glasses** — `receiveFile` command (we only have `sendFile`)
6. **Display modes** — Three explicit modes (dual/full/minimal) vs our inferred modes
7. **Dashboard bidirectional** — ReceiveFromApp/RespondToApp/SendToApp pattern
