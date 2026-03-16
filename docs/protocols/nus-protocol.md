# Nordic UART Service (NUS) Protocol

The G2 glasses expose a secondary BLE communication channel via the Nordic UART Service. NUS uses simple 1-2 byte commands with **no G2 packet envelope** — no header, no CRC, no protobuf. This makes it useful for low-latency operations like gesture events and microphone control.

**Source**: `G2NordicUARTClient.swift`, `G2Protocol.swift`

## BLE Characteristics

| UUID | Direction | Purpose |
|------|-----------|---------|
| `6E400001-B5A3-F393-E0A9-E50E24DCCA9E` | — | Service UUID |
| `6E400002-B5A3-F393-E0A9-E50E24DCCA9E` | Phone → Glasses | TX (write) |
| `6E400003-B5A3-F393-E0A9-E50E24DCCA9E` | Glasses → Phone | RX (notify) |

## Commands (Phone → Glasses)

### Heartbeat

Single byte ping to keep NUS connection alive.

```
TX: 25
```

### Microphone Control

Enable or disable the glasses' microphone for audio streaming.

```
TX: 0E 01    Enable microphone
TX: 0E 00    Disable microphone
```

There are two mic control paths:
- **NUS** (`[0x0E, 0x01/0x00]`): Interactive, gets echo confirmation
- **G2 packet** (svc 0x06-20): Fire-and-forget, used internally by protocol features

### Text Display

Display UTF-8 text on the glasses. The glasses handle word wrapping.

```
TX: 4E <UTF-8 bytes>
```

Example: Display "Hello World"
```
TX: 4E 48 65 6C 6C 6F 20 57 6F 72 6C 64
```

### BMP Image Display

Send a BMP image to the glasses display.

```
TX: 15 <BMP data>
```

The image data must be in BMP format. Display canvas is 576 × 288 pixels.

## Events (Glasses → Phone)

### Gesture Events

All gesture events arrive with a `0xF5` prefix byte followed by a gesture code.

```
RX: F5 <code>
```

| Code | Gesture |
|------|---------|
| `0x01` | Single Tap |
| `0x00` | Double Tap |
| `0x04` | Triple Tap (Left) |
| `0x05` | Triple Tap (Right) |
| `0x17` | Long Press |
| `0x24` | Release |
| `0x02` | Slide Forward |
| `0x03` | Slide Backward |

See also [gestures.md](../features/gestures.md) for the G2-layer gesture protocol.

### Audio PCM Data

When the microphone is enabled, audio frames arrive with a `0xF1` prefix. The prefix is stripped before processing.

```
RX: F1 <PCM frame data>
```

The raw PCM data is delivered via the `onAudioFrame` callback. Frame size is validated against a known audio frame size before classification to distinguish audio from other NUS data.

## Firmware Update Boundary

NUS is not the primary firmware update transport for G2/R1 in current evidence.

- Runtime UI/audio controls use NUS and G2 packet services.
- Firmware checks and OTA decisioning are driven by cloud API paths (`/v2/g/check_firmware`, `/v2/g/check_latest_firmware`).
- Device-side update transfer logic is associated with DFU/file-service pathways, not simple NUS 1-2 byte commands.

See [firmware-updates.md](../firmware/firmware-updates.md) for the OTA/DFU pipeline details.

## NUS vs G2 Packet Protocol

| Aspect | NUS | G2 Packet |
|--------|-----|-----------|
| Envelope | None | 8-byte header + CRC |
| Encoding | Raw bytes | Protobuf payloads |
| Latency | Lower | Higher (header/CRC overhead) |
| Features | Gestures, mic, text, BMP | All protocol features |
| Auth required | No | Yes (3 or 7 packet handshake) |
| Characteristics | 6E4000xx | 5401/5402, 7401/7402, 6402 |

NUS is typically used for:
- Real-time gesture listening
- Quick text display (debug, status)
- Microphone enable/disable with immediate feedback
- Audio PCM streaming
- Ring gesture forwarding (tap → `[0xF5, 0x01]`)
