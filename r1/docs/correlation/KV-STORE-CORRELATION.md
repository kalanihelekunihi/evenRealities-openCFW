# `kv.bin` clean-room correlation

## Provider decision

`kv.bin` is R1 product code, not FlashDB KVDB. The recovered initializer at `0x00094E3C`
binds an 8,192-byte partition as four fixed 2,048-byte snapshots. Core initialization at
`0x000731A0` registers seven fixed classes. FlashDB 2.0.0 remains admitted only for the separate
`health.db` TSDB.

The clean-room implementation is [`r1_kv_store.c`](../../src/r1_kv_store.c). It uses only
the R1 flash HAL and the already recovered MODBUS CRC helper; it contains no reconstructed vendor
library body and exposes no raw host flash command.

## Recovered layout

Each snapshot contains eight 256-byte blocks. Blocks 0 through 6 have a 24-byte header followed by
one fixed payload; recovered block 7 was unused.

| Block | Fixed name | Payload bytes | Initial state / low flags |
| ---: | --- | ---: | ---: |
| 0 | `dev_info` | 52 | `1 / 0` |
| 1 | `ble_mult` | 90 | `1 / 0` |
| 2 | `health` | 12 | `1 / 0` |
| 3 | `hsync` | 24 | `1 / 0` |
| 4 | `power` | 4 | `1 / 2` |
| 5 | `nv_r1` | 124 | `1 / 2` |
| 6 | `r_size` | 1 | `1 / 2` |

The header stores the base-131 hash of the complete NUL-padded eight-byte name, the name itself,
`0x45503130` (`01PE`) magic, retained state, low flags plus block index, payload length, and
CRC-16/MODBUS. The implementation reproduces these fields, class lengths, and recovered compiled
defaults. The correlated stock functions are:

| Address | Role |
| --- | --- |
| `0x00057D0C` | startup sector scrub |
| `0x00064B24` | latest-slot scan |
| `0x000731A0` | class registration |
| `0x00073220` | class restore |
| `0x000734E8` | synchronized snapshot store |
| `0x00091780` | one-class writer |
| `0x00095168` | latest-snapshot reader |
| `0x00095304` | snapshot writer/rollover |
| `0x0005D87C` | CRC-16/MODBUS |
| `0x0005D8CC` | base-131 name hash |

The separately bounded identity/calibration recovery protocol reads and plans fill-only changes
for the `nv_r1`, `power`, and `r_size` classes. Its pure implementation never commits the store and
the live BLE command remains refused; see
[`NV-RECOVERY-CORRELATION.md`](NV-RECOVERY-CORRELATION.md).

## Intentional security hardening

The stock scanner accepts a slot from block 0 magic alone, restores later classes independently,
and erases both sectors at rollover. A power interruption can therefore select a partial snapshot
or erase the only complete copy. openR1 preserves the public class layout but deliberately tightens
the transaction rules:

- all seven class records must pass hash, name, magic, index, exact length, and CRC checks;
- the otherwise-unused block 7 contains an `r1_meta` generation/complement commit record;
- blocks 1 through 6 and the commit record are programmed before block 0, making block 0 the final
  visibility marker;
- new snapshots alternate sectors, and only the sector not containing the current snapshot may be
  erased;
- legacy stock snapshots are imported only when all seven records validate strictly and block 7 is
  erased; the next write migrates them to the hardened form.

These differences are explicit audit corrections, so the resulting partition is functionally
compatible at the class level but not byte-identical to stock after openR1 writes it.

## Verification

Host tests verify the seven names and lengths, recovered defaults, exact `01PE` placement, reopen,
four-slot rollover, capacity/error behavior, legacy-shaped reads, and deterministic interruption at
every erase/program boundary of a rollover. After each simulated reboot the visible health class is
either the complete previous value or the complete replacement. The same source passes
ASan/UBSan and freestanding Cortex-M4 compilation. The physical internal-flash transport is now
linked through Nordic fstorage/FAL; migration, power-loss, and
owned-device timing capture remain required.
