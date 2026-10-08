# HAL control request tail

Image: `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`, base
`0x410000`, SHA-256
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.
The isolated source/test harness is built with `make` in this directory.

`control_remaining.c` adds bounded handlers for requests 25, 28, 32, and 35–40.
Requests 26–27, 29–31, and 33–34 go through the typed
`opencfw_hal_mspi_control_unrecovered_request` provider cut; the source does
not report success for them. Request 40 returns the stock invalid-argument
code 6. Exact source and stock ranges/hashes are in `result.json`.

Request 25 at `0x4258c0` requires a nonnull config and reads its first byte as
the device mode. On module 1 or 2, modes 10 and 11 are rejected with code 5
when handle byte 9 has any low two bits set. Otherwise the byte is written to
handle offset 10 and private helper `0x424120` is called. The fixture records
the wrapper plus actual private helper.

Request 28 writes `0x80` to module base + `0x2b4` and executes DMB only when
handle byte `0x8c8` is zero; both branches are tested. Request 32 writes
`0x00200000` to that register, stores 1 at handle+`0x838`, and clears
handle+`0x844`.

Requests 35–40 pass all 316 original/source cases. Requests 35 and 36 validate
config and update fields in `MSPIx_DEV0CFG` and `MSPIx_DEV0XIP`; 37 and 38
clear/set bit 6 in `DEV0XIP`; 39 either clears bit 0 in
`MSPIx_DEV0SCRAMBLING` or enables it and applies the supplied packed fields;
40 returns 6. Requests 28/32 pass another 12 cases, bringing the verified
bounded requests 28, 32, and 35–40 subset to 328 cases. The comparisons execute
the pinned `0x4251c0` dispatcher against synthetic MMIO at
`0x40060000–0x40063fff`.

The request25 wrapper follows stock's unconditional invalid-mode return for
modules 1 and 2 with mode 10 or 11. It does not gate that branch on the handle's
latency byte. With the separately owned device-configure source rebuilt, all
972 original/source cases pass.

The original/source run uses the locked firmware bytes and mapped synthetic
RAM/MMIO only. There are no hardware writes or physical timing claims. The
remaining unclosed interval is requests 26–27, 29–31, and 33–34. Direct stock
inspection shows request 31 enters queue helper `0x4279f0` and updates handle
state at `+0x82c`; request 33 writes CQ control then calls `0x4240aa` and
branches on its result while updating `+0x844`; request 34 validates a
descriptor and calls `0x42790a` before constructing CQ command tuples. Those
paths depend on queue execution and descriptor semantics, so they remain
explicit unresolved providers rather than modeled-success stubs.
