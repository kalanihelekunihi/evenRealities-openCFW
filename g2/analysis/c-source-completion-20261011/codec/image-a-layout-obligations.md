# Codec image-A loaded layout obligations

The authenticated stage-2 SRAM source image is 14,716 bytes at
`0x10023400..0x10026d7c`. Native XIP consumers use corresponding
`0x2002xxxx` SRAM aliases. The authenticated XIP source image is 36,484
bytes at `0x10203004..0x1020be88`. The startup BSS clear is
`0x20026d80..0x2002ecec` (32,620 bytes), with stack top `0x2002f7fc`.
These are stock intervals, not placements achieved by the current
relocatable candidate link.

The selected C/ASM graph owns the 64-word vector source; selected
native SRAM and XIP body candidates; and typed initializer sections
for OTP, flash catalog, module table, clock, board (240 bytes), UART
channels (256 bytes), AOUT data, KWS/sample/request tail (264 bytes),
and flash state/API (152 bytes). Current target object checks cover
their scalar bytes and pointer relocation slots, as documented in
`resident-source-round.md`. The console port is a source-owned NOBITS
word that needs placement at `0x2002731c` inside the startup clear.

A final linker composition must establish all of these simultaneously:

1. Place the full SRAM load sections and vector at native addresses,
   preserving each typed section's exact extent and required adjacency.
2. Resolve image-A function pointers to the corresponding selected C/ASM
   providers, including 23 flash API slots and nine sample callback
   slots. Compare relocated words against the native table values.
3. Place source-owned XIP literals, tables, strings, and code at a
   coherent XIP map. Address literal pools and jump-table case tails in
   the 267 catalogue-range gaps are not individually byte-equivalent
   merely because source algorithms compile.
4. Establish the source-to-runtime SRAM alias relationship and prove
   the stage loader/copy, BSS clear, and entry order on the final map.
5. Preserve the 107 SRAM range-gap fragment attributions (1,696
   bytes) after named initializer sections are subtracted: 82 are
   structural address literals or zero alignment, and all 25 mixed
   fragments have neighboring source-candidate identities. Their exact
   native instruction/data split and interior jump-table relocations
   still need final-map and bounded runtime qualification.

The 230-input candidate link is relocatable. It does not satisfy these
placement/copy/entry requirements or establish native runtime equality.

`image_a_known_data.ld` and `check_known_data_link.py` now provide an
isolated target-link placement check for the 256-byte vector, all 23
named initialized sections spanning the contiguous 2,200-byte tail,
and the four-byte console BSS cell. The linker pins their authenticated
addresses; the checker verifies each output address, type, and size,
every tail adjacency, and that the BSS cell lies inside the native
conditional clear span. The check accepts an already compiled candidate
object and does not change the unified builder or assert any unknown
XIP/code placement or runtime alias mechanism. Its first receipt used
the coherent `codec-data-reloc-final-round` object, which predates the
subsequent keyword-field metadata rename; the object bytes for that
initializer were separately rechecked after the rename.
