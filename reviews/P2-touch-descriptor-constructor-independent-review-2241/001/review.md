# Independent review 2241

**Result:** REVISE_PROSE.

The source, body `[0x5548,0x569E)`, and literal `[0x56A0,0x56A4)` hashes match the receipt. The literal decodes to `0x0FFF0000`; the intervening two bytes at `0x569E` remain excluded. Isolated replay regenerated all 144 rows. The corrected fixtures distinguish parameter byte 32 (packed header field) from byte 33 (count-scaling mode). They assert the full 48-byte output, ordered writes, map-entry/destination child arguments, child-status propagation, and preserved registers. The only intercepted call is child `0x51BC`; the original constructor and `0x5528` execute.

The decoded control flow agrees with the documented map selection, row/parameter strides, `+12` word and optional bit-15 update, child call, validity-dependent status, and `+20` result word. However, the kind-1 first destination word is not fully specified in the pseudocode: “configuration nibbles/byte and parameter halfword12 packed as the replay specifies” delegates the actual formula to the fixture script. For instruction-backed prose, state the masks and positions explicitly: `(config[96]&0x0F) | ((config[93]<<4)&0xF0) | ((config[94]<<8)&0x0F00) | ((parameter.half12<<16)&0x003F0000) | (config[95]<<24)`. This is the only concrete prose correction I found.

**Fixture limits:** Indices are only 0 and 2, kinds only 0/1/2, and each source-field pattern uses either all-zero or one nonzero seed. The corrected byte-32/byte-33 distinction is useful, but broader independent field variation and aliasing are not tested. Child `0x51BC` returns only 0 or 3 without mutating buffers.

**Scope:** No canonical admission is made. Child effects, aliasing, concurrency, and physical field meanings remain unresolved.
