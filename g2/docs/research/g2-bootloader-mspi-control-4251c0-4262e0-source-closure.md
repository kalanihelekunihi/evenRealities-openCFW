# G2 bootloader MSPI control source closure

The complete `am_hal_mspi_control` dispatcher at `[0x004251c0,0x004262e0)` is now routed as one BSD-3-Clause source-owned production unit. Apple Clang 21 and Linux Clang 22.1.8 emit the exact 4,384 authenticated bytes with no relocations, and the resulting canonical bootloader provider remains byte-identical to the reviewed provider.

This identity is independently cross-checked against the separately mapped 4,384-byte Apollo-main `am_hal_mspi_control` body at `[0x004c0f78,0x004c2098)`. The two link placements share 4,297 exact bytes; the remaining 87 bytes occur in 53 bounded address-coupled branch or literal runs. Both complete bodies and the comparison are fail-closed. The vendored AmbiqSuite 5.1.0 translation unit, public request enum, BSD license, and openCFW stock-request ordinal adapter remain separately authenticated.

All four direct bootloader callers are pinned. A separate host-executable semantic model covers every valid stock request ordinal (`0..39`), low-byte request aliases, handle/configuration guards, register and state effects, command-queue and sequence transitions, and injected subordinate failures. The preceding 28-byte literal pool at `[0x004251a4,0x004251c0)` remains explicit retained non-code data rather than being misreported as source. Together with the adjacent transfer and interrupt tranche, this closes the bounded bootloader MSPI HAL code interval through `0x00426506`.

Hardware validation is blocked by unavailable physical evidence. Future authorized qualification must cover register writes, XIP transitions, timing, FIFO, interrupt, flash-bus, and cold-boot behavior. This wave performed no signing, flashing, erasing, reset, MMIO, or device operation.
