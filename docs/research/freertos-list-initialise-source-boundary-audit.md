# G2 FreeRTOS list-initialisation source-boundary audit

Status: source-integrated in the Apollo-main core overlay for official G2
package `2.2.6.10`  
Scope: Apollo-main application; offline overlay and package assembly only,
with no signing, flashing, or hardware access

## Result

The next source-safe FreeRTOS-Kernel V10.5.1 list leaf is
`vListInitialise`:

| Property | Recovered value |
|---|---|
| Official range | `0x0045607C...0x00456099` |
| End-exclusive range | `[0x0045607C,0x0045609A)` |
| Size | 30 bytes |
| SHA-256 | `6ea73f3bfc40bb5776bb925a560b7e6e2d2103e96a87756847e625860cdc351d` |
| Upstream source | `third_party/freertos-kernel/list.c`, `vListInitialise` |
| Official direct call sites | 12 in five containing functions |
| Stored entry/interior pointers | none |
| External branches into the interior | none |
| Calls made by the function | none |
| Target source-object size | 22 bytes |
| Target relocations/undefined symbols | zero/zero |

This is a complete, exact released-source boundary. It constructs an empty
FreeRTOS list by pointing the traversal index and both end-marker links at
the embedded mini end marker, setting that marker's sort value to
`portMAX_DELAY`, and setting the item count to zero.

`vListInitialiseItem` was considered first because its upstream operation is
smaller: it clears only `ListItem_t.pxContainer`. The official application,
however, has no standalone callable body for it in the recovered list
cluster. Its operation was inlined into object-initialisation paths. There
is therefore no stock function span that can be independently redirected,
hashed, or given a closed caller topology. Recreating it as a source helper
would be useful only after the containing task/timer paths become
source-owned; it is not the next binary-to-source replacement boundary.

The integrated source is:

`components/apollo_main/core_overlay/runtime_freertos_list_initialise.c`

It is registered as a complete entry redirect in the core overlay. The file
has no include, external declaration, absolute call seam, device address, or
binary dependency. It retains the upstream MIT notice and uses
project-prefixed types and a project-prefixed entry so it cannot collide with
later use of the complete FreeRTOS headers.

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

The repository snapshot verifier authenticates the annotated tag, peeled
commit, tree, selected blobs, and retained MIT license. No unresolved
Cortex-M55 port choice affects this leaf: all behavior is fixed by the list
layout and the recovered `portMAX_DELAY` value.

## Exact binary-to-source proof

The complete official body is:

```text
0045607C  adds.w  r1, r0, #8
00456080  str     r1, [r0, #4]
00456082  movs.w  r1, #-1
00456086  str     r1, [r0, #8]
00456088  adds.w  r1, r0, #8
0045608C  str     r1, [r0, #12]
0045608E  adds.w  r1, r0, #8
00456092  str     r1, [r0, #16]
00456094  movs    r1, #0
00456096  str     r1, [r0]
00456098  bx      lr
```

With `r0 = List_t *pxList`, the instruction stream maps one-to-one to the
pristine V10.5.1 operation:

1. form `&pxList->xListEnd` at `pxList + 0x08`;
2. set `pxList->pxIndex` at `+0x04` to the end marker;
3. set `xListEnd.xItemValue` at `+0x08` to `0xFFFFFFFF`;
4. set `xListEnd.pxNext` at `+0x0C` to the end marker;
5. set `xListEnd.pxPrevious` at `+0x10` to the end marker;
6. set `pxList->uxNumberOfItems` at `+0x00` to zero;
7. return without a stack frame or callee.

The official bytes are:

```text
10f1080141605ff0ff31816010f10801c16010f108010161002101607047
```

The boundaries are independently closed:

| Range | Recovered content | Bytes | SHA-256 |
|---|---|---:|---|
| `[0x00456036,0x0045607C)` | preceding literal-pool region | 70 | `ee4e597cbb3d06e3306132a9b0725e82ae257b7ff2331cf2abd070e85d6b7fc7` |
| `[0x0045607C,0x0045609A)` | `vListInitialise` | 30 | `6ea73f3bfc40bb5776bb925a560b7e6e2d2103e96a87756847e625860cdc351d` |
| `[0x0045609A,0x004560B2)` | `vListInsertEnd` | 24 | `78e2f1765fd9ba8e71098dababdfc4a4a1aabb73ed1f730d4fc24b94b54a2aba` |

The body starts at its first end-marker address calculation, ends at its own
`bx lr`, and contains no literal or alignment bytes.

## Recovered ABI and configuration

The callable ABI is the ordinary 32-bit Arm procedure-call ABI:

| Item | Contract |
|---|---|
| Argument | `r0 = List_t *pxList` |
| Return | `void` |
| Official scratch registers | `r1`, condition flags |
| Stack use | none |
| Calls or tail calls | none |

The official offsets prove the complete required data ABI:

| Type or field | Size/offset |
|---|---:|
| Pointer | 4 bytes |
| `UBaseType_t` | 4 bytes |
| `TickType_t` | 4 bytes |
| `ListItem_t` | `0x14` bytes |
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
`configUSE_MINI_LIST_ITEM=1`. The 32-bit all-ones sort value proves
32-bit `TickType_t` and `portMAX_DELAY=0xFFFFFFFF`. Together with the
observed pointer writes, that closes every configuration parameter used by
this released source body.

The candidate pins the target-only sizes and offsets with compile-time
assertions. It preserves the upstream behavior exactly: no null check,
alignment check, scheduler guard, or additional initialization is added.

There is no dependency on:

- a TCB, timer, queue, or event-group object layout;
- scheduler state, interrupt state, privilege, TrustZone, FPU, or MVE;
- `configASSERT`, callbacks, owner fields, or device registers;
- another source or retained binary function.

## Whole-image control-flow topology

The installed application was scanned at every halfword for wide Thumb
`BL` and `B.W` encodings, at every halfword for narrow unconditional and
conditional branches plus `CBZ`/`CBNZ`, and at every byte for possible
stored 32-bit even or odd/Thumb addresses.

### Entry and interior references

| Reference kind | Entry references | External interior references |
|---|---:|---:|
| `BL` | 12 | 0 |
| `B.W` | 0 | 0 |
| narrow `B` / conditional `B` / `CBZ` / `CBNZ` | 0 | 0 |
| aligned stored even/Thumb entry | 0 | n/a |
| aligned stored even/Thumb interior | n/a | 0 |

The ordered direct-call inventory is:

| Call site | Encoding | Recovered containing function and role |
|---|---|---|
| `0x004415A0` | `14f06cfd` | `xQueueGenericReset`: initialize one queue event list |
| `0x004415A8` | `14f068fd` | `xQueueGenericReset`: initialize the other queue event list |
| `0x0045569E` | `00f0edfc` | `prvInitialiseTaskLists`: initialize a ready list in the priority loop |
| `0x004556AE` | `00f0e5fc` | `prvInitialiseTaskLists`: initialize the first delayed list |
| `0x004556B8` | `00f0e0fc` | `prvInitialiseTaskLists`: initialize the second delayed list |
| `0x004556BE` | `00f0ddfc` | `prvInitialiseTaskLists`: initialize the pending-ready list |
| `0x004556C6` | `00f0d9fc` | `prvInitialiseTaskLists`: initialize the termination-waiting list |
| `0x004556CE` | `00f0d5fc` | `prvInitialiseTaskLists`: initialize the suspended-task list |
| `0x0047EACA` | `d7f7d7fa` | `prvCheckForValidListAndQueue`: initialize active timer list 1 |
| `0x0047EAD2` | `d7f7d3fa` | `prvCheckForValidListAndQueue`: initialize active timer list 2 |
| `0x0047EBCC` | `d7f756fa` | `xEventGroupCreateStatic`: initialize the event-group wait list |
| `0x0047EBEC` | `d7f746fa` | `xEventGroupCreate`: initialize the event-group wait list |

The SHA-256 of those call-site addresses packed in order as little-endian
32-bit words is
`5e740bd209e577e749d813825efdc0934ffba60442ae33968527992d4ce27e9d`.

The 12 static `BL` sites are not the total number of list initializations
performed during scheduler setup. The first
`prvInitialiseTaskLists` call is inside the priority loop and initializes
56 ready lists; the five later sites initialize one global list each. The
single source boundary remains generic in every case because only a
`List_t *` crosses it.

The five containing functions are independently bounded:

| Recovered caller | Range | Bytes | SHA-256 |
|---|---|---:|---|
| `xQueueGenericReset` | `[0x00441516,0x004415CA)` | 180 | `e5b7c5e487374e7966b8f2febb8aa1b804efa516c92f9e436a369ec5df100ad8` |
| `prvInitialiseTaskLists` | `[0x0045568C,0x004556E0)` | 84 | `db9aad99c9dfd14cb9f2eb453dd86af05b11ed049eacf8771f25a82382894723` |
| `prvCheckForValidListAndQueue` | `[0x0047EAB8,0x0047EAF6)` | 62 | `e34431d020471c30b8e3d3fed60fb15e83b77f49ee2921fcdae5e3be7d589ece` |
| `xEventGroupCreateStatic` | `[0x0047EB94,0x0047EBD8)` | 68 | `8bbcf73cd3d7f93fcd7564b8c5bd06d4936fb21859cfca99017c2a8c3f5dfc6c` |
| `xEventGroupCreate` | `[0x0047EBD8,0x0047EBF8)` | 32 | `fe1edcf1a00dfbb69d8015b5958d6c24ffa6591e2fac90bb4e44ed8ebd33baf5` |

### Stored-address false-positive closure

A byte-granular scan reports two apparent stored copies of the even entry
address:

```text
0x005DD143 -> 0x0045607C
0x005DD20D -> 0x0045607C
```

Both four-byte windows are `7c604500`, both start at unaligned addresses,
and neither represents an address-bearing word. Each window crosses three
Thumb instructions:

```text
005DD140  movw  ip, #0xffff
005DD144  cmp   r0, ip
005DD146  beq   ...

005DD20A  movw  ip, #0xffff
005DD20E  cmp   r0, ip
005DD210  beq   ...
```

The matching bytes are the last byte of `movw`, all of `cmp`, and the first
byte of `beq`. The aligned word scan finds no entry or interior pointer.
These two overlapping instruction windows are retained in the regression
test so a future scan cannot accidentally promote them to callback or
dispatch-table evidence.

## Isolated target implementation

With the overlay's existing Cortex-M target flags at `-O2`, the source
candidate emits exactly one 22-byte Thumb function:

```text
mov.w  r1, #-1
mov    r2, r0
str    r1, [r2, #8]!
movs   r1, #0
str    r2, [r0, #4]
str    r2, [r0, #12]
str    r2, [r0, #16]
str    r1, [r0]
bx     lr
```

The emitted bytes and hash are:

```text
4ff0ff31024642f8081f00214260c260026101607047
SHA-256 608e9d4ec0accd8c26784960dbc2dc4bab55e0d65a29ffcba9ecf9e2576eb96b
```

The compiler reorders independent stores relative to the official body, but
the final list state and externally observable upstream semantics are
identical. The source-vs-pristine oracle tests exercise poisoned initial
states, varied values, exact end-marker construction, repeat
initialization, and surrounding canaries.

Object inspection proves:

- one defined function:
  `open_cfw_freertos_list_initialise`;
- no other function symbols;
- no undefined symbols;
- no `.text` relocations;
- no literal pool, call, branch seam, or absolute address;
- no retained binary-blob dependency.

The source file, host fixture, and pristine-upstream oracle fixture are
pinned by SHA-256 in the focused test:

| Artifact | SHA-256 |
|---|---|
| source candidate | `a77b7c99f2cd092b80caae0c247cae708ba52a4cd89f723274ddc93fc2442733` |
| candidate host fixture | `f4831aeae6a27b0b498e5716f61e57a81016b943a18bc072a7bc2176bd4ce11b` |
| upstream oracle fixture | `a8eb4eafa362d4097b533114ba60748553f851634a91fe8824eb0d2701fae112` |

## Current source-consumer note

The stock caller topology above is immutable evidence from the official
application. The two earlier OpenCFW source replacements that construct the
retained odd Thumb entry `0x0045607D` and call it indirectly are:

- `components/apollo_main/core_overlay/rtos_event_group_create.c`;
- `components/apollo_main/core_overlay/rtos_timer_runtime_initialize.c`.

The later source-owned `open_cfw_freertos_task_lists_initialize` consumer does
not repeat that absolute-address seam. Its six strict `R_ARM_THM_CALL`
relocations bind directly to `open_cfw_freertos_list_initialise`, and its
header forward-declares the provider's exact structure tag. The explicit
`(struct open_cfw_freertos_list_initialise_list *)(void *)` conversions close
the C prototype contract without changing the recovered 20-byte list ABI.

The entry redirect at the complete official `vListInitialise` function remains
ABI-compatible for the two older source consumers and all retained stock
callers. Direct source-to-source binding is the required pattern for new
consumers because it avoids adding another absolute-address seam.

## Production integration result

The production overlay now:

1. registers the source implementation without weakening its recovered ABI
   assertions;
2. redirects the complete 30-byte official entry at `0x0045607C` with
   `replace_freertos_list_initialise` and applies the established NOP-fill
   policy to the unused remainder;
3. preserves the ordinary `void vListInitialise(List_t *)` AAPCS contract;
4. leaves official callers unchanged because the complete entry redirect
   preserves their ABI;
5. binds the newer `open_cfw_freertos_task_lists_initialize` consumer directly
   to the source symbol through six strict relocations, while retaining the two
   older absolute-entry consumers documented above as explicit compatibility
   seams;
6. retains the focused stock-body, caller, interior-reference, stored-pointer,
   object-shape, and upstream-oracle tests; and
7. leaves `vListInitialiseItem` as an inlined-source concern rather than
   inventing a nonexistent official redirect boundary.

The canonical manifest classifies the 30-byte stock span as a generated source
entry replacement. Aggregate overlay, component, package, coverage, and
dual-profile pins fail closed around the active provider and its consumers.

## Validation performed

`tests/test_runtime_freertos_list_initialise.py` performs eight focused
checks:

- exact recovered list ABI;
- candidate parity with pristine V10.5.1 `list.c`;
- varied poisoned initial state and complete state overwrite;
- idempotent repeat initialization and canary preservation;
- one bounded 22-byte target leaf with exact bytes/hash;
- zero target relocations and zero undefined symbols;
- pinned source, fixtures, upstream source, stock body, and boundaries;
- exact caller, interior-reference, stored-address, and caller-span
  topology.

The focused suite passes all eight tests. The neighboring `vListInsertEnd` and
`uxListRemove` suites also pass in the combined regression run. Production
registration is additionally covered by the aggregate overlay, scheduler,
manifest, coverage, and toolchain-profile tests.

The original boundary analysis and candidate validation were isolated. The
subsequent production promotion updated the overlay descriptor, manifest,
aggregate tests, shared coverage inventory, and reproducible firmware
artifacts. Neither phase signed or flashed firmware or changed hardware state.
