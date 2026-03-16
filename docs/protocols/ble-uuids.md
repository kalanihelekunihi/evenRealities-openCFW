# Even G2 BLE UUIDs & Characteristics

## Service UUID

```
Base UUID: 00002760-08c2-11e1-9073-0e8ac72e{xxxx}
```

| UUID Suffix | Full UUID | Purpose | Status |
|-------------|-----------|---------|--------|
| `0001` | `00002760-08c2-11e1-9073-0e8ac72e0001` | Service Discovery / Registration | Known |
| `0002` | `00002760-08c2-11e1-9073-0e8ac72e0002` | Service Discovery / Registration | Known |
| `1001` | `00002760-08c2-11e1-9073-0e8ac72e1001` | Unknown — confirmed present in Android code | Confirmed — Android RE 2026-03-14 |
| `5401` | `00002760-08c2-11e1-9073-0e8ac72e5401` | Control TX (phone→glasses write) | Known |
| `5402` | `00002760-08c2-11e1-9073-0e8ac72e5402` | Control RX (glasses→phone notify) | Known |
| `5450` | `00002760-08c2-11e1-9073-0e8ac72e5450` | EUS GATT Service Declaration | Confirmed — Android RE 2026-03-14 |
| `6401` | `00002760-08c2-11e1-9073-0e8ac72e6401` | Display TX (phone→glasses write) | Known |
| `6402` | `00002760-08c2-11e1-9073-0e8ac72e6402` | Display RX (glasses→phone notify) | Known |
| `6450` | `00002760-08c2-11e1-9073-0e8ac72e6450` | ESS GATT Service Declaration | Confirmed — Android RE 2026-03-14 |
| `7401` | `00002760-08c2-11e1-9073-0e8ac72e7401` | File TX (phone→glasses write) | Known |
| `7402` | `00002760-08c2-11e1-9073-0e8ac72e7402` | File RX (glasses→phone notify) | Known |
| `7450` | `00002760-08c2-11e1-9073-0e8ac72e7450` | EFS GATT Service Declaration | Confirmed — Android RE 2026-03-14 |

## ATT Handles

| Handle | UUID Suffix | Direction | Purpose |
|--------|-------------|-----------|---------|
| `0x0842` | 5401 | Write | Commands (Phone -> Glasses) |
| `0x0844` | 5402 | Notify | Responses (Glasses -> Phone) |
| `0x0864` | 6402 | Write | Display/Rendering commands |
| `0x0874` | 7401 | Write | File transfer (Notifications) |
| `0x0876` | 7402 | Notify | File transfer responses |
| `0x0884` | ? | Notify | Secondary control (audio?) |

## Channel Architecture

The G2 uses multiple characteristic pairs for different functions:

| Channel | Service Decl | Write (TX) | Notify (RX) | Purpose |
|---------|-------------|-------|--------|---------|
| **EUS (Control)** | 0x5450 | 0x5401 | 0x5402 | Auth, protobuf commands (all services) |
| **ESS (Display)** | 0x6450 | 0x6401 | 0x6402 | Display commands / encrypted sensor stream |
| **EFS (File)** | 0x7450 | 0x7401 | 0x7402 | File transfers (notifications, OTA, maps) |

> **Confirmed via Android RE (2026-03-14)**: The `x450` characteristics are **GATT service declarations** (parent services) for each pipe — not alternate data channels. Each pipe has a triplet: service declaration (x450), TX write (x401), RX notify (x402).

**Private Service Types (BleG2PsType)** — from Even.app reverse engineering:
- Type 0 = Basic/Control (5401/5402)
- Type 1 = File (7401/7402)
- Type 2 = Display (6401/6402)

**Pipe Channel Selection**: The app uses `selectPipeChannel` to dynamically route traffic to different characteristics at runtime.

## Characteristic Properties

### Write Characteristic (0x5401)
- **Properties**: Write Without Response
- **Usage**: All commands sent to glasses
- **MTU**: 512 bytes (supports multi-packet)

### Notify Characteristic (0x5402)
- **Properties**: Notify
- **Usage**: All responses from glasses
- **CCCD**: Must enable notifications (write 0x0100)

### Display Characteristic (0x6402)
- **Properties**: Notify
- **Usage**: Encrypted sensor stream (~18.8 Hz, 205 bytes/frame) — head angle in trailer
- **Format**: Encrypted binary (not G2 protocol packets)
- **CCCD**: Must enable notifications (write 0x0100)

### File Write Characteristic (0x7401)
- **Properties**: Write Without Response
- **Usage**: File transfer commands and data (notifications)
- **Services**: 0xC4-00 (commands), 0xC5-00 (data)

### File Notify Characteristic (0x7402)
- **Properties**: Notify
- **Usage**: File transfer responses (cache status, errors)
- **CCCD**: Must enable notifications (write 0x0100)

## Connection Parameters

```
Connection Interval: 7.5ms - 30ms (typical)
Slave Latency: 0
Supervision Timeout: 2000ms
MTU: 512 bytes
```

## Device Naming

G2 glasses advertise with names like:
- `Even G2_XX_L_YYYYYY` (Left)
- `Even G2_XX_R_YYYYYY` (Right)

Where:
- `XX` = Model variant
- `L/R` = Left/Right ear
- `YYYYYY` = Serial suffix

## R1 Ring UUIDs

| UUID | Role |
|---|---|
| `BAE80001-4F05-4503-8E65-3AF1F7329D1F` | Ring Service |
| `BAE80012-4F05-4503-8E65-3AF1F7329D1F` | Ring TX (phone→ring write) |
| `BAE80013-4F05-4503-8E65-3AF1F7329D1F` | Ring RX (ring→phone notify) |

## Nordic DFU UUID (G2 Bootloader)

```
DFU Service Base: 8EC90000-F315-4F60-9FB8-838830DAEA50
Advertised UUID:  FE59 (during DFU mode)
DFU Name:         B210_DFU
```

Used when G2 enters DFU/bootloader mode. This is an auxiliary update path (nRF52840 DFU bootloader from Even.app bundle). The G2 main runtime on Apollo510b uses a custom EVENOTA protocol for primary firmware updates. See [firmware-updates.md](../firmware/firmware-updates.md) for both paths.

## Nordic SMP UUID (R1 Ring OTA)

The R1 Ring uses Nordic SMP (Simple Management Protocol) via iOSMcuManagerLibrary for firmware updates — distinct from the G2's custom OTA:

```
SMP Service:        8D53DC1D-1DB7-4CD3-868B-8A527460AA84
SMP Characteristic: DA2E7828-FBCE-4E01-AE9E-261174997C48
```

The SMP service UUID is the standard Nordic MCU Manager DFU service. The characteristic UUID is used for SMP command/response exchange over BLE. The R1 uses standard Nordic DFU, not Even-custom OTA.

## Pairing

The G2 uses **custom application-level authentication** rather than BLE pairing/bonding:
- No PIN required
- No secure pairing
- Session established via 7-packet handshake
- Timestamp + transaction ID exchange
