# G2 bootloader numeric and format-primitive source closure

Nine adjacent authenticated entries are source-owned:

| Stock span | Recovered contract | Callers | Compiled leaf |
|---|---|---:|---:|
| `[0x00415844,0x00415900)` | unsigned 64-bit divide by ten | 2 | 106 B at `0x004348D0` |
| `[0x00415900,0x00415924)` | unsigned decimal digit count | 2 | 28 B at `0x0043493A` |
| `[0x00415924,0x00415936)` | signed-magnitude decimal digit count | 1 | 20 B at `0x00434956` |
| `[0x00415936,0x0041595C)` | hexadecimal digit count | 1 | 24 B at `0x0043496A` |
| `[0x0041595C,0x004159A0)` | optional-minus, uint32-wrapping decimal parser | 2 | 48 B at `0x00434982` |
| `[0x004159A0,0x00415A08)` | unsigned 64-bit decimal output, nullable destination | 4 | 74 B at `0x004349B2` |
| `[0x00415A08,0x00415A7C)` | unsigned 64-bit hexadecimal output, case selector, nullable destination | 1 | 72 B at `0x004349FC` |
| `[0x00415A7C,0x00415A94)` | nullable string length | 1 | 20 B at `0x00434A44` |
| `[0x00415A94,0x00415AB6)` | repeated-character output, nullable destination | 5 | 32 B at `0x00434A58` |

The decimal counter and decimal-output leaf each call the source-owned
divide-by-ten helper. The signed counter tail-calls the unsigned counter. All
other leaves are relocation-free. Strict extraction pins authenticate every
source, stock span, caller topology, object, relocation, final byte sequence,
and placement.

Host tests cover quotient boundaries and deterministic random values, signed
extrema, digit boundaries, parser consumption/sign/wrap behavior, decimal and
hexadecimal output including `UINT64_MAX`, upper/lowercase selection, nullable
output length calculation, nullable strings, and nonpositive repeat counts.

The canonical 1,536-byte overlay hashes to
`6349a7c29d08cab96c499c53ef3527ecc0569cf03be9bb38e412de96e0564273`.
Its 150,136-byte provider hashes to
`c210163056368efdd4acaefa5a952a2a720b39a41b4519203b6ce10f0020639d`
and contains 1,529 compiled-source bytes, 2,078 generated redirect/NOP bytes,
eight generated alignment bytes, and 146,521 retained authenticated bytes.
The Linux provider hashes to
`53a05ce39aadf648ba39eba045cbbf316ce8e66276c28160f91b97e85e0f15b7`.

The unsigned canonical package is 4,731,714 bytes with SHA-256
`47f05f015e7f347a541a55c150d426449ec591e2b345625020a74443f57ee1fe`;
its 4,327,994-byte flash plan hashes to
`5f87afc33d0d6f747e2f29be888eb4a98aec1ce3e404addf55611a05cb84e643`
and contains 6,234 placed, two unresolved, five container-only, and six
protected regions. The Linux package is 4,507,724 bytes with SHA-256
`3b0b9f9b998e47f7473413278602bb9f368610c63eb8efbfbdfe81003bf2860b`;
its 2,303,131-byte flash plan hashes to
`af6ea4fa6d5d2a54ba86e9e18565d7853b57c5ce6468efb7f11f9debb1db9968`
and contains 3,312 placed regions with the same unresolved and protected
boundaries.

Software closure is complete only for these nine helpers. The adjacent
floating-point conversion and formatter bodies remain software gaps. Physical
boot and caller-path evidence is blocked because no authorized responsive G2
right temple is available; the left temple remains stock. Nothing was signed,
transmitted, or flashed.
