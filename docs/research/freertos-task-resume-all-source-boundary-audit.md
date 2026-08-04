# FreeRTOS `xTaskResumeAll` source-boundary audit

Status: production-integrated in the FreeRTOS scheduler-cluster tranche;
current Apple source span `[0x007B0800,0x007B0924)`, Linux span
`[0x007B0F24,0x007B1048)`

## Result and scope

The source implementation owns the complete FreeRTOS-Kernel V10.5.1
`xTaskResumeAll` routine from authenticated commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. Focused disassembly supplies
only the G2 RAM bindings, callable boundary, caller/callee topology, selected
configuration, and 32-bit list/TCB ABI.

This boundary began as an isolated research tranche and is now live production
source. It is registered in the Apollo-main overlay and core-source manifest,
the complete stock entry receives a redirect/fill replacement, and its port
trio, `prvResetNextTaskUnblockTime`, `xTaskIncrementTick`, and assertion-mask
dependencies all resolve to source-owned providers.

| Source or validation input | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/freertos/runtime_freertos_task_resume_all.c` | 6,262 | `455b29e4eaec27451ad5ed24953583291659201b7fbd2da5c330f6e9da081dd5` |
| `components/shared/freertos/runtime_freertos_task_resume_all.h` | 10,625 | `9eaadd2e390b7300e90140a1e114481eaac2135c9830d320a2a8653f213c1045` |
| `tests/fixtures/runtime_freertos_task_resume_all_host.c` | 20,218 | `783030ea1fe57d39609511e4c27dda1dad4c83599ba52af0f081a121c30cf89e` |
| `tests/fixtures/runtime_freertos_task_resume_all_upstream_oracle_host.c` | 6,366 | `ac3d0f00ed2ae54c4cf2726651b881758661037ffa8aff7b083386fc74ad2ff4` |
| `tests/test_runtime_freertos_task_resume_all.py` | 31,288 | `1fd811855f0110a14685a73fa37c4f6e1211da8cee97bddfb376c4be46a6ac17` |

The oracle adapter includes the independently pinned 16,051-byte pristine
`tasks.c` oracle fixture, whose SHA-256 is
`432ad24d7bb999cdd4f785ad0ac90b2720717171475a6cd4f86fe6e4b0b30cdf`.
It therefore invokes the authenticated upstream function rather than a second
adaptation. The underlying 223,695-byte `tasks.c` snapshot hashes to
`14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463`.

## Official body and recovered configuration

| Property | Evidence |
|---|---|
| Stock span | `[0x00454DCC,0x00454EFE)` |
| Size | 306 bytes |
| SHA-256 | `548e05e1f8a2f498372dd1f4eb7c6536e093dbbfdb82fbe8f9b54231cedc8a09` |
| ABI | Thumb, `BaseType_t` return, no arguments |
| Tick width | 32-bit unsigned |
| Preemption | enabled |
| Port-optimized task selection | disabled |
| Maximum priorities | 56 |
| Trace/coverage hooks | empty |
| List integrity check bytes | disabled |

The leading assertion reads `uxSchedulerSuspended` and, on zero, calls
`ulSetInterruptMask`, writes zero through address `UINTPTR_MAX`, and loops.
The valid path enters the port critical section, performs a wrapping 32-bit
decrement and a fresh volatile scheduler-depth read, and exits through the port
critical-section helper on every non-asserting path.

The complete recovered RAM seam is:

| Upstream object | G2 address |
|---|---:|
| `pxReadyTasksLists[56]` | `0x2006A49C` |
| `xPendingReadyList` | `0x20073D24` |
| `pxCurrentTCB` | `0x20074A20` |
| `uxCurrentNumberOfTasks` | `0x20074A30` |
| `uxTopReadyPriority` | `0x20074A38` |
| `xPendedTicks` | `0x20074A40` |
| `xYieldPending` | `0x20074A44` |
| `uxSchedulerSuspended` | `0x20074A58` |

The corresponding literal words are pinned at `0x004551B0`, `0x004557A8`,
`0x004551A4`, `0x004551A0`, `0x004551AC`, `0x00455A18`, `0x00455A14`, and
`0x00455468`. The candidate retains a 20-byte `List_t`, 20-byte `ListItem_t`,
12-byte mini-list end, state item at TCB `+0x04`, event item at `+0x18`, and
priority at `+0x2C`.

## Released mutation and call order

The source preserves the upstream order:

1. Assert a nonzero scheduler depth before entering the critical section.
2. Enter the port critical section, decrement depth, and reload it.
3. On the outermost resume with at least one task, repeatedly remove the
   pending head's event item, execute the compiler memory barrier, remove its
   state item, update numeric top priority, and insert the state item at the
   selected ready-list index.
4. Store `xYieldPending=pdTRUE` when a moved task's priority is greater than or
   equal to the freshly loaded current task priority.
5. If any pending task moved, call `prvResetNextTaskUnblockTime` once.
6. Copy volatile `xPendedTicks`, invoke `xTaskIncrementTick` exactly that many
   times, latch any nonzero result into `xYieldPending`, then store zero to the
   volatile pending-tick word.
7. Reload `xYieldPending`; with preemption enabled, return `pdTRUE` and call
   the port yield helper when it is nonzero.
8. Exit the port critical section and return the already-yielded flag.

The official body has exactly six direct outgoing calls:

| Call site | Target | Candidate seam |
|---|---:|---|
| `0x00454DDC` | `0x005FA0A4` | assertion `ulSetInterruptMask` |
| `0x00454DEA` | `0x004420D0` | port enter critical |
| `0x00454EBE` | `0x00455876` | reset next unblock time |
| `0x00454ECC` | `0x0045504C` | increment tick |
| `0x00454EF2` | `0x004420BC` | port yield |
| `0x00454EF6` | `0x004420E8` | port exit critical |

The address-pair digest for this call closure is
`d1f9fbac618757e8280d28a9c8c830751c7e61c1fd2c73d848dd649d5c48516e`.

## Direct entry, caller, and stored-pointer topology

The stock function has 21 direct `BL` callers:

```text
0x004418D8  0x00441936  0x0044194A  0x00441B76
0x00441BEC  0x00441C32  0x00441CA2  0x00441D2E
0x00441D78  0x00454B7A  0x00454FCE  0x00455600
0x00455786  0x004561E8  0x0045627A  0x0047E8AC
0x0047E8DE  0x0047E8EC  0x0047ECBE  0x0047EE14
0x0057E216
```

Their little-endian address digest is
`0376e19f832cae16a06c7f82772d8447c7b0ba259829731b5f2d9fd459bbcbbf`;
the address-plus-encoding record digest is
`b6a64bf2fc5277484f9ec220ae171f77a520adb1bcf03c9b57f56360a9a769f2`.

Whole-application scans find no non-linking `B.W` or `B<c>.W` branch to the
entry, no wide or narrow direct external transfer to an interior instruction,
and no literal stored entry address. A byte-granular pointer scan does find 22
incidental interior-valued patterns in unrelated code/data; they are
intentionally retained as false-hit evidence with digest
`3bbc8c32bcc73d9275d5a486a5f909a19718991b19f668ff857ee80e49e280a8`.
None normalizes to the public entry and no pattern establishes an alternate
callable owner. This is complete for the scanned direct encodings and literal
little-endian pointers, but it does not prove the absence of a target computed
at run time and transferred through `BX`/`BLX` register, `LDR`/`POP` to `PC`,
or `TBB`/`TBH`. No such computed-indirect ownership is claimed by this isolated
boundary.

## Target profiles and relocation closure

Both reviewed profiles emit a four-byte-aligned 292-byte Thumb function, 14
bytes smaller than the stock IAR body. The profile difference is confined to
compiler register allocation/instruction selection in the inlined list
operations.

| Profile | Function SHA-256 |
|---|---|
| Apple clang 21.0.0 | `8b8a8bde3a875d1b4f6b28d3aa0e4bedf2c80f80d0c0c380614e3e1a8c4216a3` |
| Homebrew clang 22.1.8 | `7fb0e6bab36ed324d800362e1d1f85e29b8b7924e6cbe994600ebe998fe025a6` |

Each profile has the same six `R_ARM_THM_CALL` relocations:

```text
+0x012  open_cfw_freertos_port_enter_critical
+0x022  open_cfw_freertos_port_exit_critical
+0x02E  ulSetInterruptMask
+0x0EE  open_cfw_freertos_task_reset_next_task_unblock_time
+0x0FC  open_cfw_freertos_task_increment_tick
+0x11C  open_cfw_freertos_port_yield
```

There are no other undefined symbols, writable data dependencies, or hidden
runtime providers. Two independent target compilations per profile are
byte-identical. Linux qualification uses the reviewed image
`opencfw-linux-llvm:22.1.8`, compiler
`/home/linuxbrew/.linuxbrew/opt/llvm/bin/clang`, and exact mounted source root
`/Users/kalani/Repo/SybilSightABCD/openCFW`.

## Differential semantics and limitations

The focused verifier compares the candidate with pristine upstream
`xTaskResumeAll` over nested resume, zero-task outermost resume, higher- and
lower-priority pending migration, multi-tick drain, same-priority time slicing,
and a two-task pending migration that reaches priority 55. Snapshots include the
return value, scheduler globals, pending and blocked list counts, ready-list
counts, state/event containers, canonical list indices, and canonical list
order. The multi-task graph points both source-list indices at removable items
and the priority-55 ready-list index at an existing task. It proves source-list
index repair while preserving the destination index and inserting the migrated
task immediately before it.

Candidate tick, reset-next, and yield call counts are asserted for every
scenario. The tick count reached by pristine upstream is paired with the
candidate tick-call count, and the upstream return value pairs the candidate
yield-call count. A dedicated outer-resume trace asserts every instrumented
volatile access, barrier, dependency call, yield, and critical-section event in
released order, including a three-tick `0, 1, 0` result sequence. The assertion
test separately proves both fail-stop dispatch and the exact
assert-load/enter/decrement-store/reload/exit order.

The host graphs intentionally exercise the FreeRTOS `MiniListItem_t` sentinel
through the common `ListItem_t` prefix. Host differential libraries therefore
compile with `-fno-strict-aliasing`, matching that upstream layout contract on a
64-bit host; the separately pinned 32-bit target objects retain the production
flags and exact relocation/body checks above.

Apple clang and exact-root Linux LLVM each pass all seven focused semantic
tests. Production integration additionally links the complete scheduler
cluster, redirects every authenticated stock boundary without overlap, and
pins the aggregates. The post-semaphore, pre-reset/unordered historical
baseline used Apple overlay/component/package pins of
121,330/3,644,726/4,423,180 bytes with SHA-256
`b0e7ec99bdf68b0b42b79e2bb935274f6b5a12d53a449cca3f021fa906ad1e3c`,
`d9af47dd5b4668f23722a530df40b12dfb926ef5c0cc6fb603733b2e14a05a17`,
and `74278f0c7ae44e5364a6bca3abc762fcb48a0b2dcb06d816412566c5e974541d`;
Linux pins were 123,184/3,646,580/4,425,034 bytes with SHA-256
`2ece296109ba518aa5e9474bc46dc0f77003abd57231c5becd6525dd18673c63`,
`0c65b98e4867b7aa143572ccb831879c88ebeded4c8e41d2e294a72bd0ea61a9`,
and `b07ee2e813356553bd5c8f0a7c2f951376f8b338be6e53b6aff75824062f47f1`.
Later source promotions supersede those aggregate hashes without moving this
function. No G2 was flashed or executed.
