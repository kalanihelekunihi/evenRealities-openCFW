# G2 bootloader MSPI initialize source candidate

This candidate record is superseded by
`g2-bootloader-mspi-initialize-424a5a-424aea-source-closure.md`. Production now
routes an 88-byte structured-C return path at the authenticated entry. Apple
Clang 21 and Homebrew LLVM Clang 22 emit identical bytes (SHA-256
`9476ac1668a350be0af32604c47a50476782fa21eaa7001648928feed497ef9c`)
with no relocations; the unreachable 56-byte stock tail remains retained.

The host implementation exercises the recovered Ambiq state ABI: four `0x8d0`-byte states; initialization bit 24 and magic `0x00bebebe` at offset `0`; module at `+4`; invalid clock frequency at `+0x0c`; null TCB at `+0x18`; clock-source sentinel `7` at `+0x8c9`; and XIP-off minimum delay `8` at `+0x8cc`. It rejects module values above three with status `5`, a null output handle with status `6`, and an already allocated state with status `7`. The sole direct stock caller is `0x0042029a`; the PC-relative state-base literal resolves to `0x2001caa0` at `0x004251ac`.

The next code body is `am_hal_mspi_configure` at `[0x00424af0, 0x00424bd4)`. The intervening two alignment bytes and four-byte state-base literal remain authenticated official data.

This software-only source wave performed no flash, reset, signing, or MMIO operation. Physical state allocation, SRAM, cold-boot, and downstream MSPI qualification is blocked by unavailable physical evidence; this source closure does not by itself claim firmware functional completeness.
