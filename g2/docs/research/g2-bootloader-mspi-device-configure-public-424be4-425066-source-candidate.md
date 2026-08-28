# G2 bootloader public MSPI device-configure source candidate

Public `am_hal_mspi_device_configure` at `[0x00424be4, 0x00425066)` is now compilable BSD-3-Clause C routed at its authenticated production address. Apple Clang 21 and Homebrew LLVM Clang 22 emit the exact 1,154 stock bytes (SHA-256 `baf84c7a01d10528a6367c12651b215274674bbfe206d9d26edddda387d85658`) without relocations.

The host semantic model covers initialized/configured handle checks, MSPI1/2 high-frequency and hexadecimal-mode exclusions, all 23 accepted frequency values, HFRC/HFRC2 lifecycle and error propagation, clock-selector and divisor classes, SDR250 selection, DMA threshold class, device configuration dispatch, state updates, timeout `10000`, and the four XIP-off delay classes. The exact target body retains all stock register-field writes and calls the already source-owned clock, pad-mode, and XIP-delay providers at their authenticated addresses.

The 16 bytes before the body remain authenticated literal data. The next body is `am_hal_mspi_enable` at `[0x00425066, 0x004250f0)`.

Hardware validation is blocked by unavailable physical evidence. Future authorized qualification must cover clock switching, flash modes, pad routing, timing, XIP, DMA thresholds, and cold-boot behavior; this software-only wave makes no physical-validation claim. No flash, reset, signing, or MMIO operation was performed.
