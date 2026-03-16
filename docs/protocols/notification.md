# Push Notification Protocol (File Services 0xC4/0xC5)

## Overview

Push notifications use the **File Transfer** protocol on the 0x74xx characteristics. Unlike the teleprompter which uses protobuf on 0x54xx, notifications transfer JSON files with a CRC32C checksum for integrity validation.

## BLE Characteristics

| UUID | Name | Direction | Purpose |
|------|------|-----------|---------|
| `0x7401` | Notif Write | Phone → Glasses | Send file commands and data |
| `0x7402` | Notif Notify | Glasses → Phone | Receive status/responses |

Full UUIDs:
```
Write:  00002760-08c2-11e1-9073-0e8ac72e7401
Notify: 00002760-08c2-11e1-9073-0e8ac72e7402
```

## Message Sequence

```
1. AUTH (on 0x54xx)          - Standard 7-packet authentication
2. FILE_CHECK (0xC4-00)      - Announce file with checksum
3. START (0xC4-00, 0x01)     - Begin transfer
4. DATA (0xC5-00)            - Send JSON payload
5. END (0xC4-00, 0x02)       - Complete transfer
6. HEARTBEAT (on 0x54xx)     - Sync to left eye
```

## Service IDs

| Service ID | Name | Payload | Description |
|------------|------|---------|-------------|
| `0xC4-00` | File Command | varies | File check, start (0x01), end (0x02) |
| `0xC5-00` | File Data | JSON bytes | Raw file content |

## FILE_CHECK Header (93 bytes)

The FILE_CHECK command announces a file transfer with its checksum:

```
Offset  Size  Field       Description
------  ----  -----       -----------
0       4     mode        0x00010000 (little-endian: 00 00 01 00)
4       4     size        len(json) * 256 (little-endian)
8       4     checksum    (CRC32C << 8) & 0xFFFFFFFF (little-endian)
12      1     extra       (CRC32C >> 24) & 0xFF
13      80    filename    Null-padded filename string
```

**Total: 93 bytes**

### Checksum Calculation

The CRC32C checksum is split across two fields:

```python
crc = calc_crc32c(json_bytes)           # Full CRC32C
size = len(json_bytes) * 256            # Size encoding
checksum = (crc << 8) & 0xFFFFFFFF      # Lower 24 bits shifted, 0x00 in low byte
extra = (crc >> 24) & 0xFF              # High byte of CRC
```

**Glasses reconstruct**: `full_crc = (extra << 24) | (checksum >> 8)`

### CRC32C Algorithm

- **Type**: CRC-32C (Castagnoli)
- **Polynomial**: 0x1EDC6F41
- **Init**: 0
- **Mode**: Non-reflected (MSB-first)

```python
CRC32C_POLY = 0x1EDC6F41

def _generate_crc32c_table(poly=CRC32C_POLY):
    """Generate 256-entry lookup table from polynomial (non-reflected, MSB-first)."""
    table = []
    for i in range(256):
        crc = i << 24
        for _ in range(8):
            if crc & 0x80000000:
                crc = ((crc << 1) ^ poly) & 0xFFFFFFFF
            else:
                crc = (crc << 1) & 0xFFFFFFFF
        table.append(crc)
    return table

CRC32C_TABLE = _generate_crc32c_table()

def calc_crc32c(data: bytes) -> int:
    crc = 0
    for b in data:
        idx = b ^ ((crc >> 24) & 0xFF)
        crc = ((crc << 8) & 0xFFFFFFFF) ^ CRC32C_TABLE[idx]
    return crc
```

## JSON Payload Format

```json
{
  "android_notification": {
    "msg_id": 12345,
    "action": 0,
    "app_identifier": "com.google.android.gm",
    "title": "Sender Name",
    "subtitle": "Subject Line",
    "message": "Body text",
    "time_s": 1704067200,
    "date": "20240101T120000",
    "display_name": "Gmail"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `msg_id` | int | Unique message ID |
| `action` | int | 0 = show notification |
| `app_identifier` | string | Android package name |
| `title` | string | Notification title (sender) |
| `subtitle` | string | Notification subtitle (subject) |
| `message` | string | Notification body |
| `time_s` | int | Unix timestamp |
| `date` | string | Date string (YYYYMMDDTHHMMSS) |
| `display_name` | string | App display name |

## Packet Structure

All packets follow the standard G2 format:

```
[AA] [21] [seq] [len] [total] [num] [svc_hi] [svc_lo] [payload...] [crc_lo] [crc_hi]
```

### FILE_CHECK Packet

```
AA 21 10 5F 01 01 C4 00 [93-byte header] [crc16]
      ↑  ↑           ↑
     seq len=95   service
```

### START Packet

```
AA 21 49 03 01 01 C4 00 01 [crc16]
                        ↑
                     start command
```

### DATA Packet

```
AA 21 49 XX 01 01 C5 00 [json_bytes] [crc16]
         ↑           ↑
       len+2      data service
```

For multi-packet transfers:
```
AA 21 49 XX [total] [num] C5 00 [chunk] [crc16]
            ↑       ↑
         total    packet#
         pkts    (1-indexed)
```

### END Packet

```
AA 21 DA 03 01 01 C4 00 02 [crc16]
                        ↑
                     end command
```

## Cache Behavior

The glasses cache notifications by checksum. Responses to FILE_CHECK:

| Response | Meaning | Action |
|----------|---------|--------|
| `CACHE_MISS` | New content | Send full data |
| `CACHE_HIT` (CHECK: OK) | Content cached | Still send data for display |

**Note**: Even on cache hit, send the data packets to trigger display.

## Filename

The filename field uses:
```
user/notify_whitelist.json
```

This suggests an app whitelisting mechanism. The `app_identifier` may need to match a whitelisted app package name.

## Complete Example

```python
async def send_notification(right_client, left_client, title, subtitle, message):
    # Build JSON
    json_bytes = build_notification_json(title, subtitle, message)

    # Calculate checksum fields
    crc = calc_crc32c(json_bytes)
    size = len(json_bytes) * 256
    checksum = (crc << 8) & 0xFFFFFFFF
    extra = (crc >> 24) & 0xFF

    filename = b"user/notify_whitelist.json"

    # FILE_CHECK (93-byte payload)
    fc_payload = (
        struct.pack('<I', 0x100) +          # mode
        struct.pack('<I', size) +           # size
        struct.pack('<I', checksum) +       # checksum
        bytes([extra]) +                    # extra (CRC high byte)
        filename + bytes(80 - len(filename)) # null-padded filename
    )
    await right_client.write_gatt_char(CHAR_NOTIF_WRITE,
        build_packet(0x10, 0xC4, 0x00, fc_payload))
    await asyncio.sleep(0.3)

    # START
    await right_client.write_gatt_char(CHAR_NOTIF_WRITE,
        build_packet(0x49, 0xC4, 0x00, bytes([0x01])))
    await asyncio.sleep(0.1)

    # DATA
    await right_client.write_gatt_char(CHAR_NOTIF_WRITE,
        build_packet(0x49, 0xC5, 0x00, json_bytes))
    await asyncio.sleep(0.3)

    # END
    await right_client.write_gatt_char(CHAR_NOTIF_WRITE,
        build_packet(0xDA, 0xC4, 0x00, bytes([0x02])))

    # Heartbeat to left eye (on 0x54xx)
    await asyncio.sleep(0.2)
    await left_client.write_gatt_char(CHAR_WRITE,
        bytes.fromhex("aa210e0601018020080e106b6a00e174"))
```

## Size Limitations

| Limit | Value | Notes |
|-------|-------|-------|
| Single packet max | 234 bytes | JSON must fit in one packet for reliable delivery |
| Multi-packet | WIP | Transfers >234 bytes fail silently |

**Recommendation**: Keep JSON under 234 bytes. Truncate message field if needed.

## Known Issues

1. **Multi-packet transfers**: Messages >234 bytes don't display. The glasses may not properly reassemble chunked data.

2. **App whitelisting**: The `app_identifier` may need to match a known app. `com.google.android.gm` (Gmail) is confirmed working.

3. **Cache behavior**: Same content won't re-display without changing the checksum.

## Notification Metadata Service (0x02-20)

In addition to the file-transfer path above, Even.app defines a `ProtoNotificationExt` that creates notification metadata packages routed through service 0x02-20. This is the protobuf-based metadata path:

- **Service ID**: 0x02-20 (TX), confirmed via i-soxi proto schema
- **Purpose**: Notification metadata proto (app name, title, body, icon type, etc.)
- **Relationship to file transfer**: The file transfer (0xC4/0xC5) alone is sufficient for notification display on glasses (confirmed testAll-3). The 0x02-20 metadata proto is optional — likely used for richer notification features (category filtering, actions, etc.)

Note: The JSON key in file-transferred notifications is `"android_notification"` even on iOS — the firmware expects this key regardless of platform.

## Credits

- Checksum algorithm discovered through analysis of aegray's notification captures
- CRC32C table from aegray's even-g2 implementation
