# G2 bootloader MSPI configure source candidate

`am_hal_mspi_configure` at `[0x00424af0, 0x00424bd4)` is now compilable BSD-3-Clause C and is routed at its authenticated production address. Apple Clang 21 and Homebrew LLVM Clang 22 emit the exact 228 stock bytes (SHA-256 `7e844f8b690703208e8e932371914cc19506c0d8adf682bfe03a28e55357ad8c`) without relocations.

The semantic host implementation validates the recovered initialized-handle magic and disabled-state precondition, clears XIP enable and the AXI/scrambling defaults, records the TCB address and size, classifies the TCB end against Apollo510 `SSRAM_BASEADDR` `0x20080000`, reproduces the unsigned command-queue capacity formula `((size - 8) * 4) / 72` with the 256-entry cap, and sets clock-on-D4, configured, and invalid-device state fields. Tests cover invalid handle, enabled handle, null TCB, TCM/non-TCM boundaries, unsigned small-size behavior, and capacity capping.

The six bytes at `[0x00424aea, 0x00424af0)` and the 16 literal bytes at `[0x00424bd4, 0x00424be4)` remain authenticated data. The next code body is public `am_hal_mspi_device_configure` at `[0x00424be4, 0x00425066)`; the following independently bounded bodies are `am_hal_mspi_enable` and `am_hal_mspi_disable`.

Hardware validation is blocked by unavailable physical evidence. Future authorized qualification must cover MMIO, TCB residency, command-queue operation, clock-on-D4, and cold-boot behavior; this software-only wave makes no physical-validation claim. No flash, reset, signing, or MMIO operation was performed.
