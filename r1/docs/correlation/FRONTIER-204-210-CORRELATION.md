# 204...210-byte frontier correlation

The five largest unresolved application functions after the 212...222-byte closure are now
source-routed from their complete Ghidra extents, immutable body hashes, direct Thumb branch
words, recovered call context, literal records, strings, and provider boundaries.

| Recovered function | Bytes | Disposition |
| --- | ---: | --- |
| `0x00089EEC..<0x00089FBE` | 210 | R1 Goodix-facing stream-registration configuration |
| `0x00093628..<0x000936F8` | 208 | blocked unattributed shared tensor-arena runtime |
| `0x0008A64C..<0x0008A718` | 204 | R1 six-bucket activity-record expansion |
| `0x00064B24..<0x00064BF0` | 204 | R1 newest-valid-slot adapter over FAL/device reads |
| `0x0004D4AC..<0x0004D578` | 204 | R1 connection-mode adapter over Nordic GAP SVCs |

The tier contains five functions / 1,030 bytes. `summarize_r1_frontier_204_210.py` pins every
extent and SHA-256 against recovered application image
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1`.

## Product-owned behavior

`0x00089EEC` clears a 240-byte R1 state block, binds eight callback slots, then registers and
enables these named channels in this exact order: `hr` (4 bytes/type 1), `spo2` (6/type 2),
`raw_hr` (124/type 5), `wear` (2/type 3), `gray` (12/type 8), `aging` (12/type 9), `hrv`
(10/type 4), and `adt` (24/type 7). `r1_sensor_stream_registration_plan` exposes only this
configuration. It neither recreates the callbacks nor the still-unattributed generic
sensor-stream registry/scheduler.

`0x0008A64C` rejects a null six-word record, hours above 23, timestamps above the recovered
maximum, future recorded timestamps, and future local-day starts. An admitted record expands to
bucket indexes `hour * 6 + 0...5`. `r1_activity_flash_record_enqueue_plan` feeds those six words
through the existing bounded 16-byte offline queue and reports accepted, dropped-zero, and
overwritten counts. Time acquisition, flash decoding, and logging remain outside this function.

## Provider adapters

`0x0004D4AC` is called from the R1 BLE connection-event consumer. It selects one of four public
Nordic `ble_gap_conn_params_t` records and invokes S140 SVC `0x7A`
(`sd_ble_gap_ppcp_set`) followed by SVC `0x75` (`sd_ble_gap_conn_param_update`). The recovered
records at `0x0009917A` are default `{72,84,4,600}`, fast A `{12,24,4,600}`, fast B
`{12,24,4,600}`, and glasses `{16,16,2,600}`. `r1_connection_parameter_mode_adapter` owns only
the role/state no-op and profile-selection policy. `openr1_connection_parameter_mode_apply`
passes the selected public record to the pinned Nordic SDK 17.1.0 APIs; no SoftDevice code is
recreated.

`0x00064B24` scans configured slots newest-to-oldest, requests an exact 24-byte header through a
configured flash-device read callback, and accepts the first header whose little-endian word at
offset 12 matches the device magic. It returns the next slot (`latest + 1`) or zero when none is
valid and continues past failed/short provider reads. `r1_latest_valid_flash_slot_scan_adapter`
implements that bounded scan over `r1_flash`; Nordic fstorage and upstream FAL/FlashDB remain the
storage providers. The raw branch-word scanner reports `0x00094F38` as a caller, but that address
falls in a Ghidra function gap and may be branch-looking data, so no caller-identity claim depends
on it.

## Blocked shared runtime

`0x00093628` maintains twelve tensor descriptors in an approximately 1,700-word shared arena. It
sorts live offsets, compacts buffers, and allocates a requested span. Direct callers at
`0x00091DAC` and `0x00091DD6` sit in descriptor/graph construction used across independently
gated GoMore and Goodix paths. No exact third-party source, version, or license has been
authenticated. The body is therefore classified
`unknown_shared_quantized_neural_runtime_candidate` with disposition
`investigate_before_implementing`; OpenR1 does not synthesize a substitute allocator.

## Rebuilt unsigned image

The retained clean-room symbols are `r1_activity_flash_record_enqueue_plan` at `0x000344EC`,
`r1_system_control_command_37_plan` at `0x0003642C`,
`r1_latest_valid_flash_slot_scan_adapter` at `0x0003661C`,
`r1_sleep_sync_plan_acknowledgement` at `0x00036842`, `r1_fds_plan_event` at `0x0003686C`,
`r1_connection_parameter_mode_adapter` at `0x000369A0`,
`r1_sensor_stream_registration_plan` at `0x00037430`, `r1_bae8_plan_hvx_result` at
`0x00038AE2`, `openr1_cmbacktrace_log_task_snapshot` at `0x00039910`,
`openr1_connection_parameter_mode_apply` at `0x000399EC`, and
`openr1_storage_plan_fds_event` at `0x0003AFA8`.

The linked image contains 94,804 bytes of text, 236 bytes of data, and 132,544 bytes of BSS. Its
95,040-byte BIN has SHA-256
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`; the standalone HEX has
SHA-256 `48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf`.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_frontier_204_210.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```

Code signing, deployment authorization, private keys, provider substitution, security bypasses,
live programming, and raw captured health data remain outside this closure.
