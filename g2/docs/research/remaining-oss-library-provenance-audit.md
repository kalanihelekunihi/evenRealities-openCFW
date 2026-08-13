# Remaining Apollo-main open-source provenance and source-close audit

Status: research-only provenance and prioritization audit, with the later
production timeout-check, unordered-event-removal, and queue-reset results
recorded as current-state updates; the audit itself performed no hardware
action

> Historical priority note: several ranked actions below have since been
> completed or superseded. Current dependency disposition is authoritative in
> [`third-party-utility-gap-priority.md`](third-party-utility-gap-priority.md).
> In particular, the FreeType configuration/allocator/face-destruction work is
> closed, and whole-image evidence proves that no conventional linked
> `FT_Done_FreeType` entry can be assigned safely.

Scope: opaque or retained-compatibility executable regions in the official G2
`2.2.6.10` Apollo-main image. Addresses are installed run addresses and ranges
are end-exclusive. The official OTA's 32-byte wrapper is removed before
mapping its payload at `0x00438000`.

## Decision

The remaining Apollo-main image is not one undifferentiated decompilation
target. Twelve high-confidence source-close clusters can use released source
as their algorithmic authority. Focused disassembly is still necessary, but
only to recover or verify G2 configuration, fixed-address state, object ABI,
port callbacks, caller topology, and safe placement.

The strongest immediate sequence is:

1. classify the unreachable stock TLSF spans as retired compatibility bytes;
2. promote the complete isolated FreeRTOS reset-next, scheduler-port, tick,
   and `xTaskResumeAll` candidates together as one scheduler cluster;
3. retain the now-promoted FreeRTOS timeout, unordered-event-removal, and
   queue-reset functions under their authenticated dual-profile gates;
4. source the main EasyLogger output and hexdump functions using explicit G2
   sink and formatter ports;
5. vendor the exact FreeType 2.9.1 release now, but integrate it only after its
   allocator/lifecycle boundary has an oracle;
6. admit littlefs read-only APIs only after a golden external-flash capture;
   and
7. validate the verified FlashDB 2.1.1 snapshot and completed fail-closed
   read-only port against a golden capture before any production mount.

This audit deliberately rejects name-only matches. LVGL, nanopb, TinyFrame,
Cordio, CmBacktrace, FreeRTOS-Plus-CLI, and the generic ring buffer are not
assigned a new exact revision below unless the binary contains a discriminator
stronger than a path or family name.

## Evidence and confidence rules

### Official binary

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Installed payload at `0x00438000` | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |

The current core-source manifest still accounts for 3,438,528 Apollo-main
base bytes as opaque. Some are active first-party code, some are data or
padding, and some (notably the stock TLSF closure) are no longer reachable
through the production entry graph.

### Confidence vocabulary

- **A / authenticated local source**: the local snapshot verifier pins the
  official repository identity, source bytes, and license; the stock symbol is
  selected by instruction-level behavior and configuration evidence.
- **A- / authenticated source, integration closure incomplete**: the library
  and source symbol are certain, but a complete target-body oracle, outgoing
  dependency closure, or entry/reference scan remains before production.
- **B / exact release identity, snapshot not yet vendored**: the binary fixes
  the release and relevant source symbols, but openCFW does not yet have a
  local byte-pinned source snapshot and verifier.
- **Rejected**: a family or file name is real, but no single upstream revision
  is justified.

A source-equivalent commit set is acceptable when all members have identical
compiled inputs; it is not rewritten as a false historical-checkout claim.

### Authenticated source matrix

| Library | Defensible source identity | Relevant source | License | Qualification |
|---|---|---|---|---|
| FreeRTOS-Kernel | tag `V10.5.1`; tag object `d7b40dbed508c305c2a32ccf3982045ec9ba8734`; commit `def7d2df2b0506d3d249334974f51e427c17a41c`; tree `7496dfa815c3cea2f45a090c6e92d113f494b930` | `tasks.c`, `queue.c`, `portable/IAR/ARM_CM55_NTZ/non_secure/port.c` | MIT | Exact local authenticated release; selected G2 port is NTZ/non-secure, MPU off, FPU on |
| TLSF | source-equivalent range `a1f743ffac0305408b39e791e0ffb45f6d9bc777...deff9ab509341f264addbd3c8ada533678591905`; selected snapshot `deff9ab` | `tlsf.c`, `tlsf.h` | BSD-3-Clause | Local authenticated source-equivalent snapshot; signed/unsigned bitmap-literal change is target-equivalent for valid shifts |
| EasyLogger | source-equivalent core set `cd93d9c768415f4b7279f2d3ef2366ce15ea087c`, `34cc1717825c799979a1b4b3739be1e5668a7322`, and selected `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` | `easylogger/src/elog.c`, `elog_utils.c`, headers | MIT | Local authenticated source blobs are identical across the three commits; G2 `elog_async_api.c` is downstream, not upstream |
| littlefs | source-equivalent official release `v2.10.1`, commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`, tree `06dd0162169d3cb550cd24a3e34d0e4d02983ad3` | `lfs.c`, `lfs.h`, `lfs_util.c`, `lfs_util.h` | BSD-3-Clause | Local authenticated source-equivalent release selected by the complete 38-assertion fingerprint |
| FlashDB | lightweight tag/commit `2.1.1` / `714d6159e7e6afb267a3953756abca445c350e61`, tree `3410ae8111e4dbf6ae22d995bfcf37274abf89ea` | `src/fdb.c`, `src/fdb_kvdb.c`, `src/fdb_utils.c`, headers, and generic FAL core | Apache-2.0 | Exact 14-file snapshot and recovered configuration/FAL ABI are verified offline; no production registration |
| FreeType | tag object `VER-2-9-1` at `ad55868d889b6ba8d2aed846b4b4b460f8a83e42`, peeled commit `86bc8a95056c97a810986434a3f268cbe67f2902` | 297 selected header/module source files | FreeType License | Exact `2.9.1` numeric version, ten-module table, signed tag/commit chain, and production-excluded local snapshot are verified offline |

FlashDB and FreeType now have the same byte-count, Git-object, SHA-256,
license, official-image, and fail-closed file-set verification discipline as
the earlier snapshots; both remain production-excluded.

## Ranked source-close candidates

| Rank | Cluster | Stock range / entry | Stock bytes | Direct callers | Confidence | Immediate disposition |
|---:|---|---|---:|---:|---|---|
| 1 | Retired stock TLSF internals, `tlsf_add_pool`, and `tlsf_create` | `[0x004CFD18,0x004D0580)`, `[0x004D0608,0x004D06AC)`, `[0x004D06B4,0x004D06D6)` | 2,152 + 164 + 34 | zero active external callers after the nine public redirects | A | Reclassify as inactive authenticated compatibility bytes; reclaim only after the stock-closure reference proof is made a fail-closed manifest gate |
| 2 | `prvResetNextTaskUnblockTime` | `[0x00455876,0x0045589C)` | 38 | 6 | A | Promote the existing isolated candidate; no algorithm/configuration gap remains |
| 3 | `vPortYield`, `vPortEnterCritical`, `vPortExitCritical` | `[0x004420BC,0x00442114)` | 88 | 21 / 45 / 51 | A | Promote the existing isolated trio and bind to the source-owned BASEPRI mask pair |
| 4 | `xTaskIncrementTick` | `[0x0045504C,0x0045519E)` | 338 | 3 | A | Promote the existing differential-tested candidate after rank 2 and explicit relocation pins |
| 5 | `xTaskResumeAll` | `[0x00454DCC,0x00454EFE)` | 306 | 21 | A | Promote with ranks 2-4 as one scheduler cluster; candidate/oracle, topology, fixed state, and all six outgoing relocations are complete |
| 6 | `vTaskRemoveFromUnorderedEventList`; `xTaskCheckForTimeOut` | `[0x0045547C,0x00455556)`; `[0x00455566,0x004555E6)` | 218 + 128 promoted | 1 / 3 redirected | A | Complete: both are production source-owned and dual-profile qualified |
| 7 | `xQueueGenericReset` | `[0x00441516,0x004415CA)` | 180 promoted | 1 redirected | A | Complete: authenticated `queue.c` algorithm with source-owned event-list dependencies |
| 8 | EasyLogger `elog_output` | `[0x0043D574,0x0043D976)` | 1,026 | 6,239 | A- | Use a bounded upstream-derived G2 adapter, not pristine `elog.c` unchanged |
| 9 | EasyLogger `elog_hexdump` | `[0x0043DACC,0x0043DC88)` | 444 | 41 | A- | Reuse upstream function with the source helpers, G2 async sink, and formatter seam made explicit |
| 10 | littlefs public/read-only API cluster | `[0x004CFA58,0x004CFD0C)` | 692 | not yet entry-enumerated | A- | Compile pristine v2.10.1 core/config as an oracle now; production read-only admission waits for a golden flash capture |
| 11 | FlashDB KVDB initializer/core | `[0x005453FE,0x0054552C)` and `[0x00585BC8,0x00585C46)` | 302 + 126 | 2 / 1 | A- identity/configuration, mount-policy blocked | The selected 2.1.1 KVDB/FAL closure and fail-closed read-only port are verified production-excluded; all 21 defaults and the boot-counter lifecycle are resolved, while production mount still waits for a golden capture, non-destructive policy, and schema semantics; writes/erases remain denied |
| 12 | FreeType initialization/module cluster | entries `0x005242FC`, `0x0052431C`, `0x0052729C`, `0x005274B2` | 28, 56, preliminary 278, 68 | 1 each | B | Vendor exact 2.9.1 and selected modules; integrate only after target-boundary and allocator/lifecycle closure |

The ranks are production-risk order, not byte-yield order. FreeType offers a
large eventual opaque-byte reduction, but the small scheduler leaves provide
much stronger first integration steps.

## Detailed findings and focused-disassembly questions

### 1. TLSF: stop treating dead released code as an unknown algorithm

The complete stock TLSF closure is `[0x004CFD18,0x004D09B4)`, 3,228 bytes,
SHA-256
`007d8ac1f0e118281a07f6bde1049256800894d9684dff16e1d316f1ea4a7f9d`.
All nine externally reached public entries already redirect to the complete
vendored TLSF implementation. The source translation unit exports its own
`tlsf_create`, `tlsf_add_pool`, allocator operations, and local
`default_walker`, `block_insert`, `block_locate_free`, `block_merge_next`,
`block_prepare_used`, `block_remove`, and `block_split` helpers.

The remaining executable compatibility spans are:

| Role | Range | Bytes | SHA-256 |
|---|---|---:|---|
| Internal implementation prefix/helpers | `[0x004CFD18,0x004D0580)` | 2,152 | `7ce86f11408d3e818c3e27475d31b69ac0f05b6a00410114aed0d16f073ec75d` |
| Stock `tlsf_add_pool` | `[0x004D0608,0x004D06AC)` | 164 | `a383735dedc429f082e8b1f26c87e57089f165bc209dfade1b3c727f3a9ab639` |
| Stock `tlsf_create` | `[0x004D06B4,0x004D06D6)` | 34 | `2847a68f388ab99195397a78a6ce47d608c433c908b78d228294639a42bb3df0` |

The existing closure scan finds 157 calls into the original TLSF closure:
133 stock-internal and 24 external calls to the nine now-redirected public
entries. It finds no external branch into an internal body. The sole genuine
stored code pointer is the stock-internal literal at `0x004D0994` pointing to
the stock `default_walker` at `0x004D0555`; both ends are dead after the public
redirects.

No additional algorithm decompilation is warranted. The remaining work is an
ownership proof: make the no-active-entry/no-external-pointer result a build
gate, mark the bytes as authenticated retired stock rather than unknown
opaque functionality, and reclaim or overwrite them only if the packaging
layout benefits.

### 2-5. FreeRTOS scheduler closure

All four scheduler candidates come from authenticated `tasks.c` or the
selected NTZ `port.c`.

#### `prvResetNextTaskUnblockTime`

The 38-byte stock leaf hashes to
`a789916ee424c824c5c5f2302e62e4a861f0fa1289917d9c0e095947bce82598`.
Its callers are `0x00454B0A`, `0x00454EBE`, `0x0045509A`, `0x00455420`,
`0x004554D0`, and `0x00455D9A`. Focused disassembly has already fixed:

- `pxDelayedTaskList` at `0x20074A24`;
- `xNextTaskUnblockTime` at `0x20074A50`;
- 32-bit `TickType_t`, `portMAX_DELAY=UINT32_MAX`;
- 20-byte `List_t` and the head-value offsets; and
- the required second volatile delayed-list-pointer read on the nonempty path.

Apple clang 21 and Linux clang 22.1.8 emit the same relocation-free 32-byte
candidate. Promotion needs placement, redirect, manifest, and aggregate hash
pins, not more reverse engineering.

#### Scheduler-port trio

The contiguous 88 bytes hash to
`ba9b86be2e0caa3b3bb32b45a7f1f4730fc94f6ad80153d470de5cb6e7a9b228`.
The exact subranges and hashes are already pinned by
`freertos-scheduler-port-trio-source-boundary-audit.md`. The recovered port
choices are `ICSR=0xE000ED04`, PendSV-set bit 28, critical nesting word
`0x2000309C`, `portCRITICAL_NESTING_IN_TCB=0`, active assertions, and the
source-owned `BASEPRI=0x30` mask pair.

There is no remaining parameter ambiguity. Production review should instead
focus on preserving volatile nesting rereads and barrier order, binding the
three call relocations to the source mask pair, and measuring the redirect
latency at the 117 aggregate callers.

#### `xTaskIncrementTick`

The 338-byte stock body hashes to
`438ad4e9e1a7b439671463b2bbfd13616ebb6de32bd2aad53b802d31f11cc050`.
Its callers are the SysTick path at `0x0044211C`, `xTaskResumeAll` at
`0x00454ECC`, and the catch-up path at `0x00456408`. Its only calls are the
source mask assertion seam and `prvResetNextTaskUnblockTime`.

The isolated implementation has a pristine `tasks.c`/`list.c` oracle and
closes the relevant build configuration: preemption and time slicing on,
tick hook off, nonoptimized numeric ready priority, 32-bit ticks, 56
priorities, mini-list layout, and no list integrity words. Apple and Linux
candidate tests pass. Production should promote it only after rank 2 is a
source provider and profile-specific relocation/placement pins are recorded.

#### `xTaskResumeAll`

The retained 306-byte body hashes to
`548e05e1f8a2f498372dd1f4eb7c6536e093dbbfdb82fbe8f9b54231cedc8a09`
and has 21 direct `BL` callers. A fresh complete-image wide-branch scan
reproduces that count and finds no `B.W` caller. The dedicated closure audit
finds no interior or stored-pointer entry and confirms all six outgoing calls.

The isolated candidate is now complete. Its implementation is
`components/shared/freertos/runtime_freertos_task_resume_all.c` (6,262 bytes,
SHA-256
`455b29e4eaec27451ad5ed24953583291659201b7fbd2da5c330f6e9da081dd5`)
with `components/shared/freertos/runtime_freertos_task_resume_all.h` as its
source boundary header (10,625 bytes, SHA-256
`9eaadd2e390b7300e90140a1e114481eaac2135c9830d320a2a8653f213c1045`).
The candidate pins the stock ABI and recovered state at:

- ready lists `0x2006A49C`;
- pending ready list `0x20073D24`;
- current TCB `0x20074A20`, current task count `0x20074A30`, and top ready
  priority `0x20074A38`; and
- pended ticks `0x20074A40`, yield pending `0x20074A44`, and scheduler
  suspended `0x20074A58`.

Independent Apple and exact-root Linux builds each pass all seven candidate
tests. The Apple target is 292 bytes with SHA-256
`8b8a8bde3a875d1b4f6b28d3aa0e4bedf2c80f80d0c0c380614e3e1a8c4216a3`;
the Linux target is also 292 bytes with SHA-256
`7fb0e6bab36ed324d800362e1d1f85e29b8b7924e6cbe994600ebe998fe025a6`.
Both have the same six `R_ARM_THM_CALL` relocations:

- `+0x012` `open_cfw_freertos_port_enter_critical`;
- `+0x022` `open_cfw_freertos_port_exit_critical`;
- `+0x02E` `ulSetInterruptMask`;
- `+0x0EE` `open_cfw_freertos_task_reset_next_task_unblock_time`;
- `+0x0FC` `open_cfw_freertos_task_increment_tick`; and
- `+0x11C` `open_cfw_freertos_port_yield`.

The candidate host fixture is 17,310 bytes with SHA-256
`f537cd78715fb583e4893786f4cbbfe922e0f0e9f98016f713e336ba93dd14fd`;
the pristine upstream oracle is 4,228 bytes with SHA-256
`5729ede872fcc65af90e5721fd3257e710d75eee73ccb77049409d9874122713`.
The hashes and the seven-test semantic matrix are pinned by
`tests.test_runtime_freertos_task_resume_all` and
`docs/research/freertos-task-resume-all-source-boundary-audit.md`.

Promote this only with ranks 2-4 as the scheduler cluster. Production work
remaining is cluster linking, overlay-space allocation, redirects, and
aggregate manifest pins; no algorithm, ABI, fixed-state, caller-topology, or
candidate-oracle gap remains.

### 6. Completed FreeRTOS unordered-event removal and timeout check

The exact bodies are:

| Function | Range | Bytes | SHA-256 | Callers |
|---|---|---:|---|---|
| `vTaskRemoveFromUnorderedEventList` | `[0x0045547C,0x00455556)` | 218 | `aa14475cf28218296c4fd829c02080fc017a5fe137f476de47e747f1e920e33b` | `0x0047EE02` |
| `xTaskCheckForTimeOut` | `[0x00455566,0x004555E6)` | 128 | `83a983995a285b3257a1213bdbe3fa0542bae0c9296a88fd8b22c1388abdf72c` | `0x004418C0`, `0x00441BCA`, `0x00441CF6` |

The 16-byte `vTaskInternalSetTimeOutState` leaf between them is already
production source. The public `vTaskSetTimeOutState` function appears before
that leaf in authenticated `tasks.c`, but it has no corresponding stock body:
the two identified neighbors abut the internal leaf exactly, and all three
queue setup calls go directly to the internal leaf. It was therefore
dead-stripped and is not a decompilation target.

Production now uses authenticated `tasks.c` directly for the unordered-event
function. Focused disassembly pinned the list/TCB ABI, assertion seams,
ready-list insertion, and its call to the source-owned reset-next leaf. The
timeout-check questions listed by the original audit are also settled:
`INCLUDE_vTaskSuspend=1`, `portMAX_DELAY=UINT32_MAX`,
`INCLUDE_xTaskAbortDelay=0`, the volatile overflow/tick ordering, timeout
update behavior, and critical-section providers are all pinned. Its stock
entry redirects to the authenticated source leaf in production.

### 7. Completed FreeRTOS `xQueueGenericReset`

The 180-byte stock function hashes to
`e5b7c5e487374e7966b8f2febb8aa1b804efa516c92f9e436a369ec5df100ad8`.
Its sole direct entry caller is `prvInitialiseNewQueue` at `0x004416AE`; the
generic queue creators are already source-owned and reach that initializer.

The exact `queue.c` algorithm is now production-integrated. Focused
disassembly pinned:

- the 80-byte `Queue_t` reset offsets and queue lock bytes;
- new-queue versus existing-queue behavior;
- initialization of both event lists through source `vListInitialise`;
- the existing-queue `xTaskRemoveFromEventList` call and conditional yield;
- active assertion/trace/coverage branches; and
- complete entry/interior/stored-pointer closure.

This removes the source-to-stock dependency from queue creation without
importing pristine `queue.c` wholesale.

### 8-9. EasyLogger output cluster

The local EasyLogger core source is authenticated. The remaining two complete
functions are not proprietary formatting algorithms.

#### `elog_output`

The complete 1,026-byte body hashes to
`d7c5fd89997fc677ecce543af7c33cd08614b832a47602f1fd895bb7ab45f90c`.
All 6,239 direct callers land on the entry; existing audits found no alternate
entry, interior branch, or stored function pointer.

The ordinary filter/format algorithm matches upstream, but pristine source
cannot be linked unchanged. The G2 adaptation must preserve:

- an early `IPSR != 0` silent return before every argument/state access;
- fixed logger `0x20070BE8` and 1,024-byte buffer `0x2006BD30`;
- the source-owned logger filters, locks, helpers, strings, and color tables;
- G2 assertion hook/fail-stop policy;
- downstream argument order `(buffer, length, level)`, not upstream
  `(level, buffer, length)`; and
- the stock IAR `vsnprintf` seam until the entire 6,239-caller format corpus
  proves the source mpaland formatter compatible.

Focused disassembly has already answered these parameters. What remains is a
source candidate/oracle, exact target relocations, and package promotion.

#### `elog_hexdump`

The complete 444-byte body hashes to
`782cb65686dde396075abdd4f7c6a168bbf64962498d97446ab35e0e1670536c`.
A fresh complete-image wide-branch scan finds 41 direct `BL` callers and no
`B.W` caller. Unlike G2 `elog_output`, the stock hexdump begins immediately
with buffer initialization and logger gates; it has no early IPSR check. Do
not add one speculatively.

The upstream `elog_hexdump(name,width,buf,size)` algorithm in `elog.c` is the
source authority. Focused disassembly must still pin the exact outgoing
formatter calls, `uint16_t` wrap behavior for offset/size, width-zero policy,
shared buffer locking, G2 async sink argument order, and interior/stored
references. The source-owned `elog_strcpy`, lock/unlock, and length helpers
should be linked directly.

### 10. littlefs read-only cluster

The Apollo-main public veneer cluster is 692 bytes with SHA-256
`8fac514f80a47d951c7d25b2912e10d20054e527113767caa8570ab0b346ea3d`.
It contains `lfs_format`, mount/unmount, remove/rename/stat, file lifecycle and
I/O, mkdir, and directory lifecycle/read APIs. The released algorithms are
available from authenticated v2.10.1 `lfs.c`; numerous private leaves are
already production source.

The exact G2 `lfs_config` is substantially recovered: 16-byte reads,
256-byte programs, 4-KiB blocks, 3,008 blocks, 500 block cycles, 4-KiB cache,
256-byte lookahead, compact threshold zero, dynamic allocation, no
thread-safe hooks, no multiversion support, and external range
`0x01400000...0x01FC0000`.

Algorithm decompilation is unnecessary. The production gate is data and port
validation:

1. enumerate every public entry, caller, interior transfer, and stored
   pointer rather than redirecting the aggregate range blindly;
2. capture and hash the complete external flash without mutation;
3. mount a copy read-only with the authenticated source and compare
   superblock, disk version, tree, and contents;
4. admit mount/stat/read/directory-read paths first; and
5. keep format/program/erase and stock auto-format recovery unreachable until
   disposable-copy power-loss tests pass.

### 11. FlashDB 2.1.1

The in-image `2.1.1` literal, stock diagnostics, and initializer call graph
make the upstream identity exact. The two pinned anchors are:

| Function | Range | Bytes | SHA-256 | Callers |
|---|---|---:|---|---|
| `fdb_kvdb_init` | `[0x005453FE,0x0054552C)` | 302 | `c40571f5f8710c17ca10a713ec7dd6fa7a32da2fac0e2c1571806ff33cd03aad` | `0x004D9776`, `0x005107F0` |
| `_fdb_init_ex` | `[0x00585BC8,0x00585C46)` | 126 | `dcf189562e2516bdc6a47f4975b16f01c15d0250990e2d51745f14cb604ce4aa` | `0x00545520` |

The fail-closed analyzer now proves FAL-backed KVDB mode, no live/retained
TSDB subsystem or file mode, `FDB_WRITE_GRAN=1`, 4-KiB sectors, 64-entry KV
and sector caches, no KV auto
update, a short-enum `0x8AC` object ABI, and corrected bindings
`sysenv@kvdb` / `factory@NVdb`. The two FAL partitions and single `norflash`
device record, including callback slots and geometry, are authenticated.
`+0x34/+0x38` are partition offset/length fields, not `fdb_db` fields.
The original `FDB_USING_TSDB` macro state is not statically proven; the
minimal recovered source configuration omits it. Seven reconstructed Git
trees prove the selected 14 paths/blobs belong to the pinned commit.

The default tables, mutex, driver callbacks, return-value mismatch, reset
magic, and stock default-recovery paths are now statically recovered. The
production-excluded source port differentially matches upstream FAL reads,
uses the shared CMSIS mutex, maps every nonzero MX25 result to `-1`, and
unconditionally denies write and erase. Keep the selected official 14-file
2.1.1 KVDB/FAL closure and this port production-excluded until a golden
capture proves read-only parity and a non-destructive mount policy prevents
stock default/reset behavior; higher-level schema semantics remain unresolved.
The system-KVDB object now proves that reset zeroes `kvbooCount` and that
initialization reads, increments, and persists it before running eleven closed
record migrations.

### 12. FreeType 2.9.1

FreeType is the largest newly eligible exact-release import. The numeric
version is written directly by the stock `FT_New_Library` body: major `2`,
minor `9`, patch `1`. This is corroborated by the `cff-load` service and the
pre-2.13 autofit `warping` property. The official `VER-2-9-1` tag resolves to
tag object `ad55868d889b6ba8d2aed846b4b4b460f8a83e42` and commit
`86bc8a95056c97a810986434a3f268cbe67f2902`.

The smallest initialization/module anchors are:

| Upstream symbol/file | Stock range or preliminary boundary | Bytes | SHA-256 | Sole caller |
|---|---|---:|---|---|
| `FT_Add_Default_Modules`, `src/base/ftinit.c` | `[0x005242FC,0x00524318)`; separate module-table literal at `[0x00524318,0x0052431C)` | 28 | `32e95da285f105bf01c667f02c9d4ff2631fbf393b7f3876eb7264f30528b47f` | `0x00524346` |
| `FT_Init_FreeType`, `src/base/ftinit.c` | `[0x0052431C,0x00524354)` | 56 | `b5b7601a9be9efc68a5b0740025aeb715cd62d308204d546d7942f67eac57ba2` | `0x004B1C2E` |
| `FT_Add_Module`, `src/base/ftobjs.c` | preliminary `[0x0052729C,0x005273B2)`; end/reference closure not yet production-grade | 278 | `c9f520d0d156b4408be50b39543c6d4eeb804eec2f081a5c6ef68e5e6af535e7` | `0x00524308` |
| `FT_New_Library`, `src/base/ftobjs.c` | `[0x005274B2,0x005274F6)` | 68 | `772b74ab537810e31ac97d836f318555b7fc20bdb0d574a5ef67b06b0975f0b7` | `0x00524332` |

The module table is already recovered and selects exactly ten classes:
autofitter, TrueType, CFF, psaux, psnames, pshinter, SFNT, smooth,
smooth-LCD, and smooth-LCDV. Vendor only their official 2.9.1 source closure,
not every FreeType driver. Preserve the dual-license choice and select one
license consistently in notices and distributions.

Later focused work resolves the TrueType default as v40-minimal, pins the GX
variation services and exact ten-module table, recovers the complete
`am_ftsystem.c` allocator seam, and closes `FT_Done_Face` exactly at
`[0x00526814,0x0052687E)`. A whole-image branch and pointer scan finds only
`FT_Init_FreeType` failure cleanup reaching `FT_Done_Memory`; the conventional
`FT_Done_FreeType` topology is absent, so assigning a stock entry would be a
guess rather than closure. Remaining work is optional configuration not
selected by surviving evidence, exact IAR details, production admission, and
comparison against the unavailable external G2 font assets.

The version and released algorithms should not be decompiled. Only the G2
port/configuration and any proven local patches require reconstruction.

## Explicitly rejected exact-version imports

| Family | Proven evidence | Why it is not an unequivocal single-source import yet |
|---|---|---|
| LVGL | eight mapped core bodies and configuration/ABI discriminators establish official-history compatibility interval `60d976c466e8…344c7c318047`; the released v9.3.0 tag is excluded as too new; 78 paths split into upstream core/FreeType wrappers, 11 Ambiq draw files, and separate vendor/Even glue; the seven-function / 638-byte private display port is source-owned | exact hybrid-tree and private display-port commits remain unresolved; first-party input/display managers and FreeType-system glue are not upstream LVGL, but there is no linked third-party input-port artifact; see `lvgl-version-recovery-audit.md` and `lvgl-ambiq-display-port-closure-audit.md` |
| nanopb | compact 0.4 descriptor ABI and pristine-upstream 0.4.7–0.4.9 compatibility band; authenticated reference builds exclude 0.4.4–0.4.6 but collide byte-for-byte for all three survivors; no malloc, 16-bit fields, 64-bit values, UTF-8 validation off | no surviving runtime discriminator or generated-source stamp separates 0.4.7, 0.4.8, and 0.4.9; see `nanopb-point-release-recovery-audit.md` |
| TinyFrame | full send topology and receive anchors establish MIT upstream source-equivalence interval `44ecc068…a29167a6`; ten retained source lines select exact core blobs introduced by `eb75483e`; SOF/width/endian/CRC, 1024-byte TX buffer, soft lock, request/response peer-ID policy, listener-timeout ABI, and transport seam are recovered | the exact historical checkout remains unresolved only because the core-identical `eb75483e…a29167a` interval is binary-unobservable. The G2 object/heap/logging/transport boundary and eight public entries are production source-owned under dual-profile pins; only hardware golden-frame validation remains; see `tinyframe-source-admission-boundary-audit.md` |
| Cordio / Packetcraft | definitive Cordio host and Ambiq FreeRTOS/HCI ports; ATT client-feature and eight-event DM state-machine bodies establish r20.05-or-later semantics; audited public source blobs are identical over r20.05–r20.05c | exact whole-tree identity remains unresolved because G2 carries Ambiq/local WSF and trace divergence and no authenticated AmbiqSuite 5.1.0 Cordio archive is available; see `cordio-version-recovery-audit.md` |
| CmBacktrace | definitive armink component; compatible unmodified-upstream interval `4abadfa0…73714489` on the untagged post-1.4.1 line advertising `1.4.2`; FreeRTOS/IAR/depth/name/M33-class configuration recovered; MIT license | no exact vendor commit inside the equivalence interval, exact CPU selector, or patched-English/custom-language choice survives; see `cmbacktrace-version-recovery-audit.md` |
| FreeRTOS-Plus-CLI | classic MIT V1.0.4-compatible core selected at `43defa56`/tree `12448758`, with exact two-file blobs unchanged through `1309654d`; complete interpreter boundary, descriptor/list/callback ABI, buffer limits, allocation behavior, and 76-descriptor census recovered | exact historical vendor commit is unresolved and G2 adds a unique blank-input suppression patch at `[0x005848CA,0x005848F4)`; vendor commands/handlers remain first-party; see `freertos-plus-cli-source-recovery-audit.md` |
| generic `ringBuffer` | retained `third_party\ringBuffer\ringbuffer.c` path | no author, license, version, or discriminating implementation signature |
| Even `fw_event_loop` | source path and diagnostics | first-party Even framework code, not a third-party library |

These components can still use released source as a behavioral comparator,
but they must not be labeled exact-version vendor imports yet.

## Cross-cutting LZ4 point-release status and parity gap

LZ4 is not ranked as remaining opaque because `LZ4_decompress_safe` is
already source-owned. Independent review against the official primary source
does **not**, however, support an exact historical point-release claim. The
official v1.9.4 commit `5ff83968` and its `lib/lz4.c` digest `b6a85fd8`
already contain all four markers previously attributed only to v1.10.0.
Official v1.10.0 commit `ebb370ca` refactors that logic and peels the first
iteration. The stock peeled control-flow graph favors v1.10.0, but a
compiler-optimized v1.9.4 build cannot be excluded. Treat v1.10.0 as an
authenticated source candidate, not proof of the historical checkout; the
point release remains unresolved.

The actionable production gap is semantic rather than provenance-only. For
the malformed input below, with output capacity 10:

```text
10 41 01 00 50 5a 5a 5a 5a 5a
```

the current hand decoder returns 10 and emits `AAAAAZZZZZ`. Both official
v1.9.4 and v1.10.0 `LZ4_decompress_safe` return `-2`, while the outer stock
adapter reports failure as 0. The hand decoder is missing the `MFLIMIT`
close-to-end rule and therefore accepts a block both official candidates and
stock reject. Differences between negative upstream error positions usually
clamp away at the outer adapter, but this acceptance-versus-rejection case
does not.

Before claiming the source replacement fully closed:

1. keep both official v1.9.4 and v1.10.0 as authenticated comparison
   candidates and label the historical point release unresolved;
2. repair or replace the hand decoder so the `MFLIMIT` close-to-end behavior
   matches the official implementations and stock adapter contract;
3. pin the vector above plus malformed, truncation, and overflow
   differentials against both official releases; and
4. reconcile `evenhub_lz4.c`, `overlay.json`, `NOTICE.md`, and `EVIDENCE.md`
   while retaining the BSD-2-Clause notice.

## Reproducible checks performed

The following read-only gates passed during this audit:

```text
third_party/freertos-kernel/verify_snapshot.py  OK
third_party/littlefs/verify_snapshot.py         OK
third_party/easylogger/verify_snapshot.py       OK
third_party/tlsf/verify_snapshot.py             OK

tests.test_runtime_freertos_reset_next_task_unblock_time  8/8 OK
tests.test_freertos_scheduler_port_trio_candidate         8/8 OK
tests.test_runtime_freertos_task_increment_tick          10/10 OK
tests.test_runtime_freertos_task_resume_all               7/7 OK (Apple)
tests.test_runtime_freertos_task_resume_all               7/7 OK (exact-root Linux)
combined FreeRTOS scheduler candidate chain              33/33 OK (Apple)
combined FreeRTOS scheduler candidate chain              33/33 OK (exact-root Linux)
third_party/flashdb/verify_snapshot.py                       OK
tests.test_flashdb_snapshot                               4/4 OK
tests.test_analyze_g2_flashdb                             5/5 OK
```

A fresh halfword-wide `BL`/`B.W` scan of the authenticated payload also
reproduced the caller counts and sites newly quoted here for
`xQueueGenericReset`, the unordered-event/timeout-check pair,
`xTaskResumeAll`, `elog_hexdump`, the
four FreeType anchors, and the two FlashDB anchors. It did not attempt to
replace a complete executable-code/reference analyzer for the candidates
that still require narrow-branch and stored-pointer closure.

## Limitations

- Proven source identity does not prove Even's historical checkout unless a
  surviving tag/commit discriminator says so.
- A library release identity does not prove every stock function is
  unmodified. Large clusters still require structural/source-oracle
  comparison and explicit downstream patch separation.
- Retired bytes remaining physically present in a package are not active
  binary dependencies, but they should not be counted as source-generated
  bytes. Classify them separately rather than inflating source coverage.
- Static/offline validation does not establish boot, interrupt latency,
  storage durability, display output, or power-loss behavior on G2 hardware.
- No hardware was connected, signed, flashed, reset, formatted, or erased.

## Current production update: `xTaskCheckForTimeOut`

The ranked audit's timeout-check half is no longer a candidate. The exact
FreeRTOS-Kernel V10.5.1 source now replaces all 128 stock bytes and appends a
136-byte relocation-free leaf plus two alignment bytes. Apple places it at
`[0x007B1440,0x007B14C8)`; Linux places it at
`[0x007B1B94,0x007B1C1C)`. The canonical package is 4,421,054 bytes with
SHA-256
`4fb13f64e81b8a6ef9bdf784ac38d5fc08ed03e4d310601a48bf4b395c20ab37`;
the qualified Linux package is 4,422,930 bytes with SHA-256
`22c0e367882b005c1b85ee40d138e596c423d5a6335b8d93bc5a68873323c3ab`.

The canonical component now retains 3,440,108 opaque bytes. Its manifest has
821 main regions and 884 whole-package regions, with 877 placed, two
unresolved, and five container-only. This production update does not change
the audit's hardware limitation: all qualification remained offline and no
device was connected, signed, flashed, reset, formatted, booted, or executed.

## Current production update: queue reset and unordered event removal

Ranks 6 and 7 are complete. Authenticated FreeRTOS-Kernel V10.5.1 source now
owns the complete 180-byte `xQueueGenericReset` and 218-byte
`vTaskRemoveFromUnorderedEventList` stock spans through full-span `B.W` plus
NOP-fill redirects. Apple appends relocation-free 172-byte and 214-byte
leaves after two alignment bytes; exact-root Linux appends 174-byte and
210-byte leaves separated by two alignment bytes.

| Profile | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 121,706 / `03dd692b55204fc36f67469ece0175e981b6281123a1b20b3db592ee2dd0b44c` | 3,645,102 / `ae123c6a119bfebd0420898aef590a9ba1fd7f7dc7da00b3d347f6573bba43ec` | 4,423,556 / `7cf86c7311b4684eb6d2fdd4f832989317c858733f8438dc01ee649fcd1cf250` |
| Linux Clang 22.1.8 | 123,558 / `f2c33def6131981c1a283968bc02bd55cde32536f4f33a7fa3cbf905d42693fc` | 3,646,954 / `5ff7dd5894b74573971912371f22d0b463c32552ea1037441e1de992a6a8d3b9` | 4,425,408 / `fe49c0d9830327a0fdd0e7815a147bb6b810e27b9a9277b3bbfe9021de247a75` |

Canonical package accounting is 122,488 source, 86,467 generated, and
4,214,601 opaque bytes; exact-root Linux is 124,397 source, 86,410 generated,
and the same 4,214,601 opaque bytes. The focused nine-test suite passes on
both profiles. No physical G2 was connected, signed, flashed, reset, booted,
or executed.
