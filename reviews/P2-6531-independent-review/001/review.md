# Independent review 6531

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet and its 480-byte source slice hash-match. Map 4900 decodes a zero-extended low-byte index, rejects values `>=12`, and uses the literal at 0x427C84 plus `40*index` to select the descriptor. The LDR.W at 0x427820 independently resolves to 0x427C84; that pinned word is 0x430880. The twelve extracted records are each 40 bytes and concatenate exactly to the interval 0x430880..0x430A60.

The mapped consumer reads descriptor offsets 0, 4, 8, 12, and 16 as addresses to dereference. It uses the value at offset 20 in an OR before writing through the offset-16 pointer. Offsets 24..36 are retained as raw record words here; their purpose is not inferred. The `<12` branch is signed `BLT` after `UXTB`, which is equivalent to the claimed bound because the compared value is in 0..255.

This establishes the selected table extent and the listed local access roles, not the meaning of the fields or hardware objects. No canonical files or gates changed.
