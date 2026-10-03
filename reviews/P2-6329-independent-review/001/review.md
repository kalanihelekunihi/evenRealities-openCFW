# Independent review 6329

Disposition: **PASS_SCOPED**; `accepted:false`.

All three packet extents, source-body hashes, and receipt file hashes match the locked image. GNU Thumb decoding confirms three frameless leaves. The initialization leaf uses the first selected word to clear mask 0x1F00, then inserts 1000 (decimal, immediate 0x3E8) into bits 16–31 of a fresh word. It performs five separate selected-word reads whose values are discarded before full-word stores of 0, 800, 450, 600, and 250 (decimal), then freshly clears bit 1 and bit 0 in separate operations on the first word. The enable leaf ORs 3 into its selected word and writes byte 1 to its selected global byte. The disable leaf checks a fresh global byte; when nonzero it clears the low two bits of its selected word and then stores zero to that byte; either branch returns zero.

The reads and writes are individually ordered as described; this does not establish atomicity or hardware meaning. No admission or C-equivalence claim is made, and canonical files/gates remain unchanged.
