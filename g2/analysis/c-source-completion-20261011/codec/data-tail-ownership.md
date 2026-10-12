# Image-A XIP data-tail label attribution

The retained Ghidra catalogue labels 23 addresses after executable XIP
code as functions. Direct bytes and consumers show data or string-boundary
labels instead. This is semantic source ownership only; final XIP
placement, scatter copying, and relocation equivalence remain open.

| Stock address | Source owner / finding | Qualification |
| --- | --- | --- |
| `0x1020a8aa` | `board_uart.c` nine signed gain values | Semantic C array; stock catalogue extent is only four bytes. |
| `0x1020a8ee` | `resident_xip_audio_config_leaves.c` five PGA corrections | Five semantic bytes; sixth zero is adjacent padding/layout. |
| `0x1020a910` | `resident_xip_aout_db_table.c` 37 typed code/dB pairs | 148 semantic bytes. |
| `0x1020a9a4` | `resident_xip_aout_select_channel.c` 12 selector bytes | Exact semantic array. |
| `0x1020acc4` | `resident_xip_padmux_gpio.c` 64 pin/function bytes | Exact semantic array. |
| `0x1020ad30` | `resident_xip_system_dma_board.c` 26 board pin bytes | Exact semantic array. |
| `0x1020aea2` | `resident_xip_system_initialize.c` 12 LDO trim values | Exact semantic 24-byte array. |
| `0x1020afd2`, `0x1020afd6` | System initializer `ESMT`/`ZBIT` vendor strings | `0x1020afd6` begins at an intervening NUL; string placement is open. |
| `0x1020b1c4`, `0x1020b204` | `resident_xip_mode_initialize.c` typed idle/TWS descriptors | Pointer relocations and final placement need qualification. |
| `0x1020b446`, `0x1020b77c` | NUL boundaries before app log strings | No independent object body; log literals are source-owned. |
| `0x1020b908` | Selected NationalChip `base/src/crc32.c` lookup | All 1024 stock bytes match standard reflected CRC-32 polynomial generation; stock SHA-256 `12f3e0576d447eb37b36d82ba0c1c5481b8f0d12fdc70347ce4a076b229d4c86`. |
| `0x1020bd08` | `resident_xip_fpadd_parts.c` canonical opposite-infinity NaN parts | Five zero words; selected C data. Final placement remains open. |
| `0x1020bd1c` | `resident_xip_udiv_bitlength_data.c` 256-byte `i.bit_length()` table | Exact stock bytes; receipt `udiv-bitlength-data-receipt.json`. Native lookup use/placement still open. |
| `0x1020be1c` | `resident_flash_transfer.c` 14-case native flash-info dispatch | C switch has action semantics; original interior-label relocation table layout is still open. |
| `0x1020be54` through `0x1020be7e` | `resident_flash_product_catalog.c` six named flash products | C strings are source-owned; some catalogue labels include preceding NUL bytes, so byte-for-byte layout remains open. |

The only newly identified semantic initializer gap in this pass was
the 256-byte division bit-length table. The remaining gaps in these
labels concern exact string adjacency, the flash dispatch table's
internal branch relocations, and final source section placement.
