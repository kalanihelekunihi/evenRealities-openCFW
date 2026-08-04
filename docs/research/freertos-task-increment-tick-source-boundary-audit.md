# FreeRTOS `xTaskIncrementTick` source-boundary audit

Status: production-integrated in the FreeRTOS scheduler-cluster tranche;
current Apple source target `0x007B06A8`, Linux target `0x007B0DD0`

## Result and scope

The source implementation closes the complete FreeRTOS-Kernel V10.5.1
`xTaskIncrementTick` routine from authenticated commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. The scheduling algorithm and
list operations come from the released MIT-licensed kernel source. Focused G2
disassembly supplies the selected build configuration, fixed kernel-global
addresses, 32-bit list/TCB ABI, callable boundary, and its two outgoing call
seams.

This boundary began as a deliberately isolated research candidate. It is now
production-configured: the source is registered in the Apollo-main overlay and
core-source manifest, the complete official entry is redirected, and flashable
artifacts contain the relocated function. Its reset-helper, assertion-mask,
port, and resume dependencies are source-owned within the reviewed scheduler
cluster.

The source and validation boundary is:

| File | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/freertos/runtime_freertos_task_increment_tick.c` | 6,927 | `0fb59aba7fb8b8ab1f7fc2b2cc5095f9bb05334770d44790a42b33ad80369cb2` |
| `components/shared/freertos/runtime_freertos_task_increment_tick.h` | 11,502 | `0e7990ad52bc620fd9529b350baab42c22b06cb6ad916e6bcf535f12f560d906` |
| `tests/fixtures/runtime_freertos_task_increment_tick_host.c` | 26,629 | `5ada37e8754a711ab14d456d74be14fe352f4bb6a9e5e8b791037b8ef12003df` |
| `tests/fixtures/runtime_freertos_task_increment_tick_upstream_oracle_host.c` | 16,051 | `432ad24d7bb999cdd4f785ad0ac90b2720717171475a6cd4f86fe6e4b0b30cdf` |
| `tests/test_runtime_freertos_task_increment_tick.py` | 31,205 | `0596abbec22d2a88200a4a46bbc9d2948ecb7670ef48dc93a6d2a8dac7662bb2` |

The authenticated 223,695-byte `third_party/freertos-kernel/tasks.c`
snapshot hashes to
`14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463`.
The oracle also uses the authenticated 10,338-byte `list.c`, SHA-256
`db5c169cf3efd68da1c6a923ac84eebc724d602c940bde0b9b5f01f05028fde4`,
only to construct and inspect genuine upstream lists.

## Official body and call closure

| Property | Evidence |
|---|---|
| Stock span | `[0x0045504C,0x0045519E)` |
| Size | 338 bytes |
| SHA-256 | `438ad4e9e1a7b439671463b2bbfd13616ebb6de32bd2aad53b802d31f11cc050` |
| Upstream function | FreeRTOS-Kernel V10.5.1 `tasks.c`, `xTaskIncrementTick` |
| Return ABI | 32-bit `BaseType_t`; zero or one |

The complete released image has three direct `BL` callers:

| Call site | Encoding | Containing routine |
|---|---|---|
| `0x0044211C` | `12f096ff` | `SysTick_Handler` |
| `0x00454ECC` | `00f0bef8` | `xTaskResumeAll` |
| `0x00456408` | `fef720fe` | tick catch-up path |

The little-endian caller-address digest is
`1a3ea5d9db1d906a1f91d344c8e6228b55ed15522fc8ca7186f50e5846f25d7d`.
The address-plus-encoding record digest is
`2102130f9d20f69f316b7e41d3d36c9e142ab1c323c19647b815347364fa9cfb`.

The stock body has exactly two outgoing calls:

| Call site | Encoding | Target | Role |
|---|---|---|---|
| `0x00455076` | `a5f115f8` | `ulSetInterruptMask` at `0x005FA0A4` | enabled `configASSERT` fail-stop path |
| `0x0045509A` | `00f0ecfb` | `prvResetNextTaskUnblockTime` at `0x00455876` | recompute delayed-list head after tick wrap |

Whole-application branch scans find no non-linking wide or narrow transfer to
the public entry, and no external branch to an interior instruction. A
byte-granular normalized-pointer scan finds six apparent values in the stock
span, but all six occur at odd, unaligned byte offsets and are instruction/data
coincidences rather than stored code pointers. Their
`(location,value,normalized-value)` record digest is
`a62e912b15215e33f75cb097bcf6575df948fb0ee4d5ca7a1a2192f4e75d7c6c`.
There is no authenticated alternate entry, callback-table owner, or jump-table
entry into this boundary.

## Recovered configuration

The released control flow is the exact upstream algorithm after preprocessing
with these G2 selections:

| Configuration | Recovered value | Consequence inside this function |
|---|---:|---|
| `configASSERT` | enabled | tick-wrap list invariant masks interrupts, fault-writes, and loops on failure |
| `configUSE_PREEMPTION` | `1` | a newly ready higher-priority task or pending yield requests a switch |
| `configUSE_TIME_SLICING` | `1` | more than one task on the current ready list requests a switch |
| `configUSE_TICK_HOOK` | `0` | no application tick-hook edge |
| `configUSE_PORT_OPTIMISED_TASK_SELECTION` | `0` | numeric `uxTopReadyPriority`; no bitmap primitive |
| `configUSE_16_BIT_TICKS` | `0` | 32-bit wrapping ticks and `portMAX_DELAY=0xFFFFFFFF` |
| `configMAX_PRIORITIES` | `56` | 56 contiguous ready lists |
| `configUSE_MINI_LIST_ITEM` | `1` | 12-byte end marker inside each list |
| `configUSE_LIST_DATA_INTEGRITY_CHECK_BYTES` | `0` | no integrity sentinels in list structures |
| `configLIST_VOLATILE` | empty | list link fields use the released non-volatile declaration |
| trace/coverage hooks used here | empty | no emitted trace or coverage call |

The body behaves as follows:

1. If the scheduler is suspended, increment only `xPendedTicks` and return
   false because the tick hook is disabled.
2. Otherwise increment the 32-bit tick count with unsigned wrap.
3. On wrap, assert that the current delayed list is empty, swap the delayed and
   overflow-delayed pointers, increment `xNumOfOverflows`, and call
   `prvResetNextTaskUnblockTime`.
4. When the tick reaches the next-unblock time, remove every due task from its
   delayed list and, if present, its event list; insert it at the end of its
   priority's ready list; and raise `uxTopReadyPriority` as needed.
5. Request a switch for a newly ready task strictly above the current task,
   for a time slice when the current ready list contains at least two tasks, or
   when `xYieldPending` is nonzero.

The candidate keeps upstream `listREMOVE_ITEM` and `listINSERT_END` semantics
inline. In particular, removal repairs both neighbors, reanchors `pxIndex`
when it points at the removed item, clears `pxContainer`, and decrements the
list count; ready insertion is relative to the list's current index rather
than unconditionally relative to the end marker.

## Recovered RAM and structure ABI

| Kernel state | Address or layout |
|---|---:|
| `pxCurrentTCB` | volatile pointer word at `0x20074A20` |
| `pxDelayedTaskList` | volatile pointer word at `0x20074A24` |
| `pxOverflowDelayedTaskList` | volatile pointer word at `0x20074A28` |
| `xTickCount` | volatile 32-bit tick at `0x20074A34` |
| `uxTopReadyPriority` | volatile 32-bit priority at `0x20074A38` |
| `xPendedTicks` | volatile 32-bit tick at `0x20074A40` |
| `xYieldPending` | volatile 32-bit `BaseType_t` at `0x20074A44` |
| `xNumOfOverflows` | volatile 32-bit `BaseType_t` at `0x20074A48` |
| `xNextTaskUnblockTime` | volatile 32-bit tick at `0x20074A50` |
| `uxSchedulerSuspended` | volatile 32-bit depth at `0x20074A58` |
| `pxReadyTasksLists[56]` | `0x2006A49C`, stride `0x14` |
| delayed-list backing objects | `0x20073CFC` and `0x20073D10` |

The recovered target ABI is 32-bit little-endian: pointers, `BaseType_t`,
`UBaseType_t`, and `TickType_t` are four bytes. `ListItem_t` is `0x14` bytes
with value/next/previous/owner/container at offsets
`+0x00/+0x04/+0x08/+0x0C/+0x10`. `MiniListItem_t` is `0x0C` bytes.
`List_t` is `0x14` bytes with item count/index/end marker at
`+0x00/+0x04/+0x08`; the end marker's `pxNext` is therefore at list offset
`+0x0C`.

The admitted TCB prefix has `xStateListItem` at `+0x04`,
`xEventListItem` at `+0x18`, and `uxPriority` at `+0x2C`. The candidate does
not claim the remainder of the vendor TCB layout.

## Isolated target objects

Both reviewed profiles use the project's freestanding Thumb-2 flags, including
`--target=thumbv7em-none-eabi`, `-mthumb`, `-O2`, `-fropi`, function/data
sections, disabled jump tables and unwind tables, and strict warnings. The
compiler output is deterministic within each reviewed profile but is not
byte-identical between profiles:

| Profile | Function section | SHA-256 | Call relocations |
|---|---:|---|---|
| Apple clang 21.0.0 | 344 bytes | `453dd5addafa0fade84729e0f215668b067055eea7daf43cc089b9ee98e02888` | `+0x3C` type 10 to `ulSetInterruptMask`; `+0x64` type 10 to `open_cfw_freertos_task_reset_next_task_unblock_time` |
| Homebrew clang 22.1.8 | 338 bytes | `889ae62e4116bbd1bd8c8db65612b779372dfe8a4f26e5c78e3a0828e1671c5a` | `+0x38` type 10 to `ulSetInterruptMask`; `+0x60` type 10 to `open_cfw_freertos_task_reset_next_task_unblock_time` |

Type 10 is `R_ARM_THM_CALL`. Those two functions are the only undefined
symbols referenced by the function section. Each ELF object also has the
normal eight-byte `.ARM.exidx` companion and one `R_ARM_PREL31` relocation
from that index entry back to the function section; neither object contains a
writable-data or nonempty read-only-data dependency.

Linux qualification uses the reviewed source-root spelling
`/Users/kalani/Repo/SybilSightABCD` and the pinned
`opencfw-linux-llvm:22.1.8` image. The source itself does not embed
`__FILE__`; the exact-root policy remains necessary for the aggregate project.

## Pristine-upstream semantic oracle

The upstream oracle does not restate or translate the candidate algorithm. It
compiles and invokes `xTaskIncrementTick` directly from the authenticated
pristine `tasks.c`, with pristine `list.c` used for graph construction and
inspection, the recovered `FreeRTOSConfig.h`, and host-only definitions for
unreached port/application seams.

Candidate and upstream fixtures expose the same pointer-independent model:
task identifiers, delayed-list selectors, ready/event-list identifiers,
sentinel and null identifiers, scalar scheduler globals, list order and
indices, state/event containers, wake ticks, and priorities. This makes full
post-call graph snapshots stable across ASLR and host architectures. The
candidate fixture additionally records volatile global loads/stores, ready-list
selection, reset-helper invocation, and assertion entry so mutation ordering
can be checked separately from final-state equality.

The focused differential verifier covers the suspended path, ordinary tick,
future delayed head, one and multiple due tasks, event-list removal, ready-list
index preservation, higher-priority preemption, equal-priority time slicing,
pending yield, 32-bit wrap with delayed-list swap and overflow count, and
`portMAX_DELAY` handling. Valid upstream graph scenarios avoid deliberately
triggering its aborting assertion path; the candidate harness exercises and
records that fail-stop seam independently before any list swap or overflow
mutation. The canonical Apple-clang and exact-root Linux-clang runs each pass
all 10 focused tests.

## Production closure and remaining limits

This boundary does not source-own `SysTick_Handler`, the tick catch-up path,
scheduler initialization, task creation, the complete TCB, or a migrated
FreeRTOS RAM arena. It does source-link to the live reset helper at
`0x007B0688` (Apple) or `0x007B0DB0` (Linux), and its assertion relocation
binds to source-owned `ulSetInterruptMask` at `0x007AFF08` or `0x007B054C`.
The production overlay carries separate reviewed placements and relocations for
both profiles and owns the complete 338-byte stock redirect/fill boundary.

The post-semaphore, pre-reset/unordered historical baseline used Apple
overlay/component/package pins of 121,330/3,644,726/4,423,180 bytes with
SHA-256
`b0e7ec99bdf68b0b42b79e2bb935274f6b5a12d53a449cca3f021fa906ad1e3c`,
`d9af47dd5b4668f23722a530df40b12dfb926ef5c0cc6fb603733b2e14a05a17`,
and `74278f0c7ae44e5364a6bca3abc762fcb48a0b2dcb06d816412566c5e974541d`;
Linux pins were 123,184/3,646,580/4,425,034 bytes with SHA-256
`2ece296109ba518aa5e9474bc46dc0f77003abd57231c5becd6525dd18673c63`,
`0c65b98e4867b7aa143572ccb831879c88ebeded4c8e41d2e294a72bd0ea61a9`,
and `b07ee2e813356553bd5c8f0a7c2f951376f8b338be6e53b6aff75824062f47f1`.
Later source promotions supersede those aggregate hashes without moving this
function. All evidence is offline; no G2 hardware was flashed, reset, or
executed.
