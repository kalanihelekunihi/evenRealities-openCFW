# G2 logger-settings object and provider recovery

Status: read-only, fail-closed closure of the stock 2.2.6.10
`app\gui\logger\logger_setting.c` translation unit. No overlay, package,
signer, flash, filesystem, BLE, or hardware state is changed.

## Result

The retained path originally appeared to cover one 84-byte Ghidra function.
That was only the visible anchor. Two additional copies of the same path
pointer occur inside a large callback that baseline Ghidra did not define, and
its compiler pools bridge the entire physical interval
`[0x00458DF0,0x0045A558)`.

The closed object contains eight functions / 5,574 function-envelope bytes.
Recursive Thumb reachability separates 5,466 instruction bytes from 108 bytes
of embedded compiler data. Four outer pools contribute another 418 bytes, for
5,992 physical bytes total.

| Function | Stock interval | Bytes | Recovery basis |
|---|---:|---:|---|
| BLE-log transmit setter | `[0x00458DF0,0x00458E32)` | 66 | baseline function plus internal calls |
| BLE-log enabled getter | `[0x00458E32,0x00458E48)` | 22 | baseline function plus internal call |
| `loggerSetting_cancel_ble_transmit` | `[0x00458E48,0x00458E9C)` | 84 | retained exact name/path and external call |
| file-size helper | `[0x00458E9C,0x00458ED2)` | 54 | internal direct call and complete return |
| `delete_all_files_in_dir` | `[0x00458ED2,0x0045904A)` | 376 | retained exact name and internal call |
| `scan_log_files` | `[0x00459050,0x00459264)` | 532 | retained exact name and internal call |
| `loggerSetting_common_data_handler` | `[0x004592DC,0x0045A386)` | 4,266 | retained exact name/path and callback pointer `0x006A4564` |
| `simplify_log_filename` | `[0x0045A3B4,0x0045A462)` | 174 | retained exact name and internal call |

Only the first three functions existed in the immutable 7,370-function
baseline. A clean no-analysis headless replay seeded at all eight reviewed
entries independently produced the same boundaries and control flow. The
checked analyzer reconstructs the functions directly from authenticated Thumb
branches, rejects unresolved jump tables or escaped control flow, and pins all
2,015 reachable instructions.

## Protocol behavior

The stored callback accepts phone event `0`, peer file-list event `0x0B`, and
peer delete-result event `0x0C`. It decodes and encodes `LoggerDataPackage`
through nanopb. Phone command IDs are:

| ID | Behavior |
|---:|---|
| 0 | connection heartbeat |
| 1 | BLE logger switch; requires union tag 3 |
| 2 | BLE logger level; requires union tag 4 |
| 4 | scan and return file list |
| 5 | delete one role-qualified file; requires union tag 7 |
| 6 | delete every regular file in `/log` |

Command 3 and other values take the unknown-command path in this image.

The file inventory is a 0x328-byte record: at most twenty 40-byte entries,
followed by count and total-size words. Each entry contains a 31-byte bounded
name plus terminator, a 32-bit size, and an 8-bit type. Dot entries and
`compress_manager.bin` are excluded. Regular-file size is recovered by
open/seek/tell/close. `compress_log_N.bin` is rendered as `<role>:N`, while
`hardfault.txt` becomes `<role>:h`.

Delete requests are copied to a bounded buffer and validated against the
role-dependent `L:/log/` or `R:/log/` prefix before removal. File lists and
delete results are routed between phone, master, and slave using the existing
G2 role and message providers. A 100-tick `vTaskDelay` precedes one
master-to-slave list transfer.

## Dependency and commit result

No third-party implementation is embedded in this object. Its 338 external
direct calls terminate at already admitted boundaries:

| Boundary | Calls | Recovered source state |
|---|---:|---|
| EasyLogger diagnostics | 250 | 2.2.99-equivalent core; selected `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` |
| EasyLogger/G2 BLE-log controls | 4 | upstream `elog_set_filter_lvl` plus bounded G2-local mirror/callback adapters |
| IAR DLIB primitives | 39 | EWARM 9.20+ floor, 9.60.2 leading candidate; exact release unavailable |
| nanopb streams and messages | 16 | compatible 0.4.7–0.4.9.1; selected 0.4.9 commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824` |
| G2 file wrappers over littlefs | 12 | littlefs v2.10.1-equivalent commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318` |
| FreeRTOS `vTaskDelay` | 1 | exact V10.5.1 commit `def7d2df2b0506d3d249334974f51e427c17a41c` |
| G2 role/BLE/message policy | 15 | private first-party source |
| G2 compressed-log drain | 1 | private first-party downstream logger integration |

The logger object therefore adds no dependency family, no opaque utility
definition, and no new version discriminator. In particular, its nanopb and
littlefs calls do not narrow their already documented binary-equivalent
checkout intervals, and its DLIB string scanner does not identify an exact IAR
archive. The private `logger_setting.c`, generated LoggerDataPackage schema,
and producing Even commit remain unavailable; historical 2.0.9 analyses are
useful semantic corroboration only, not redistribution source or commit proof.

## Topology and boundary

Nine direct BL sites land exactly on reviewed entries: eight internal and one
external call to the cancel function. The common handler has the sole stored
Thumb pointer. There are zero BL decodes to strict function interiors, zero
unrecovered direct targets inside the physical object, and no other stored
entry pointer. The object follows an EFS function/pool and ends exactly before
the independent role-state function at `0x0045A558`.

The production overlay contains no logger-settings source or redirect. A
future clean-room implementation must reconstruct the private protobuf schema
and validate destructive file commands, role routing, BLE transport, and
littlefs behavior on a disposable target before admission.

## Reproduction

```sh
make logger-settings-closure
```

This authenticates every function, compiler-data island, outer pool, path
pointer, call edge, stored callback, provider pin, and the aggregate
first-party frontier. It performs no hardware operation.
