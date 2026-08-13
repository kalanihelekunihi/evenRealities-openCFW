# G2 FreeRTOS queue-creation cluster source-boundary audit

Status: audited source candidate; not yet registered by the Apollo-main
production overlay  
Scope: Apollo-main application from official G2 package `2.2.6.10`;
offline disassembly and source comparison only, with no signing, flashing, or
hardware access

## Subsequent production status

The candidate milestone and fixed-provider wording below are historical.
The queue creation cluster has since entered production, and its assertion
seam now lands on the exact source-assembled MIT FreeRTOS-Kernel V10.5.1
`ulSetInterruptMask` body. The sectionized Clang-syntax pair source has
SHA-256
`28f16b37970b5529fe63cf250365b955b0c65fe2a016efda1ba718ee3b768de5`;
its fixed spans are `[0x005FA0A4,0x005FA0BA)`
(`f6bd0708e653c8e8880e33e298f9dc8ede1305c9386ea4ca5ff554d4022dc323`)
and `[0x005FA0BA,0x005FA0C8)`
(`97532a7902b38e1551198dd647d0fcdc3a6f19315b6491058a813c7643e0028a`),
with isolated copies at `[0x007B00D8,0x007B00EE)` and
`[0x007B00EE,0x007B00FC)`.

## Result

The retained queue-creation and mutex-initialization cluster is
unequivocally FreeRTOS-Kernel V10.5.1 `queue.c`. It should be implemented
from the authenticated upstream source rather than recreated from
decompilation. Focused disassembly closes the G2-specific configuration,
object ABI, dependency, and entry-topology gaps.

The cluster contains four complete functions:

| Function | Official end-exclusive range | Bytes | SHA-256 |
|---|---|---:|---|
| `xQueueGenericCreateStatic` | `[0x004415CA,0x00441636)` | 108 | `2ea331756c835ac36e34e934a9cb807f2695aeae46d6c459dc3033a9879b51b6` |
| `xQueueGenericCreate` | `[0x00441636,0x00441696)` | 96 | `2e2411839f0b813cc4356ae5a06eafa9e5ee125d200e3980d81e9757c73f0660` |
| `prvInitialiseNewQueue` | `[0x00441696,0x004416B8)` | 34 | `a95e0e593a7afb1fbc642b83c9bc54ab0dc6d994ad4e109bf14dc914d3c2add7` |
| `prvInitialiseMutex` | `[0x004416B8,0x004416D6)` | 30 | `b74cd4e549fb5b1420f880bbdd86c996f25322ecfd6875555923197d98a875e6` |

The contiguous 268-byte span
`[0x004415CA,0x004416D6)` has SHA-256
`88026bc2cb8b45e5983a6e34072ff2be0767a06775930305310dfcdf28bd48ad`.
It contains no literal pool or alignment gap between the four functions.

This is the smallest recommended **atomic queue-creation closure**:

1. both public generic creators are directly used by official binary callers;
2. both creators share `prvInitialiseNewQueue`;
3. the already source-owned dynamic mutex creator and the retained static
   mutex creator both use `prvInitialiseMutex`; and
4. compiling the four together allows their internal calls to resolve
   directly to source instead of preserving two unnecessary private binary
   seams.

The two private leaves are individually redirectable, and together account
for only 64 official bytes. Replacing only those leaves would be a valid
smaller mechanical increment, but it would leave allocation, validation, and
static/dynamic provenance in opaque generic creators. It would not complete
the queue-creation work flagged by the scheduler-state audit.

No unresolved binary fact blocks a bounded source implementation of the
four-function closure. Production integration still requires an isolated
host oracle, target compilation pins, redirect entries, relocation-drift
review, aggregate package ownership checks, and reproducibility gates.

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
| Upstream file | `third_party/freertos-kernel/queue.c` |
| Version | `V10.5.1` |
| Commit | `def7d2df2b0506d3d249334974f51e427c17a41c` |
| Tree | `7496dfa815c3cea2f45a090c6e92d113f494b930` |
| `queue.c` bytes | `125,614` |
| `queue.c` SHA-256 | `5cdf4fa35fe059446effff5bf20deaf83ddffb08921bc198fda106b1d17dd894` |
| `queue.c` Git blob | `5c872e0302839d96aab90919788fdc2b0be1c09e` |

The repository snapshot verifier authenticates the annotated tag, peeled
commit, tree, selected blobs, and retained MIT license. The official tag is
not cryptographically signed, so the copied source is additionally pinned by
Git object identity and SHA-256.

## Exact boundary proof

The preceding complete function is `xQueueGenericReset`:

| Range | Bytes | SHA-256 |
|---|---:|---|
| `[0x00441516,0x004415CA)` | 180 | `e5b7c5e487374e7966b8f2febb8aa1b804efa516c92f9e436a369ec5df100ad8` |

Its final instruction is `pop {r4,r5,r6,pc}` at `0x004415C8`. The static
creator begins immediately at `0x004415CA` with its own
`push {r3,r4,r5,lr}`.

The function after the cluster is the already source-owned public dynamic
mutex creator:

| Range | Bytes | SHA-256 |
|---|---:|---|
| `[0x004416D6,0x004416F0)` | 26 | `fd3801ca9d39f700a0c4dc5598707c4dd9c6efd75ec8c25d432e7ef29c15eddf` |

`prvInitialiseMutex` ends with `pop {r0,pc}` at `0x004416D4`; the public
creator begins at `0x004416D6` with its own `push {r4,lr}`. No bytes are
shared across either boundary.

The internal boundaries are equally explicit:

- `xQueueGenericCreateStatic` returns with
  `pop {r1,r4,r5,pc}` at `0x00441634`;
- `xQueueGenericCreate` starts with
  `push {r3,r4,r5,r6,r7,lr}` at `0x00441636` and returns at
  `0x00441694`;
- `prvInitialiseNewQueue` starts with `push {r3,r4,r5,lr}` at
  `0x00441696` and returns at `0x004416B6`;
- `prvInitialiseMutex` starts with `push {r7,lr}` at
  `0x004416B8`.

## Released-source behavior recovered from the official image

### `xQueueGenericCreateStatic`

The official function uses the ordinary five-argument Arm ABI:

| Register/location | Value |
|---|---|
| `r0` | queue length |
| `r1` | item size |
| `r2` | caller-owned queue storage, or null for zero-size items |
| `r3` | caller-owned `StaticQueue_t` |
| caller stack word 0 | eight-bit queue type |
| return `r0` | queue handle or null |

It:

1. asserts that the static control block is non-null;
2. validates a nonzero queue length;
3. requires storage to be non-null exactly when item size is nonzero;
4. materializes and checks the constant `sizeof(StaticQueue_t) == 0x50`;
5. writes one to `Queue_t.ucStaticallyAllocated` at `+0x46`;
6. calls `prvInitialiseNewQueue` with the original five arguments; and
7. returns the caller-owned control-block address.

Every rejected input follows the active G2 `configASSERT` fail-stop path.
The otherwise redundant volatile size materialization and comparison prove
that `configASSERT_DEFINED=1`.

### `xQueueGenericCreate`

The official function uses:

| Register | Value |
|---|---|
| `r0` | queue length |
| `r1` | item size |
| `r2` | eight-bit queue type |
| return `r0` | allocated queue handle or null |

It:

1. rejects a zero queue length;
2. checks `UINT32_MAX / length >= item_size`;
3. checks that `length * item_size + 0x50` cannot overflow;
4. asks `pvPortMalloc` for exactly
   `0x50 + length * item_size` bytes;
5. returns null without asserting if allocation fails;
6. derives queue storage as `queue + 0x50`;
7. writes zero to `ucStaticallyAllocated` at `+0x46`;
8. calls `prvInitialiseNewQueue`; and
9. returns the allocation unchanged.

Invalid dimensions follow the active assertion fail-stop path. An allocator
failure does not. This is the exact V10.5.1 distinction between invalid
creation parameters and ordinary allocation failure.

### `prvInitialiseNewQueue`

The private five-argument ABI is the same as the released source:

| Register/location | Value |
|---|---|
| `r0` | queue length |
| `r1` | item size |
| `r2` | queue storage |
| `r3` | eight-bit queue type |
| caller stack word 0 | `Queue_t *` |

The official 34-byte body:

1. points `pcHead` at the queue object itself when item size is zero;
2. otherwise points `pcHead` at caller/allocator-provided storage;
3. writes length at `+0x3C` and item size at `+0x40`;
4. calls `xQueueGenericReset(queue, pdTRUE)`;
5. writes the trace queue type byte at `+0x4C`; and
6. returns.

The call to `xQueueGenericReset` initializes the send and receive event lists,
queue read/write positions, message count, and lock bytes. Passing
`pdTRUE` selects the new-queue branch, so no task can be unblocked during
this call.

### `prvInitialiseMutex`

The private one-argument ABI is `r0 = Queue_t *`, with no return value.
Null is an accepted no-op because the upstream failed-trace hook emits no
code in this build.

For a non-null queue, the 30-byte body:

1. clears the mutex holder at `+0x08`;
2. sets `pcHead` at `+0x00` to null, the V10.5.1
   `queueQUEUE_IS_MUTEX` discriminator;
3. clears recursive-call count at `+0x0C`; and
4. performs
   `xQueueGenericSend(queue, NULL, 0, queueSEND_TO_BACK)` to put the
   binary semaphore into its initial available state.

The byte at `+0x4C` remains the queue-type value established by
`prvInitialiseNewQueue`. The released `uxQueueType` compatibility macro in
this part of `queue.c` aliases `pcHead`; it is not the trace metadata byte.

## Recovered Queue_t, list, and configuration ABI

The exact queue control block is 80 bytes:

| Offset | Field | Cluster use |
|---:|---|---|
| `+0x00` | queue storage head / mutex discriminator | initialized |
| `+0x04` | write pointer | initialized through reset |
| `+0x08` | queue tail / mutex holder | reset or cleared |
| `+0x0C` | last-read pointer / recursive count | reset or cleared |
| `+0x10` | tasks waiting to send (`List_t`) | initialized through reset |
| `+0x24` | tasks waiting to receive (`List_t`) | initialized through reset |
| `+0x38` | messages waiting | initialized through reset/send |
| `+0x3C` | queue length | written directly |
| `+0x40` | item size | written directly |
| `+0x44` | receive lock byte | initialized through reset |
| `+0x45` | transmit lock byte | initialized through reset |
| `+0x46` | static-allocation provenance byte | written by both creators |
| `+0x47` | alignment padding | untouched |
| `+0x48` | trace queue number | untouched by released creation code |
| `+0x4C` | trace queue-type byte plus padding | type byte written directly |

Each `List_t` is 20 bytes. The source-owned `vListInitialise` entry used
indirectly by reset has already pinned the 20-byte list layout, 12-byte mini
end marker, 32-bit `TickType_t`, and `portMAX_DELAY=0xFFFFFFFF`.

The cluster closes these released configuration values:

| Configuration | Recovered value | Evidence |
|---|---:|---|
| `configSUPPORT_STATIC_ALLOCATION` | `1` | static creator and `+0x46` marker |
| `configSUPPORT_DYNAMIC_ALLOCATION` | `1` | dynamic creator and `+0x46` marker |
| `configUSE_MUTEXES` | `1` | mutex initializer and both public wrappers |
| `configUSE_TRACE_FACILITY` | `1` | trace number/type fields and `+0x4C` store |
| `configUSE_QUEUE_SETS` | `0` | no queue-set pointer in the 80-byte object |
| `configASSERT` | enabled | active fail-stop calls and static size check |
| `portBYTE_ALIGNMENT` | `8` | queue allocator and recovered `heap_4` ABI |
| pointer/`UBaseType_t`/`size_t` | 32 bits | object offsets and overflow arithmetic |

The trace facility fields are present, but all four creation hook macros are
empty in the compiled G2 configuration:

- `traceQUEUE_CREATE`;
- `traceQUEUE_CREATE_FAILED`;
- `traceCREATE_MUTEX`; and
- `traceCREATE_MUTEX_FAILED`.

There is no omitted call or write at any of their released-source positions.
A bounded source implementation should retain hook points as empty
configuration macros, not invent a logging or registry side effect.

## Whole-image control-flow and stored-reference topology

The complete installed application was scanned:

- at every halfword for Thumb `BL` and `B.W`;
- at every halfword for narrow unconditional and conditional branches plus
  `CBZ`/`CBNZ`;
- at every byte for little-endian even and odd/Thumb entry or interior
  pointers.

The result is:

| Function | Direct `BL` entry callers | `B.W` entry callers | External interior branches | Stored entry pointers | Stored interior pointers |
|---|---:|---:|---:|---:|---:|
| `xQueueGenericCreateStatic` | 5 | 0 | 0 | 0 | 0 |
| `xQueueGenericCreate` | 6 | 0 | 0 | 0 | 0 |
| `prvInitialiseNewQueue` | 2 | 0 | 0 | 0 | 0 |
| `prvInitialiseMutex` | 2 | 0 | 0 | 0 | 0 |

The ordered direct-call inventories are:

### `xQueueGenericCreateStatic`

| Call site | Encoding | Containing function / role |
|---:|---|---|
| `0x00441700` | `fff763ff` | `xQueueCreateMutexStatic` |
| `0x004417A8` | `fff70fff` | `xQueueCreateCountingSemaphoreStatic` |
| `0x004498F8` | `f7f767fe` | CMSIS-RTOS2 `osSemaphoreNew`, static-control-block branch |
| `0x00449AA2` | `f7f792fd` | CMSIS-RTOS2 `osMessageQueueNew`, static-control-block branch |
| `0x0047EAEA` | `c2f76efd` | timer-service list and static queue initializer |

The SHA-256 of these call-site addresses packed in order as little-endian
32-bit words is
`27bc36d1e3c55f51961f442b1fba9571447d7ae19e458d1b9295ff2b63a95f2a`.

### `xQueueGenericCreate`

| Call site | Encoding | Containing function / role |
|---:|---|---|
| `0x004416E0` | `fff7a9ff` | `xQueueCreateMutex` |
| `0x004417D4` | `fff72fff` | `xQueueCreateCountingSemaphore` |
| `0x00449906` | `f7f796fe` | CMSIS-RTOS2 `osSemaphoreNew`, dynamic branch |
| `0x00449AB4` | `f7f7bffd` | CMSIS-RTOS2 `osMessageQueueNew`, dynamic branch |
| `0x004738B2` | `cdf7c0fe` | display-lock initializer |
| `0x00513FC4` | `2df737fb` | one-time subsystem semaphore initializer |

The SHA-256 of these call-site addresses packed in order is
`4be852612877174962efeb6b12872c9210cf6775b7d97899aaa7bd73a3d19461`.

### Private initializer calls

`prvInitialiseNewQueue` is called only at:

| Call site | Encoding | Caller |
|---:|---|---|
| `0x00441620` | `00f039f8` | `xQueueGenericCreateStatic` |
| `0x00441680` | `00f009f8` | `xQueueGenericCreate` |

The packed caller-list digest is
`5315fbdc46ea0e7d2f823bbf72e90b646f319925269805796dd41eb28d0d2b11`.

`prvInitialiseMutex` is called only at:

| Call site | Encoding | Caller |
|---:|---|---|
| `0x004416E8` | `fff7e6ff` | `xQueueCreateMutex` |
| `0x00441708` | `fff7d6ff` | `xQueueCreateMutexStatic` |

The packed caller-list digest is
`4ad88307099ae64ad93ff56536dfd10bdc38b1bdba767f4ea593f713ffa158c4`.

The relevant containing functions are independently pinned:

| Range | Role | Bytes | SHA-256 |
|---|---|---:|---|
| `[0x004416D6,0x004416F0)` | dynamic mutex creator | 26 | `fd3801ca9d39f700a0c4dc5598707c4dd9c6efd75ec8c25d432e7ef29c15eddf` |
| `[0x004416F0,0x00441710)` | static mutex creator | 32 | `2977000da7aab5b87abce1270dca6518785de04a1e72d08082802713d478fd28` |
| `[0x00441790,0x004417C2)` | static counting-semaphore creator | 50 | `a46100f23dd51b8276a4c2ebafa1ba96c6813114810ae0f5297764c20368eb62` |
| `[0x004417C2,0x004417EE)` | dynamic counting-semaphore creator | 44 | `ed30ebca04b655b1ec31e60296d977382d0712057db88f99b205a555b374120f` |
| `[0x0044989A,0x0044994E)` | CMSIS semaphore creator | 180 | `ebdcf69b866e35e468ba9ce84d7e7ac9b58377b5ffcc439762d729f7d99a098c` |
| `[0x00449A32,0x00449ABE)` | CMSIS message-queue creator | 140 | `52d0abf097914cc84b2cdfe7f628dc61f9efb40bac880112062315d2b1bfba47` |
| `[0x004738A8,0x004738DE)` | display-lock initializer | 54 | `bba889445f513ff5e715afe2e98a6d5ca8e206bf4769a0fb372a6c62e4323aa8` |
| `[0x0047EAB8,0x0047EAF6)` | timer runtime initializer | 62 | `e34431d020471c30b8e3d3fed60fb15e83b77f49ee2921fcdae5e3be7d589ece` |
| `[0x00513F9C,0x0051400A)` | one-time subsystem initializer | 110 | `9e014098c460b5a94ff0cf388e5d01ce9462eb27b537798a46f5dc0be251bcfd` |

The `0x00513F9C` caller's exact semaphore role is proven by its
`(length=1,item_size=0,type=3)` creator tuple and later take/give use. No
unequivocal public symbol name is assigned to that private subsystem
function.

## Current source-overlay references outside the official scan

The official-image topology above is necessary but not sufficient for an
integration patch because the current source overlay also uses stable stock
Thumb entries:

| Source file | Current retained entry use |
|---|---|
| `runtime_freertos_queue.c` | dynamic generic creator `0x00441637`; mutex initializer `0x004416B9` |
| `lv_display_lock.c` | dynamic generic creator `0x00441637` |
| `rtos_timer_runtime_initialize.c` | static generic creator `0x004415CB` |

Redirecting the complete official entries would preserve these calls.
Preferably, the integration should instead link these source consumers
directly to the new source functions. That removes avoidable source-to-stock-
redirect-to-source hops and makes the remaining ABI seams explicit.

## Direct dependency seams

The cluster has four executable dependencies:

| Caller | Target | Role | Current status |
|---|---:|---|---|
| both generic creators | `0x00441696` | `prvInitialiseNewQueue` | part of recommended source closure |
| `prvInitialiseNewQueue` | `0x00441516` | `xQueueGenericReset(queue,pdTRUE)` | retained official V10.5.1 queue seam |
| dynamic generic creator | `0x00456110` | `pvPortMalloc` | retained official V10.5.1 `heap_4` seam |
| `prvInitialiseMutex` | `0x004417EE` | `xQueueGenericSend` | public entry is already source-owned |

All assertion branches call the retained fail-stop entry
`0x005FA0A4`, then write zero through `0xFFFFFFFF` and loop. That entry is
outside FreeRTOS `queue.c` and remains a reviewed application/port seam.

### List/reset seam

`xQueueGenericReset` is an exact released-source function, but it is not yet
source-owned. For `pdTRUE` it:

- calculates queue tail/read/write positions;
- clears message count;
- sets both queue lock bytes to `-1`;
- initializes both 20-byte task wait lists; and
- enters/exits the recovered critical-section seam.

Its list calls already redirect to source-owned V10.5.1 `vListInitialise`.
The four-function queue-creation closure can therefore retain reset as one
well-bounded compatibility seam. A later reset integration can use the same
upstream source and close its critical-section and event-list branches
separately.

### Allocator seam

The allocator at `0x00456110` is unequivocally FreeRTOS V10.5.1
`heap_4`, not the separate application TLSF allocator:

| Property | Recovered value |
|---|---:|
| reviewed malloc range | `[0x00456110,0x00456210)` |
| reviewed malloc bytes | 256 |
| reviewed malloc SHA-256 | `8d86a7daf341ad836729e4abdd25b66b45f97a56d6d1077c07bf0c5718f8dc57` |
| heap base | `0x20004558` |
| heap bytes | `0x2F000` |
| alignment | 8 |
| block header | 8 bytes |
| ownership bit | `0x80000000` |
| locking | `vTaskSuspendAll` / `xTaskResumeAll` |

The queue-creation closure should continue calling this heap until the
authenticated `heap_4.c` source is integrated with its exact SRAM placement
and globals. It must not substitute the application TLSF heap.

### Trace seam

There is no executable trace dependency in this cluster. The queue trace
metadata fields are ABI-significant, but the four creation hooks compile to
no operations. Preserve the upstream hook sites as configuration-controlled
empty macros.

## Source-integration design

Use the authenticated V10.5.1 algorithms, retaining project-prefixed types
and symbols until the complete kernel headers/configuration are admitted.
The bounded implementation should:

1. define the exact 80-byte `Queue_t` view with `_Static_assert` checks for
   every used offset;
2. define the exact five-argument static/private ABIs;
3. compile both generic creators and both private initializers in one source
   translation unit;
4. link internal creator-to-initializer calls directly;
5. link `prvInitialiseMutex` directly to the existing source-owned generic
   send implementation;
6. retain explicit fixed seams for `xQueueGenericReset`, `pvPortMalloc`, and
   the assertion fail-stop until those functions are separately integrated;
7. preserve empty trace hooks and the exact allocation-failure behavior; and
8. redirect all four complete official entry spans with the established
   `B.W` plus NOP fill policy.

Do not compile pristine `queue.c` wholesale yet. The repository does not
have a production `FreeRTOSConfig.h`, complete G2 port selection, or a single
source-owned closure for every public function that a full translation unit
could retain. A bounded port of these exact upstream functions is safer than
guessing those unrelated build settings. Linker garbage collection of the
complete upstream file can be revisited after configuration and port headers
are production-owned.

## Ranked integration recommendation

1. **Integrate the four-function 268-byte creation cluster together.**
   There is no remaining ABI or configuration blocker. Use released V10.5.1
   source, keep reset/`heap_4`/assert as explicit seams, and link the
   existing source generic-send function directly.
2. **Add `xQueueCreateMutexStatic` next.** Its complete 32-byte official
   body is a trivial wrapper over the new static creator and mutex
   initializer. This removes the last stock public mutex-creation wrapper
   without adding a dependency.
3. **Add the static and dynamic counting-semaphore creators.** Their complete
   50- and 44-byte bodies validate `max >= initial`, call the appropriate
   generic creator, and publish the initial count.
4. **Integrate `xQueueGenericReset`.** Use released source, the already
   source-owned list initializer, and the reviewed critical/event-list seams.
   This removes the largest remaining creation-time queue dependency.
5. **Vendor and authenticate V10.5.1 `heap_4.c`, then integrate it as its
   own allocator project.** The current bounded FreeRTOS snapshot
   intentionally excludes `portable/MemMang`. Preserve heap base
   `0x20004558`, size `0x2F000`, its recovered globals, suspension policy,
   hook, accounting, and eight-byte alignment.
6. **Only then consider compiling a broader pristine `queue.c` translation
   unit.** Gate that step on a production `FreeRTOSConfig.h`, closed port
   choice, target section-GC proof, and full object/layout assertions.

## Audit method and limitations

This audit:

- hashes the official installed bytes after removing the 32-byte OTA
  preamble;
- compares instruction semantics with the authenticated V10.5.1 `queue.c`;
- disassembles every cluster function and each direct caller context;
- scans the complete application for wide and narrow Thumb branches;
- scans every byte for possible stored even or odd/Thumb entry/interior
  pointers; and
- includes current source-overlay consumers that call the retained entries
  by fixed address.

No device was connected. No flash operation, signing attempt, runtime claim,
or hardware validation was performed. Function naming is limited to
identities closed by released source or surrounding project evidence; the
private caller at `0x00513F9C` is intentionally described by behavior rather
than assigned a speculative subsystem symbol.
