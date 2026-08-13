# G2 FreeRTOS task-count source-boundary audit

Status: task-count getter and corrected adjacent tick-getter pair
source-integrated in the Apollo-main production overlay
Scope: official G2 package `2.2.6.10`, Apollo-main application; offline
analysis, host/target compilation, and subsequent source-overlay integration,
with no signing, flashing, or hardware access

## Result

Three adjacent high-confidence FreeRTOS-Kernel V10.5.1 source boundaries are
now production-integrated. The original subject is
`uxTaskGetNumberOfTasks`:

| Property | Recovered value |
|---|---|
| Official range | `0x00454F10...0x00454F15` |
| End-exclusive range | `[0x00454F10,0x00454F16)` |
| Size | 6 bytes |
| SHA-256 | `43e18c3d205509129b075a8eb8c2c70afde30da1b933ac72d2963813aea8cfec` |
| Upstream source | `third_party/freertos-kernel/tasks.c`, `uxTaskGetNumberOfTasks` |
| Direct callers | four `BL` sites |
| Stored entry/interior pointers | none |
| External branches into the interior | none |
| Calls made by the function | none |
| TCB fields read | none |
| Stock global seam | `uxCurrentNumberOfTasks` word at `0x20074A30` |
| Integrated target implementation | one 12-byte relocation-free Thumb leaf |

The complete official algorithm performs one volatile 32-bit load from
`uxCurrentNumberOfTasks` and returns it. Independent stock paths increment
the same word when adding a new task, decrement it for an immediate
non-current-task deletion, and decrement it during deferred idle-task
cleanup after self-deletion. The global identity is therefore proved by its
writers and not inferred only from function shape or address proximity.

The function is unconditional in pristine V10.5.1 `tasks.c`; there is no
unresolved `config*` or `INCLUDE_*` gate. It has no port call, critical
section, TCB layout, list layout, trace hook, or vendor structure seam. The
complete source-replacement boundary is unequivocal.

The production-integrated source is
`components/apollo_main/core_overlay/runtime_freertos_task_count.c`. It is
registered by the Apollo-main overlay, which redirects the complete
authenticated stock entry to it.

The corrected adjacent pair is also production-integrated:

| Function | Official span | Bytes | Shared seam |
|---|---|---:|---|
| `xTaskGetTickCount` | `[0x00454EFE,0x00454F06)` | 8 | `xTickCount` at `0x20074A34` |
| `xTaskGetTickCountFromISR` | `[0x00454F06,0x00454F10)` | 10 | `xTickCount` at `0x20074A34` |

Their aggregate stock SHA-256 is
`d0b93ff29439d26b92dcd56fd012a9dab842364f7c5f4b4f7f39a27ed8cfe077`.
The 3,412-byte MIT shared implementation
`components/shared/freertos/runtime_freertos_tick_count.c` has SHA-256
`948d1b2de6026adc7cf84a34a359c859c32126b3afcafe92c2347f5f7ab56363`;
its header hashes to
`adc4065b3504a7eacb2e29e2d357636917e2b690afc49b265689e36d66171dae`.

## Authoritative inputs

The reviewed official image is:

| Property | Value |
|---|---|
| File | `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` |
| Package bytes | `3,523,396` |
| Package SHA-256 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| OTA preamble | 32 bytes |
| Installed application bytes | `3,523,364` |
| Installed application SHA-256 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Application load address | `0x00438000` |

The source comparator is the authenticated FreeRTOS-Kernel V10.5.1
snapshot:

| Property | Value |
|---|---|
| Commit | `def7d2df2b0506d3d249334974f51e427c17a41c` |
| Tree | `7496dfa815c3cea2f45a090c6e92d113f494b930` |
| `tasks.c` bytes | `223,695` |
| `tasks.c` SHA-256 | `14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463` |
| `tasks.c` Git blob | `d97085d8736905c1eeb9d9e871c81e5970ee70ed` |

`third_party/freertos-kernel/verify_snapshot.py` authenticates the annotated
tag, peeled commit, tree, selected file blobs, and retained MIT license.

The adjacent tick-getter interpretation additionally depends on the following
authenticated source/configuration evidence:

| Input | Bytes | SHA-256 | Relevant authenticated claim |
|---|---:|---|---|
| `third_party/freertos-kernel/include/FreeRTOS.h` | 51,577 | `03e9c94aba57e3cf7f4f73bc2d3eb4a96ae38f3425eedb5450622ca286475a0b` | atomic tick macros compile the normal critical section away and the ISR mask acquire/release to `0`/no-op |
| `third_party/freertos-kernel/portable/IAR/ARM_CM55_NTZ/non_secure/portmacrocommon.h` | 12,636 | `c184e6b1727732bbdd0d4dd33b9af4ea25d13040620666123941fff464bffc99` | a non-16-bit configuration makes `TickType_t` `uint32_t` and defines `portTICK_TYPE_IS_ATOMIC=1` |
| recovered compile-closure `FreeRTOSConfig.h` | 5,184 | `537e12cd879b06d7748f9b0e177f6ad0e17cd176405945771580e6d9c8312889` | `configUSE_16_BIT_TICKS=0` |

The recovered configuration is at
`components/apollo_main/core_overlay/candidates/cmsis_freertos_constructors/FreeRTOSConfig.h`.
It explicitly does **not** claim to be a complete byte-identical vendor
`FreeRTOSConfig.h`; only the tick-width selection used here is asserted.
The official binary independently proves that selection by loading one
32-bit word in each getter. The official blob provenance record is itself
pinned at 1,438 bytes and SHA-256
`53c3819fb9cf9cc819861787a14fa84f6e084cf03396a3a5636718f8539f6809`;
it names the same package version, payload size, and payload digest shown
above.

## Exact stock-to-source proof

The complete official body is:

```text
00454F10  ldr     r0, [pc, #0x28C]  ; literal at 0x004551A0
00454F12  ldr     r0, [r0]           ; uxCurrentNumberOfTasks
00454F14  bx      lr
```

The official bytes are:

```text
a34800687047
```

For the narrow literal load, aligned architectural PC is `0x00454F14`.
Adding `0xA3 * 4` selects literal word `0x004551A0`, whose exact
little-endian value is `0x20074A30`. The second instruction performs one
32-bit load; the third returns it in AAPCS result register `r0`.

This maps one-to-one to the complete released V10.5.1 function:

```c
UBaseType_t uxTaskGetNumberOfTasks( void )
{
    return uxCurrentNumberOfTasks;
}
```

The neighboring boundaries are independently pinned:

| Range | Recovered content | Bytes | SHA-256 |
|---|---|---:|---|
| `[0x00454EFE,0x00454F06)` | `xTaskGetTickCount` leaf | 8 | `6dbb234e35fb86f883529c083fed0e1cabdca99d6647a95568ed1a5522310ac0` |
| `[0x00454F06,0x00454F10)` | `xTaskGetTickCountFromISR` leaf | 10 | `8fe0a4f494b20b340d1126b2da725919f86c53cc3c1cabf5031fffc03f6de63a` |
| `[0x00454F10,0x00454F16)` | `uxTaskGetNumberOfTasks` | 6 | `43e18c3d205509129b075a8eb8c2c70afde30da1b933ac72d2963813aea8cfec` |
| `[0x00454F16,0x00454F38)` | following `pcTaskGetName` function | 34 | `a25ace28ece3ca37f11da7e73945acb28f1f99d906203613e9856d2070c07817` |

There is no fall-through from either neighbor. The selected function owns
its terminal `bx lr` and contains no padding or literal data.

The two tick getters form an exact 18-byte closure
`[0x00454EFE,0x00454F10)` with bytes
`dff8ac08006870470020dff8a00800687047` and SHA-256
`d0b93ff29439d26b92dcd56fd012a9dab842364f7c5f4b4f7f39a27ed8cfe077`.
This closure is important: the earlier eight-byte
`[0x00454F08,0x00454F10)` interpretation omitted the leading
`movs r0,#0` at `0x00454F06` and incorrectly treated the second instruction
at `0x00454F08` as a possible entry.

## Authenticated adjacent tick-getter pair

### Exact bodies and shared global

The complete normal getter is:

```text
00454EFE  ldr.w   r0, [pc, #0x8AC]  ; literal at 0x004557AC
00454F02  ldr     r0, [r0]           ; xTickCount
00454F04  bx      lr
```

Its exact bytes are `dff8ac0800687047`, and its SHA-256 is
`6dbb234e35fb86f883529c083fed0e1cabdca99d6647a95568ed1a5522310ac0`.
The complete ISR getter is:

```text
00454F06  movs    r0, #0
00454F08  ldr.w   r0, [pc, #0x8A0]  ; literal at 0x004557AC
00454F0C  ldr     r0, [r0]           ; xTickCount
00454F0E  bx      lr
```

Its exact bytes are `0020dff8a00800687047`, and its SHA-256 is
`8fe0a4f494b20b340d1126b2da725919f86c53cc3c1cabf5031fffc03f6de63a`.
Both PC-relative loads select literal `0x004557AC`, whose exact value is
`0x20074A34`. This word is immediately after the independently authenticated
`uxCurrentNumberOfTasks` word at `0x20074A30`, but its `xTickCount` identity
is established by both released getter algorithms and not merely by
adjacency.

These bodies are the exact V10.5.1 source after the authenticated G2 tick
configuration is applied:

- `configUSE_16_BIT_TICKS=0` selects a 32-bit `TickType_t`;
- the IAR Cortex-M55 NTZ port consequently defines
  `portTICK_TYPE_IS_ATOMIC=1`;
- `portTICK_TYPE_ENTER_CRITICAL()` and
  `portTICK_TYPE_EXIT_CRITICAL()` compile away;
- `portTICK_TYPE_SET_INTERRUPT_MASK_FROM_ISR()` becomes constant `0`, which
  accounts for the ISR leaf's leading `movs r0,#0`;
- `portTICK_TYPE_CLEAR_INTERRUPT_MASK_FROM_ISR()` becomes a no-op after
  consuming that saved value;
- the selected port does not override
  `portASSERT_IF_INTERRUPT_PRIORITY_INVALID()`, so the authenticated
  `FreeRTOS.h` default is empty.

Thus `0x00454F08` is the ISR leaf's second instruction, not a callable
boundary. No configuration guess or decompilation-derived substitute is
needed for either algorithm. The production overlay now registers both
source-replacement boundaries and authenticates the complete stock entries
before emitting their redirects.

### Direct caller closure

The whole installed application has exactly nine `BL` calls to
`xTaskGetTickCount`:

| Call site | Encoding |
|---:|---|
| `0x004490DC` | `0bf00fff` |
| `0x004492F6` | `0bf002fe` |
| `0x0044933E` | `0bf0defd` |
| `0x0047DC7C` | `d7f73ff9` |
| `0x0047E91A` | `d6f7f0fa` |
| `0x004C6932` | `8ef7e4fa` |
| `0x0052A4AE` | `2af726fd` |
| `0x0052A576` | `2af7c2fc` |
| `0x00576084` | `def63bff` |

The SHA-256 of those nine addresses packed in ascending order as
little-endian 32-bit words is
`3b032511b7c47b3afe47149262380345e354dea6d00f2b9dda369d10ce89abcd`.

`xTaskGetTickCountFromISR` has exactly one direct caller:

| Call site | Encoding |
|---:|---|
| `0x004490D6` | `0bf016ff` |

The complete halfword-aligned control-flow scan finds no `BL`, `B.W`, narrow
branch, conditional branch, `CBZ`, or `CBNZ` to `0x00454F08`, or to any
other interior instruction of either tick leaf. A separate byte-granular
stored-address scan finds no even or odd/Thumb pointer to `0x00454F08`.
Consequently there is no alternate entry that could justify retaining the
stale boundary.

## Global-seam closure

The fixed word `0x20074A30` is assigned the upstream
`uxCurrentNumberOfTasks` identity from three independent stock writer
contexts.

### Task creation

The add-new-task path at `[0x00454A04,0x00454A0E)` executes:

```text
ldr.w   r1, [pc, #0x798]  ; literal at 0x004551A0
ldr     r0, [r1]
adds    r0, r0, #1
str     r0, [r1]
```

Its exact bytes are `dff898170868401c0860`, with SHA-256
`fc892da7e24d91de18d81a6aa774a9947bd55fc72d9766c2d0ee83a20a68d373`.
The path enters the retained critical section immediately beforehand,
increments the population, and then handles first-task/current-task setup.
This is pristine `prvAddNewTaskToReadyList`.

### Immediate deletion

The non-current-task delete path at `[0x00454B00,0x00454B0A)` executes:

```text
ldr.w   r0, [pc, #0x69C]  ; literal at 0x004551A0
ldr     r1, [r0]
subs    r1, r1, #1
str     r1, [r0]
```

Its exact bytes are `dff89c060168491e0160`, with SHA-256
`81d068905daaac80d580d640680771a5c10d4b15a5ece8204b763bfc088915e6`.
This is the released `vTaskDelete` decrement for a task that can be cleaned
up immediately.

### Deferred self-deletion cleanup

The idle-task cleanup path at `[0x004556F6,0x00455700)` performs the same
load, decrement, and store through literal `0x00456040`, which also contains
`0x20074A30`. Its bytes are `dff848090168491e0160`, with SHA-256
`3acbbe0119579b1d1888255c30e28e35e524b1c027d240a519002a9b8bd9c48d`.
This is pristine `prvCheckTasksWaitingTermination` after a self-deleting
task is removed from the termination list.

Together, these paths prove that the word counts the current live task
population across both deletion modes. The integrated implementation
intentionally retains its fixed address. A future fully linked FreeRTOS kernel
should replace it with the source symbol only as part of one atomic
kernel-global RAM-layout migration.

## ABI and configuration closure

The callable ABI is ordinary 32-bit Arm AAPCS:

| Item | Contract |
|---|---|
| Arguments | none |
| Return | unsigned 32-bit task count in `r0` |
| Scratch state | `r0` and condition flags |
| Stack use | none |
| Calls/tail calls | none |

The official Cortex-M55 port defines `UBaseType_t` as unsigned long; both IAR
for this target and the freestanding Arm compiler use a 32-bit unsigned type.
The body does not require:

- the size or any field offset of G2's vendor-extended TCB;
- ready, delayed, suspended, termination, queue, timer, event-group, or list
  object layout;
- interrupt masking or a critical section around the single aligned word
  read;
- the Cortex-M55 port, TrustZone, MPU, FPU, or Apollo STIMER configuration;
- an assertion path, trace hook, callback, allocator, or libc helper.

`uxTaskGetNumberOfTasks` is not conditional on a `config*` or `INCLUDE_*`
macro in pristine V10.5.1. The three queue callers arise from released
queue-lock saturation macros, but the leaf itself has no queue ABI seam.

Tests cover zero, ordinary live counts, the observed application threshold
of 40, and unsigned 32-bit edge values. They also instrument the host seam to
prove the function performs exactly one word read.

## Whole-image topology

The complete installed application was scanned at every halfword for Thumb
`BL`, `B.W`, narrow unconditional/conditional branches, `CBZ`, and `CBNZ`,
and at every byte for possible even or odd/Thumb stored addresses.

### Direct entry references

| Call site | Encoding | Observed use |
|---|---|---|
| `0x00441A06` | `13f083fa` | queue transmit-lock saturation guard |
| `0x00441AD2` | `13f01dfa` | queue receive-lock saturation guard |
| `0x00441E2A` | `13f071f8` | queue lock saturation guard |
| `0x0059446E` | `c0f64ffd` | application population threshold check against 41 tasks |

The first three contexts exactly match the released `queue.c`
`prvIncrementQueueTxLock` and `prvIncrementQueueRxLock` policy: a signed
8-bit queue lock counter is incremented only while its unsigned value is
below the number of tasks, because no more tasks than the current population
can be unblocked.

The SHA-256 of those addresses packed in order as little-endian 32-bit words
is
`b046158abaf3afa64a28952e51e719cb87acade8a1c757395d91c398accca7e9`.

The scan finds:

- exactly those four `BL` calls to the entry;
- no `B.W` or narrow branch to the entry;
- no external direct branch into the four-byte interior;
- no stored even entry address, odd/Thumb entry address, or interior address,
  including in an unaligned byte-granular scan.

There is therefore no callback table, vector, jump table, hidden alternate
entry, or interior ownership that must move with the function.

## Integrated source implementation

The integrated implementation preserves the released single-return algorithm
and MIT notice. Its only G2 adaptation names the authenticated stock word
through `OPEN_CFW_FREERTOS_CURRENT_TASK_COUNT`. Tests override that macro with
an instrumented host reader; the freestanding Arm build uses `0x20074A30`.

With the core overlay's Cortex-M flags at `-O2`, Clang emits:

```text
00000000  movw    r0, #0x4A30
00000004  movt    r0, #0x2007
00000008  ldr     r0, [r0]
0000000A  bx      lr
```

The target bytes are:

```text
44f63020c2f2070000687047
```

The emitted function is 12 bytes with SHA-256
`1f9b9ecb6dcd1ec096f881d9f2c53d3fefe72abdbd7a569a6fb2583fd426a2b9`.
It has no relocation, undefined symbol, data section, callee, or second
function. It is six bytes larger than stock because it materializes the
absolute RAM address locally instead of sharing IAR's literal pool; that size
difference does not change behavior or ABI.

## Focused validation

`tests/test_runtime_freertos_task_count.py` contributes eleven tests that:

- authenticate the official provenance record, image, vendored V10.5.1
  snapshot, selected NTZ port macros, and recovered tick-width configuration;
- pin the exact normal and ISR tick-getter bodies, individual hashes, shared
  literal/global, and 18-byte pair closure;
- pin the complete stock body, neighbors, literal address, and SRAM word;
- pin independent creation, immediate-deletion, and deferred-deletion writer
  semantics;
- host-execute ordinary and unsigned 32-bit edge counts;
- prove the candidate performs exactly one word read;
- pin the target symbol, bytes, SHA-256, lack of relocations, and lack of
  undefined symbols;
- scan the complete official application for all nine normal tick calls, the
  single ISR tick call, and the existing task-count calls;
- prove no wide/narrow branch or stored address targets the stale
  `0x00454F08` interior boundary;
- scan every byte for the relevant stored entry and interior pointers.

Source SHA-256 is
`5cae3cac2e72f532844feac5eab4ab762c7cb82e2c90ae4015f6ce24a48605ac`;
fixture SHA-256 is
`4f03a8934f3e128c64478408dd4b1ca0ad60b4ec52cf62edc754dd00fcf3bcea`;
and test SHA-256 is
`6b66226f9708ad06bf98e0b58b089cf835b18816171781d6886a8b4632836e67`.

The focused suite passes:

```text
Ran 11 tests

OK
```

## Applied integration contract

The Apollo-main production overlay:

1. registers `open_cfw_freertos_task_get_number_of_tasks` for the original
   task-count boundary;
2. registers the shared `open_cfw_freertos_tick_count_read` provider and
   both public tick getter leaves;
3. redirects the complete six-byte stock span
   `[0x00454F10,0x00454F16)` with the established `B.W` plus NOP policy;
4. redirects the complete 8- and 10-byte tick getter spans
   `[0x00454EFE,0x00454F06)` and `[0x00454F06,0x00454F10)`;
5. retains fixed `uxCurrentNumberOfTasks` word `0x20074A30` and
   `xTickCount` word `0x20074A34` until kernel RAM
   globals are migrated atomically;
6. preserves all four task-count callers, all nine normal tick callers, and
   the sole ISR tick caller.

Aggregate relocation drift, package ownership, reproducibility, and
full-regression gates remain required whenever this integration changes. The
final tick placement is:

| Source object | Overlay offset | Runtime span | Bytes |
|---|---:|---|---:|
| shared tick provider | 115,912 | `[0x007B07EC,0x007B07F8)` | 12 |
| normal getter | 115,924 | `[0x007B07F8,0x007B07FC)` | 4 |
| ISR getter | 115,928 | `[0x007B07FC,0x007B0800)` | 4 |

The final 115,932-byte overlay hashes to
`272ba0e0492b0c6b721adec53a007809158d6871ccdb7ec52d4b6ceadd4b4529`;
the 3,639,328-byte Apollo-main component hashes to
`615304858150f5ee6b7b4c62a714629375010c6f4ab20bea1b6958daa6a5b4af`.
Builder accounting is 116,114 source-owned bytes including 182 in place,
81,626 generated patch bytes, 81,808 replaced-stock bytes, 3,441,556 opaque
base bytes, and the 32-byte wrapper.
The raw installed-application partition is 116,118 source, 81,622 generated,
and 3,441,556 opaque bytes.

The 4,417,782-byte package hashes to
`3bf635fb81439451e67642dc5ce11dde47a1773bda8ef11c12b35cd9bbbec01d`.
Its 596,957-byte flash plan hashes to
`2b89447a0a867d1ec34f51e5798a4da7b28effe8bc5d7e27b1b7f24ce1c9cd3c`
and records 828 placed, two unresolved, five container-only, and six
protected regions. Package ownership is 116,738 source bytes (2.642457%),
83,415 generated bytes (1.888165%), and 4,217,629 opaque bytes
(95.469378%); 200,153 bytes (4.530622%) are controlled. Boot ownership is
unchanged at 620 source, 817 generated, and 147,785 opaque bytes.

## Ranked follow-ups

1. Migrating `xTickCount` from fixed compatibility word `0x20074A34` to a
   linked source symbol remains a separate atomic kernel-global/tick-writer
   change.
2. `pvTaskIncrementMutexHeldCount` is compact released code, but it combines
   the current-TCB word with the recovered mutex-held-count TCB field and is
   less isolated than this task-count getter.
3. Cortex-M55 port functions remain port- and interrupt-policy boundaries, so
   they are less suitable than generic kernel leaves for the next atomic
   increment.
