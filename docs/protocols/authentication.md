# Authentication Protocol

The G2 glasses use an application-level authentication handshake (not BLE pairing). Auth packets are sent on services `0x80-00` (AuthControl) and `0x80-20` (AuthData). Responses arrive on `0x80-00`, `0x80-01` (AuthResponse), and `0x80-02` (Transport ACK).

**Source**: `G2Auth.swift`, `G2ConnectionHelper.swift`, `ProtocolConstants.swift`

## Auth Modes

Two modes are available. Both end with a time-sync packet that sets the glasses' clock.

### Fast 3-Packet (`fast3Packet`)

Used for quick reconnection. Sufficient for most features.

| Seq | Service | Payload Type | Description |
|-----|---------|-------------|-------------|
| 0x01 | 0x80-00 | Capability (type=4, msgId=0x0D) | Query glasses capabilities |
| 0x02 | 0x80-20 | CapabilityResponse (type=5, msgId=0x0E, mode=2) | Confirm fast mode |
| 0x03 | 0x80-20 | TimeSync (type=0x80, msgId=0x0F) | Set clock + transaction ID |

### Full 7-Packet (`full7Packet`)

Used by teleprompter and Even AI. More thorough negotiation.

| Seq | Service | Payload Type | Description |
|-----|---------|-------------|-------------|
| 0x01 | 0x80-00 | Capability (type=4, msgId=0x0C) | Initial capability query |
| 0x02 | 0x80-20 | CapabilityResponse (type=5, msgId=0x0E, mode=2) | Fast mode response |
| 0x03 | 0x80-20 | TimeSync (type=0x80, msgId=0x0F) | First time sync |
| 0x04 | 0x80-00 | Capability (type=4, msgId=0x10) | Extended capability |
| 0x05 | 0x80-00 | Capability (type=4, msgId=0x11) | Additional capability |
| 0x06 | 0x80-20 | CapabilityResponse (type=5, msgId=0x12, mode=1) | Final mode |
| 0x07 | 0x80-20 | TimeSync (type=0x80, msgId=0x13) | Final time sync |

## Payload Formats

### Capability Query (type=4)

Sent on AuthControl (0x80-00).

```
08 04         field 1 varint: type = 4
10 <msgId>    field 2 varint: message ID
1A 04         field 3 LD, length 4
  08 01       nested field 1: primary = 1
  10 04       nested field 2: secondary = 4
```

### Capability Response (type=5)

Sent on AuthData (0x80-20).

```
08 05         field 1 varint: type = 5
10 <msgId>    field 2 varint: message ID
22 02         field 4 LD, length 2
  08 <mode>   nested field 1: mode (0x02=fast, 0x01=final)
```

### Time Sync (type=0x80)

Sent on AuthData (0x80-20). Sets the glasses' internal clock.

```
08 80 01      field 1 varint: type = 128 (0x80, encoded as 2-byte varint)
10 <msgId>    field 2 varint: message ID
82 08 <len>   field 128 LD (2-byte tag), length <len>
  08 <ts...>  nested field 1 varint: Unix timestamp (seconds)
  18 E8 FF FF FF FF FF FF FF FF 01
              nested field 3 varint: transaction ID sentinel (-24 as signed varint)
```

The transaction ID is always the varint encoding of signed Int64(-24): `E8 FF FF FF FF FF FF FF FF 01`.

## Response Behavior

### Timing

Glasses respond within **~51ms** of the first auth packet. This is critical — the response handler must be registered **before** sending any packets, not after.

### Response Types

| Service | Meaning | Format |
|---------|---------|--------|
| 0x80-00 | Auth echo / heartbeat echo | Full G2 packet with protobuf payload |
| 0x80-01 | Auth success indicator | Protobuf: `f3={f1=1}` means success |
| 0x80-02 | Transport ACK | 8-byte header only, no payload, no CRC |

### AuthResponse Decoding (0x80-01)

```
Payload protobuf:
  field 1 varint: 4 (always type=capability, regardless of command type sent)
  field 2 varint: <glasses-generated msg_id> (NOT echoed from sender)
  field 3 LD:
    field 1 varint: 1 = success, other = failure
```

**Important**: AuthResponse packets on 0x80-01 always have type=4 (capability), even when responding to type=5 (capability response) or type=128 (time sync) commands. The field 2 msg_id is the glasses' own counter, not an echo of the sender's msg_id.

### Dual-Eye Echo Pattern

When both eyes are connected, **each eye independently echoes auth responses**. The echoes arrive 50-100ms apart with different glasses-generated sequence numbers. This is expected behavior — both echoes should be processed.

### Auth Must Be Sequential for Dual-Eye

Auth for left and right eyes must run **sequentially**, not concurrently. Both eyes share a single BLE notify characteristic (0x5402) and response decoder. Concurrent auth creates a race condition where callback overwrites leave one eye's completion flag permanently unset, causing a 5+ second timeout waste.

## Timing Constants

| Parameter | Value |
|-----------|-------|
| Inter-packet delay | 100ms |
| Post-auth delay | 500ms |
| Expected response latency | ~51ms |
| Auth timeout | 1500ms (before trying next mode) |

## Implementation Notes

- Register the response handler (onTransportACK / onAuthResponse) **before** sending auth packets. Glasses respond faster than the send loop completes.
- `G2Auth.lastSuccessfulMode` caches which mode worked, enabling faster subsequent connections.
- Time sync can also be sent standalone via `G2Auth.syncTime()` after initial auth.

## Example Packet (Fast Auth, Packet 1)

```
AA 21 01 0C 01 01 80 00 08 04 10 0D 1A 04 08 01 10 04 A7 04
│  │  │  │  │  │  │  │  └─────────── payload ──────────┘ └CRC┘
│  │  │  │  │  │  └──┘ service 0x80-00 (AuthControl)
│  │  │  │  │  └ packet 1 of 1
│  │  │  │  └ total 1 packet
│  │  │  └ length 12 (10 payload + 2 CRC)
│  │  └ seq 1
│  └ type 0x21 (command)
└ magic 0xAA
```
