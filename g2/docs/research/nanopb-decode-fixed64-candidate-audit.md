# nanopb `pb_decode_fixed64` production-source audit

Status: bounded Apollo-main production source leaf closed over source-owned
`pb_read`; three retained stock identity/data seams remain

Scope: official G2 `2.2.6.10` Apollo-main image, authenticated nanopb
compatibility source, the source-owned `pb_read` ABI seam, Apple Clang 21.0.0 and
exact-root Linux Clang 22.1.8 production objects, entry replacement, manifest
ownership, and package accounting. This remains offline assembly evidence;
no signing flow or hardware state is changed.

## Result

The 32-byte official function at `[0x004901AC,0x004901CC)` is nanopb's
`pb_decode_fixed64()` under the recovered 64-bit, little-endian callback-stream
configuration. Its complete algorithm is available from authenticated
upstream source and does not need decompilation. It has one G2 dependency: the
call to `pb_read()` at `0x0048F3BE`.

The production source leaf is
`components/shared/nanopb/runtime_nanopb_decode_fixed64.c`. Its exported name
is `open_cfw_nanopb_decode_fixed64`, and the Apollo-main overlay redirects the
complete stock span to it. The leaf declares the source-level
`open_cfw_nanopb_read` ABI seam. The subsequent bounded `pb_read` promotion
supplies that implementation through a full-span entry trampoline at the
stable ABI address `0x0048F3BE`. The read implementation is now source-owned;
its separately reviewed binary closure retains only private `buf_read` Thumb
identity `0x0048F3A5` and the two error strings at `0x00787C70` and
`0x0078B690`.

## Source authority and point-release qualification

The source authority is the repository's offline-verifiable nanopb snapshot:

| Item | Pin |
|---|---|
| Selected compatibility tag | `nanopb-0.4.9` |
| Selected commit | `98bf4db69897b53434f3d0ba72e0a3ab1a902824` |
| Selected tree | `2c4c260bcff3f9f7081238d377274dd385d76582` |
| `pb_decode.c` | 53,845 bytes / `e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a` |
| Exact `pb_decode_fixed64` definition | bytes `[43854,44688)`, 834 bytes / `7f9da692a631280aa5b91a5d08440ac68f5060a64814997dde8dcbdb2f0b4974` |
| Recovered G2 options | 1,551 bytes / `ae758999d239e49e2d5c5bf6de3f4aef3aab5cd3c29d8de65c4db301c62899db` |
| License | Zlib |

The exact definition is independently byte-identical in each surviving
pristine release:

| Release | Commit | Full `pb_decode.c` | Definition span | Definition SHA-256 |
|---|---|---|---:|---|
| 0.4.7 | `b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba` | `9ed9e255e433324fc28557adb03bf494a3711c2a0480c97b3690a6871ce29c66` | `[43768,44602)` | `7f9da692a631280aa5b91a5d08440ac68f5060a64814997dde8dcbdb2f0b4974` |
| 0.4.8 | `6cfe48d6f1593f8fa5c0f90437f5e6522587745e` | `9ed9e255e433324fc28557adb03bf494a3711c2a0480c97b3690a6871ce29c66` | `[43768,44602)` | `7f9da692a631280aa5b91a5d08440ac68f5060a64814997dde8dcbdb2f0b4974` |
| 0.4.9 | `98bf4db69897b53434f3d0ba72e0a3ab1a902824` | `e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a` | `[43854,44688)` | `7f9da692a631280aa5b91a5d08440ac68f5060a64814997dde8dcbdb2f0b4974` |

The release identities and complete source hashes are pinned by the existing
point-release audit, and the selected file belongs to the authenticated 0.4.9
Git tree. The official 0.4.9 annotated tag and commit are unsigned, so Git
object integrity is proven but signer identity is not.

The exact historical vendor point release remains unresolved. The stock
`pb_read()` behavior excludes pristine releases through 0.4.6, but controlled
reference builds cannot distinguish 0.4.7, 0.4.8, and 0.4.9. Selecting the
authenticated 0.4.9 snapshot is an openCFW compatibility choice, not a claim
that Even Realities used that checkout or an unmodified upstream tree.

The altered production leaf retains the upstream Zlib notice. Its local pins
are:

| File | Bytes | SHA-256 |
|---|---:|---|
| `runtime_nanopb_decode_fixed64.c` | 2,083 | `865fa587e7b783e83f24107e52bf3010053d0660b06dc0ac2e7f72bb8ad969bc` |
| `runtime_nanopb_decode_fixed64.h` | 1,726 | `6394df89057700817341e0550ae21033629d3a1ea458d5a68a6edc2b233cc6bd` |

## Exact official boundary

The authenticated OTA package is 3,523,396 bytes with SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
Removing its 32-byte wrapper gives the 3,523,364-byte application loaded at
`0x00438000`, SHA-256
`19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

The complete selected stock bytes are:

```text
1cb50c0008226946fff703f9002801d1002004e0dde90001c4e90001012016bd
```

They hash to
`96228dfbdfe30665d79281ba0fd5ba3b3af38701396671cd20b77623ffd82d54`.
The complete instruction sequence is:

```text
004901AC  push   {r2,r3,r4,lr}
004901AE  movs   r4,r1
004901B0  movs   r2,#8
004901B2  mov    r1,sp
004901B4  bl     0x0048F3BE
004901B8  cmp    r0,#0
004901BA  bne    0x004901C0
004901BC  movs   r0,#0
004901BE  b      0x004901CA
004901C0  ldrd   r0,r1,[sp]
004901C4  strd   r0,r1,[r4]
004901C8  movs   r0,#1
004901CA  pop    {r1,r2,r4,pc}
```

This is nanopb's little-endian fast path: read eight bytes into an aligned
local union, return false before touching the destination when the read
fails, otherwise transfer the 64-bit value to the destination and return
true. The source leaf retains that ordering and therefore preserves the
destination on every failure.

The complete predecessor `pb_decode_fixed32` at
`[0x00490190,0x004901AC)` is 28 bytes and hashes to
`1ee27599a8ac5b8d2a0cbaac59986fb49be7b24c348a960a216b8cbbecce5bf3`.
The successor head at `[0x004901CC,0x004901E4)` is 24 bytes and hashes to
`f86ba3605d946c51e45452a18f09d848c26c0373dd08fb9e68206dedc1f68a36`.
The predecessor returns through its own `pop {...,pc}`, and the successor
starts with a distinct `push`; no neighbor falls through into the leaf.
There is no shared epilogue, literal pool, or alignment byte in the stock
span.

## ABI and configuration closure

The recovered callable ABI is:

```c
bool pb_decode_fixed64(pb_istream_t *stream, void *destination);
```

- `r0` is the callback-stream pointer and receives the Boolean result;
- `r1` is a suitably aligned writable eight-byte destination;
- `PB_WITHOUT_64BIT` is disabled;
- `PB_LITTLE_ENDIAN_8BIT == 1` is the selected target path;
- the target has 32-bit pointers, 32-bit `size_t`, eight-bit bytes, and native
  64-bit integers; and
- callback streams and runtime error strings are enabled.

The shared source header pins the G2 `pb_istream_t` layout on a 32-bit target:
callback `+0`, state `+4`, `bytes_left` `+8`, `errmsg` `+12`, total 16 bytes.
The fixed64 leaf itself treats the stream as opaque. Its one call uses
the source-declared ABI:

```c
bool open_cfw_nanopb_read(
    struct open_cfw_nanopb_istream *stream,
    uint8_t *buffer,
    size_t count
);
```

The reviewed fixed64 relocation targets the stable `pb_read` ABI entry at
`0x0048F3BE`; that complete 150-byte entry now redirects to the qualified
source-owned read leaf. The authenticated original body occupies
`[0x0048F3BE,0x0048F454)` and hashes to
`69aecb900c749fd98bd2d05e2229e9a3d6829bd36f3e393f624e3579a9b4af7f`.
The source promotion preserves its bounds, callback, saturating accounting,
and sticky-first-error behavior while retaining the three explicit stock seams
listed above.

No heap, descriptor, schema, generated message, writable global, read-only
literal, AEABI helper, port hook, or hardware address enters the leaf.

## Caller and dependency topology

The sole external ingress is the `BL` at `0x0048F8C6`, encoding
`00f071fc`, inside `decode_basic_field` at
`[0x0048F7F4,0x0048F968)`. That 372-byte caller hashes to
`2b1bf389327c0f6ccde636bbb51e36cd0bab3eccc811db9aa0efd3dbfef9e445`.

A complete application scan found:

- exactly that one external `BL` to the entry;
- no external `B.W`, wide conditional, narrow `B`/conditional branch,
  `CBZ`, or `CBNZ` to the entry or any interior halfword;
- no aligned or unaligned stored even or Thumb entry/interior pointer; and
- no entry shared with either neighbor.

The stock body has one and only one outgoing call: `0x004901B4`, encoding
`fff703f9`, to `pb_read` at `0x0048F3BE`. The production object likewise has
exactly one undefined symbol and one call relocation, both named
`open_cfw_nanopb_read`.

## Cross-profile object, relocation, and placement closure

Both reviewed compilers use the production Thumbv7E-M freestanding flags.
Renaming the former candidate symbol changes only ELF section/symbol strings;
the executable text and sole relocation remain unchanged.

| Property | Apple Clang 21.0.0 | Exact-root Linux Clang 22.1.8 |
|---|---|---|
| Complete object | 936 bytes / `fc8f839b98f4a6da48fa022a5c35c22e19f38bee8045bb731b1230395b485d2e` | 940 bytes / `f447c5715142e7a5b2c144566ac3094a58727611e011137d440e8d549a2e329b` |
| Function section | 28 bytes, alignment 4 | 30 bytes, alignment 4 |
| Unrelocated SHA-256 | `c4cfb6fece88a057c874d8f2ffcce961df9ef15fb16c78421f48396f0cceff2c` | `bfaf01f7496cce042c84c35708421508fbf2fa5acd9d9fcb209753901e09af10` |
| Overlay offset | 124,612 | 126,432 |
| Runtime address | `0x007B29E8` | `0x007B3104` |
| Padding before | 2 bytes | 2 bytes |
| Relocated SHA-256 | `6e970db6346919f9937f459489b5699b1b5bf5e0d2b4f19a327cbbe6d2b4adb0` | `4e067bc2e9e3cb63335507bd64f3e73321c24294ec3313c72f57cd801a9b8968` |

Apple unrelocated and relocated text:

```text
10b582b00c4669460822fff7feff18b1dde900216160226002b010bd
10b582b00c4669460822dcf4e4fc18b1dde900216160226002b010bd
```

Linux unrelocated and relocated text:

```text
10b582b00c4669460822fff7feff00281cbfdde90012c4e9001202b010bd
10b582b00c4669460822dcf456f900281cbfdde90012c4e9001202b010bd
```

Each object has one `R_ARM_THM_CALL` relocation at `+0x0A`, one undefined
symbol (`open_cfw_nanopb_read`), no allocated data, and one ordinary eight-byte
`.ARM.exidx` companion. The relocated calls decode exactly to `0x0048F3BE`.

The complete 32-byte stock entry replacements are one `B.W` followed by
fourteen Thumb NOPs:

```text
Apple: 22f31cbc00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf
Linux: 22f3aabf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf
```

They hash to
`8d2dc699f879d4fb1a33813da444d5af1565cd9e17a93dac0922c9b66f6f3382`
and
`918801fc87be3e7e55a1509e10d0ab05f969b4578038c147fd100e2feecfc9c0`
respectively. Independent branch decoding recovers the exact Apple and Linux
leaf addresses above.

## Bootloader exclusion

No authenticated bootloader homolog was found. The official 148,599-byte
bootloader hashes to
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`
and loads at `[0x00410000,0x00434477)`. It contains no full fixed64 body,
read-prologue or success-store signature, `pb_read` provider signature,
`decode_basic_field` signature, or nanopb runtime error strings. The only two
of 21 aligned `movs r2,#8` sites followed promptly by a call are unrelated
configuration/function-table paths and lack the read/check/64-bit-store
topology. Promotion is therefore intentionally Apollo-main only.

## Differential validation

The focused host harness links the altered production leaf and pristine
authenticated nanopb `pb_decode.c`/`pb_common.c` under the recovered G2 option
header. Both sides receive equivalent callback streams and provider outcomes.

It compares status, 64-bit destination, bytes remaining, bytes consumed,
callback count, and error class across exactly 25,030 cases: 30 directed edge
cases and 25,000 deterministic randomized cases. Coverage includes zero and
all-one values, byte-order witnesses, extra input, every truncated input
length, every insufficient byte budget, callback failure, sticky preexisting
errors, randomized payload lengths, randomized declared budgets, randomized
provider failures, and randomized initial destinations. Every false result
separately asserts that the destination retains its initial 64-bit value.

The target gate independently authenticates the source slice, selected
snapshot context, official body, neighbors, sole caller, sole provider,
complete ingress/pointer closure, local source pins, and target ELF layout.
The focused module passes seven of seven tests. All compiler outputs are
created in operating-system temporary directories and removed by the harness.

## Production registration and accounting boundary

The Apollo-main configuration registers one additional function, patch site,
and relocated leaf: `655/604/86` becomes `656/605/87`. The manifest splits the
official region beginning at wrapped OTA offset `0x581CC` into a 32-byte
`generated_source_entry_replacement` plus its residual official bytes, then
adds one two-byte alignment region and one source-compiled leaf. Apollo-main
region count therefore moves from 935 to 938; bootloader ownership is
unchanged.

The profile-specific build delta is:

| Artifact/accounting | Apple Clang 21.0.0 | Exact-root Linux Clang 22.1.8 |
|---|---|---|
| Overlay | 124,610 -> 124,640 / `476843181113c88594d1a766a60b91a15a3ec76a4c898c46d3176f64ea21c867` | 126,430 -> 126,462 / `f5d4a4e441b1185001e031d1b9d319474ffd721c1280e1611e29f08169cb46cc` |
| Component | 3,648,006 -> 3,648,036 / `d334b5d063701af87691b2c946a315d481d2317f91293517fd16638b06182f07` | 3,649,826 -> 3,649,858 / `0d765ead02aa3d9981fe14b4aa8663bff57f12b307a2f9ce7e6d226225523a16` |
| Main source-owned | 124,792 -> 124,822 | 126,612 -> 126,644 |
| Main generated patch | 86,088 -> 86,120 | 86,254 -> 86,286 |
| Main replaced stock | 86,270 -> 86,302 | 86,436 -> 86,468 |
| Main opaque | 3,437,094 -> 3,437,062 | 3,436,928 -> 3,436,896 |

The Apple package grows by 30 bytes to 4,426,530 bytes and hashes to
`a3d06dd732722859a7cd4da1582cea49464cbbfccdb90e329afa6ec9352195d4`.
The Apple flash plan is 725,221 bytes with SHA-256
`506b34cd171e5d03da34faa9431f44e57b512d5d9e211cff8e9490ab0c716897`
and reports 1,010 placed, two unresolved, and five container-only regions.
The Linux package grows by 32 bytes to 4,428,352 bytes and hashes to
`75af4c1facb8c663cff2a8d4469625261ffa04d9c9587dc0db9ecf2c2f401b6d`.
Its 599,794-byte flash plan hashes to
`14644134ce433085cfba526710635ae6c1f769ab9cd90e27857da15779c3fc80`
and reports 840 placed, two unresolved, and five container-only regions.

At this audit's fixed64-only milestone, exact canonical package ownership
changed from
`125409 / 88122 / 4212969` to `125437 / 88156 / 4212937` on Apple and from
`127305 / 87894 / 4213121` to `127335 / 87928 / 4213089` on Linux, ordered as
source/generated/opaque. The succeeding `pb_read` promotion reclassifies its
150 stock bytes as generated entry replacement and appends the source-owned
158-byte implementation. Current exact ownership is
`125595 / 88306 / 4212787` on Apple and
`127493 / 88080 / 4212939` on Linux. Its current packages hash to
`f861d049873d497b44f25b265bad4a6ba9409aef3ff3abb4ed6abc1a031a4804`
and `0269400751d0ffa0f58c5cf8658b4dbc6e8af90a875d13bc2e5f684a436d26a9`.

No firmware was signed or flashed. No G2 was connected, reset, booted, or
otherwise accessed.

Reproduce the focused production gate with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_runtime_nanopb_decode_fixed64
```
