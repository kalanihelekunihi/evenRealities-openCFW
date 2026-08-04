# nanopb `pb_decode_svarint` production-source audit

Status: Apple and exact-root Linux production ownership recorded

Scope: official G2 `2.2.6.10` Apollo-main image, authenticated nanopb
compatibility source, the existing source-owned unsigned-varint leaf, and an
Apple and exact-root Linux production leaves and their direct
source-to-source relocation. No hardware state is changed.

## Result

The 64-byte official function at `[0x00490150,0x00490190)` is nanopb's
`pb_decode_svarint()` under the recovered 64-bit callback-stream
configuration. Its complete algorithm can be maintained from authenticated
upstream source instead of decompilation. The only G2 boundary is one call to
`pb_decode_varint()` at `0x0048F5B8`; that entry is already redirected to the
production source leaf `open_cfw_nanopb_decode_varint`.

The bounded production implementation is
`components/shared/nanopb/runtime_nanopb_decode_svarint.c`. Its exported name
is `open_cfw_nanopb_decode_svarint`. The Apollo-main overlay binds its sole
relocation directly to the source-owned unsigned decoder and replaces the
complete stock span with a non-linking `B.W` plus 30 Thumb NOPs.

## Source authority and point-release qualification

The source authority is the repository's offline-verifiable nanopb snapshot:

| Item | Pin |
|---|---|
| Selected compatibility tag | `nanopb-0.4.9` |
| Selected commit | `98bf4db69897b53434f3d0ba72e0a3ab1a902824` |
| Selected tree | `2c4c260bcff3f9f7081238d377274dd385d76582` |
| `pb_decode.c` | 53,845 bytes / `e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a` |
| Exact `pb_decode_svarint` definition | bytes `[42912,43210)`, 298 bytes / `df1caa71053163bdefaea7d6b19bdc72f10c63f09430003b88f10fb7dac3ff6e` |
| Recovered G2 options | 1,551 bytes / `ae758999d239e49e2d5c5bf6de3f4aef3aab5cd3c29d8de65c4db301c62899db` |
| License | Zlib |

The exact historical vendor point release is not proven. G2's discriminating
`pb_read()` and `pb_decode_varint()` instructions exclude pristine releases
through 0.4.6, while controlled builds make pristine 0.4.7, 0.4.8, and 0.4.9
runtime object triplets byte-identical. openCFW deliberately selects the
authenticated 0.4.9 snapshot as a compatibility baseline; it does not claim
that Even Realities used that checkout or rule out an equivalent vendor fork.

The altered production leaf retains the upstream Zlib notice. Its complete local
pins are:

| File | Bytes | SHA-256 |
|---|---:|---|
| `runtime_nanopb_decode_svarint.c` | 1,943 | `f361cafc8813257e16fafb9ee986c88c632eb2c7edc604dcb02e27ec85a7df4d` |
| `runtime_nanopb_decode_svarint.h` | 1,789 | `d1ca3c0520784c4837c9570416934c7884eeeba2eba2a42091cd040d5222e72c` |

## Exact official boundary

The authenticated official package is 3,523,396 bytes with SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
Removing its 32-byte OTA wrapper gives the 3,523,364-byte application at
`0x00438000`, SHA-256
`19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

The selected stock bytes are:

```text
1cb50c006946fff72ffa002801d1002015e0dde90001c00709d5dde900014908
5fea3000c043c943c4e9000106e0dde9000149085fea3000c4e90001012016bd
```

They hash to
`80b24be422cf924f3ae1b79669312535dc0d5a56dd88be8a6b9e4ee5ff064048`.
The complete instruction sequence is:

```text
00490150  push   {r2,r3,r4,lr}
00490152  mov    r4,r1
00490154  mov    r1,sp
00490156  bl     0x0048F5B8
0049015A  cmp    r0,#0
0049015C  bne    0x00490162
0049015E  movs   r0,#0
00490160  b      0x0049018E
00490162  ldrd   r0,r1,[sp]
00490166  lsls   r0,r0,#31
00490168  bpl    0x0049017E
0049016A  ldrd   r0,r1,[sp]
0049016E  lsrs   r1,r1,#1
00490170  rrxs   r0,r0
00490174  mvns   r0,r0
00490176  mvns   r1,r1
00490178  strd   r0,r1,[r4]
0049017C  b      0x0049018C
0049017E  ldrd   r0,r1,[sp]
00490182  lsrs   r1,r1,#1
00490184  rrxs   r0,r0
00490188  strd   r0,r1,[r4]
0049018C  movs   r0,#1
0049018E  pop    {r1,r2,r4,pc}
```

Every instruction has an exact upstream role: decode an unsigned 64-bit
varint to a temporary; return false without touching the destination on
failure; test bit zero; compute either `~(value >> 1)` or `value >> 1`; store
the complete 64-bit result; and return true.

The predecessor `pb_decode_bool` at `[0x0049012C,0x00490150)` is 36 bytes and
hashes to
`946ebcb7df90360a19f331bbe5c3962deade8c0525ce4c3ef2d1698263e94b1e`.
It returns through its own `pop {...,pc}`. The following source-owned
`pb_decode_fixed32` stock boundary begins with its own prologue at
`0x00490190`; `[0x00490190,0x004901AC)` is 28 bytes and hashes to
`1ee27599a8ac5b8d2a0cbaac59986fb49be7b24c348a960a216b8cbbecce5bf3`.
There is no shared epilogue, fallthrough, literal pool, or alignment byte in
the replaced span.

## ABI and configuration closure

The recovered callable ABI is:

```c
bool pb_decode_svarint(pb_istream_t *stream, int64_t *destination);
```

- `r0` is the callback-stream pointer and receives the Boolean result;
- `r1` is an eight-byte signed destination;
- the destination is written only after unsigned decoding succeeds;
- `PB_WITHOUT_64BIT` is disabled;
- the target has 32-bit pointers and two's-complement 64-bit integers; and
- callback streams and runtime error strings are enabled.

The production leaf reuses `runtime_nanopb_decode_varint.h`, whose 32-bit target
assertions pin the G2 `pb_istream_t` layout: callback `+0`, state `+4`,
`bytes_left` `+8`, `errmsg` `+12`, total 16 bytes. The signed leaf never
dereferences the stream itself; the source-owned unsigned provider owns that
ABI and all error/consumption behavior. The production header separately
asserts eight-byte signed and unsigned scalar widths and the target's
two's-complement relation.

No heap, descriptor, schema, generated message, first-party callback,
writable global, read-only literal, port hook, or hardware address enters the
leaf.

## Caller and dependency topology

The sole external ingress is the `BL` at `0x00490290`, encoding
`fff75eff`, inside `pb_dec_varint` at `[0x004901D6,0x00490352)`. That
380-byte caller hashes to
`ccae20aa7dff8515a5a2b6ad4a05248a865dfaa8c912fd38c8c5f77c3a6a8e0a`.
The packed caller address hashes to
`24a39bc0e5db3354edc0720e0677567cdb9316e1eb64ffed2fefcf7ff890acee`;
the address-plus-encoding record hashes to
`9a00fb7e6b4c861087633683fbb5f387b42af17393ea41634e2262e2d16928c2`.

A complete application scan found:

- exactly that one external `BL` to the entry;
- no external `B.W`, wide conditional, narrow `B`/conditional branch,
  `CBZ`, or `CBNZ` to the entry or any interior halfword;
- no aligned or unaligned stored even/Thumb entry or interior pointer; and
- no entry shared with either neighbor.

The stock body has one and only one outgoing call: `0x00490156`, encoding
`fff72ffa`, to `pb_decode_varint` at `0x0048F5B8`. The complete 112-byte
stock callee hashes to
`f93d678981f92603982c9afc6c6f9976ca14d1a7a7e0bfc949d3ff73f2791ff2`.
That stock entry is already replaced in production by the qualified
`open_cfw_nanopb_decode_varint` source leaf. Production testing links the
signed leaf to that exact production source, while its reference side invokes
pristine authenticated upstream `pb_decode_svarint()` and
`pb_decode_varint()`.

## Apple target-object closure

Apple Clang 21.0.0 (`clang-2100.3.27.1`) compiles the production leaf twice with
the production Thumbv7E-M freestanding flags and produces identical objects:

| Property | Pin |
|---|---|
| Complete object | 972 bytes / `ac61ef30926a714ee4338414dcdc0de304d50b866f69a3f7c625b12c5d5a8435` |
| Function section | 54 bytes, alignment 4 |
| Function SHA-256 | `19e103f83ab8879d36eb1b0513bf541601e40bc82e69e0dc252308c0646d1286` |
| Text relocations | one: `+0x08`, `R_ARM_THM_CALL`, `open_cfw_nanopb_decode_varint` |
| Undefined symbols | only `open_cfw_nanopb_decode_varint` |
| Allocated data | none |
| Allocated metadata | one ordinary eight-byte `.ARM.exidx` section |

The leaf has no local strings, writable state, or extra provider. Its call is
registered as `target_function: open_cfw_nanopb_decode_varint`; there is no
fixed stock target. Apple appends the relocated text at overlay offset
124,916 / runtime `0x007B2B18`, where it hashes to
`1b181a82adbbb72dc6fc09b1b70dd48f4c0eefdf25a8c4e71701710cb12dae3f`.
The complete 64-byte entry replacement hashes to
`e8c5601b86e9a38362fb292b0a8ba70250d2ccc3094d0c8c117b1c33f5bf11cc`.

## Exact-root Linux target-object closure

The reviewed `/Users/kalani/Repo/SybilSightABCD/openCFW` replay uses
`/home/linuxbrew/.linuxbrew/bin/clang`, exactly
`Homebrew clang version 22.1.8`. Two independent compilations produce
identical 968-byte objects, SHA-256
`866820ef347453a3cbf2feed221eeab0b571a9b79b6988cc17d2861b1aeaced5`.

| Property | Exact-root Linux pin |
|---|---|
| Function section | 50 bytes, alignment 4 |
| Function SHA-256 | `3617ea95d4a2cbabf3a1abb375e572323fffcebfa68cb4e19874cb4a831d9662` |
| Text relocations | one: `+0x08`, `R_ARM_THM_CALL`, `open_cfw_nanopb_decode_varint` |
| Undefined symbols | only `open_cfw_nanopb_decode_varint` |
| Allocated data | none |
| Allocated metadata | one eight-byte `.ARM.exidx`, SHA-256 `01acecb507abfe1a354aa8064f4af5d3f1acd019e37db3c11c97523b71c76e9d` |

After two alignment bytes, the linked leaf is placed at overlay offset
126,744 / runtime `0x007B323C`, where it hashes to
`63e4707f5fd537094855d38f6b4df8578b77644c131e180db2e682d32fbc1fab`.
Its sole call resolves source-to-source to `open_cfw_nanopb_decode_varint` at
`0x007B2C80`; no fixed stock target is recorded. The complete 64-byte entry
replacement starts `23f374b8`, continues with 30 Thumb NOPs, and hashes to
`e6bb4ee4baec73757a5f465cf99a32e787fb25bd651b2b16e2e76fda4c6d18fd`.

## Differential validation

The focused host harness links three independently attributable pieces:

1. the altered signed production leaf;
2. the existing production `open_cfw_nanopb_decode_varint` source and its
   host read-byte provider; and
3. pristine authenticated nanopb `pb_decode.c`/`pb_common.c` as the oracle.

It compares status, 64-bit result bits, destination-on-failure preservation,
bytes remaining, bytes consumed, callback count, and error class across more
than 26,000 cases. Coverage includes signed extrema, all important varint
width transitions, 21,000 deterministic random 64-bit encodings,
noncanonical accepted encodings, truncation at every byte, callback failure
at every read, sticky preexisting errors, byte-budget mismatches, overflow
forms, and deterministic malformed streams.

The target gate separately authenticates the source slice, official body,
neighbors, sole caller, sole callee, complete ingress/pointer closure, local
source pins, and target ELF layout.

## Production ownership and remaining boundary

The Apple manifest now splits the exact official range at `0x00490150` into
the 64-byte generated entry replacement and contiguous official neighbors,
then appends the 54-byte source leaf at component offset 3,648,312. It has 951
Apollo-main regions. The resulting Apple artifacts are:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Overlay | 124,970 | `1cfdeb0382a10f1c9dad9d203bd2f3a0d1f56390815eafffcf925f7731bb80ec` |
| Apollo-main component | 3,648,366 | `eaf24d1adce80ce958c5ff90585bc2da6a2f76634a9d2539e3a5cf2b37814bf1` |
| EVENOTA package | 4,426,860 | `e77b984d3644cade761b2aecec399ccb9249c419c2ca6e9f4963cbbbfa208cf7` |
| Component report | 1,506,730 | `416f196c1669b4387a19ddccdd07952e9042db4acc69aad935d83c77e2235ffa` |
| Package report | 2,323 | `8b49f17724accbecd568e046a940868980d28d845d0bb9222fb42a49d9f03b7f` |
| Flash plan | 734,550 | `a14dc76800b140af67678fe7d6b86d92152aeb2a9e523467c84afbe19653e24e` |

The authenticated nanopb allowlist therefore contains ten bounded altered
functions. Pristine nanopb translation units remain unregistered. The
independently recorded exact-root Linux artifacts are:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Overlay | 126,794 | `be028b3e22b5952325965c029523dacb0b2d3bad3602c397de706a53708d88f0` |
| Apollo-main component/provider | 3,650,190 | `78ff4ac1538ad3d43076510f06a9ddb3ba1ca2a0f421d3778f96e2a40c6f1696` |
| EVENOTA package | 4,428,684 | `b5391623b98a886bf87989a5c28c5f500556866d08dbbff5c25535f6f707af06` |
| Component report | 1,526,818 | `9bc54ee3c66ddbbf4e3396143b05af0e156289c9802b6d6b5222d39c6828f2b5` |
| Package report | 2,322 | `a54f2300f21b47519999fd5210f1fb2906410d8d6ee63630420ff018318db112` |
| Flash plan | 604,150 | `5126f5582cbb6a260fccb13aa3b1259863a813867a3d4aac77c83dee2fccb348` |

The Linux plan has 846 placed, two unresolved, and five container-only
records; effective package ownership is 127,675 source / 88,260 generated /
4,212,749 opaque bytes. Nothing in this audit authorizes device execution.

No firmware was signed or flashed. No G2 was connected, reset, booted, or
otherwise accessed.
