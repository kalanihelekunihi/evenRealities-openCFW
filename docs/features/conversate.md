# Conversate / ASR Protocol

The Conversate protocol displays real-time speech transcription on the G2 glasses. Commands are sent on service `0x0B-20`. This protocol requires a hardcoded 2-packet initialization sequence before transcript updates can be sent.

**Source**: `G2ConversateProtocol.swift`, `G2ConversateSender.swift`

## Initialization

Two hardcoded packets must be sent before any transcript updates. These configure the conversate display mode on the glasses.

### Init Packet 1

Configures the display layout.

```
AA 21 2A 18 01 01 0B 20
08 01 10 35 1A 10 08 01 12 0A 08 01 10 01 18 00 20 01 28 00 18 00
63 62
```

Payload breakdown:
```
08 01       field 1: type = 1 (init)
10 35       field 2: msg_id = 53
1A 10       field 3 LD, length 16:
  08 01     nested field 1: mode = 1
  12 0A     nested field 2 LD, length 10:
    08 01   nested field 1: display = 1
    10 01   nested field 2: enabled = 1
    18 00   nested field 3: 0
    20 01   nested field 4: 1
    28 00   nested field 5: 0
  18 00     nested field 3: 0
```

### Init Packet 2

Finalizes session setup.

```
AA 21 2D 09 01 01 0B 20
08 FF 01 10 38 52 00
F3 83
```

Payload breakdown:
```
08 FF 01    field 1: type = 255 (varint, 2 bytes)
10 38       field 2: msg_id = 56
52 00       field 10 LD, length 0 (empty)
```

## Transcript Update Format

After initialization, transcript updates use type=5 frames:

```
08 05                    field 1: type = 5
10 <update_id>           field 2: update counter (varint, never reuse)
3A <len>                 field 7 LD: nested message
  0A 1E <30 bytes>       nested field 1 LD: 30-byte fixed text (space-padded)
  10 <flag>              nested field 2 varint: 0x00=partial, 0x01=final
```

### Text Field Rules

- Fixed length: **30 bytes** (always)
- Encoding: UTF-8
- Padding: right-padded with spaces (`0x20`) if text is shorter than 30 bytes
- Truncation: text longer than 30 bytes is truncated

### Update ID Rules

- Starts at `0x41` (65)
- **Must be incremented** for each update
- **Must never be reused** within a session — the glasses track seen IDs and ignore duplicates

### Partial vs Final Flag

| Value | Meaning |
|-------|---------|
| `0x00` | Partial — more text coming (interim transcript) |
| `0x01` | Final — utterance complete |

## Timing Constraints

| Parameter | Value | Notes |
|-----------|-------|-------|
| Inter-frame delay | 600ms minimum | Between consecutive transcript updates |
| Post-write delay | 50ms minimum | After each BLE write operation |

These delays are critical — sending frames too quickly causes the glasses to drop updates silently.

## Message Sequence

```
1. Auth (3 or 7 packets)
2. Init packet 1 (display config)
   └── 600ms delay
3. Init packet 2 (session finalize)
   └── 600ms delay
4. Transcript update (type=5, updateId=0x41, partial)
   └── 600ms delay
5. Transcript update (type=5, updateId=0x42, partial)
   └── 600ms delay
6. ...
7. Transcript update (type=5, updateId=0xNN, final)
```

## Usage Notes

- Conversate is write-only — no responses are expected from the glasses
- The init sequence is hardcoded from a reference Python implementation; the exact field meanings are inferred but unconfirmed
- Long text should be split across multiple 30-byte frames
- For real-time ASR, send partial results as they arrive, then a final frame when the utterance is complete
