# BQ27427 initialized descriptor binding

**The mapping is resolved. Stock configuration targets subclass 105, block 0, byte 5 and writes the whole byte to `0x28`.** It then reaches the normal dirty-gated data-memory commit/checksum path. This is related to the newly acquired Zephyr CC Gain workaround but is not its selective sign-bit clear algorithm.

## Locked initialization evidence

Official Apollo payload SHA-256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`, canonical raw SHA `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`, load base `0x438000`, locked bundle `f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`.

Reuse of the already byte-bound initializer mapping is explicit: scatter record at `0x75D3F4`, compressed stream `0x79189E..0x79430E` (10,864 bytes), destination `0x20000000`, output length 17,752 (`0x4558`). Independent Python decoding and freshly executed original decoder `0x43A11E` agree over the entire record and leave the following 64 guard bytes unchanged. No decoder provider stubs, reset simulation or RAM snapshot assumption is used. Compressed data has no simple one-to-one flash offset for each RAM byte; the authenticated record and decoder establish the mapping.

Decoded RAM `0x200006EC..0x20000724` is the seven-entry table, stride eight. `descriptor-results.json` records exact bytes and full hashes.

| Index | Subclass | Block | Offset | Type | Exact bytes |
|---|---:|---:|---:|---:|---|
| 0 | 82 | 0 | 6 | 2 | 520602000000401f |
| 1 | 82 | 0 | 8 | 2 | 520802000000ff7f |
| 2 | 82 | 0 | 10 | 2 | 520a0200b80b3011 |
| 3 | 64 | 0 | 4 | 1 | 400401000000ff00 |
| 4 | 82 | 0 | 2 | 1 | 520201000000ff00 |
| 5 | 81 | 0 | 0 | 2 | 510002000000d007 |
| 6 | 105 | 0 | 5 | 1 | 690501000000ff7f |

## Actual configured behavior

Root literal `0x53C1CC` points to `0x200006EC`. Configure `0x53BB8C..0x53BCDA`, SHA `aa1a85372d9952b3cba9ec540200536d9e832d0a5c072819e84f246344c0ddb4`, builds the index-6 buffer at sp+0x48 with subclass 105/block 0, calls read at `0x53BCAC`, then sets r2=40 and r1=6 for update at `0x53BCB6`. The buffer is passed to commit at `0x53BCCE`.

Generic update `0x53B6F0..0x53B8BA`, SHA `ffa13effca5ff6bfbc0f8400917e362a63f02ed8334ba11e1d711ca4c2a688f7`, checks buffer+34 valid. Type 1 performs a direct STRB at data offset 5 and sets buffer+35 dirty, with no sign predicate or preservation of low seven bits. Twelve fresh original-instruction cases cover previous bytes 00/28/7F/80/A8/FF with valid 0/1: every valid case becomes 28/dirty1, and invalid cases remain unchanged. The diagnostic-level provider alone returns zero in these tests.

Commit `0x53BA32..0x53BB6A`, SHA `44134f7391a61a7dc4374c84d60c102a5259f696555e17dfa8005a4b2a460371`, gates on dirty, writes class/block and all 32 bytes, executes checksum `0x53B522..0x53B5A0` (SHA `0f5c6c2a0a77e5c674c0bd9d7abb69071a7af4332b2c89601c1d2a71c975f3b1`), writes register 60, and clears dirty on success. A separate fresh original-instruction commit fixture verifies class 105, whole-block write and recomputed checksum. Mode entry/exit, bus writes, diagnostic and delay are explicitly successful stubs in this fixture; no bus or physical gauge is exercised. It is a synthetic post-update buffer, not execution of the full configure/read/commit round trip.

## Zephyr comparison and limits

Pinned official Zephyr driver `87a40fa6068d12d14a7a3521c3d12925da2cc37e` conditionally clears byte5 bit7 and XOR-adjusts checksum, preserving the other seven bits. Stock's constant 0x28 also has sign clear, but overwrites magnitude bits and recomputes checksum for the full block. For prior 0xA8 both produce 0x28; for 0x80 Zephyr produces 0x00 while stock produces 0x28; for sign-clear 0x7F Zephyr leaves 0x7F while stock writes 0x28. Do not call these generally equivalent or assign an erratum rationale from shared addresses alone.

The emulator's zero-byte default cannot prove stock avoids this update: the bounded stock update writes 0x28 whenever its buffer is valid. Full driver execution against that emulator was not tested here. Physical ROM calibration bytes, correctness of constant magnitude, board-family selection, live bus success and later table mutation remain unknown. Initialized table provenance is now closed; it no longer requires an external RAM dump. Source pseudocode and retained disassemblies explain the exact bounded distinction without device writes, emulator changes, production edits, Git or canonical-ledger updates.
