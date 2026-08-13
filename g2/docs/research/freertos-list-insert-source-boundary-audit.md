# G2 FreeRTOS sorted-list-insertion source-boundary audit

Status: source-integrated in the Apollo-main core overlay for official G2
package `2.2.6.10`  
Scope: Apollo-main application; offline overlay and package assembly only,
with no signing, flashing, or hardware access

## Result

The remaining FreeRTOS-Kernel V10.5.1 `list.c` function in the recovered
Apollo-main list cluster is the complete sorted-insertion leaf
`vListInsert`:

| Property | Recovered value |
|---|---|
| Official range | `0x004560B2...0x004560E7` |
| End-exclusive range | `[0x004560B2,0x004560E8)` |
| Size | 54 bytes |
| SHA-256 | `10c1fa85d530a003183c42d2fc11b80386669d011ce19f7a9c2a6d32516d4c59` |
| Upstream source | `third_party/freertos-kernel/list.c`, `vListInsert` |
| Official direct call sites | five in three containing functions |
| Stored entry/interior pointers | none |
| External branches into the interior | none |
| Calls made by the function | none |
| Target source-object size | 58 bytes |
| Target relocations/undefined symbols | zero/zero |

This is a complete, exact released-source boundary. It inserts a
`ListItem_t` into a `List_t` in ascending unsigned `xItemValue` order. Equal
values retain FIFO insertion order because traversal continues through
existing equal-valued nodes. The `portMAX_DELAY` case selects the current
tail directly, avoiding a traversal that could not pass the all-ones end
marker.

The integrated source is:

`components/apollo_main/core_overlay/runtime_freertos_list_insert.c`

It is registered as a complete entry redirect in the core overlay. It has no
include, external declaration, absolute call seam, device address, or binary
dependency. It retains the upstream MIT notice and uses project-prefixed types
and a project-prefixed entry so it cannot conflict with a later complete
FreeRTOS-header integration.

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
| `list.c` bytes | `10,338` |
| `list.c` SHA-256 | `db5c169cf3efd68da1c6a923ac84eebc724d602c940bde0b9b5f01f05028fde4` |
| `list.c` Git blob | `afcae87f11413a14a5a95138fb9bffb6787826c4` |

The repository snapshot verifier authenticates the official annotated tag,
peeled commit, tree, selected blobs, and retained MIT license. No unresolved
Cortex-M55 portable-layer selection affects this generic list function.

## Exact binary-to-source proof

The complete official body is:

```text
004560B2  push    {r4}
004560B4  ldr     r3, [r1]
004560B6  cmn.w   r3, #1
004560BA  bne     0x004560C0
004560BC  ldr     r2, [r0, #16]
004560BE  b       0x004560D0
004560C0  adds.w  r2, r0, #8
004560C4  b       0x004560C8
004560C6  ldr     r2, [r2, #4]
004560C8  ldr     r4, [r2, #4]
004560CA  ldr     r4, [r4]
004560CC  cmp     r3, r4
004560CE  bhs     0x004560C6
004560D0  ldr     r3, [r2, #4]
004560D2  str     r3, [r1, #4]
004560D4  ldr     r3, [r1, #4]
004560D6  str     r1, [r3, #8]
004560D8  str     r2, [r1, #8]
004560DA  str     r1, [r2, #4]
004560DC  str     r0, [r1, #16]
004560DE  ldr     r1, [r0]
004560E0  adds    r1, r1, #1
004560E2  str     r1, [r0]
004560E4  pop     {r4}
004560E6  bx      lr
```

With `r0 = List_t *pxList` and
`r1 = ListItem_t *pxNewListItem`, this maps one-to-one to pristine
V10.5.1:

1. load `pxNewListItem->xItemValue`;
2. compare it with 32-bit all-ones `portMAX_DELAY`;
3. for `portMAX_DELAY`, load `pxList->xListEnd.pxPrevious`;
4. otherwise begin at `&pxList->xListEnd`, follow `pxNext`, and continue
   while the next item's unsigned value is less than or equal to the new
   value;
5. set the new item's next pointer to the iterator's next pointer;
6. set that next item's previous pointer to the new item;
7. set the new item's previous pointer to the iterator;
8. set the iterator's next pointer to the new item;
9. set the new item's container to the input list;
10. increment the list item count and return.

`BHS` at `0x004560CE` is the unsigned
`pxIterator->pxNext->xItemValue <= xValueOfInsertion` condition with the
comparison operands in compiler-selected order. Continuing on equality is
the released FIFO behavior for equal-valued list items.

The official bytes are:

```text
10b40b6813f1010f01d1026907e010f1080200e0526854682468a342fad253684b604b6899608a60516008610168491c016010bc7047
```

The adjacent leaf boundaries close the selected span:

| Range | Recovered content | Bytes | SHA-256 |
|---|---|---:|---|
| `[0x0045609A,0x004560B2)` | `vListInsertEnd` | 24 | `78e2f1765fd9ba8e71098dababdfc4a4a1aabb73ed1f730d4fc24b94b54a2aba` |
| `[0x004560B2,0x004560E8)` | `vListInsert` | 54 | `10c1fa85d530a003183c42d2fc11b80386669d011ce19f7a9c2a6d32516d4c59` |
| `[0x004560E8,0x0045610E)` | `uxListRemove` | 38 | `e1ca0b525effd60568d00101c08010374cebfd3c80ee6ade4fec4da54bcb8794` |

The selected function owns its save/restore pair and terminal `bx lr`, has
only internal conditional/unconditional branches, and has no literal pool.

## Recovered ABI and configuration

The callable ABI is the ordinary 32-bit Arm procedure-call ABI:

| Item | Contract |
|---|---|
| First argument | `r0 = List_t *pxList` |
| Second argument | `r1 = ListItem_t *pxNewListItem` |
| Return | `void` |
| Official scratch registers | `r2`, `r3`, `r4`, condition flags |
| Official stack use | save/restore `r4`, no local frame |
| Calls or tail calls | none |

The complete required data ABI is:

| Type or field | Size/offset |
|---|---:|
| Pointer | 4 bytes |
| `UBaseType_t` | 4 bytes |
| `TickType_t` | 4 bytes |
| `ListItem_t` | `0x14` bytes |
| `ListItem_t.xItemValue` | `+0x00` |
| `ListItem_t.pxNext` | `+0x04` |
| `ListItem_t.pxPrevious` | `+0x08` |
| `ListItem_t.pxContainer` | `+0x10` |
| `MiniListItem_t` | `0x0C` bytes |
| `List_t` | `0x14` bytes |
| `List_t.uxNumberOfItems` | `+0x00` |
| `List_t.pxIndex` | `+0x04` |
| `List_t.xListEnd` | `+0x08` |

The 20-byte list and 12-byte embedded end marker prove
`configUSE_LIST_DATA_INTEGRITY_CHECK_BYTES=0` and
`configUSE_MINI_LIST_ITEM=1`. The all-ones special comparison and end-marker
behavior prove 32-bit `TickType_t` with
`portMAX_DELAY=0xFFFFFFFF`.

The pristine source invokes `listTEST_LIST_INTEGRITY(pxList)` and
`listTEST_LIST_ITEM_INTEGRITY(pxNewListItem)` before traversal. Under the
recovered zero-integrity-byte configuration, both macros are empty. The
official function has no assertion load, comparison, failure branch, call,
or extra field access, matching that configuration exactly.

The candidate pins all target sizes and offsets with compile-time
assertions. It preserves the upstream preconditions: list and item pointers
must be non-null, the list must already have a valid end marker, and the item
must not already be linked. Adding defensive checks would not be an exact
source replacement.

There is no dependency on:

- a TCB, timer, scheduler, queue, or event-group object layout;
- interrupt state, privilege, TrustZone, FPU, MVE, or a port operation;
- `configASSERT`, callbacks, owner contents, or device registers;
- another source function or retained binary function.

## Whole-image control-flow topology

The installed application was scanned at every halfword for wide Thumb
`BL` and `B.W`, at every halfword for narrow unconditional and conditional
branches plus `CBZ`/`CBNZ`, and at every byte for possible stored 32-bit even
or odd/Thumb addresses.

### Entry and interior references

| Reference kind | Entry references | External interior references |
|---|---:|---:|
| `BL` | 5 | 0 |
| `B.W` | 0 | 0 |
| narrow `B` / conditional `B` / `CBZ` / `CBNZ` | 0 | 0 |
| aligned stored even/Thumb entry | 0 | n/a |
| aligned stored even/Thumb interior | n/a | 0 |

The ordered direct-call inventory is:

| Call site | Encoding | Recovered containing function and role |
|---|---|---|
| `0x004552A0` | `00f007ff` | `vTaskPlaceOnEventList`: insert the current TCB event item into the supplied event list |
| `0x00456000` | `00f057f8` | `prvAddCurrentTaskToDelayedList`: insert the current TCB state item into the overflow delayed list |
| `0x0045600E` | `00f050f8` | `prvAddCurrentTaskToDelayedList`: insert the current TCB state item into the current delayed list |
| `0x0047E95A` | `d7f7aafb` | `prvInsertTimerInActiveList`: insert the timer item into the overflow timer list |
| `0x0047E972` | `d7f79efb` | `prvInsertTimerInActiveList`: insert the timer item into the active timer list |

The SHA-256 of those call-site addresses packed in order as little-endian
32-bit words is
`a966051c31865cdddfdb9c0467d20f3bc9c5051e74baba0998c0f8b2664d03a9`.

The three containing functions are independently bounded:

| Recovered caller | Range | Bytes | SHA-256 |
|---|---|---:|---|
| `vTaskPlaceOnEventList` | `[0x00455282,0x004552AE)` | 44 | `2821a3c55358d806ed227c81a27746f8d9c35b648182fc9abb647de72ed9025d` |
| `prvAddCurrentTaskToDelayedList` | `[0x00455FA8,0x0045601E)` | 118 | `918fddb6333958607bec10181d39ffee564ca44f4db6cb43ee362cc62ba4f764` |
| `prvInsertTimerInActiveList` | `[0x0047E93C,0x0047E97A)` | 62 | `8428e1dc245cc497ecd09cece33787774eb8686182d994d2dccbec942930db62` |

Every caller's task- or timer-specific object knowledge ends before the
generic `List_t *` and embedded `ListItem_t *` cross the function boundary.
No containing object layout is therefore part of the replacement ABI.

### Stored-address false-positive closure

A byte-granular scan reports one apparent stored interior address:

```text
0x00528207 -> 0x004560C0
```

The four-byte window is `c0604500`, begins at an unaligned address, and is
not an address-bearing word. It crosses three Thumb instructions:

```text
00528204  ldrb.w  ip, [r6, r3]
00528208  cmp     r0, ip
0052820A  beq     ...
```

The matching bytes are the last byte of `ldrb.w`, the complete `cmp`, and
the first byte of `beq`. The aligned scan finds no entry or interior
pointer. The focused regression retains this false-positive window so a
future byte scan cannot promote instruction overlap to dispatch-table or
callback evidence.

## Isolated target implementation

The candidate source retains the direct upstream traversal and splice
semantics. A local Clang loop directive disables automatic traversal-loop
unrolling, keeping the source-owned target leaf compact and the emitted code
shape stable without altering behavior.

With the overlay's existing Cortex-M target flags at `-O2`, it emits exactly
one 58-byte Thumb function:

```text
push    {r7, lr}
ldr.w   ip, [r1]
adds.w  r2, ip, #1
beq     max_value
add.w   r2, r0, #8
mov     lr, r2
loop:
ldr     r2, [r2, #4]
ldr     r3, [r2]
cmp     r3, ip
bls     loop
b       splice
max_value:
ldr.w   lr, [r0, #16]
ldr.w   r2, [lr, #4]
splice:
str     r2, [r1, #4]
str     r1, [r2, #8]
str.w   lr, [r1, #8]
str.w   r1, [lr, #4]
str     r0, [r1, #16]
ldr     r1, [r0]
adds    r1, #1
str     r1, [r0]
pop     {r7, pc}
```

The emitted bytes and hash are:

```text
80b5d1f800c01cf1010207d000f108029646526813686345fad903e0d0f810e0def804204a609160c1f808e0cef80410086101680131016080bd
SHA-256 2afa2aa9cade7d864031311300ad5cc1f1e845fb67ad92a7c3ccb26f674d1cb7
```

Object inspection proves:

- one defined function: `open_cfw_freertos_list_insert`;
- no other function symbols;
- no undefined symbols;
- no `.text` relocations;
- no literal pool, external call, absolute address, or retained binary seam.

The source file, candidate host fixture, and pristine-upstream oracle
fixture are pinned in the focused test:

| Artifact | SHA-256 |
|---|---|
| source candidate | `e2592ce9acbcdaa3fbfaf30635f14fe77449310313eb6534a8a4b2b6f3b4be67` |
| candidate host fixture | `740210cbf8b14cfb29b73b8d2d69872f0f9d62b31523d59de56586c7b93547c3` |
| upstream oracle fixture | `063686b37d2802d8669939f3470e8c9f732b044dbf8748bf8ef92491243a941a` |

The independent oracle compiles pristine
`third_party/freertos-kernel/list.c` with the recovered list configuration;
it does not restate the insertion algorithm.

## Current source-consumer note

The stock topology above remains the immutable official-image evidence. The
current source-owned timer insertion helper constructs the retained odd
Thumb entry `0x004560B3` and calls it indirectly:

- `components/apollo_main/core_overlay/rtos_timer_insert.c`.

That consumer was not edited by this audit. A later integration should bind
it directly to `open_cfw_freertos_list_insert`. A complete redirect at the
official entry remains ABI-compatible for stock callers, but direct
source-to-source binding removes the avoidable absolute-address seam.

## Integration contract

A later overlay integration should:

1. register the isolated source candidate without weakening its recovered
   ABI assertions or compact-loop directive;
2. redirect the complete 54-byte official entry at `0x004560B2`, then use
   the established NOP-fill policy for the unused stock remainder;
3. preserve the ordinary
   `void vListInsert(List_t *, ListItem_t *)` AAPCS contract;
4. bind the already source-owned timer consumer directly to the new symbol;
5. retain the focused stock-body, caller, interior-reference, stored-pointer,
   target-object, and upstream-oracle checks;
6. verify overlay placement and branch range before firmware assembly;
7. keep the no-guard upstream preconditions and unsigned comparison
   behavior unchanged.

No official caller rewrite is required for correctness because a complete
entry redirect preserves the existing ABI.

## Validation performed

`tests/test_runtime_freertos_list_insert.py` performs ten focused checks:

- exact recovered list and item ABI;
- empty-list insertion parity with pristine V10.5.1;
- out-of-order insertion and bidirectional sorted links;
- FIFO order for equal values;
- unsigned high-bit ordering and repeated `portMAX_DELAY` insertion;
- item count, container, owner, value, index, and canary preservation;
- one bounded 58-byte target leaf with exact bytes/hash;
- zero target relocations and zero undefined symbols;
- pinned source, fixtures, upstream source, stock body, and boundaries;
- exact caller, narrow/interior-reference, stored-address, and caller-span
  topology.

The focused suite passes all ten tests. The isolated `vListInitialise`,
`vListInsertEnd`, and `uxListRemove` suites also pass in the combined list
regression.

All work remained isolated. No overlay descriptor, manifest, aggregate test,
shared source-coverage inventory, memory map, README, firmware artifact, or
hardware state was modified.
