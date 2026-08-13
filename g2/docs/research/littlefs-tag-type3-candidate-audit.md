# littlefs `lfs_tag_type3` dual-image source-promotion audit

Date: 2026-08-02

Scope: authenticate the private littlefs `lfs_tag_type3` leaf in both official
G2 firmware images, qualify its bounded source adaptation, and record its
atomic production integration in Apollo main and the bootloader.

Decision: **GO for both reviewed production overlays and deterministic offline
firmware assembly; NO-GO for signing, flashing, reset, boot, filesystem
mutation, or hardware operation.**

The Apollo-main body at `[0x004CAE98,0x004CAEA0)` and bootloader body at
`[0x00410BA0,0x00410BA8)` are byte-identical, call-free eight-byte Thumb
leaves. The complete images contain exactly 30 and 17 decoded direct calls,
respectively, and no observed alternate or interior ingress from any audited
branch or stored-pointer class. The production leaf implements the exact
scalar behavior of the authenticated littlefs v2.10.1 definition and is now
registered in both overlay configs, the canonical manifest, and littlefs
provenance as one atomic dual-image promotion.

Both Apple and exact-root Linux artifacts were assembled and verified offline.
No firmware was signed, flashed, booted, or exercised on G2 hardware.

## Authenticated upstream definition

| Property | Pin |
|---|---|
| Repository | `https://github.com/littlefs-project/littlefs.git` |
| Selected release | `v2.10.1` |
| Selected commit | `0494ce7169f06a734a7bd7585f49a9fa91fa7318` |
| License | BSD-3-Clause |
| `third_party/littlefs/lfs.c` | 196,753 bytes; SHA-256 `81a209e8551754d13b24fc0a2b6707fb3b2475e14feba00bf0df722b98a31398` |

The exact upstream definition is `lfs.c` bytes `[10420,10514)`, 94 bytes,
SHA-256
`3cc2c9ec46ebb7fc3d3d71c6b39b235a5da0cde23adf2c182cafd24d6410b53e`:

```c
static inline uint16_t lfs_tag_type3(lfs_tag_t tag) {
    return (tag & 0x7ff00000) >> 20;
}
```

The selected slice includes the two newlines after the closing brace. The
private type declaration is exactly `typedef uint32_t lfs_tag_t;`, `lfs.c`
bytes `[9602,9629)`, 27 bytes, SHA-256
`cb4dcd6212b1a269371d86dddf98ed74853e2eb43753c5d8f8659abbca167ce2`.
The contract is therefore a pure unsigned 32-bit mask and shift returning all
eleven type bits as a value from zero through `0x7ff`, which fits exactly in
`uint16_t`.

The selected tree is an authenticated source-equivalent baseline. The
stripped images do not prove it was Even Realities' exact historical checkout,
and `third_party/littlefs/PROVENANCE.json` retains that ambiguity. Function
identity is independently corroborated by its byte-identical position between
the already identified `lfs_tag_type2` and `lfs_tag_chunk` helpers and by the
official body's exact mask-and-shift semantics. The production source and
header retain the upstream copyright notices and BSD-3-Clause SPDX identifier.

## Authoritative firmware inputs and stock bodies

| Input | Bytes | SHA-256 |
|---|---:|---|
| Official Apollo-main OTA `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Apollo-main installed payload after the 32-byte OTA preamble | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Official bootloader `blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin` | 148,599 | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` |

Apollo main loads at `0x00438000`. Its stock helper begins at installed-payload
offset `0x00092E98` and OTA file offset `0x00092EB8`. The bootloader loads at
`0x00410000`, placing its stock helper at file offset `0x00000BA0`.

| Image | Runtime span | Bytes | SHA-256 |
|---|---|---|---|
| Apollo main | `[0x004CAE98,0x004CAEA0)` | `000d4005400d7047` | `818012c47ba81ee18e2996d51a8a29a96a78ced50854b6fefcebf92e7b9ed9d6` |
| Bootloader | `[0x00410BA0,0x00410BA8)` | `000d4005400d7047` | `818012c47ba81ee18e2996d51a8a29a96a78ced50854b6fefcebf92e7b9ed9d6` |

The official Thumb body shifts the tag right by 20, clears every bit above
bit ten, and returns through `lr`. This is algebraically identical to upstream
`(tag & 0x7ff00000) >> 20`. Neither body contains a decoded outgoing call or
branch.

The predecessor in each image is the independent `lfs_tag_type2` leaf and
ends with `bx lr` (`7047`). The helper also ends with `bx lr`, and the
successor begins the independent `lfs_tag_chunk` leaf. Sequential execution
therefore cannot fall into or out of the selected body, and no shared tail or
literal pool is owned by it.

## Exact callers and complete-image ingress closure

The complete Apollo-main payload has exactly these direct `BL` entries:

```text
0x004CB70A fff7c5fb    0x004CB716 fff7bffb
0x004CB7C0 fff76afb    0x004CBD5E fff79bf8
0x004CBF82 fef789ff    0x004CBFB2 fef771ff
0x004CBFC6 fef767ff    0x004CC07E fef70bff
0x004CC12E fef7b3fe    0x004CCBDC fef75cf9
0x004CCC18 fef73ef9    0x004CCE72 fef711f8
0x004CCEB2 fdf7f1ff    0x004CCEF8 fdf7ceff
0x004CD57A fdf78dfc    0x004CDB46 fdf7a7f9
0x004CDC4C fdf724f9    0x004CE4B6 fcf7effc
0x004CE520 fcf7bafc    0x004CE5C8 fcf766fc
0x004CE6C6 fcf7e7fb    0x004CE702 fcf7c9fb
0x004CE70A fcf7c5fb    0x004CE718 fcf7befb
0x004CE746 fcf7a7fb    0x004CE802 fcf749fb
0x004CE8CA fcf7e5fa    0x004CF346 fbf7a7fd
0x004CF376 fbf78ffd    0x004CF726 fbf7b7fb
```

| Apollo-main evidence | SHA-256 |
|---|---|
| little-endian caller addresses | `0118197b8b33207bd4188384b00ebe8f400a19780ae2cb6fc0e71fe739a31d66` |
| concatenated encodings | `039114068b0da49cd7ca9239b368c44b0ab5d349eae96288450f15cc9cfa16b4` |
| address-plus-encoding records | `0017668c7690b4edba82415b7023fcbae82ea720454a214375425b088298d88a` |

The complete bootloader has exactly these direct `BL` entries:

```text
0x00411412 fff7c5fb    0x0041141E fff7bffb
0x004114C8 fff76afb    0x00411A66 fff79bf8
0x00411CDE fef75fff    0x00411D8E fef707ff
0x004127E0 fef7def9    0x0041281C fef7c0f9
0x00412A76 fef793f8    0x00412AB6 fef773f8
0x00412AFC fef750f8    0x0041317E fdf70ffd
0x00413696 fdf783fa    0x0041379C fdf700fa
0x00414A16 fcf7c3f8    0x00414A46 fcf7abf8
0x00414DF6 fbf7d3fe
```

| Bootloader evidence | SHA-256 |
|---|---|
| little-endian caller addresses | `24880dfe7ab1b30670330e5eaffda21683118091f906c7ef36403b102989029f` |
| concatenated encodings | `67aea6e13012127639aa8163680a3f4fc7a319a81f0b11cd643268f520b7fbe0` |
| address-plus-encoding records | `6ca71e2e3014534a257564169eef0afdb50e554b2fc2be6bc6401270b55a5616` |

For both images, a halfword-aligned scan through the final complete halfword
found exactly the listed `BL` entries. It found no `B.W`, wide conditional,
narrow unconditional, narrow conditional, `CBZ`, or `CBNZ` entry into the
body; no external target enters an interior halfword. A byte-aligned scan
found no stored even or Thumb address for any entry or interior byte address.
Together with the terminating predecessor, these checks close the decoded
branch, sequential, and stored-address ingress classes used by the focused
gate. They are not a universal data-flow proof against an address synthesized
by an unrecognized multi-instruction sequence.

## Scalar ABI and source differential

The isolated callable contract is AAPCS32 Thumb, little-endian:

| Register | Meaning |
|---|---|
| `r0` on entry | one unsigned 32-bit `lfs_tag_t` value |
| `r0` on return | zero-extended unsigned 16-bit type value |

There are no pointer or stack arguments, structures, providers, global state,
allocation, filesystem-object access, callbacks, configuration conditionals,
or hardware dependencies. The production header exposes only a `uint32_t`
scalar alias and `uint16_t` result, with compile-time width assertions.

The focused differential compiles the actual authenticated upstream
definition beside the production adaptation. It checks eight directed edge and pattern
values, exhausts all 65,536 combinations of the complete upper 16-bit word
with deterministic lower-word noise, and checks 20,000 seeded random 32-bit
inputs. All 85,544 comparisons match the pristine definition. The exhaustive
portion covers every combination of all eleven source-relevant type bits and
the ignored validity bit.

## Deterministic Apple target-object closure

Apple Clang `21.0.0 (clang-2100.3.27.1)` compiles the actual adaptation twice
under both reviewed production-shaped profiles:

| Profile | Target and optimization | Object bytes / SHA-256 | Text alignment |
|---|---|---|---:|
| Apollo main | `thumbv7em-none-eabi`, `-mthumb -O2` | 784 / `e314943356d7da90680a50e249b082c83a4ca105f2a6e4bc2173495f9be52a31` | 4 |
| Bootloader | `arm-none-eabi`, `-mcpu=cortex-m55 -mthumb -Oz` | 784 / `745001dad9d930eb56e1ac3799ddf71c29506e4662703ccbc7daa2a7a14f55f9` | 2 |

Both profiles produce the same complete isolated text:

```text
c0f30a507047
```

The six bytes hash to
`a6781f0a92086cca25476ca00824d8f0fd736ac7d800aa9e3f6e4d6544490921`.
Each object has zero undefined symbols and zero text relocations. Its only
other allocated section is the canonical eight-byte
`.ARM.exidx.text.open_cfw_littlefs_tag_type3` record with flags `130`, which
the focused extractor authenticates and discards. This closes the generated
leaf's provider and relocation dependencies in both production images.

Homebrew Clang 22.1.8 emits the same six-byte text under both reviewed target
profiles, so the leaf pin is cross-toolchain identical even though the
surrounding Apollo-main overlays remain profile-specific.

## Production inputs and registration gate

| Production input | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/littlefs/runtime_littlefs_tag_type3.c` | 857 | `6940b4ac0622dc1f2b84a0c663dc1522dfc7b198f59d6f452828adfd299e37c8` |
| `components/shared/littlefs/runtime_littlefs_tag_type3.h` | 893 | `4e3b70d5ad8e8fce0e5dc2bd43fc8459c62c742d84a93f949bf0dd4fb44fe869` |
| `tests/test_runtime_littlefs_tag_type3.py` | 33,340 | `d292e7712aaa5f0521418ca696836cea58b3b4d73d606bb0d3733e832bf18d5e` |

The focused test pins both source files, pristine upstream bytes, official
image identities, both stock bodies and complete caller sets, predecessor and
successor boundaries, Apple and Linux placements, complete entry redirects,
aggregate overlays/components/packages, manifest topology, provenance
ownership, and rollback behavior. It requires the source/header/symbol to be
present in both overlay configs, the canonical manifest, and
`third_party/littlefs/PROVENANCE.json`.

## Production placements and complete entry redirects

| Image/profile | Source-leaf offset / runtime span | Complete stock patch |
|---|---|---|
| Apollo main, Apple | 124,588 / `[0x007B29D0,0x007B29D6)` after two alignment bytes | `e7f29abd00bf00bf` |
| Apollo main, exact-root Linux | 126,408 / `[0x007B30EC,0x007B30F2)` after two alignment bytes | `e8f228b900bf00bf` |
| Bootloader, both | 644 / `[0x004346FC,0x00434702)` | `23f0acbd00bf00bf` |

Each non-linking `B.W` plus NOP fill owns the complete eight-byte stock span.
The Apple main alignment occupies `[0x007B29CE,0x007B29D0)`; Linux uses
`[0x007B30EA,0x007B30EC)`. The bootloader leaf follows `lfs_tag_type1`
directly and needs no new alignment.

## Aggregate offline artifacts

| Profile | Apollo-main overlay/component | Boot overlay/component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 124,594 / `2648682a1bf736c6bce9610f38c43a0b127d46fa9f0fbec9c21bc5775c1a99a0`; 3,647,990 / `2468a250bbd2ed67e0baf8cfb3abe84269743f04003fe100d676af0f526d1de0` | 650 / `efc0bc7a5fa7351a9aa372bec40d1a88fde0284b251486db11a9877947da6d50`; 149,250 / `826358deb7400e8c25b744487979c0c7f32b7e1db63588b5a244c3375e885a62` | 4,426,472 / `96f5309c2f77834a2c034b00d04618f0fa42ea3019924d5d51047f7a54c3db4d` |
| exact-root Linux Clang 22.1.8 | 126,414 / `df3b885d5a5c952144fd50324f556e1fdf9435728bb2db8aa015183eb0f4cd4f`; 3,649,810 / `478877ed8ac940d208216d4950a423f70728571fa9f18795c1ee01d521ee858c` | 650 / `968dbeac7adef3acc5151cd15189bba3528de295147ecca60832f1cf87b425e3`; 149,250 / `bb3d7eef87a59529f67de9996324a91575d6e1218471a5330b153eb28950742a` | 4,428,292 / `e56f78421dd83283e3d4e3f4a6b61a3400260c2618719cc6051453dd9e249bc1` |

The Apple flash plan is 714,877 bytes with SHA-256
`ca572a550a016d968e28eeb6c48d131481542a6f3478d668e13e32dd365217de`.
It records 995 placed, two unresolved, and five container-only records. The
exact-root Linux plan records 833 placed, two unresolved, and five
container-only records. Offline assembly is GO under both reviewed profiles;
these artifact pins are not a hardware-validation claim.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_runtime_littlefs_tag_type3
git diff --check -- components/shared/littlefs/runtime_littlefs_tag_type3.c components/shared/littlefs/runtime_littlefs_tag_type3.h tests/test_runtime_littlefs_tag_type3.py docs/research/littlefs-tag-type3-candidate-audit.md
```

Observed focused result: five of five tests pass. All compiler products are
created inside an operating-system temporary directory and removed by the
harness.
The test and build gates are offline only: signing, flashing, mount, format,
erase, reset, boot, and all G2 hardware operation remain NO-GO.
