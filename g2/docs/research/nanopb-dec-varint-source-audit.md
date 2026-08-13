# nanopb private `pb_dec_varint` source audit

## Result

The complete G2 Apollo-main private nanopb `pb_dec_varint` function at
`[0x004901D6,0x00490352)` is now source-recreated. The production leaf is
`components/shared/nanopb/runtime_nanopb_dec_varint.c`; it is altered
Zlib-licensed source selected from the authenticated nanopb 0.4.9 snapshot at
commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`.

Authenticated runtime and reference-build evidence still supports a pristine
nanopb 0.4.7--0.4.9 compatibility interval. Selecting 0.4.9 is a maintained
openCFW baseline, not proof of the vendor's historical point release.

No stock executable or data seam remains in this function. Its two executable
dependencies are already source-owned, and both diagnostics are emitted as
local read-only source data. No image was signed, flashed, or run on hardware.

## Authenticated boundary and upstream source

| Item | Bytes | SHA-256 |
|---|---:|---|
| Official OTA component | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Stock `pb_dec_varint` `[0x004901D6,0x00490352)` | 380 | `ccae20aa7dff8515a5a2b6ad4a05248a865dfaa8c912fd38c8c5f77c3a6a8e0a` |
| Upstream `pb_decode.c` | 53,845 | `e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a` |
| Upstream definition `[44845,47571)` | 2,726 | `be9044f37413d5f5ccacf8b94473552824d913037aa23ff853c59bd77c111b93` |
| Preceding private `pb_dec_bool` | 10 | `572c2ada01c7ee81d56e65766e4e7219783592d34f3399ee6bc761b7c494f3e7` |
| Following boundary literal island `[0x00490352,0x00490358)` | 6 | `21ce7bac3d5f13a0ceb363b9740d84e8d0a487bb76e9e2c509528038f2a683b8` |
| Following `pb_dec_bytes` `[0x00490358,0x004903EA)` | 146 | `c7543cf3079885d044833361ff8331ac10403760377ba3448419255ccae74c37` |

The fail-closed analyzer authenticates all of these spans before accepting the
boundary. Rizin 0.9.1 was used independently to inspect the Thumb control flow,
16-bit iterator loads, 64-bit register pairs, truncation stores, and literal
loads.

## Ingress and outgoing closure

A whole-component Thumb scan covers BL, B.W, wide conditional branches,
narrow B/Bcond/CBZ/CBNZ forms, and byte-granular stored canonical and Thumb
pointers. The only exterior ingress is the expected BL from
`decode_static_field` at `0x0048F872` (`00f0b0fc`) to the function entry. No
branch or stored pointer targets an interior byte. The caller-address digest is
`1caf8859fd83af820c48f63d9cb9373bad8f74b56f1ef11a3c19517a6920f0b5`;
the address-plus-encoding digest is
`915f92293b0a44e365f929a5c3e1512239d00d7a67ca0de69122848a588e68b6`.

The stock body has exactly three linked external calls:

| Call site | Target | Production provider |
|---|---|---|
| `0x004901EC` | `0x0048F5B8` | `open_cfw_nanopb_decode_varint` |
| `0x00490290` | `0x00490150` | `open_cfw_nanopb_decode_svarint` |
| `0x004902A0` | `0x0048F5B8` | `open_cfw_nanopb_decode_varint` |

The stock literal slots at `0x004905C4` and `0x004905C8` resolve to the
NUL-terminated strings `invalid data_size` at `0x0078182C` and
`integer too large` at `0x00781840`. The source closure owns equivalent
18-byte strings and preserves nanopb's first-error-wins rule.

## ABI and behavior

The recovered ABI is:

```c
bool pb_dec_varint(pb_istream_t *stream, const pb_field_iter_t *field);
```

`pb_field_iter_t` is 40 bytes with 16-bit `data_size` at `+0x12`, 8-bit
`type` at `+0x16`, and `pData` at `+0x1C`. The low four type bits select
normal, unsigned, or zig-zag signed varint handling. Sizes 8, 4, 2, and 1 are
accepted. Truncating stores occur before the range comparison, matching
upstream behavior; invalid sizes do not write the destination. For legacy
non-zig-zag fields of 32 bits or less, the decoded unsigned value is first cast
through `int32_t`, preserving nanopb issue-97 compatibility.

Focused host tests cover every size, unsigned and signed limits, legacy
negative encoding, provider failure, truncating overflow, invalid sizes, and a
preexisting sticky error. They also pin the analyzer, target object, overlay,
patch, and manifest registrations.

## Apple Clang production object and placement

Apple Clang 21.0.0 with the reviewed freestanding Thumb flags emits:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Raw ELF object | 1,452 | `02f0886edcb5466cafec9d3904bda0a1ab88a8ab1ae5b9ecd12fb0f5d2c82e20` |
| Unrelocated text | 304 | `87d285297c00b55c45b2ec5705495c772f80f1331ab54667fb7d9f4b3196efad` |
| Relocated text at `0x007B2DF0` | 304 | `b1e508ee7571c033c7beb95301e6323e226b5865e7c9a9c45fd11a2c7c590125` |
| Source diagnostic rodata at `0x007B2F20` | 36 | `42b784209d1e9ff26348f821c401beb47dfdda57c3a399c0c28b002f52540f0f` |
| Text plus rodata closure | 340 | `b015c63f85d575a9d181d2c8c51b5387c86b8759ec6b29e81f48824b2b1dfaca` |

The object carries three source-provider call relocations and three paired
local PREL MOVW/MOVT references to its diagnostic aggregate. There is no
undefined stock symbol. The entry replacement is a B.W plus 188 Thumb NOPs;
its complete 380-byte SHA-256 is
`83503acd8c8719da6e706a535cf9fea83d8be887fdfcf57fc040830e8a6cf5e5`.

## Aggregate effect

The Apple overlay is now 125,984 bytes with SHA-256
`22a9696573e83ba0d79664dcfbdf4d7424fa326bcb5e95bc9d4ce4bdb6079e70`.
The Apollo component is 3,649,380 bytes with SHA-256
`51bb3220d572527954e78a3e51c30f5b4235ec936613c2f6684527ba43bd8be1`.
The canonical core-source package is 4,427,874 bytes with SHA-256
`f13f305ab510f4e6ac3dd20576b2d543fc171314a35b9d194153bbff194b3f87`.
It contains 1,050 placed, two preserved unresolved, and five container-only
regions. The flash-plan JSON is 753,820 bytes with SHA-256
`db98175be8544487a9a95010f160d448a42ad303fef095aa0e1e84c48170111b`.

Package ownership becomes 126,750 source-compiled bytes (2.862548%), 89,387
generated bytes (2.018734%), 216,137 controlled bytes (4.881282%), and
4,211,737 opaque compatibility bytes (95.118718%). The reviewed Linux Clang
22.1.8 object and aggregate replay remain explicitly pending; Apple values are
not copied into that profile.
