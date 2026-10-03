# Independent review 2257

**Result:** PASS_SCOPED.

Source, code `[0x50E4,0x5182)`, literal `[0x5184,0x5188)`, referenced table `[0xB4C4,0xB4FC)`, and all artifact hashes match the receipt. The isolated replay regenerated all 512 fixtures. Original `AA2C` executes without interception and receives the pinned table pointer and count 56. Assertions cover the complete ordered write ledger, full 128-byte configuration and 256-byte destination buffers, zero return, and R4–R7/SP preservation.

Decoded flow matches the slot model: reset bytes 99–112 to `0xFF`, clear byte 104, select byte 99 or 100 for selector 1 or 2 (otherwise no selection), establish next-slot state in byte 107 and byte 98, then scan the cached 14 bytes in order and copy corresponding table words to `destination + slot*4`. The 256 selector values and both initial patterns are represented. The literal points to the exact 56-byte table whose words are exported in `table.json`.

**Limits:** Configuration and destination are separate buffers; pointer aliasing, changing context pointers, and physical meaning are not established. No canonical admission is made.
