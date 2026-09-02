# G2 bootloader floating common-divisor source closure

The authenticated stock entry is `[0x00426D48,0x00426DB2)`, 106 bytes,
SHA-256 `f6d214ecce42adb7ca36928d8d457c2d6c18af45c10cc68da953d3252290eeed`.
Its direct callers are `0x00426DCE` and `0x0042706C`; no interior halfword
has a direct caller or stored entry pointer. The body performs at most 16
Euclidean remainder iterations, terminates below `2^-23`, calls the retained
`floorf` veneer at `0x00427C90`, and returns `-1.0f` on exhaustion. The
Apollo-main analogue at `0x0053937C` agrees in 102 of 106 bytes; only its
provider-call displacement differs.

`runtime_float_gcd_426d48.c` is 1,176 bytes of clean-room MIT C, SHA-256
`64c0ae997c107d5eb83f6856c94f7e8a3e5fae86f003df81a5ad57b7a56bc781`.
The stock caller passes inputs through `s0` and `s1`, and `floorf` consumes and
returns `s0`; the production entry and provider explicitly declare
`pcs("aapcs-vfp")`. This replaces the earlier softfp-incompatible declaration.

Apple clang 21.0.0 and Homebrew clang 22.1.8 emit the same 92-byte leaf. Its
unrelocated SHA-256 is
`650ac1e603da47c895eecf060ce578e346835c18ae8c4720fe99a3aca4798b03`;
after the strict call relocation at offset `0x36`, its SHA-256 is
`5f1d08b32b7c2291eabdff7d7ab4b17d63b265f827338acf974af4f67c082d5c`.
It occupies `[0x00415C64,0x00415CC0)`, and the stock entry is a generated
`B.W` plus NOP fill.

Current deterministic Apple/Linux provider hashes are
`ac373b3c0caa5dcb6ae25cf6f004c76e778d936b7a584e3ecdf83a17283bca36`
and `4993c8d06b148fa4518268af8fd5133e1494f18c74387249326dac78da1ddde0`.
Complete package hashes are
`12a36be93bc410f2e9e122343455b24888b3750c3c0888a4410aa46cf983b891`
and `a17eb8cb3527d7956c9da71f450488a0e19e08d3862e4753ec62d1ffaf4472af`;
both have zero unresolved flash regions.

No signing, flashing, reset, MMIO access, or physical-device operation was
performed. Target ABI behavior, timing, caller integration, and cold boot are
blocked by unavailable physical evidence. Firmware-wide completeness is not
claimed.
