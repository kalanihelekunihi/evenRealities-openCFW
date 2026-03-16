# Even G2 Packet Structure

## Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         G2 BLE Packet                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│   │      HEADER      │  │     PAYLOAD      │  │       CRC        │  │
│   │     8 bytes      │  │   Variable len   │  │     2 bytes      │  │
│   │                  │  │                  │  │                  │  │
│   │  AA 21 01 0C     │  │  Protobuf data   │  │  Little-endian   │  │
│   │  01 01 80 00     │  │  (service-       │  │  CRC-16/CCITT    │  │
│   │                  │  │   specific)      │  │                  │  │
│   └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                       │
│   Phone → Glasses: Type = 0x21 (Command)                             │
│   Glasses → Phone: Type = 0x12 (Response)                            │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Transport Layer

All packets follow this structure:

```
┌────────┬────────┬────────┬────────┬────────┬────────┬────────┬────────┬─────────────┬────────┬────────┐
│ Magic  │  Type  │  Seq   │  Len   │  Pkt   │  Pkt   │  Svc   │  Svc   │   Payload   │  CRC   │  CRC   │
│  0xAA  │        │   ID   │        │  Tot   │  Ser   │  Hi    │  Lo    │     ...     │   Lo   │   Hi   │
└────────┴────────┴────────┴────────┴────────┴────────┴────────┴────────┴─────────────┴────────┴────────┘
   [0]      [1]      [2]      [3]      [4]      [5]      [6]      [7]       [8:N-2]      [N-1]    [N]
```

### Header Fields (8 bytes)

| Offset | Field | Description |
|--------|-------|-------------|
| 0 | Magic | Always `0xAA` |
| 1 | Type | `0x21` = Command, `0x12` = Response |
| 2 | Sequence | Incrementing counter (0-255) |
| 3 | Length | Payload length + 2 (includes CRC) |
| 4 | Packet Total | Total packets in message (usually `0x01`) |
| 5 | Packet Serial | Current packet number (usually `0x01`) |
| 6 | Service Hi | Service ID high byte |
| 7 | Service Lo | Service ID low byte |

### Fragment Counters and OTA Mapping

The fragmentation bytes in the header align with OTA/file tokens found in Even.app static analysis:

- Header byte `[4]` (`Packet Total`) maps to `packetTotalNum`
- Header byte `[5]` (`Packet Serial`) maps to `packetSerialNum`

In current G2 file-transfer flows (`0xC4-00`/`0xC5-00`), these fields identify each chunk within a transfer and should be tracked to detect dropped or reordered packets.

### Payload

Variable length, protobuf-encoded. Structure depends on service.

### CRC (2 bytes)

- **Algorithm**: CRC-16/CCITT
- **Init Value**: 0xFFFF
- **Polynomial**: 0x1021
- **Input**: Payload bytes only (skip first 8 bytes)
- **Output**: Little-endian (low byte first)

```python
def crc16_ccitt(data, init=0xFFFF):
    crc = init
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

def build_packet(seq, service_hi, service_lo, payload):
    header = bytes([0xAA, 0x21, seq, len(payload) + 2, 0x01, 0x01, service_hi, service_lo])
    crc = crc16_ccitt(payload)
    return header + payload + bytes([crc & 0xFF, (crc >> 8) & 0xFF])
```

## Message Types

### Command (0x21)
Sent from phone to glasses.

```
AA 21 01 0C 01 01 80 00 [payload] [crc]
       ↑              ↑
       seq=1          service=0x8000
```

### Response (0x12)
Sent from glasses to phone.

```
AA 12 FD 08 01 01 80 00 [payload] [crc]
       ↑
       glasses uses its own seq counter
```

## Multi-Packet Messages

For payloads exceeding MTU (512 bytes):

```
Packet 1: AA 21 05 EC 05 01 ...  (total=5, serial=1)
Packet 2: AA 21 05 EC 05 02 ...  (total=5, serial=2)
Packet 3: AA 21 05 EC 05 03 ...  (total=5, serial=3)
...
```

- `Packet Total` (byte 4): Total number of packets (`packetTotalNum`)
- `Packet Serial` (byte 5): Current packet (1 to N, `packetSerialNum`)
- Sequence ID remains constant across all packets

## Varint Encoding

Payload fields use protobuf-style varint encoding:

| Value | Encoding |
|-------|----------|
| 0-127 | Single byte |
| 128-16383 | Two bytes (MSB has bit 7 set) |
| 16384+ | Three+ bytes |

```python
def encode_varint(value):
    result = []
    while value > 0x7F:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value & 0x7F)
    return bytes(result)
```

Examples:
- `10` → `0x0A`
- `127` → `0x7F`
- `128` → `0x80 0x01`
- `255` → `0xFF 0x01`
- `300` → `0xAC 0x02`

## Decoder Tool

`tools/g2_packet_decoder.py` decodes Even G2 transport packets and annotates inferred protocol fields.

It supports:
- Transport header parsing (`AA 21 ...`)
- CRC16/CCITT verification over payload
- Protobuf wire decoding (varint/len/fixed32/fixed64)
- Service-specific annotations for auth, teleprompter, display-config, even-ai, and file transfer packets
- Optional CRC-init brute-force for mismatched packets

### Usage

From repo root:

```bash
python3 tools/g2_packet_decoder.py --hex "aa21241c01010720080310352a1408001000220e77686174277320313020706c7573fdaf"
```

Decode multiple packets:

```bash
python3 tools/g2_packet_decoder.py \
  --hex "aa2149030101c40001d1f1" \
  --hex "aa21105f0101c4000001000000ca000000e2ff6ff7757365722f6e6f746966795f77686974656c6973742e6a736f6e000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000cdb7"
```

Decode from text logs with embedded hex:

```bash
python3 tools/g2_packet_decoder.py --file trace.log --extract-text-hex
```

Decode from binary streams:

```bash
python3 tools/g2_packet_decoder.py --file capture.bin --scan-binary
```

Allow mismatched CRC packets during stream scan:

```bash
python3 tools/g2_packet_decoder.py --file capture.bin --scan-binary --allow-bad-crc
```

Infer candidate CRC init values on mismatch:

```bash
python3 tools/g2_packet_decoder.py --hex "aa210e0601018020080e106b6a00e174" --infer-crc-init
```

### Notes

- `captures/*.log` are `btsnoop` capture files; they may not contain raw `AA 21` frames in a directly scan-friendly layout. If scan returns zero packets, first export packet payloads to hex lines and use `--extract-text-hex`.
- For malformed or experimental packets, header `len` can disagree with the byte stream; the decoder still reports what can be parsed and highlights CRC anomalies.
