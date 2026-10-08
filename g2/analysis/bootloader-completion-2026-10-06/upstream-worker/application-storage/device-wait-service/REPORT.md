# Stock INFO-space word dispatch `0x4213e6`

`g2/components/bootloader/application_storage/device_wait_service.c` now exports
the descriptive symbol `opencfw_boot_info_read_dispatch(info_space,
word_offset, word_count, destination)`. The old
`opencfw_boot_device_wait_service` symbol forwards to it for the frozen
mode-wait caller. Despite that historical caller name, stock `0x4213e6` routes
reads from INFO0/INFO1 spaces; it does not schedule or wait for an event.

The selector values correspond in order to the Apollo510 SDK 5.1 enum
`CURRENT_INFO0`, `CURRENT_INFO1`, `OTP_INFO0`, `OTP_INFO1`, `MRAM_INFO0`, and
`MRAM_INFO1`. The table records stock bounds and base routes; the word offset
and word count are checked with the stock 32-bit addition before dispatch.

| Selector | Stock maximum `word_offset + word_count` | Stock route |
| --- | ---: | --- |
| 0 | `0x40` if INFO0 selects OTP, otherwise `0x200` | OTP_INFO0 with bit-27 gate, otherwise INFO0 |
| 1 | `0x2c0` if INFO1 selects OTP, otherwise `0x600` | OTP_INFO1 with bit-27 gate, otherwise INFO1 and add `0x280` to offsets at least `0x200` |
| 2 | `0x40` | OTP_INFO0 with bit-27 gate |
| 3 | `0x2c0` | OTP_INFO1 with bit-27 gate |
| 4 | `0x200` | MRAM_INFO0 |
| 5 | `0x600` | MRAM_INFO1 |

Every route forms its address as the selected base plus four times its final
word offset. Null destination and unsupported selector return 6; a range that
exceeds the selected stock bound returns 5; a selected OTP route with the
stock bit-27 gate clear returns 9. Valid requests call the resident reader
with `(address, destination, word_count)`, ignore that routine's result, and
return 0. The stock bit-27 gate is preserved as a raw status predicate; the
available evidence does not establish that it is identical to a particular
SDK readiness API result. No additional end-address constraint is added beyond
stock's range expression.

## Upstream basis

The local SDK snapshot is pinned Apollo510 HAL commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`, release marker
`release_sdk5p1p0-366b80e084`; its per-file provenance and BSD-3-Clause notices
are recorded in
[`FILE-PROVENANCE.tsv`](../../ambiqhal-apollo510/FILE-PROVENANCE.tsv). The
source files below are inside the same local acquired snapshot:

| Evidence | Local path relative to `upstream-worker/ambiqhal-apollo510/` | SHA-256 | Relevant lines |
| --- | --- | --- | --- |
| INFO selector enum | `ambiqhal/mcu/apollo510/hal/am_hal_info.h` | `43bf671719ceab7d56b0e7b11c35894c75088771d156b84838fd71d136121858` | 65–73 |
| HAL offset/count and OTP power contract | `ambiqhal/mcu/apollo510/hal/am_hal_info.h` | same | 120–148 (INFO0), 169–194 (INFO1) |
| INFO / OTP base addresses | `ambiqhal/mcu/apollo510/regs/am_reg_base_addresses.h` | `e6d15af8c495288f88a8ad0eea1ccae07cb14cac356f4fb3c138e4c3fedae16d` | 84–90 |
| INFO0/INFO1 size and INFO1 visible offset | `ambiqhal/mcu/apollo510/hal/mcu/am_hal_mram.h` | `6997e72e3d551e90867c64e4b8bc3a71b6f15a78e0076e925143c256399a2ab4` | 105–107 |

The HAL explicitly defines offsets as byte-offset divided by four, count as
number of words, and says the caller powers OTP when needed. Its enum order and
base-address macros corroborate the selector names and addresses recovered
from stock. The MRAM header's `INFO1_VISIBLE_OFFSET` is `0x1200` bytes, or
`0x480` words; stock's `+0x280` rebase after input offset `0x200` maps to that
visible offset. The selector's stock arithmetic and bounds remain authoritative
where they do not impose an independent HAL range check.

The device-info record's former `clock_factors` label was also misleading:
the SDK device struct stores ITCM, DTCM, SSRAM, and MRAM sizes. The correction
and supporting structure evidence are documented in the integrated
[`DEVICE-INFO-LAYOUT.md`](../../../integrated-status/DEVICE-INFO-LAYOUT.md).

## ROM thunk and differential

`info_read_rom_thunk.S` is an instruction-form reconstruction of stock
`0x41d28a..0x41d292`: `push {r7,lr}; bl 0x48; pop {r0,pc}`. It calls the named
external `opencfw_boot_rom48` entry. The unusual pop is intentional: it
discards the ROM return value and returns the saved R7 value. The resident
routine at `0x48` is not available as source.

The standalone Unicorn comparison compiles the C provider and assembly thunk
as a Cortex-M Thumb ELF. It runs the stock dispatch and stock thunk versus
those source functions for 8,064 selector/range/state fixtures, four
null-destination fixtures, and two direct-thunk saved-R7 sentinels. It compares return values, destination word,
volatile state reads, and ROM arguments, and covers 368 distinct original
instruction bytes including the ROM thunk. The ROM entry's returned status
and first destination word are controlled by the fixture; complete resident
ROM read, copy, error, and physical OTP behavior remain outside this test.

Run with:

```sh
make verify PYTHON=/Users/kalani/.local/share/opencfw/venv/bin/python
```
