# nanopb Boolean decoder-pair production-source audit

Status: Apple Clang production ownership closed; exact-root Linux replay pending

Scope: official G2 `2.2.6.10` Apollo-main image, authenticated nanopb source,
the public `pb_decode_bool` leaf, private `pb_dec_bool` field adapter, their
source-owned call closure, entry replacements, and package accounting. This is
offline reverse-engineering and assembly evidence; it does not sign, flash, or
operate hardware.

## Result

Two separately bounded stock functions are now source-owned:

| Function | Official span | Bytes | SHA-256 | Direct caller |
|---|---:|---:|---|---:|
| `pb_decode_bool` | `[0x0049012C,0x00490150)` | 36 | `946ebcb7df90360a19f331bbe5c3962deade8c0525ce4c3ef2d1698263e94b1e` | `0x004901D0` |
| private `pb_dec_bool` | `[0x004901CC,0x004901D6)` | 10 | `572c2ada01c7ee81d56e65766e4e7219783592d34f3399ee6bc761b7c494f3e7` | `0x0048F848` |

`open_cfw_nanopb_decode_bool` calls the already production-owned
`open_cfw_nanopb_decode_varint32`. `open_cfw_nanopb_dec_bool` loads the
iterator's `pData` member at recovered offset `+0x1C` and tail-calls the new
public Boolean decoder. There are no stock strings, data objects, compiler
helpers, heap hooks, schemas, or hardware addresses in this two-function
closure.

## Upstream authority

The selected compatibility source remains the offline-authenticated
`nanopb-0.4.9` snapshot:

| Item | Pin |
|---|---|
| Selected commit | `98bf4db69897b53434f3d0ba72e0a3ab1a902824` |
| Selected tree | `2c4c260bcff3f9f7081238d377274dd385d76582` |
| `pb_decode.c` | 53,845 bytes / `e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a` |
| `pb_decode_bool` definition | bytes `[42715,42911)`, 196 / `5db66c94774daecd96a5daf5d83ff441462e4793a76638ef096f82d1c3a9c38f` |
| `pb_dec_bool` definition | bytes `[44696,44844)`, 148 / `e3e930719ed531df7d647cdf9ecd002c522c2d4d55e6f8299c258532713f6e6c` |
| License | Zlib |

The broader point-release audit proves that pristine 0.4.7, 0.4.8, and 0.4.9
remain indistinguishable for the recovered G2 runtime configuration. Selecting
0.4.9 is an openCFW maintenance choice, not a claim that Even Realities used
that precise checkout or an unmodified upstream tree.

Local production pins are:

| File | Bytes | SHA-256 |
|---|---:|---|
| `runtime_nanopb_decode_bool.c` | 1,592 | `ac020d4746af6c6e68dbf10eb796475f3e39fbc63e253fa4320a265f508ca286` |
| `runtime_nanopb_decode_bool.h` | 1,632 | `9dfa4eb516bf8394af1d68fdd294ba60d3e7531301a1a2e20fc1474446ae455a` |
| `runtime_nanopb_dec_bool.c` | 1,508 | `8f2c510bba9eb1fdec823b0855fb17ee08aad39bae6e863369a9877cdb700674` |
| `runtime_nanopb_dec_bool.h` | 2,038 | `d6867428ea9adfe2552199d9716c72e7fb83db6f116c0c390051c7e82132a34a` |

## Exact stock behavior and boundaries

The public body is:

```text
0049012C  push   {r2,r3,r4,lr}
0049012E  mov    r4,r1
00490130  mov    r1,sp
00490132  bl     0x0048F5AE
00490136  cmp    r0,#0
00490138  bne    0x0049013E
0049013A  movs   r0,#0
0049013C  b      0x0049014E
0049013E  ldr    r0,[sp]
00490140  cmp    r0,#0
00490142  beq    0x00490148
00490144  movs   r0,#1
00490146  b      0x0049014A
00490148  movs   r0,#0
0049014A  strb   r0,[r4]
0049014C  movs   r0,#1
0049014E  pop    {r1,r2,r4,pc}
```

It preserves the destination when varint32 decoding fails, maps zero to
`false`, and maps every nonzero 32-bit wire value to `true`. Its only outgoing
call is the `BL` at `0x00490132`, encoding `fff73cfa`, to the source-owned
public varint32 ABI entry at `0x0048F5AE`.

The private adapter is exactly:

```text
004901CC  push   {r7,lr}
004901CE  ldr    r1,[r1,#0x1C]
004901D0  bl     0x0049012C
004901D4  pop    {r7,pc}
```

Its only incoming `BL` is at `0x0048F848` in `decode_basic_field`; its only
outgoing edge is the `BL` at `0x004901D0`, encoding `fff7acff`, to the public
Boolean decoder. The public decoder has no other direct caller. Neighbor pins
close the public predecessor `[0x004900F0,0x0049012C)`, the complete
`pb_decode_svarint` successor `[0x00490150,0x00490190)`, the complete
`pb_decode_fixed64` adapter predecessor `[0x004901AC,0x004901CC)`, and the
first 24 bytes of `pb_dec_varint` at `[0x004901D6,0x004901EE)`. Each neighbor
has its own prologue or return; neither selected span owns shared literals,
padding, or an epilogue.

## ABI closure

The public ABI is `bool (pb_istream_t *, bool *)`. The private ABI is
`bool (pb_istream_t *, const pb_field_iter_t *)`. Recovered target assertions
pin one-byte `bool`, four-byte pointers and `uint32_t`, `pData` at iterator
offset `0x1C`, and a 40-byte `pb_field_iter_t`. The adapter does not inspect the
field type; `decode_basic_field` has already selected the Boolean logical type.

## Apple object and placement closure

Apple Clang 21.0.0 (`clang-2100.3.27.1`) with the production Thumbv7E-M flags
produces:

| Leaf | Object | Text | Unrelocated SHA-256 | Placement | Relocated SHA-256 |
|---|---|---|---|---|---|
| public | 936 / `52b965c6ba1ed396a5407bbe83b7a8793b3a7098e371507590ac5fbc70c798c3` | 28 | `78ba0cb5e4d04780ccf342901f5b391cb7e83c1ddaea2f4c16568b2046c55565` | offset 125,608 / `0x007B2DCC` | `740079cb6d09fc781988afdffaef731dcc7b3f077270cc6838d640f3bd442dfb` |
| adapter | 904 / `29cb46491f2b9e0afc48bfc2ddc32bb57d6504a480220b7c1fc0e05a0f2c5d53` | 6 | `9b19b7f735da3d5d0e070ed5728ee0ece919d6a6a40891554cb611112067b452` | offset 125,636 / `0x007B2DE8` | `f167416fe762edc4e2f78fa03d83a26df55774635ae39a3e641596a15af26d64` |

The public object has one `R_ARM_THM_CALL` relocation at `+8`; the adapter has
one `R_ARM_THM_JUMP24` relocation at `+2`. Both have only ordinary eight-byte
`.ARM.exidx` metadata outside their selected executable section and no
allocated data.

The 36-byte public entry patch is `22f34ebe` plus sixteen Thumb NOPs, SHA-256
`320c3cf0e367dd80e427d586702c429c33908fdd572c0c7c514274d393fe4f4c`.
The 10-byte adapter patch is `22f30cbe` plus three NOPs, SHA-256
`4ef15d913b67ef0e6f8af3f7b072f1fb7a7eb3ed980955b030ccbfd7bc6509f7`.

## Manifest and aggregate accounting

The Apple overlay is 125,642 bytes and hashes to
`1b3b0079c710cd4eab93e3a2fdf9b08df541e31ac127e222ea584cff3e639997`.
The 3,649,038-byte Apollo component hashes to
`589379f0eec3008700d74277b61e006c264f5e89f8db4505cba302c602d0baa8`.
The 4,427,532-byte package hashes to
`8d48624d32ba7303eb7bbb65aa5e3280177ae97f31a6af2facbf68eadcf3100f`.
The 974-region Apollo manifest produces 1,046 placed flash regions and two
unresolved preserved regions.

Exact package ownership is 126,410 source bytes (2.855089%), 89,005 generated
bytes (2.010262%), and 4,212,117 opaque compatibility bytes (95.134648%). The
controlled total is 215,415 bytes (4.865352%). The two stock spans move 46
bytes from opaque to generated ownership and the appended leaves add 34 source
bytes.

Exact-root Linux Clang 22.1.8 object, placement, entry-patch, aggregate, and
ownership pins remain pending a reviewed replay. No Linux values are inferred
from Apple output.
