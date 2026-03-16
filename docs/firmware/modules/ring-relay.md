# Ring Relay Module (`0x91`)

## Scope
- Command service: `0x91-20`
- Response service: `0x91-00`
- Function: protobuf relay path between G2 and R1 ring data/event envelopes (`RingDataRelay_common_data_handler` / `APP_PbRxRingFrameDataProcess` evidence in OTA firmware strings).

## Firmware Evidence (Binary Strings, `ota_s200_firmware_ota.bin`)
- `RingDataRelay_common_data_handler` (`0x002D3D08`)
- `APP_PbRxRingFrameDataProcess` (`0x002DE8E8`)
- `[pb.ring]ring recv eventType = %d, len = %d` (`0x002C07B0`)
- `[pb.ring]ring command_id: %d` (`0x002DE908`)
- `[pb.ring]pEvent:event_id = %d, event_param = %d, ring_mac size = %d` (`0x0028E4A0`)
- `[pb.ring]Unknown command_id: %d` (`0x002DE928`)
- `[pb.ring]Unknown event_id: %d` (`0x002DE948`)
- `[pb.ring]Unknown event type: %d` (`0x002DE988`)
- `[pb.ring]txLen = %d` (`0x002FA2B4`)
- `[pb.ring]len=%d` (`0x002FF200`)
- `PB_RxRingEvent` (`0x002FF220`)
- `APP_PbTxEncodeRingEvent` (`0x002FDD3C`)
- `ring.proto` (`0x00303398`)

Supporting ring transport/runtime strings:
- `[ring.proto]RING_GlassesHeartbeat send`
- `[ring.proto]RING_GlassesHeartbeat recv ok`
- `[ring.proto]glasses status send to ring: %02X %02X`
- `[task.ring]RING_TASK_MSG_HEARTBEAT_EVT`
- `[task.ring]RING_TASK_MSG_RECONNECT_RING`
- `RING_TASK_MSG_RECONNECT_RING`

### v2.0.7.16 Additions
- `RING_CmdTouchUpdata` (`ring.proto` module)
- `[ring.proto]RING_CmdTouchUpdata tick = %d, type = %d` — ring touch events now carry tick (duration/timestamp) and type (gesture classification) metadata
- `RING_TASK_MSG_RECONNECT_RING` — ring reconnection task message (also present in v2.0.6.14)

## Capture Evidence (Current Local Sessions)
- `captures/rawBLE.txt`, `captures/20260301-1-bleraw.txt`, and `captures/20260301-2-bleraw.txt` contain no `0x91-20`/`0x91-00` packets.
- Current command-ID mapping for `0x91` is therefore firmware-string-driven and simulator-inferred (not yet trace-verified).

## Current Simulator Behavior (`g2-mock-firmware/src/ble_core.cpp`)

### Envelope Handling
- Reads outer protobuf:
  - `f1` -> `command_id`
  - `f2` -> message ID
- Emits response on `0x91-00` with mirrored command/message fields.

### `command_id = 1` (Event envelope)
- Parses nested `f3` event payload when present:
  - `f1` ring MAC bytes
  - `f2` event ID
  - `f3` event param (varint or bytes fallback parse)
  - `f4` error code
- Persists ring MAC and last event state.
- Responds with normalized nested event payload on `f3`.

### `command_id = 2` (Raw data envelope)
- Parses nested `f4` raw payload (if provided) and updates internal state:
  - battery, charge state, hr, spo2, hrv, temp, calories, steps, wear status
- Responds with synthetic full raw-data snapshot on `f4` (fields `1..17`) with current timestamps.

### Unknown command path
- Logs unknown command ID and returns protobuf envelope with empty status payload (`f3` empty bytes).

## Next Actionable Improvements
1. Recover authoritative `eventType` and `command_id` enum tables from deeper binary disassembly around `PB_RxRingEvent` / `APP_PbTxEncodeRingEvent`.
2. Replace inferred `command_id=1/2` behavior with trace-validated payloads from real `0x91` captures.
3. Model ring heartbeat/status push traffic (currently only request/response path) using `RING_GlassesHeartbeat*` and `RING_SendGlassesStatusEvt` evidence.
4. Integrate `RING_CmdTouchUpdata` tick/type metadata into ring event envelope parsing — determine whether tick is absolute timestamp or duration, and map type values to gesture classification (tap/hold/swipe).
