# Even Realities G2 Smart Glasses - Protocol Documentation

I have been reverse engineering the Even Realities G2 smart glasses BLE protocol. If you are interersted in joining this effort, please do!

## What the hell does that even mean???

The G2 glasses use a custom protocol created by EvenRealities. This BLE (bluetooth) protocol is used to transmit data in packets to and from the glasses. Currently, the G2 glasses are restricted to the functionality offered in the Even app - reverse engineering the BLE protocol removes this restriction.



## Status

| Feature | Status | Notes |
|---------|--------|-------|
| BLE Connection | Working | Standard BLE, no special pairing |
| Authentication | Working | 7-packet handshake sequence |
| Teleprompter | Working | Custom text display confirmed |
| Calendar Widget | Working | Display events on glasses |
| Notifications | Partial | Metadata only (app + count) |
| Even AI | Research | Protocol identified |
| Navigation | Research | High display traffic observed |

## Quick Start

```bash
cd examples/teleprompter
pip install -r requirements.txt

# Display custom text on glasses
python teleprompter.py "Hello from Python!"

# Multi-line text
python teleprompter.py "Line one
Line two
Line three"
```

## Documentation

The original per-topic docs (ble-uuids, packet-structure, services, teleprompter) have been
incorporated into our comprehensive protocol documentation which now supersedes them:

- BLE UUIDs → [protocols/ble-uuids.md](../../protocols/ble-uuids.md)
- Packet Structure → [protocols/packet-structure.md](../../protocols/packet-structure.md)
- Service Reference → [protocols/services.md](../../protocols/services.md)
- Teleprompter → [features/teleprompter.md](../../features/teleprompter.md)

## Key Findings

### CRC Algorithm
- **Type**: CRC-16/CCITT
- **Init**: 0xFFFF
- **Polynomial**: 0x1021
- **Scope**: Calculated over payload bytes only (skip 8-byte header)
- **Format**: Little-endian

### Packet Structure
```
[AA] [21] [seq] [len] [01] [01] [svc_hi] [svc_lo] [payload...] [crc_lo] [crc_hi]
```

### Architecture
The G2 uses a dual-channel design:
- **Content Channel** (0x5401): What to display (text, data)
- **Rendering Channel** (0x6402): How to display (positioning, styling)

## Contributing

Pull requests welcome! Areas needing research:
- Navigation turn-by-turn protocol
- Even AI request/response format
- Translation feature
- Display rendering commands (0x6402)

## Credits

- Protocol research by the Even Realities community


## Disclaimer

This is an unofficial community project for educational purposes. Not affiliated with Even Realities.

## Discord
For all communications, I recommend Discord. Join the [EvenRealities Discord Server](https://discord.gg/arDkX3pr), which contains a reverse engineering channel containing many threads, including G2 RE.
