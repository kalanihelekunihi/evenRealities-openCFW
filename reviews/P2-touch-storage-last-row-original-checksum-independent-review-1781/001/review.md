# Independent review 1781: scoped pass

The exact 7FA4..8054 body is 176 bytes / 84 instructions, with original 7FA0, 7F7C, 7F78, 7F6C and 7E68 reached in the original path. All 192 isolated fixtures match candidate call order, selected pointer, return and SP. The synthetic rows contain exact CRC bytes over row+1 for width−4 bytes, with one deliberately corrupted checksum. Width 131 rounds stride to 128; the CRC range reaches row+127, so it stays within that stride despite the nominal final three row bytes falling beyond it.

The synthetic RAM fixtures establish the bounded instruction behavior only. No physical storage, concurrency or canonical coverage claim follows.
