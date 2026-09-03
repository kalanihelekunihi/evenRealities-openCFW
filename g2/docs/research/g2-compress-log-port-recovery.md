# G2 compact-log port recovery

## Result

The retained first-party translation unit
`platform\service\compress_log\port\compress_log_port.c` is closed as twelve
functions in the physical interval `[0x0044A474, 0x0044AA2C)`. The object is
1,464 bytes with SHA-256
`ecded42852da19e04b0e31b75c62e2a0fa3b596ee53f13bed94bde2eaad00411`:
1,324 executable bytes and 140 bytes of mode strings, alignment, and literal
pool data. Eleven entries were present in the authenticated Ghidra corpus; the
stored timeout callback at `0x0044A8B6` was restored from its odd Thumb pointer
at `0x0044AA24`, exact retained symbol, and raw control flow.

The dependency result is favorable for OpenCFW. All eighteen file operations
already reach production source-owned shared-file wrappers over the selected
littlefs v2.10.1-equivalent baseline. All three timeout operations already
reach production source-owned delayed-callback wrappers. The only compiler
runtime dependency is two bounded IAR `snprintf` calls. EasyLogger and the now
closed private compact-log core are diagnostic/record providers, not embedded
definitions.

The object therefore hides no additional third-party library, version, or
commit. Its first-party rotation, manager-file, version-header, and export-state
policy is now implemented in production C and routed over the existing
source-owned file/event providers. Twelve guarded redirects replace all 1,324
callable stock bytes. The private historical producing commit remains
binary-unobservable, but it is no longer a software prerequisite.

## Reproduction

Run:

```sh
make compress-log-port-closure
```

The analyzer authenticates the official G2 2.2.6.10 image, all three
manifests, the complete executable and physical intervals, M-profile Thumb
control flow, call and entry topology, the stored callback, path and diagnostic
strings, manager constants, upstream provenance, all twelve production source
leaves and redirects, 41 strict relocations, and both compiler-profile pins.
The target also compiles and executes the host behavioral suite.

| Evidence | Result |
|---|---:|
| Linked functions | 12 |
| Ghidra-discovered / restored | 11 / 1 |
| Path-anchored functions | 3 |
| Raw path references / referencing functions | 6 / 4 |
| Function body bytes | 1,324 |
| Outer data bytes | 140 |
| Physical bytes | 1,464 |
| Reachable instructions | 526 |
| Direct body calls | 68 |
| Internal / external direct calls | 15 / 53 |
| Indirect calls | 0 |
| Whole-image direct `BL` entries | 23 |
| Stored entry pointers | 1 |
| Strict-interior entries | 0 |

The concatenated body SHA-256 is
`3a7ad30e3761b47953eda29a8237033c7209e950beffc605587f74b3e502ac42`.
The instruction topology digest is
`2be142ae6dd88378871ba1176b8cb5286ace5a8c17da07dbd5b9178c0f352165`.
The direct-call digest is
`24ac77cd8ad08248569a02b25321f89159eed8ce374aba0c3c545e4b41818597`,
and the whole-image direct-entry digest is
`bb3a1f3738e141705139ae867fe0151df0f4cd4ae700d51d6689821e0a46f087`.

## Function inventory

| Entry | Bytes | Recovered role |
|---:|---:|---|
| `0x0044A474` | 20 | format `/log/compress_log_%d.bin` |
| `0x0044A488` | 40 | probe numbered-file existence |
| `0x0044A4B0` | 128 | reconcile manager state against present files |
| `0x0044A530` | 176 | load, validate, and default manager state |
| `0x0044A5E0` | 66 | save the 12-byte manager record |
| `0x0044A622` | 24 | remove a numbered file |
| `0x0044A63A` | 224 | `_write_file_version_header` |
| `0x0044A71A` | 116 | advance and, when needed, evict the five-file ring |
| `0x0044A798` | 286 | `compress_log_sync_to_files` |
| `0x0044A8B6` | 68 | `compress_log_export_timeout_callback` |
| `0x0044A904` | 170 | `compress_log_export_notify` |
| `0x0044A9AE` | 6 | return the export-active flag |

The two ten-byte data gaps hold the exact file modes `rb`, `wb`, `r+b`, and
`w+b`. The 120-byte trailing pool closes the object and contains the stored
timeout callback pointer. The preceding IAR `strlen` ends at `0x0044A472`,
followed by two alignment bytes; the following object begins with a separate
CMSIS mutex initializer at `0x0044AA2C`.

## Rotation and manager format

The port owns five numbered files. Each file is limited to `0x7D000`, or
512,000 bytes. The 12-byte manager record at
`/log/compress_manager.bin` contains:

- 32-bit magic `0x4C4D4752`;
- one-byte active-file index;
- one-byte oldest-file index;
- one-byte valid-file count;
- padding; and
- a 32-bit current offset.

On load, invalid indices above four, counts above five, bad magic, and offsets
at or above `0x7D001` are reset. The reconcile helper probes all five numbered
files and repairs oldest/count state before saving it. When the active file
fills, rotation advances modulo five; at full occupancy it removes the oldest
file and advances that index too. A newly opened file receives the exact
27-byte header:

```text
Software_Version: 2.2.6.10\n
```

The sync function appends caller bytes across file boundaries, updates the
current offset after each successful write, and persists manager state. The
production implementation preserves that policy while calling the existing
OpenCFW-source-owned shared file operations.

## Export timeout

`compress_log_export_notify(1)` sets the export-active byte and schedules the
stored callback after 120,000 ticks. A stop notification removes that delayed
callback and clears the state. On expiry the restored callback emits its
diagnostic and clears the same byte. The pointer at `0x0044AA24` is
`0x0044A8B7`, the odd Thumb encoding of the complete `0x0044A8B6` entry; no
other stored entry or direct interior ingress exists.

## Provider closure

| Provider | Calls | Status |
|---|---:|---|
| EasyLogger controls and `elog_output` | 24 | admitted at commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` |
| Closed G2 compact-output hook | 6 | first-party object-closed; not upstream EasyLogger |
| IAR DLIB `snprintf` | 2 | bounded, EWARM 9.20+ floor / 9.60.2 leading candidate |
| Shared file runtime | 18 | production source-owned over littlefs |
| Delayed-callback runtime | 3 | production source-owned |

The file-runtime entries are exact OpenCFW production redirects for open,
close, read, write, seek, and remove. Their backend uses the authenticated
littlefs source-equivalent v2.10.1 selection at commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. That commit is a reproducible
baseline, not proof of Even's historical checkout; later source states remain
binary-equivalent under the recovered G2 configuration.

The export scheduler entries are exact production redirects for delayed
insertion and removal. The production compact-log implementation calls these
OpenCFW provider APIs directly and does not need another RTOS or timer
implementation.

## OpenCFW production result

`components/apollo_main/core_overlay/compress_log_port.c` (17,905 bytes,
SHA-256 `473ddda6dd3b0f37d0cac08b9a1cbc6d3730fb79540598b9eb99c4c239b2226e`)
implements all twelve functions. The Apple profile emits 1,090 text bytes and
the Linux profile emits 1,086; both carry 41 reviewed relocations and feed the
complete CFF/LC3 firmware builder. Host tests cover manager recovery, rotation,
header creation, cross-file writes, missing-file reconciliation, invalid-state
reset, export start/stop, and timeout expiry.

Live concurrent logging, power-loss recovery, storage wear, and export timing
remain **blocked by unavailable physical evidence**. No hardware, signing,
flashing, erase, or runtime operation was performed in this work.
