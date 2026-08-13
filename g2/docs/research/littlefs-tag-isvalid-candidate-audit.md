# littlefs `lfs_tag_isvalid` production source audit

Date: 2026-08-02

Scope: authenticate the private littlefs `lfs_tag_isvalid` leaf in both
official G2 firmware images, preserve a source adaptation, and register it
atomically in both production overlays with `lfs_tag_type1`.

Decision: **GO for deterministic offline source assembly in both Apollo
images; NO-GO for signing, flashing, reset, boot, filesystem mutation, or
hardware operation.**

The Apollo-main body at `[0x004CAE6A,0x004CAE74)` and bootloader body at
`[0x00410B72,0x00410B7C)` are byte-identical, call-free ten-byte Thumb leaves.
Each image has exactly three decoded direct calls to its entry and no observed
alternate or interior ingress from any audited branch or stored-pointer class.
The production adaptation implements the exact boolean behavior of the
authenticated littlefs v2.10.1 definition and is registered in both overlay
registries, the canonical production manifest, and littlefs provenance.

Firmware artifacts were assembled and checked offline. No artifact was signed,
flashed, booted, or exercised on G2 hardware for this audit.

## Authenticated upstream definition and ABI

| Property | Pin |
|---|---|
| Repository | `https://github.com/littlefs-project/littlefs.git` |
| Selected release | `v2.10.1` |
| Selected commit | `0494ce7169f06a734a7bd7585f49a9fa91fa7318` |
| License | BSD-3-Clause |
| `third_party/littlefs/lfs.c` | 196,753 bytes; SHA-256 `81a209e8551754d13b24fc0a2b6707fb3b2475e14feba00bf0df722b98a31398` |

The exact upstream definition is `lfs.c` bytes `[10042,10129)`, 87 bytes,
SHA-256
`bb8e571d6dbddd1fe446ec7b4838979a4ab9bd6d6184e2f8d9b6c00cc0835b13`:

```c
static inline bool lfs_tag_isvalid(lfs_tag_t tag) {
    return !(tag & 0x80000000);
}
```

The selected slice includes the two newlines after the closing brace. The
private type declaration is exactly `typedef uint32_t lfs_tag_t;`, `lfs.c`
bytes `[9602,9629)`, 27 bytes, SHA-256
`cb4dcd6212b1a269371d86dddf98ed74853e2eb43753c5d8f8659abbca167ce2`.
The recovered contract is therefore a pure unsigned 32-bit validity-bit test:
tags with bit 31 clear return boolean true, while tags with bit 31 set return
boolean false.

The selected tree is an authenticated source-equivalent baseline; the
stripped images do not prove it was Even Realities' exact historical checkout.
`third_party/littlefs/PROVENANCE.json` retains that ambiguity. The local source
and header preserve the upstream copyright notices and BSD-3-Clause SPDX
identifier. The boundary uses C `bool`, `uint32_t`, and compile-time assertions
for the recovered four-byte tag and one-byte reviewed boolean type widths.

## Authoritative firmware inputs and stock bodies

| Input | Bytes | SHA-256 |
|---|---:|---|
| Official Apollo-main OTA `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Apollo-main installed payload after the 32-byte OTA preamble | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Official bootloader `blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin` | 148,599 | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` |

Apollo main loads at `0x00438000`. Its stock body begins at installed
payload offset `0x00092E6A` and OTA file offset `0x00092E8A`. The bootloader
loads at `0x00410000`, placing its stock body at file offset `0x00000B72`.

| Image | Runtime span | Bytes | SHA-256 |
|---|---|---|---|
| Apollo main | `[0x004CAE6A,0x004CAE74)` | `c00f90f00100c0b27047` | `0249b2c9c987097c7c0e628917a7dd6b67d4d1ee24f64339a7e0dd11977e4c9e` |
| Bootloader | `[0x00410B72,0x00410B7C)` | `c00f90f00100c0b27047` | `0249b2c9c987097c7c0e628917a7dd6b67d4d1ee24f64339a7e0dd11977e4c9e` |

The Thumb body shifts bit 31 into bit zero, inverts it, truncates the result to
the reviewed boolean width, and returns through `lr`. This is algebraically
identical to upstream `!(tag & 0x80000000)`. No decoded outgoing branch is
present in either body. The immediately preceding instruction in each image is
`pop {r4, pc}` (`10bd`), so sequential execution cannot fall through into the
stock entry.

## Exact callers and complete-image ingress closure

The complete Apollo-main payload has exactly these direct `BL` entries:

| Call site | Encoding | Target |
|---:|---|---:|
| `0x004CBB06` | `fff7b0f9` | `0x004CAE6A` |
| `0x004CBE92` | `fef7eaff` | `0x004CAE6A` |
| `0x004CF230` | `fbf71bfe` | `0x004CAE6A` |

| Apollo-main evidence | SHA-256 |
|---|---|
| little-endian caller addresses | `a8d1a349dc8381e29584323692b0c96df2c9b94bfbb477407aa6d22beb3e82ee` |
| concatenated encodings | `a11852b39f3aecf105c16a86767437920cb2d41a5d8685249d6b22d3f882a0ee` |
| address-plus-encoding records | `3218754d3f33ad2be3ddaf81bfc38ed4326a30b30a25ea62f3415fb1113a4491` |

The complete bootloader has exactly these direct `BL` entries:

| Call site | Encoding | Target |
|---:|---|---:|
| `0x0041180E` | `fff7b0f9` | `0x00410B72` |
| `0x00411B9A` | `fef7eaff` | `0x00410B72` |
| `0x00414908` | `fcf733f9` | `0x00410B72` |

| Bootloader evidence | SHA-256 |
|---|---|
| little-endian caller addresses | `0305b3c824b1748953137975ca3f81b345fbe15f66a7fd5883e85c937a71331c` |
| concatenated encodings | `e45c22e5d0653aeaaf0eccb8f9ddd5ac04aa3e547a34695e9402ed2beed09918` |
| address-plus-encoding records | `59ab470669e02502e855df6f10be748e2fbad41af14ccb9745506437938a3751` |

For both images, a halfword-aligned scan through the final complete halfword
found exactly the three listed `BL` entries and found no `B.W`, wide
conditional, narrow unconditional, narrow conditional, `CBZ`, or `CBNZ`
entry into the body. It found no external branch to an interior halfword and
no byte-aligned stored even or Thumb address for any byte address in either
span. Together with the terminating predecessor, these checks close the
decoded branch, sequential, and stored-address ingress classes used by the
focused gate. They are not a universal data-flow proof against an address
synthesized by an unrecognized multi-instruction sequence.

## Scalar ABI and source differential

The isolated callable contract is AAPCS32 Thumb, little-endian:

| Register | Meaning |
|---|---|
| `r0` on entry | one unsigned 32-bit `lfs_tag_t` value |
| `r0` on return | canonical boolean zero or one |

There are no pointer or stack arguments, structures, providers, global state,
allocation, filesystem-object access, callbacks, or hardware dependencies.

The focused differential compiles the actual authenticated upstream definition
beside the production adaptation and compares both through the recovered scalar and bool
types. It checks eight directed edge and pattern values, exhausts all 65,536
combinations of the complete upper 16-bit word with deterministic lower-word
noise, and checks 20,000 seeded random 32-bit inputs. All 85,544 comparisons
match the pristine definition. The exhaustive portion covers both validity-bit
classes and every combination of the ignored upper tag bits.

## Deterministic Apple target object closure

Apple Clang `21.0.0 (clang-2100.3.27.1)` compiles the production adaptation twice for
`thumbv7em-none-eabi` at `-O2` with the focused freestanding and deterministic
flags. Both output objects are byte-identical:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| target ELF object | 788 | `e3871538017e418dada7c63f5d4395c7911e691256971de34883fdb43952400a` |
| `.text.open_cfw_littlefs_tag_isvalid` | 6 | `65e477818b1c6002b2ceb88812da258524e438ded36dfa059e034c3bce19624e` |

The complete isolated text is `c043c00f7047`, aligned to four bytes. It has
zero undefined symbols and zero text relocations. The only other allocated
section is the canonical eight-byte
`.ARM.exidx.text.open_cfw_littlefs_tag_isvalid` record (flags `130`), which the
focused extractor authenticates and discards. This closes the generated
function's provider and relocation dependencies.

## Production artifacts and registration gate

| Production input | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/littlefs/runtime_littlefs_tag_isvalid.c` | 848 | `a91417d6193cdfb9589cd9e62f9b6eebe65e1e11a75ca36d0f42d85c36d907a2` |
| `components/shared/littlefs/runtime_littlefs_tag_isvalid.h` | 928 | `6efcd1b229fb0477285f8fbdfbc6f1c92701a787fb17995a6115bfa5a944c6cd` |
| `tests/test_runtime_littlefs_tag_isvalid.py` | 36,927 | `ef744ebd4526be581a9035725e0e48b8b9c8d6f23882a3a6891ab28951d6bf06` |

The focused test pins both source files, the pristine upstream bytes, official
image identities, both stock bodies, both caller sets, predecessor return,
object bytes, extracted text, relocation closure, patch bytes, placements,
and final aggregate artifacts. It requires the source path, header path, and
symbol to be registered exactly in:

- `components/apollo_main/core_overlay/overlay.json`;
- `components/bootloader/core_overlay/overlay.json`;
- `manifests/g2-2.2.6.10-core-source.json`; and
- `third_party/littlefs/PROVENANCE.json`.

Apollo main replaces all ten stock bytes with `B.W` plus three NOPs. Apple
patch bytes are `e7f2a7bd00bf00bf00bf`; Linux uses
`e8f235b900bf00bf00bf`. The source leaf is placed at offset 124,568 /
`0x007B29BC` for Apple and 126,388 / `0x007B30D8` for Linux, after two
alignment bytes. Bootloader patch bytes are `23f0bbbd00bf00bf00bf`, and its
leaf is at offset 628 / `0x004346EC` under both profiles.

This leaf was promoted atomically with `lfs_tag_type1`. The resulting Apple
main overlay/component are 124,586 / 3,647,982 bytes with SHA-256
`043dbfb45fcfb9707616c486ac2e736227f7186af8b25fc71a5e355a8e0ba79a`
and `1227c4953bfcaeb62fb497b8a6911462a2d25fd3ed7b2bb88eea9dd3fdf13a18`;
boot is 644 / 149,244 bytes with SHA-256
`959923a9b5253bd6409fedb82427b7ff666e2d52bc09ac5c391bc28bfbcc70c2`
and `e8924fe19f6f768d01fa7c6ec111a4db5790eb28c423c5be84e09b0996423e20`.
The 4,426,458-byte package hashes to
`f0e7e4c5e090ea558968b6293f3eec0a7f88a6126ea164547c25c8462b60be23`.

Exact-root Linux main is 126,406 / 3,649,802 bytes with SHA-256
`7196c0d0d456b46e125b793d7ab4c6175768067589f4153d9b3ee997011c0314`
and `a8684ae43a99cc692dd6cb95c8d4835cc138492d49bf9fd4a3689d32523913ef`;
boot is 644 / 149,244 bytes with SHA-256
`078b88569f6adb147d3c12c727f29c5f3a6ddeb2f66de7d68122b4096f6ac794`
and `6fff06068442ab3203d124c0adfd5052f216459642f67aa32cc39afffd2c0593`.
The 4,428,278-byte package hashes to
`07cee183416db26bbe13673c1123e4ef19593d6343caa63c6c94791a210dc0dc`.
These are offline assembly pins, not a signing, flashing, or hardware approval.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_runtime_littlefs_tag_isvalid
git diff --check -- components/shared/littlefs/runtime_littlefs_tag_isvalid.c components/shared/littlefs/runtime_littlefs_tag_isvalid.h tests/test_runtime_littlefs_tag_isvalid.py docs/research/littlefs-tag-isvalid-candidate-audit.md
```

Expected focused result: five tests pass. All compiler products are created in
an operating-system temporary directory and removed by the test harness.
