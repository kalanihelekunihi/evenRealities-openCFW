# G2 bootloader MSPI initialize source candidate

`am_hal_mspi_initialize` at `[0x00424a5a, 0x00424aea)` is now represented by compilable BSD-3-Clause C and routed into the production bootloader overlay at its authenticated address. Apple Clang 21 and Homebrew LLVM Clang 22 both emit the exact 144 stock bytes (SHA-256 `7708fb5a3bfd2f3f137722f96dc65a9a566da5c70470a014a565df98e2ed87dc`) with no relocations.

The host implementation exercises the recovered Ambiq state ABI: four `0x8d0`-byte states; initialization bit 24 and magic `0x00bebebe` at offset `0`; module at `+4`; invalid clock frequency at `+0x0c`; null TCB at `+0x18`; clock-source sentinel `7` at `+0x8c9`; and XIP-off minimum delay `8` at `+0x8cc`. It rejects module values above three with status `5`, a null output handle with status `6`, and an already allocated state with status `7`. The sole direct stock caller is `0x0042029a`; the PC-relative state-base literal resolves to `0x2001caa0` at `0x004251ac`.

The next code body is `am_hal_mspi_configure` at `[0x00424af0, 0x00424bd4)`. The intervening two alignment bytes and four-byte state-base literal remain authenticated official data.

This software-only source wave performed no flash, reset, signing, or MMIO operation. Physical state allocation, SRAM, cold-boot, and downstream MSPI qualification is blocked by unavailable physical evidence; this source closure does not by itself claim firmware functional completeness.
