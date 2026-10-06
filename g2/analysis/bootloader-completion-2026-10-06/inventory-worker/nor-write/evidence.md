# NOR page-program and sector-erase source evidence

## Identity and instruction provenance

The input artifact is the locked `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`,
SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`,
loaded at `0x00410000`. The worker executed the original Thumb instructions
directly from that image and compared their provider events and return values
with the ARM-compiled readable candidates in `g2/components/bootloader/nor_write/`.

| Entry | Range, end exclusive | Length | SHA-256 |
|---|---:|---:|---|
| Sector erase `0x420A08` | `0x420A08–0x420ADA` | 210 bytes | `0a0a96db9e3a1c6fcbdfcebd96db6f16e22c780940889677a16ebc880d0dd899` |
| Page program `0x420B0C` | `0x420B0C–0x420C14` | 264 bytes | `dcaf2a13af5fb811c228b4845363682411abf1acab703507368f6d1e4463b15e` |
| WREN `0x420984` | `0x420984–0x4209BE` | 58 bytes | `e675df17f3a419b27b088cd7cd0c5785537fe730f597f894ba648e3a76afa3e5` |
| WRDI `0x4209C4` | `0x4209C4–0x4209FC` | 56 bytes | `f29c57daa25ee3108fe92b65e0076a21ac49af5ded9c735c33624e26e4400cd2` |

Hashes are over the ranges above, including the stock epilogues and excluding
the next function/padding bytes.

## Recovered behavior

`0x420A08` requires a nonzero active MSPI handle (`0x200270DC`), a 4 KiB
aligned starting address, and an address below `0x02000000`. It returns 2 for
no handle, 6 for alignment failure, and 5 for an out-of-range address. The
transaction order is mutex/before helper `0x41FF08`, write-mode setup
`0x420F10`, raw delay `0x4207F4`, WREN `0x420984`, one opcode `0x20` command
through `0x42069E`, another raw delay, WRDI `0x4209C4`, restore mode `0x420E8C`,
and after/unlock helper `0x41FF1E`. Pre-erase delay failure maps to 3; the
post-command delay failure maps to 4; WREN, command-transfer, and WRDI status
values propagate. Each error site uses its own original variadic message at
`0x415FAE`.

`0x420B0C(address, buffer, length)` requires a nonzero handle, nonnull buffer,
and nonzero length; invalid input returns 6. It checks only that the starting
address is below `0x02000000` (failure 5), then divides writes at 256-byte page
boundaries. For each chunk it calls raw delay `0x4207F4`, WREN, one opcode
`0x02` transfer with the chunk address/buffer/length, wait helper `0x4207A2`
with argument 10, and WRDI. Delay or ready-wait failures map to 4; WREN,
transfer, and WRDI statuses propagate. The wrapper has no end-address or
overflow guard; the lower command provider may reject a later chunk that
crosses the device limit. Cleanup always restores at `0x420E8C`, then calls
`0x41FF1E`.

`0x420984` sends opcode `0x06` through `0x42069E`, logs at severity 1 on
failure, and returns the transfer status. `0x4209C4` sends opcode `0x04`,
logs at severity 2 on failure, and returns the transfer status. The status
polling/readiness implementation is `0x4207A2`; `0x4209C4` is WRDI, not a
ready helper.

The raw arguments 1, 10, 500, 1000, and 5 passed into timing helpers are
preserved without assigning physical units. The code uses parent helper names
`opencfw_bl_nor_read_before`, `opencfw_provider_420f10`,
`opencfw_bl_nor_read_delay`, `opencfw_bl_nor_wait`,
`opencfw_bl_nor_read_configure`, and `opencfw_bl_nor_read_after`.

## Differential results and limits

`nor-write-comparison.json` records 27 passing cases over 590 distinct
original instruction bytes. Cases cover successful 4 KiB erase, 3-page
program splitting (15/256/17 bytes), handle/argument/alignment/range errors,
delay and wait failures, WREN/WRDI/transfer failures, and a request that
crosses the device limit after a valid starting address. The fixture hash and
source/linker/test hashes are embedded in the JSON.

Only the local program/erase/WREN/WRDI instructions execute on both sides.
Setup, restore, mutex/timing services, the `0x42069E` PIO command boundary,
diagnostic sinks, and lower MSPI/HAL behavior are synthetic provider cuts.
The command family `0x42069E` has its own source and comparison elsewhere.
No flash bytes are read or modified; no filesystem or hardware result is
claimed. This is not a standalone bootable payload, and the source still
depends on linked NOR, timer, mutex, HAL, and logging providers.
