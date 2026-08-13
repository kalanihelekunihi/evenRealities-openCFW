# G2 FreeRTOS list-removal source-boundary audit

Status: implementation-ready source-replacement recommendation for official
G2 package `2.2.6.10`  
Scope: Apollo-main application only; read-only binary analysis; no firmware
assembly, signing, flashing, or hardware access

## Result

The next lowest-risk exact-upstream `list.c` boundary after
`vListInsertEnd` is FreeRTOS-Kernel V10.5.1 `uxListRemove`:

| Property | Recovered value |
|---|---|
| Official range | `0x004560E8...0x0045610D` |
| End-exclusive range | `[0x004560E8,0x0045610E)` |
| Size | 38 bytes |
| SHA-256 | `e1ca0b525effd60568d00101c08010374cebfd3c80ee6ade4fec4da54bcb8794` |
| Upstream source | `third_party/freertos-kernel/list.c`, `uxListRemove` |
| Official direct callers | ten `BL` sites in nine functions |
| Stored entry/interior pointers | none |
| External branches into the interior | none |
| Calls made by the function | none |
| Port, TCB, or device dependencies | none |

This is an exact released-source match. The complete official body performs
the same ordered field accesses as pristine V10.5.1: unlink the item, repair
the list traversal index only when it points at the removed item, clear the
item's container, decrement the list count, and return the remaining count.
It is a leaf and uses only the recovered generic `ListItem_t` and `List_t`
ABI.

`vListInitialise` is eight bytes smaller, but it writes `portMAX_DELAY` and
constructs the configuration-selected mini end marker. `uxListRemove` has no
tick constant, end-marker operation, traversal loop, port macro, task field,
vendor global, or callee. That makes it the safer next independent boundary
despite its larger official caller set.

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

The repository snapshot verifier authenticates the official annotated tag,
peeled commit, tree, selected Git blobs, and retained MIT license. Its
unresolved Cortex-M55 port-variant choice does not affect this function:
`uxListRemove` includes no portable-layer operation.

## Exact binary-to-source proof

The complete official body is:

```text
004560E8  ldr   r1, [r0, #16]
004560EA  ldr   r2, [r0, #8]
004560EC  ldr   r3, [r0, #4]
004560EE  str   r2, [r3, #8]
004560F0  ldr   r2, [r0, #4]
004560F2  ldr   r3, [r0, #8]
004560F4  str   r2, [r3, #4]
004560F6  ldr   r2, [r1, #4]
004560F8  cmp   r2, r0
004560FA  bne   0x00456100
004560FC  ldr   r2, [r0, #8]
004560FE  str   r2, [r1, #4]
00456100  movs  r2, #0
00456102  str   r2, [r0, #16]
00456104  ldr   r0, [r1]
00456106  subs  r0, r0, #1
00456108  str   r0, [r1]
0045610A  ldr   r0, [r1]
0045610C  bx    lr
```

With `r0 = pxItemToRemove` on entry and the proven list ABI, this maps
one-to-one to the released source:

1. load `pxItemToRemove->pxContainer` into `pxList`;
2. set `pxItemToRemove->pxNext->pxPrevious` to
   `pxItemToRemove->pxPrevious`;
3. set `pxItemToRemove->pxPrevious->pxNext` to
   `pxItemToRemove->pxNext`;
4. compare `pxList->pxIndex` with the item;
5. when equal, set the index to the item's previous node;
6. set `pxItemToRemove->pxContainer` to `NULL`;
7. decrement `pxList->uxNumberOfItems`;
8. reload and return the remaining item count.

The official bytes are:

```text
0169826843689a60426883685a604a68824201d182684a60002202610868401e086008687047
```

The boundaries are independently closed by the adjacent functions and
alignment:

| Range | Recovered content | Bytes | SHA-256 |
|---|---|---:|---|
| `[0x004560B2,0x004560E8)` | `vListInsert` | 54 | `10c1fa85d530a003183c42d2fc11b80386669d011ce19f7a9c2a6d32516d4c59` |
| `[0x004560E8,0x0045610E)` | `uxListRemove` | 38 | `e1ca0b525effd60568d00101c08010374cebfd3c80ee6ade4fec4da54bcb8794` |
| `[0x0045610E,0x00456110)` | alignment word | 2 | not part of either function |

The selected body begins at the first container load, ends at its own
`bx lr`, and has no literal pool. The following function starts with
`push.w {r4,r5,r6,r7,r8,lr}` at `0x00456110`.

## Semantics, ABI, and configuration closure

The callable ABI is the ordinary 32-bit Arm procedure-call ABI:

| Item | Contract |
|---|---|
| Argument | `r0 = ListItem_t *pxItemToRemove` |
| Return | `r0 = UBaseType_t` remaining item count |
| Scratch registers | `r1`, `r2`, `r3`, condition flags |
| Stack use | none |
| Calls or tail calls | none |

The only data-layout requirements are:

| Type or field | Size/offset |
|---|---:|
| Pointer | 4 bytes |
| `UBaseType_t` | 4 bytes |
| `ListItem_t` | `0x14` bytes |
| `ListItem_t.pxNext` | `+0x04` |
| `ListItem_t.pxPrevious` | `+0x08` |
| `ListItem_t.pxContainer` | `+0x10` |
| `List_t.uxNumberOfItems` | `+0x00` |
| `List_t.pxIndex` | `+0x04` |

The recovered 20-byte `ListItem_t` proves
`configUSE_LIST_DATA_INTEGRITY_CHECK_BYTES=0` for this ABI. A replacement
must pin that layout with compile-time size and offset assertions.

There is no behavioral dependency on:

- `portMAX_DELAY`, `TickType_t`, or `configUSE_16_BIT_TICKS`;
- `MiniListItem_t` or `configUSE_MINI_LIST_ITEM`;
- a scheduler, interrupt, privilege, TrustZone, FPU, or MVE port macro;
- `configASSERT`, a TCB layout, a timer layout, or an Apollo device address;
- any owner value or item sort value.

The pristine source contains `mtCOVERAGE_TEST_DELAY()` between unlinking and
index repair, and `mtCOVERAGE_TEST_MARKER()` on the non-repair branch.
V10.5.1 defines both as empty unless an external decision-coverage build
overrides them. The official body contains no instructions or call seam for
either macro, exactly matching the normal released configuration.

`configLIST_VOLATILE` can qualify list fields, but it neither changes the
recovered field layout nor introduces a port dependency. The official reload
of the count before return preserves the released source's observable access
sequence.

The function assumes the ordinary FreeRTOS precondition that the item is
currently linked and has a valid non-null container. It deliberately has no
null or membership guard. Adding one would not be an exact upstream
replacement.

## Whole-image control-flow and stored-address closure

The complete installed application was scanned at every halfword for wide
Thumb `BL` and `B.W` encodings, at every halfword for narrow unconditional
and conditional `B`, `CBZ`, and `CBNZ`, and at every byte for possible
stored 32-bit even or odd/Thumb addresses.

### Entry and interior references

| Reference kind | Entry references | External interior references |
|---|---:|---:|
| `BL` | 10 | 0 |
| `B.W` | 0 | 0 |
| narrow `B` / conditional `B` / `CBZ` / `CBNZ` | 0 | 0 |
| stored even entry `0x004560E8` | 0 | n/a |
| stored Thumb entry `0x004560E9` | 0 | n/a |
| stored even or odd/Thumb interior | n/a | 0 |

The `BNE` at `0x004560FA` is wholly internal and targets
`0x00456100`. No external control flow enters after the function's first
instruction.

The ordered official caller list is:

```text
0x00454AC4
0x00454AD2
0x00454C9A
0x004556F2
0x00455908
0x004559B8
0x00455A84
0x00455FB8
0x0047E84C
0x0047E9C2
```

The SHA-256 of those addresses packed in that order as little-endian
32-bit words is
`5e769191048e16c897132bef83eff5c6188ee79f6fd8bacde078d220789e01ee`.

### Official caller inventory

| Call site | Encoding | Recovered V10.5.1 caller and role |
|---|---|---|
| `0x00454AC4` | `01f010fb` | `vTaskDelete`: remove TCB state item at `+0x04` |
| `0x00454AD2` | `01f009fb` | `vTaskDelete`: conditionally remove TCB event item at `+0x18` |
| `0x00454C9A` | `01f025fa` | `vTaskPrioritySet`: remove a ready-state item before priority-list reinsertion |
| `0x004556F2` | `00f0f9fc` | `prvCheckTasksWaitingTermination`: remove a deleted task's state item |
| `0x00455908` | `00f0eefb` | `xTaskPriorityInherit`: move a ready mutex holder after inheritance |
| `0x004559B8` | `00f096fb` | `xTaskPriorityDisinherit`: move the current ready task after disinheritance |
| `0x00455A84` | `00f030fb` | `vTaskPriorityDisinheritAfterTimeout`: move a ready mutex holder |
| `0x00455FB8` | `00f096f8` | `prvAddCurrentTaskToDelayedList`: remove the current TCB state item |
| `0x0047E84C` | `d7f74cfc` | `prvProcessExpiredTimer`: remove the timer list item at timer `+0x04` |
| `0x0047E9C2` | `d7f791fb` | `prvProcessReceivedCommands`: conditionally remove timer item `+0x04` |

The nine containing functions are independently bounded:

| Recovered caller | Range | Bytes | SHA-256 |
|---|---|---:|---|
| `vTaskDelete` | `[0x00454AAE,0x00454B4C)` | 158 | `fed4eb28935bf7034f3f1893518e7de056995a5083d42863ab007e9e74de2597` |
| `vTaskPrioritySet` | `[0x00454C12,0x00454CEC)` | 218 | `fa38a23c007a168f79051504b23dd4087eb7845da2c3fb933c8083c8ade31152` |
| `prvCheckTasksWaitingTermination` | `[0x004556E0,0x0045571C)` | 60 | `0c2e27502e5f60b2ac93bddd8ca6ebb41d183d24da456f1cec160b1ec34818b1` |
| `xTaskPriorityInherit` | `[0x004558CC,0x0045596E)` | 162 | `7a03706199fa57820990f7cd15a4c9cc2a222b85e35697625af41eb7c4182806` |
| `xTaskPriorityDisinherit` | `[0x0045596E,0x00455A12)` | 164 | `34e2c3a8b02daf3ea3f8d3d382ef3d802d48f4d65ee26fa0353d0faab51c7e93` |
| `vTaskPriorityDisinheritAfterTimeout` | `[0x00455A1C,0x00455ACA)` | 174 | `457932fc906a97ce86aa034cd06c428db6d4943538b18c58e22775f1acc6ee68` |
| `prvAddCurrentTaskToDelayedList` | `[0x00455FA8,0x0045601E)` | 118 | `918fddb6333958607bec10181d39ffee564ca44f4db6cb43ee362cc62ba4f764` |
| `prvProcessExpiredTimer` | `[0x0047E83A,0x0047E878)` | 62 | `94ed9421f98b5f3dd08dd15024fb413dcee8c28ef9f3b9d6c548b11e56b26335` |
| `prvProcessReceivedCommands` | `[0x0047E97A,0x0047EA90)` | 278 | `7b11858bca279a51a5b6b9565b9ba9b6c5da9eed337ef50206f57ac314f4257f` |

This inventory also explains why the larger caller count does not widen the
replacement ABI: every call passes only a generic embedded `ListItem_t *`,
and every result consumer expects the standard 32-bit remaining-count
return.

## Current OpenCFW timer-consumer note

The raw official-image list above is the immutable topology used to pin the
stock boundary. In the current OpenCFW build, the two official timer caller
functions are already replaced at their entries by source implementations.
Their source equivalents still reach retained `uxListRemove` through the
explicit odd Thumb address `0x004560E9`:

- `components/apollo_main/core_overlay/rtos_timer_expire.c`;
- `components/apollo_main/core_overlay/rtos_timer_drain.c`.

The compiler materializes that constant with `MOVW`/`MOVT` followed by
`BLX`; it is not a stored word and therefore is intentionally not counted as
an official-image stored-address reference or a direct `BL` reference.

A source integration should preferably bind both timer consumers directly to
the new project-prefixed source symbol. Keeping their absolute calls is still
functionally compatible if the complete stock entry receives the normal
non-linking `B.W` redirect, but direct symbol binding removes an avoidable
retained-address seam.

## Why this is an atomic safe boundary

| Candidate | Bytes | Official direct callers | Configuration or algorithmic exposure |
|---|---:|---:|---|
| `vListInitialise` | 30 | 12 | writes `portMAX_DELAY` and constructs configured end marker |
| **`uxListRemove`** | **38** | **10** | fixed-offset unlink/index/count primitive |
| `vListInsert` | 54 | 5 | sorted traversal and `portMAX_DELAY` special case |

`uxListRemove` has:

- one entry and one return;
- one internal conditional branch;
- no loop, literal, call, callback, global, or port operation;
- no external interior entry and no stored entry/interior pointer;
- a fixed AAPCS signature and a complete upstream-source oracle;
- callers whose object-specific knowledge ends before the generic item
  pointer crosses the boundary.

The replacement therefore does not require the task, timer, scheduler, or
portable layer to become source-owned at the same time.

## Implementation contract

A later source replacement should:

1. use the authenticated V10.5.1 `uxListRemove` body and retain its MIT
   notice;
2. expose a project-prefixed entry such as
   `open_cfw_freertos_list_remove`;
3. define the exact 32-bit `List_t`/`ListItem_t` ABI or include the pinned
   upstream headers under the recovered configuration;
4. assert every size and offset listed above at compile time;
5. preserve the exact no-guard upstream precondition and `UBaseType_t`
   return;
6. redirect the complete 38-byte official entry at `0x004560E8`, then apply
   the overlay's established NOP-fill policy to the remainder;
7. rebind the two current source timer consumers to the new source symbol;
8. test removal from one-item and multi-item lists, head/middle/tail nodes,
   `pxIndex` equal and unequal cases, item-container clearing, and exact
   remaining-count returns against pristine V10.5.1;
9. pin the stock bytes/hash, all ten official call sites and encodings,
   caller-list digest, absent wide/narrow interior entries, and absent
   stored entry/interior pointers;
10. leave `vListInitialise` and `vListInsert` unchanged until each receives
    its own configuration-focused audit.

No official caller rewrite is required for correctness because an entry
redirect preserves the existing AAPCS ABI. Directly rebinding already
source-owned consumers is a cleanup of their retained-address seam, not a
condition for closure.

## Validation performed

- authenticated the local FreeRTOS-Kernel V10.5.1 snapshot with
  `third_party/freertos-kernel/verify_snapshot.py`;
- verified the official package and installed-application sizes and hashes;
- decoded the selected body in Thumb/M-class mode and mapped every
  instruction to pristine `list.c`;
- confirmed the preceding function, following alignment word, and next
  function prologue;
- decoded `BL` and `B.W` candidates at every installed-application
  halfword;
- decoded narrow unconditional/conditional `B`, `CBZ`, and `CBNZ`
  candidates at every installed-application halfword;
- scanned every installed-application byte offset for even and odd/Thumb
  entry or interior address words;
- inspected all ten call sites and independently pinned their nine
  containing function spans;
- inspected the two current source timer consumers that construct the
  retained odd Thumb entry.

All checks were read-only. No firmware was assembled, signed, flashed, or
executed on hardware.
