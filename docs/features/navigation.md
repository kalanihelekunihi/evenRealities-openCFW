# Navigation Protocol

The navigation protocol displays turn-by-turn directions on the G2 glasses. Commands are sent on service `0x08-20` and responses arrive on `0x08-00`.

**Source**: `G2NavigationProtocol.swift`, `G2NavigationSender.swift`

## Protobuf Message Structure

Navigation payloads use a nested protobuf structure:

```
Outer message:
  field 1 (varint): navigation_state
  field 2 (varint): message_id
  field 5 (length-delimited): nested navigation message

Nested message:
  field 1 (varint): inner_type = 4
  field 2 (LD): distance        (string, e.g. "86 m")
  field 3 (LD): instruction     (string, e.g. "Turn left")
  field 4 (LD): time_remaining  (string, e.g. "7 min")
  field 5 (LD): total_distance  (string, e.g. "701 m")
  field 6 (LD): eta             (string, e.g. "ETA: 13:07")
  field 7 (LD): speed           (string, e.g. "0.0 km/h")
  field 8 (varint): icon        (1-4)
```

## Navigation States

| Value | State | Description |
|-------|-------|-------------|
| 2 | Dashboard widget | Compact view in dashboard |
| 7 | Active navigation | Full navigation display |

## Icon Types

| Value | Icon | Description |
|-------|------|-------------|
| 1 | Turn Left | Left turn arrow |
| 2 | Turn Right | Right turn arrow |
| 3 | Straight | Continue straight |
| 4 | U-Turn | U-turn arrow |

## Example Payload

A navigation update showing "Turn left in 100 m":

```
08 07           field 1: state = 7 (active navigation)
10 <msgId>      field 2: message ID (varint)
2A <len>        field 5 LD: nested message
  08 04         inner field 1: type = 4
  12 05         inner field 2 LD: "100 m"
    31 30 30 20 6D
  1A 09         inner field 3 LD: "Turn left"
    54 75 72 6E 20 6C 65 66 74
  22 05         inner field 4 LD: "7 min"
    37 20 6D 69 6E
  2A 05         inner field 5 LD: "701 m"
    37 30 31 20 6D
  32 0A         inner field 6 LD: "ETA: 13:07"
    45 54 41 3A 20 31 33 3A 30 37
  3A 08         inner field 7 LD: "0.0 km/h"
    30 2E 30 20 6B 6D 2F 68
  40 01         inner field 8: icon = 1 (turn left)
```

## Usage Notes

- All string fields are UTF-8 encoded
- The `message_id` should be incremented for each update
- Navigation updates are write-only — no ACK is expected from the glasses
- State 7 activates the full navigation UI; state 2 shows a compact widget
- Auth is required before sending navigation commands
