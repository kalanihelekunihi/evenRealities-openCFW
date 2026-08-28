# G2 bootloader MSPI blocking-transfer and interrupt source candidates

The blocking transfer at `[0x004262e0,0x0042644c)` and interrupt enable, disable, and status services at `[0x00426450,0x00426506)` are now compilable BSD-3-Clause C routed at their authenticated production addresses. Both reviewed Clang profiles emit all four stock bodies exactly; the four bytes at `[0x0042644c,0x00426450)` remain authenticated data.

The host model covers handle validation, hexadecimal-mode address alignment, unsupported continuation, command-queue/high-priority/sequence exclusion, RX/TX FIFO dispatch, FIFO and completion error propagation, interrupt save/clear/restore, interrupt mask mutation, and raw versus enabled-only status reads.

The adjacent `am_hal_mspi_control` body at `[0x004251c0,0x004262e0)` is now production source; the bounded MSPI HAL code interval through `0x00426506` is closed. Hardware validation is blocked by unavailable physical evidence, so FIFO, interrupt, timing, and flash-bus behavior have not been physically validated. No hardware operation was performed.
