# G2 FreeRTOS next atomic source-boundary audit

Status: implementation-ready source-replacement recommendation for official
G2 package `2.2.6.10`  
Scope: Apollo-main application only; read-only binary analysis; no firmware
assembly, signing, flashing, or hardware access

## Result

The next lowest-risk atomic FreeRTOS source-replacement boundary is the
standalone V10.5.1 `vListInsertEnd` function:

| Property | Recovered value |
|---|---|
| Official range | `0x0045609A...0x004560B1` |
| End-exclusive range | `[0x0045609A, 0x004560B2)` |
| Size | 24 bytes |
| SHA-256 | `78e2f1765fd9ba8e71098dababdfc4a4a1aabb73ed1f730d4fc24b94b54a2aba` |
| Upstream source | `third_party/freertos-kernel/list.c`, `vListInsertEnd` |
| Direct callers | one, `BL` at `0x00454AF0` |
| Stored entry/interior pointers | none |
| External branches into the interior | none |
| Calls made by the function | none |
| Port/TCB dependencies | none |

This is an unequivocal upstream-source match, not a lookalike inferred only
from a generic linked-list pattern. Every official instruction maps in order
to the field operations in FreeRTOS-Kernel V10.5.1 `vListInsertEnd`, using the
exact recovered `List_t` and `ListItem_t` offsets. The only official caller is
the standard `vTaskDelete` path. It passes the task's generic state-list item
at TCB `+0x04`, but `vListInsertEnd` treats it only as a `ListItem_t` and never
reads the G2-specific TCB stack-depth field at `+0x54`.

The function can therefore be sourced directly from the authenticated
FreeRTOS snapshot under its retained MIT license. It does not require a
focused disassembly to recover a vendor algorithm or a G2 port shim.

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

The comparator is the authenticated FreeRTOS-Kernel V10.5.1 snapshot:

| Property | Value |
|---|---|
| Commit | `def7d2df2b0506d3d249334974f51e427c17a41c` |
| Tree | `7496dfa815c3cea2f45a090c6e92d113f494b930` |
| `list.c` bytes | `10,338` |
| `list.c` SHA-256 | `db5c169cf3efd68da1c6a923ac84eebc724d602c940bde0b9b5f01f05028fde4` |
| `list.c` Git blob | `afcae87f11413a14a5a95138fb9bffb6787826c4` |

The source function is
[`vListInsertEnd`](../../third_party/freertos-kernel/list.c), immediately
following `vListInitialiseItem`. The snapshot verifier authenticates that file
and its license rather than relying on a locally reconstructed copy.

## Exact binary-to-source proof

The complete official body is:

```text
0045609A  ldr   r2, [r0, #4]
0045609C  str   r2, [r1, #4]
0045609E  ldr   r3, [r2, #8]
004560A0  str   r3, [r1, #8]
004560A2  ldr   r3, [r2, #8]
004560A4  str   r1, [r3, #4]
004560A6  str   r1, [r2, #8]
004560A8  str   r0, [r1, #16]
004560AA  ldr   r1, [r0]
004560AC  adds  r1, r1, #1
004560AE  str   r1, [r0]
004560B0  bx    lr
```

With `r0 = pxList`, `r1 = pxNewListItem`, and the proven list ABI, those
instructions are exactly:

1. load `pxList->pxIndex`;
2. set the new item's `pxNext` to the index;
3. set the new item's `pxPrevious` to `pxIndex->pxPrevious`;
4. make the previous item point forward to the new item;
5. make the index point backward to the new item;
6. set `pxNewListItem->pxContainer = pxList`;
7. increment `pxList->uxNumberOfItems`;
8. return.

That is the complete released V10.5.1 algorithm, including its ordering. There
are no omitted checks, calls, barriers, task fields, trace hooks, or
port-specific instructions.

The official bytes are:

```text
42684a6093688b6093685960916008610168491c01607047
```

The neighboring boundaries are also unambiguous:

| Range | Recovered function | Bytes | SHA-256 |
|---|---|---:|---|
| `[0x0045607C,0x0045609A)` | `vListInitialise` | 30 | `6ea73f3bfc40bb5776bb925a560b7e6e2d2103e96a87756847e625860cdc351d` |
| `[0x0045609A,0x004560B2)` | `vListInsertEnd` | 24 | `78e2f1765fd9ba8e71098dababdfc4a4a1aabb73ed1f730d4fc24b94b54a2aba` |
| `[0x004560B2,0x004560E8)` | `vListInsert` | 54 | `10c1fa85d530a003183c42d2fc11b80386669d011ce19f7a9c2a6d32516d4c59` |
| `[0x004560E8,0x0045610E)` | `uxListRemove` | 38 | `e1ca0b525effd60568d00101c08010374cebfd3c80ee6ade4fec4da54bcb8794` |

The preceding bytes `0x00456036...0x0045607B` are a literal pool, not an
earlier entry or fall-through body. `uxListRemove` is followed by a two-byte
alignment word at `0x0045610E`.

## ABI and configuration dependencies

The replacement must preserve the already recovered 32-bit ABI:

| Type or field | Size/offset |
|---|---:|
| Pointer | 4 bytes |
| `UBaseType_t` | 4 bytes |
| `TickType_t` | 4 bytes |
| `ListItem_t` | `0x14` bytes |
| `ListItem_t.pxNext` | `+0x04` |
| `ListItem_t.pxPrevious` | `+0x08` |
| `ListItem_t.pxContainer` | `+0x10` |
| `List_t` | `0x14` bytes |
| `List_t.uxNumberOfItems` | `+0x00` |
| `List_t.pxIndex` | `+0x04` |

The relevant V10.5.1 configuration is:

- `configUSE_LIST_DATA_INTEGRITY_CHECK_BYTES=0`. The 20-byte list item,
  20-byte list, and absence of integrity-check loads/assertions prove this.
- `configUSE_MINI_LIST_ITEM=1`. The 12-byte end marker and 20-byte `List_t`
  prove the released mini-list layout.
- `configUSE_16_BIT_TICKS=0`. List values are 32-bit, although this specific
  function does not read `xItemValue`.
- `mtCOVERAGE_TEST_DELAY()` is empty in the production build.
- `configLIST_VOLATILE`, whether empty or `volatile`, does not change this
  structure layout or algorithm.

These are ordinary V10.5.1 configuration selections. None requires a vendor
source fork. The replacement should compile with explicit `sizeof` and
`offsetof` assertions so a later configuration change cannot silently alter
the binary ABI.

Global `configASSERT` support does not add a call here:
`listTEST_LIST_INTEGRITY` and `listTEST_LIST_ITEM_INTEGRITY` expand to no-ops
when list integrity-check bytes are disabled. This explains why the official
function remains a leaf even though assertions are enabled elsewhere.

## Whole-image closure

The complete 3,523,364-byte installed application was scanned at every
halfword for Thumb direct branches and at every byte for possible stored
32-bit addresses.

### Direct control-flow references

| Reference kind | Entry references | External interior references |
|---|---|---|
| `BL` | `0x00454AF0 -> 0x0045609A` | none |
| `B.W` | none | none |
| narrow `B` / conditional `B` / `CBZ` / `CBNZ` | none | none |

The SHA-256 of the ordered little-endian direct-caller address list
`[0x00454AF0]` is
`9e0a01c401e10b8036c42c32899ebf5884ea2f0a48689eefe8a9535b4106def1`.

### Stored-address references

The byte-granular scan found:

- no stored even entry address `0x0045609A`;
- no stored Thumb entry address `0x0045609B`;
- no stored even interior address;
- no stored odd/Thumb interior address.

There is consequently no vector-table ownership, callback registration,
jump-table entry, or hidden interior entry that has to be rebound with the
function.

### Sole caller

The call is inside the official `vTaskDelete` implementation:

| Property | Value |
|---|---|
| Caller function range | `[0x00454AAE,0x00454B4C)` |
| Caller bytes | 158 |
| Caller SHA-256 | `fed4eb28935bf7034f3f1893518e7de056995a5083d42863ab007e9e74de2597` |
| Call instruction | `0x00454AF0` |
| List argument | `0x20073D38`, `xTasksWaitingTermination` |
| Item argument | deleting TCB `+0x04`, `xStateListItem` |

The surrounding path first removes the state item and any event item. If the
task being deleted is the current task, it appends that state item to
`xTasksWaitingTermination` and increments the pending-cleanup count. This is
the released V10.5.1 `vTaskDelete` relationship and explains the one
out-of-line call.

Other kernel sites contain compiler-inlined list insertion operations.
Replacing this entry intentionally does not claim those inlined bytes as
source-owned. It replaces one complete callable boundary and its one official
call path without expanding the patch into `tasks.c`.

## Why this boundary is lower risk than its neighbors

| Candidate | Bytes | Direct callers | Additional behavior |
|---|---:|---:|---|
| `vListInitialise` | 30 | 12 | end-marker construction and `portMAX_DELAY` |
| **`vListInsertEnd`** | **24** | **1** | fixed-offset pointer splice only |
| `vListInsert` | 54 | 5 | sorted traversal and `portMAX_DELAY` special case |
| `uxListRemove` | 38 | 10 | index repair, detach, decrement, return value |

All four are strong future source candidates and all four have clean entry,
interior-branch, and stored-pointer closure. `vListInsertEnd` is the best
first step because it has the smallest body, fewest callers, no loop, no
conditional branch, no callee, and no return-value consumer.

The remaining three should be integrated as later independent boundaries,
not bundled into this patch merely because they are adjacent in `list.c`.
That keeps failures attributable and prevents a first list-layer change from
simultaneously affecting initialization, sorted delay insertion, and removal.

## Implementation contract

A source replacement should:

1. use the authenticated V10.5.1 `vListInsertEnd` body and retained MIT notice;
2. expose a project-prefixed entry such as
   `open_cfw_freertos_list_insert_end`;
3. define the exact 32-bit `List_t`/`ListItem_t` ABI or include the pinned
   upstream headers under the recovered configuration;
4. assert the sizes and field offsets listed above at compile time;
5. redirect the complete 24-byte official entry at `0x0045609A` and fill the
   remainder with the overlay's established NOP policy;
6. test empty, one-item, multi-item, and non-end `pxIndex` insertion cases
   against a pristine V10.5.1 oracle;
7. pin the official body hash, the sole caller, the absence of interior
   branches, and the absence of stored entry/interior pointers;
8. leave the neighboring three official `list.c` functions unchanged until
   they receive their own source boundaries.

No direct caller rewrite is required because the entry redirect preserves the
existing AAPCS call ABI.

## Validation performed

The authenticated snapshot verifier passed:

```text
FreeRTOS-Kernel V10.5.1 official snapshot, unsigned annotated tag,
48 upstream files, dual unselected IAR Cortex-M55 port alternatives,
MIT license, Git blobs, and SHA-256 pins: OK
```

The existing focused G2 port analyzer also passed all package, vector,
21-span, port, TCB, tick, and heap checks. The additional read-only topology
scan reproduced the function/caller hashes and the closure counts reported
above.

## Decision

Use the pinned FreeRTOS-Kernel V10.5.1 implementation of `vListInsertEnd`
directly. It is a fully identified open-source library boundary, and focused
disassembly has already resolved every configuration and ABI detail needed
for this function. No decompilation or behavioral re-creation is warranted.
