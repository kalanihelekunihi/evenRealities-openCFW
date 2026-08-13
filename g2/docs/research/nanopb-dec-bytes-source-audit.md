# nanopb private `pb_dec_bytes` source audit

## Result

The complete G2 Apollo-main private nanopb `pb_dec_bytes` function at
`[0x00490358,0x004903EA)` is source-recreated. The production leaf is
`components/shared/nanopb/runtime_nanopb_dec_bytes.c`, altered Zlib-licensed
source selected from the authenticated nanopb 0.4.9 snapshot at commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`.

The authenticated compatibility interval remains nanopb 0.4.7--0.4.9. The
0.4.9 pin is the maintained openCFW baseline, not proof of the vendor's
historical point release. No stock executable or data seam remains in this
function: its varint32 decoder and stream reader are source-owned, and all
three diagnostics are local source rodata. No image was signed, flashed, or
run on hardware.

## Authenticated boundary and upstream source

| Item | Bytes | SHA-256 |
|---|---:|---|
| Official OTA component | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Stock `pb_dec_bytes` `[0x00490358,0x004903EA)` | 146 | `c7543cf3079885d044833361ff8331ac10403760377ba3448419255ccae74c37` |
| Upstream `pb_decode.c` | 53,845 | `e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a` |
| Upstream definition `[47571,48677)` | 1,106 | `343c9c20cbd27012513eac9e7950d3c7d03733bb318d608be2f2538c44705374` |
| Preceding literal island `[0x00490352,0x00490358)` | 6 | `21ce7bac3d5f13a0ceb363b9740d84e8d0a487bb76e9e2c509528038f2a683b8` |
| Following `pb_dec_string` `[0x004903EA,0x00490488)` | 158 | `8be0060c8134054cbe4964c682b8b2c22aa6dc170bdf235d3fee97220aaded2f` |

The fail-closed analyzer authenticates every span before accepting the
boundary. Rizin 0.9.1 independently confirmed the Thumb control flow, 16-bit
size header, iterator field loads, and literal-slot references.

## Ingress and closure

The only direct exterior ingress is the BL at `0x0048F8E8` (`00f036fd`) to
the entry. The caller-address digest is
`c682d51419d5c10c414ad0bb61bfea223b4a238ebf78817a7125b5c215b2a6cb`;
the address-plus-encoding digest is
`199a78e75f8c403796b8f557ffddcb017009a0ddd6159f290b51823f560e6055`.
No branch targets an interior byte.

Two byte-granular four-byte scans superficially resemble interior Thumb
pointers. Rizin classifies both as 16-bit pair-table data, not pointers:

| Record | Stored word | 16-bit pair | Classification |
|---|---|---|---|
| `0x0064D2E0` | `0x00490381` | `(0x0381,0x0049)` | non-pointer data record |
| `0x0064E164` | `0x004903B7` | `(0x03B7,0x0049)` | non-pointer data record |

Their 48-byte context digests are respectively
`43481a9e88704a7562acdd0074e0bc075e2c058d213bf4a62fa4d96cbfe7de8d`
and `f46c33eb6145c25296a8bd40d6bce35519fdc06a5569727ed1c7a7c973e7918a`.
The stock body has exactly two external calls: `0x00490362` calls source-owned
`pb_decode_varint32`, and `0x004903E4` calls source-owned `pb_read`.

The stock literal slots resolve to `bytes overflow`, `size too large`, and
`no malloc support`. The source owns a 48-byte aggregate containing all three
NUL-terminated strings and preserves nanopb's first-error-wins rule.

## Configuration and behavior

The recovered configuration uses 16-bit `pb_size_t` with `PB_ENABLE_MALLOC`
disabled. A length larger than `UINT16_MAX` fails with `bytes overflow`.
Pointer-allocated fields fail with `no malloc support`; statically allocated
fields require `length + 2 <= field->data_size`. On a valid field, the 16-bit
length is stored before `pb_read`, so a reader failure retains the decoded
length exactly as upstream does.

The source retains the upstream allocation-overflow guard and its
`size too large` diagnostic even though the reviewed compiler proves that
branch unreachable after the 16-bit size bound. Focused host tests cover
decoder failure, overflow, insufficient storage, disabled pointer allocation,
sticky errors, successful payload placement, and reader-failure ordering.

## Apple Clang production object and placement

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Raw ELF object | 1,224 | `976f145657ac31e8cc1561667dc970de0704377e52f32b72ad5b205f23891395` |
| Unrelocated text | 98 | `015e10515e87a2993c78839e9152a5d1bdc4cc864a7d5b6f4a12945595168506` |
| Relocated text at `0x007B2F44` | 98 | `5ea32d890eb894b11cc01c95edddef23f6e8f7560a44f77878f8884f8ec11f70` |
| Diagnostic rodata at `0x007B2FA6` | 48 | `718eead5f51032fc1fbec902f9720d51167ad6c95bca4d7314a30e8226a5f255` |
| Text plus rodata closure | 146 | `8e35a40f624a8356e7b158fb442afdeb76eba54fe663a5b812cd7dd3cdb368d5` |

The object carries two source-provider calls and two paired PREL MOVW/MOVT
references to local diagnostics. The full stock span is replaced by a B.W and
71 Thumb NOPs; the 146-byte replacement digest is
`739656a5e08296d19f5a917f8b175907b92dadf5a60acd36e4d6d6816965615c`.

## Aggregate effect

The Apple overlay is 126,130 bytes with SHA-256
`0a6aa0d4c0736a3fdc4dfb4cafdb80fad4e6ab3befe3cc3e8d5d383822ec5502`.
The Apollo component is 3,649,526 bytes with SHA-256
`c387d5b4afdd50834c833d942f4b4e8e398bbbc5e31bd9f6c8daced8a9380148`.
The canonical package is 4,428,020 bytes with SHA-256
`e2f7cf1f06f70e9ea1c0a4c7afb57205789f4dfa366d496edcbe3707795c2de2`.
It contains 1,054 placed, two preserved unresolved, and five container-only
regions. The flash plan is 756,646 bytes with SHA-256
`fd7b6932c780572f6edc35f79eacd791854d4dd5e7e84e57d2151384d56d453c`.

Package ownership is now 126,896 source-compiled bytes (2.865750%), 89,533
generated bytes (2.021965%), 216,429 controlled bytes (4.887715%), and
4,211,591 opaque compatibility bytes (95.112285%). The reviewed Linux Clang
22.1.8 replay remains pending; Apple pins are not copied into that profile.
