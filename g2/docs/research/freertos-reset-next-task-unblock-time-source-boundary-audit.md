# FreeRTOS `prvResetNextTaskUnblockTime` source-boundary audit

Status: production-integrated in the FreeRTOS scheduler-cluster tranche;
current Apple source target `0x007B0688`, Linux target `0x007B0DB0`

## Result and scope

The source implementation owns the complete FreeRTOS-Kernel V10.5.1
`prvResetNextTaskUnblockTime` private leaf from authenticated commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. Focused disassembly supplies
only the G2 RAM addresses and the selected 32-bit `List_t` ABI.

This boundary began as a deliberately isolated research candidate. It is now
registered in the Apollo-main overlay and core-source manifest, receives a
complete stock-entry redirect, and is covered by aggregate production tests.
The source-owned `xTaskIncrementTick` and `xTaskResumeAll` callers resolve to
this live helper.

The originally admitted source boundary is:

| File | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/freertos/runtime_freertos_reset_next_task_unblock_time.c` | 2,544 | `afaf50d27bf7fc9a106e15b9318d36f0afa6ff6ba35619269297f41e3ce867b8` |
| `components/shared/freertos/runtime_freertos_reset_next_task_unblock_time.h` | 4,721 | `33d825bc20a59592935908a88a061062707fc5e81590f077a7adb2324ef07073` |
| `tests/fixtures/runtime_freertos_reset_next_task_unblock_time_host.c` | 7,792 | `c9ae51f8a9be9850dc8e00ebe3b23ffcfe0aaea0292aef23e77936b3be061d47` |

The implementation retains the upstream MIT notice. The authenticated
223,695-byte `third_party/freertos-kernel/tasks.c` snapshot hashes to
`14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463`.

## Official body and recovered globals

| Property | Evidence |
|---|---|
| Stock span | `[0x00455876,0x0045589C)` |
| Size | 38 bytes |
| Bytes | `dff8d81708680068002805d15ff0ff30dff8d817086005e00868c0680068dff8c81708607047` |
| SHA-256 | `a789916ee424c824c5c5f2302e62e4a861f0fa1289917d9c0e095947bce82598` |
| `pxDelayedTaskList` | volatile pointer word at `0x20074A24` |
| `xNextTaskUnblockTime` | volatile 32-bit `TickType_t` at `0x20074A50` |
| Empty-list value | `portMAX_DELAY = UINT32_MAX` |

The entry load uses aligned architectural PC `0x00455878` plus immediate
`0x7D8` to select literal `0x00456050`, whose word is `0x20074A24`. Both
stores use literal `0x00456060`, whose word is `0x20074A50`: the empty branch
loads it at `0x00455886`, while the non-empty branch loads it at
`0x00455894`.

The complete released instruction order is:

1. Load the address of the volatile `pxDelayedTaskList` word.
2. Read the delayed-list pointer.
3. Read `List_t.uxNumberOfItems` at offset `+0x00`.
4. If zero, materialize `UINT32_MAX` and store it to
   `xNextTaskUnblockTime`.
5. Otherwise, reload the volatile delayed-list pointer, read
   `xListEnd.pxNext` at list offset `+0x0C`, read the head item value at
   item offset `+0x00`, and store that value to `xNextTaskUnblockTime`.

The second pointer load is not folded into the first. The source and host
oracle preserve this volatile re-evaluation explicitly.

## List ABI and selected configuration

The body authenticates the following G2 FreeRTOS list contract:

| Type or field | Recovered value |
|---|---:|
| `sizeof(UBaseType_t)` | 4 |
| `sizeof(TickType_t)` | 4 |
| pointer width | 4 |
| `sizeof(ListItem_t)` | `0x14` |
| `sizeof(MiniListItem_t)` | `0x0C` |
| `sizeof(List_t)` | `0x14` |
| `List_t.uxNumberOfItems` | `+0x00` |
| `List_t.pxIndex` | `+0x04` |
| `List_t.xListEnd` | `+0x08` |
| `List_t.xListEnd.pxNext` | `+0x0C` |
| `ListItem_t.xItemValue` | `+0x00` |

This is consistent with `configUSE_16_BIT_TICKS=0`,
`configUSE_MINI_LIST_ITEM=1`, and
`configUSE_LIST_DATA_INTEGRITY_CHECK_BYTES=0`. Upstream `configLIST_VOLATILE`
is empty in this build, but `List_t.uxNumberOfItems` and the
`pxDelayedTaskList` global itself are volatile. No TCB layout, port call,
critical-section entry, trace hook, assertion, heap operation, or external
function is part of this leaf.

`configUSE_TICKLESS_IDLE=1` explains the calls from event-list removal paths,
but does not add a conditional branch inside the helper.

## Complete caller and reference topology

The stock leaf has six direct `BL` callers:

| Call site | Encoding | Containing routine |
|---|---|---|
| `0x00454B0A` | `00f0b4fe` | `vTaskDelete` |
| `0x00454EBE` | `00f0dafc` | `xTaskResumeAll` |
| `0x0045509A` | `00f0ecfb` | `xTaskIncrementTick` |
| `0x00455420` | `00f029fa` | `xTaskRemoveFromEventList` |
| `0x004554D0` | `00f0d1f9` | `vTaskRemoveFromUnorderedEventList` |
| `0x00455D9A` | `fff76cfd` | `xTaskGenericNotify` |

The little-endian caller-address digest is
`e849e824765de1654a2c5cca71758a37bce2729459dc5f3b7cb71b9854082c56`.
The address-plus-encoding digest is
`012189a12f316609470b8801612f6365db31ce8510ec46a218c3044a02a86fd3`.

The containing routine spans are independently pinned:

| Span | Bytes | SHA-256 |
|---|---:|---|
| `[0x00454AAE,0x00454B4C)` | 158 | `fed4eb28935bf7034f3f1893518e7de056995a5083d42863ab007e9e74de2597` |
| `[0x00454DCC,0x00454EFE)` | 306 | `548e05e1f8a2f498372dd1f4eb7c6536e093dbbfdb82fbe8f9b54231cedc8a09` |
| `[0x0045504C,0x0045519E)` | 338 | `438ad4e9e1a7b439671463b2bbfd13616ebb6de32bd2aad53b802d31f11cc050` |
| `[0x00455370,0x00455466)` | 246 | `1a5d4850f0799e97548f23ee1617fc1de362f8d2a674301baa6facd579d13de4` |
| `[0x0045547C,0x00455556)` | 218 | `aa14475cf28218296c4fd829c02080fc017a5fe137f476de47e747f1e920e33b` |
| `[0x00455C48,0x00455DB8)` | 368 | `fbcc2f27349099a2dc37ef103fc959730f14c6e0ef387507cbcba22fd3fc0a63` |

Whole-application scans find exactly those six calls and no non-linking
`B.W`, narrow unconditional or conditional branch, `CBZ`, or `CBNZ` to the
entry or from outside to an interior instruction. An unaligned, byte-granular
normalized pointer scan finds no stored even entry address, Thumb entry
address, or interior pointer. There is no alternate entry, callback table,
jump table, or ownership ambiguity.

The immediate preceding function `[0x00455836,0x00455876)` is 64 bytes and
hashes to
`86f7fc5725fe0fbbe85c07f68669981bad154cd58163427a6ead8106538e2a12`.
The following `xTaskGetCurrentTaskHandle` leaf `[0x0045589C,0x004558A4)` is
8 bytes and hashes to
`c7437c4b802c4991fe9a7bda7e790a1e252276812c72d57ef2b0db2cc18ac661`.
Neither neighbor falls through into this leaf.

## Isolated target object

The reviewed Apple clang 21.0.0 and Homebrew clang 22.1.8 profiles emit the
same four-byte-aligned, relocation-free 32-byte Thumb function:

```text
44f62420c2f207000168096821b10168c9680968c16270474ff0ff31c1627047
```

Its SHA-256 is
`249e6dafc8adc7286fbf5b96db744f902a04c7a38709a4344f766e01ec264a5f`.
The object contains one defined function, no undefined symbol, no relocation
against the function section, and no writable data. The compiler reuses base
address `0x20074A24` and stores to `xNextTaskUnblockTime` at displacement
`+0x2C`; this remains the exact recovered `0x20074A50` seam.

Linux qualification runs from the reviewed exact source-root spelling
`/Users/kalani/Repo/SybilSightABCD` with Homebrew clang 22.1.8. This leaf does
not embed `__FILE__`, so its bytes are independently root-invariant, but the
exact-root run preserves the aggregate project qualification policy.

## Host oracle and validation boundary

The host fixture records delayed-list pointer loads, count reads, head-value
reads, and the final time store. It proves:

- an empty list performs one volatile pointer load and stores `UINT32_MAX`;
- a non-empty list performs two pointer loads;
- the second load can select a different list and its head value wins;
- zero, `INT32_MAX`, and `UINT32_MAX` head values are preserved bit-for-bit;
- any nonzero 32-bit item count selects the non-empty path; and
- the final time store occurs after the selected value is obtained.

The focused test also authenticates the upstream snapshot, exact local source
pins, official bytes and literals, list ABI tokens, neighbor boundaries, full
caller/interior/stored-pointer topology, both reviewed compiler identities,
target bytes, absence of relocations/data, and current production registration
in the overlay and manifest.

This function boundary does not itself claim delayed-list initialization,
event-list removal, notification delivery, or a full RAM-layout migration.
The production scheduler cluster separately source-owns its tick and resume
callers. The post-semaphore, pre-reset/unordered historical baseline pins were
Apple overlay/component/package
121,330/3,644,726/4,423,180 bytes with SHA-256
`b0e7ec99bdf68b0b42b79e2bb935274f6b5a12d53a449cca3f021fa906ad1e3c`,
`d9af47dd5b4668f23722a530df40b12dfb926ef5c0cc6fb603733b2e14a05a17`,
and `74278f0c7ae44e5364a6bca3abc762fcb48a0b2dcb06d816412566c5e974541d`;
and Linux equivalents were 123,184/3,646,580/4,425,034 bytes with SHA-256
`2ece296109ba518aa5e9474bc46dc0f77003abd57231c5becd6525dd18673c63`,
`0c65b98e4867b7aa143572ccb831879c88ebeded4c8e41d2e294a72bd0ea61a9`,
and `b07ee2e813356553bd5c8f0a7c2f951376f8b338be6e53b6aff75824062f47f1`.
Later source promotions supersede those aggregate hashes without moving this
function. All validation remains offline; no hardware was flashed or executed.
