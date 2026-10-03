# Independent review 2623: alternate-profile restore map

**Result: PASS_SCOPED.** `accepted` remains false.

The candidate receipt, source image, pseudocode, replay source, and instruction listing hashes match. The body `[0x42F4B2, 0x42F5F0)` is exactly 140 contiguous instructions. Every recorded byte sequence and all 19 literal word values match the authenticated image. An independent `arm-none-eabi-objdump` decode agrees with the six ordered bitfield insertions, table-index selection, saved-byte selection, cached-versus-fresh control-bit reads, conditional calls, and epilogue.

This review is static only. It makes no dynamic execution claim and does not infer the behavior of child `0x41C838`, saved-byte provenance, table contents, hardware effects, or complete runtime behavior. The packet remains private and unaccepted.
