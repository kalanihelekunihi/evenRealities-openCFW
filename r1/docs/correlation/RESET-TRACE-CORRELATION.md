# Retained reset-trace correlation

Snapshot: 2026-08-12.

## Result

Twelve recovered functions / 598 bytes implement a small R1-owned retained reset-trace policy
and one bounded adapter to the Nordic/CMSIS reset primitive. The record behavior is independently
implemented in `r1/src/r1_reset_trace.c`. No Nordic reset implementation, CmBacktrace unwind
implementation, or other provider body is reconstructed locally.

The recovered application image used for every byte and caller check has SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

## Recovered record

The retained record is exactly 16 bytes:

| Record bytes | Meaning |
| --- | --- |
| `0` | validity marker; valid records contain zero |
| `1` | logical field 0: persist tag |
| `2` | logical field 1: reboot caller |
| `3...6` | logical fields 2...5: return address, little-endian |
| `7...10` | logical fields 6...9: program counter, little-endian |
| `11...13` | logical fields 10...12: reserved trace data |
| `14...15` | little-endian Modbus CRC16 over bytes `0...13` |

An invalid record is zeroed and resealed before mutation. Writing a reboot caller clears both
addresses. Writing any persist tag other than persist tag `7` also clears both addresses; tag `7`
is the recovered fault tag and preserves the address fields until the fault site is captured.
Address reads fail on invalid CRC or validity marker rather than returning untrusted retained RAM.

## Exact executable closure

The hash for each row covers the exact executable extent. The capture adapter is scatter-loaded:
its 74-byte hash concatenates `0x00058A9A..<0x00058AB8` and
`0x0007EEDA..<0x0007EF06` in that order.

| Entry / extent | Bytes | Clean-room name | SHA-256 | Direct callers |
| --- | ---: | --- | --- | --- |
| `0x00027484..<0x00027488` | 4 | `r1_reset_trace_program_counter_probe` | `2f36aa868e36a46cb9de8406212506a64e14817b3c631b90f30a905674fac3f9` | `0x00058A9E`, `0x0007EFEC` |
| `0x00058A9A..<0x00058AB8` + `0x0007EEDA..<0x0007EF06` | 74 | `r1_reset_trace_capture_site_adapter` | `bde43a241c98603e87d276d909e04b4a3a886c3f8f4105bfb05858b753ad5c39` | `0x0008F30A` |
| `0x0007A5E0..<0x0007A604` | 36 | `r1_fault_reset_adapter` | `77f3d4d2be4de22f3dc279b544d03040d312d8ee7be3ea82d20d34ffb0a47388` | five exception vectors at `0x000274B4...0x000274E4` |
| `0x0007EDFC..<0x0007EE2C` | 48 | `r1_reset_trace_byte_read` | `bdba1d9e048b2fdcd3026ae9e30695dbdfaf87cfbd0f2f1999717c17d202355a` | ten, including boot diagnostics `0x00081AF4`, `0x00081B42` |
| `0x0007EE30..<0x0007EE76` | 70 | `r1_reset_trace_byte_write` | `6704ba247e2313adaff20df009598e1182e338277b3e4e92a6c088c79b621635` | eighteen record mutators |
| `0x0007EE7C..<0x0007EEDA` | 94 | `r1_reset_trace_return_address_read` | `f18ca971732969e60bc92ceba01f0b9d43786390c6df5bae0f669bff265997aa` | `0x00081AB8` |
| `0x0007EF06..<0x0007EF4C` | 70 | `r1_reset_trace_addresses_clear` | `75f3a2038e40662326683c09ae2a344c2cf935360fa1425348f475b9315a49e5` | `0x0007EFDA`, `0x0007F006` |
| `0x0007EF4C..<0x0007EFAA` | 94 | `r1_reset_trace_program_counter_read` | `957a422f61c5ef5d497ff8db7e28e5a17af0a6ab0c47df4358d6d1ebdb23d593` | `0x00081A7A` |
| `0x0007EFAA..<0x0007EFD6` | 44 | `r1_reset_trace_program_counter_write` | `87f1ceef56d1255890b15f103c2afd4e426ccf58606f6e59ca899323d79a721a` | `0x00058AA4`, `0x0007EFF0` |
| `0x0007EFD6..<0x0007EFEA` | 20 | `r1_reset_trace_reboot_caller_write` | `f5f20cd326030969b639bda3b9561b04fbc68e6ac180ed986ede7131b6944464` | `0x0003E9CE`, `0x00084428` |
| `0x0007EFEA..<0x0007EFFE` | 20 | `r1_reset_trace_current_site_capture` | `c997bcb97299bfbeaf3eedf09363fb0e3b48ee027af96d4412cb379c34a0e6b4` | `0x0004602C`, `0x0004606E`, `0x00046090`, `0x0007A5E6` |
| `0x0007EFFE..<0x0007F016` | 24 | `r1_reset_trace_persist_tag_write` | `0f14dfd6b784417c86fd3f583af41a31c055e046f496d05a4ccb53895c110b86` | six, including the fault adapter at `0x0007A5E2` |

The exact complete caller sets, including all byte-write sites, are machine-checked by:

```sh
PYTHONPATH=tools \
python3 tools/summarize_r1_reset_trace_closure.py
```

## Product/provider boundary

Eleven functions are classified `r1_product_specific` with disposition
`clean_room_behavior_only`. The function at `0x0007A5E0` is classified
`r1_nordic_cmsis_provider_adapter` with disposition
`clean_room_adapter_only_use_nordic_sdk_and_cmsis`: local code records the recovered fault tag and
site, then calls Nordic SDK 17.1.0 CMSIS `NVIC_SystemReset`. CMSIS owns the barriers, AIRCR reset
request, and non-returning reset behavior.

Armink CmBacktrace remains the fault-diagnosis and unwind provider. The local exception glue gives
CmBacktrace the original exception LR/SP first, then records the reset-wrapper's own PC/return site,
matching the stock separation between fault diagnosis and the retained reset hook.

## openR1 implementation and verification

The portable module tests record initialization, the exact zero-record CRC bytes, field bounds,
little-endian address packing, invalid-record repair, tag-7 preservation, non-fault clearing,
reboot-caller clearing, capture, snapshot, and null handling. Host, ASAN/UBSAN, and Cortex-M4 object
builds pass.

The Nordic target retains the record in `.openr1_noinit` and publishes a retained internal API in
`.openr1_reset_trace_api`. In the current linked image:

- portable functions start at `0x00035146`, with snapshot at `0x0003528C`;
- the retained-record accessor, capture adapter, and fault/reset adapter link at `0x00037AC0`,
  `0x00037AD0`, and `0x00037B04`;
- `.openr1_reset_trace_api` is 16 bytes at `0x0003BE48`;
- the 16-byte record is at RAM `0x20026AD4`;
- the image is text 85,608, data 220, BSS 132,448 bytes;
- HEX SHA-256 is `48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf`;
- BIN SHA-256 is `421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`.

Code signing, boot redirection, and deployment bypass remain outside this implementation.
