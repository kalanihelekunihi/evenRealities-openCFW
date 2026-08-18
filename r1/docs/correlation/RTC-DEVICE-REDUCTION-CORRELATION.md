# RTC-device reduction correlation (owner-authorized, 2026-08)

## Decision

Under the "Owner-authorized full reduction (2026-08-14)" section of
[`../SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md), the ten-function family
`unknown_rtc_device_provider_candidate` is reduced from the recovered
decompilation evidence to compilable C at
[`../../reconstructed/rtc_device/`](../../reconstructed/rtc_device/).  The
reconstruction is not vendor source and is never presented as such; every
file carries the provenance banner.  The ledger disposition for the ten
entries is now `clean_room_reimplementation_owner_authorized`.  The boundary
doc [`../boundaries/RTC-DEVICE-PROVIDER-BOUNDARY.md`](../boundaries/RTC-DEVICE-PROVIDER-BOUNDARY.md)
remains the provenance record of why no upstream source could be admitted.

Stock image: application, load base `0x00027000`, SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

## Evidence extraction path

- Ghidra bodies: `research/decompilation/application/decompiler-output.c`
  (seven of ten entries).
- The three Ghidra-missed bodies (`0x00056274`, `0x00056318`, `0x0005639C`)
  were re-disassembled from the byte-exact rebuilt image
  (`research/decompilation/rebuild/rebuilt-application.bin`) with Capstone
  (Thumb) and cross-checked with GNU `arm-none-eabi-objdump`; both tools
  agree on every instruction, including the loop conditions discussed below.
- Literal pools, the const nrfx config at `0x0009A638`
  (`00 00 06 41 00 00 00 00`, prescaler overridden to `0xFFF`), the `sys rtc`
  ops table at `0x00099C8C`, and the state roots `0x2000737C` / `0x20007384`
  were read from the rebuilt image.
- Callee attribution: `0x000276C8` = toolchain `gmtime` (ledger
  `arm_toolchain_runtime`), `0x000277FE` = `strcmp` thunk, `0x0002775C` =
  `memmove` thunk, `0x000277AA` = `memset(..., 0, n)` thunk,
  `0x0007AD6C/0x0007AD20/0x0007AE4C` = Nordic `nrfx_rtc_init` /
  `nrfx_rtc_enable` / `nrfx_rtc_tick_enable`, `0x0004E5BC` =
  `app_error_handler`, `0x00085CE0/0x00085D46/0x00085DA8/0x00050DF0` =
  generic-registry family (still blocked).

## Recovered layout

State root (`0x2000737C`): `+0x00` signed int16 UTC offset in minutes,
`+0x02` uint16 eight-tick divider, `+0x04` uint32 epoch counter, `+0x08`
record table (`0x20007384`, 256 records of 88 bytes).  Record: `+0x00` name
pointer, `+0x04` opened flag, `+0x08` 44-byte calendar (alarm compare
values), `+0x34` embedded `nrfx_rtc_t` (8 bytes), `+0x3C` callback,
`+0x40..+0x57` embedded generic-registry record.  Shared 0x40-byte time
block: calendar `+0x00`, epoch `+0x2C`, int16 UTC offset `+0x30`, uint64
millisecond value `+0x38`.  The reconstruction static-asserts these offsets
for the 32-bit target ABI.

## Per-function contract and reconstruction decisions

| Stock extent | Bytes | Reconstructed symbol | Contract |
| --- | ---: | --- | --- |
| `0x00050DAA..<0x00050DB5` | 12 | `rtc_device_ops_control` | ops-table slot 7: forward argument via the `0x50DE0` tail, return 1 |
| `0x00050DB6..<0x00050DBF` | 10 | `rtc_device_ops_set_time` | ops-table slot 4: forward (epoch, offset) through the registry set-time path, return 1 |
| `0x00050DE0..<0x00050DEB` | 12 | `rtc_device_ops_control` (tail) | `dispatcher_slot_0x20(*rtc_handle, 0, argument)` |
| `0x00056274..<0x000562E0` | 108 | `rtc_device_tick` | 8 Hz divider 0..7; on the 8th tick increment epoch, convert `epoch + offset_min*60`, dispatch record callbacks on second+minute match with `uint8` hour |
| `0x000562E0..<0x00056316` | 54 | `rtc_device_epoch_to_calendar` | toolchain `gmtime`, then month +1, year +1900, year-day +1 |
| `0x00056318..<0x0005638E` | 118 | `rtc_device_open` | name scan; first open inits embedded nrfx instance (prescaler 4095, priority 6), tick-enable, enable, mark opened; already open returns 0; no match returns 17 |
| `0x0005639C..<0x000563C0` | 36 | `rtc_device_snapshot` | NULL out returns 4; else epoch at `+0x2C`, 32-bit `epoch*1000 + divider` widened to uint64 at `+0x38`, return 0 |
| `0x000563F8..<0x00056440` | 72 | `rtc_device_calendar_write` | record-0 name compare, else 2; verbatim 44-byte copy, return 0 |
| `0x00056444..<0x00056498` | 84 | `rtc_device_callback_bind` | record-0 name compare, else 2; store/clear callback at `+0x3C`, return 0 |
| `0x0005649C..<0x00056502` | 102 | `rtc_device_epoch_initialize` | NULL block returns 4; offset applied unconditionally, then name match and opened required (else 17); epoch stored; validation conversion discarded; return 0 |

## Divergences from the stock binary (all deliberate)

1. **Full record scan.**  In the stock tick walk, open scan, and the
   (separately owned) registrar, the loop tail is `i = (i + 1) & 0xFF;
   beq body` — the loop continues only when the counter wraps to zero, so
   from a zero start only record slot 0 is ever examined (confirmed with two
   disassemblers; with the single registered `sys rtc` record at slot 0 this
   is behaviorally harmless in stock).  The reconstruction implements the
   evidently intended full 256-entry scan with a NULL-name guard, which is
   observably identical on every stock-reachable state and is exercised by a
   host test that registers a second record at slot 5.
2. **Explicit provider bindings.**  Stock calls the toolchain `gmtime`,
   Nordic `nrfx_rtc_*`, `app_error_handler`, and the generic registry
   directly.  The reconstruction binds each through `rtc_device_providers` /
   `rtc_device_bind_registry`; an unbound mandatory provider returns
   `RTC_DEVICE_STATUS_BAD_ARGUMENT` instead of faulting.
3. **Bad-argument handling.**  Stock dereferences name/calendar/block
   arguments unchecked; the reconstruction returns the recovered code 4
   (`RTC_DEVICE_STATUS_BAD_ARGUMENT`) for NULL arguments.
4. **Ops veneers fail closed while the registry is blocked.**  Stock returns
   1 unconditionally after dispatching into the generic registry.  The
   registry family (`unknown_generic_device_provider_candidate`) is not yet
   reduced, so with no bound registry seam the veneers return 17
   (`RTC_DEVICE_STATUS_LOOKUP_FAILED`); once bound they forward and return
   the recovered 1.
5. **Epoch-initialize validation conversion** is kept (side-effect free,
   result discarded) only when a breakdown provider is bound.
6. **Zeroed padding.**  The three recovered padding words of the calendar
   record are zeroed by the epoch->calendar adapter (stock leaves stack
   residue); the 44-byte named write still copies caller bytes verbatim.
7. **No libc in the freestanding unit.**  Name compare and the 44-byte copy
   use local loops, matching the r1 freestanding convention (no `string.h`).

Preserved exactly: the status scheme {0, 2, 4, 17}, the 8 Hz divider and
eighth-tick epoch advance, the signed-minute offset ×60 applied at
conversion time only (the stored epoch is offset-free), the 32-bit wrap of
`epoch*1000 + divider` in the snapshot, callback dispatch with the `uint8`
hour, prescaler 4095 / priority 6 / init-fault-continue ordering in open,
and the unconditional offset write in epoch-initialize.

## Host test mapping (`tests/test_openr1.c`)

- `test_rtc_device_epoch_to_calendar`: civil-time vectors (leap years 2000/
  2016, non-leap 2100, 30/31-day months, year rollover, `0xFFFFFFFF`
  wraparound to 2106-02-07 06:28:15) plus a sweep cross-checked against host
  `gmtime`, and bad-argument/provider-failure paths.
- `test_rtc_device_open_and_epoch_initialize`: lookup failure 17, first/second
  open, recovered nrfx configuration and call order, init-fault-continue,
  unbound-provider failure, full-table scan (slot 5), epoch-initialize
  ordering quirk and codes.
- `test_rtc_device_tick_and_callback_dispatch`: 8-tick epoch accumulation,
  alarm dispatch hour, +60/-300 minute offsets, epoch and local-time
  wraparound, callback clear.
- `test_rtc_device_named_records`: verbatim 44-byte calendar write, name
  mismatch 2, bad arguments, callback store/clear.
- `test_rtc_device_snapshot`: epoch/millisecond composition and the 32-bit
  wrap.
- `test_rtc_device_ops_veneers`: fail-closed unbound seams; bound forwarding
  of control (op 0) and set-time (epoch, offset) with recovered return 1.

## Integration state

The module is compiled by the r1 host/sanitizer/sim builds, the freestanding
Cortex-M4 object gate, and both target images.  The shared transparent
composition in `platform/nrf52840/openr1_rtc_service.c` registers a live
`sys rtc` record in the reconstructed generic registry, binds the slot-0x14
time request and slot-0x20 snapshot routes, opens the recovered record, and
copies the source-defined target instance descriptor into its recovered
field.  The Nordic/S140 target links Nordic SDK `nrfx_rtc.c` and owns RTC2;
the Zephyr target exposes RTC2 through its source counter driver.  Both use
prescaler 4095, IRQ priority 6, and deliver eight hardware ticks per second.
Phone time command `0x05` is adopted into both the product-owned `r1_clock`
and this recovered service.  A host composition test covers registration,
time set, veneers, snapshots, and tick advancement.  No raw BLE clock setter,
internal callback-registration command, rollback bypass, signing bypass, or
deployment action is exposed; physical drift remains a hardware gate.

The immutable boundary census
[`../../tools/evidence/summarize_r1_rtc_device_boundary.py`](../../tools/evidence/summarize_r1_rtc_device_boundary.py)
continues to pin the nine-body / 798-byte split (seven family bodies, the R1
registration wrapper, Nordic `nrfx_rtc_init`) against the rebuilt image; the
ledger-level family accounts ten entries including the three ops-table
veneers.
