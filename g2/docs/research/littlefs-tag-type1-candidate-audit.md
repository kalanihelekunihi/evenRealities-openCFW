# littlefs `lfs_tag_type1` production source audit

Date: 2026-08-02

Scope: authenticate the private littlefs `lfs_tag_type1` leaf in both official
G2 firmware images, preserve a source adaptation, and register it atomically
in both production overlays with `lfs_tag_isvalid`.

Decision: **GO for deterministic offline source assembly in both Apollo
images; NO-GO for signing, flashing, reset, boot, filesystem mutation, or
hardware operation.**

The Apollo-main body at `[0x004CAE88,0x004CAE90)` and bootloader body at
`[0x00410B90,0x00410B98)` are byte-identical, call-free eight-byte Thumb
leaves. Each image has exactly eight decoded direct calls to its entry and no
observed alternate or interior ingress from any audited branch or
stored-pointer class. The production adaptation implements the exact scalar
behavior of the authenticated littlefs v2.10.1 definition and is registered
in both overlay registries, the canonical production manifest, and littlefs
provenance.

Firmware artifacts were assembled and checked offline. No artifact was signed,
flashed, booted, or exercised on G2 hardware for this audit.

## Authenticated upstream definition

| Property | Pin |
|---|---|
| Repository | `https://github.com/littlefs-project/littlefs.git` |
| Selected release | `v2.10.1` |
| Selected commit | `0494ce7169f06a734a7bd7585f49a9fa91fa7318` |
| License | BSD-3-Clause |
| `third_party/littlefs/lfs.c` | 196,753 bytes; SHA-256 `81a209e8551754d13b24fc0a2b6707fb3b2475e14feba00bf0df722b98a31398` |

The exact upstream definition is `lfs.c` bytes `[10232,10326)`, 94 bytes,
SHA-256
`ebf0229d6e0f78175c43641b09906fea19575fc3f34ac8862ae60159df1ec743`:

```c
static inline uint16_t lfs_tag_type1(lfs_tag_t tag) {
    return (tag & 0x70000000) >> 20;
}
```

The selected slice includes the two newlines after the closing brace. The
private type declaration is exactly `typedef uint32_t lfs_tag_t;`, `lfs.c`
bytes `[9602,9629)`, 27 bytes, SHA-256
`cb4dcd6212b1a269371d86dddf98ed74853e2eb43753c5d8f8659abbca167ce2`.
The recovered contract is therefore a pure unsigned 32-bit mask and shift
whose result is one of `0x000`, `0x100`, ..., `0x700` and fits exactly in
`uint16_t`.

The selected tree is an authenticated source-equivalent baseline; the
stripped images do not prove it was Even Realities' exact historical checkout.
`third_party/littlefs/PROVENANCE.json` retains that ambiguity. The local source
and header preserve the upstream copyright notices and BSD-3-Clause SPDX
identifier.

## Authoritative firmware inputs and stock bodies

| Input | Bytes | SHA-256 |
|---|---:|---|
| Official Apollo-main OTA `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Apollo-main installed payload after the 32-byte OTA preamble | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Official bootloader `blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin` | 148,599 | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` |

Apollo main loads at `0x00438000`. Its stock body begins at installed
payload offset `0x00092E88` and OTA file offset `0x00092EA8`. The bootloader
loads at `0x00410000`, placing its stock body at file offset `0x00000B90`.

| Image | Runtime span | Bytes | SHA-256 |
|---|---|---|---|
| Apollo main | `[0x004CAE88,0x004CAE90)` | `000d10f4e0607047` | `fc26e04a6784b91dc07f170f8a3bd23096f7caa92c15430a179edf215b509fdd` |
| Bootloader | `[0x00410B90,0x00410B98)` | `000d10f4e0607047` | `fc26e04a6784b91dc07f170f8a3bd23096f7caa92c15430a179edf215b509fdd` |

The Thumb body shifts `r0` right by 20 bits, masks the result with `0x700`,
and returns through `lr`. For unsigned 32-bit input this is algebraically
identical to upstream `(tag & 0x70000000) >> 20`. No decoded outgoing branch is
present in either body.

## Exact callers and complete-image ingress closure

The complete Apollo-main payload has exactly these direct `BL` entries:

| Call site | Encoding | Target |
|---:|---|---:|
| `0x004CAF32` | `fff7a9ff` | `0x004CAE88` |
| `0x004CAF64` | `fff790ff` | `0x004CAE88` |
| `0x004CB2F0` | `fff7cafd` | `0x004CAE88` |
| `0x004CB560` | `fff792fc` | `0x004CAE88` |
| `0x004CBC94` | `fff7f8f8` | `0x004CAE88` |
| `0x004CBCBA` | `fff7e5f8` | `0x004CAE88` |
| `0x004CBD12` | `fff7b9f8` | `0x004CAE88` |
| `0x004CCBA2` | `fef771f9` | `0x004CAE88` |

| Apollo-main evidence | SHA-256 |
|---|---|
| little-endian caller addresses | `f97e68b63d92a74c55f1eba09ecd3b109d1516555cc4666d4c03617c45f2e3ba` |
| concatenated encodings | `bb64df215a7ffa78053cf7f9172109bfc216753948ce7c9386a775e1507ac505` |
| address-plus-encoding records | `9c93a65bd664e28f8b4ed69a036955ccd3cafece93aed8078f639913f505033e` |

The complete bootloader has exactly these direct `BL` entries:

| Call site | Encoding | Target |
|---:|---|---:|
| `0x00410C3A` | `fff7a9ff` | `0x00410B90` |
| `0x00410C6C` | `fff790ff` | `0x00410B90` |
| `0x00410FF8` | `fff7cafd` | `0x00410B90` |
| `0x00411268` | `fff792fc` | `0x00410B90` |
| `0x0041199C` | `fff7f8f8` | `0x00410B90` |
| `0x004119C2` | `fff7e5f8` | `0x00410B90` |
| `0x00411A1A` | `fff7b9f8` | `0x00410B90` |
| `0x004127A6` | `fef7f3f9` | `0x00410B90` |

| Bootloader evidence | SHA-256 |
|---|---|
| little-endian caller addresses | `83c9e58936e433cb5491e391d3c44831d1d6f06fb1190b3111a326a74ba0ceaf` |
| concatenated encodings | `bdd585ae5c81bc94ec15fe578f41a1d0b4920868b5a9edd986c92c7e5c1c18de` |
| address-plus-encoding records | `29e1dbc1961092225a777207bce451b4f1e168256148830c21f21a6b9b89afb0` |

For both images, a halfword-aligned scan through the final complete halfword
found exactly the eight listed `BL` entries and found no `B.W`, wide
conditional, narrow unconditional, narrow conditional, `CBZ`, or `CBNZ`
entry into the body. It found no external branch to an interior halfword and
no byte-aligned stored even or Thumb address for any byte address in either
span. These checks close the decoded branch and stored-address classes used by
the focused gate; they are not a universal data-flow proof against an address
synthesized by an unrecognized multi-instruction sequence.

## Scalar ABI and source differential

The isolated callable contract is AAPCS32 Thumb, little-endian:

| Register | Meaning |
|---|---|
| `r0` on entry | one unsigned 32-bit `lfs_tag_t` value |
| `r0` on return | zero-extended unsigned 16-bit type value |

There are no pointer or stack arguments, structure layouts, providers, global
state, allocation, filesystem-object access, callback, or hardware dependency.
The production header exposes only a `uint32_t` scalar alias and a `uint16_t`
result, with compile-time width assertions.

The focused differential compiles the actual authenticated upstream definition
beside the production adaptation and compares both through those scalar types. It checks
eight directed edge and pattern values, exhausts all 65,536 combinations of
the complete upper 16-bit word with deterministic lower-word noise, and checks
20,000 seeded random 32-bit inputs. All 85,544 input comparisons match the
pristine definition; the exhaustive portion includes every combination of all
source-relevant type bits and the ignored validity bit.

## Deterministic Apple target object closure

Apple Clang `21.0.0 (clang-2100.3.27.1)` compiles the production adaptation twice for
`thumbv7em-none-eabi` at `-O2` with the focused freestanding and deterministic
flags. Both output objects are byte-identical:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| target ELF object | 788 | `42e5702fb7cb30ad327459f6b143207eef8442d645860e12fcc80100044e3a48` |
| `.text.open_cfw_littlefs_tag_type1` | 10 | `079f868da6ae04c0d4ace93e9e9d9132247224f81903b57fba51d407f49ddfcf` |

The complete isolated text is `4ff4e06101ea10507047`, aligned to four bytes.
It has zero undefined symbols and zero text relocations. The only other
allocated section is the canonical eight-byte
`.ARM.exidx.text.open_cfw_littlefs_tag_type1` record (flags `130`), which the
focused extractor authenticates and discards. This closes the generated
function's provider and relocation dependencies.

## Production artifacts and registration gate

| Production input | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/littlefs/runtime_littlefs_tag_type1.c` | 857 | `7c0df44bd2ebce1eae4cacbfa174c0f963dd03dcc5719ab386c0400201357b46` |
| `components/shared/littlefs/runtime_littlefs_tag_type1.h` | 893 | `0993093546ead7b159179c7aaebbef926be24b39ca5202d04b17f0569ca830f6` |
| `tests/test_runtime_littlefs_tag_type1.py` | 37,026 | `4feea6693ae1e9baf10fbf05b596c59b47fac5ce349a07aa47aaa8a4491d11dc` |

The focused test pins both source files, the pristine upstream bytes, official
image identities, both stock bodies, both caller sets, object bytes, extracted
text, relocation closure, patch bytes, placements, and final aggregate
artifacts. It requires the source path, header path, and symbol to be
registered exactly in:

- `components/apollo_main/core_overlay/overlay.json`;
- `components/bootloader/core_overlay/overlay.json`;
- `manifests/g2-2.2.6.10-core-source.json`; and
- `third_party/littlefs/PROVENANCE.json`.

Apollo main replaces all eight stock bytes with `B.W` plus two NOPs. Apple
patch bytes are `e7f29cbd00bf00bf`; Linux uses
`e8f22abd00bf00bf`. The source leaf is placed at offset 124,576 /
`0x007B29C4` for Apple and 126,396 / `0x007B30E0` for Linux, after two
alignment bytes. Bootloader patch bytes are `23f0afbd00bf00bf`, and its leaf
is at offset 634 / `0x004346F2` under both profiles.

This leaf was promoted atomically with `lfs_tag_isvalid`. The final aggregate
artifact pins are recorded in the companion validity audit and the two overlay
registries: Apple package 4,426,458 bytes /
`f0e7e4c5e090ea558968b6293f3eec0a7f88a6126ea164547c25c8462b60be23`;
exact-root Linux package 4,428,278 bytes /
`07cee183416db26bbe13673c1123e4ef19593d6343caa63c6c94791a210dc0dc`.
These are offline assembly pins, not a signing, flashing, or hardware approval.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_runtime_littlefs_tag_type1
git diff --check -- components/shared/littlefs/runtime_littlefs_tag_type1.c components/shared/littlefs/runtime_littlefs_tag_type1.h tests/test_runtime_littlefs_tag_type1.py docs/research/littlefs-tag-type1-candidate-audit.md
```

Expected focused result: five tests pass. All compiler products are created in
an operating-system temporary directory and removed by the test harness.
