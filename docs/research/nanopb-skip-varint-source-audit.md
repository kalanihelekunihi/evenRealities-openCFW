# nanopb `pb_skip_varint` production source audit

Status: **production promoted and fail-closed for Apple Clang 21.0.0 and
exact-root Linux Clang 22.1.8**.

The official G2 nanopb-compatible function at
`[0x0048F628,0x0048F64C)` is now a complete source replacement. Production
authenticates all 36 stock bytes, writes one profile-specific `B.W` followed
by sixteen Thumb NOPs, and redirects the unchanged stock caller to a separate
Zlib-licensed `open_cfw_nanopb_skip_varint` source leaf. The leaf binds one
reviewed call seam to source-owned `pb_read` through its stable entry
trampoline at `0x0048F3BE`.

All qualification described here was compilation, packaging, and offline
binary analysis. No image was signed or flashed and no G2 hardware was
operated.

## Result and attribution boundary

The source promotion is approved because the function boundary, caller
topology, and dependency closure are complete:

- the 36-byte stock body corresponds to authenticated nanopb
  `pb_skip_varint` source;
- a whole-application Thumb scan finds exactly one caller and no alternate or
  interior ingress;
- the stock body makes exactly one nonlocal call, to reviewed `pb_read`;
- the production leaf introduces no rodata, writable data, or additional
  runtime dependency;
- Apple and Linux produce the same deterministic object and unrelocated text;
  and
- both full-span patches, manifest ownership records, and aggregate artifacts
  are pinned independently.

The selected upstream baseline is official nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. Authenticated G2 evidence and
controlled reference builds establish compatibility with pristine nanopb
0.4.7 through 0.4.9; they do not prove Even Realities' historical point
release or checkout. The broader pristine `pb_common.c`, `pb_decode.c`, and
`pb_encode.c` translation units remain production-unregistered.

## Authenticated inputs

| Input | Bytes | SHA-256 |
|---|---:|---|
| official OTA package | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| installed application at `0x00438000` | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| authenticated nanopb `pb_decode.c` | 53,845 | `e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a` |
| recovered G2 nanopb option contract | 1,551 | `ae758999d239e49e2d5c5bf6de3f4aef3aab5cd3c29d8de65c4db301c62899db` |

The authenticated upstream release records:

- annotated unsigned tag object
  `b3056c326da0e6cf702fd13ae2fe63225caa0801`;
- commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`;
- tree `2c4c260bcff3f9f7081238d377274dd385d76582`;
- `pb_decode.c` Git blob `068306a05339af05b3b3fb80894746ed9a077bf8`;
  and
- the unchanged upstream Zlib license.

The exact 200-byte upstream `pb_skip_varint` function body hashes to
`4c9c2629d6c8bf7e8e986a8cb54413d39a804ddb0e848c64aae009d3b10aac62`.

## Stock boundary

The stock function is 36 bytes at `[0x0048F628,0x0048F64C)`:

```text
1cb50400012269462000fff7c4fe002804d09df800000006f4d401e0002000e0012016bd
```

Its SHA-256 is
`fae83b1a62a07bb9c7a3d3f6c398bc13433ebe1cd75d01945f83f30e6fcc9c5d`.
The adjacent boundaries are independently pinned:

| Function | Official span | Bytes | SHA-256 |
|---|---|---:|---|
| predecessor `pb_decode_varint` | `[0x0048F5B8,0x0048F628)` | 112 | `f93d678981f92603982c9afc6c6f9976ca14d1a7a7e0bfc949d3ff73f2791ff2` |
| successor `pb_skip_string` | `[0x0048F64C,0x0048F66C)` | 32 | `03afe2d60436676fffba342c7b8c9504992fa903d7cba768396fd1de2c6c66cd` |

The two adjacent skip functions occupy 68 bytes at
`[0x0048F628,0x0048F66C)` and hash to
`5e6ebac0dfbc3643144fae98faa36f618e0394b3a95f0bbba491d3d08b256fb8`.

## Caller and ingress closure

The sole caller is the `PB_WT_VARINT` arm of `pb_skip_field`:

- call site `0x0048F6B6`;
- BL encoding `fff7b7ff`;
- caller span `[0x0048F6A0,0x0048F6EA)`, 74 bytes;
- caller-span SHA-256
  `36089daffbbc82abad65d97ae0fd64b58b8ad227ed585aa704611bc30369912d`;
- caller-address SHA-256
  `50928d08fafc23b989efcfa9f52fda5ea709f3d3f25ade154a3f5a26db7026a1`;
- encoding SHA-256
  `7ed7519397d8ee8f4521fa23f04205e9dbd1acb64edfed6355be43407196c50d`;
  and
- address-plus-encoding record SHA-256
  `b2397ecfb2eb9a346838d99fb183dcc9ab0ec287da915fdbf0d5217bbac88e93`.

Whole-application scans find no additional BL, `B.W`, wide conditional,
narrow unconditional or conditional branch, `CBZ`/`CBNZ`, aligned pointer,
byte-granular even or Thumb pointer, or materialized `MOVW`/`MOVT` address to
the stock entry or an interior byte. The sole caller remains byte-identical
and enters the generated replacement at the original address.

## ABI, behavior, and retained dependency

The source leaf uses the upstream AAPCS32 signature:

```c
bool open_cfw_nanopb_skip_varint(
    struct open_cfw_nanopb_istream *stream
);
```

`r0` carries the stream pointer and returns the Boolean status. The recovered
32-bit callback-stream ABI remains callback `+0`, state `+4`, `bytes_left`
`+8`, and error pointer `+12`, for a 16-byte structure. `bool` and the nanopb
byte type are one byte; `size_t` is four bytes.

The stock body has one outgoing call:

| Call site | Encoding | Target |
|---|---|---|
| `0x0048F632` | `fff7c4fe` | `pb_read` at `0x0048F3BE` |

The authenticated original `pb_read` body occupies
`[0x0048F3BE,0x0048F454)`, is 150 bytes, and hashes to
`69aecb900c749fd98bd2d05e2229e9a3d6829bd36f3e393f624e3579a9b4af7f`.
The production relocation binds the exact three-argument seam
`open_cfw_nanopb_read(stream, buffer, count)` to that address, whose complete
entry now redirects to the source-owned read leaf. Its only remaining stock
closure is private `buf_read` identity plus two error strings.

The source reads exactly one byte per iteration. It returns false immediately
when `pb_read` fails and returns true after consuming the first byte without
bit 7 set. It intentionally adds no ten-byte or overflow limit: arbitrarily
long continuation sequences remain accepted until their terminator or the
stream boundary, matching authenticated upstream behavior.

## Source, object, and extraction pins

| File | Bytes | SHA-256 |
|---|---:|---|
| `runtime_nanopb_skip_varint.c` | 1,925 | `89e53ebc01a2d28c4a94ac4a38313b8213788a23ed55bf767a9e8a5c6d961225` |
| `runtime_nanopb_skip_varint.h` | 2,401 | `30a8aea087894af29396746a31bbebfc9195e12ee4d66e79b4b637828eeab103` |

Apple Clang 21.0.0 and Homebrew Clang 22.1.8 both produce the same 932-byte
object with SHA-256
`651b45c3291a106f6e930129db85af7bbcba416f9ccc260f87b4d5a417eb53d4`.
Compile-twice qualification reproduces that object in each profile.

Both objects contain the same 36-byte, four-byte-aligned unrelocated text:

```text
b0b582b004460df1070500bf204629460122fff7feff18b19df907100029f5d402b0b0bd
```

Its SHA-256 is
`7e2f6a8b3dca56e4c2d0499a6d4f12ad97dc4bc7f127ff6f4c31b8d379f0ba3b`.
The only executable relocation is an `R_ARM_THM_CALL` at text offset 18 to
`open_cfw_nanopb_read`, fixed at `0x0048F3BE`. There is no local rodata,
writable data, or other undefined runtime symbol.

Each object also contains the normal eight-byte CANTUNWIND `.ARM.exidx`
record, `0000000001000000`, SHA-256
`01acecb507abfe1a354aa8064f4af5d3f1acd019e37db3c11c97523b71c76e9d`.
Its metadata-only `R_ARM_PREL31` association is deliberately discarded under
the authenticated CANTUNWIND policy.

## Placement and patch pins

| Profile | Alignment | Source leaf | Relocated text SHA-256 |
|---|---|---|---|
| Apple Clang 21.0.0 | `[0x007B28AE,0x007B28B0)`, 2 B | `[0x007B28B0,0x007B28D4)`, offset 124,300 | `d3a60ee83a801c7f7ae58b45d0a1e7b6d85fd920484f738ea5698b1196897df7` |
| exact-root Linux Clang 22.1.8 | `[0x007B2FCA,0x007B2FCC)`, 2 B | `[0x007B2FCC,0x007B2FF0)`, offset 126,120 | `09b1b218b4b222b284b44d433b5ae257e70c13b9cab13e7d53ca9168e7bcf27c` |

The generated replacements are:

| Profile | Replacement | SHA-256 |
|---|---|---|
| Apple | `23f342b9` plus 16 x `00bf` | `ec17aa0a8e01050d8b30f737e7ca83d4b8842da1d7d33f6b3b74fa199a4f4519` |
| Linux | `23f3d0bc` plus 16 x `00bf` | `f54c433a31f74f74b34709901da696d850b4dd2d0fb743b8166d49256c287303` |

The patch generator rechecks the exact stock size and hash before assembly.
Post-assembly scans require the sole retained stock caller to enter the
generated redirect and reject every branch or stored pointer to the relocated
leaf interior or either alignment byte.

## Phase-local aggregate production pins

| Profile | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 124,336 / `97c57c110eb7b5fb7474bf945f35121432dfd713c02fcd47931da699c1da739a` | 3,647,732 / `6f58d53a7f747ef8e9f701d01eb9fe1364dd3770df23aed58d9d6f0e7f743d99` | 4,426,186 / `21becb0b47e98f4bb50a296f4e9211a8b43ee57645e0c84e6d2053a15c5340ec` |
| exact-root Linux Clang 22.1.8 | 126,156 / `e7f3d94e8a7253f761c5d535dba918b765c9f3f2aba82a5cdc5372bd0ebf9d62` | 3,649,552 / `160c431d1ff7ea9bd941583705fd2ebfb9cb6b7037298bf3d0bd8f2bd72dbd71` | 4,428,006 / `44adc5125db5e459bc0e32f258a02fbf2f564f8f4f739b542d7406741c046ab1` |

The cross-profile overlay config contains 643 functions, 592 patch sites, and
74 relocated leaves. The canonical Apollo-main manifest has 898 exactly
tiled regions:

| Address status | Regions | Bytes |
|---|---:|---:|
| container-only | 1 | 32 |
| generated alignment | 41 | 82 |
| generated source-entry replacement | 578 | 85,662 |
| generated exact load image | 1 | 6 |
| generated exact replacement | 7 | 134 |
| official blob | 177 | 3,437,344 |
| source compiled | 93 | 124,472 |

Exact whole-package ownership is 125,107 source, 87,814 generated, and
4,213,265 opaque bytes for Apple. Linux exact ownership is 126,988 source,
87,753 generated, and 4,213,265 opaque bytes.

The coarser Apple flash plan is 686,335 bytes, SHA-256
`ade1ae21d30884a7007289b6f53a3ce60e71d8c4227293c935f0b0019acd71b7`,
with 954 placed, two unresolved, five container-only, and 961 total records.
It classifies 125,092 source, 87,677 generated, and 4,213,417 opaque bytes.
The Linux flash plan is 579,136 bytes, SHA-256
`b8b604173230837fddf9553eaf6307c47677404987ce8eec772bc2f815f0f986`,
with 811 placed, two unresolved, five container-only, and 818 total records.
Its package-envelope accounting is 126,997 source, 87,592 generated, and
4,213,417 opaque bytes. These coarse plan classifications do not replace the
exact manifest/package ownership above.

The earlier queue-accessor artifact and accounting tables and all nanopb
aggregate values in this section are phase-local provenance; they are not
current aggregate pins. The subsequent littlefs `lfs_file_size_` production
phase repins the overlay, component, package, manifest, and flash plans without
changing this nanopb leaf, ABI, dependency, or provenance boundary.

## Qualification gate

The focused production suite verifies authenticated snapshot provenance and
the exact upstream function body; source and header pins; compile-twice object
identity under both compilers; exact text, CANTUNWIND, and relocation closure;
upstream/production behavior across empty, terminated, long-continuation,
truncated, and callback-failure streams; stock boundaries and adjacent bytes;
the sole caller and `pb_read` call seam; full-span patch bytes; whole-image
branch and pointer ingress; exclusion of broad pristine translation units;
exact manifest tiling and ownership; and the overlay, component, package, and
flash-plan identities. The promotion is fail-closed at provenance, source,
object, behavior, patch, topology, ownership, and aggregate-artifact layers.
