# Heartbeat / Keepalive Protocol

The heartbeat mechanism keeps the BLE connection alive and verifies the glasses are responsive. Heartbeat commands are sent on service `0x80-20` (AuthData) and responses arrive on `0x80-00` (AuthControl) — note the service shift.

**Source**: `ProtocolConstants.swift`, `G2ResponseDecoder.swift`

## Command Format

Heartbeat is sent as a standard G2 packet on service 0x80-20.

```
AA 21 <seq> 06 01 01 80 20 08 0E 10 6B 6A 00 <crc_lo> <crc_hi>
                              │  │  │  │  └──┘ field 13 LD, empty
                              │  │  │  └ field 2 varint: msg_id = 107
                              │  │  └ field 1 varint: type = 14 (0x0E)
                              └──┘ service 0x80-20 (AuthData)
```

### Payload Fields

```
08 0E       field 1 varint: type = 14 (MUST be 0x0E)
10 <msgId>  field 2 varint: message ID
6A 00       field 13 LD, length 0 (empty)
```

## Critical: Only Type 14 Works

From probe testing (2026-02-18):

| Type | Result |
|------|--------|
| 13 (0x0D) | No response |
| **14 (0x0E)** | **Echo response** |
| 15 (0x0F) | No response |

Only type 14 triggers a heartbeat echo. This was confirmed by sweeping types 13-15 against all message ID variants.

## Valid Message IDs

All three tested message IDs work:

| msg_id | Hex | Status |
|--------|-----|--------|
| 106 | 0x6A | Works |
| 107 | 0x6B | Works (default) |
| 108 | 0x6C | Works |

## Response Types

Two different response types may arrive after a heartbeat:

### Transport ACK (service 0x80-02)

An 8-byte header-only packet with no payload and no CRC. Arrives ~34ms after send.

```
AA 12 <seq> 00 01 01 80 02
```

This confirms the glasses received the packet at the transport layer.

### Heartbeat Echo (service 0x80-00)

A full G2 packet with protobuf payload echoed back. Arrives ~180-200ms after send. The response uses a glasses-generated sequence number (different from the request).

```
AA 12 <glasses_seq> <len> 01 01 80 00 <payload...> <crc_lo> <crc_hi>
```

The echo payload may include additional status fields beyond the original request (e.g. wearing state, charging state, case state).

## Response Routing

| What was sent | Response arrives on |
|---------------|-------------------|
| Heartbeat on 0x80-20 | Echo on 0x80-00 (service shift) |
| Heartbeat on 0x80-20 | Transport ACK on 0x80-02 |

Both eyes independently echo heartbeat responses when both are connected, each with different sequence numbers arriving 50-100ms apart.

## Timing

| Parameter | Value |
|-----------|-------|
| Transport ACK latency | ~34ms |
| Echo response latency | ~180-200ms |
| Recommended keepalive interval | 3-5 seconds |

## CRC Anomaly

The CRC in heartbeat echo responses matches the **original TX packet CRC**, not a recalculated CRC over the response payload. This is consistent with the glasses echoing the request CRC. The response decoder handles this by accepting both canonical and echoed CRC values.
