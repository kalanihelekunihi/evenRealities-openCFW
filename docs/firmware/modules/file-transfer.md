# File Transfer + Export Module (`0xC4` / `0xC7`)

## Scope
- Upload command/data services: `0xC4-00` / `0xC5-00`
- Export command/data services: `0xC6-00` / `0xC7-00`
- Export reply/data services: `0xC2-00` / `0xC3-00`
- Physical BLE channel: file characteristic (`0x7401` write / `0x7402` notify)
- Covers both phone->glasses send and glasses->phone export flows.

## Firmware Evidence (Binary)
- `_efsExportFileParse` symbol string
- `[efs.service]eEvenFileExportServiceCID_EVEN_FILE_SERVICE_CMD_EXPORT_START = %d ms`
- `[efs.service]eEvenFileExportServiceCID_EVEN_FILE_SERVICE_CMD_EXPORT_RESULT_CHECK response = %d`
- `[ota.service]export filePath = %s`
- `[ota.service]export file %d%% eclipse time: %d ms speed : %d KB/S`

## Current Simulator Behavior (`g2-mock-firmware/src/ble_core.cpp`)

### Send Flow (phone -> glasses)
- `FILE_CHECK` (`0xC4`, 93-byte header): stores file metadata and responds with LE16 status `0`.
- `START` (`0xC4`, payload `0x01`): accepted without dedicated ACK (matches local captures).
- `DATA` (`0xC5`): accumulates bytes/chunks and responds with LE16 status `1`.
- `END` (`0xC4`, payload `0x02`): responds with LE16 status `2`, logs transfer summary, emits proactive devinfo on `0x04-01`.

### Export Flow (glasses -> phone, firmware-backed lane split)
- Phase-0 export start uses `0xC6` with payload `[phase=0][transferKind][path...]`
  - `transferKind=0xAA` exports an existing file path
  - firmware copies the path into an `0x50`-byte export context buffer
- Successful export start replies on `0xC2-00` with a 10-byte open reply
  - bytes `2..5` = file size (LE32)
  - bytes `6..9` = CRC32 (LE32)
- Export data then streams on `0xC3-00`
- The old `0xC4/0xC5`-based export model was an app-side inference and is not the authoritative firmware path

## Next Actionable Improvements
1. Confirm whether phase `2` completion is required for all exports or only for specific app flows.
2. Validate multi-chunk counter edge behavior (wrap, mismatch/error responses) against additional traces.
3. Add capture-replay fixtures for mixed notification-send + logger-export sessions on the same file channel.
