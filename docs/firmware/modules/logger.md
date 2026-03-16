# Logger Module (0x0F)

## Scope
- Command service: `0x0F-20`
- Response service: `0x0F-00`
- Log namespace and control-plane commands for file list/delete/delete-all/live settings.

## Firmware Evidence (Binary)
- `loggerSetting_common_data_handler` at `ota_s200_firmware_ota.bin:0x0027A534`
- `loggerSetting_common_data_handler: invalid file path, must start with /log/: %s` at `0x0026C488`
- `loggerSetting_common_data_handler delete file failed: %s` at `0x0027FA28`
- `loggerSetting_common_data_handler delete all logger file failed` at `0x0027A534`
- `loggerSetting_common_data_handler: unknown cmd = %d` at `0x0027A66C`
- `[efs.service]eEvenFileExportServiceCID_EVEN_FILE_SERVICE_CMD_EXPORT_START = %d ms` at `0x00284A10`
- `[efs.service]eEvenFileExportServiceCID_EVEN_FILE_SERVICE_CMD_EXPORT_RESULT_CHECK response = %d` at `0x00284A34`
- `[ota.service]export filePath = %s` at `0x002D1EA8`

Known log-path strings in firmware corpus:
- `/log/compress_log_%d.bin`
- `/log/compress_manager.bin`
- `/log/imu_rawdata_%02d%02d%02d.csv`

## Current Simulator Behavior (`g2-mock-firmware/src/ble_core.cpp`)
- Supports command IDs:
  - `1` file list
  - `2` delete file
  - `3` delete all
  - `4` live switch (stores enable flag)
  - `5` live level (stores level, clamped to 0..7)
  - `6` heartbeat (ACK status)
- Path guard implemented from firmware string evidence:
  - delete-file requests are accepted only when path starts with `/log/`
- Simulated resident file set:
  - `/log/compress_log_0.bin` ... `/log/compress_log_4.bin`
  - `/log/hardfault.txt`
- Responses:
  - echo command in `f1`
  - optional `f2` message ID
  - `f3` status payload for live switch / level / heartbeat
  - file list emitted as repeated `f5` strings for list command
- File-service export is firmware-backed on the dedicated export lanes, not the upload lanes:
  - export start uses `0xC6`
  - export open reply uses `0xC2`
  - export data streams on `0xC3`
  - older app-side `0xC4/0xC5` export notes should be treated as historical inference, not authoritative firmware behavior

## Next Actionable Improvements
1. Validate chunk-counter mismatch and retry semantics from additional firmware-era traces.
2. Model file-list behavior from real `/log` directory scans (ordering, missing-file semantics, manager/rawdata files).
3. Reconstruct firmware-native live stream payload envelopes for command IDs `4/5/6` beyond ACK/state storage.
