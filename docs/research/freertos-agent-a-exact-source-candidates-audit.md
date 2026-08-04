# FreeRTOS queue-reset and unordered-event-removal source integration audit

Status: authenticated FreeRTOS-Kernel V10.5.1 source, production-integrated
in the Apollo-main overlay and core-source manifest
Scope: official G2 Apollo-main application from package `2.2.6.10` and the
authenticated FreeRTOS-Kernel V10.5.1 snapshot; no signing, flashing, device,
debugger, or external-state access

## Result

Two remaining opaque FreeRTOS functions can be maintained from exact upstream
source instead of decompilation:

| Function | Official range | Stock bytes | Stock SHA-256 | Production result |
|---|---|---:|---|---|
| `xQueueGenericReset` | `[0x00441516,0x004415CA)` | 180 | `e5b7c5e487374e7966b8f2febb8aa1b804efa516c92f9e436a369ec5df100ad8` | source-owned as `open_cfw_freertos_queue_generic_reset` |
| `vTaskRemoveFromUnorderedEventList` | `[0x0045547C,0x00455556)` | 218 | `aa14475cf28218296c4fd829c02080fc017a5fe137f476de47e747f1e920e33b` | source-owned as `open_cfw_freertos_task_remove_from_unordered_event_list` |

They did **not** require one inseparable source closure. Queue reset retains
explicit calls to the already source-owned task-event-removal, list-init,
critical-section, and yield entries. Unordered removal inlines only the exact
upstream list and ready-list macros and retains the already source-owned
reset-next-unblock leaf. The production overlay appends queue reset first and
unordered removal second, with exact source/section hashes and empty
relocation allowlists. The core manifest splits both complete official spans
into generated source-entry replacements, emits a full-span `B.W` followed
only by NOP fill, and records both appended source leaves. Every official
entry address remains stable while both complete algorithms move into
authenticated source ownership.

## Authoritative inputs

The official image is pinned as follows:

| Property | Value |
|---|---|
| Package | [`ota_s200_firmware_ota.bin`](../../blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin) |
| Package bytes | `3,523,396` |
| Package SHA-256 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| OTA preamble | 32 bytes |
| Installed application bytes | `3,523,364` |
| Installed application SHA-256 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Runtime base | `0x00438000` |

The source authority is the repository's authenticated release snapshot:

| Property | Value |
|---|---|
| Project/release | [FreeRTOS-Kernel `V10.5.1`](https://github.com/FreeRTOS/FreeRTOS-Kernel/tree/V10.5.1) |
| Commit | [`def7d2df2b0506d3d249334974f51e427c17a41c`](https://github.com/FreeRTOS/FreeRTOS-Kernel/commit/def7d2df2b0506d3d249334974f51e427c17a41c) |
| Tree | `7496dfa815c3cea2f45a090c6e92d113f494b930` |
| [`queue.c`](../../third_party/freertos-kernel/queue.c) bytes/SHA-256 | `125,614` / `5cdf4fa35fe059446effff5bf20deaf83ddffb08921bc198fda106b1d17dd894` |
| `queue.c` Git blob | `5c872e0302839d96aab90919788fdc2b0be1c09e` |
| [`tasks.c`](../../third_party/freertos-kernel/tasks.c) bytes/SHA-256 | `223,695` / `14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463` |
| [`list.c`](../../third_party/freertos-kernel/list.c) bytes/SHA-256 | `10,338` / `db5c169cf3efd68da1c6a923ac84eebc724d602c940bde0b9b5f01f05028fde4` |
| `list.c` Git blob | `afcae87f11413a14a5a95138fb9bffb6787826c4` |
| License | [MIT](../../third_party/freertos-kernel/LICENSE.md) |

The pinned [snapshot verifier](../../third_party/freertos-kernel/verify_snapshot.py)
checks the [provenance manifest](../../third_party/freertos-kernel/PROVENANCE.json),
annotated tag object, peeled commit, tree, every selected Git blob, copied
SHA-256 value, and retained license. The upstream tag is annotated but not
cryptographically signed; the Git object identities and local hashes are
therefore part of the qualification boundary.

## Production source and oracle boundary

The focused test fails closed on every source, header, and fixture byte:

| File | Bytes | SHA-256 |
|---|---:|---|
| [`runtime_freertos_queue_generic_reset.c`](../../components/shared/freertos/runtime_freertos_queue_generic_reset.c) | 4,002 | `223758f605ee22220e5a534db4675545cc43a1f1fc5f24051c3c7c3cc92d556c` |
| [`runtime_freertos_queue_generic_reset.h`](../../components/shared/freertos/runtime_freertos_queue_generic_reset.h) | 9,551 | `eb47ede13109bfcc7ce0434bfcb14e4d3be7627e05b4348a399cc964e8038bb5` |
| [`runtime_freertos_queue_generic_reset_candidate_host.c`](../../tests/fixtures/runtime_freertos_queue_generic_reset_candidate_host.c) | 10,823 | `04851ae9628e65d36b4f070a0be98ac671d2b55aa32adfe0ca5416a590e5af65` |
| [`runtime_freertos_queue_generic_reset_upstream_oracle_host.c`](../../tests/fixtures/runtime_freertos_queue_generic_reset_upstream_oracle_host.c) | 4,610 | `84f20593a74bdd4650d64a2e1e8a3b39542a3b489d1a686aae1b8890dd72037a` |
| [`runtime_freertos_task_remove_from_unordered_event_list.c`](../../components/shared/freertos/runtime_freertos_task_remove_from_unordered_event_list.c) | 4,452 | `3656a2e24d63a2dd92743fde085be59ff4c830afb357535b38dbd4a4dc39f77c` |
| [`runtime_freertos_task_remove_from_unordered_event_list.h`](../../components/shared/freertos/runtime_freertos_task_remove_from_unordered_event_list.h) | 9,425 | `4b21346b0c0ec7a60e0752b0c6c38bbf1eab576e07eb52d9f11b42a7b96e91d` |
| [`runtime_freertos_task_remove_from_unordered_event_list_candidate_host.c`](../../tests/fixtures/runtime_freertos_task_remove_from_unordered_event_list_candidate_host.c) | 13,110 | `57ca256adc82b8a07f882cfc1ea7c62a46bb9598bbcbc6170342085618eb7e20` |
| [`runtime_freertos_task_remove_from_unordered_event_list_upstream_oracle_host.c`](../../tests/fixtures/runtime_freertos_task_remove_from_unordered_event_list_upstream_oracle_host.c) | 4,951 | `8b1bdb2144acebce47e0daa82bdd305b52ba4ab3bb0a22623eeca2f91c9ca199` |

The transitive host-oracle boundary is separately pinned so that a shared
fixture or recovered configuration change cannot silently redefine the
reference behavior:

| Transitive input | Bytes | SHA-256 |
|---|---:|---|
| [`runtime_freertos_task_increment_tick_upstream_oracle_host.c`](../../tests/fixtures/runtime_freertos_task_increment_tick_upstream_oracle_host.c) | 16,051 | `432ad24d7bb999cdd4f785ad0ac90b2720717171475a6cd4f86fe6e4b0b30cdf` |
| [`FreeRTOSConfig.h`](../../components/apollo_main/core_overlay/candidates/cmsis_freertos_constructors/FreeRTOSConfig.h) | 5,184 | `537e12cd879b06d7748f9b0e177f6ad0e17cd176405945771580e6d9c8312889` |
| [host `portmacro.h`](../../components/apollo_main/core_overlay/candidates/cmsis_freertos_constructors/portmacro.h) | 910 | `6e1ac1013191a6bd3e4924656a03a1515a1d5f06df83b8fbb9073a489961e675` |
| [host `string.h`](../../components/apollo_main/core_overlay/candidates/cmsis_freertos_constructors/string.h) | 513 | `1612795defaff20b3a0ad57b0106a1906a973d94557b2ac7c35d8d5307771f1d` |
| [snapshot verifier](../../third_party/freertos-kernel/verify_snapshot.py) | 19,109 | `a140aca673c0516e2dd2d948bd9cdb673445729b7593c5e79a0f70e50dd04b1b` |
| [provenance manifest](../../third_party/freertos-kernel/PROVENANCE.json) | 13,785 | `810d28df622a96646dd70d56311355c3531393fcf0fac1feac585f9cd799f99a` |
| [focused qualification test](../../tests/test_freertos_agent_a_exact_source_candidates.py) | current tree | pins production registration, topology, differential behavior, and both compiler profiles |

The oracle fixtures do not contain renamed copies of either function. They
compile the pristine authenticated `queue.c`, `tasks.c`, and `list.c` through
the already reviewed G2 configuration/host port adapter and invoke the real
upstream functions.

## `xQueueGenericReset` recovered configuration and ABI

The candidate preserves the complete upstream algorithm and admits only
focused G2 parameters:

- 32-bit `BaseType_t`, `UBaseType_t`, `size_t`, and pointers;
- 32-bit ticks;
- exact 80-byte `Queue_t`;
- 20-byte `List_t`, 20-byte `ListItem_t`, and 12-byte mini end item;
- queue head/write/tail/read offsets `+0x00`, `+0x04`, `+0x08`, and `+0x0C`;
- send/receive lists at `+0x10` and `+0x24`;
- message count, length, and item size at `+0x38`, `+0x3C`, and `+0x40`;
- signed one-byte receive/transmit locks at `+0x44` and `+0x45`;
- `queueUNLOCKED=-1`, `pdPASS=1`, `pdFAIL=0`;
- `configUSE_PREEMPTION=1`; and
- active `configASSERT`, with coverage markers compiling to no operations.

The target defaults expose each retained provider explicitly:

| Provider | Entry | Current qualification |
|---|---:|---|
| assertion interrupt-mask/fail-stop entry | `0x005FA0A4` | source-owned fixed entry |
| `portYIELD_WITHIN_API` | `0x004420BC` | source-owned fixed entry |
| critical enter | `0x004420D0` | source-owned fixed entry |
| critical exit | `0x004420E8` | source-owned fixed entry |
| `xTaskRemoveFromEventList` | `0x00455370` | source-owned redirect entry |
| `vListInitialise` | `0x0045607C` | source-owned redirect entry |

The hosted differential covers:

- new-queue list initialization with both pre-existing lists populated;
- any nonzero `xNewQueue` value, not only one;
- existing empty queues;
- existing queues with lower, equal, and higher-priority blocked senders;
- the conditional yield only for a higher-priority unblocked sender;
- zero-size semaphore items and length one;
- exact tail/write/read calculations and lock resets;
- zero length and both multiplication-overflow arrangements; and
- the null-pointer and final-result assertion boundaries.

### Exact stock topology

The sole direct call is:

| Call site | Encoding | Caller |
|---:|---|---|
| `0x004416AE` | `fff732ff` | `prvInitialiseNewQueue` in `[0x00441696,0x004416B8)` |

The containing 34-byte caller hashes to
`a95e0e593a7afb1fbc642b83c9bc54ab0dc6d994ad4e109bf14dc914d3c2add7`.
The packed caller-address digest is
`08afd3a5c3d78375eb18903997a05d47149dc307e6f99419c57f5cceb542ad84`;
the address-plus-encoding digest is
`d1757b72e2dab8e691c80387ce2efea7f86315e2c28387edbf919d6908d4b332`.

The stock body has exactly eight outgoing `BL` instructions:

```text
0x00441522 -> 0x005FA0A4
0x0044154A -> 0x004420D0
0x0044158E -> 0x00455370
0x00441596 -> 0x004420BC
0x004415A0 -> 0x0045607C
0x004415A8 -> 0x0045607C
0x004415AC -> 0x004420E8
0x004415B8 -> 0x005FA0A4
```

A whole-application scan at every halfword finds no unconditional `B.W`,
Thumb-2 `B<c>.W`, narrow conditional/unconditional branch, `CBZ`, or `CBNZ`
to the entry, and no such external transfer to an interior instruction. A
byte-granular even/Thumb pointer scan finds no entry or interior value at all;
its empty-record digest is
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## `vTaskRemoveFromUnorderedEventList` recovered configuration and ABI

The candidate preserves the exact upstream operation order:

1. assert that the scheduler is suspended;
2. publish `xItemValue | 0x80000000`;
3. load and assert the owning TCB;
4. remove the event item;
5. call `prvResetNextTaskUnblockTime` **before** removing the state item;
6. remove the state item and insert it at the current ready-list index;
7. update `uxTopReadyPriority` only when the task priority is higher; and
8. set `xYieldPending` only when the unblocked priority exceeds the current
   task's priority.

Focused ABI assertions preserve:

- exact list sizes and all five `ListItem_t` offsets;
- the complete 112-byte G2 TCB size;
- state item at TCB `+0x04`, event item at `+0x18`, and priority at `+0x2C`;
- `configMAX_PRIORITIES=56`;
- non-optimized ready-list selection;
- `configUSE_TICKLESS_IDLE=1`;
- `taskEVENT_LIST_ITEM_VALUE_IN_USE=0x80000000`; and
- the following fixed state/providers.

| State/provider | Address |
|---|---:|
| ready-list array | `0x2006A49C` |
| current-TCB pointer | `0x20074A20` |
| top ready priority | `0x20074A38` |
| yield-pending word | `0x20074A44` |
| scheduler-suspended count | `0x20074A58` |
| reset-next-unblock leaf | `0x00455876` |
| assertion interrupt-mask/fail-stop entry | `0x005FA0A4` |

The five literal words used by the stock body remain pinned at
`0x00455644`, `0x00455C40`, `0x00455DBC`, `0x00455C34`, and `0x00455C44`.
They contain, in order, scheduler-suspended, top-priority, ready-array,
current-TCB, and yield-pending addresses.

The graph differential covers lower/equal/higher current priorities, top
priority update/no-update, empty and prepopulated ready lists, sentinel and
task-valued list indexes, event/state index repair during removal, all-zero,
high-bit, and all-one item values, tick values zero through `UINT32_MAX-1`,
reset-next ordering, and both assertion paths.

### Exact stock topology

The sole direct call is:

| Call site | Encoding | Caller |
|---:|---|---|
| `0x0047EE02` | `d6f73bfb` | event-group set path in `[0x0047ED76,0x0047EE1E)` |

The 168-byte containing caller hashes to
`38b05fcf35bc59fd639e8a540e0e211d5d2a7026d1ad5fce97cd27f573084133`.
The packed caller-address digest is
`3294692df13736bddb4a8f78d24f0d8845c4af17630e3851e461cee721294dc0`;
the address-plus-encoding digest is
`1f50b74aa3b56987fd3161abb610dccb67d1dd72b7cea450d43fe62042629808`.

The body has exactly three outgoing calls:

```text
0x00455486 -> 0x005FA0A4
0x004554A0 -> 0x005FA0A4
0x004554D0 -> 0x00455876
```

There is no unconditional `B.W`, Thumb-2 `B<c>.W`, or narrow entry caller and
no such external transfer to an interior instruction. No aligned stored entry
or interior pointer exists. The byte-granular scan reports eleven unaligned
instruction/data-window false positives, which are pinned rather than silently
discarded:

```text
0x00550F7F -> 0x00455520   0x00551AA3 -> 0x00455500
0x005528AF -> 0x00455520   0x0073FCB2 -> 0x0045554E
0x00740416 -> 0x0045554E   0x00780B55 -> 0x00455554
0x00784769 -> 0x00455554   0x007848BD -> 0x00455554
0x0078744B -> 0x00455554   0x00789D6B -> 0x00455554
0x0078CA2D -> 0x00455552
```

Their ordered address/value-record digest is
`1e53cb6a968ed5792d96b4a5088072522ffad1ccdf5adb0bde2cace3ded5ccc4`.
None is four-byte aligned and none equals the entry.

## Target-object qualification

Both production compiler profiles now have independently measured target
objects. The Apple profile is `Apple clang version 21.0.0`. The Linux profile
is the exact `/home/linuxbrew/.linuxbrew/bin/clang` in the retained
`opencfw-linux-llvm` qualification container, which reports `Homebrew clang
version 22.1.8`. Linux compilation used the required mounted source spelling
`/Users/kalani/Repo/SybilSightABCD/openCFW`; it did not substitute the native
workspace path or infer bytes from Apple output.

Each source was compiled twice per profile with the production Thumbv7E-M
freestanding flags. Every same-profile pair was byte-identical.

| Profile | Production function section | Alignment | Bytes | SHA-256 | Text relocations | Undefined symbols/data |
|---|---|---:|---:|---|---:|---:|
| Apple Clang 21.0.0 | queue generic reset | 4 | 172 | `689da8cc4cd4757e609cdf77b3675ff7330fb46ea9b1efc29f4d96772f066baa` | 0 | 0 |
| Apple Clang 21.0.0 | unordered event removal | 4 | 214 | `c4a89f560a07598f3af72a4ca0e3a6bda1f23bd86e6f777ecea690f6db67ecdd` | 0 | 0 |
| Linux Clang 22.1.8 | queue generic reset | 4 | 174 | `18f27b60f944abbc4a8c703e4aa6e4fba0bac243a4010ea32474e9f8d9fe31ff` | 0 | 0 |
| Linux Clang 22.1.8 | unordered event removal | 4 | 210 | `b2e29e859cae0b43dadddf1dad7f44f9740ae5b6ed93a3febf3a28a7128331e4` | 0 | 0 |

The two complete Apple ELF objects are respectively 1,064 bytes with SHA-256
`54aa9daedd79bb553499997b611cf9430e3976bc7887de585dca617b7d03bf41`
and 1,144 bytes with SHA-256
`39953af7c0f8adbcd3d10b90b0e3f75573ab9e4136a9822a624b4878e7e4c43e`.
The two complete Linux ELF objects are respectively 1,048 bytes with SHA-256
`c5adf0faa71999de6d020bf8c9653dd4ec50da56104bc4f297e5bd6086bb568e`
and 1,120 bytes with SHA-256
`67ef01829118d020bafaee3d1c0f600645fd6c19ea831d77c29f9c180c254028`.
The focused test pins the complete function-section hex for both profiles,
not just size and hash. Both bodies use only immediate fixed addresses and
inline list operations. The ordinary `.ARM.exidx` relocation is metadata;
no relocation targets either text section. The expanded nine-test focused
suite passed natively with Apple Clang and in the exact-root Linux Clang 22.1.8
container. Its added fail-closed check proves that every callable dependency
listed below is still intercepted by exactly one production source-owned patch
at the fixed address used by the production source.

## Historical atomic production plan and completed result

The plan below records the pre-promotion reasoning retained for audit history.
The semaphore predecessor completed, and this tranche was then promoted in
the specified reset-then-unordered order. Its provisional equations must not
be mistaken for current placement; the final placements and pins are recorded
in the completed-result subsection below.

### Source and dependency records

Promote the candidate modules to production names
`runtime_freertos_queue_generic_reset.c/.h` and
`runtime_freertos_task_remove_from_unordered_event_list.c/.h`, remove the
`_candidate` suffixes from their exported symbols, and add both sources to
the Apollo overlay source list. Register two relocated leaves with empty
relocation arrays, their exact source hashes, and the profile-specific text
pins above. Append the queue reset function first and unordered removal
second.

Queue reset retains these fixed/redirect dependencies: assert
`0x005FA0A4`, yield `0x004420BC`, critical enter `0x004420D0`, critical exit
`0x004420E8`, `xTaskRemoveFromEventList` `0x00455370`, and `vListInitialise`
`0x0045607C`. Unordered removal retains assert `0x005FA0A4`,
`prvResetNextTaskUnblockTime` `0x00455876`, and the pinned ready-list/current-
TCB/top-priority/yield/scheduler-suspended RAM addresses. All callable
dependencies are already source-owned entries. The focused test now verifies
their exact patch names, target functions, addresses, uniqueness, and
production function registration. Neither new leaf has text relocations or a
dependency on the other.

The question of promoting `xQueueGenericReset` before its sole caller is not
a blocker. The premise is already stale in the current production tree:
`prvInitialiseNewQueue` at `[0x00441696,0x004416B8)` is source-owned and its
source currently calls Thumb entry `0x00441517`. A full-span redirect at
`0x00441516` therefore rebinds it without recompiling the caller. Even if the
caller were still opaque, the same redirect would be ABI-safe because the
only stock call lands at the function entry and no transfer lands inside the
body. The event-group set source similarly calls `0x0045547D`, so its sole
unordered-removal call is rebound by the entry redirect alone.

For the minimal atomic tranche, retain those two fixed calls. Directly
rebinding `runtime_freertos_queue_create.c` or `rtos_event_group_set.c` to new
C symbols would change already-qualified source hashes and compiled layout,
forcing unrelated leaf and downstream-offset repins. That source-to-source
cleanup is a separate optimization, not a prerequisite for ownership.

### Exact stock-region and redirect split

In `g2-2.2.6.10-core-source.json`, split
`opaque_after_easylogger_control` as follows:

| Region | File offset | Runtime range | Bytes | Ownership |
|---|---:|---|---:|---|
| preceding residual | 23,168 | `[0x0043DA60,0x00441516)` | 15,030 | `official_blob` |
| queue-reset replacement | 38,198 | `[0x00441516,0x004415CA)` | 180 | `generated_source_entry_replacement` |

The existing queue-create-static region remains unchanged at file offset
38,378/runtime `0x004415CA`.

Split
`opaque_between_freertos_task_remove_from_event_list_and_timeout_state` as
follows:

| Region | File offset | Runtime range | Bytes | Ownership |
|---|---:|---|---:|---|
| preceding residual | 119,942 | `[0x00455466,0x0045547C)` | 22 | `official_blob` |
| unordered-removal replacement | 119,964 | `[0x0045547C,0x00455556)` | 218 | `generated_source_entry_replacement` |

The existing timeout-state region remains unchanged at file offset
120,182/runtime `0x00455556`.

Add patch sites `replace_freertos_queue_generic_reset` and
`replace_freertos_task_remove_from_unordered_event_list`, each using `b_w`
over the complete stock span with NOP fill. Pin the respective 180-byte and
218-byte stock hashes from the result table. Final redirect bytes must be
recorded only after the post-predecessor destination addresses exist.

### Profile placement and byte payoff

Use these placement equations after the active predecessor tranche is final:

| Profile | Queue reset | Inter-function alignment | Unordered removal | Net appended bytes after initial front pad |
|---|---|---:|---|---:|
| Apple | `R_A=align4(E_A)`, `[R_A,R_A+172)` | 0 | `[R_A+172,R_A+386)` | 386 |
| Linux | `R_L=align4(E_L)`, `[R_L,R_L+174)` | 2 | `[R_L+176,R_L+386)` | 386 |

Thus component and package growth is `386 + ((-E_profile) & 3)` bytes. If
the post-predecessor end is four-byte aligned, the growth is exactly 386 bytes
on both profiles. The prescribed reset-then-unordered order avoids an extra
two-byte Apple pad. No provisional absolute placement is recorded: doing so
while the preceding semaphore tranche is in flight would create a stale pin,
not additional evidence.

The tranche reclassifies 398 stock bytes from opaque to generated redirects.
With aligned post-predecessor ends it appends 386 bytes and increases total
controlled coverage by 784 bytes on both profiles. Apple gains 386 source
bytes plus 398 generated redirect bytes. Linux gains 384 source bytes plus
400 generated bytes (398 redirect and two alignment). Any initial front pad
must additionally be counted as generated coverage and package growth.

### Aggregate repins required in the same change

The promotion is complete only when the following are updated atomically:

- `components/apollo_main/core_overlay/overlay.json`: two sources, two
  relocated leaves, two ordered functions, two patch sites, profile section
  pins/offsets, aggregate function/leaf/patch counts, and Apple/Linux overlay
  and component size/hash pins;
- `manifests/g2-2.2.6.10-core-source.json`: the two exact official-region
  splits, appended source/alignment regions, provider pins for both profiles,
  package sizes/hashes, and revised component description;
- generated component/package build reports, flash plans, and `SHA256SUMS`
  for both profiles;
- aggregate tests `test_core_overlay.py`,
  `test_apollo_overlay_relocated_leaves.py`,
  `test_apollo_overlay_relocated_closures.py`, `test_toolchain_profiles.py`,
  `test_open_cfw.py`, and this focused test's registration expectations;
- dependency/topology expectations in `test_runtime_freertos_queue_create.py`,
  `test_rtos_event_group_set.py`, `test_runtime_freertos_list_initialise.py`,
  `test_runtime_freertos_reset_next_task_unblock_time.py`,
  `test_runtime_freertos_timeout_state.py`, and
  `test_freertos_queue_next_closure_candidate.py` wherever they still call
  either body opaque; and
- `README.md`, `components/README.md`, overlay `EVIDENCE.md`/`NOTICE.md`,
  `docs/memory-map.md`, `docs/source-coverage.md`,
  `docs/upstream-inventory.md`, `docs/linux-reproducible-build.md`, this
  audit, and the related FreeRTOS configuration, queue-closure,
  timeout/reset-next, and remaining-OSS audits.

The build tools and Makefile consume these declarative records and do not
need a source-code change unless qualification uncovers a missing validation
rule. No ownership count, package hash, redirect encoding, or final address
should be pre-pinned before the current production predecessor is stable.

### Completed production record

Apple places a two-byte alignment region at overlay offset 121,330, queue
reset at offset 121,332 (172 bytes), and unordered removal at offset 121,504
(214 bytes). Linux places queue reset at offset 123,184 (174 bytes), a
two-byte inter-function alignment region, and unordered removal at offset
123,360 (210 bytes). Both functions have zero text relocations.

| Profile | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 121,718 / `76e21a06d75ed5c3beb5343014621e432726ea285e46d54978a4de43d9b6b666` | 3,645,114 / `c32ff5c5daf946812df503cfaa328c1cc22dc4206201da0b752a365f235e0108` | 4,423,568 / `0e18c7c435edaff3fa5b692e8c17251f075c472933c93b05153ac0307e6f4ca8` |
| exact-root Linux Clang 22.1.8 | 123,570 / `6885adb2da4019a5595fd14fefe7e6682e6d32e63b45c47b3436828a1238d288` | 3,646,966 / `657140490b0bd0b1f5aeb44505cc24b01377d16254f91c30e31893d1890731ca` | 4,425,420 / `d7870c13b9417f8a9866ad6b87858e712c1c6c005b0b534bdd1d4ba540b64d60` |

Canonical component accounting is 121,900 source-owned bytes (including 182
in place), 84,654 generated patch bytes, 84,836 replaced-stock bytes,
3,438,528 opaque bytes, and 32 wrapper bytes. The Apple package partitions
into 122,500 source, 86,467 generated, and 4,214,601 opaque bytes. Linux
component accounting is 123,752 source-owned bytes (including 182 in place),
84,820 generated patch bytes, 85,002 replaced-stock bytes, 3,438,362 opaque
bytes, and 32 wrapper bytes; its package partitions into 124,409 source,
86,410 generated, and 4,214,601 opaque bytes.

## Validation boundary and limitations

`tests/test_freertos_agent_a_exact_source_candidates.py` checks:

- authenticated upstream release provenance;
- exact production source/header and host-fixture pins;
- exact transitive oracle/configuration and provenance-gate pins;
- pristine upstream graph differentials;
- assertion and arithmetic edges;
- exact stock package/application/body hashes;
- full-image `BL`, unconditional `B.W`, Thumb-2 `B<c>.W`, narrow-branch,
  interior-transfer, and stored-pointer topology;
- caller and outgoing-call inventories/digests;
- exact G2 literal and object ABI values;
- deterministic Apple and exact-root Linux target objects and complete
  profile-specific section bytes;
- absence of target text relocations, undefined symbols, and data; and
- exact one-to-one production source ownership for all retained callable
  provider addresses; and
- unique production function, relocated-leaf, patch-site, and manifest-region
  registration for both promoted functions, including full-span redirects and
  NOP fill.

All results are static/offline. They do not establish on-device scheduling,
interrupt latency, timing, electrical safety, bootability, signing, or
flashability. No physical G2 was connected or accessed.
