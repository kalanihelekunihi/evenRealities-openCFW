# Case flash and package capacity audit

The official `firmware_box.bin` is 55,784 bytes: a 32-byte `EVEN` header and
55,752-byte payload. Header bytes 8–11 encode `0x0000d9c8` (55,752). This is
the **stock image length**, not an authenticated maximum firmware size.

Native Case 0x08002d48 sets an erase operation with start page 0 and count
128; 0x08002e04 writes received firmware doublewords to `0x08040000 +
offset`. The selected C candidate retains these constants in
`application_policy_box_erase_bank_candidate.c` and
`application_policy_box_write_chunk_candidate.c`. The native literal at
0x08002eb8 is `0x08040000`. These facts establish an alternate firmware
write address and 128-page erase request. The pinned STM32G0 HAL comparator
defines 2 KiB pages (`stm32g0xx_hal_flash.h:888`), which would make that
erase request 256 KiB. Its bank size, however, depends on the device's flash
size register and dual-bank option (`stm32g0xx_hal_flash.h:877-889`); the
comparator is not proof of this Case device's physical capacity or bank
configuration.

The size producer is the native record parser at 0x08001e94: command 0x58,
subcommand 0x20 accepts four big-endian payload bytes at offsets 12–15 and
stores them at `0x2000089c`, which is the OTA box's `+0x20` size field. The
file-open loop at 0x08001574 reads this field, requests at most 240 bytes per
transport packet, and passes each received chunk to the flash writer; its
selected complete control flow has no fixed maximum-size comparison. The
apply-file path reads the same field for checksum. This identifies a real
runtime size flow, but acceptance by the remote sender, flash HAL and package
loader still needs qualification. No source-side maximum has been added.

The source-owned, rooted, optimized diagnostic ELF currently has a 63,856-byte
load segment, 8,104 bytes larger than the stock payload. It ends before
`0x08010000`, and far before the native alternate-write address
`0x08040000`. Therefore stock payload length alone does not establish a size
blocker. Final admissibility still requires target flash identification,
updater/package size checks, runtime vector/entry and branch relocation
qualification, and full executable/data root coverage. The diagnostic ELF is
not a flashable release.

Concrete open checks:

1. Confirm native record parser and file-open source against bounded stock
   oracles at sizes above `0xd9c8`, and inspect any external package sender or
   loader cap. The visible Case code lacks a fixed length comparison.
2. Identify actual Case MCU and flash-size/dual-bank option values from an
   authenticated device or binary data. The vendor comparator alone is only a
   conditional calculation.
3. Finish computed/registered callback root census and initialized-data
   ownership before final linker garbage collection or package creation.

## Current executable-root boundary

The retained direct-branch audit lists 406 distinct Thumb `BL` targets below
the apparent initialized-table region. All 406 have at least one C source
address mention; this is a lead, not whole-body proof. Six targets are absent
from Ghidra's fixed-function catalogue; source paths exist for all six, and
the optimized ELF contains the checked timer/legacy/jump-table providers.
The aligned native odd-word scan finds 61 candidate pointer words to 39
distinct executable targets (34 words in vector slots). All 39 have source
symbols in the optimized linked ELF. These two censuses do not detect
runtime-constructed pointers, unaligned references, or externally registered
callbacks. No final dead-section removal is admitted from them alone.
