# FreeRTOS queue next-closure audit

Status: production-integrated and dual-profile qualified; the isolated
candidate sections below preserve the pre-promotion evidence

Scope: official G2 `2.2.6.10` Apollo-main image and authenticated
FreeRTOS-Kernel V10.5.1 source

## Result

The smallest useful ISR-side queue promotion is unequivocally upstream
FreeRTOS-Kernel V10.5.1 `xQueueGiveFromISR`:

| Function | Official end-exclusive span | Bytes | SHA-256 |
|---|---|---:|---|
| `xQueueGiveFromISR` | `[0x00441A42,0x00441B0A)` | 200 | `c56510d6607b980330894348b4f10affb4b1c90c256c497814803a72a7f71e9e` |

It has no queue-private copy or unlock dependency. Its only remaining opaque
executable callee is `xTaskRemoveFromEventList`. That callee is itself an
unequivocal V10.5.1 `tasks.c` function and its remaining callees are already
source-owned. Therefore the recommended **strict source closure** is the
noncontiguous pair:

| Function | Official end-exclusive span | Bytes | SHA-256 |
|---|---|---:|---|
| `xQueueGiveFromISR` | `[0x00441A42,0x00441B0A)` | 200 | `c56510d6607b980330894348b4f10affb4b1c90c256c497814803a72a7f71e9e` |
| `xTaskRemoveFromEventList` | `[0x00455370,0x00455466)` | 246 | `1a5d4850f0799e97548f23ee1617fc1de362f8d2a674301baa6facd579d13de4` |

Their ordered concatenation is 446 bytes with SHA-256
`c676fb469cfb041aaa6ca082198f25191089d06f67619289dec172ce578f2e4b`.
The pair has no unidentified executable provider, no callback ABI, and no
interior entry. It is implementation-ready. Fixed FreeRTOS RAM objects remain
compatibility state and must not be moved by this tranche.

Promoting only the 200-byte queue function is also safe if a smaller patch is
desired: it may continue to call the complete stock task function at
`0x00455370`. Promoting the 446-byte strict closure is preferred because it
removes that opaque executable seam for all queue callers at once.

## Isolated candidate verification

At the isolated pre-promotion stage, the strict pair had this non-production,
project-prefixed source candidate; those filenames remain as audit history:

| Artifact | Purpose |
|---|---|
| `components/shared/freertos/runtime_freertos_queue_next_closure.h` | Exact G2 queue/list/TCB ABI, compile-time size/offset assertions, and injectable fixed providers/RAM seams |
| `components/shared/freertos/runtime_freertos_queue_next_closure.c` | Bounded V10.5.1-equivalent implementations of `xQueueGiveFromISR` and `xTaskRemoveFromEventList` |
| `tests/fixtures/runtime_freertos_queue_next_closure_host.c` | Hosted candidate graph plus assertion/provider/trace instrumentation |
| `tests/fixtures/runtime_freertos_queue_next_closure_upstream_oracle_host.c` | Thin adapter that compiles and invokes pristine authenticated V10.5.1 `queue.c`, `tasks.c`, and `list.c` |
| `tests/test_freertos_queue_next_closure_candidate.py` | Differential, path, provenance, topology, and target-object checks |

The focused test proves matching upstream graphs for empty and nonempty wait
lists, lower-, equal-, and higher-priority wakeups, nullable wake flags,
suspended-scheduler pending-ready insertion, locked and saturated transmit
locks (including negative signed-lock values other than `queueUNLOCKED`), and a
full queue. It independently varies the `pcHead` mutex discriminator and the
aliased union holder/tail word, so an ordinary semaphore with a non-null tail
word is not mistaken for a held mutex. Ready-list tests seed an existing task,
place `pxIndex` at both the end marker and that task, and prove the released
`listINSERT_END` ordering and index preservation against the pristine oracle.
The reset seam records that tickless unblock-time reset occurs only after the
state item is ready and the event item is detached. Separate checks cover the
queue, item-size, ISR-mutex, lock-saturation, and owner assertions. Fixed target
seams remain injectable in the hosted build.

Apple clang 21.0.0 compiles the candidate twice for
`thumbv7em-none-eabi` using the reviewed freestanding flags. The object bytes
are deterministic. The task and queue text sections are 216 and 212 bytes,
with SHA-256 values
`ee7695d521943e9e85f026f000f8b9bf25517ffd96cf85a6e263ba129217a94e`
and
`a96ce1e9c86adad777fc709a3cead4e943f8c35bb9118ba9922bac393e45a5ba`.
The only executable relocation is the queue candidate's call to the task
candidate; the two additional type-42 relocations are the expected EHABI index
associations. No writable or read-only data payload is emitted.

This verification was deliberately isolated at the pre-promotion stage. At
that time neither candidate symbol nor its source file was present in
`overlay.json` or the core-source manifest, and no production caller had been
redirected. The later production integration and aggregate validation are
recorded at the end of this audit.

## Authenticated inputs

| Input | Authentication |
|---|---|
| Official OTA | `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`, 3,523,396 bytes, SHA-256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Installed application | OTA after the 32-byte preamble, load `0x00438000`, 3,523,364 bytes, SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Upstream release | FreeRTOS-Kernel V10.5.1 annotated tag, commit `def7d2df2b0506d3d249334974f51e427c17a41c`, tree `7496dfa815c3cea2f45a090c6e92d113f494b930`, MIT |
| `queue.c` | 125,614 bytes, SHA-256 `5cdf4fa35fe059446effff5bf20deaf83ddffb08921bc198fda106b1d17dd894`, Git blob `5c872e0302839d96aab90919788fdc2b0be1c09e` |
| `tasks.c` | 223,695 bytes, SHA-256 `14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463`, Git blob `d97085d8736905c1eeb9d9e871c81e5970ee70ed` |

The isolated released-source definition bodies hash as follows. These pins
identify the exact reviewed algorithms; they do not assert compiler byte
identity with the IAR-built stock image.

| Definition body | Source bytes | SHA-256 |
|---|---:|---|
| `xQueueGiveFromISR` | 7,595 | `7f6370d8922ecc0767390e3d86080b9e9ae69c5efec5af374e95163ea6a17559` |
| `xTaskRemoveFromEventList` | 2,950 | `dcb6ab01e83d3b9270e21b698a49f17c3476ea511343433492e85f90c4565838` |

The repository snapshot verifier passes and authenticates all 49 selected
upstream files. The annotated tag is not cryptographically signed; the tag
object, peeled commit, tree, selected Git blobs, and copied bytes are pinned.

## Exact queue-core boundaries

Focused Thumb disassembly divides the retained queue region without shared
instructions or literal pools:

| Official span | Bytes | Identity | Current status |
|---|---:|---|---|
| `[0x00441952,0x00441A42)` | 240 | `xQueueGenericSendFromISR` | opaque |
| `[0x00441A42,0x00441B0A)` | 200 | `xQueueGiveFromISR` | source-replaced; originally the next candidate in this audit |
| `[0x00441B0A,0x00441C44)` | 314 | `xQueueReceive` | opaque |
| `[0x00441C44,0x00441DA6)` | 354 | `xQueueSemaphoreTake` | source-replaced |
| `[0x00441DA6,0x00441E66)` | 192 | `xQueueReceiveFromISR` | opaque |
| `[0x00441E66,0x00441E8A)` | 36 | `uxQueueMessagesWaiting` | opaque |
| `[0x00441E8A,0x00441EA2)` | 24 | `uxQueueMessagesWaitingFromISR` | opaque |
| `[0x00441EA2,0x00441EC4)` | 34 | `vQueueDelete` | source-replaced |
| `[0x00441EC4,0x00441ED8)` | 20 | `prvGetDisinheritPriorityAfterTimeout` | opaque |
| `[0x00441ED8,0x00441F5E)` | 134 | `prvCopyDataToQueue` | opaque |
| `[0x00441F5E,0x00441F88)` | 42 | `prvCopyDataFromQueue` | opaque |
| `[0x00441F88,0x00441FF6)` | 110 | `prvUnlockQueue` | opaque |
| `[0x00441FF6,0x00442012)` | 28 | `prvIsQueueEmpty` | source-replaced |
| `[0x00442012,0x00442030)` | 30 | `prvIsQueueFull` | source-replaced |

The candidate begins with its own `push {r3,r4,r5,r6,r7,lr}` at
`0x00441A42` and returns with `pop {r1,r4,r5,r6,r7,pc}` at `0x00441B08`.
Its predecessor ends at `0x00441A40`; `xQueueReceive` starts independently
at `0x00441B0A`. The neighboring predecessor/successor hashes are
`09caa940da5c5337919aec35f7e3f4e2068558df48ca9ce430daaddf1e9deb08`
and
`f96de373691fb5d916ccbe25e0bc1d3474b918c16968b540b601fe6e36575560`.

The G2 image omits both `xQueuePeek` and `xQueuePeekFromISR`, selecting
`INCLUDE_xQueuePeek=0`. No unexplained body is hidden between receive and
receive-from-ISR; the source-replaced semaphore/mutex take occupies that
interval.

## Released `xQueueGiveFromISR` behavior

The AAPCS32 Thumb ABI is `r0=QueueHandle_t`,
`r1=BaseType_t *pxHigherPriorityTaskWoken` (nullable), and
`r0=pdPASS(1)` or `pdFAIL(0)` on return. Disassembly preserves the released
algorithm:

1. Assert a non-null queue, zero item size, and that a held mutex is not being
   given from an ISR.
2. Acquire the FreeRTOS `BASEPRI` mask and retain its returned prior value.
3. If `uxMessagesWaiting < uxLength`, increment the message count.
4. If `cTxLock == queueUNLOCKED (-1)` and the receive-wait list is nonempty,
   call `xTaskRemoveFromEventList`. If it returns true and the optional output
   pointer is non-null, store `pdTRUE` through the pointer.
5. If the queue is locked, increment its signed transmit lock only while the
   lock's unsigned value is below `uxTaskGetNumberOfTasks`; retain the released
   `INT8_MAX` assertion.
6. Return `pdPASS`; return `pdFAIL` without mutation when the queue is full.
   Restore the saved interrupt mask on both ordinary exits.

The complete outgoing-call graph is:

| Call sites | Target | Ownership after recommended closure |
|---|---|---|
| `0x00441A4C`, `0x00441A60`, `0x00441A86`, `0x00441A94`, `0x00441AE6` | `ulSetInterruptMask`, `0x005FA0A4` | source-owned fixed copy; assertion paths and ISR mask acquisition |
| `0x00441AC0` | `xTaskRemoveFromEventList`, `0x00455370` | promoted with strict closure |
| `0x00441AD2` | `uxTaskGetNumberOfTasks`, `0x00454F10` | already source-replaced |
| `0x00441B02` | `vClearInterruptMask`, `0x005FA0BA` | source-owned fixed copy |

`xQueueGiveFromISR` never invokes a yield directly. The task removal routine
sets `xYieldPending` when appropriate; the queue function additionally reports
the wake through the caller's optional flag. This remains correct when the
optional pointer is null.

## Strict task-side closure

`xTaskRemoveFromEventList` receives a nonempty `List_t *` in `r0`, removes
the highest-priority owner, makes it ready immediately or queues it in
`xPendingReadyList` while the scheduler is suspended, sets
`xYieldPending=pdTRUE` when the unblocked priority exceeds the current task,
and returns that comparison as `BaseType_t`.

Its only direct calls are:

| Call site | Target | Current ownership |
|---|---:|---|
| `0x0045537A` | `0x005FA0A4` | source-owned interrupt-mask/assert seam |
| `0x00455420` | `0x00455876` | source-replaced `prvResetNextTaskUnblockTime` |

List removal and ready-list insertion are released macros inlined into the
246-byte stock function; there is no hidden list-function call. Its exact
entry has nine direct queue-core `BL` callers:

```text
0x0044158E  0x00441900  0x004419F4  0x00441AC0  0x00441C10
0x00441D56  0x00441E18  0x00441F9A  0x00441FD0
```

Their little-endian address digest is
`a70b7dc8096a87718913eab967349886456a22c8ee3c85da0d0a77a66d91a501`.
Redirecting the task entry therefore affects generic reset/send, task and ISR
give/receive, semaphore take, and queue unlock, all through the same released
ABI.

## Object, global, and configuration closure

The G2-specific ABI recovered by disassembly is 32-bit little-endian with
4-byte pointers and 32-bit `BaseType_t`, `UBaseType_t`, and `TickType_t`.

| `Queue_t` field used by the candidate | Offset |
|---|---:|
| `pcHead` / mutex discriminator | `+0x00` |
| `u.xSemaphore.xMutexHolder` | `+0x08` |
| `xTasksWaitingToReceive` (`List_t`) | `+0x24` |
| `uxMessagesWaiting` | `+0x38` |
| `uxLength` | `+0x3C` |
| `uxItemSize` | `+0x40` |
| `cRxLock` / `cTxLock` | `+0x44` / `+0x45` |

`sizeof(Queue_t)=0x50`, `sizeof(List_t)=0x14`,
`sizeof(ListItem_t)=0x14`, and `sizeof(MiniListItem_t)=0x0C`.
`List_t.uxNumberOfItems` is `+0x00`, its index is `+0x04`, and its end node
begins at `+0x08`. A `ListItem_t` has value/next/previous/owner/container at
`+0x00/+0x04/+0x08/+0x0C/+0x10`.

The strict task closure uses these TCB fields:

| `TCB_t` field | Offset |
|---|---:|
| `xStateListItem` | `+0x04` |
| `xEventListItem` | `+0x18` |
| `uxPriority` | `+0x2C` |

Its fixed RAM compatibility seam is:

| Upstream object | G2 address |
|---|---:|
| `pxReadyTasksLists[56]` | `0x2006A49C` (stride `0x14`) |
| `xPendingReadyList` | `0x20073D24` |
| `pxCurrentTCB` | `0x20074A20` |
| `uxCurrentNumberOfTasks` | `0x20074A30` |
| `uxTopReadyPriority` | `0x20074A38` |
| `xYieldPending` | `0x20074A44` |
| `uxSchedulerSuspended` | `0x20074A58` |

The configuration needed for the two-function closure is fully recovered:

| Setting/seam | Recovered G2 value |
|---|---|
| `configMAX_PRIORITIES` | `56` |
| `configUSE_PREEMPTION` | `1` |
| `configUSE_TICKLESS_IDLE` | `1`; task removal calls reset-next-unblock-time |
| `configUSE_PORT_OPTIMISED_TASK_SELECTION` | `0`; numeric top-priority word and 56 ready lists |
| `configUSE_QUEUE_SETS` | `0`; no queue-set object word or notify branch |
| `configUSE_MUTEXES` | `1`; mutex discriminator/holder assertion retained |
| `configUSE_TRACE_FACILITY` | `1` for object fields; queue/task trace hooks in these bodies emit no code |
| `configSUPPORT_STATIC_ALLOCATION` / `configSUPPORT_DYNAMIC_ALLOCATION` | `1` / `1`; the 80-byte queue layout retains its allocation marker |
| `configQUEUE_REGISTRY_SIZE` | `0`; no registry storage changes this closure |
| `configUSE_16_BIT_TICKS` | `0`; list values and `TickType_t` are 32-bit |
| `configUSE_MINI_LIST_ITEM` | `1`; the list end is the 12-byte mini-item form |
| `configUSE_LIST_DATA_INTEGRITY_CHECK_BYTES` | `0`; no integrity sentinels alter list offsets |
| `configLIST_VOLATILE` | empty in this build; list count remains explicitly volatile |
| `INCLUDE_xQueuePeek` | `0`; neither task nor ISR peek body is present |
| `configASSERT` | enabled; disables interrupts, writes zero through `0xFFFFFFFF`, then loops |
| `portASSERT_IF_INTERRUPT_PRIORITY_INVALID` | emits no code in these stock ISR functions |
| `queueYIELD_IF_USING_PREEMPTION` / `portYIELD_FROM_ISR` | no direct yield in `xQueueGiveFromISR`; wake is returned and latched |

## Caller and ownership topology

The candidate queue entry has exactly four direct `BL` callers:

| Call site | Containing path |
|---|---|
| `0x004499D8` | CMSIS-FreeRTOS `osSemaphoreRelease` ISR branch |
| `0x00449E48` | CMSIS-FreeRTOS `osMemoryPoolFree` ISR branch |
| `0x00473894` | application ISR-side semaphore give |
| `0x00513F6C` | application ISR-side semaphore give |

The caller-address digest is
`2f14fa17758a7633ba914c8f78a65d9168840abce36e1754c872896e898675cf`.
Whole-application scans find no `B.W`, narrow branch, external transfer to an
interior instruction, or stored entry/interior pointer for
`xQueueGiveFromISR`.

The task closure similarly has no wide or narrow external interior transfer
and no stored exact entry. A byte-granular scan produces overlapping integer
patterns such as `0x00455441`/`0x00455445`; aligned instances are bytes of
ASCII strings including `ENTER_ANIM_COMPLETE`, `TERMINAL_UI_EVENT`, and
`EVENT_GIF_COMPLETE`, not executable pointers. No word contains the Thumb
entry `0x00455371`, and none is reached as a branch target. They do not create
interior ownership.

For planning the subsequent closures, the other public caller sets are:

| Function | Direct `BL` callers |
|---|---|
| `xQueueGenericSendFromISR` | `0x00449AEE`, `0x0047E80A`, `0x0047EB64` |
| `xQueueReceive` | `0x00449B9C`, `0x0047E99A` |
| `xQueueReceiveFromISR` | `0x0044997C`, `0x00449B6A`, `0x00449D6A` |
| `uxQueueMessagesWaiting` | `0x00449A2C`, `0x00449BE6`, `0x00449E5E` |
| `uxQueueMessagesWaitingFromISR` | `0x00449A24`, `0x00449BDE`, `0x00449E1C` |

None has a direct external interior branch or stored exact entry. The only
byte-scan hit inside `xQueueReceiveFromISR` is the unaligned four-byte pattern
at `0x0064CCAB`; its surrounding 16-byte records prove it is overlapping
non-pointer resource data, not a word-aligned Thumb reference.

## Promotion order after this closure

1. **Promote `xQueueGiveFromISR` and `xTaskRemoveFromEventList` together.**
   Reuse pristine V10.5.1 algorithms, bind the fixed RAM words above, and
   retain the already source-owned mask, task-count, and reset-unblock leaves.
2. **Promote the read-side ISR closure:** `xQueueReceiveFromISR`
   `[0x00441DA6,0x00441E66)` plus `prvCopyDataFromQueue`
   `[0x00441F5E,0x00441F88)`, 234 stock bytes. Its remaining fixed data-copy
   provider is the complete `__aeabi_memcpy` body
   `[0x00439BE4,0x00439C8A)` (166 bytes, SHA-256
   `8e696e1fb54917a436f850e562f74e8cc8734c259fdaac9f767a3c264ff427cd`).
   Bind its void AAPCS helper ABI explicitly or replace it with a reviewed
   source provider; do not model it as ISO `memcpy` returning `r0`.
3. **Promote generic ISR send:** `xQueueGenericSendFromISR` plus
   `prvCopyDataToQueue`, 374 stock bytes. Besides the same copy provider, the
   complete source helper retains the V10.5.1
   `xTaskPriorityDisinherit` seam at `[0x0045596E,0x00455A12)` (164 bytes,
   SHA-256
   `34e2c3a8b02daf3ea3f8d3d382ef3d802d48f4d65ee26fa0353d0faab51c7e93`).
4. **Promote task-context receive:** `xQueueReceive` plus the shared
   copy-from helper and `prvUnlockQueue`, 466 stock bytes. Do this after
   source-closing `xTaskCheckForTimeOut` and `vTaskPlaceOnEventList`; the
   remaining scheduler, port, timeout-state, resume, and empty-predicate
   dependencies are already source-owned. The `xTaskCheckForTimeOut`
   prerequisite is now satisfied by the production follow-on below;
   `vTaskPlaceOnEventList` remains the named open prerequisite.
5. Fold the 36-byte task and 24-byte ISR message-count accessors into the
   nearest queue tranche. They are unequivocal upstream leaves but remove
   less behavior than the ISR give/receive path.

For the first tranche, require a pristine-source oracle, assertion and
locked/unlocked randomized host tests, exact queue/list/TCB ABI assertions,
Apple/Linux isolated builds, scans of all four queue callers and all nine task
callers after redirect, deterministic aggregate rebuilds, and manifest
accounting. Hardware flashing is outside this audit.

## Upstream facts versus G2-derived parameters

The V10.5.1 function algorithms, names, API contracts, constants, list
semantics, and MIT license come directly from the authenticated upstream
snapshot. The following are not guessed upstream defaults: official entry
addresses, end-exclusive spans, body hashes, callers, selected compile-time
branches, empty trace/priority-validation seams, structure offsets, fixed RAM
addresses, and fixed provider addresses. Those values are G2-specific facts
recovered by focused disassembly and whole-image reference scans.

No part of this audit claims the historical compiler version or every G2
`FreeRTOSConfig.h` option. All parameters that can affect the recommended
closure are pinned above; unrelated application hooks and unused configuration
switches remain outside its boundary.

## Production promotion result

The strict pair is now active in `overlay.json`: complete redirect/NOP spans
replace both stock functions, while relocated source leaves are appended in
task-then-queue order. The queue leaf's one `R_ARM_THM_CALL` targets the
simultaneously selected, whole global function section for
`open_cfw_freertos_task_remove_from_event_list`; local, weak, data,
same-section, and unselected defined-symbol targets remain rejected.

Apple places task removal at `[0x007B1254,0x007B132C)` and queue give at
`[0x007B132C,0x007B1400)`. Linux places them at
`[0x007B19A8,0x007B1A80)` and `[0x007B1A80,0x007B1B54)`. The resulting
Apple/Linux overlay pins are 119,066 /
`da056ac28814f1b07c90d3651b290cd459bfde5e3cbcf30fed9a75a72729a0ae`
and 120,942 /
`8d56bdf484f3b1d67378f53eef89d7aea88282c6d552b8b2b1ee2bb7e0cb6905`.
The package pins are 4,420,916 /
`1b3ea44cc1cbd8004585e0208e33605c4e5f59229fdc5cb23395d19e0ba120f2`
and 4,422,792 /
`b93b39eb8e6f70e144b517dd7d770adcea67f62aa1100d722d4d1d0e6f8907ea`.
The Linux profile reproduced in two normal fail-closed builds. Production
promotion and validation were offline; no hardware was flashed or executed.

## Current timeout-check follow-on

The adjacent authenticated FreeRTOS V10.5.1 `xTaskCheckForTimeOut` dependency
is now production source-owned. Its 128-byte stock span
`[0x00455566,0x004555E6)` is redirected to a relocation-free 136-byte leaf,
placed at `[0x007B1440,0x007B14C8)` for Apple and
`[0x007B1B94,0x007B1C1C)` for Linux after two alignment bytes in each
profile. This does not yet source-close `vTaskPlaceOnEventList` or the
task-context receive closure described above.

The current Apple package is 4,421,054 bytes with SHA-256
`4fb13f64e81b8a6ef9bdf784ac38d5fc08ed03e4d310601a48bf4b395c20ab37`;
the Linux package is 4,422,930 bytes with SHA-256
`22c0e367882b005c1b85ee40d138e596c423d5a6335b8d93bc5a68873323c3ab`.
The canonical manifest has 821 main regions and records 877 placed, two
unresolved, and five container-only regions. The follow-on was qualified
offline; no G2 was connected, signed, flashed, reset, or executed.
