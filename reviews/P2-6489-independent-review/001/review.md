# Independent review 6489

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet source hash and both file hashes match. All 97 listed rows match a fresh extraction from the locked binary, including each 12-byte record's address, raw bytes, little-endian word 0, bytes 4–7, and little-endian word 8. The interval arithmetic is exact: 97 × 12 = 1,164 bytes, and F674 + 0x48C = FB00. The span hash matches the survey's recorded value.

GNU Thumb decoding verifies the caller at 4301D6: it sets R1 to 97, loads R0 from literal 43023C (whose word is F674), calls 430280, then makes the listed later calls, sets R0 to zero, and returns through `POP {R1,PC}`. In combination with the reviewed unsigned index/count loop and 12-byte stride, this supports the stated consumer-defined extent up to FB00.

This does not establish record semantics beyond observed field reads, absence of other consumers, or global code/data classification or admission.

No canonical files or gates changed.
