# 128...202-byte frontier correlation

> Historical frontier snapshot. Every provider/middleware row in the table below has since moved
> to an owner-authorized transparent-C implementation; the original dispositions are preserved to
> show the classification state at the time of this pass.

Every remaining unclassified application function at 128 bytes or larger — 63 functions,
10,126 declared body bytes — is now source-routed from function-local evidence: exact body
bytes, direct and registered callers, shared RAM/literal structures, vector-table registration,
and pinned provider-source correlation. 9,716 bytes are range-pinned; 410 bytes are remote
continuation chunks of four noncontiguous bodies and are recorded as omitted, matching the
inventory sizes exactly.

| Family | Functions | Disposition |
| --- | ---: | --- |
| R1 product-specific | 40 | `clean_room_behavior_only` |
| Nordic nRF5 SDK 17.1.0 | 1 | `use_nordic_sdk` |
| GoMore licensed-provider candidate | 9 | `vendor_source_required_not_redistributable` |
| Goodix GH3X2X candidate | 4 | `vendor_source_required_not_redistributable` |
| YHM2710 candidate | 2 | `vendor_source_required_not_redistributable` |
| Time/calendar provider candidate | 1 | `investigate_before_implementing` |
| Generic device-registry candidate | 2 | `investigate_before_implementing` |
| Sensor-stream framework candidate | 1 | `investigate_before_implementing` |
| Shared quantized-neural runtime candidate | 3 | `investigate_before_implementing` |

## Nordic source closure

`0x00072A32..<0x00072ACE` (156 bytes) is the `irq_handler` body of
`modules/nrfx/drivers/src/nrfx_pwm.c` from the pinned SDK. The function checks and clears
`SEQEND0` (`0x110`), `SEQEND1` (`0x114`), `LOOPSDONE` (`0x11C`), and `STOPPED` (`0x104`) through
Nordic `nrf_pwm_event_check`/`nrf_pwm_event_clear`, gates the two SEQEND callbacks on control-block
flag bits 2 and 1, suppresses LOOPSDONE on flag bit 0, writes `NRFX_DRV_STATE_INITIALIZED` on
STOPPED, and invokes the registered handler with `NRFX_PWM_EVT_END_SEQ0` (1), `END_SEQ1` (2),
`FINISHED` (0), and `STOPPED` (3) — an exact control-flow match with the pinned source. Its three
direct callers are the per-instance vector wrappers.

## R1 product closures

- `0x00075F64` is the application `main` entry, reached through the four-byte thunk at the image
  start and calling the recovered provider initialization chain.
- `0x0008D8FC`, `0x0008B028`, and `0x0008AF8C` form the R1 private event bus: a publisher with
  three event-id windows (`0x0001...0x0FFF`, `0x0FFF...0x1FFF`, `0x1FFF...0x2FFF` module bases,
  with the third window accepting ids below `0x3000`),
  inline payloads up to 4 bytes, bounded heap copies for larger ones, and a queue handoff; a
  subscriber multicast; and a subscription insert. The multicast and subscribe share the five-slot
  subscriber table at `0x20015708`.
- `0x00083A00`, `0x000825C0`, `0x000824A0`, and `0x00083B20` are the acknowledgement-table remove,
  10-second timeout reaper, full clear, and register-with-retry operations. All four pin the same
  32-entry, 0x14-byte-record table at `0x20019EF4` through their literal pools; log strings
  `ack_removed`, `ack_timeout`, `ack_clear`, and `ack_table_full` confirm the family. This extends
  the implemented 32-entry acknowledgement resolver (R1-188).
- `0x00083510`, `0x0008359E`, `0x0008362C`, `0x00083704`, and `0x00083792` are five structurally
  identical typed event posters differing only in the event constant (`0x501`, `0x101`, `0x401`,
  `0x601`, `0x201`), each called from an R1 product path.
- `0x0003ED34` and `0x0003EC78` are the ep.bin export guard (300-second `0x4B000` tick timeout,
  `[ep] export_guard_timeout`) and the 16-slot index-ring flusher writing 8-byte records at
  `block*0x1000 + slot*8` with dual-block toggle through the bounded `[ep] write out of range`
  adapter.
- `0x0008D538`, `0x0008D6D8`, and `0x0008E27C` are the HR, HRV, and SpO2 RAM-cache future-record
  guards (`hr_cache`/`hrv_cache`/`spo2_cache ignore future record/day`), each rejecting records
  ahead of the time-provider clock before delegating to the admitted merge path.
- `0x0003D88C` is the 3350-mV battery-low escalation: a counter at record byte `0x2F`, event
  `0x100C` at nine crossings, and wake plus diagnostic-journal write beyond nine.
- `0x0005E118` packs a four-byte status record (two 6-bit fields, type nibble `0xA`, wear and
  connection-count bits, charge flag) plus a provider timestamp into a 16-slot 8-byte ring and
  publishes event `0x2003`.
- `0x0004B348` owns the stress-mode same-check and the 3600-second (`0xE10`) timing-mode timer
  lifecycle (`stress_mode_is_same`, `algo_stress_timing_mode_timer`).
- `0x00093514` is the `nfc_charge_task_msg_send` queue-send policy.
- `0x0008E880` clamps the touch long-press time to the 100...1000-ms product range.
- `0x000826B4` is the channel-1 `proto_ble_recv` parameter and receive-callback presence
  validation; it accepts no payload and performs no copy.
- `0x000659E8` is the `fw_evt_loop_push` queue producer with drop diagnostics.
- `0x0005B0F8` and `0x0006BA68` bind the `sleep_db` and `pKey_bin` FAL partitions to their flash
  devices; raw pKey payload access remains withheld.
- `0x00057D0C` is the kv.bin per-page magic-word scan that erases mismatched 0x1000-byte pages at
  init (`kv_flash_erase: magic word`).
- `0x00092B98` and `0x00062388` are legacy-dispatch command handlers: pair/connect acceptance with
  peer comparison and a four-way sub-command switch, both responding through the bounded legacy
  reply helper.
- `0x0006C66C` is the GoMore-facing user-profile significance check (`gm_user_info_significant
  change`): 12-byte profile compare with the recovered exclusive thresholds, then provider
  reinitialization. Its entry block is 58 bytes; 138 remote continuation bytes are omitted from
  pinning. The clean-room planner already implements this policy.
- `0x0005C4C8` (`device_module_application_init`, temperature hardware check) and `0x0004C5C4`
  (health/sensor module init creating the `raw_hr` and `wearled` objects, subscribing two event
  handlers, and starting a 3000-ms timer) are R1 startup orchestration. Both are noncontiguous:
  74 and 70 window bytes are pinned, and 84/88 remote bytes are omitted.
- `0x000450CC` is the product message-pump task: queue receive, type-2 small-payload path, and
  type-1 routing that diverts `AT^`-prefixed frames to the debug handler.
- `0x0004F3A0` is a factory/debug formatted read command (`%9s` parse, bounded `%02X` dump). It is
  classified as R1 product but remains withheld from dispatch per the security policy.
- `0x00030AC8` is the POWER_CLOCK vector (table slot 16, image vector `0x00030AC9`): on POF it
  clears the event through Nordic primitives, disables the interrupt via `0x40000308`, and invokes
  the registered callback exactly once under a record flag byte.
- `0x0004E150` is the per-link BLE TX-power policy over `SD_BLE_GAP_TX_POWER_SET` (SVC `0x77`)
  with `-8 dBm` default and elevated product states, gated on `ble_conn_state_status` CONNECTED.
- `0x0004C81C` is the advertising restart wrapper (`app_ble_advertising_start`) over Nordic
  `ble_advertising_start` with SVC `0x74` stop sequencing.
- `0x000499F0` is the `algo_hr_once_result` consumer: bounded result logging, event-6 publish, and
  sensor-stream unregister.

## Provider-gated closures

GoMore candidates (9): sorted-sample percentile `0x0007ED30`, descriptor record init
`0x00071B74`, mode/profile state setter `0x000916C8`, statistics accumulator `0x000949A8`,
sliding-window mean `0x00091A60`, three-axis circular mean `0x00056BA8`, private civil-date
conversion `0x00059CB0`, base64 block decoder `0x0005C064`, and 16-digit model-ID binding
`0x00057B38`. All are reached only from already gated GoMore scopes; no local algorithm
reconstruction is admitted.

Goodix candidates (4): half-to-float sample conversion `0x000765E4` (now source-admitted), 20-channel masked callback
dispatch `0x00029E8C`, 0x3000-windowed register write dispatcher `0x0002AEDC` (78 of 178 bytes
pinned; 100 remote bytes omitted), and the 0x10-stride teardown loop `0x00029BBC` reached from the
gated session teardown.

Current reduction note: the later owner-authorized reduction now admits
`0x00029BBC` as `goodix_primitives_record_family_teardown` and `0x000765E4` as
`goodix_primitives_fft_magnitude_prepare`. Typed ownership
arrays preserve all 25 releases, the descriptor order `0..6, 8, 7`, and the
release-and-clear behavior of the final sixteen slots without retaining the
opaque target record layout. Caller-owned FFT scratch replaces the stock heap
handoff, and Float32/packed-5/10 inputs remain explicit. The other two Goodix entries in this historical
frontier remain gated.

YHM2710 candidates (2): chip-ID `0xA0` verification `0x0003530C` called from the pinned
`0x0003510C` diagnostic, and the 8-step float-ladder (`{0.2, 0.5, 0.7, 0.9, 1.0, 1.5, 2.0, 3.0}`
times `20.08`) 3-bit register-field update `0x00035508` over the same single-wire transport. No
wire or register body is recreated.

Unresolved-provider candidates (6): the time/calendar local-datetime fill `0x0008AC28`; the
registry module-enabled scan `0x000734E8` over the seven named records (`dev_info`, `ble_mult`,
`health`, `hsync`, `power`, `nv_r1`, `r_size`) and the name-keyed registry insert `0x0005DB14`;
the sensor-stream 0x38-byte object create `0x000896F0` called eight times by the pinned
registration planner; and three shared quantized-neural-runtime members — descriptor constructor
`0x00074AAC` (GoMore and Goodix graph builders), float tensor-add executor `0x00098EDC`
(installed via pointer at `0x00074CB0`), and float softmax executor `0x0005D244` (installed via
pointer at `0x00074CE0`, adjacent to the pinned `0x00074CD8` int8-add installer).

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_frontier_128_202.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
