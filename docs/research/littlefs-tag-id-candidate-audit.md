# littlefs `lfs_tag_id` dual-image source-promotion audit

Date: 2026-08-02

Scope: authenticate the private littlefs `lfs_tag_id` leaf in both official
G2 firmware images, qualify its bounded source adaptation, and record its
atomic production integration in Apollo main and the bootloader.

Decision: **GO for both reviewed production overlays and deterministic offline
firmware assembly; NO-GO for signing, flashing, reset, boot, filesystem
mutation, or hardware operation.**

The Apollo-main body at `[0x004CAEB0,0x004CAEB8)` and bootloader body at
`[0x00410BB8,0x00410BC0)` are byte-identical, call-free eight-byte Thumb
leaves. The complete images contain exactly 50 and 41 decoded direct calls,
respectively, and no observed alternate or interior ingress from any audited
branch or stored-pointer class. The production leaf implements the exact
scalar behavior of the authenticated littlefs v2.10.1 definition and is now
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

The exact upstream definition is `lfs.c` bytes `[10702,10793)`, 91 bytes,
SHA-256
`50140c563689852013dfad180ec3b6464c6b6c5b22854f5492d63cf5de57fbe2`:

```c
static inline uint16_t lfs_tag_id(lfs_tag_t tag) {
    return (tag & 0x000ffc00) >> 10;
}
```

The selected slice includes the two newlines after the closing brace. The
private type declaration is exactly `typedef uint32_t lfs_tag_t;`, `lfs.c`
bytes `[9602,9629)`, 27 bytes, SHA-256
`cb4dcd6212b1a269371d86dddf98ed74853e2eb43753c5d8f8659abbca167ce2`.
The contract is therefore a pure unsigned 32-bit mask and shift returning the
ten ID bits from tag bits `[19:10]` as a value from zero through `0x3ff`, which
fits exactly in `uint16_t`.

The selected tree is an authenticated source-equivalent baseline. The
stripped images do not prove it was Even Realities' exact historical checkout,
and `third_party/littlefs/PROVENANCE.json` retains that ambiguity. Function
identity is independently corroborated by its byte-identical position between
the identified `lfs_tag_splice` and `lfs_tag_size` helpers and by the official
body's exact mask-and-shift semantics. The production source and header retain
the upstream copyright notices and BSD-3-Clause SPDX identifier.

## Authoritative firmware inputs and stock bodies

| Input | Bytes | SHA-256 |
|---|---:|---|
| Official Apollo-main OTA `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Apollo-main installed payload after the 32-byte OTA preamble | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Official bootloader `blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin` | 148,599 | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` |

Apollo main loads at `0x00438000`. Its stock helper begins at installed-payload
offset `0x00092EB0` and OTA file offset `0x00092ED0`. The bootloader loads at
`0x00410000`, placing its stock helper at file offset `0x00000BB8`.

| Image | Runtime span | Bytes | SHA-256 |
|---|---|---|---|
| Apollo main | `[0x004CAEB0,0x004CAEB8)` | `800a8005800d7047` | `0843abb3e9ef39afac8e69ae1e181efa0b5b5c8ebf53e20844b53fdf245b1036` |
| Bootloader | `[0x00410BB8,0x00410BC0)` | `800a8005800d7047` | `0843abb3e9ef39afac8e69ae1e181efa0b5b5c8ebf53e20844b53fdf245b1036` |

The official Thumb body shifts the tag right by ten, shifts the result left by
22, shifts it right by 22, and returns through `lr`. This clears everything
except original bits `[19:10]` and is algebraically identical to upstream
`(tag & 0x000ffc00) >> 10`. Neither body contains a decoded outgoing call or
branch.

The predecessor in each image is the independent non-leaf `lfs_tag_splice`.
Its final four bytes are `40b202bd`, ending in `pop {r1,pc}` (`02bd`), so it
cannot fall through into this leaf. The helper ends with `bx lr` (`7047`),
and the successor begins the independent `lfs_tag_size` leaf with `8005`.
Sequential execution therefore cannot enter or leave the selected body, and
no shared tail or literal pool is owned by it.

## Exact callers and complete-image ingress closure

The complete Apollo-main payload has exactly these direct `BL` entries:

```text
0x004CB262 fff725fe    0x004CB26C fff720fe
0x004CB274 fff71cfe    0x004CB286 fff713fe
0x004CB28E fff70ffe    0x004CB2E6 fff7e3fd
0x004CB2FE fff7d7fd    0x004CB306 fff7d3fd
0x004CB56C fff7a0fc    0x004CB574 fff79cfc
0x004CB64A fff731fc    0x004CB786 fff793fb
0x004CB7EA fff761fb    0x004CB92A fff7c1fa
0x004CB936 fff7bbfa    0x004CB944 fff7b4fa
0x004CBC9E fff707f9    0x004CBCAC fff700f9
0x004CBCEE fff7dff8    0x004CBCF8 fff7daf8
0x004CBDF8 fff75af8    0x004CBE02 fff755f8
0x004CBE3A fff739f8    0x004CBE42 fff735f8
0x004CBE60 fff726f8    0x004CBE68 fff722f8
0x004CBE82 fff715f8    0x004CBEA0 fff706f8
0x004CC138 fef7bafe    0x004CC146 fef7b3fe
0x004CCE82 fef715f8    0x004CCEBE fdf7f7ff
0x004CCF04 fdf7d4ff    0x004CD184 fdf794fe
0x004CD1B6 fdf77bfe    0x004CD2A8 fdf702fe
0x004CD58A fdf791fc    0x004CD5A2 fdf785fc
0x004CE4C6 fcf7f3fc    0x004CE502 fcf7d5fc
0x004CE52A fcf7c1fc    0x004CE59E fcf787fc
0x004CE63C fcf738fc    0x004CE66A fcf721fc
0x004CE6A8 fcf702fc    0x004CE82C fcf740fb
0x004CE89C fcf708fb    0x004CF700 fbf7d6fb
0x004CF756 fbf7abfb    0x004CF894 fbf70cfb
```

| Apollo-main evidence | SHA-256 |
|---|---|
| little-endian caller addresses | `8b299c57f8287b2897c79cabf888f16064f4cdb4ea60a91c2b81bb4a47a67f8a` |
| concatenated encodings | `6e0f0ed7af5c0c98793ac6dbef408721984f75c7c1b97de11082ca911a1c032c` |
| address-plus-encoding records | `6873a8429b442e11eb62f6f8b2af3332390b31b468a429609092eab5442536ce` |

The complete bootloader has exactly these direct `BL` entries:

```text
0x00410F6A fff725fe    0x00410F74 fff720fe
0x00410F7C fff71cfe    0x00410F8E fff713fe
0x00410F96 fff70ffe    0x00410FEE fff7e3fd
0x00411006 fff7d7fd    0x0041100E fff7d3fd
0x00411274 fff7a0fc    0x0041127C fff79cfc
0x00411352 fff731fc    0x0041148E fff793fb
0x004114F2 fff761fb    0x00411632 fff7c1fa
0x0041163E fff7bbfa    0x0041164C fff7b4fa
0x004119A6 fff707f9    0x004119B4 fff700f9
0x004119F6 fff7dff8    0x00411A00 fff7daf8
0x00411B00 fff75af8    0x00411B0A fff755f8
0x00411B42 fff739f8    0x00411B4A fff735f8
0x00411B68 fff726f8    0x00411B70 fff722f8
0x00411B8A fff715f8    0x00411BA8 fff706f8
0x00411D98 fef70eff    0x00411DA6 fef707ff
0x00412A86 fef797f8    0x00412AC2 fef779f8
0x00412B08 fef756f8    0x00412D88 fdf716ff
0x00412DBA fdf7fdfe    0x00412EAC fdf784fe
0x0041318E fdf713fd    0x004131A6 fdf707fd
0x00414DD0 fbf7f2fe    0x00414E26 fbf7c7fe
0x00414F64 fbf728fe
```

| Bootloader evidence | SHA-256 |
|---|---|
| little-endian caller addresses | `274d04664805db5bbaa04be1e525f2ba476ee71e4e965499cfd3bff37ddb76bd` |
| concatenated encodings | `77b629db9b027cdd46c9a59eb2a5d00eb93ddfae3710909bc81a1a06ade7d548` |
| address-plus-encoding records | `f8d8594ec11e50553a9c7c050a88c3efa76ed134cb2399ec05a6bbee396b3e0b` |

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
| `r0` on return | zero-extended unsigned 16-bit ID value |

There are no pointer or stack arguments, structures, providers, global state,
allocation, filesystem-object access, callbacks, configuration conditionals,
or hardware dependencies. The production header exposes only a `uint32_t`
scalar alias and `uint16_t` result, with compile-time width assertions.

The focused differential compiles the actual authenticated upstream
definition beside the production adaptation. It checks eight directed edge
and pattern values, exhausts all 65,536 values of a 16-bit window spanning the
complete ten-bit ID field with deterministic ignored-bit noise above and
below it, and
checks 20,000 seeded random 32-bit inputs. All 85,544 comparisons match the
pristine definition. The exhaustive portion repeats every ten-bit ID value
64 times while varying neighboring bits that the helper must ignore.

## Deterministic Apple target-object closure

Apple Clang `21.0.0 (clang-2100.3.27.1)` compiles the actual adaptation twice
under both reviewed production-shaped profiles:

| Profile | Target and optimization | Object bytes / SHA-256 | Text alignment |
|---|---|---|---:|
| Apollo main | `thumbv7em-none-eabi`, `-mthumb -O2` | 776 / `4ae5a9c3581c22b232e9e8b46ed66df8bbd5a94d1790087615781664ac63be2a` | 4 |
| Bootloader | `arm-none-eabi`, `-mcpu=cortex-m55 -mthumb -Oz` | 776 / `12a1f7437db7132bf25a8d8011e0f69a40f083d6cc259f3bbcf195b244f8f15a` | 2 |

Both profiles produce the same complete isolated text:

```text
c0f389207047
```

The six bytes hash to
`6194594e24288e708887a0e938b2a54401c8c732210d91af7a5927d03bd3604c`.
Each object has zero undefined symbols and zero text relocations. Its only
other allocated section is the canonical eight-byte
`.ARM.exidx.text.open_cfw_littlefs_tag_id` record with flags `130`, which the
focused extractor authenticates and discards. This closes the generated
leaf's provider and relocation dependencies in both production images.

Homebrew Clang 22.1.8 independently emits the same two deterministic objects
and the same six-byte text under the reviewed main and boot target profiles.
The leaf pin is therefore cross-toolchain identical even though the
surrounding Apollo-main overlays remain profile-specific.

## Production inputs and registration gate

| Production input | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/littlefs/runtime_littlefs_tag_id.c` | 845 | `5b6c3ce0f4236d6c6bc0a12891e41929e9034a7ddc2f68bd4f6a1d5d4fa07638` |
| `components/shared/littlefs/runtime_littlefs_tag_id.h` | 872 | `5d6d1c5df9a0fb31f80ad0f6a876795cb154b039fa72df17c615b38cd5e2099e` |
| `tests/test_runtime_littlefs_tag_id.py` | 38,435 | `4c7fa3a4ad2a1e08f4627ecb4263350fd818ce48d7c84d1dcf11b0249e4e6a37` |

The focused test pins both source files, the pristine upstream bytes, official
image identities, both stock bodies, both complete caller sets, predecessor
and successor boundaries, Apple and Linux placements, complete entry
redirects, aggregate sizes and cross-recorded hashes, manifest topology,
provenance ownership, and complete region continuity. It requires the
source/header/symbol to be present in both overlay configs, the canonical
manifest, and `third_party/littlefs/PROVENANCE.json`.

## Production placements and complete entry redirects

| Image/profile | Source-leaf offset / runtime span | Complete stock patch |
|---|---|---|
| Apollo main, Apple | 124,596 / `[0x007B29D8,0x007B29DE)` after two alignment bytes | `e7f292bd00bf00bf` |
| Apollo main, exact-root Linux | 126,416 / `[0x007B30F4,0x007B30FA)` after two alignment bytes | `e8f220b900bf00bf` |
| Bootloader, both | 650 / `[0x00434702,0x00434708)` | `23f0a3bd00bf00bf` |

Each non-linking `B.W` plus NOP fill owns the complete eight-byte stock span.
The Apple main alignment occupies `[0x007B29D6,0x007B29D8)`; Linux uses
`[0x007B30F2,0x007B30F4)`. The boot leaf follows the production tag-type3
leaf directly and needs no new alignment.

## Aggregate offline artifacts

| Profile | Apollo-main overlay/component | Boot overlay/component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 124,602 / `229ca8faff25bd61cd21152d828275f6e1dad9883eab359056482956ea166e98`; 3,647,998 / `8dddb1f59da1319dc15815ded6258f966a6fd08d6ed7edc134122de5bca2fff6` | 656 / `432f0c91a6db142a951db076fc89a4a80e740675d63f62263f45c21e37777ad3`; 149,256 / `6d96308ea4e5851ab137831d6da991184b6611551a01fa18e4cef3f1877f4694` | 4,426,486 / `bfa8629a4c182e7448b4b6d89f875cd99f7e105876f12e4d2904d755cafc69f1` |
| exact-root Linux Clang 22.1.8 | 126,422 / `fcf2783a5a73474fb87cdd22cc592a12056b6a4d4080e7f8ca6120b88d82ebaa`; 3,649,818 / `40d16ee5833eae6ae3229d82fcd583fd2c3ba9fe6234978d503a57c0d88ffeff` | 656 / `4cadbf422b57b1905b38df77ab0d24932839aa28f883f57e56a09183d577edb8`; 149,256 / `a3ca91bb744c777d7d98d8b34a044e613ad251a972d6e6d54a8a48b959795ad2` | 4,428,306 / `727354ce585843f11fabec93884640fdf58c71b251f5b7067ee4c0703cb53fcd` |

These deterministic aggregate hashes come from the encompassing Apple and
exact-root Linux integration builds. Offline assembly is GO only under those
reviewed profiles; the artifact pins are not a hardware-validation claim.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_runtime_littlefs_tag_id
PYTHONPYCACHEPREFIX=/tmp/open-cfw-pycache python3 -m py_compile tests/test_runtime_littlefs_tag_id.py
git diff --check -- components/shared/littlefs/runtime_littlefs_tag_id.c components/shared/littlefs/runtime_littlefs_tag_id.h tests/test_runtime_littlefs_tag_id.py docs/research/littlefs-tag-id-candidate-audit.md
```

Observed focused result: five of five tests pass. All compiler products are
created inside an operating-system temporary directory and removed by the
harness.
