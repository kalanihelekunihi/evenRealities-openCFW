# tiny-AES-c provider correlation

## Provider decision

Eight complete recovered functions form the AES-128 inverse core published by
kokke/tiny-AES-c. openR1 pins tiny-AES-c v1.0.0 commit
`e72b6eff0884673997d0ca6385169bbd9b31936d` as the compatible provider. The
aggregate evidence proves this source lineage and AES-128 configuration, but it does not uniquely
prove the exact checkout used to build the R1 image.

The provider archive, `aes.c`, `aes.h`, and `unlicense.txt` are SHA-256 pinned in
`third-party/fetched/manifest.json`. Production builds compile that upstream `aes.c` directly. No local
copy or reconstruction of its AES implementation is admitted.

## Exact recovered core

| Recovered entry | Upstream tiny-AES-c symbol | Exact discriminator |
| --- | --- | --- |
| `0x00048948` | `AddRoundKey` | XORs all 16 state bytes with round offset `round * 16` |
| `0x00048AC8` | `InvCipher` | round 10 key, rounds 9…0, inverse mix omitted at the two boundary rounds |
| `0x00061740` | `KeyExpansion` | copies a 16-byte key and produces the 176-byte AES-128 schedule with 44 words |
| `0x0007272E` | `InvMixColumns` | four columns multiplied by the AES inverse matrix constants `0E/0B/0D/09` |
| `0x000727FC` | `InvShiftRows` | exact inverse rotations of rows 1, 2, and 3 |
| `0x00072830` | `InvSubBytes` | 16 indexed substitutions through the inverse S-box |
| `0x00076570` | `Multiply` | five-term GF(2⁸) product built from nested `xtime` calls |
| `0x00098E38` | `xtime` | `(x >> 7) * 0x1B ^ (x & 0x7F) << 1` |

The ownership verifier pins every recovered body above by exact size and SHA-256. The joint call
graph is important: the isolated `xtime` expression is common to many AES implementations, while
this complete eight-function topology and the 176-byte key schedule identify the tiny-AES-c
inverse path.

## R1-owned adapter boundary

Recovered entry `0x00048B02` is not an upstream tiny-AES-c API. It copies input to a distinct
output buffer, decrypts blocks in reverse order with key half 2 and a tail chain initialized from
key half 1, then decrypts forward with key half 1 and a chain initialized from key half 2.
`0x00098E22` is its variable-length XOR helper, and `0x000891A4` is a thin product callback.
All three complete bodies are classified as `r1_product_specific` and pinned by exact size and
SHA-256 in the ownership verifier. This classification admits only their observed behavior for a
clean-room implementation; it does not claim that the recovered expression or instruction
structure is reusable source.

openR1 therefore implements only this recovered chaining/order policy in
`r1/src/r1_crypto.c`. Each block decryption and key expansion is performed through
tiny-AES-c's public `AES_init_ctx` and `AES_ECB_decrypt` APIs. The clean-room adapter rejects
partial blocks and overlapping input/output ranges, records the produced length, and clears the
provider key schedule after use. A pinned 32-byte two-pass vector and the NIST AES-128 ECB vector
are exercised by `make vendor-crypto-test`.

Code signing and deployment authorization are outside this data-transform boundary.
