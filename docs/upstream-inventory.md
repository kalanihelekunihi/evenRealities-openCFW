# Upstream library recovery inventory

openCFW classifies each opaque firmware cluster before attempting clean-room
source re-creation. An exact upstream match is vendored or ported under its
original license; focused disassembly recovers only G2 configuration, ABI,
port hooks, and proprietary glue. A family-level match is not assigned a
specific revision until discriminating binary evidence supports it.

## Strongly identified source candidates

| Library | Recovered identity | Current action |
|---|---|---|
| FreeRTOS Kernel | V10.5.1, commit `def7d2df2b0506d3d249334974f51e427c17a41c` | Reviewed queue/list/task/port boundaries are source-integrated; the selected bounded `heap_4` adapter owns initialization, insertion/coalescing, allocation, and free, `vQueueDelete` closes over source heap free, both tick-count getters bind to a source-owned provider for the recovered `xTickCount` seam, `vTaskMissedYield` binds the recovered `xYieldPending` word, and `xTaskCheckForTimeOut` now closes over source-owned timeout/critical providers; fixed scheduler/hook and remaining queue/task seams stay explicit |
| CMSIS-FreeRTOS | v10.5.1, commit `d213f261b5be6bb29a7cce8b84071706b72f4d53`, with CMSIS_5 5.9.0 at `2b7495b8535bdcb306dac29b9ded4cfb679d7e5c` | `osMessageQueueNew`, `osMutexNew`, and `osSemaphoreNew` are production-integrated from bounded Apache-2.0 source adapters with authenticated G2 ABI/configuration and direct source-owned dependencies |
| TLSF | v3.1 source-equivalent range ending at `deff9ab509341f264addbd3c8ada533678591905` | Already vendored and source-integrated |
| littlefs | v2.10.1 source-equivalent release, commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318` | Core is authenticated and vendored; both images source-integrate the scalar/alignment quartet, exact `LFS_NO_INTRINSICS` fallback-bitops trio, endian-conversion quartet, and sixteen private dual-image leaves including `lfs_alloc_lookahead`, `lfs_tag_chunk`, `lfs_tag_isvalid`, `lfs_tag_type1`, `lfs_tag_type3`, `lfs_tag_id`, and `lfs_tag_size`, while Apollo main also owns `lfs_file_tell_`, `lfs_file_rewind_`, `lfs_file_size_`, and the relocation-free `lfs_tag_type2` scalar helper. The current `lfs_tag_size` promotion passes five focused tests and has closed cross-profile and aggregate build pins; the bounded read-only G2 block port remains gated on an external-flash capture |
| LVGL | G2 uses an LVGL 9.3.0-development vendor fork compatible with official history from `60d976c466e8…` through `344c7c318047…`; released v9.3.0 `c033a98…` is too new | A production-excluded snapshot selects compatibility ceiling `344c7c…` and verifies 65 G2-mapped upstream translation units, 252 compiler-resolved/reference headers, MIT license, signed commit, 107 tree objects, and all blobs offline. Proven config/ABI is explicit, but `lv_global_t` still differs (G2 `0x1EC`, minimal reference `0x1F8`), so production remains fail-closed. Exact vendor commit is unresolved; 11 Ambiq draw files, display, FreeType system/assets, display/input managers, and Even patches stay separate. See the [snapshot README](../third_party/lvgl/README.openCFW.md) and [version/configuration audit](research/lvgl-version-recovery-audit.md) |
| FreeType | **2.9.1**, official annotated tag object `ad55868d889b6ba8d2aed846b4b4b460f8a83e42`, peeled commit `86bc8a95056c97a810986434a3f268cbe67f2902` | The unchanged FTL and 297 byte-exact source files are authenticated offline; a recovered header pins the ten-module G2 order, and focused audits prove v40/minimal TrueType, substantive GX variation services, the `am_ftsystem.c` allocator and constructor seams, plus exact `FT_Done_Face` at `[0x00526814,0x0052687E)` and its caller closure. Remaining unknowns are other configuration toggles, exact IAR compiler/linker details, the exact `FT_Done_FreeType` entry/closure, and external font asset identities, payloads, and runtime arrays. The snapshot remains production-excluded pending explicit source-configuration and promotion review. See the [snapshot audit](research/freetype-2.9.1-snapshot-audit.md) and [binary recovery audit](research/freetype-recovery-audit.md) |
| FlashDB | 2.1.1 (armink), lightweight tag/commit `2.1.1` / `714d6159e7e6afb267a3953756abca445c350e61` | The selected 14-file Apache-2.0 KVDB/FAL snapshot is byte-exact to the official tag and verified offline; this is an openCFW compatibility selection, not proof that Even used the checkout unchanged. The analyzer authenticates the 1-bit write granularity, 4-KiB sectors, 64-entry caches, short-enum `0x8AC` object ABI, partitions, callbacks, and `sysenv@kvdb` / `factory@NVdb` bindings. A production-excluded port now differentially matches upstream partition reads, preserves the shared CMSIS mutex, maps every nonzero MX25 result to `-1`, and makes write/erase unreachable six-byte failure leaves. Production admission still waits for a golden capture, non-destructive mount policy, schema semantics, and the unresolved runtime `kvbooCount` default. See the [snapshot README](../third_party/flashdb/README.openCFW.md), [configuration audit](research/flashdb-configuration-recovery-audit.md), and [read-only port audit](research/flashdb-readonly-port-source-candidate-audit.md) |
| EasyLogger | `2.2.99` source-equivalent core from `cd93d9c768415f4b7279f2d3ef2366ce15ea087c` through vendored `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`; no upstream tag | Ten main control/filter/lock entries plus the shared four-helper quartet in both Apollo images are source-integrated; image-specific source seams preserve each logger/assert policy, while the full output functions and downstream transports remain explicit binary boundaries |
| mpaland/printf | Existing commit pin in the formatter evidence | Continue using the pinned upstream core plus reviewed G2 format extensions |
| AmbiqSuite | 5.1.0 reusable Apollo510 source at commit `5efc0228528a8adce5eae0d226fac85d2551eb3b`, with CMSIS Core pinned at `d23a6949a0331ca96853bcd98b0fdcc4db47184c` | The licensed Apollo510/CMSIS closure is vendored; both production overlays compile the complete translation unit, retain only exact-upstream `am_hal_mspi_interrupt_clear`, and install authenticated main/boot redirects |
| CmBacktrace | armink CmBacktrace, compatible with unmodified upstream interval `4abadfa0…73714489` on the untagged post-1.4.1 line advertising `1.4.2`; no exact vendor commit is proven | FreeRTOS, stack dumping, IAR `.out`, depths 32/16, name limit 40, M33-class effective behavior, exact init arguments, and the 39-entry message table are recovered. Upstream `55e7b69` and later are excluded because G2 lacks its stacked-xPSR fix. A production-excluded seven-file **MIT** snapshot selects `73714489` as an explicit openCFW compatibility choice and verifies its commit, six tree objects, and blobs offline; see the [snapshot README](../third_party/cmbacktrace/README.openCFW.md) and [version/configuration audit](research/cmbacktrace-version-recovery-audit.md) |

Every third-party family embedded in the G2 `2.2.6.10` build tree is now
identified: FreeRTOS-Kernel, FreeRTOS-Plus-CLI, littlefs, TLSF, EasyLogger,
TinyFrame, Cordio/Packetcraft, LVGL v9.3 (with its bundled FreeType 2.9.1,
an LZ4-family decompressor, and `bin_decoder`/`bmp`/`fsdrv`), FlashDB 2.1.1,
nanopb (compatible with pristine upstream 0.4.7–0.4.9),
mpaland/printf, AmbiqSuite 5.1.0 / CMSIS, the generic `ringBuffer`, and
CmBacktrace. The remaining opaque bytes are first-party Even code
(`platform`/`app`/`framework`/`driver`/`product`/`service`, including the
proprietary `fw_event_loop`, audio DSP, cryptographic backend, and application
services).

Every vendored import must pin its revision or defensible source-equivalent
range, preserve its license and notices, record unmodified-file hashes, and
keep G2-specific changes in a separate port or patch layer.

## FreeRTOS-Kernel V10.5.1 authenticated release

`third_party/freertos-kernel` preserves 49 official upstream files from
annotated tag object `d7b40dbed508c305c2a32ccf3982045ec9ba8734`, peeled
commit `def7d2df2b0506d3d249334974f51e427c17a41c`, and tree
`7496dfa815c3cea2f45a090c6e92d113f494b930`. The tag is not
cryptographically signed. Authentication therefore pins the official
repository/ref identities and every selected file by byte count, Git blob
SHA-1, and SHA-256.

The snapshot includes all seven kernel implementation units, all 19 released
headers, the common MPU wrapper, and both complete released IAR Cortex-M55
port alternatives: `ARM_CM55` and `ARM_CM55_NTZ`. It also preserves exact
`portable/MemMang/heap_4.c`, 20,608 CRLF bytes with SHA-256
`d48a51e34caed771e6650d95f6c2527e52fde2a6ebc6f83b49d003aef0135e05`
and Git blob `3af0caf2b60fc4adfb103a115fefbf1b09b21dd8`, as the authenticated MIT
algorithm reference for the selected bounded G2 adapter. The pristine snapshot
does not itself supply G2 selection or placement. The port alternatives
must not be linked together. Focused instruction comparison unequivocally selects
`portable/IAR/ARM_CM55_NTZ/non_secure` with TrustZone and MPU disabled and
FPU context support enabled. The recovered port uses `BASEPRI=0x30`, Apollo
STIMER compare A on IRQ 32, a 1,024-Hz tick derived from 32.768 kHz / 32, and
tickless idle. The kernel has 56 priorities, 32-byte task names, static and
dynamic allocation, timers, mutexes, notifications, trace fields, and a
`heap_4`-shaped `0x2F000`-byte heap at `0x20004558`.

This is not permission to link pristine `tasks.c`: the exact 112-byte G2 TCB
stores a vendor stack-depth word at `+0x54`, where unmodified V10.5.1 has no
equivalent field under the compatible configuration. A complete source port
therefore needs a small reviewed TCB/tasks patch, recovered
`FreeRTOSConfig.h`, Apollo STIMER tick/tickless glue, application hooks, and
the now-reviewed bounded selection/integration of authenticated V10.5.1
`heap_4`. MVE, the exact AmbiqSuite revision, and
unrelated `INCLUDE_*` switches remain unresolved. The complete configuration
and port proof is in `docs/research/freertos-g2-config-port-audit.md`, with a
read-only 21-span verifier in `tools/analyze_g2_freertos_port.py`.

The currently integrated queue subset uses the upstream V10.5.1 algorithms
with the recovered 80-byte `Queue_t` ABI. Five public queue operations, four
generic/private creation entries, three public
static-mutex/static-counting/dynamic-counting constructor wrappers, and the
private empty/full predicates are source-owned. The wrappers link
only to the source-owned generic creators and mutex initializer; their one
retained assertion branch enters source-generated
`ulSetInterruptMask` at the unchanged Thumb address `0x005FA0A5`.
Exact upstream
`vListInitialise`, `vListInsertEnd`, `vListInsert`, and `uxListRemove` are
also source-owned at stock spans `[0x0045607C,0x0045609A)`,
`[0x0045609A,0x004560B2)`, `[0x004560B2,0x004560E8)`, and
`[0x004560E8,0x0045610E)`, using the recovered 32-bit `List`/`ListItem` ABI.
The four leaves compile to relocation-free 22-, 26-, 58-, and 34-byte Thumb
functions and pass their focused
upstream-oracle, ABI, topology, target-body, and manifest gates. Remaining
task, list, port, and queue-private calls are explicit reviewed stock seams.
`vListInitialiseItem` is deliberately not claimed because the official
binary inlines it and exposes no standalone stock body.

The paired `ulSetInterruptMask` and `vClearInterruptMask` portable-layer
leaves are exact FreeRTOS V10.5.1 Cortex-M55 assembly from
`IAR/ARM_CM55_NTZ/non_secure/portasm.s`, syntax-adapted for Clang without
changing the instruction sequence. Source copies remain in place at
`[0x005FA0A4,0x005FA0BA)` and `[0x005FA0BA,0x005FA0C8)`, preserving all
existing callers and save/set/restore latency. Their only recovered
configuration parameter is shifted `BASEPRI=0x30`; both leaves retain the
released DSB/ISB ordering and have no relocations, data, or private state.

The remaining five NTZ port leaves are now source-assembled in place from
the 5,487-byte `runtime_freertos_ntz_port.S` adapter, SHA-256
`38c6a259ca2fbfbefb373ef5a80216f2e5f1cad998173ca2b4c9cfde6c01aee8`.
The authenticated upstream `portasm.s` is 11,686 bytes, Git blob
`4d02a431e1d759f12f50e70fc55a7b0b4d368e89`, and SHA-256
`eaa83b3867edec5560c69f2a21facd7aff3c0f3bfcdfc5751722375ae328ee8f`.
The production spans are:

| Function | Stock span | Bytes | Stock SHA-256 |
|---|---|---:|---|
| `vRestoreContextOfFirstTask` | `[0x005FA058,0x005FA07E)` | 38 | `10edd4871b5f0c829e38618f1003ef0c45ec3629219317e23c62a2e255b0f4f8` |
| `vRaisePrivilege` | `[0x005FA07E,0x005FA08C)` | 14 | `29bceedf776515c291813e4eecd9a836378b81550c42d08aee35cf15df3bd8db` |
| `vStartFirstTask` | `[0x005FA08C,0x005FA0A4)` | 24 | `44ba0097fbbc1d0691837d5c51bee83e6b61509c9d89efffee9c202d930e6347` |
| `PendSV_Handler` | `[0x005FA0C8,0x005FA120)` | 88 | `d8e234bfa34805ad160e41ef54801973c9c871b36cf7ac0f365b56fe503253e3` |
| `SVC_Handler` | `[0x005FA120,0x005FA132)` | 18 | `d0fac197473b52d6ed466462d237ddb20dd8096a6507ea559e75d4bd9d88da94` |

Their exact ELF allowlist has four `R_ARM_THM_PC8` relocations to the
authenticated words at `0x005FA134` and `0x005FA138`, a
`R_ARM_THM_CALL` to `vTaskSwitchContext` at `0x004551B4`, and a
`R_ARM_THM_JUMP24` to `vPortSVCHandler_C` at `0x00442134`. The SVC and
PendSV vector values remain `0x005FA121` and `0x005FA0C9`.
`in_place_leaves` keeps the five names out of the appended overlay ABI and
ordinary patch-site graph, requires exact source/compiler/stock/output pins
and relocation order, authenticates the literal dependencies, and rejects
overlapping writes. The component therefore reports 182 source-owned
in-place bytes without changing the overlay or provider hash.

Five additional exact-upstream `tasks.c` leaves are source-integrated in
Apollo main:

| Function | Stock range | Recovered fixed-state seam |
|---|---|---|
| `xTaskGetTickCount` | `[0x00454EFE,0x00454F06)` | `xTickCount` at `0x20074A34` |
| `xTaskGetTickCountFromISR` | `[0x00454F06,0x00454F10)` | `xTickCount` at `0x20074A34` |
| `uxTaskGetNumberOfTasks` | `[0x00454F10,0x00454F16)` | `uxCurrentNumberOfTasks` at `0x20074A30` |
| `xTaskGetCurrentTaskHandle` | `[0x0045589C,0x004558A4)` | `pxCurrentTCB` at `0x20074A20` |
| `xTaskGetSchedulerState` | `[0x004558A4,0x004558C4)` | `xSchedulerRunning` at `0x20074A3C`; `uxSchedulerSuspended` at `0x20074A58` |

Each algorithm is independent of the vendor-extended TCB layout:
task-current returns the TCB pointer without dereferencing it, task-count
returns the authenticated population word, the tick getters read the
authenticated tick word through a shared source provider, and
scheduler-state implements the released three-state zero/nonzero policy.
Their focused writer/caller topology, target ABI, and integration contracts
are recorded in
`docs/research/freertos-task-current-source-boundary-audit.md`,
`docs/research/freertos-task-count-source-boundary-audit.md`, and
`docs/research/freertos-scheduler-state-source-boundary-audit.md`. These
incremental fixed-address globals remain an explicit seam until a complete
kernel link migrates the FreeRTOS RAM layout atomically.

## CMSIS-FreeRTOS v10.5.1 authenticated compile-input closure

`third_party/cmsis-freertos` now authenticates ten unmodified upstream files
from CMSIS-FreeRTOS tag `v10.5.1` and its package-declared CMSIS_5 tag
`5.9.0` dependency. The CMSIS-FreeRTOS unsigned annotated tag object is
`34e6e4c403c17de35ec0acf29610e374dc938604`, peeled commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`, tree
`d3689a816acc77a3f0b7d35439d666ad8434b6ba`. The CMSIS_5 unsigned annotated
tag object is `61e36449f53c25ef7825c40f7dd93685736f457f`, peeled commit
`2b7495b8535bdcb306dac29b9ded4cfb679d7e5c`, tree
`b88e747b2a2309b81ea77831481a58393465cd7b`.

The constructor root `cmsis_os2.c` is 70,106 bytes, Git blob
`88dca1d881f1a960872572a8a0efd94cde19dcea`, SHA-256
`8a0d60b56ad30c4f7957f64fa581158017b6812ec94b832d974c773ae4f2bc36`.
The closure pins its public/private wrapper headers, GNU-compatible CMSIS
compiler path, CMSIS RTOS2 headers, package descriptor, and license files.
`python3 third_party/cmsis-freertos/verify_snapshot.py` checks every path,
byte count, Git blob, SHA-256, direct include, selected compiler branch, and
license notice without compiling, linking, or touching hardware.

Candidate-only shims at
`components/apollo_main/core_overlay/candidates/cmsis_freertos_constructors/`
provide `{FreeRTOSConfig.h,portmacro.h,cmsis_freertos_target.h,string.h}`.
With them, the authenticated, unmodified `cmsis_os2.c` compiles for
Cortex-M55 with `-Oz -Werror`. Garbage collection retains 370 text bytes:
`IRQ_Context` 46, `osMessageQueueNew` 88, `osMutexNew` 98, and
`osSemaphoreNew` 138. It retains zero read-only or writable data and four
8-byte EHABI `.ARM.exidx` sections. The isolated candidate gate passes 6/6
tests in 0.231 seconds.

That broad closure remains candidate-only for unrelated CMSIS services. The
bounded `osMessageQueueNew` algorithm is
production-integrated from
`runtime_cmsis_message_queue_new.c`, 8,427 bytes with SHA-256
`8897019aa7a2beca32a88dc60808fb1f99b1538933b8ab4fbd9ed4fed38d433c`.
Its 124-byte target closes directly over three source-owned FreeRTOS
dependencies. The separately bounded `osMutexNew` algorithm is also
production-integrated from `runtime_cmsis_mutex_new.c`, 9,798 bytes with
SHA-256
`28081734a384c089635681014ed028414b75d375c22f0a52a64f53e22842cf2d`;
its 116-byte target closes directly over the source-owned scheduler-state
getter and static/dynamic mutex creators. The separately bounded
`osSemaphoreNew` production adapter is 11,566 bytes with SHA-256
`a947868d3fbcfc7f41d021210355e0ff777d49d3db84fa0da71a255d319c1527`;
its 178-byte target closes over source-owned scheduler, queue creation/send,
counting-semaphore, and `vQueueDelete` dependencies. The unresolved device-header,
`SystemCoreClock`, MVE, broad
`INCLUDE_*`, assert/NVIC/libc, and candidate `StaticTask_t` questions remain
outside the admitted leaf. This source boundary does not claim Even
Realities' historical checkout. The wrapper and CMSIS source retain
Apache-2.0 terms; separately supplied FreeRTOS remains MIT.

## littlefs v2.10.1 source-equivalent release

Apollo main contains an 84-byte non-threadsafe `struct lfs_config` at
`0x006E83A4`, with SHA-256
`f38bd899e180d29ee60609a2452d25c2d2d6c6fef4eb455064e23a6ca7c6e813`.
Its exact configuration is:

| Field | Value |
|---|---:|
| Read callback | `0x004763B9` |
| Program callback | `0x004763F1` |
| Erase callback | `0x00476429` |
| Sync callback | `0x004764DD` |
| Read size | 16 bytes |
| Program size | 256 bytes |
| Block size | 4,096 bytes |
| Block count | 3,008 |
| Block cycles | 500 |
| Cache size | 4,096 bytes |
| Lookahead size | 256 bytes |
| Compact threshold | 0 |
| Static buffers and limit overrides | Null/zero |
| Thread-safe hooks | Disabled |

The bootloader contains the same 84-byte layout and identical geometry at
`0x00431070`, SHA-256
`724c351d2136e3c2f10b59ad84d547da4632739ea1f20eb839e9af2cfbd5b6e8`.
Only its callbacks differ:

```text
read  0x004212D9
prog  0x00421311
erase 0x00421349
sync  0x004213D5
```

The complete assertion-line fingerprint uniquely matches official release
`v2.10.1`: all 38 upstream `v2.*` tags were checked, and the adjacent
`v2.10.0`, `v2.10.2`, and `v2.11.0` releases disagree on the recovered
compact-threshold, block-count, global-state, demove, and directory-open
lines. Assertions and debug/warn/error diagnostics are enabled, trace,
`LFS_THREADSAFE`, and `LFS_MULTIVERSION` are disabled, and dynamic allocation
is enabled.

The released tag commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318` is an exact source-equivalent
pin, not a claim about Even's historical checkout. Three upstream source
states within this generation compile byte-identically under the recovered
configuration, so the stripped binary cannot distinguish their repository
provenance. The complete audit is in
`docs/research/littlefs-version-audit.md`.

The Apollo-main public boundary comprises `lfs_format`, mount/unmount,
remove/rename/stat, file open/close/sync/read/write/seek/truncate/rewind/size,
mkdir, and directory open/close/read/rewind at
`0x004CFA58...0x004CFD0C`. The bootloader uses the subset from `lfs_format`
through directory close at `0x00415128...0x0041531C`.

This supports one vendored v2.10.1 core with main-firmware and bootloader port
tables. Before redirecting any API, capture a complete external-flash image,
mount a copy read-only, validate the superblock/disk version/tree/content
against stock behavior, and exercise mutating and power-loss cases only on
disposable copies. Device format and erase remain prohibited until that gate
passes.

Focused port disassembly recovers the standard littlefs callback ABI and the
exact address mapping:

```text
external address = 0x01400000 + block * 0x1000 + offset
partition         = 0x01400000...0x01FC0000
driver success    = 0
driver failure    = -5 (LFS_ERR_IO)
```

Apollo main calls the retained MSPI driver at `0x00471021` for reads,
`0x004708A9` for programs, and `0x0047075D` for erases. The bootloader uses
`0x00420F71`, `0x00420B0D`, and `0x00420A09`, respectively. The callbacks
ignore their `cfg` argument; `sync` is a no-op. The stock ports have
insufficient defensive bounds checking, allow partial program behavior, and
do not consistently propagate mutex, mode-transition, or busy-timeout
failures. A source port must therefore validate the full block/offset/size
range itself rather than reproduce those hazards.

A read-only source port is feasible with littlefs v2.10.1,
`LFS_READONLY`, explicit partition bounds, and stock auto-format/boot-count
paths bypassed. Full read/write ownership still requires the G2 board MSPI
initialization, timing, XIP, and power policy plus a golden external-flash
capture. The reproducible audit and analyzer are
`docs/research/littlefs-g2-block-port-audit.md` and
`tools/analyze_g2_littlefs_ports.py`.

The transport audit further identifies AmbiqSuite 5.1.0 MSPI HAL as reusable
upstream code while keeping G2 board policy in a separate adapter: Apollo510B
MSPI1/CE0, SPI mode 0, 96 MHz, IRQ 21 priority 4, interrupt mask `0x1A80`,
the recovered GPIO set, calibration sweep, mutex/timeouts, retained
sleep/wake policy, and main-only read-only 32 MiB XIP at `0x80000000`.
`tools/analyze_g2_littlefs_mspi_transport.py` validates those parameters and
the report is `docs/research/littlefs-g2-mspi-transport-audit.md`.

Twenty-one dual-image littlefs boundaries are source-integrated directly
from authenticated v2.10.1-equivalent source. Apollo main additionally owns
the main-only `lfs_file_tell_` leaf at `[0x004CE45C,0x004CE460)` and
`lfs_file_rewind_` at `[0x004CE460,0x004CE472)` and `lfs_file_size_` at
`[0x004CE472,0x004CE48A)`, for 24 littlefs boundaries in that image. Both
images own the following scalar and alignment quartet,
fallback-bitops trio, endian-conversion quartet, and ten private boundaries:

| Function | Apollo-main stock range | Bootloader stock range |
|---|---|---|
| `lfs_max` | `[0x004CA6F8,0x004CA700)` | `[0x00410400,0x00410408)` |
| `lfs_min` | `[0x004CA700,0x004CA708)` | `[0x00410408,0x00410410)` |
| `lfs_aligndown` | `[0x004CA708,0x004CA714)` | `[0x00410410,0x0041041C)` |
| `lfs_alignup` | `[0x004CA714,0x004CA720)` | `[0x0041041C,0x00410428)` |
| `lfs_npw2` | `[0x004CA720,0x004CA77A)` | `[0x00410428,0x00410482)` |
| `lfs_ctz` | `[0x004CA77A,0x004CA78A)` | `[0x00410482,0x00410492)` |
| `lfs_popc` | `[0x004CA78A,0x004CA7B2)` | `[0x00410492,0x004104BA)` |
| `lfs_scmp` | `[0x004CA7B2,0x004CA7B6)` | `[0x004104BA,0x004104BE)` |
| `lfs_fromle32` | `[0x004CA7B6,0x004CA7D8)` | `[0x004104BE,0x004104E0)` |
| `lfs_tole32` | `[0x004CA7D8,0x004CA7E0)` | `[0x004104E0,0x004104E8)` |
| `lfs_frombe32` | `[0x004CA7E0,0x004CA802)` | `[0x004104E8,0x0041050A)` |
| `lfs_tobe32` | `[0x004CA802,0x004CA80A)` | `[0x0041050A,0x00410512)` |
| `lfs_mlist_isopen` | `[0x004CB082,0x004CB0A0)` | `[0x00410D8A,0x00410DA8)` |
| `lfs_mlist_remove` | `[0x004CB0A0,0x004CB0BC)` | `[0x00410DA8,0x00410DC4)` |
| `lfs_mlist_append` | `[0x004CB0BC,0x004CB0C4)` | `[0x00410DC4,0x00410DCC)` |
| `lfs_fs_disk_version` | `[0x004CB0C4,0x004CB0CA)` | `[0x00410DCC,0x00410DD2)` |
| `lfs_fs_disk_version_major` | `[0x004CB0CA,0x004CB0D6)` | `[0x00410DD2,0x00410DDE)` |
| `lfs_fs_disk_version_minor` | `[0x004CB0D6,0x004CB0E0)` | `[0x00410DDE,0x00410DE8)` |
| `lfs_alloc_ckpoint` | `[0x004CB0E0,0x004CB0E6)` | `[0x00410DE8,0x00410DEE)` |
| `lfs_alloc_drop` | `[0x004CB0E6,0x004CB0F6)` | `[0x00410DEE,0x00410DFE)` |
| `lfs_alloc_lookahead` | `[0x004CB0F6,0x004CB12E)` | `[0x00410DFE,0x00410E36)` |

The utility quartet is compiled from one shared source file with SHA-256
`2730d0f39e02d7b6e07396894b796b26d9f73332deff23a685b5a06da0f7fb22`.
The pure `max`, `min`, and `aligndown` leaves are call-free; the sole
`alignup` relocation closes over source-owned `aligndown`. Four authenticated
stock entries in each image become eight total non-linking Thumb `B.W`
redirects. Exact spans, stock hashes, caller topology, and current placements
are recorded in
`docs/research/littlefs-next-closed-leaves-audit.md`.

The shared fallback-bitops source is 2,795 bytes with SHA-256
`405092c6e8fc65a740f951cb2affaad8766e2553c7b8d290ff58f435e8830f47`.
It compiles the exact v2.10.1 `LFS_NO_INTRINSICS` implementations of
`lfs_npw2`, `lfs_ctz`, and `lfs_popc`, preserving `npw2(0) == 32`,
`npw2(1) == 1`, and `ctz(0) == 0`. The only new relocation is the internal
Thumb call `lfs_ctz -> lfs_npw2`; there are no external, undefined, literal,
or data dependencies.

The shared endian-conversion source has SHA-256
`830d49b043181d270ac0aedda432c5e232ce8d6ce65e8e537b80b1a706fd6cac`.
Apollo510 and both reviewed compiler profiles are little-endian, so
`lfs_fromle32` and `lfs_tole32` compile to two-byte identity leaves while
`lfs_frombe32` and `lfs_tobe32` compile to four-byte byte-swap leaves.
Optimization closes the upstream helper relationships without a relocation;
all eight target bodies have no literal, data, or undefined-symbol
dependency. Complete-image scans pin 26, 19, 4, and 2 direct callers per
image and find no stored entry, non-linking incoming edge, or external
interior entry.

The shared `lfs_mlist_isopen` integration source has SHA-256
`7d0bc398c8ecd85fd00b34cc6dcc2b9fc75c754e1aed0bfbca01dd58ae9d6e0c`.
Focused disassembly supplies only the 32-bit pointer and unsigned 0/1 return
ABI plus the `struct lfs_mlist.next` offset-zero prefix. The 44-byte main and
18-byte bootloader bodies have no relocation, literal, undefined symbol,
stored entry, or interior entry.

The list helpers pin the recovered `lfs_t.mlist`/node-prefix ABI,
`lfs_fs_disk_version` closes its stock distant literal with a source-local
`0x00020001` constant, and `lfs_alloc_drop` closes its checkpoint operation
in source. The original seven main and boot private-leaf redirects
authenticate their complete stock bodies and whole-image entry/interior
topology; those emitted functions have no undefined symbol or `.text`
relocation.

The current disk-version-parts source is 1,734 bytes with SHA-256
`920d03e80c9d16a1d0b4299f8151eefe4d9f3ac1ba89c2d40bcc5830335eb5a7`.
It ports exact `lfs_fs_disk_version_major` and
`lfs_fs_disk_version_minor` from the authenticated v2.10.1 `lfs.c` at
commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`. Each profile emits two
ten-byte leaves whose sole reviewed `R_ARM_THM_CALL` relocation closes over
the existing source-owned disk-version provider. Apollo main places them at
`[0x007B01B8,0x007B01C2)` and `[0x007B01C4,0x007B01CE)`, separated by two
generated alignment bytes. The bootloader places them contiguously at
`[0x00434592,0x0043459C)` and `[0x0043459C,0x004345A6)`.

The current allocator-lookahead source is 5,445 bytes with SHA-256
`44ab9037747a4cb209404423d52cf817b035cbab5177a8c0cb05090df4b68491`.
It reuses the exact v2.10.1 `lfs_alloc_lookahead` algorithm; focused
disassembly recovers only `lfs_t.lookahead.start` at `0x54`,
`lookahead.size` at `0x58`, `lookahead.buffer` at `0x64`, and
`block_count` at `0x6C`. The identical 56-byte stock spans have SHA-256
`58285c138461a673be0bed2c5376f8d739e40e2aea753ad05d5061bfbc9265cf`.
Apollo main redirects `0x004CB0F6` to a 50-byte source leaf at
`0x007B01D0`; the bootloader redirects `0x00410DFE` to a 48-byte source
leaf at `0x004345A6`. Both target bodies are relocation-free and pass
20,000 deterministic upstream-oracle cases.

The two main-only file accessors preserve the recovered 32-bit
`lfs_file_t` ABI. `lfs_file_tell_` returns `pos +0x34`; the current
`lfs_file_size_` leaf reads `ctz.size +0x2C`, `flags +0x30`, and `pos +0x34`,
preserves `LFS_F_WRITING = 0x00020000`, and computes the writing-state maximum
through the already source-owned `open_cfw_littlefs_util_max`. The 20-byte
file-size leaf is placed at `0x007B28D4` on Apple and `0x007B2FF0` on Linux.
Its only relocation is therefore within the authenticated littlefs source
closure; it adds no stock helper, block-device callback, filesystem format, or
erase path.

The separate raw bootloader source-overlay component appends the current
source-generated bodies below `0x00438000` and redirects the authenticated
boot spans listed above. Its builder checks every complete original body
before patching and leaves EVENOTA CRC generation to the package assembler.
Focused evidence is recorded in
`docs/research/littlefs-file-tell-source-boundary-audit.md`,
`docs/research/littlefs-file-size-source-audit.md`,
`docs/research/littlefs-scmp-source-boundary-audit.md`,
`docs/research/littlefs-alloc-ckpoint-source-boundary-audit.md`,
`docs/research/littlefs-alloc-drop-source-boundary-audit.md`,
`docs/research/littlefs-mlist-remove-source-boundary-audit.md`,
`docs/research/littlefs-mlist-append-source-boundary-audit.md`,
`docs/research/littlefs-disk-version-source-boundary-audit.md`, and
`docs/research/littlefs-next-closed-leaves-audit.md`, plus
`components/bootloader/core_overlay/EVIDENCE.md`.

### Historical fallback-bitops and FreeRTOS NTZ milestones

The historical fallback-bitops production release placed the main bodies at
`0x007AEF74`, `0x007AEFBC`, and `0x007AEFCC` and the bootloader bodies at
`0x004344D2`, `0x0043450A`, and `0x0043451A`. Its 114,324-byte main overlay,
282-byte boot overlay, 3,637,720-byte main provider, and 148,882-byte boot
provider are authenticated in the component evidence. The 4,415,834-byte
package has SHA-256
`058782604ab6cb946aff0acedbbef7d367bb1d82114f28c9a70276bcdf178e9a`;
`./make.sh source`, `./make.sh verify`, all three offline inspection lanes,
and three byte-identical output-isolated reproducibility lanes passed. The
focused production gate passed 6/6 tests in 13.693 seconds, and the inherited
focused gate passed 55/55 tests in 39.997 seconds: 61 tests in 53.690
seconds summed. The canonical repository run passed all 1,806 tests in
1,139.177 seconds; inside it, all 248 Apollo-main aggregate methods passed.

The subsequent, now-superseded FreeRTOS NTZ release source-owned another 182
Apollo-main bytes in place without changing that release's main/boot overlay,
provider, or package hashes.
The main overlay/provider retained
`00318de9ff51e19f77d889fa691a3a2a54e035b1287843bda857f944af58e065`
and
`f0da043e234dc38481059459755e091622d689313cd12e5c8d5155c7b4ba3202`;
the boot overlay/provider retained
`b934dbea7624660c3c774eb0f4edd5e73a738fc59023fc69cfac96417dfe2fee`
and
`1aa7920a16ed2857a2743394c0f62395a2f2477f95c965da47d1e29c4d2d8247`.
The component report records 182 in-place source bytes, 114,506 total
source-owned bytes, and 3,443,066 opaque base bytes. The manifest contained
750 placed, two unresolved, and five container-only regions; flash-plan
SHA-256 is
`eda45c2cc276bd70bc123267d9fbdc09b0ae4aa030a7557f874c259ca7f5fee8`.
Package ownership was 114,820 source bytes (2.600188%), 81,477 generated
bytes (1.845110%), 4,219,537 opaque bytes (95.554702%), and 196,297
controlled bytes (4.445298%). The focused production gate passed 23/23 in
18.333 seconds and the linker plus inherited gate passed 21/21 in 0.705
seconds. Standard source and manifest verification passed. Three lanes under
`build/repro-freertos-ntz-output-{a,b,c}` reproduced both overlays, both
providers, the package, and the flash plan byte-for-byte; their temporary
manifests were moved to Trash. All 248 Apollo-main tests passed in 582.904
seconds. `./make.sh test` passed all 1,838 tests in 1,038.709 seconds,
including all six CMSIS constructor compile-closure tests.

### Prior disk-version-parts production

That disk-version-parts release advanced the main overlay to 114,346
bytes with SHA-256
`bdc1e353d1adcb0075231afb6c423616dcc0da8335b4b430afe51763a0b9df20`
and the 3,637,742-byte main provider to
`d69c4834f65b0661834f990da8167ca6989a1b1c97fda838edc488a4ed0b3e8e`.
Its installed bytes end at `0x007B01CE`, leaving 261,682 bytes below
`0x007F0000` and 319,026 bytes below `0x007FE000`.
The boot overlay is 302 bytes with SHA-256
`e94e33658aca89d3830182bc6c17c656256a194262835c041fecc93e1d72dc59`;
the 148,902-byte boot provider has SHA-256
`abc583d976a01e237ffa4ed29e4be1b6ff0e5ae2d9756bccec58d1779fe20239`,
ends at `0x004345A6`, and leaves 14,938 bytes before Apollo main.
The 4,415,876-byte package has SHA-256
`60cd913a716266b349ce18295064f2484749a7dbad2ab9244c923c927bd56c2f`.
Its 546,404-byte flash plan has SHA-256
`52124c17205ae10e47f0b02d0cd6bae7c2b30e10d65d787aa34201a53fe0dc68`
and records 757 placed, two unresolved, and five container-only regions.
Package ownership is 114,860 source bytes (2.601069%), 81,523 generated
bytes (1.846134%), 4,219,493 opaque bytes (95.552796%), and 196,383
controlled bytes (4.447204%).

### Prior allocator-lookahead production

That allocator-lookahead release advanced the main overlay to 114,398
bytes with SHA-256
`2189ec69f7076e216c2ba7388f4eb9d19647feb9f89c382864012902be4e0fdf`
and the 3,637,794-byte main provider to
`557fe93fdf79c5cb332c7db731db29ed7cfc42be3daa49fb0d022f81e7fe0ba8`.
Its installed bytes end at `0x007B0202`, leaving 261,630 bytes below
`0x007F0000` and 318,974 bytes below `0x007FE000`.
The boot overlay is 350 bytes with SHA-256
`1b8bb2893a33a18b8481b785a57d49c2849396cc05c5ef20d86f8cf5cef255a5`;
the 148,950-byte boot provider has SHA-256
`9af8b65041bbd576b49b4f88e2f7427daf7bb445981d608799d86e1987468736`,
ends at `0x004345D6`, and leaves 14,890 bytes before Apollo main.
The 4,415,976-byte package has SHA-256
`3d4b2f3e22a10d0755642c0544786c9a881b2ab7c2271d8a184a83f5d3d7d13f`.
Its 550,026-byte flash plan has SHA-256
`73978705e32bbb968a9741620a80e1a70f866b5e43db60f4a9f08b4404ce34d1`
and records 762 placed, two unresolved, and five container-only regions.
Package ownership is 114,958 source bytes (2.603230%), 81,637 generated
bytes (1.848674%), 4,219,381 opaque bytes (95.548096%), and 196,595
controlled bytes (4.451904%).

### Prior CMSIS `osMessageQueueNew` production

That release advanced the main overlay to 114,524 bytes with SHA-256
`de76f5db2f04f48c81ea480c348a3c9151d4441c522eba68621ad812290153e2`
and the 3,637,920-byte main provider to
`874bdc621a6cd91848dee66038c3ba97d7e4b7c7ab1fb5063739bf69fc3047e1`.
Its installed bytes end at `0x007B0280`; the boot artifacts remain unchanged.
The 4,416,102-byte package has SHA-256
`c7baf50cd5386a5e27b4c284cc0084e8cf5d0b83d74eb08b8d4a997bf66474f4`.
Its 552,937-byte flash plan has SHA-256
`79da631918503c668516e1af5d3844e3dab65c9e63d8add4834a43536ef69407`
and records 766 placed, two unresolved, and five container-only regions.
Package ownership is 115,082 source bytes (2.605963%), 81,779 generated
bytes (1.851837%), 4,219,241 opaque bytes (95.542200%), and 196,861
controlled bytes (4.457800%). The focused production gate passes 10/10
tests, offline.

## AmbiqSuite Apollo510 MSPI HAL reuse boundary

`am_hal_mspi_interrupt_clear` is unequivocally mapped to the authenticated
AmbiqSuite Apollo510 `am_hal_mspi.c` source at commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`, with source SHA-256
`5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f`.
Main
`[0x004C23DE,0x004C240E)` and boot
`[0x00426506,0x00426536)` contain the same complete 48-byte stock body:
handle validation, module extraction, `INTCLR` write, mandatory volatile
`INTSTAT` readback, and the upstream success/invalid-handle returns.

The authenticated, unmodified complete translation unit compiles for
Cortex-M55 with function/data sections. When only
`am_hal_mspi_interrupt_clear` is rooted and `--gc-sections` is applied, the
linked ARM ELF retains exactly the 48-byte leaf, no private
`g_MSPIState`, no other global code/data symbol, no unresolved symbol, and no
leaf text relocation. This proves that OpenCFW should reuse the complete
upstream translation unit with section GC instead of copying Ambiq's private
MSPI handle type into a local rewrite. The proof is reproducible with
`tools/prove_ambiq_mspi_interrupt_clear_gc.py`; stock identity and topology
are checked by `tools/analyze_g2_mspi_interrupt_clear.py` and documented in
`docs/research/ambiqsuite-mspi-interrupt-clear-source-boundary-audit.md`.

The dependency closure is now pinned, licensed, and self-contained in
`third_party/ambiqsuite-apollo510` and `third_party/cmsis-core`. The Ambiq
snapshot authenticates 71 upstream dependency files at tree
`02b79dbf428a8cded053c65c92cc58fa5fdb8e78`; the CMSIS snapshot
authenticates the seven reached Core headers plus its Apache-2.0 license at
tree `3474af187114165f3623732474e4e1bd4b3d01d8`. Their offline verifiers
pin every imported file by byte count, Git blob SHA-1, and SHA-256.

Both production overlays compile the complete authenticated
`am_hal_mspi.c` with the proven Cortex-M55 configuration, retain only
`am_hal_mspi_interrupt_clear`, and install hash-authenticated redirects at
the two stock bodies. The current boot image places the leaf at `0x00434544`;
Apollo main places it at `0x007B0128`. Each retained leaf is 48 bytes with SHA-256
`87505e035fa5fe7c0dfd7c4d85b66c6b8f3b57ced45dc7afd787db6c52b0fd7b`,
zero relocations, and no `g_MSPIState`.

Broader source-owned G2 callers must be rebuilt against the same named 5.1.0
headers. Opaque stock callers must not cross the separately proven raw
`am_hal_mspi_control` request-ordinal mismatch; that wider control boundary
remains intentionally opaque until its configuration is recovered.

## LVGL v9.3 configuration

The defensible upstream baseline is LVGL v9.3.0 with possible Ambiq or local
patches. High-confidence compiled configuration includes:

- FreeRTOS OS integration with recursive mutexes and dynamically created
  tasks;
- warning-level logging, null/allocation assertions, and a custom fatal hook;
- custom malloc/realloc/free hooks and 32-bit millisecond ticks;
- little-endian operation;
- a 576-by-288 display with DPI 130;
- native format 6 at 8 bpp, strongly identified as `LV_COLOR_FORMAT_L8`;
- custom output format 13 at 4 bpp, consistent with
  `LV_COLOR_FORMAT_A4`, using an exact `0x14400`-byte output allocation;
- FreeType, littlefs, BMP, LVGL binary decoder, flex, and grid enabled; and
- compressed fonts disabled.

Recovered ABI anchors are `sizeof(lv_global_t) == 0x1EC`,
`sizeof(lv_display_t) == 0x31C`, and `sizeof(lv_draw_buf_t) == 0x1C`.
Upstream tick, memory, FreeRTOS OSAL, misc/container, core, widget, layout,
font, and standard draw code can use the v9.3.0 baseline with ABI assertions.
Ambiq draw code, `lv_ambiq_display.c`, FreeType system glue, GPU/Nema hooks,
the L8-to-A4 pipeline, input transport, and display-manager code remain
separate G2/vendor layers.

## FlashDB 2.1.1 configuration

The application uses FlashDB's FAL-backed KVDB path, not file mode. Focused
call-site recovery pins two instances:

| Database | FAL partition |
|---|---|
| `sysenv` | `kvdb` |
| `factory` | `NVdb` |

KV and sector caches are enabled with 64 entries each. `FDB_WRITE_GRAN` is 1
bit, the KV header is 24 bytes, and `sec_size` is the `norflash` block size of
4 KiB because neither caller overrides it. `FDB_KV_AUTO_UPDATE`, file mode,
and FlashDB debug logging are off, and no live/retained TSDB subsystem is
present. The original `FDB_USING_TSDB` macro state is not statically proven;
the recovered minimal source configuration omits it. The two static `fdb_kvdb` objects
begin at `0x2005DFFC`, have stride `0x8AC`, and require the target's short-enum
ABI. The compiled FAL partitions are `kvdb` at `0x01FC0000` length `0x38000`
and `NVdb` at `0x01FF8000` length `0x8000`.

Keep FAL device/partition definitions, MRAM callbacks, mutex hooks, the two
database objects, default tables, magic/version migration, factory reset,
and service blob APIs in a separate G2 port/glue layer. The current
production-excluded read-only candidate accepts only the two authenticated
partition records, checks overflow-safe bounds, locks through the recovered
CMSIS mutex, converts every nonzero MX25 status to `-1`, and denies all
writes and erases. Before integration, retain those gates, close the
non-destructive mount policy and exact blob/delete/iterate API surface, and
validate the on-disk format against a non-mutating golden capture. The source closure is
the official `fdb.c`, `fdb_kvdb.c`, `fdb_utils.c`, public headers, and generic
FAL core/headers; omit TSDB source, file, RT-Thread, shell, demo, and
sample-port code. The offline snapshot verifier reconstructs seven Git tree
objects to prove commit-to-path-to-blob membership for every selected file.

## EasyLogger 2.2.99 configuration

Apollo main unequivocally identifies the EasyLogger `2.2.99` version label
and compiled paths for `elog.c`, `elog_utils.c`, and `elog_async_api.c`. The
bootloader identifies the same label but only `elog.c` and `elog_utils.c`;
its focused port audit proves a synchronous level-dropping channel-1 sink,
distinct absolute state, and a boot-specific assertion policy.

The primary upstream repository has no `2.2.99` tag or release; public tags
end at `2.2.0`. Commit
`a607e1715b83d42b2d431e4e415263b7044e0ecb` introduced the `2.2.99` version
string, which many later master revisions retain. The G2 core contains the
argument-aware directory/function/line helpers introduced by
`cd93d9c768415f4b7279f2d3ef2366ce15ea087c`. That commit and the only two
later official master commits, `34cc1717825c799979a1b4b3739be1e5668a7322`
and vendored
`a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`, have byte-identical
`elog.c`, `elog_utils.c`, `elog.h`, and `elog_cfg.h` blobs. The snapshot is
therefore source-equivalent; no executable discriminator can select one of
the three repository commits. The full audit is in
`docs/research/easylogger-version-audit.md`.

Official upstream uses `elog_async.c`; the retained `elog_async_api.c` path
does not exist in inspected upstream history and is classified as G2
downstream glue.

The recovered main configuration has a 1,024-byte output buffer at
`0x2006BD30`, text colors enabled, an application filter level of
`ELOG_LVL_INFO`, five 33-byte tag-level slots, and six 32-bit format masks.
Assert-level output uses mask `0xFF`; error through verbose use `0x87`.
The global logger object begins at `0x20070BE8`; the integrated ABI pins a
`0xF6` field extent and a `0xF8` padded object size.

The upstream core can be kept unmodified behind a small Apollo-main port:

| Port service | Stock entry | Recovered G2 behavior |
|---|---:|---|
| Initialize | `0x0044AA68` | Lazily create `elogMutex`; return zero |
| Formatted output | `0x0044AA80` | Enqueue with G2 async metadata, then set event bit 1 |
| Raw/hexdump output | `0x0044AA76` | Enqueue through the raw G2 path |
| Lock / unlock | `0x0044AA98` / `0x0044AAA0` | CMSIS mutex, 1,000-tick acquire timeout |
| Time string | `0x0044AAA8` | Format date, time, and final integer field in a static buffer |
| Process / thread | `0x0044AB14` / `0x0044AB1C` | Current FreeRTOS task name or `unknown` |

The mutex uses static CMSIS storage: control block `0x20072AD8`, size 80,
and handle global `0x20074578`. The asynchronous event-flags handle is
`0x20074570`. That queue/worker is G2 application policy, including its
255-byte record cap, and belongs in `g2_elog_async_glue.c` rather than the
vendored library.

The formatted-output wrapper at `[0x0044AA80,0x0044AA98)` is now a production
30-byte source leaf with explicit record-builder, event-handle, and event-set
seams; nine focused tests pin its exact call ordering and ignored return
values. The production 132-byte redirect now targets the corrected single-
owner record builder. It performs one recycle after the enqueue path exhausts
10,000 compare-and-swap retries and admits the retained enqueue seam only as
a consuming operation. The downstream transport is not attributed to
upstream EasyLogger.

The authenticated source-equivalent snapshot and license are vendored under
`third_party/easylogger`, with its bounded commit set and file hashes recorded
in `PROVENANCE.json`. The integrated Apollo-main control boundary redirects eight
control entries plus the private five-slot tag-level default initializer and
public tag-level getter while preserving the existing `0x20070BE8` logger
object, assertion hook, and port lock/unlock as explicit seams. The output
core is now production source together with its G2 async chain. Source-owned
31-byte clearing and 30-byte equality helpers
remove the stock `memset` and `strncmp` dependencies from the new filter
boundary. Pristine-upstream oracles cover state transitions, format masks,
bounded tag copying, filter defaults and first-match lookup, lock transitions,
assertion behavior, and port call ordering. The G2 asynchronous transport
remains stock.

The current dual-image helper increment additionally source-owns
`get_fmt_enabled`, its unsigned-argument and pointer-argument predicates, and
`elog_strcpy` in both Apollo images. Each image retires 320 stock bytes. The
shared 4,975-byte MIT source and 6,505-byte header hash to
`8f2850f789fba3b08bdc3e1fa8f3a4646aaef7e4b16862f3be53478071aa22b5`
and
`f3a7e9bce0f136a2ff4a76929c317aef7bbc7c29dfc60d58311d94e58f6e2393`.
The 7,068-byte image-seam source hashes to
`78dc5aa9a7eb4f072b3169ae1837855007f25e1adccec7deaefecc486c8f0823`.
It preserves the main `0x20070BE8`/`0x2007456C` and boot
`0x20026700`/`0x200270E4` logger/hook bindings and their distinct
diagnostic/wait policies. Official assertion strings and wait wrappers remain
binary seams. Both profiles use 32-bit `size_t`, six levels,
a 1,024-byte line buffer, and the corrected tag record layout `level +0`,
`tag +1`, `tag_use_flag +0x20`.

The output/async production tranche replaces 1,182 complete stock bytes.
Apple's 4,423,148-byte package hashes to
`2b1008c2fc533f1257ee58bd6d0c08b449d2e12bc57d918f101586ba1d3e3d29`;
exact-root Linux's 4,425,020-byte package hashes to
`12386dc6f165053c3a308b4ec64bf2df90becf2b793a2404830a598b62b7a33d`.
Both reproduced twice byte-identically, offline and without hardware access.

`elog_hexdump` and its G2 level-less raw path are now production source-owned
for the authenticated 2.2.6.10 image. Complete `B.W`/NOP replacements cover
`[0x0043DACC,0x0043DC88)`, `[0x00448CCC,0x00448D4E)`, and
`[0x0044AA76,0x0044AA80)`. Ten strict leaves close the upstream-derived main
body over bounded arithmetic formatter helpers and a clean-room single-owner
transport adapter. The two-argument raw wrapper routes only to the level-less
builder; it does not reuse the incompatible three-argument formatted submit
path, set event flags, write the reserved level byte, or recycle after the
consuming enqueue. The original candidate and host fixtures remain excluded.
Complete stock topology, Apple/Linux closure, and production pins are in
`docs/research/easylogger-hexdump-source-candidate-audit.md`.

## Identified families needing focused configuration recovery

| Family | Evidence gap to close |
|---|---|
| Packetcraft/Ambiq Cordio | Definitive Cordio/Packetcraft BLE host with Ambiq FreeRTOS/HCI ports. Two body discriminators require **r20.05-or-later** semantics; the bounded public source-oracle interval is r20.05–r20.05c because the audited blobs are identical throughout. A production-excluded r20.05c snapshot now authenticates five C sources, 35 transitive headers, Apache-2.0 license, commit, 21 tree objects, and all blobs offline, and compiles the five reference units. It is a function-level openCFW source choice, not the exact vendor tree: G2's Ambiq FreeRTOS WSF/local trace diverge, and Ambiq HCI plus Even `platform\ble`/MRAM glue remain excluded. See the [snapshot README](../third_party/cordio/README.openCFW.md) and [version audit](research/cordio-version-recovery-audit.md) |
| LZ4 | Resolved API/family and production source selection: the stock image is unequivocally decompress-only LZ4-compatible code with `read_variable_length` at `0x0054EE90`, `LZ4_decompress_generic` at `0x0054EF08`, `LZ4_decompress_safe` at `0x0054F338`, and canonical `inc32table`/`dec64table`. The evidence does **not** unequivocally separate the compatible v1.9.4/v1.10.0 stock point releases. openCFW independently selects authenticated upstream **LZ4 v1.10.0** commit `ebb370ca83af193212df4dcbadcc5d87bc0de2f0` as its maintained decompress-only production replacement; no compressor is linked. See the [promotion result](research/lz4-upstream-production-promotion-plan.md) and [stock reachability/provider audit](research/lz4-stock-reachability-memory-provider-audit.md). Remaining: replace the two stock EABI memory providers with source-owned shims and optionally compact the unreachable stock/legacy decoders |
| TinyFrame | Receive and send clusters now establish official MIT source-equivalence interval `44ecc068…a29167a6`; release 2.3.0 is too old, while exact vendor commit remains unresolved due G2 magic/layout/log/transport patches. Config: SOF `0x01`, 2-byte big-endian ID/LEN/TYPE and CRC-16/ARC, 1024-byte TX buffer, no mutex with per-instance soft lock, request IDs `(next++ & 0x7FFF) | peer_bit`, responses preserve full IDs. Header CRC covers `SOF || ID || LEN || TYPE`; zero-length frames omit DATA_CKSUM. The production-excluded parser candidate now implements both details and has regression coverage for the former incorrect framing; it remains excluded until the surrounding G2 object/transport ABI is source-owned. See the [send/version audit](research/tinyframe-send-version-recovery-audit.md) and [receive audit](research/tinyframe-wire-format-recovery-audit.md) |
| FreeRTOS-Plus-CLI | The reusable MIT interpreter is the classic V1.0.4-compatible core. A production-excluded snapshot selects `43defa56`/tree `12448758`, verifies the exact CRLF C/H/history/license files through compatible ceiling `1309654d`, and carries a clean 1,077-byte patch containing only G2's blank-input suppression delta `[0x005848CA,0x005848F4)`. The independently named production parameter accessor source-integrates `[0x005848FC,0x00584960)`. Separately, seven GPL-3.0-only clean-room leaves replace the complete G2 console task `[0x00541600,0x0054171C)` while retaining the stock interpreter ABI, 22 setup groups, and 76 proprietary descriptors. The source task preserves the 127-byte safe payload and requires receive count exactly one; it supersedes the old two-byte capacity leaf. Snapshot and candidates remain excluded, and the selected commit is not an exact vendor-provenance claim. Recovered ABI: 16-byte descriptor, 8-byte list node, dynamic registration, 128-byte interpreter boundary, expected parameter counts -1..3, and highest parameter index 11. Vendor commands/handlers and unresolved static-allocation policy remain separate. See the [snapshot README](../third_party/freertos-plus-cli/README.openCFW.md), [source recovery audit](research/freertos-plus-cli-source-recovery-audit.md), [accessor promotion audit](research/freertos-cli-get-parameter-source-candidate-audit.md), and [console-task audit](research/freertos-cli-console-task-source-candidate-audit.md) |
| nanopb | Runtime at `0x0048F000`–`0x00491400` is compatible with pristine upstream **0.4.7–0.4.9**. Focused disassembly pins the callback ABI, varint guard, and saturating `pb_read()` accounting; reference builds prove all three surviving releases source-equivalent under the recovered config. The authenticated 0.4.9 compatibility snapshot verifies tag/commit/tree/blobs/Zlib offline. Thirteen bounded altered production functions now include private/public varint32 and `pb_skip_string` as independently audited leaves while pristine translation units remain unregistered. The constructor preserves the 16-byte ABI and canonical callback identity `0x0048F3A5` for all 30 callers. No constructor, varint32, or skip-string bootloader homolog exists. Even schemas/generated messages remain separate first-party inputs. See the [snapshot README](../third_party/nanopb/README.openCFW.md), [skip-string audit](research/nanopb-skip-string-source-audit.md), [varint32 audit](research/nanopb-decode-varint32-pair-source-audit.md), and [point-release audit](research/nanopb-point-release-recovery-audit.md). Remaining: recover vendor provenance or a generator stamp that separates the three surviving releases, and continue bounded source ownership of higher-level decoding and first-party schema glue. |

The nanopb configuration already proves 16-bit field descriptors,
error strings and callback streams enabled, 64-bit values supported, packed
repeated encoding and size checks enabled, and dynamic allocation disabled.
The old local nanopb 0.3.x trees are ABI-incompatible and must not be used.
openCFW now selects 0.4.9 and vendors `pb.h`, common, encode, and decode as one
authenticated production-excluded unit. Generated message sources, Even
schemas, and application transport glue remain separate. The selection is
recorded as an openCFW compatibility choice unless stronger vendor provenance
resolves the exact shipped point release.

## Uncertain or proprietary boundaries

Do not assign an upstream identity without stronger evidence:

- the generic `third_party\ringBuffer\ringbuffer.c` path;
- the `evtloop` 1.1.4 product/version label;
- IAR DLIB runtime code;
- G2 application services, audio algorithms, and cryptographic backend;
- codec, touch, and EM9305 controller images; and
- charging-case firmware HAL provenance.

These remain blob-backed or are re-created only from a reviewed behavioral
contract and host/target tests.

## Priority order

1. Obtain a full external-flash capture, validate pinned littlefs v2.10.1
   read-only against it, and only then install the bounded read-only port.
2. Extend the integrated EasyLogger boundary beyond the completed dual-image
   helper quartet while keeping both distinct G2 transports isolated.
3. Complete the FreeRTOS/CMSIS queue, task, list, and port closure from the
   authenticated V10.5.1 snapshot.
4. Validate the completed FlashDB 2.1.1 read-only source/oracle against a
   golden external-flash capture before any production mount; keep every
   write/erase path denied.
5. Capture hardware TinyFrame golden packets and validate the recovered wire format against them.
6. Integrate LVGL, Cordio, and FreeType when the link strategy can reclaim
   stock code rather than duplicating large libraries in the append-only
   overlay.

## Prior authenticated FreeRTOS getter

`runtime_freertos_pc_task_get_name.c` is a bounded production port of
`pcTaskGetName` from authenticated FreeRTOS-Kernel V10.5.1 `tasks.c` at
commit `def7d2df2b0506d3d249334974f51e427c17a41c`. The 3,489-byte MIT
source has SHA-256
`d46408b0bdce9622ac1fa8c694ccc790c76169b681d0c413a4ada35fbe29d21a`.
The G2 seams are `pxCurrentTCB=0x20074A20`,
`configMAX_TASK_NAME_LEN=32`, `pcTaskName=+0x34`, and the fail-stop
assertion's source-owned `ulSetInterruptMask` target.

Production pins are: 34-byte stock SHA-256
`a25ace28ece3ca37f11da7e73945acb28f1f99d906203613e9856d2070c07817`,
raw 38-byte leaf SHA-256
`b680e949844cca19a586fbe865837f8180e592434ac1517b29ceb1482c9dd3b6`,
and final leaf SHA-256
`88edbdea558812d213013a8d319a09c63dafa86ec91a7640f427c72c77552da1`.

## Prior CMSIS-FreeRTOS `osMutexNew` production

The 9,798-byte Apache-2.0
`runtime_cmsis_mutex_new.c`, SHA-256
`28081734a384c089635681014ed028414b75d375c22f0a52a64f53e22842cf2d`,
ports the exact authenticated CMSIS-FreeRTOS v10.5.1 algorithm from commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. Focused G2 evidence pins
enabled static/dynamic allocation and recursive mutexes, disabled queue
registry, robust rejection, the recursive-handle low bit, the 80-byte
`StaticSemaphore_t`, the 16-byte 32-bit attribute ABI, and the inlined
`IPSR`/`PRIMASK`/`BASEPRI` rejection policy.

The complete stock span `[0x0044971C,0x004497B6)` is 154 bytes with SHA-256
`09f88d8a6a64730936a52aa0c2f90d9bcb0152f6e2439919f6409110148999ec`.
Its 30 direct callers have ordered digest
`14d18197e409351bfa6ded1310c61c1f27246ebd93ecf86452d19ac0bdadbfd0`;
no alternate, interior, or stored entry exists. Two generated alignment bytes
at `[0x007B02A6,0x007B02A8)` precede the 116-byte leaf at
`[0x007B02A8,0x007B031C)`. Its five relocations at
`+0x0E/+0x32/+0x56/+0x5C/+0x64` bind only to the source-owned scheduler-state
getter and static/dynamic mutex creators at
`0x007AECFC/0x007AEEBC/0x007AE100`.

That release's overlay was 114,680 bytes with SHA-256
`7603cf2a0de6e8b05d66dc356bf3e0701f6157536d29bdac8ad692dc56e0362c`;
the 3,638,076-byte Apollo-main component hashes to
`f696c6dfbd8ab1f7b5cc44fdc06fcdc5baf44f368ad55130e7571d82ee31ec82`.
The 4,416,258-byte package hashes to
`11d40cd1b3648f96b5ec98c9fa2dff6de121e878978206a0a9694ede38d3a0ff`.
The focused production gate passes 10/10 tests offline; no hardware was
accessed.

At that point `osSemaphoreNew` remained candidate-only pending production
closure of `heap_4`.

## Prior FreeRTOS heap and CMSIS semaphore production

The pristine authenticated V10.5.1 `heap_4.c` now supplies the algorithms for
the bounded 16,885-byte MIT `runtime_freertos_heap4.c` adapter, SHA-256
`d848b90a00da24db963c49dbff2472314b2a76c6cf269efef46e6cac56889986`.
Its four source leaves preserve the recovered G2 heap layout and accounting
globals. The 5,851-byte MIT `runtime_freertos_queue_delete.c`, SHA-256
`fa8033f61e418dbfb304dd7443dea340bfff88958df493e276ea92db4491da2b`,
closes `vQueueDelete` over source-owned heap free and interrupt masking.

The 11,566-byte Apache-2.0 `runtime_cmsis_semaphore_new.c`, SHA-256
`a947868d3fbcfc7f41d021210355e0ff777d49d3db84fa0da71a255d319c1527`,
ports exact authenticated CMSIS-FreeRTOS v10.5.1 `osSemaphoreNew`. Its
178-byte leaf closes over source scheduler, queue creation/send/delete, and
counting-semaphore dependencies. The overlay/component/package hashes at that
historical milestone were
`6359e4e8c824af3cea36280a1aabd6ad671027e38fb3263fe9ac0cbb292660b4`,
`00d112e265f40dd8bf98fc9021bba54b3bcc94f159111b2f4815d5484e91c67c`,
and
`064c9429352132cee2a5dfe45c2bf52349e10111b89db91f093b1ce16ed0c2b0`.

## Prior dual-image EasyLogger helper production

The shared EasyLogger helper quartet now runs from source in Apollo main and
the S200 bootloader. Main's 115,910-byte overlay and 3,639,306-byte component
hash to
`e59da6e6753c0c8a9fa73bad8cd555313d0e2ae6ed95006c818e6697e4fbe32d`
and
`00f5f11dd18c13c56137d0f527da3ecd8ae850a9ae35dc96d671a4b998d79b61`.
Boot's 622-byte overlay and 149,222-byte provider hash to
`fc02cf66854adace4d213e08764e435e27c8c2bc7cc4f7caac6ff286f3adf813`
and
`b4a5b0f2028842a2d6fde9424fff05fac2db3bf0e26e7f01d16a990e67ed9052`.
The 4,417,760-byte package hashes to
`fb662322f26e06aa04eb1d3f55f8c8f18606e510fac9c35885de3e4f92864c4d`;
its 592,687-byte flash plan hashes to
`c06c84e277bad2160479e0ec1f7a626abb804574f42ecee0709f0978657cd1b3`.

## Preceding FreeRTOS tick-getter production

The production source boundary reuses the MIT FreeRTOS-Kernel V10.5.1
algorithms at commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. The pinned 223,695-byte
upstream `tasks.c` hashes to
`14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463`.
The bounded 3,412-byte `runtime_freertos_tick_count.c` and 1,186-byte header
hash to
`948d1b2de6026adc7cf84a34a359c859c32126b3afcafe92c2347f5f7ab56363`
and
`adc4065b3504a7eacb2e29e2d357636917e2b690afc49b265689e36d66171dae`.
Focused disassembly supplies only the G2 boundary and state binding.

The exact official spans are `[0x00454EFE,0x00454F06)` for
`xTaskGetTickCount` and `[0x00454F06,0x00454F10)` for
`xTaskGetTickCountFromISR`; their aggregate 18-byte SHA-256 is
`d0b93ff29439d26b92dcd56fd012a9dab842364f7c5f4b4f7f39a27ed8cfe077`.
The earlier proposed ISR entry at `0x00454F08` is corrected to an interior
instruction. Nine normal callers and the sole ISR caller retain the official
entries.

Apollo main places two generated alignment bytes at
`[0x007B07EA,0x007B07EC)`, a relocation-free 12-byte source provider at
`[0x007B07EC,0x007B07F8)`, and the two four-byte source getters through
`0x007B0800`. The provider binds `xTickCount` at `0x20074A34`; each getter
has one jump relocation to it. Complete non-linking redirects and NOP fill
replace the 18 official bytes.

The 115,932-byte overlay and 3,639,328-byte main component hash to
`272ba0e0492b0c6b721adec53a007809158d6871ccdb7ec52d4b6ceadd4b4529`
and
`615304858150f5ee6b7b4c62a714629375010c6f4ab20bea1b6958daa6a5b4af`.
The raw main application partitions into 116,118 source, 81,622 generated,
and 3,441,556 opaque bytes. Builder accounting is 116,114 source-owned bytes
including 182 in place, 81,626 generated patch-site bytes, 81,808
replaced-stock bytes, 3,441,556 opaque base bytes, and the 32-byte wrapper.

The 4,417,782-byte package hashes to
`3bf635fb81439451e67642dc5ce11dde47a1773bda8ef11c12b35cd9bbbec01d`
and classifies 116,738 source bytes (2.642457%), 83,415 generated bytes
(1.888165%), and 4,217,629 opaque bytes (95.469378%); 200,153 bytes
(4.530622%) are controlled. Its 596,957-byte flash plan hashes to
`2b89447a0a867d1ec34f51e5798a4da7b28effe8bc5d7e27b1b7f24ce1c9cd3c`
and records 828 placed, two unresolved, five container-only, and six
protected regions. Of the placed regions, 53 are source-compiled, 574 are
generated source-entry replacements, and 18 are generated alignments. Boot
ownership remains 620 source, 817 generated, and 147,785 opaque bytes.

## Preceding FreeRTOS missed-yield production

The complete stock `vTaskMissedYield` function is the ten-byte span
`[0x004555E6,0x004555F0)`, SHA-256
`8cada1af8ad4973f2ad647d45c8a0ac9c56fdf2d8b270607844b7940eb7d5d2d`.
It has exactly two direct callers at `0x00441FA2` and `0x00441FD8`, and no
alternate entry or stored function pointer. FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` identifies its semantics
unequivocally as `xYieldPending = pdTRUE`; focused disassembly recovers the
G2 word at `0x20074A44`.

Apple clang 21 and Homebrew clang 22.1.8 emit the same relocation-free
14-byte source leaf. Canonical placement is
`[0x007B0800,0x007B080E)`; Linux placement is
`[0x007B0F38,0x007B0F46)` after two alignment bytes. The canonical overlay,
component, and package are 115,946, 3,639,342, and 4,417,796 bytes, with
SHA-256 values
`a24cd67ac1d308b8812c329a294f3f07cbe9db4bc815be3fe081ba0c2fd9008c`,
`f037745e9b85d16fc048ba2fedb282f7fc498a524a90b803b652556e286cf77d`,
and
`f06fdc7a1e9034e72321680b35fbd542b12dad06135e6f01f701d670dba676ae`.
The overlay contains 592 functions and 559 patch sites; builder accounting
is 116,128 source-owned, 81,636 generated patch, 81,818 replaced-stock, and
3,441,546 opaque bytes.

Linux independently pins a 117,794-byte overlay, 3,641,190-byte component,
and 4,419,644-byte package with SHA-256 values
`00cbcf99a63f69fa7fd2af607685179ac73edeafd0fc8c4e1ad49b6a13a02c0e`,
`f134beba731634fd81b42b143e3b1e414b4b8c07a9e3f009cc49e7c8258b1657`,
and
`13409c4d615651f1b8cb5618d6d1cb1a4d5095e8245c41b41c585a258c9114e1`.
Its aggregate is source-root-sensitive because TLSF embeds absolute
`__FILE__`; the recorded root spelling is
`/Users/kalani/Repo/SybilSightABCD`. See
[`research/freertos-missed-yield-source-boundary-audit.md`](research/freertos-missed-yield-source-boundary-audit.md).

## Preceding FreeRTOS event-item and mutex-held production

FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` unequivocally supplies the
current `uxTaskResetEventItemValue` and
`pvTaskIncrementMutexHeldCount` source bodies. The recovered boundaries are:

| Function | Stock span | Bytes | Stock SHA-256 | Caller |
|---|---|---:|---|---|
| `uxTaskResetEventItemValue` | `[0x00455ACA,0x00455AE0)` | 22 | `76463ec53fbc06884c159bf5b7d01708c06e404e9b51bdcaab307b219179c049` | `0x0047ECCE` |
| `pvTaskIncrementMutexHeldCount` | `[0x00455AE0,0x00455AF6)` | 22 | `3cca7b821687976e59eccd737dc20b2064b86d66195c6f60f6a7cc2353f40d2f` | `0x00441D46` |

Both functions preserve volatile evaluations through `pxCurrentTCB` at
`0x20074A20`. Reset binds event-list value `+0x18`, priority `+0x2C`, and
56 priorities. Mutex-held binds field `+0x64` and
`configUSE_MUTEXES=1`.

Canonical placement is `[0x007B0810,0x007B082A)` for the 26-byte reset leaf
and `[0x007B082C,0x007B0844)` for the 24-byte mutex-held leaf, with two
alignment bytes before each. Their SHA-256 values are
`04fee613f7c2fb46a3e6f5832f7ea61875543a30160757ffd63579b58f0c45c6`
and
`494b41afb48389988e2678920ae7e1796b41a3d568e5c01c35c12c48bf7b57bf`.

The canonical overlay, component, and package are 116,000, 3,639,396, and
4,417,850 bytes, with SHA-256 values
`203b31ea09e03c919da51b4d194cab2c3325ad5d5eed3efc7464018af90e2059`,
`78375130a88e6ec0d14bc936b8f16f4535056344288419baba83d81fd4f3bdc3`,
and
`9ffe927fdb587db9fae07043d7dc0938d2519c95d29e71cd0dca021cadf31d85`.
The overlay records 594 functions and 561 patch sites; builder accounting is
116,182 source-owned, 81,680 generated patch, 81,862 replaced-stock, and
3,441,502 opaque bytes.

The package contains 116,802 source, 83,473 generated, and 4,217,575 opaque
bytes; 200,275 bytes are controlled. Its 604,237-byte flash plan hashes to
`c25b80e357274ee25903c74d6472cb0a3ab30d6f5d702a053b88c145e3ddd521`
and records 838 placed, two unresolved, and five container-only regions.

Linux places the leaves at `[0x007B0F48,0x007B0F62)` and
`[0x007B0F64,0x007B0F7C)`. Its overlay, component, and package are 117,848,
3,641,244, and 4,419,698 bytes with SHA-256 values
`12e592da338cbcf99ee81ec3551ff5ae22410f34387ba35dcbdfbf38294f8cc9`,
`a81f7ca5c4219f9f31820a9f3e18aa6f5bb85004b7bedc9f25f9083dbdfd14e6`,
and
`e86eb0003e5b9f7f15c416ab9485e3457ce2082b17720d85ef59b6f198efe4b2`.
The reviewed Linux source root remains
`/Users/kalani/Repo/SybilSightABCD`. See the
[reset audit](research/freertos-reset-event-item-value-source-boundary-audit.md)
and [mutex-held audit](research/freertos-mutex-held-source-boundary-audit.md).

## Prior FreeRTOS scheduler-suspend and timeout-state production

That release added two more unequivocal FreeRTOS-Kernel V10.5.1 task leaves
from authenticated commit
`def7d2df2b0506d3d249334974f51e427c17a41c`:

| Function | Stock span | Bytes | Stock SHA-256 | Recovered G2 binding |
|---|---|---:|---|---|
| `vTaskSuspendAll` | `[0x00454D7C,0x00454D88)` | 12 | `3651c872be8fd55503df57fb49f5d0b7b94b0e784237141389a4b965b8edb6e2` | volatile `uxSchedulerSuspended` word `0x20074A58`, 32-bit increment and barrier ordering |
| `vTaskInternalSetTimeOutState` | `[0x00455556,0x00455566)` | 16 | `6ff12b123d1647953300d002a439daf4df52f96e369eebbb0b183a1a4fb3e862` | `xNumOfOverflows=0x20074A48`, `xTickCount=0x20074A34`, `TimeOut_t` size/alignment 8/4 and offsets `+0`/`+4` |

The timeout leaf has four direct callers at `0x00441886`, `0x00441B90`,
`0x00441CBC`, and `0x004555D0`. Whole-image scans close alternate branches,
interior transfers, and stored pointers. Apple clang 21 and Homebrew clang
22.1.8 emit the same relocation-free 18-byte source body, SHA-256
`8319202babe42ee571774682793c4c4c1a54c3a72826a92ba5c60273ba451c6a`,
while preserving overflow-read/store before tick-read/store.

Canonical placement is `[0x007B0844,0x007B0854)` for suspend and
`[0x007B0854,0x007B0866)` for timeout. Linux placement is
`[0x007B0F7C,0x007B0F8C)` and `[0x007B0F8C,0x007B0F9E)`. Neither profile
requires alignment padding between the two leaves.

That release's production pins were:

| Profile / artifact | Bytes | SHA-256 |
|---|---:|---|
| canonical overlay | 116,034 | `d0b36ab3661f3b3487e3962bfe58d9f588f6a6f1ea14e1d9389f7e45d98094bd` |
| canonical Apollo-main component | 3,639,430 | `8a747653cc4d938e447197f2bec199933b68072318f0743e3cd85dcf656db8bc` |
| canonical core-source package | 4,417,884 | `e3b7f29a19a4b3c19a14377a8ea8a77d14458a48678955d406ef7eea274dd6e7` |
| Linux overlay | 117,882 | `5c3c381342bb57ec4f33192ea89c2d40e8f0018c39c7092551243be7159dc326` |
| Linux Apollo-main component | 3,641,278 | `6bead197d657c26fa6ba84210949c8e28b266fbf63a8f908edda1d64516a3163` |
| Linux core-source package | 4,419,732 | `a801d1ecbf83780701cbb7fdc1ae14401a656ba79102877458a3a88c73bc3fc4` |

The overlay records 596 functions and 563 patch sites. Builder accounting is
116,216 source-owned, 81,708 generated patch, 81,890 replaced-stock, and
3,441,474 opaque bytes. The package records 116,836 source, 83,501
generated, and 4,217,547 opaque bytes; 200,337 bytes are controlled. Its
608,608-byte flash plan hashes to
`c6cde87716d8ff407e06998aadaaa0da6e78e5689ea1ac2963f104178447cae2`
and records 844 placed, two unresolved, and five container-only regions.

The reviewed Linux root remains `/Users/kalani/Repo/SybilSightABCD` because
unrelated TLSF data embeds absolute `__FILE__`. See the
[timeout-state audit](research/freertos-timeout-state-source-boundary-audit.md)
for the complete source, topology, ABI, and redirect evidence.

## Prior authenticated scheduler-cluster reuse

FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` now supplies the production
implementations of `vPortYield`, `vPortEnterCritical`, `vPortExitCritical`,
`prvResetNextTaskUnblockTime`, `xTaskIncrementTick`, and `xTaskResumeAll`.
Focused disassembly supplies only the G2 configuration and ABI bindings:
fixed scheduler globals, list/TCB layout, `configMAX_PRIORITIES=56`, tick and
time-slicing policy, interrupt-mask providers, and port MMIO addresses.

The tranche replaces 770 stock bytes and adds 776 compiled bytes plus six
Apple alignment bytes. Its canonical overlay/component/package pins are
116,816 / 3,640,212 / 4,418,666 bytes with SHA-256 values
`b9cb2b00d4859650d120ff713a8af9a1ca626876b46bac751098abdbca575153`,
`fcb218fd5d9a33b2398cd046550b26258ca9da90d423c50ae635203535614a58`,
and
`5a31772a8a4fb746fa9eff53d618541fd38cf44a93c9d602eb88e15d142cef01`.
This is source reuse under the vendored MIT notice, not a decompiled
reimplementation. G2-specific seams remain explicitly pinned and tested.

## Prior authenticated LZ4 v1.10.0 source reuse

The maintained production decompressor is now built from authenticated
upstream LZ4 v1.10.0 commit
`ebb370ca83af193212df4dcbadcc5d87bc0de2f0` under BSD-2-Clause. This is an
openCFW selection: it does not assign that point release to the stripped stock
image. The selected closure is intentionally narrow—`LZ4_decompress_safe`,
64 bytes of read-only `inc32table`/`dec64table`, a four-byte G2 ABI adapter,
and a 30-byte EvenHub mode-2 adapter. No compressor, frame API, writable LZ4
state, or unrelated upstream function is retained.

Apple clang emits 1,660 bytes of relocated decoder text at
`[0x007B0B74,0x007B11F0)`, followed by the tables at
`[0x007B11F0,0x007B1230)`, safe adapter at
`[0x007B1230,0x007B1234)`, and mode-2 adapter at
`[0x007B1234,0x007B1252)`. Linux clang emits 1,690 text bytes at
`[0x007B12A8,0x007B1942)`, two alignment bytes, the same 64-byte tables at
`[0x007B1944,0x007B1984)`, then the adapters at
`[0x007B1984,0x007B1988)` and `[0x007B1988,0x007B19A6)`.

| Artifact | Apple clang 21 | Linux clang 22.1.8 |
|---|---|---|
| Overlay | 118,574 / `1a0b92e12203b78f48191969744128bfbcc2559c811ae40a1f393370eceacea9` | 120,450 / `2901320d6169c2b9ad49d501cb25e7f50ceaa90b94e7d0640f80d318932d8fc7` |
| Apollo-main component | 3,641,970 / `6621c7d0403e37d0598c5f2f521633afb13b98034542c8010cf9d210f576e91d` | 3,643,846 / `140cac71e8ec612f2129800ee9a205c30f743dfd51664207c1661fdb337d8f8d` |
| Core-source package | 4,420,424 / `d576be2c4626006a830593a5ad1aae21da8ee3e16d67d80c62eb8f3994bfc294` | 4,422,300 / `cb1516c2c61402626a723f05f4fb315e8af91adae599818830b2f8e1ffee0bf8` |

The original primary mode-2 and hand-decoder sections are retained under
`_legacy` names and are unreachable, preventing address churn in later
functions. The stock generic decoder and reader likewise remain unreachable
opaque compatibility bytes. The active object still binds authenticated stock
void-EABI `__aeabi_memcpy` at `0x00439BE4` and `__aeabi_memmove` at
`0x00439710`; full provider spans, overlap paths, and the memmove-to-memcpy
tail are audited.

Canonical component accounting is 118,756 source-owned, 82,478 generated
patch, 82,660 replaced-stock, 3,440,704 opaque-base, and 32 wrapper bytes.
Canonical package accounting is 119,370 source, 84,277 generated, and
4,216,777 opaque bytes. This integration was validated offline; no hardware
was flashed or executed.

## Prior authenticated FreeRTOS queue/task closure reuse

FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` now supplies production
`xTaskRemoveFromEventList`, `xQueueGiveFromISR`, and
`prvTaskCheckFreeStackSpace`. These are source reuse under the retained MIT
license. Disassembly contributes only the G2-specific queue/list/TCB/global
bindings, caller topology, and stack configuration.

The three complete stock spans total 468 bytes; the selected source leaves
total 490 bytes and need one two-byte alignment region per profile. Apple
places them at `0x007B1254..0x007B143E`; Linux places them at
`0x007B19A8..0x007B1B92`. The package pins are 4,420,916 bytes /
`1b3ea44cc1cbd8004585e0208e33605c4e5f59229fdc5cb23395d19e0ba120f2`
for Apple and 4,422,792 bytes /
`b93b39eb8e6f70e144b517dd7d770adcea67f62aa1100d722d4d1d0e6f8907ea`
for Linux. The reviewed exact-root Linux recording and two normal rebuilds
were byte-identical. No physical device was used.

## Preceding authenticated FreeRTOS timeout-check reuse

Authenticated FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` now also supplies production
`xTaskCheckForTimeOut`. This is source reuse under the retained upstream MIT
license, not a decompilation. Focused disassembly supplies only the G2
configuration and ABI facts needed to instantiate that released algorithm:

- official span `[0x00455566,0x004555E6)`, 128 bytes, SHA-256
  `83a983995a285b3257a1213bdbe3fa0542bae0c9296a88fd8b22c1388abdf72c`;
- `INCLUDE_vTaskSuspend=1`, `INCLUDE_xTaskAbortDelay=0`, 32-bit ticks, and
  `portMAX_DELAY=UINT32_MAX`;
- `xTickCount=0x20074A34`, `xNumOfOverflows=0x20074A48`, and the eight-byte
  `TimeOut_t` layout; and
- the three callers plus the already source-owned assertion, critical, and
  internal timeout-snapshot providers.

Apple and Linux append a 136-byte relocation-free source leaf after two
alignment bytes. Their leaf hashes are
`33f0782fa8af468bccf78b558cc010a9f7a89f30c7c76abced9a799feb6a93f5`
and
`486515dfdbdb1e175321445df167dca27357f270421b2d00492268e8da7c815c`.
The canonical and Linux packages are respectively 4,421,054 bytes /
`4fb13f64e81b8a6ef9bdf784ac38d5fc08ed03e4d310601a48bf4b395c20ab37`
and 4,422,930 bytes /
`22c0e367882b005c1b85ee40d138e596c423d5a6335b8d93bc5a68873323c3ab`.
All provenance checks, compilation, assembly, and package inspection were
offline; no hardware was connected or operated.

## Preceding authenticated FreeRTOS semaphore-take reuse

FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` now supplies production
`xQueueSemaphoreTake` and its private
`prvGetDisinheritPriorityAfterTimeout` dependency. This is authenticated MIT
source reuse; disassembly supplies only the recovered G2 configuration and
ABI. The Apple leaves are 602 and 18 bytes at overlay offsets 120,728 and
120,708; Linux emits 600 and 18 bytes at offsets 122,584 and 122,564. The
candidate's sole relocation binds to the source helper. The stock helper stays
byte-identical but has no remaining assembled branch or stored-pointer
reference, so no unnecessary redirect was emitted. Final Apple/Linux package
pins are 4,423,180 /
`74278f0c7ae44e5364a6bca3abc762fcb48a0b2dcb06d816412566c5e974541d`
and 4,425,034 /
`b07ee2e813356553bd5c8f0a7c2f951376f8b338be6e53b6aff75824062f47f1`.
No hardware was operated.

## Preceding authenticated littlefs private rewind reuse

The littlefs v2.10.1 snapshot at commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318` now also supplies the bounded
production adaptation `runtime_littlefs_file_rewind_private.c`. Its exact
192-byte upstream definition begins at `lfs.c` offset 118,157 and hashes to
`74638292061613417c2ce7c6bbed200d2bee046c35a7a835fb4d9bb183ab755a`.
The 1,239-byte source and 1,743-byte header hash to
`e6afb5b67671b3219971b19c20290c601568752d814064147f5ccd4118f5acc8`
and
`7430dcd1ad1ea3973d619f2d67d8d8b11a688018d48a3bc26a40e407d1fedb56`.

The selected source reuse is BSD-3-Clause. Focused disassembly supplies only
the G2-specific private seek binding at `0x004CE3BC`, the sole public-wrapper
caller, stock boundary, and placement. It does not authenticate the vendor's
filesystem port or authorize format/erase/hardware behavior.

## Preceding bounded CmBacktrace production reuse

The authenticated CmBacktrace compatibility baseline at commit
`73714489f9d8af130aacb515586b397b604a5768` is now represented in production
by the bounded MIT-licensed
`components/shared/cmbacktrace/runtime_cmbacktrace_get_cur_thread_name.c`.
This production source reuses the upstream FreeRTOS behavior only; commit
selection remains an openCFW compatibility choice, not proof of Even's exact
vendor checkout. The vendored pristine snapshot remains production-excluded.

Device-specific behavior lives in the separately recovered openCFW adapter:
current TCB at `0x20074A20`, task-name offset `0x34`, including null-to-`0x34`.
The adapter is not attributed to upstream CmBacktrace. Both Apple and Linux
target objects and placements, the single stock entry replacement, and the
complete ingress closure are fail-closed. No hardware was operated.

## Preceding bounded nanopb production reuse

The authenticated nanopb 0.4.9 snapshot is now used as the explicit
compatibility baseline for three altered production leaves:
`components/shared/nanopb/runtime_nanopb_decode_varint.c` and
`components/shared/nanopb/runtime_nanopb_skip_varint.c`, plus
`components/shared/nanopb/runtime_nanopb_close_string_substream.c`. Version
0.4.9 is an
openCFW compatibility selection within the authenticated 0.4.7–0.4.9 range,
not proof of the vendor's nanopb revision or checkout; all three pristine
releases remain indistinguishable under recovered G2 evidence.

For `pb_decode_varint`, focused disassembly supplies the exact stock range,
16-byte callback stream ABI, three-caller topology, overflow literal, and the
reviewed `pb_readbyte` seam at `0x0048F454`. For `pb_skip_varint`, the verifier
pins the altered source and header, authenticated upstream function bytes,
36-byte stock range `[0x0048F628,0x0048F64C)`, and sole `pb_read` seam at
`0x0048F3BE`. For `pb_close_string_substream`, it pins the 42-byte stock range
`[0x0048F7CA,0x0048F7F4)`, all three callers, zero-remainder and failed-read
semantics, the exact 16-byte stream layout, and the same sole stock `pb_read`
seam. The 2,061-byte source and 2,537-byte header hash to
`736e7ec228f9282ba5b093fd482441e6e2017fff860d989dc3aadb2bdeff0fcb`
and
`851af370162d79f4bd0be8b8bb9a5731d47cf02527078b9e278019340f2d65d4`.
The broader pristine `pb_common.c`, `pb_decode.c`, and
`pb_encode.c` files remain production-unregistered. The offline snapshot
verifier permits only these three bounded registrations and rejects direct
broad-runtime linkage. All three production sources retain Zlib terms;
host-only candidate and oracle fixtures remain excluded.

Both compiler profiles pin the relevant raw objects, extracted text and
relocation closures, full-span redirects, aggregate component, and package.
Behavioral qualification pins authenticated upstream semantics and exercises
the bounded production behavior with host oracles. All work was offline; no
firmware was signed or flashed and no G2 hardware was operated.

## Preceding authenticated FreeRTOS queue-reset/unordered-removal reuse

FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` now supplies production
`xQueueGenericReset` and `vTaskRemoveFromUnorderedEventList`. Focused
disassembly supplies only G2 queue/list/TCB ABI, fixed-address scheduler
state, feature gates, assertion providers, and entry topology. Full-span
redirects replace the 180-byte and 218-byte stock bodies; all Apple and Linux
source leaves are relocation-free.

Apple's overlay/component/package pins are 121,718 /
`76e21a06d75ed5c3beb5343014621e432726ea285e46d54978a4de43d9b6b666`,
3,645,114 /
`c32ff5c5daf946812df503cfaa328c1cc22dc4206201da0b752a365f235e0108`,
and 4,423,568 /
`0e18c7c435edaff3fa5b692e8c17251f075c472933c93b05153ac0307e6f4ca8`.
The exact-root Linux pins are 123,570 /
`6885adb2da4019a5595fd14fefe7e6682e6d32e63b45c47b3436828a1238d288`,
3,646,966 /
`657140490b0bd0b1f5aeb44505cc24b01377d16254f91c30e31893d1890731ca`,
and 4,425,420 /
`d7870c13b9417f8a9866ad6b87858e712c1c6c005b0b534bdd1d4ba540b64d60`.
This is authenticated MIT source reuse qualified offline; no hardware was
operated.

## Bounded dual-image littlefs tag-ID production reuse

The authenticated littlefs v2.10.1 source-equivalent snapshot now also
supplies `components/shared/littlefs/runtime_littlefs_tag_id.c` and its
header. The exact upstream authority is `lfs.c[10702:10793]`, 91 bytes,
SHA-256
`50140c563689852013dfad180ec3b6464c6b6c5b22854f5492d63cf5de57fbe2`,
at commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`. This establishes
source-equivalent behavior, not Even Realities' exact historical checkout.

Focused disassembly contributes only the 32-bit scalar ABI, identical stock
spans `[0x004CAEB0,0x004CAEB8)` and `[0x00410BB8,0x00410BC0)`, complete
50/41 direct-caller topology, and entry-replacement addresses. The common
six-byte source leaf is provider- and relocation-free and implements only
`(tag & 0x000ffc00) >> 10`.

Final profile placements and aggregate artifact identities are pinned in the
memory-map and reproducible-build ledgers. The unchanged BSD-3-Clause terms remain at
`third_party/littlefs/LICENSE.md`. This bounded scalar reuse imports neither
the broad library nor a block-device, mount, format, program, or erase path,
and it authorizes no signing, flashing, reset, boot, or hardware operation.

## Current bounded dual-image littlefs tag-validity/type1 production reuse

The authenticated littlefs v2.10.1 source-equivalent snapshot now also
supplies altered BSD-3-Clause adaptations of `lfs_tag_isvalid` and
`lfs_tag_type1`. Their exact upstream authorities are `lfs.c[10042:10129]`
and `lfs.c[10232:10326]`, with SHA-256
`bb8e571d6dbddd1fe446ec7b4838979a4ab9bd6d6184e2f8d9b6c00cc0835b13`
and `ebf0229d6e0f78175c43641b09906fea19575fc3f34ac8862ae60159df1ec743`.
This proves compatible source behavior, not Even Realities' exact checkout.

Focused disassembly contributes only the 32-bit scalar ABI, identical
main/boot stock bodies, three/eight caller sets, entry topology, and patch
addresses. Both production leaves are provider- and relocation-free and are
registered atomically in the two overlays. The final Apple package is
4,426,458 bytes, SHA-256
`f0e7e4c5e090ea558968b6293f3eec0a7f88a6126ea164547c25c8462b60be23`;
exact-root Linux is 4,428,278 bytes, SHA-256
`07cee183416db26bbe13673c1123e4ef19593d6343caa63c6c94791a210dc0dc`.
Complete component hashes remain fail-closed in the overlay registries and
canonical manifest.

The unchanged BSD-3-Clause terms remain at
`third_party/littlefs/LICENSE.md`. The two scalar helpers do not import the
broad library, a block-device port, or a format/erase path. Offline assembly
is GO; signing, flashing, reset, boot, filesystem mutation, and hardware
operation remain NO-GO.

## Preceding authenticated FreeRTOS task-list initializer reuse

FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` now also supplies the bounded
production adaptation
`components/shared/freertos/runtime_freertos_task_lists_initialize.c`. The
exact upstream boundary is `tasks.c[150869:151768]`, 899 bytes with SHA-256
`0908b0fb7a1b43d6d4fa2bd8212ba069ac6a8d4d036b4f973ae7f3baa6dd6e63`.
The 3,529-byte source and 5,886-byte header retain MIT terms and hash to
`58773452256b0f44647040085bbcc7a896a1cbd3efd0c5c4b4de3ddfe1a9e857`
and
`6fe827f6d2659a784e8b3e22fa096162dfd4003146c0425222efc92c63baef9e`.

The recovered G2 list ABI, 56-priority selection, fixed Apollo-main SRAM map,
sole caller, overlay placement, and generated `replace_freertos_task_lists_initialize`
entry replacement are compatibility evidence, not upstream provenance. The
production symbol `open_cfw_freertos_task_lists_initialize` closes its only
callable dependency over source-owned `open_cfw_freertos_list_initialise`.
The separately compiled bootloader homolog remains excluded. Qualification
was offline; no firmware was signed or flashed and no hardware was operated.

## Preceding EasyLogger G2 single-owner glue selection

The downstream/private G2 record builder at the official entry
`[0x00448D4E,0x00448DD2)` now selects the corrected single-owner openCFW
implementation. This does not change the upstream attribution boundary:
`elog_output` remains the authenticated EasyLogger-derived portion, while the
record builder, enqueue ownership contract, and submit wrapper remain G2
application glue. The stock-compatible double-recycle builder is retained as
an audit oracle and is not linked into production.

Apple overlay/component/package pins are 121,706 / 3,645,102 / 4,423,556
bytes and exact-root Linux pins are 123,558 / 3,646,954 / 4,425,408 bytes.
Their respective SHA-256 triples are
`03dd692b55204fc36f67469ece0175e981b6281123a1b20b3db592ee2dd0b44c`,
`ae123c6a119bfebd0420898aef590a9ba1fd7f7dc7da00b3d347f6573bba43ec`,
`7cf86c7311b4684eb6d2fdd4f832989317c858733f8438dc01ee649fcd1cf250`
and
`f2c33def6131981c1a283968bc02bd55cde32536f4f33a7fa3cbf905d42693fc`,
`5ff7dd5894b74573971912371f22d0b463c32552ea1037441e1de992a6a8d3b9`,
`fe49c0d9830327a0fdd0e7815a147bb6b810e27b9a9277b3bbfe9021de247a75`.
No hardware was operated.

## Preceding bounded nanopb fixed32 production reuse

The authenticated nanopb compatibility snapshot now supplies a fourth
bounded production adaptation,
`components/shared/nanopb/runtime_nanopb_decode_fixed32.c` and its header.
The selected baseline is official nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`, but the exact upstream
definition is identical across authenticated pristine 0.4.7, 0.4.8, and
0.4.9. This establishes compatibility, not Even Realities' historical point
release or checkout.

The 1,975-byte altered Zlib source and 1,750-byte header hash to
`fefd8a899174fb9332c366df691dc2c8ec6f4792f3fd464b65dbb573ace8ee19`
and
`738e4c7d4ea983b0ba967fa42cdcc61cb2e20837531bc6176b7f95a5fe8e2460`.
Focused disassembly supplies only the G2 stock span
`[0x00490190,0x004901AC)`, sole caller, recovered stream boundary, little-
endian behavior, and provider address. The leaf retains one call to stock
`pb_read` at `0x0048F3BE`; neither that provider nor the broader pristine
`pb_common.c`, `pb_decode.c`, or `pb_encode.c` translation units become
source-owned.

Both reviewed profiles pin the same 960-byte object and 50-byte unrelocated
text, with exactly one call relocation at offset 10. Full-span redirects and
that phase's aggregate component/package artifacts are qualified offline.
The 648/597/79 config census belongs to this preceding tranche. No signing,
flashing, or hardware behavior is claimed.

## Preceding bounded littlefs tag-type production reuse

The authenticated littlefs v2.10.1 source-equivalent snapshot now supplies
the bounded BSD-3-Clause production adaptation
`components/shared/littlefs/runtime_littlefs_tag_type2.c` and its header. The
selected commit is `0494ce7169f06a734a7bd7585f49a9fa91fa7318`; the exact
92-byte upstream definition hashes to
`65f614cf5ed7152f7ad2176547453c329b1f15442e550ef6632b0f7773970f78`.
This establishes source compatibility, not the vendor's exact historical
checkout.

Focused disassembly supplies only the scalar `uint32_t` ABI, official stock
span `[0x004CAE90,0x004CAE98)`, two direct callers, and closed entry topology.
The ten-byte source text is relocation- and provider-free and hashes to
`88be40d05d37142bf0bae8306026d8c405a4f8f441aabd87ee6731557d4149fd`.
Apple places it at `[0x007B29A8,0x007B29B2)` and exact-root Linux at
`[0x007B30C4,0x007B30CE)`.

The current config census is 649 functions, 598 patches, and 80 relocated
leaves; the Apple build report records 645 overlay functions and 594 generated
patch records. Apple overlay/component/package/plan sizes are 124,558 /
3,647,954 / 4,426,408 / 698,204; exact-root Linux uses 126,378 / 3,649,774 /
4,428,228 / 586,282. The canonical manifest has 915 regions, and canonical package
ownership is 125,327 source, 88,020 generated, and 4,213,061 opaque bytes.

The complete unchanged BSD-3-Clause terms remain at
`third_party/littlefs/LICENSE.md`. The source leaf contains no filesystem
object or G2 block-device path. The broader library and hardware ports remain
outside this reuse, and qualification authorizes no signing, flashing,
filesystem format or erase, or hardware operation.

## Preceding bounded dual-image littlefs tag-chunk production reuse

The authenticated littlefs v2.10.1 source-equivalent snapshot now also
supplies the shared altered BSD-3-Clause
`components/shared/littlefs/runtime_littlefs_tag_chunk.c` adaptation. Its
exact upstream source authority is `lfs.c[10514:10607]`, 93 bytes, SHA-256
`406b74c2d10482c959cf1048d9589d00d8b416ee4661203bd339144baa74cd09`;
the independently pinned 32-bit tag typedef is `lfs.c[9602:9629]`, SHA-256
`cb4dcd6212b1a269371d86dddf98ed74853e2eb43753c5d8f8659abbca167ce2`.
This proves source-equivalent behavior, not Even Realities' exact historical
checkout.

Focused disassembly contributes only the identical six-byte stock spans,
four-caller topology in each image, scalar ABI, and entry-replacement
addresses. The six-byte source leaf is provider- and relocation-free. It is
registered atomically in Apollo main and the bootloader, where complete
`B.W`-plus-NOP patches replace `[0x004CAEA0,0x004CAEA6)` and
`[0x00410BA8,0x00410BAE)`.

Apple main/boot overlay/component pins are 124,566/3,647,962 and
628/149,228 bytes; the 4,426,422-byte package hashes to
`441bc7dd753518464afa0ac8ab84c26aedcd18228dbab3427d8c20ff66a8d914`.
Exact-root Linux uses 126,386/3,649,782 and 628/149,228 bytes; its
4,428,242-byte package hashes to
`8f62cf0ffb7d861ca1e6f9881e3221557f0da4640491489c7468129c5d57f1ba`.
Complete hashes are pinned in the overlay registries and canonical manifest.

The unchanged BSD-3-Clause terms remain at
`third_party/littlefs/LICENSE.md`. This bounded scalar reuse does not import
the broad library, a block-device port, or any format/erase path. All
qualification was offline; no image was signed or flashed and no hardware was
operated.

## Preceding bounded dual-image littlefs tag-size production reuse

At that milestone the atomic reuse boundary selected the bounded adaptation
`components/shared/littlefs/runtime_littlefs_tag_size.c` and its header for
both Apollo images. Its source authority is the exact 87-byte private
definition at authenticated littlefs v2.10.1 `lfs.c[10793:10880]`, SHA-256
`9df85bc43ca9f90ef58c425c5fd9bbbbf53585093be5fad0cc580fc88814ea5c`,
commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`. The exact behavior is the
pure unsigned mask `tag & 0x000003ff`; the source-equivalent selection is not
proof of Even Realities' historical checkout.

Focused disassembly contributes only the byte-identical stock spans
`[0x004CAEB8,0x004CAEBE)` and `[0x00410BC0,0x00410BC6)`, their complete
15/14 direct-caller topology, and the recovered 32-bit scalar ABI. Apple
production text is provider- and relocation-free. Final placements, redirects,
artifact identities, manifest ownership, and exact-root Linux parity are
closed in the explicit build-evidence ledgers; the settled tag-ID reuse is the
preceding production boundary.

The unchanged BSD-3-Clause terms remain at
`third_party/littlefs/LICENSE.md`. This promotion imports neither the broad
library nor a block-device, mount, format, program, or erase path, and it
authorizes no signing, flashing, reset, boot, or hardware operation.

## Preceding bounded nanopb `pb_read` production reuse

At this preceding milestone the authenticated nanopb compatibility snapshot
supplied a sixth bounded altered production adaptation,
`components/shared/nanopb/runtime_nanopb_read.c` and `.h`. Their 2,874/2,059
bytes hash to
`65f8f3cb92729e98f82f1254b18ba969cdd8a57c7ac74e8713137b5585102453`
and `aaa9847151722953498958687e91d55dc0b18cc9a60318b4f754110c66a443d6`.
The exact upstream 814-byte `pb_read` definition is byte-identical in
authenticated nanopb 0.4.7, 0.4.8, and selected compatibility baseline 0.4.9
commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`; this does not establish
Even Realities' historical point release.

Focused disassembly supplies the complete stock span
`[0x0048F3BE,0x0048F454)`, its two internal recursive calls and 13 external
callers, the recovered 16-byte stream ABI, and complete ingress topology. The
stock entry redirected to the source-owned 158-byte leaf without changing
any caller address. No external branch or stored pointer enters the interior.
At that milestone three binary-owned dependencies remained explicit: the
private `buf_read` odd Thumb identity at `0x0048F3A5`, end-of-stream string at
`0x00787C70`, and I/O error string at `0x0078B690`. The subsequent private
read-pair and constructor promotions source-own the private helper bodies and
constructor while preserving that callback identity; only the two error
strings and copy helper remain explicit binary seams.

Apple places the leaf at `0x007B2A04`; exact-root Linux uses `0x007B3124`
after two alignment bytes. At that milestone the canonical manifest had 941
main and 67 boot regions, and packages hashed to
`f861d049873d497b44f25b265bad4a6ba9409aef3ff3abb4ed6abc1a031a4804`
at 4,426,688 bytes and
`0269400751d0ffa0f58c5cf8658b4dbc6e8af90a875d13bc2e5f684a436d26a9`
at 4,428,512 bytes. No bootloader homolog was authenticated. Qualification was
offline; no image was signed or flashed and no hardware was operated. The
preceding nine-function boundary follows immediately below.

## Preceding bounded nanopb stream-constructor reuse milestone

At that preceding milestone, the nanopb snapshot authorized nine bounded
production functions. The then-new
`pb_istream_from_buffer` adaptation used tag `nanopb-0.4.9`, commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`, and the exact upstream
definition `pb_decode.c[5114:5692]` under Zlib. The source-equivalent
0.4.7--0.4.9 range did not identify the vendor checkout. Focused disassembly
supplied the complete 28-byte stock span, its 30 callers, the 16-byte stream
ABI, and callback identity `0x0048F3A5`. No bootloader homolog or broad nanopb
translation unit was included. Apple/Linux packages at that milestone were
4,426,806 / `062eaf5a7f301022f97162f4517d15248276e80c11a27b7c9f9b0e4cda4fbef2`
and
4,428,632 / `c9f09923a8c97706f32aed0c0c7db455a9aed01eff06d968cf8be81ee552793f`.
The constructor qualification is recorded in
`docs/research/nanopb-istream-from-buffer-source-audit.md`; no hardware
operation is authorized.

## Preceding bounded nanopb signed-varint reuse

At that preceding signed-varint milestone, nanopb's production allowlist
contained ten bounded altered functions.
The new `open_cfw_nanopb_decode_svarint` leaf selects the authenticated
nanopb 0.4.9 `pb_decode.c[42912:43210]` definition (298 bytes,
`df1caa71053163bdefaea7d6b19bdc72f10c63f09430003b88f10fb7dac3ff6e`)
as a compatibility baseline. Its only executable relocation targets the
already source-owned `open_cfw_nanopb_decode_varint`, so no opaque nanopb
provider remains in this leaf's dependency closure. The full 64-byte stock
span is generated ownership and the Apple manifest contains 951 regions.
This does not prove the vendor checkout; pristine nanopb translation units
remain unregistered. Exact-root Linux Clang 22.1.8 emits a 50-byte leaf at
`0x007B323C`, linked directly to the source-owned unsigned decoder, and pins
the overlay/component/package at 126,794 / 3,650,190 / 4,428,684 bytes.

## Preceding bounded nanopb varint32 reuse

At the preceding varint32 milestone the production allowlist contained twelve
independently audited altered functions; the current skip-string section below
brings it to thirteen. Private `pb_decode_varint32_eof` selects upstream bytes
`[5762,7483)` and public `pb_decode_varint32` selects `[7485,7617)` from the
authenticated 0.4.9 snapshot. One altered C/H pair supplies two separately
owned Apple text leaves and a private literal closure; no broad pristine
translation unit is registered. Version 0.4.9 is a compatibility baseline,
not proof of the vendor point release. No bootloader homolog was found.
Exact-root Linux independently pins the leaves at offsets 126,796 and 127,036
and the final overlay/component/package at 127,046 / 3,650,442 / 4,428,936.

## Current bounded nanopb skip-string reuse

The production allowlist now contains thirteen independently audited altered
functions. `pb_skip_string` selects the byte-identical authenticated
0.4.7--0.4.9 definition, replaces `[0x0048F64C,0x0048F66C)`, and calls only
source-owned varint32/read providers. Apple/Linux place identical 34-byte text
at `0x007B2C4C`/`0x007B336C` and close at
`125258/3648654/4427148` / `127082/3650478/4428972`. This is compatibility
reuse, not proof of the vendor checkout, bootloader reuse, or hardware
execution.
