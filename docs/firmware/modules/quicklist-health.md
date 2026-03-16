# Quicklist + Health Module (0x0C)

## Scope
- Command service: `0x0C-20`
- Response service: `0x0C-00`
- Shared handler family in firmware (`quicklist` + `health`) with protobuf `command_id` dispatch.

## Firmware Evidence (Binary)
- `pb_service_quicklist` path string at `ota_s200_firmware_ota.bin:0x0026FA38`
- `[pb.quicklist]quicklist command_id: %d` at `0x002C8D10`
- `[pb.quicklist]pItem:uid = %d, index = %d, isCompleted = %d, title.size = %d, timestamp = %lld, ts_type = %d` at `0x00267F30`
- `[pb.quicklist]pMultItems:data_type = %d, total_count = %d, items_count = %d` at `0x00280C44`
- `[pb.health]health command_id: %d` at `0x002D29E0`
- `[pb.health]pSingleData:data_type = %d, goal = %d, value = %f, avg_value = %f, duration = %d, trend = %d` at `0x002D2A80`
- `[pb.health]pMultData:data_type = %d, data_set_count = %d` at `0x002D2A58`
- `[pb.health]pSingleHighlight:data_type = %d, text_size = %d` at `0x002D2AA8`
- `[pb.health]pMultHighlight:Highlight_count = %d` at `0x002B78D8`
- `APP_PbRxHealthFrameDataProcess` at `0x002DE578`
- `PB_RxHealthSingleData` at `0x002F2804`
- `PB_RxHealthMultData` at `0x002F9898`
- `PB_RxHealthSingleHighlight` at `0x002E8DF0`
- `PB_RxHealthMultHighlight` at `0x002E8E0C`
- `APP_PbTxEncodeHealthSingleData` at `0x002DE5B8`
- `APP_PbTxEncodeHealthMultData` at `0x002DE5F8`
- `APP_PbTxEncodeHealthSingleHighlight` at `0x002D3900`
- `APP_PbTxEncodeHealthMultHighlight` at `0x002D3948`
- `quicklist_handle_full_update` at `0x002E11C4`
- `quicklist_handle_add_up_update` at `0x002E11E4`
- `quicklist_handle_modify_update` at `0x002E1224`
- `quicklist_handle_add_down_update` at `0x002D7294`
- `page_state_sync_quicklist_expanded` at `0x002D25A8`

## Capture Evidence (2026-03-02)
From `captures/20260302-2-testAll/tasks.txt` and `captures/20260302-3-testAll/tasks.txt`:
- TX (`0x0C-20`) payload: `08018784` (decoded `f1=1`)
- RX (`0x0C-00`) payload: `08011a008bda` (decoded `f1=1`, `f3=empty`)
- Observed behavior for this flow: delayed ACK envelope on `0x0C-00`.

## Current Simulator Behavior (`g2-mock-firmware/src/ble_core.cpp`)
- Maintains persistent quicklist item state keyed by UID.
- Maintains persistent health record state keyed by `data_type` plus highlighted type precedence for query responses.
- Health parser accepts both:
  - firmware-aligned numeric ordering (`goal` then `value`/`avg_value`)
  - legacy simulator app ordering (`value` then `goal`) for backward compatibility
- Health numeric decoding accepts both protobuf varint and fixed32-float wire types (firmware logs print `value`/`avg_value` as `%f`).
- Supports command IDs:
  - `1` full update: clears state, applies repeated item payloads
  - `2` batch add: upsert items
  - `3` single item: upsert item
  - `4` delete: remove by UID
  - `5` toggle complete: update completion by UID (explicit value or toggle fallback)
  - `6` paging request: returns next page by anchor UID
  - `10` health batch save: parses repeated `f5` records and upserts health data state
  - `11` health highlight update: updates record state and highlight type
  - `12` health query: returns stateful repeated `f5` health records (highlighted type first)
- Paging response generation:
  - emits up to `6` items (`QUICKLIST_PAGE_SIZE`)
  - sorted by item index when present, then UID
- ACK envelope remains firmware-compatible (`f1=1`, optional `f2`, `f3=empty`).

## Wire Shape Modeled for Items
- Per-item nested fields under repeated `f5`:
  - `f1` UID (varint or string accepted)
  - `f2` index
  - `f3` isCompleted
  - `f4` title
  - `f5` timestamp
  - `f6` timestamp type

## Wire Shape Modeled for Health Records
- Per-record nested fields under repeated `f5`:
  - `f1` `data_type` (string preferred; varint accepted as fallback)
  - `f2` goal (canonical; firmware log order)
  - `f3` value (`float32` fixed32 preferred; varint fallback)
  - `f4` avg_value (`float32` fixed32 preferred; varint fallback)
  - `f5` duration
  - `f6` trend
- Compatibility shim:
  - if `f3` value is absent and `f2` exists, simulator treats `f2` as legacy `value` and reinterprets `f3` as legacy `goal`.
- Known type labels included in simulator state (from firmware strings):
  - `HEART_RATE`, `BLOOD_OXYGEN`, `TEMPERATURE`, `STEPS`, `CALORIES`, `SLEEP`, `PRODUCTIVITY`, `ACTIVITY_MISSING`

## Next Actionable Improvements
1. Recover exact `health command_id` table for `SingleData/MultData/SingleHighlight/MultHighlight` routing and bind each variant to concrete protobuf field layouts.
2. Confirm firmware paging edge behavior (anchor-not-found, end-of-list, wrap behavior) from deeper captures.
3. Add replay fixtures for mixed quicklist + health sequences (full update -> toggle -> health save/highlight -> health query), including fixed32 metric fields.
