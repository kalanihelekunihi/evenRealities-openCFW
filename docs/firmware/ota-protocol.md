# OTA Firmware Transfer Protocol

BLE wire protocol for transferring firmware to Even G2 glasses. This documents the confirmed file transfer path and the inferred OTA-specific command vocabulary.

> **Cross-reference**: API endpoints and CDN download flow in [firmware-updates.md](firmware-updates.md).
> Per-component binary formats in [firmware-files.md](firmware-files.md) and per-component docs.

---

## 1. BLE Service Channels

| Channel | Char UUID | Direction | Role |
|---------|-----------|-----------|------|
| File Write | `0x7401` | Phone → Glasses | Control commands + data chunks |
| File Notify | `0x7402` | Glasses → Phone | ACK responses (non-protobuf) |
| File Parent | `0x7450` | — | GATT service declaration (Phase 6 confirmed) |

The file channel is separate from the control channel (`0x5401/0x5402`) and display channel (`0x6401/0x6402`). OTA transfer MUST use the file channel characteristics.

## 2. Transfer Sequence

Each file transfer follows a 4-step sequence on `0x7401`:

```
FILE_CHECK  →  START  →  DATA (×N chunks)  →  END
   ↓             ↓            ↓                  ↓
  ACK           ACK       [optional]            ACK
```

All commands use the G2 packet envelope: `AA 21 [seq] [len] [total] [num] [svc_hi] [svc_lo] [payload] [CRC16]`

### 2.1 FILE_CHECK (0xC4-00)

Announces the incoming file with metadata. The glasses validate and prepare storage.

```
Payload layout:
  [0-3]  mode (LE32) — transfer mode (0x01 for file write)
  [4-7]  scaled_size (LE32) — file size × scale factor
  [8-11] checksum (LE32) — CRC32C of file data, shifted
  [12]   extra_crc (byte) — upper bits of CRC32C
  [13-44] filename (32 bytes, null-padded ASCII)
```

Checksum encoding:
- `crc = G2CRC.crc32c(fileData)`
- `scaled_size = fileSize × 4` (scale factor from SDK)
- `checksum_field = (crc << 8) & 0xFFFFFFFF`
- `extra_byte = (crc >> 24) & 0xFF`

### 2.2 START (0xC4-00)

Single-byte payload: `0x01`. Signals the glasses to begin accepting data chunks.

### 2.3 DATA (0xC5-00)

Raw file data in chunks, using multi-packet fragmentation:
- `total` = number of chunks in this segment (max 255)
- `num` = chunk index (1-based)
- Each chunk ≤ MTU - packet overhead (typically 234 bytes)
- All chunks share the same `seq` number

### 2.4 END (0xC4-00)

Single-byte payload: `0x02`. Signals transfer complete for this segment.

## 3. ACK Responses (0x7402)

ACKs are **non-protobuf** 2-byte little-endian status words:

| Status (LE16) | Constant | Meaning |
|---------------|----------|---------|
| `0x0000` | `FILE_RSP_SUCCESS` | Ready / file check accepted |
| `0x0001` | `FILE_RSP_FAIL` | Generic failure |
| `0x0002` | `FILE_RSP_TIMEOUT` | Transfer timeout |
| `0x0003` | `FILE_RSP_START_ERR` | Start command rejected |
| `0x0004` | `FILE_RSP_DATA_CRC_ERR` | CRC mismatch on data |
| `0x0005` | `FILE_RSP_RESULT_CHECK_FAIL` | Post-transfer verification failed |
| `0x0006` | `FILE_RSP_FLASH_WRITE_ERR` | Flash write error |
| `0x0007` | `FILE_RSP_NO_RESOURCES` | Device out of resources |

## 4. Multi-Segment Transfer

The G2 packet format limits `packetNumber` to UInt8 (max 255 chunks per sequence). Firmware packages (~4 MB at 234 bytes/chunk = ~17K chunks) require multi-segment transfer:

```
Segment 1: FILE_CHECK → START → DATA[1..255] → END
  (inter-segment delay: 1000ms)
Segment 2: FILE_CHECK → START → DATA[1..255] → END
  ...
Segment N: FILE_CHECK → START → DATA[1..remaining] → END
```

Each segment has a unique filename suffix:
- Segment 0: `firmware/ota_package.bin`
- Segment 1+: `firmware/ota_package.bin.{index}`

The Even.app binary confirms this via `partsTotal`/`currentPart` wire tokens.

## 5. OTA-Specific Command Vocabulary (Inferred)

From Even.app static RE, a richer OTA command set exists beyond the generic file transfer path. These use custom byte encoding (`.fromBytes`), NOT protobuf.

### OTA Transmit Commands

| Command | Purpose |
|---------|---------|
| `OTA_TRANSMIT_START` | Initiate OTA session |
| `OTA_TRANSMIT_INFORMATION` | Send firmware metadata (version, component list) |
| `OTA_TRANSMIT_FILE` | Transfer firmware data |
| `OTA_TRANSMIT_RESULT_CHECK` | Request verification after transfer |
| `OTA_TRANSMIT_NOTIFY` | Notify completion / request reboot |

### OTA Response Codes

| Code | Constant | Meaning |
|------|----------|---------|
| — | `OTA_RECV_RSP_SUCCESS` | OTA accepted |
| — | `OTA_RECV_RSP_FAIL` | OTA rejected |
| — | `OTA_RECV_RSP_HEADER_ERR` | Package header invalid |
| — | `OTA_RECV_RSP_PATH_ERR` | Component path not found |
| — | `OTA_RECV_RSP_CRC_ERR` | CRC verification failed |
| — | `OTA_RECV_RSP_FLASH_WRITE_ERR` | Flash write during OTA failed |
| — | `OTA_RECV_RSP_NO_RESOURCES` | Insufficient resources |
| — | `OTA_RECV_RSP_TIMEOUT` | OTA session timeout |
| — | `OTA_RECV_RSP_CHECK_FAIL` | Post-OTA integrity check failed |
| — | `OTA_RECV_RSP_SYS_RESTART` | System restarting after OTA |
| — | `OTA_RECV_RSP_UPDATING` | OTA in progress (busy) |

### Wire Metadata Tokens

```
otaMagic1, otaMagic2    — OTA session handshake markers
components              — Component list in package
fileType                — Component type ID
fileLength              — Component binary size
fileCrc32               — Component CRC32 checksum
fileSign                — MD5 signature
fileId / fileID         — Package/component identifier
fileTransmitCid         — Transfer connection ID
packetLen               — Per-packet data length
packetSerialNum         — Chunk sequence number
packetTotalNum          — Total chunks in segment
partsTotal              — Total segments in multi-segment transfer
currentPart             — Current segment index
packetAck               — ACK packet flag
```

> **Status**: Firmware binary string analysis (Wave 10, `firmware_string_index.py`) confirmed all OTA transmit command IDs and revealed the **OTA FILE packet wire format**:
>
> **OTA FILE packet layout** (from `pt_ota_transmit_file` error strings):
> - CRC position: `recv_value[payload_len + 5]` → **5-byte OTA header** before payload
> - Payload: exactly **1000 bytes** enforced (`payload_len is not equal to 1000`)
> - Timestamp: each packet carries timestamp matching `upgrade_file_timestamp` (set in INFORMATION phase)
> - INFORMATION validates: `data_len != EVEN_OTA_FILE_HEADER_SIZE` → fixed header size for metadata
>
> **Error response functions** (all stable across versions):
> `OTA_ReplyCrcErrorToAPP`, `OTA_ReplyNoResourcesToAPP`, `OTA_ReplyTimeoutToAPP`
>
> **OTA state tracking**: `SYSTEM_OTA_STATUS_ID state come from self/peer = %d` — each eye tracks OTA status independently and relays to peer via wired link.
>
> The iOS SDK currently uses the generic file transfer path (FILE_CHECK → START → DATA → END). The OTA-specific path uses different framing (5-byte header + 1000-byte payload + CRC) — hardware testing needed to confirm exact byte layout of the 5-byte header.

### OTA Transmit Types (firmware-confirmed)

| Enum | Component | LittleFS Path |
|------|-----------|---------------|
| `eOTATransmitType_GLASSES_FIRMWARE` | Main app | `/ota/s200_firmware_ota.bin` |
| `eOTATransmitType_BOOTLOADER` | Bootloader | `/ota/s200_bootloader.bin` |
| `eOTATransmitType_BLE9305_BIN` | EM9305 BLE | `/firmware/ble_em9305.bin` |
| `eOTATransmitType_TOUCH_BIN` | Touch | `/firmware/touch.bin` |
| `eOTATransmitType_AUDIO_BIN` | Codec | `/firmware/codec.bin` |
| `eOTATransmitType_BOX_BIN` | Case MCU | `/firmware/box.bin` |
| `eOTATransmitType_FONT` | Font files | XIP flash at 0x80100000+ |
| `eOTATransmitType_OTHER_BIN` | Generic | — |
| `eOTATransmitType_EXTERNAL_FLASH` | External flash | XIP address space |

### OTA Update Flow (firmware-confirmed)

```
1. Phone downloads EVENOTA package from cdn.evenreal.co
2. Phone sends firmware to glasses via BLE file transfer (0xC4/0xC5)
3. Glasses write ota/s200_firmware_ota.bin to LittleFS
4. Glasses set OTA flag and reboot
5. Bootloader reads OTA flag, validates CRC, programs MRAM
6. Bootloader clears flag, jumps to updated application
7. Application updates sub-components (codec, BLE, touch) from /firmware/
8. Box case can also initiate OTA for glasses via wired UART (dual-bank with bank swap)
```

### Box OTA Path (from box firmware strings)

The charging case can update glasses firmware independently via wired UART:
1. Check glasses ready
2. Get running bank number (dual-bank flash)
3. Erase target bank
4. Copy serial number
5. Transfer firmware from case storage
6. CRC verification: `crc_cal: 0x%x, crc_rx:0x%x`
7. Bank swap: `Swap bank(2->1) & RESET` or `Swap bank(1->2) & RESET`
- Box OTA has a 3-minute timeout
- Battery must be >50% for box OTA

**Box OTA wire format** (from string cross-reference, Wave 10):

| Phase | Function | Min recv_len | Purpose |
|-------|----------|-------------|---------|
| firmware_check | `pt_box_ota_firmware_check` | ≥ 8 bytes | Version comparison |
| begin | `pt_box_ota_begin` | ≥ 4 bytes | Start OTA, set `g_is_box_ota_mode=true` |
| file_get | `pt_box_ota_file_get` | ≥ 9 bytes | Read firmware chunks (≤240 bytes) |
| result_check | `pt_box_ota_result_check` | ≥ 9 bytes | CRC result + version confirmation |

Box UART framing (from `box_uart_mgr.c`): pack/unpack with CRC at last byte of framed message. Error handling: `serial recv data does not meet the protocol`.

## 6. Timing Constraints

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Post-FILE_CHECK delay | 500 ms | Glasses need time to validate and prepare flash |
| Post-START delay | 200 ms | Storage initialization |
| Inter-chunk delay | 10 ms | Prevent BLE buffer overflow |
| Post-DATA delay | 500 ms | Allow flash write to complete before END |
| Inter-segment delay | 1000 ms | Flash sector erase between segments |

## 7. Pre-Transfer Prerequisites

| Check | Requirement | Error Code |
|-------|-------------|------------|
| Connection | G2Session must be active | `deviceNotConnected` |
| Battery | Both eyes ≥ 50% | `batteryTooLow` |
| Charging | Device must be on charger | `notCharging` |

## 8. iOS SDK Implementation

| File | Purpose |
|------|---------|
| `G2FirmwareTransferClient.swift` | Multi-segment transfer orchestrator |
| `G2FileTransferClient.swift` | Generic file transfer protocol (reused) |
| `G2FirmwareAPIClient.swift` | CDN download + MD5 verification |
| `G2EVENOTAParser.swift` | Binary parser + CRC32C validation |
| `G2FirmwareModels.swift` | Response models + version comparison |
| `FirmwareCheckView.swift` | Full firmware management UI |

## 9. Component Update Chain

From firmware binary analysis (Phase 4/7), the glasses orchestrate OTA to sub-components:

```
Phone → Glasses (Apollo510b main app)
  ├→ EM9305 BLE radio (HCI patch, stable across versions)
  ├→ GX8002B audio codec (TinyFrame serial)
  ├→ CY8C4046FNI touch (I2C DFU)
  ├→ Case MCU (wired relay through frame)
  └→ Apollo510b bootloader (self-update)
```

The packaging order in EVENOTA is consistent across all 5 captured versions:
`codec(4) → BLE(5) → touch(3) → box(6) → bootloader(1) → main_app(0)`

Evidence: `captures/firmware/analysis/2026-03-03-integrity-packaging-semantics.md`
