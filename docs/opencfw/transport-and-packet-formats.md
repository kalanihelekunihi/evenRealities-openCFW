# Transport and Packet Formats

This document is the clean-room transport baseline for `openCFW`. It records the identified packet/lane behavior, the inferred but still-open wire details, and the unresolved conflicts that must remain configurable.

## Identified Transport Baseline

### Lane Pairs

| Lane | Write | Notify | State | Notes |
|---|---|---|---|---|
| Control | `0x5401` | `0x5402` | Identified | Main protobuf command/response plane |
| Display | `0x6401` | `0x6402` | Identified | Display config/content and display-side feedback |
| File | `0x7401` | `0x7402` | Identified | File transfer, notifications, OTA |

### UUID Family

Base UUID family:

`00002760-08c2-11e1-9073-0e8ac72e{suffix}`

Known characteristic suffixes:

| Suffix | State | Role |
|---|---|---|
| `5401` | Identified | Control write |
| `5402` | Identified | Control notify |
| `6401` | Identified | Display write |
| `6402` | Identified | Display notify |
| `7401` | Identified | File write |
| `7402` | Identified | File notify |
| `5450` | Partial | Control parent/alternate service anchor |
| `6450` | Partial | Display parent/alternate service anchor |
| `7450` | Partial | File parent/alternate service anchor |

## G2 Packet Envelope

### Identified Fields

The core G2 envelope is stable on the control and file lanes, and on display-lane packets that actually use the protobuf-style transport:

| Offset | Size | Field | Identified Meaning |
|---|---:|---|---|
| `0x00` | 1 | Magic | `0xAA` |
| `0x01` | 1 | Type | `0x21` command, `0x12` response |
| `0x02` | 1 | Sequence | Per-endpoint sequence counter |
| `0x03` | 1 | Length | payload length + CRC bytes |
| `0x04` | 1 | Packet Total | total fragments in message |
| `0x05` | 1 | Packet Serial | current fragment index |
| `0x06` | 1 | Service Hi | service ID high byte |
| `0x07` | 1 | Service Lo | service ID low byte |
| `0x08..` | var | Payload | protobuf or lane-specific raw payload |
| trailer | 2 | CRC | CRC-16/CCITT over payload only, little-endian |

### Clean-Room Implication

- The envelope parser/builder should be reusable across control and file lanes.
- Fragment support is required from the start.
- CRC must be calculated over payload bytes only, not the transport header.

## Authentication Transport

### Identified

| Service | Role |
|---|---|
| `0x80-00` | AuthControl |
| `0x80-20` | AuthData |
| `0x80-01` | AuthResponse |
| `0x80-02` | Transport ACK |

Two auth flows are documented strongly enough to preserve:

- Fast 3-packet auth
- Full 7-packet auth

Both flows end with a time-sync packet and both rely on app-layer auth rather than BLE pairing.

### Inferred but Important

- Each eye maintains its own response timing and sequence evolution.
- Dual-eye auth should remain sequential until independent live evidence proves concurrent auth is safe against shared response routing.

## File Lane Transport

### Identified

| Service | State | Meaning |
|---|---|---|
| `0xC4-00` | Identified | File command lane |
| `0xC5-00` | Identified | File data lane |

Stable file-lane sequence:

`FILE_CHECK -> START -> DATA -> END`

Stable response format on `0x7402`:

- Non-protobuf
- 2-byte little-endian status word

Identified reusable `FILE_CHECK` header:

| Field | Identified Value |
|---|---|
| Mode | `0x00000100` |
| Size scaling | `len(data) * 256` |
| Checksum field | `(CRC32C << 8) & 0xFFFFFFFF` |
| Extra byte | `CRC32C >> 24` |
| Filename field | 80-byte null-padded UTF-8 string |
| Total payload size | 93 bytes |

This layout is now supported by three local evidence sources:

- working capture logs showing `sizeScaled=59904` for 234-byte notification payloads (`234 * 256`)
- `G2FileTransferClient.swift`
- `G2FirmwareTransferClient.swift`

### Partial

The remaining ambiguity is not the generic file-transfer header itself, but the relationship between that reusable path and the OTA-specific raw transfer path:

| Area | Source | State | Notes |
|---|---|---|---|
| Generic file transfer path | local source + captures | Identified | 93-byte FILE_CHECK header, shared by notification transfer and current firmware-transfer client |
| OTA-specific raw path | firmware strings / OTA notes | Partial | separate 5-byte header + 1000-byte payload path appears to exist beyond the generic client |
| Older alternate FILE_CHECK description | older OTA notes | Partial | 32-byte filename / `x4` scaling description is not currently authoritative for the reusable client path |

### OTA-Specific Path

A richer OTA-specific transfer path is strongly suggested beyond generic `0xC4/0xC5`:

| Property | State | Notes |
|---|---|---|
| 5-byte OTA packet header | Partial | Present in firmware string evidence |
| 1000-byte OTA payload chunks | Partial | Enforced by OTA-specific error strings |
| OTA information/result-check phases | Partial | Real command family, but field layout still open |

## Display Lane Special Cases

### Identified

- `0x6401` carries display-facing writes.
- `0x6402` carries display/render feedback.
- Not all `0x6402` traffic is G2-envelope protobuf data.

### Partial

- `0x6402` also carries a sensor/render stream with hardware-adjacent formatting that is not yet fully modeled as normal G2 packets.
- Head-angle / render-state trailer behavior is real, but still not fully closed.

## Unidentified or Still Open

| Area | Why It Is Still Open |
|---|---|
| Exact runtime role of `0x5450/0x6450/0x7450` | They appear as parent/alternate service anchors, but the exact behavioral role is still not fully closed |
| `0x0884` notify handle | Secondary notify path exists in captures/docs but the corresponding service contract is not authoritative yet |
| Exact relationship between generic file transfer and OTA-specific raw transfer | The reusable client path is clear, but the firmware may still support a second OTA-only framing mode |
| Exact OTA-specific 5-byte header layout | Firmware strings prove it exists, but not the final byte contract |
| `0x6402` stream descrambling and full trailer schema | Display-side stream is only partially recovered |

## Clean-Room Guidance

- Implement one common G2 envelope layer.
- Treat the 93-byte FILE_CHECK header as the identified reusable file-transfer contract.
- Keep any OTA-only raw file path separate from the generic file-transfer implementation until its 5-byte header is closed.
- Treat display notify traffic as a mixed lane: some packets use the common envelope, some do not.
- Keep `0x5450/0x6450/0x7450` represented in manifests and code, but do not attach hard behavior to them yet.

## Source Documents

- `../protocols/packet-structure.md`
- `../protocols/ble-uuids.md`
- `../protocols/authentication.md`
- `../protocols/notification.md`
- `../firmware/ota-protocol.md`
- `../features/display-pipeline.md`
- `../firmware/g2-service-handler-index.md`
