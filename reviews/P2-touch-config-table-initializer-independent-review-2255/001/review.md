# Independent review 2255

**Result:** PASS_SCOPED.

Source, code `[0x52BC,0x5368)`, literals `[0x5368,0x5378)`, table `[0xB41C,0xB4C4)`, and all candidate artifact hashes match the receipt. The isolated replay regenerates all 162 fixtures. It checks the exact ordered write ledger and full 256-byte destination, plus R4–R7/SP preservation.

The decoded body agrees with the table-driven flow: copy 21 default words, apply the byte-90 and byte-91 seven-word overlays in sequence, conditionally OR `0x100` into destination word 188 when selector byte 117 is 5, and finally apply the byte-92 overlay. Independent flag values include 0/1/2, so only the exact value 1 activates each overlay; the selector tests 0/5/255 and initial destination values 0/all-ones. The pinned table artifact exports 21 default words and three seven-word overlays.

**Limits:** Context, configuration, and destination use separate buffers. The fixture does not establish alias behavior or physical interpretation of these fields. R0 is documented as incidental and not asserted. No canonical admission is made.
