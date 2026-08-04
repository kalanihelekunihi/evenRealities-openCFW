# littlefs `lfs_tag_size` dual-image source-promotion audit

Date: 2026-08-02

Scope: authenticate the private littlefs `lfs_tag_size` leaf in both official
G2 firmware images, qualify its bounded source adaptation, and record its
atomic production integration in Apollo main and the bootloader.

Decision: **GO for both reviewed production overlays and deterministic offline
firmware assembly; NO-GO for signing, flashing, reset, boot, filesystem
mutation, or hardware operation.**

The Apollo-main body at `[0x004CAEB8,0x004CAEBE)` and bootloader body at
`[0x00410BC0,0x00410BC6)` are byte-identical, call-free six-byte Thumb
leaves. The complete images contain exactly 15 and 14 decoded direct calls,
respectively, and no observed alternate or interior ingress from any audited
branch or stored-pointer class. The production leaf implements the exact
scalar behavior of the authenticated littlefs v2.10.1 definition and is
registered in both overlay configs, the canonical manifest, and littlefs
provenance as one atomic dual-image promotion.

Both Apple and exact-root Linux artifacts are assembled and verified offline
as part of the encompassing production tranche. No firmware is signed,
flashed, booted, or exercised on G2 hardware.

## Authenticated upstream definition

| Property | Pin |
|---|---|
| Repository | `https://github.com/littlefs-project/littlefs.git` |
| Selected release | `v2.10.1` |
| Selected commit | `0494ce7169f06a734a7bd7585f49a9fa91fa7318` |
| License | BSD-3-Clause |
| `third_party/littlefs/lfs.c` | 196,753 bytes; SHA-256 `81a209e8551754d13b24fc0a2b6707fb3b2475e14feba00bf0df722b98a31398` |
| `third_party/littlefs/lfs.h` | 26,439 bytes; SHA-256 `ee44e99d6b19119b3e577b969b80c9d5e6f96410c9593794afddf6d4b314c486` |

The exact upstream definition is `lfs.c` bytes `[10793,10880)`, 87 bytes,
SHA-256
`9df85bc43ca9f90ef58c425c5fd9bbbbf53585093be5fad0cc580fc88814ea5c`:

```c
static inline lfs_size_t lfs_tag_size(lfs_tag_t tag) {
    return tag & 0x000003ff;
}
```

The selected slice includes the two newlines after the closing brace. The
private type declaration is exactly `typedef uint32_t lfs_tag_t;`, `lfs.c`
bytes `[9602,9629)`, 27 bytes, SHA-256
`cb4dcd6212b1a269371d86dddf98ed74853e2eb43753c5d8f8659abbca167ce2`.
The return declaration is exactly `typedef uint32_t lfs_size_t;`, `lfs.h`
bytes `[974,1002)`, 28 bytes, SHA-256
`e61a4bdad54f4bb8a78f53764fd1043376bd4d922f34d2dd554beab89cd0561f`.
The contract is therefore a pure unsigned 32-bit mask returning the low ten
size bits as a zero-extended value from zero through `0x3ff`.

The selected tree is an authenticated source-equivalent baseline. The
stripped images do not prove it was Even Realities' exact historical checkout,
and `third_party/littlefs/PROVENANCE.json` retains that ambiguity. Function
identity is independently corroborated by its byte-identical position between
the `lfs_tag_id` and `lfs_tag_dsize` helpers in both images and by the
official body's exact mask semantics. The production source and
header retain the upstream copyright notices and BSD-3-Clause SPDX identifier.

## Authoritative firmware inputs and stock bodies

| Input | Bytes | SHA-256 |
|---|---:|---|
| Official Apollo-main OTA `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Apollo-main installed payload after the 32-byte OTA preamble | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Official bootloader `blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin` | 148,599 | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` |

Apollo main loads at `0x00438000`. Its stock helper begins at installed-payload
offset `0x00092EB8` and OTA file offset `0x00092ED8`. The bootloader loads at
`0x00410000`, placing its stock helper at file offset `0x00000BC0`.

| Image | Runtime span | Bytes | SHA-256 |
|---|---|---|---|
| Apollo main | `[0x004CAEB8,0x004CAEBE)` | `8005800d7047` | `8596106584e598a657aea7fdd2e1156a748158d2d63d9c121c92587fabbdf8ca` |
| Bootloader | `[0x00410BC0,0x00410BC6)` | `8005800d7047` | `8596106584e598a657aea7fdd2e1156a748158d2d63d9c121c92587fabbdf8ca` |

The official Thumb body shifts the tag left by 22 and then logically right by
22 before returning through `lr`. This is algebraically identical to upstream
`tag & 0x000003ff`. Neither body contains a decoded outgoing call or branch.

The predecessor in each image is the independent `lfs_tag_id` leaf and
ends with `bx lr` (`7047`). The helper also ends with `bx lr`, and the
successor begins `lfs_tag_dsize` with `push {r4,lr}` (`10b5`). Sequential execution
therefore cannot fall into or out of the selected body, and no shared tail or
literal pool is owned by it.

## Exact callers and complete-image ingress closure

The complete Apollo-main payload has exactly these direct `BL` entries:

```text
0x004CAECC fff7f4ff    0x004CAF10 fff7d2ff
0x004CAF26 fff7c7ff    0x004CAF48 fff7b6ff
0x004CB368 fff7a6fd    0x004CB3D4 fff770fd
0x004CB77E fff79bfb    0x004CB7DA fff76dfb
0x004CBFD4 fef770ff    0x004CBFFA fef75dff
0x004CC026 fef747ff    0x004CC032 fef741ff
0x004CDC5C fdf72cf9    0x004CF578 fbf79efc
0x004CF59E fbf78bfc
```

| Apollo-main evidence | SHA-256 |
|---|---|
| little-endian caller addresses | `e23410e3b34d0ccc5f7d7e90b1a02d2544b6cf8421bf0fb96f90468917a92901` |
| concatenated encodings | `107e3c7e125825108b2f90ed90762b9ad9010bf1873fb06300087e3379884dcd` |
| address-plus-encoding records | `320fa8bc85f88a2dc10bd929a751cc9a0f9a82161a3fdb3102ef6e674beb72b9` |

The complete bootloader has exactly these direct `BL` entries:

```text
0x00410BD4 fff7f4ff    0x00410C18 fff7d2ff
0x00410C2E fff7c7ff    0x00410C50 fff7b6ff
0x00411070 fff7a6fd    0x004110DC fff770fd
0x00411486 fff79bfb    0x004114E2 fff76dfb
0x00411C5A fef7b1ff    0x00411C86 fef79bff
0x00411C92 fef795ff    0x004137AC fdf708fa
0x00414C48 fbf7baff    0x00414C6E fbf7a7ff
```

| Bootloader evidence | SHA-256 |
|---|---|
| little-endian caller addresses | `404e52ad9b8da4197b6fcd0aae1982284e47f1c4a70437df6ea432cc9fafd275` |
| concatenated encodings | `5b072bdf79d01c7c43b3c3c6e8fec8d71d2166b1972c5aa397d3089c68b61db2` |
| address-plus-encoding records | `3cedd904ff7bce58fe38992ad70830407b6389a1cc20c9ca54f28c5802f5e401` |

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
| `r0` on return | unsigned 32-bit `lfs_size_t` value in `[0,0x3ff]` |

There are no pointer or stack arguments, structures, providers, global state,
allocation, filesystem-object access, callbacks, configuration conditionals,
or hardware dependencies. The production header exposes only a `uint32_t`
tag alias and `uint32_t` result alias, with compile-time width assertions.

The focused differential compiles the actual authenticated upstream
definition beside the production adaptation. It checks nine directed edge and pattern
values, exhausts all 65,536 combinations of the complete lower 16-bit word
with deterministic upper-word noise, and checks 20,000 seeded random 32-bit
inputs. All 85,545 comparisons match the pristine definition. The exhaustive
portion covers every combination of all ten source-relevant size bits and six
ignored low-word bits while varying every ignored upper bit deterministically.

## Deterministic Apple target-object closure

Apple Clang `21.0.0 (clang-2100.3.27.1)` compiles the actual adaptation twice
under both reviewed production-shaped profiles:

| Profile | Target and optimization | Object bytes / SHA-256 | Text alignment |
|---|---|---|---:|
| Apollo main | `thumbv7em-none-eabi`, `-mthumb -O2` | 780 / `a8325647f526cf10d9e5d82df49358fdc1d4b1f6b2f9ba2a6c15fc085f7f29b7` | 4 |
| Bootloader | `arm-none-eabi`, `-mcpu=cortex-m55 -mthumb -Oz` | 780 / `37511de65a26da5a2d3bf7356f850135502a14b3426c7da6c1ea3f84d59cb9bf` | 2 |

Both profiles produce the same complete isolated text:

```text
6ff39f207047
```

The six bytes hash to
`35890ebcdee5cb7f51b3e8d874201b7e0214f6111eebe56c772133f259cf9b54`.
Each object has zero undefined symbols and zero text relocations. Its only
other allocated section is the canonical eight-byte
`.ARM.exidx.text.open_cfw_littlefs_tag_size` record with flags `130`, which
the focused extractor authenticates and discards. This closes the generated
leaf's provider and relocation dependencies in both production images.

Homebrew Clang 22.1.8 independently emits the same two deterministic objects
and the same six-byte text under the reviewed main and boot target profiles.
The leaf pin is therefore cross-toolchain identical even though the
surrounding Apollo-main overlays remain profile-specific.

## Production inputs and registration gate

| Production input | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/littlefs/runtime_littlefs_tag_size.c` | 854 | `533bbfcbfc2440e02b79692a2a7ccff87c3cb62cbb0788c1d5bf806fd3bca849` |
| `components/shared/littlefs/runtime_littlefs_tag_size.h` | 1,000 | `0f29febdc25b081de1821a41c9065870c02154375985bf648d8e1b63f6cc3528` |
| `tests/test_runtime_littlefs_tag_size.py` | 36,735 | `c1e41d56be9294376cdff7eb6ff5fd6bdc179860b6beafbb43d026c22ae676c4` |

The focused test pins both source files, the pristine upstream bytes, official
image identities, both stock bodies, both complete caller sets, predecessor
and successor boundaries, Apple main and boot object bytes, extracted text,
and relocation closure. The completed production gate additionally pins both
profile placements, complete entry redirects, aggregate artifact hashes,
manifest topology and continuity, and provenance ownership.

## Production placements and complete entry redirects

| Image/profile | Source-leaf offset / runtime span | Complete stock patch |
|---|---|---|
| Apollo main, Apple | 124,604 / `[0x007B29E0,0x007B29E6)` after two alignment bytes | `e7f292bd00bf` |
| Apollo main, exact-root Linux | 126,424 / `[0x007B30FC,0x007B3102)` after two alignment bytes | `e8f220b900bf` |
| Bootloader, both | 656 / `[0x00434708,0x0043470E)` | `23f0a2bd00bf` |

Each non-linking `B.W` plus one Thumb NOP owns the complete six-byte stock
span. Apple main alignment occupies `[0x007B29DE,0x007B29E0)`; Linux uses
`[0x007B30FA,0x007B30FC)`. The boot leaf follows the production tag-ID leaf
directly and needs no new alignment.

## Aggregate offline artifacts

| Profile | Apollo-main overlay/component | Boot overlay/component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 124,610 / `3748b98f262a2db4cc38c2b0ce63ed83ee01cd945384a31fc7e132d99db79b7a`; 3,648,006 / `4a518e8fa6eaad8113d3ac14070ce6fdc3f2ddbf318b651bfa13423d9a0caa2a` | 662 / `7cb3c17a03dda3b8576d8288ffa61df1332d89f1f24d6c5877bf0143e233902b`; 149,262 / `695688b7cc4d9583e9e5c854db44980acab9a58d367bc7e02fa5e51eb00e3267` | 4,426,500 / `bed7320b89d6497cc261ee948716004821e3a1c3eb92018271c27a1e4c89432f` |
| exact-root Linux Clang 22.1.8 | 126,430 / `8e252b96fd244107603046a4a0eb3ef17fe261e026bb52d793ccbbb764a5df56`; 3,649,826 / `a34fb1906c0b20702b7636866479b7680776aeda3cad7fb36a544bea78ffc6b8` | 662 / `e4c743531f56c190b7e3129768d410480a2f3433a5b680c7bf432ef0b05a7021`; 149,262 / `fc3d07c8a59e1c33f26965cdb1888114412c3ca671d6137f7c3166acc81c8d74` | 4,428,320 / `70ec26aaf4ddb42ae04938edb4a54f3875c6d33a856e477cdf7acc461ebcff0d` |

These deterministic aggregate hashes come from the encompassing Apple and
exact-root Linux integration builds. Offline assembly is GO only under those
reviewed profiles; the artifact pins are not a hardware-validation claim.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_runtime_littlefs_tag_size
PYTHONPYCACHEPREFIX=/tmp/open-cfw-pycache python3 -m py_compile tests/test_runtime_littlefs_tag_size.py
git diff --check -- components/shared/littlefs/runtime_littlefs_tag_size.c components/shared/littlefs/runtime_littlefs_tag_size.h tests/test_runtime_littlefs_tag_size.py docs/research/littlefs-tag-size-candidate-audit.md
```

## Subsequent aggregate successor

The tag-size leaf and its dual-image placements remain unchanged. The later
Apollo-main-only nanopb fixed64 promotion advances aggregate package pins to
4,426,530 /
`a3d06dd732722859a7cd4da1582cea49464cbbfccdb90e329afa6ec9352195d4`
for Apple and 4,428,352 /
`75af4c1facb8c663cff2a8d4469625261ffa04d9c9587dc0db9ecf2c2f401b6d`
for exact-root Linux. Final manifest counts are `938 main / 67 boot`; the
bootloader tag-size component remains byte-identical to the pins above. This
note prevents the phase-local tag-size aggregate table from being mistaken
for the current whole-package identity.

Observed focused result: five of five tests pass. All compiler products are
created inside an operating-system temporary directory and removed by the
harness.
