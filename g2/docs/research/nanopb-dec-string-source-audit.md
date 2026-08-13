# nanopb private `pb_dec_string` source audit

## Result

The complete G2 Apollo-main private nanopb `pb_dec_string` function at
`[0x004903EA,0x00490488)` is source-recreated. The production leaf is
`components/shared/nanopb/runtime_nanopb_dec_string.c`, altered Zlib-licensed
source selected from the authenticated nanopb 0.4.9 snapshot at commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`.

The authenticated compatibility interval remains nanopb 0.4.7--0.4.9. The
0.4.9 pin is a maintained openCFW baseline rather than proof of the vendor's
historical point release. No stock executable or data seam remains: both calls
terminate in source-owned nanopb providers and all diagnostics are local
source rodata. No image was signed, flashed, or run on hardware.

## Authenticated boundary and upstream source

| Item | Bytes | SHA-256 |
|---|---:|---|
| Official OTA component | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Stock `pb_dec_string` `[0x004903EA,0x00490488)` | 158 | `8be0060c8134054cbe4964c682b8b2c22aa6dc170bdf235d3fee97220aaded2f` |
| Upstream `pb_decode.c` | 53,845 | `e980f2a41d9abe37b7e6fb4c9ba1ebfd68507a6fd2653f8d755e1947a9c84b1a` |
| Upstream definition `[48677,49908)` | 1,231 | `73375d35f4938cd170ac34eb6f32668fcdf253c9b850955524e3a8e5357f8646` |
| Preceding `pb_dec_bytes` | 146 | `c7543cf3079885d044833361ff8331ac10403760377ba3448419255ccae74c37` |
| Successor literal island `[0x00490488,0x0049048C)` | 4 | `f7f19bacfc4d8f9f6d541ca42347ee12eb069b9b747b03ab956e69e5d7b146b9` |
| Following `pb_dec_submessage` `[0x0049048C,0x00490538)` | 172 | `3e28ac2fb953613cff7b8a7c30cfdc91aa6c585ea44769e7f64603be853f6f91` |

The fail-closed analyzer authenticates every span before accepting the
boundary. Rizin 0.9.1 independently confirmed the complete Thumb body,
iterator offsets, 32-bit size arithmetic, diagnostic loads, and provider calls.

## Ingress and closure

The sole exterior ingress is the BL at `0x0048F90A` (`00f06efd`) from
`decode_static_field`. The caller-address digest is
`a47c2c2f311117ed8061190f3e8f5f0fac13fb4ef98b7d32db420b11bee96299`;
the address-plus-encoding digest is
`2805361f141a407619453f9c99d5d62ee49b37e5d02a5fbf05efa63913b03cc1`.
The 32-byte caller context digest is
`18266aa7fd75c47de34fe4107856c38bae9c17305ccd97ce1ab90ca2ece74ad8`.
No wide, narrow, or conditional branch targets an interior byte, and no
canonical or Thumb pointer pattern names the entry or an interior address.

The stock body calls source-owned `pb_decode_varint32` from `0x004903F6` and
source-owned `pb_read` from `0x00490478`. Literal slots resolve to
`size too large`, `no malloc support`, and `string overflow`; the production
source owns a 49-byte aggregate with all three NUL-terminated strings and
preserves nanopb's first-error-wins behavior.

## Configuration and behavior

The recovered target has 32-bit `size_t`, 16-bit `pb_size_t`,
`PB_ENABLE_MALLOC` disabled, and `PB_VALIDATE_UTF8` disabled. A decoded
`UINT32_MAX` length and any allocation-size wrap fail with `size too large`.
Pointer fields fail with `no malloc support`; static fields require
`length + 1 <= field->data_size`. The terminator is stored before `pb_read`,
so it remains present if the reader fails, matching upstream ordering.

Focused host tests cover decode failure, maximum length, disabled pointer
allocation, insufficient storage, sticky diagnostics, empty strings,
successful reads, and read failure after terminator placement.

## Apple Clang production object and placement

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Raw ELF object | 1,260 | `ffbb4295bfecc6a32306669cf6b367e1692cfc56766f5bcefa72aa45c29b3f91` |
| Unrelocated text | 114 | `8bb5ae7a48ad06f4f7d8748ca7b39c1274ac997d3eca59a8cb2e08ca5a40af58` |
| Relocated text at `0x007B2FD8` | 114 | `7fd11bd5b7f323722739a9f0a19ccba696e5b04659b2d917ec8bd69ae96161c4` |
| Diagnostic rodata at `0x007B304A` | 49 | `997f0ec78270c8595ea07bc75acc9467b3adb246d10a6ad02da619d1d4686161` |
| Text plus rodata closure | 163 | `c0be9fa4a77f3390c9e37325512cb946fe2e673224c0b7d05c3558111926b5cf` |

The object carries two provider-call relocations and three paired PREL
MOVW/MOVT references to the diagnostic aggregate. Two generated zero bytes
align the leaf. The full 158-byte stock replacement digest is
`c0f90e1f28318642ddb43e5d5963203ca6ec1d9695c97a2280162f27db51e536`.

## Aggregate effect

The Apple overlay is 126,295 bytes with SHA-256
`5474d06c7141c0a518190089711452b2533cd0c62a907c679b8f38f5d06ea055`.
The Apollo component is 3,649,691 bytes with SHA-256
`f7c06b0652a7e7ddd3f974cf27ecabb9c3289b1c946520fc141bc90a5ecae9e8`.
The canonical package is 4,428,185 bytes with SHA-256
`f96c90d1f55b86130b827ab64e4e2eea6c976e972ef5f457ba624b7e23dceaec`.
It contains 1,058 placed, two preserved unresolved, and five container-only
regions. The flash plan is 759,478 bytes with SHA-256
`b5819e9b940a21c990f7af67f6be8a4fb64e6875eec9ef2d9221e4480f890053`.

Package ownership is 127,059 source-compiled bytes (2.869325%), 89,693
generated bytes (2.025503%), 216,752 controlled bytes (4.894827%), and
4,211,433 opaque compatibility bytes (95.105173%). The reviewed Linux Clang
22.1.8 replay remains pending; Apple pins are not copied into that profile.
