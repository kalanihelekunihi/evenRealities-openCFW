# Generic device-registry reduction correlation (owner-authorized, 2026-08)

## Decision

Under the "Owner-authorized full reduction (2026-08-14)" section of
[`../SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md), the forty-function family
`unknown_generic_device_registry_candidate` is reduced from the recovered
decompilation evidence to compilable C at
[`../../reconstructed/generic_device_registry/`](../../reconstructed/generic_device_registry/).
The reconstruction is not vendor source and is never presented as such;
every file carries the provenance banner.  The boundary doc
[`../boundaries/GENERIC-DEVICE-REGISTRY-BOUNDARY.md`](../boundaries/GENERIC-DEVICE-REGISTRY-BOUNDARY.md)
remains the provenance record of why no upstream source could be admitted.
The ledger disposition flip to
`clean_room_reimplementation_owner_authorized`, the verifier/evidence-tool
re-pinning, and the test-runner wiring are delegated to the integrator wave
(this reduction deliberately touches no shared ledger, verifier, tool, or
build file).

Stock image: application, load base `0x00027000`, SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

## Evidence extraction path

- Ghidra bodies: `research/decompilation/application/decompiler-output.c`
  (all forty entries; every ledger row has
  `inventory_source=ghidra_functions_csv`).
- Ghidra could not recover the seven dispatchers' tail calls
  (`UNRECOVERED_JUMPTABLE`), lost argument recovery in the subscriber-list
  cluster (`extraout_r2` markers), and folded shared tail-called helpers
  into the `0x0005D1EA`/`0x0005D21E` bodies.  All forty bodies were
  therefore re-verified against fresh Capstone (and, where GNU
  `arm-none-eabi-objdump` did not crash, cross-checked) Thumb disassembly
  of the byte-exact rebuilt image
  `research/decompilation/rebuild/rebuilt-application.bin`; both tools
  agree on every instruction inspected, including every literal-pool state
  root quoted below.
- Callee attribution via the ownership ledger: `0x000277AA/0x000277FE/
  0x0002775C/0x000277F0` = toolchain memset-zero/strcmp/memmove/strlen
  (`arm_toolchain_runtime`); `0x000855A0` = FreeRTOS `pvPortMalloc`
  (`freertos_10_5_1_nordic_nrf52_port`); `0x0009879C` =
  `xTaskGetCurrentTaskHandle`; `0x0007D488/0x0007D536` = CMSIS-FreeRTOS
  `osMutexAcquire`/`osMutexRelease`; `0x00078510` = Nordic busy-wait delay;
  `0x000799D6` = Nordic/SEGGER logger; `0x0008FE14/0x00091780/0x000914EC/
  0x00091638` = R1 product helpers (`r1_product_specific`).

## Recovered layout

Registry record (24 bytes): `+0x00` name pointer, `+0x04` operation-table
pointer, `+0x08..+0x13` private words, `+0x14` next pointer.  Global list
head at `0x20007680`.  Operation table: nine words; dispatchers exist for
the slots at byte offsets `0x00/0x08/0x0C/0x10/0x14/0x18/0x20`.  The
dispatchers are tail calls: the record stays in r0 and the caller's r1..r3
pass through to the operation untouched, so an operation receives
`(device, arg1, arg2, arg3)`; the request-block callers pass
`(device, 0, block, 0)`.

Request block (0x14 bytes, static per callsite; boundary-doc protocol
`{u8 cmd = 0xAE, u16 reg, buf, len, data, len2}`): `+0x00` command byte,
`+0x02` code/register, `+0x04` buffer, `+0x08` length, `+0x0C` data,
`+0x10` second length.  Time request block (0x40 bytes, stack-allocated and
zeroed by `0x00050DF0`): epoch at `+0x2C`, uint16 UTC offset at `+0x30` —
the same layout the rtc_device family documents.

Subscriber machinery: list descriptor `{link_offset, head, tail}` (stock
`0x20015408`, link_offset 28, configured by the non-family R1 initcall at
`0x0005DAB4`); nodes are absolute pointers whose prev/next link words live
at `node + link_offset + 0/+4`.  Subscriber node (0x24 bytes; 0x1C data +
8-byte link pair): `+0x00` root back-pointer, `+0x04` current-task handle,
`+0x08` name[8] (seven characters + NUL), `+0x10` flags (bit0 set by the
non-family poller at `0x0005DA4C`, bit1 disable), `+0x14` port tick word,
`+0x18` subscribe parameter.  Subscriber state: initialized flag at
`0x20016730`, current subscriber at `0x20016734`, CMSIS mutex handle at
`0x20016738`, port object (op at `+0x08`, called as
`f(operation, word_ptr)`) at `0x20015404`.

Client wiring roots (all fixed .bss slots, rebound as explicit wiring in
the reconstruction): control device `0x200076CC` with record-B at `+0x04`
and the slot-0x20 gate flag at `+0x08`; control block `0x200076DC`; time
device `0x20007380`; request block A `0x200076FC` with device
`0x200076F8`; shared 0xAE bus block `0x20006840` with device `0x2000683C`;
request block B `0x2000680C` with device `0x200067FC`; message blocks
`0x2001E560`/`0x2001E56C` with device `0x200077C0`; slot-0x0C device
`0x20006838`; flash-erase-all state `0x200067B4` (`+0x04` record, `+0x08`
ops); flash-erase-sector state `0x20006908` (`+0x00` ready byte, `+0x04`
record, `+0x08` ops); sync state `0x20006970` (`+0x04` ops, flush at
`+0x18`); module table `0x20007DE8..<0x20007E04` (records: name pointer at
`+0x04`, enabled bit0 at `+0x12`).  Flash records carry the region base at
word `+0x34`; the erase operation sits at ops `+0x30` and is called as
`erase(address, 0x1000)`.

## Per-function contract and reconstruction decisions

| Stock extent | Bytes | Reconstructed symbol | Contract |
| --- | ---: | --- | --- |
| `0x00085CE0..<0x00085D01` | 34 | `generic_device_registry_find` | strcmp walk from the global head; returns the matching record or NULL |
| `0x00085D58..<0x00085DA1` | 74 | `generic_device_registry_register` | rejects NULL record/name/ops and duplicate names; appends at the tail, clears next, returns 1 else 0 |
| `0x00085D08..<0x00085D19` | 18 | `generic_device_registry_dispatch_slot_00` | NULL record -> 1; NULL slot -> 5; else tail-invoke, pass-through return |
| `0x00085D1A..<0x00085D2B` | 18 | `generic_device_registry_dispatch_slot_08` | same shape; missing -> 5 |
| `0x00085CBA..<0x00085CCB` | 18 | `generic_device_registry_dispatch_slot_0c` | same shape; missing -> 6 |
| `0x00085D2C..<0x00085D45` | 26 | `generic_device_registry_dispatch_slot_10` | same shape; missing -> 2 |
| `0x00085DA8..<0x00085DC1` | 26 | `generic_device_registry_dispatch_slot_14` | same shape; missing -> 3 |
| `0x00085CCC..<0x00085CDD` | 18 | `generic_device_registry_dispatch_slot_18` | same shape; missing -> 7 |
| `0x00085D46..<0x00085D57` | 18 | `generic_device_registry_dispatch_slot_20` | same shape; missing -> 9 |
| `0x00077E30..<0x00077E3B` | 12 | `generic_device_registry_list_set_next` | guarded store of next at `node + link_offset + 4`; NULL node no-op |
| `0x00077E3C..<0x00077E45` | 10 | `generic_device_registry_list_set_prev` | guarded store of prev at `node + link_offset`; NULL node no-op |
| `0x0005D8E6..<0x0005D8ED` | 8 | `generic_device_registry_list_head` | guarded head getter (NULL -> NULL) |
| `0x0005D8EE..<0x0005D8F5` | 8 | `generic_device_registry_list_next` | next getter; unguarded in stock (see divergences) |
| `0x0005D8F6..<0x0005D8FD` | 8 | `generic_device_registry_list_tail` | guarded tail getter (NULL -> NULL) |
| `0x0005D8CC..<0x0005D8E5` | 26 | `generic_device_registry_hash` | BKDR-style `h = h*0x83 + byte`, 32-bit wrap |
| `0x0005D94A..<0x0005D985` | 60 | `generic_device_registry_list_append_alloc` | allocates `link_offset + 8` (36) bytes, appends at tail, fixes links; NULL on allocation failure; node not zeroed |
| `0x0005D998..<0x0005D9FF` | 104 | `generic_device_registry_list_remove` | head/tail/middle unlink; storage never freed (stock behavior) |
| `0x00097730..<0x00097741` | 18 | `generic_device_registry_lock` | `osMutexAcquire(mutex, 0xFFFFFFFF)` when a handle is bound, else no-op |
| `0x00097748..<0x00097755` | 14 | `generic_device_registry_unlock` | `osMutexRelease(mutex)` when bound, else no-op |
| `0x0005DB14..<0x0005DBB1` | 158 | `generic_device_registry_subscribe` | gated on initialized flag, non-NULL name, nonzero parameter; under the mutex: duplicate-name rejection, pool append, 0x1C zero, root/task/parameter stores, name capped at 7, flags cleared of bits 0/1; returns the node or NULL |
| `0x0005DBBC..<0x0005DBE9` | 46 | `generic_device_registry_subscriber_keepalive` | under the mutex: clear flag bit1, zero tick, refresh tick via port op `(1, &tick)`; NULL node no-op |
| `0x0005DBEA..<0x0005DC05` | 28 | `generic_device_registry_subscriber_disable` | under the mutex: set flag bit1; NULL node no-op |
| `0x0005DA00..<0x0005DA2B` | 44 | `generic_device_registry_subscriber_notify` | under the mutex: port op `(1, &tick)` then `(0, NULL)`; NULL node no-op |
| `0x0005DA30..<0x0005DA45` | 22 | `generic_device_registry_subscriber_current_task` | returns the current subscriber's task handle when flag bit0 is set, else NULL |
| `0x000509BC..<0x000509DB` | 32 | `generic_device_registry_ctrl_request` | fills the static control block `{cmd, code, buf (only when nonzero), len}`; slot 0x14 on the control device with `(device, 0, block)`; void |
| `0x0006F90E..<0x0006F91F` | 18 | `generic_device_registry_ctrl_adapter` | ops-table veneer: reorders to `ctrl_request(cmd, 0, buf, len)`, returns 1 |
| `0x00050ABC..<0x00050AD9` | 30 | `generic_device_registry_ctrl_cycle` | slot 0x08 on record B; slot 0x20 with arg1 = 1 when the gate flag is set |
| `0x00050DF0..<0x00050E17` | 40 | `generic_device_registry_time_request` | zeroed 0x40 block, epoch at +0x2C, offset at +0x30; slot 0x14 on the time device |
| `0x00050F34..<0x00050F57` | 36 | `generic_device_registry_request_a_control` | request block A `{cmd, code, data, len2}`; slot 0x10; returns 1 when the operation returned 0, else 0 (recovered inversion) |
| `0x00050F5C..<0x00050F81` | 38 | `generic_device_registry_request_a_transfer` | request block A `{cmd, code, buf (only when nonzero), len}`; slot 0x14; same inversion |
| `0x00044BE0..<0x00044BEC` | 12 | `generic_device_registry_bus_read_command_ae` | reorders the read wrapper's three payload arguments, selects command `0xAE`, and tail-calls the shared control dispatcher |
| `0x00050510..<0x0005052E` | 30 | `generic_device_registry_bus_control_dispatch` | fills shared bus block `{cmd, code, data, len2}` and invokes slot 0x10 on the bus device |
| `0x00050534..<0x00050554` | 32 | `generic_device_registry_bus_transfer_dispatch` | fills shared bus block `{cmd, code, buf (only when nonzero), len}` and invokes slot 0x14 on the bus device |
| `0x0005D1EA..<0x0005D1F3` | 52* | `generic_device_registry_bus_read` | zero length -> 0; else calls the explicit command-`0xAE` veneer and returns its status |
| `0x0005D1F4..<0x0005D21D` | 42 | `generic_device_registry_bus_update_bit` | seeds a local with arg4, reads register 0x0D into it, and on status 0 writes back with low bit replaced by `arg1 & 1` (stock `bfi`) |
| `0x0005D21E..<0x0005D241` | 68* | `generic_device_registry_bus_write` | zero length -> 0; else Nordic delay(5), then the explicit command-`0xAE` transfer dispatcher, status pass-through |
| `0x00077214..<0x0007721B` | 8 | `generic_device_registry_slot_0c_entry` | pure thunk: slot 0x0C on the bound device |
| `0x00087AF8..<0x00087B15` | 30 | `generic_device_registry_message_control` | packs message B `{arg2, arg1, arg3}`, slot 0x10, returns arg3 |
| `0x0009338C..<0x000933AF` | 36 | `generic_device_registry_request_b_control` | request block B `{code, data, len2}` — the command byte is NOT written; slot 0x10; inverted return |
| `0x00096FB0..<0x00096FD5` | 38 | `generic_device_registry_message_transfer` | packs message A `{arg2, arg1, arg3}`, replacing a zero arg3 with `strlen(arg2)`; slot 0x14 |
| `0x0005B2F8..<0x0005B327` | 48 | `generic_device_registry_flash_erase_all` | erases `sector_count()` sectors from the record base, 0x1000 each; recovered 8-bit loop counter |
| `0x0005E1FC..<0x0005E221` | 38 | `generic_device_registry_flash_erase_sector` | when ready and sector < 2: erase one 0x1000 sector, return 1; else 0 |
| `0x000734E8..<0x00073577` | 144 | `generic_device_registry_sync_modules` | enabled-gated module scan: `sync_one_class(record, index16)` per entry, gated R1/Nordic logging of nonzero statuses, then flush `(1, 0)`; returns 1 |

\* Ghidra assigned the callers at `0x0005D1EA` and `0x0005D21E` legacy
noncontiguous extents of 52 and 68 bytes. Independent Thumb disassembly of the
rebuilt image authenticated the three tail-called helpers at `0x00044BE0`,
`0x00050510`, and `0x00050534`; they are now separate exact manual ledger
supplements and separate C functions. The script seed at `0x00044BE4` is an
interior instruction of the contiguous `0x00044BE0..<0x00044BEC` veneer.

## Divergences from the stock binary (all deliberate)

1. **Explicit provider bindings.**  Stock calls `pvPortMalloc`,
   `xTaskGetCurrentTaskHandle`, `osMutexAcquire`/`osMutexRelease`, the
   subscriber port operation, the Nordic delay, and the R1
   flash-geometry/sync/log helpers directly.  The reconstruction binds each
   through `generic_device_registry_providers`; an unbound mandatory
   provider fails explicitly with the function's recovered failure value
   (NULL / 0 / 1) instead of faulting.  The bus write returns 0 without
   dispatching when the delay provider is unbound.
2. **NULL/argument validation.**  Stock dereferences record names, the
   ops-table pointer, and list nodes unchecked (register walks
   `device->name` before its own NULL check; dispatchers fault on a NULL
   ops table; the next getter and list remove fault on NULL nodes).  The
   reconstruction validates first and returns the recovered failure value:
   register 0, find NULL, dispatcher missing-operation status, getter NULL,
   void functions no-op.  Identical on every stock-reachable state.
3. **Per-context state.**  Stock uses fixed .bss addresses (listed above);
   the reconstruction keeps them as wiring fields/state inside
   `generic_device_registry`, bound through
   `generic_device_registry_bind_wiring`.  Observable behavior is identical
   for the single stock instance.
4. **Alignment-safe link access.**  The offset-based link words are read
   and written byte-wise so the freestanding unit is alignment-clean on
   wide host ABIs; on the 32-bit target the recovered offsets are
   word-aligned and the codegen is equivalent.
5. **Tail-call argument regularization.**  Stock leaf wrappers pass the
   request block in r2 with r1 = r3 = 0; `0x00050ABC`/`0x00077214` leave
   caller leftovers in r1..r3 (no contract).  The reconstruction passes
   explicit zero arguments and documents that no operation may rely on the
   leftover registers.
6. **No libc in the freestanding unit.**  strcmp/strlen/memmove/memset are
   local loops, matching the r1 freestanding convention (no `string.h`).

Preserved exactly, quirks included: the positive status scheme
{0,1,2,3,5,6,7,9}; the nine-slot table and per-slot missing codes; the
duplicate-name rejection returning 0 after a full walk; append-at-tail and
next-clearing in register; the 0x83 hash recurrence; `link_offset + 8`
allocation sizing; removal without free; the subscribe name cap of seven
characters applied to a uint8-truncated `strlen` (names of 256+ characters
wrap) and the duplicate check running against the *truncated* stored name
(re-subscribing an over-long name is not detected); the 0x1C-byte zero that
preserves the link pair; the request-block field sets per wrapper
(including the buffer-only-when-nonzero stale-word behavior and the
unwritten command byte in `0x0009338C`); the inverted `status == 0 -> 1`
returns; the zero-length early-out 0 in the bus read/write; the Nordic
delay(5) preceding the bus write; the register-0x0D read-modify-write bit
rule; the `{arg2, arg1, arg3}` message packing and zero-length strlen
substitution; the 8-bit sector-loop counter and sector < 2 gate; and the
sync scan's enabled gate, 16-bit index, triple log-level sampling (bit0 or
bit2 -> R1 logger with marker `0x0C800000`, bit1 -> Nordic logger with
packed id `0x001C0003`), and unconditional return 1.

## Host test mapping (`tests/test_reconstructed_generic_device_registry.c`)

- `test_registry_register_and_find`: bad-argument 0s, append order,
  next-clearing, duplicate rejection, find hit/miss/NULL.
- `test_registry_dispatchers`: all seven slots — NULL record 1, per-slot
  missing codes {5,5,6,2,3,7,9}, NULL-table guard, tail-call argument and
  return pass-through.
- `test_list_helpers`: guarded/unguarded getters, store guards, append link
  integrity and allocation size (`link_offset + 2` pointer words),
  allocation failure, head/middle/tail removal, empty-list collapse.
- `test_hash`: recovered recurrence vectors including a wrap case.
- `test_subscribe`: gate flags and bad arguments, recovered node contents,
  7-character cap, truncated-name duplicate quirk, tail linking, mutex
  wait-forever pairing, allocation-failure and unbound-provider failure.
- `test_subscriber_operations` / `test_mutex_guards`: keepalive flag/tick
  semantics and port-op sequencing, disable bit1, notify op pair,
  current-task gating, mutex no-op when unbound.
- `test_ctrl_request_and_adapter` / `test_ctrl_cycle` /
  `test_time_request`: block field sets, stale buffer word, adapter
  reorder + return 1, slot cycle gating, zeroed 0x40 time block.
- `test_request_block_a` / `test_request_block_b`: inverted returns,
  per-slot dispatch, the unwritten command byte.
- `test_bus_read_write` / `test_bus_update_bit`: 0xAE command, zero-length
  0, delay(5) ordering, stale buffer word, status pass-through, the
  read-modify-write bit rule, and the failed-read skip.
- `test_slot_0c_entry` / `test_message_wrappers`: thunk dispatch, message
  packing order, arg3 return, strlen substitution.
- `test_flash_erase_all` / `test_flash_erase_sector`: sector walk from the
  record base, 0x1000 length, count/ready/sector gates, unbound-provider
  no-ops.
- `test_sync_modules`: enabled gate, index order, log gating on level bits
  with recovered marker/packed-id, flush `(1, 0)`, unconditional return 1.

## Integration state

The module is host-tested (plain and ASan/UBSan harnesses) and compiles
clean under the r1 freestanding Cortex-M4 object flags.  It is not yet
referenced by the linked target: OpenR1 product code binds devices through
direct typed bindings, and the stock consumers of the registry arrive
through the interlocked B210 platform families (software-TWI, sensor
stream, time/calendar).  The integrator wave owns the ledger disposition
flip, the verifier/evidence re-pinning (family count pin at
`tools/verify_openr1.py` line ~3282, frontier confidence map at ~7122, the
`investigate_before_implementing` rows in
`tools/evidence/summarize_r1_frontier_{32_63,64_127,128_202,final53}.py`,
and a per-entry census on the RTC model), the `Makefile` source lists, and
the `tests/test_openr1.c` call site for
`test_reconstructed_generic_device_registry()`.  The reconstructed rtc_device
family's fail-closed ops veneers (`rtc_device_bind_registry` seams) can be
retired against this module's dispatchers once the integrator wires them.
No dispatch command, authorization, rollback, signing, or deployment
behavior is exposed beyond the recovered semantics.
