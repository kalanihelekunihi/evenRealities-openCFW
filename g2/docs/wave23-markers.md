# Wave 23 markers

Scope: em9305 asm -> C, 59 units. See the Wave 23 section of C-RECONSTRUCTION-PROGRESS.md.
Build g2c-w23-em9305 (621/621), final link g2c-w23-final-em9305 with 0 undefined, -Os unchanged.

No marker was added and none was removed. inventory-w23.json:
- em9305: unverified 1, flag 1 (the [0x80fd74,0x80ff54) ROM-use question, unchanged).
- apollo-main: guess 5 (the sim-fix RAM-cell flags), stub 1, weak 3, inferred 2.
- codec-a: guess 1, flag 1. touch: flag 1. bootloader and codec-b: none.

The 5 apollo-main GUESS flags (after wave 22):
| Site | State |
|---|---|
| stock_ram_cells.c header | The sizes of the g2_stock_ram_* objects are the gap to the next known cell. The stock allocation extent is not recovered. |
| stock_ram_cells.c 0x200007a1 field name | The value 0x00620063 is a verified constant and only the field name is open. |
| stock_ram_cells.c g2_stock_ram_20094400 | The size beyond 0x25807 is open. |
| display_ring_descriptor_data_20002c48.c | The dsc words stay raw until the glyph data is ported. |
| g2-apollo-main.ld ucHeap base | The size matches stock and the exact base is open. |
