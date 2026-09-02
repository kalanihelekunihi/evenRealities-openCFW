# G2 bootloader MSPI blocking-transfer and interrupt source closure

The four callable entries in `[0x004262e0,0x00426506)` are now production-routed from maintained BSD-3-Clause AmbiqSuite Apollo510 C:

- `am_hal_mspi_blocking_transfer` contributes 256 compiled bytes at `0x004262e0` and retains its three reviewed calls to the source-routed FIFO helpers and the authenticated delay-status service.
- interrupt enable and disable contribute 44 compiled bytes each at `0x00426450` and `0x00426484`.
- interrupt status contributes 60 compiled bytes at the halfword-aligned `0x004264ba` entry.

Apple Clang 21 and LLVM 22 produce identical bytes for all four leaves. The canonical providers are 163,840 bytes / `1b412d32…` and 163,824 bytes / `5d70e373…`. The production source is ordinary freestanding C; the retired raw executable transcript remains absent.

The source functions are shorter than the corresponding stock function envelopes. Their compiled return instructions and local literal boundaries are pinned, and the remaining stock bytes are kept as five explicit authenticated regions: the adjacent control tail (436 bytes), the blocking-transfer tail plus alignment (112 bytes), and interrupt tails of 8, 10, and 16 bytes. Neither canonical provider contains an external wide branch or stored Thumb entry into those regions. They are therefore retained unreachable evidence, not unimplemented callable services and not falsely claimed source bytes.

The host semantic model continues to cover handle validation, hexadecimal-mode address alignment, unsupported continuation, command-queue/high-priority/sequence exclusion, RX/TX FIFO dispatch, FIFO and completion error propagation, interrupt save/clear/restore, interrupt mask mutation, and raw versus enabled-only status reads.

The next entry at `0x00426506` (interrupt clear) and the following interrupt-service and power-control entries are already production-routed. Physical FIFO, interrupt, timing, flash-bus, and cold-boot behavior is **blocked by unavailable physical evidence**. No hardware operation was performed.
