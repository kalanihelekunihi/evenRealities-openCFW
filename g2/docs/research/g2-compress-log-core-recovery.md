# G2 compact-log core recovery

## Result

The retained first-party translation unit
`platform\service\compress_log\core\compress_log.c` is closed as eight
functions in the contiguous executable interval
`[0x0043C7CC, 0x0043D0C8)`. The body is 2,300 bytes with SHA-256
`f106c8bfa77dc32dad8dc3a9fc1cceeff7eb36c872fb2b3525e12ceb963a9565`.
Seven entries were present in the authenticated Ghidra corpus; the force-sync
entry at `0x0043CF8C` was restored from raw Thumb control flow, literal
references, and its exact retained diagnostic symbol.

This closure corrects an important dependency attribution. The extremely
high-volume function at `0x0043CE9E` is **not** upstream EasyLogger
`elog_output`. It is G2-private compact-log glue, backed by a private record
encoder at `0x0043CB84`. The authenticated, upstream-derived EasyLogger
`elog_output` remains the separately audited function at `0x0043D574`.
Consequently, the private hook's 5,718 whole-image callers are not evidence
that its executable body came from the selected EasyLogger commit.

The object embeds no third-party function definition and provides no new
version discriminator. Its dependencies terminate at already identified IAR
DLIB, EasyLogger, FreeRTOS-Kernel/port, CMSIS-FreeRTOS, and first-party service
seams. No historical private G2 producing commit is observable in the binary.
OpenCFW now production-routes a clean-room C implementation of all eight
functions in both reviewed compiler profiles. Eight guarded stock-entry
redirects replace all 2,300 stock executable bytes while preserving the
external ABI and the existing whole-image compact-output ingress.

## Reproducible evidence

Run:

```sh
make compress-log-core-closure
```

The fail-closed analyzer authenticates the official G2 2.2.6.10 image, three
pinned manifests, all function bodies, M-profile Thumb control flow, direct
call topology, whole-image entry topology, retained strings, external literal
cells, upstream provenance records, the production C/header identities, all
eight strict relocated leaves, all eight guarded redirects, and the Apple and
Linux complete-firmware provider pins. The same target also executes the host
behavior harness and compiles the implementation as freestanding ARM C.

The ordinary decoder used by several earlier object audits is insufficient
here because the code contains M-profile system instructions such as `MRS`.
This analyzer enables Capstone's M-class mode. It also uses the decoded jump
group rather than a mnemonic-prefix heuristic, preventing the arithmetic
instruction `BICS` from being misclassified as a branch.

| Evidence | Result |
|---|---:|
| Linked functions | 8 |
| Ghidra-discovered / restored | 7 / 1 |
| Path-anchored Ghidra functions | 2 |
| Raw path references / referencing functions | 6 / 3 |
| Body bytes | 2,300 |
| Reachable instructions | 898 |
| Direct body calls | 78 |
| Internal / external direct body calls | 11 / 67 |
| Indirect body calls | 0 |
| Whole-image direct `BL` entry sites | 5,726 |
| Strict-interior direct `BL` entries | 0 |
| Stored entry pointers | 0 |

The reachable-instruction topology digest is
`c825c08437327d58cb711c5412109b4548c0e4731ef59364eae798ee6e87f880`.
The direct-body-call digest is
`1ba055d02427a000609eae520e852b5c622023f490eec9201e3f930dcba4e14f`.
The whole-image entry digest is
`4aa233cc3570726566c9925232cecbda6663f65e69bb487976ec267a0141a0ae`.

## Exact function inventory

| Entry | Bytes | Recovered role |
|---:|---:|---|
| `0x0043C7CC` | 46 | lazy static recursive-mutex initialization |
| `0x0043C7FA` | 216 | mutex-protected exact-count ring read |
| `0x0043C8D2` | 382 | `_log_get_all_buffer`, with thread/exception critical sections |
| `0x0043CA50` | 308 | ring write and persistence-pressure scheduling |
| `0x0043CB84` | 794 | private compact-record encoder |
| `0x0043CE9E` | 100 | whole-image compact-log output hook |
| `0x0043CF02` | 138 | `svc_compress_log_sync_to_files` |
| `0x0043CF8C` | 316 | `svc_compress_log_force_sync_to_files` |

The first function was already independently identified as the sole private
caller of `xQueueCreateMutexStatic` in the FreeRTOS queue-wrapper audit. It
creates mutex type `4` in the static buffer at `0x20072998`, stores the handle
through `0x20074388`, and asserts on failure.

## Physical-boundary qualification

The complete executable body is contiguous, but this closure deliberately
does not claim one complete physical interval. Twenty-three four-byte literal
cells used by the body occupy `[0x0043D0E0, 0x0043D13C)`, after three small
EasyLogger accessors at `[0x0043D0C8, 0x0043D0E0)`. Those interleaved cells are
individually authenticated as one 92-byte region with SHA-256
`e773a770bfbbb9f2f22dcb5d680d229ccc7027ce0996def759c7b21b1cbf68c1`,
but they are excluded from the first-party frontier's physical-byte total.
This avoids assigning EasyLogger code or linker-shared pool ownership to the
compact-log translation unit without stronger linker evidence.

## Private compact-record format

The encoder constructs a maximum 44-byte record:

- a 12-byte header, beginning with `0x7B` and ending with the high marker
  `0xDC` in its first word;
- at most 32 bytes of encoded arguments;
- a tick-derived millisecond field from `osKernelGetTickCount() % 1000`;
- a current epoch field from the already closed G2 time service; and
- caller-supplied packed level, argument-count, and format/string identity
  fields.

It parses flags, decimal widths, precision, and `l`/`ll` length modifiers from
the format string. Integer, pointer, character, and float-like arguments
consume four encoded bytes. `%s` consumes a fixed 16-byte slot and retains at
most the source string's last 16 bytes, zero-padding shorter strings. Encoding
stops when the format ends, the 32-byte argument area is full, or the packed
argument-count limit is reached. The resulting record is written through the
private ring writer.

This is observable G2 behavior, not an EasyLogger source admission. No public
source or retained third-party path identifies a generating repository or
commit for this compact format.

## Persistence behavior

`svc_compress_log_sync_to_files` uses a 10,000-tick gate. On each eligible
invocation it drains at most nine full 4,096-byte blocks through the
compress-log port. The force-sync function drains full blocks and then the
remaining partial record data, reporting block, remainder, and byte totals.
The port implementation is a distinct translation unit whose complete
production source route is independently authenticated by
`make compress-log-port-closure`; this core calls its source-owned entry at
`0x0044A798` through a strict relocation.

## Provider boundary

| Provider | Calls | Qualification |
|---|---:|---|
| IAR DLIB | 13 | `memcpy`, `memset`, and `strlen`; EWARM 9.20+ floor, 9.60.2 leading candidate |
| EasyLogger controls/output | 30 | two small accessors plus the G2-adapted upstream-derived `elog_output` at `0x0043D574` |
| FreeRTOS kernel and port | 14 | static recursive mutex, take/give, and thread/exception critical-section seams |
| CMSIS-FreeRTOS | 2 | exact `osKernelGetTickCount` wrapper |
| Other G2 providers | 8 | scheduling, OTA state, time, persistence port, and mode gates |

The relevant authenticated source selections remain:

- EasyLogger commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`;
- CMSIS-FreeRTOS commit `d213f261b5be6bb29a7cce8b84071706b72f4d53`;
- FreeRTOS-Kernel commit `def7d2df2b0506d3d249334974f51e427c17a41c`;
- CMSIS_5 commit `2b7495b8535bdcb306dac29b9ded4cfb679d7e5c`.

These commits explain the provider functions only. They do not identify the
private G2 compact-log hook or encoder's historical source commit.

## OpenCFW production implementation

`components/apollo_main/core_overlay/compress_log_core.c` recreates the
compact-record encoder, ring policy, mutex/critical-section handling, and
persistence cadence as first-party compatibility behavior. The route keeps
the existing entry ABI at `0x0043CE9E`, so the 5,726 authenticated direct
callers continue to use one guarded replacement. It does not transplant
upstream `elog_output` at that address. The eight production leaves total
2,498 bytes in each reviewed profile and carry 66 authenticated strict
relocations to source-owned or explicitly retained policy providers.

Runtime equivalence, flash wear, concurrent producer stress, and power-loss
recovery remain **blocked by unavailable physical evidence**. This audit used
no device, signing, flashing, erase, or runtime operation.
