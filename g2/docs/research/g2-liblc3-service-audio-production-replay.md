# G2 LC3 service-audio production-order replay

This software receipt closes the exact runtime-import and final-relocation
subproblems for the admitted Apollo-main LC3 encoder. It does not write a
firmware image, authorize a stock patch, update an OTA integrity record, or
claim hardware behavior.

## Exact import ownership

The specialized Apple closure retains exactly 11 external symbols. Ten are
implemented by the freestanding MIT-licensed scalar provider in
`components/shared/liblc3/runtime_liblc3_target_runtime.c`. The target compile
requires every export to be a whole global/default `STT_FUNC`, rejects any
undefined symbol, and fixed-address links all ten functions plus their private
clear helper with zero output relocations. Placement uses only the remaining
authenticated, target-free NOP tails after the 84-leaf strict suffix pack.

The eleventh import, `sqrtf`, binds to the existing source-owned
`open_cfw_iar_sqrtf` at `0x007B42B6` (Thumb value `0x007B42B7`). Its current
core receipt authenticates the complete 28-byte function and its single
`R_ARM_THM_JUMP24` tail relocation to source-owned
`open_cfw_iar_domain_error`.

The canonical Apple bindings and LC3 consumer relocation counts are:

| Import | Thumb binding | Provider | Consumers |
| --- | ---: | --- | ---: |
| `__aeabi_memclr` | `0x004577BF` | LC3 target runtime | 1 |
| `__aeabi_memclr4` | `0x004577BB` | LC3 target runtime | 2 |
| `fabsf` | `0x004577B5` | LC3 target runtime | 9 |
| `floorf` | `0x0045775D` | LC3 target runtime | 1 |
| `fmaxf` | `0x004576C1` | LC3 target runtime | 6 |
| `fminf` | `0x0045767F` | LC3 target runtime | 1 |
| `memcpy` | `0x00457785` | LC3 target runtime | 6 |
| `memmove` | `0x00457703` | LC3 target runtime | 4 |
| `memset` | `0x004577A7` | LC3 target runtime | 1 |
| `sqrtf` | `0x007B42B7` | source-owned core leaf | 6 |
| `truncf` | `0x00457733` | LC3 target runtime | 1 |

The Apple target runtime is 324 code bytes. Its relocatable object is 3,552
bytes with SHA-256
`32c8fd25c4f2f46797bf60ca6dd562e58814d958d9f0bcb755445b4c9c3ac6aa`;
the zero-import fixed-address ELF is 32,360 bytes with SHA-256
`f6d417f3e3f052b948ef76168f41f2d294e2dc67e8413f6f288333c4eb60c42e`.
The independent LLVM 22 compile is 318 code bytes, a 3,528-byte object, and a
32,352-byte fixed ELF. Differences are independently pinned rather than
treated as byte-equivalent.

Host qualification exercises guarded copy/set/clear operations, both overlap
directions and exact alias for `memmove`, deterministic finite float grids,
subnormals, infinities, NaNs, and signed-zero min/max/floor behavior. These are
software semantics checks; they are not target timing or hardware evidence.

## Complete relocation replay

The builder preserves the route's relocation-bearing object, then links it at
the exact capacity-proven order:

1. 404-byte `.lc3_table_rodata` at `0x007EA620`,
2. 60,480-byte `.rodata` at `0x007EA7C0`, and
3. 19,360-byte `.text` at `0x007F9400`.

The Apple text ends at `0x007FDFA0`, 96 bytes before protected
`0x007FE000`. All 485 input relocations are consumed: 224 `R_ARM_ABS32`, 238
`R_ARM_THM_CALL`, and 23 `R_ARM_THM_JUMP24`; no relocation or undefined import
remains in the final ELF. By input section they are 78 table, 74 read-only,
and 333 text relocations. The input-record digest is
`2eec52d62c54fb3f7922e4f8f48b00c6034634ca0f050c2bd7ee3a05c78acf15`.

The finalizer separately validates all 78 immutable table initializers
word-for-word and preserves all six authenticated code references to the five
tables. Final Apple artifacts are:

| Section | Bytes | SHA-256 |
| --- | ---: | --- |
| text | 19,360 | `86553c51050d3797a6e6282e04fad2be1d1a07c0044988868631e7f0cd4a3f47` |
| rodata | 60,480 | `2b162cbd557aa106f2bfb30637fe6c620c9852858a54195a616ab52449836797` |
| table rodata | 404 | `6f9aa167cd171d8328ca185e70ce2ada7c8bdd17440c8d7dac2f62fa0ef3f18f` |

The 137,988-byte final ELF has SHA-256
`eabee1e399c2a216e6971fa7756cd6395b193b32f70b8a293ac34ae7cf6f2bc4`.
Its two exact non-linking Thumb veneers remain `82f2d6be` from stock encode
entry `0x0057A940` to `0x007FD6F0` and `82f253bf` from stock setup entry
`0x0057A926` to `0x007FD7D0`.

The independent LLVM 22 replay consumes 486 input relocations (one additional
`fabsf` call), preserves the same 78 initializers and six references, and
leaves zero outputs. Its 19,308-byte text ends at `0x007FDF6C`; its final ELF
SHA-256 is
`48005f2ca8b9ea3961422dd58a09afa02e446ad7b88bb1a609fb809c74efdaab`.

Canonical report digests are
`bfd15afbbb89881462facee37939a00e9d7b40da7b8e53bf18bc24182b91997c`
for Apple Clang and
`d18cfd2720e77c59ba780a866a683e7fee33f4c5e073ecedfa38a6adeee03b67`
for LLVM 22.

## Remaining fail-closed boundary

Import ownership, relocation replay, immutable table initialization, branch
reach, and the four exact 2,628-byte RAM contexts are now software-closed in
one deterministic replay. Production routing remains false because the
canonical package builder does not yet atomically apply the target-runtime
tail payloads, 84 suffix moves and redirects, three LC3 XIP sections, two
service-audio veneers, and package CRC/integrity changes as one verified OTA
transaction. The replay intentionally emits no combined image while that
ownership/integrity step is absent.

Run the focused gates with:

```sh
python3 -m unittest -v \
  g2.tests.test_runtime_liblc3_target_runtime \
  g2.tests.test_apollo_liblc3_service_audio_production_replay
```
