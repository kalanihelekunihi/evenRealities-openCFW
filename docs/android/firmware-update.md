# Even Android App — Firmware Update (OTA/DFU)

> Extracted from `even_android.apk` (com.even.sg), 2026-03-14.

## Overview

The Even app supports three firmware update paths:
1. **G2 Glasses OTA** — EVENOTA format over BLE (0xC4/0xC5 services)
2. **R1 Ring DFU** — Nordic DFU (nRF) protocol via `mcumgr_flutter`
3. **MCU Update** — Case MCU firmware via `McuOtaUpgrade`

## G2 Glasses OTA

### Classes
| Class | Description |
|-------|-------------|
| `BleG2OtaUpgradeMixin` | OTA upgrade logic mixed into BleG2CmdService |
| `BleG2OtaHeader` | OTA file header parser (`fromBytes`) |
| `BleG2OtaDevice` | Device OTA state |
| `BleG2OtaEvent` | OTA progress/status events |
| `EvenOtaComponentInfo` | EVENOTA component metadata (`fromBytes`) |
| `EvenOtaUpgradeCmd` | OTA command types |
| `FirmwareUpdateManager` | High-level update orchestration |
| `FirmwareUpdateLogger` | OTA process logging |
| `FirmwareUpdateMode` | Update mode enum |

### OTA Header
From string: `BleG2OtaHeader{otaMagic1: ... components, otaMagic2: ...}`
- `otaMagic1` — First magic number for EVENOTA container
- `otaMagic2` — Second magic number
- Components parsed individually from EVENOTA container

### OTA File Structure (EVENOTA)
Confirmed via `EvenOtaComponentInfo.fromBytes`:
- 6-entry container format matching iOS/firmware analysis
- Components: BLE EM9305, Box MCU, Codec GX8002B, Touch CY8C4046FNI, S200 Bootloader, S200 Firmware

### OTA Transport
- Uses `BleG2FileServiceMixin` (mxins/ble_g2_cmd_service_ota_ext.dart)
- File transfer over EFS pipe (0xC4/0xC5 characteristics)
- Multi-packet with CRC32 verification
- Progress events via `BleG2OtaEvent`
- File CRC validation: `"file length or crc32 is 0"`, `"check file crc32 is correct = true"`

### Firmware API
- `ApiServiceCommonExt.checkLatestFirmware` — Check for updates
- `ApiServiceCommonExt.checkFirmware` — Legacy check
- `ApiServiceCommonExt.syncFirmware` — Report installed version
- CDN: `cdn.evenreal.co` for firmware downloads

### DeviceOtaInfo Model
- `_$DeviceOtaInfoFromJson` / `_$DeviceOtaInfoToJson` — JSON serialization
- Contains firmware version info and update availability

## R1 Ring DFU

### Nordic DFU Implementation
- **8 parallel DFU service instances** in AndroidManifest:
  - `dev.steenbakker.nordicdfu.DfuService` through `DfuService8`
  - All with `foregroundServiceType="connectedDevice"`
- Uses `mcumgr_flutter` package for MCU Manager protocol
- `nordic_dfu` Flutter plugin wrapping Android Nordic DFU library

### DFU Classes
| Class | Description |
|-------|-------------|
| `DfuUpgrade` | Main upgrade logic |
| `DfuUpgradeState` | State machine (process states) |
| `DfuUpgradeType` | Type enum (bootloader, softdevice, app) |
| `DfuEventHandler` | Event handling |
| `DfuManifest` | DFU package manifest |
| `DfuManifestFile` | Individual manifest file entry |

### DFU States (from strings)
```
"Dfu process starting, originalAddress: "
"Dfu process started, originalAddress: "
"Dfu upgrading, originalAddress: "
"Dfu completed, originalAddress: "
"Dfu disconnected, originalAddress: "
"Dfu error, originalAddress: "
"Dfu aborted, originalAddress: "
```

### DFU Address Handling
- `_calculateAndroidDfuMac` — Calculates DFU-mode MAC address
  - Nordic DFU changes the device MAC address when entering DFU mode
  - Android-specific calculation needed

### DFU Manifest (JSON)
```json
{
  // Parsed by DfuManifest.fromJson / DfuManifestFile.fromJson
  // Contains firmware type, file path, size, version
}
```

### Ring Update Pages
- `pages/devices/ota/ring/` — Ring firmware update UI
- `pages/devices/ota/ring_bootloader_sd/` — Bootloader + SoftDevice update
- `pages/devices/ota/ring_dfu_error/` — DFU error handling
- `pages/devices/ota/share/` — Shared OTA UI components

## MCU Update (Case Firmware)

### Classes
| Class | Description |
|-------|-------------|
| `McuOtaUpgrade` | MCU firmware update mixin |
| `McuManifest` | MCU update manifest (`fromJson`) |
| `McuManifestFile` | Manifest file entry (`fromJson`) |
| `McuLogMessage` | MCU update logging |
| `initMcuListener` / `disposeMcuListener` | MCU event lifecycle |
| `mcumgr_flutter` | MCU Manager protocol package |

### MCU Update Flow
1. Parse `McuManifest` from server
2. Initialize MCU listener
3. Upload firmware via MCU Manager protocol
4. Monitor progress via events
5. Dispose listener on completion

## Firmware Update Manager

### FirmwareUpdateManager
- `FirmwareUpdateManagerFactory` — Creates appropriate manager for device type
- `FirmwareUpdateMode` — Update mode (normal, force, background)
- `FirmwareUpdateLogger` — Detailed OTA logging

### Update Modes
- Normal: User-initiated with progress UI
- Force: Required update (blocks app usage)
- Background: Silent update when conditions met

## File Transfer (Shared Infrastructure)

### BleG2FileServiceMixin
```
mxins/ble_g2_cmd_service_file_ext.dart  — File commands
mxins/ble_g2_cmd_service_ota_ext.dart   — OTA-specific file ops
```

### File Transfer CRC
From extracted strings:
- `"last package(last 2 bytes) crc: "` — Per-packet CRC
- `"check big package crc: "` — Reassembled data CRC
- `"file crc error"` — CRC mismatch
- `"EVEN_FILE_SERVICE_RSP_DATA_CRC_ERR"` — Service error code

### EFS Protocol (efs_transmit.pbenum.dart)
- Protobuf enum for file service responses
- Matches `0xC4-00` / `0xC5-00` response format from iOS analysis

## Key Differences from iOS Swift SDK

1. **8 DFU service instances** — Android registers 8 parallel Nordic DFU services (vs single in iOS)
2. **MCU Manager** — Uses `mcumgr_flutter` for case MCU updates (we use custom protocol)
3. **DFU MAC calculation** — Android-specific MAC address derivation for DFU mode
4. **FirmwareUpdateManagerFactory** — Factory pattern for device-type-specific updates
5. **Update modes** — Explicit normal/force/background modes
6. **Ring bootloader+SD update** — Dedicated page for combined bootloader/softdevice update
