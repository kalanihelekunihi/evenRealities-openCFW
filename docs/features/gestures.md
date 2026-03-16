# Gesture Protocol

The G2 glasses report touch gestures through two independent layers: the G2 packet protocol (protobuf-encoded on the control channel) and the Nordic UART Service (simple byte codes). Both can be active simultaneously.

**Source**: `G2ResponseDecoder.swift`, `G2NordicUARTClient.swift`

## G2-Layer Gestures (Protobuf)

Gesture events arrive as G2 response packets on the control notify channel (0x5402).

### Tap and Swipe (Service 0x01-01)

| Gesture | Protobuf Pattern | Detection |
|---------|-----------------|-----------|
| Single Tap | Default (no swipe marker) | Fallback when no swipe pattern matches |
| Swipe Forward | Contains `12 04 08 01` | Nested field 2, LD 4 bytes, field 1 = 1 |
| Swipe Backward | Contains `12 04 08 02` | Nested field 2, LD 4 bytes, field 1 = 2 |

Example tap payload:
```
08 01 12 02 10 01
```

Example swipe forward payload:
```
08 01 12 04 08 01
```

### Long Press (Service 0x0D-01)

Long press events arrive on a separate service ID. The payload contains a counter value extracted from nested protobuf:

```
08 01 1A 02 08 06
```

| Field | Value | Meaning |
|-------|-------|---------|
| 1 (varint) | 1 | Type indicator |
| 3 (LD) | nested | Press metadata |
| 3.1 (varint) | 6 | Counter/identifier (exact semantics unknown — may be press count, duration, or zone) |

The counter value is now extracted from field 3.field1 (previously hardcoded to 0).

### Double-Tap Detection

Double-tap is detected in software, not by the glasses firmware:

- **Window**: 400ms between two single-tap events
- **Validation**: The two taps must have different counter values (to distinguish from a single echoed tap)
- If a second tap arrives within the window, a `doubleTap` gesture is emitted
- If the window expires without a second tap, a single `tap` gesture is emitted

## NUS-Layer Gestures

NUS gesture events use a `0xF5` prefix followed by a single gesture code byte. These bypass the G2 packet format entirely.

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

See [nus-protocol.md](../protocols/nus-protocol.md) for NUS connection details.

## R1 Ring Gesture Forwarding

The Even R1 ring detects gestures and forwards them to the G2 glasses. Ring gestures are first decoded on the phone, then translated to NUS commands:

| Ring Gesture | Ring Bytes | Forwarded As |
|-------------|-----------|-------------|
| Single Tap | `FF 04 01` | NUS `F5 01` |
| Double Tap | `FF 04 02` | NUS `F5 00` |
| Swipe Forward | `FF 05 00/01` | Scroll forward event |
| Swipe Backward | `FF 05 02+` | Scroll backward event |
| Hold | `FF 03 20` | Custom action |

See [r1-ring.md](../devices/r1-ring.md) for the full ring protocol.

## Gesture Routing Summary

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│ G2 Touch │────▶│ 0x01-01/0D-01│────▶│ onGesture()  │
│ Bar      │     │ G2 packet    │     │              │
└──────────┘     └──────────────┘     │              │
                                      │  App Logic   │
┌──────────┐     ┌──────────────┐     │              │
│ G2 Touch │────▶│ NUS 0xF5     │────▶│ onGesture()  │
│ Bar      │     │ Simple byte  │     │              │
└──────────┘     └──────────────┘     │              │
                                      │              │
┌──────────┐     ┌──────────────┐     │              │
│ R1 Ring  │────▶│ Ring decode  │────▶│ onGesture()  │
│          │     │ → NUS fwd    │     │              │
└──────────┘     └──────────────┘     └──────────────┘
```

Both the G2-layer and NUS-layer gesture events are unified through the `G2GestureActionRouter` before reaching the application.
