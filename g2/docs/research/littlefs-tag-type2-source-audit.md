# littlefs `lfs_tag_type2` production source audit

Date: 2026-08-02

Scope: the private Apollo-main `lfs_tag_type2` scalar helper in official G2
firmware `2.2.6.10`, its bounded openCFW source replacement, and the recorded
Apple Clang and exact-root Linux Clang build profiles.

Decision: **GO (high confidence) for this exact Apollo-main entry replacement;
NO-GO for a broader littlefs source-ownership claim or hardware flashing.**

The official helper at `[0x004CAE90,0x004CAE98)` is an eight-byte, call-free
Thumb leaf. Exactly two complete-image direct calls enter its first halfword;
no tested branch or stored-pointer class enters its interior. Its recovered
ABI and behavior are the exact scalar contract of `lfs_tag_type2` in the
authenticated littlefs v2.10.1 source-equivalent snapshot. The replacement
has no provider, relocation, data, allocation, callback, filesystem-object,
or hardware closure.

This decision does **not** prove that the selected Git commit was Even
Realities' exact historical checkout. It does not replace the surrounding
`lfs_dir_fetchmatch`, the bootloader's byte-identical helper, the complete
littlefs translation unit, or either G2 block-device port. No image was signed,
flashed, booted, or exercised on hardware for this audit.

## Authenticated upstream and remaining history ambiguity

| Property | Pin |
|---|---|
| Repository | `https://github.com/littlefs-project/littlefs.git` |
| Selected release | `v2.10.1` |
| Commit | `0494ce7169f06a734a7bd7585f49a9fa91fa7318` |
| Tree | `06dd0162169d3cb550cd24a3e34d0e4d02983ad3` |
| Commit date | `2024-12-20T09:02:13-06:00` |
| License | BSD-3-Clause |
| `lfs.c` | 196,753 bytes; SHA-256 `81a209e8551754d13b24fc0a2b6707fb3b2475e14feba00bf0df722b98a31398` |
| `LICENSE.md` | 1,523 bytes; SHA-256 `0cb4ff1daf5fdc1359c6a6ee3116092f08fc100c9d58b1b77ab17bfd801f856d` |

The complete 38-assertion bootloader line fingerprint selects v2.10.1 among
the 38 inspected official v2 tags, and Apollo main has the same littlefs
source generation. The selected snapshot is therefore an authenticated
**source-equivalent release baseline**, not proof of the vendor's exact
repository state. The selected `lfs.c` and two later official source states
compile byte-identically under the recovered G2 configuration: one later
state adds an explicit cast and another differs only in disabled trace code.
The stripped binaries cannot resolve that remaining repository-history
ambiguity, so `third_party/littlefs/PROVENANCE.json` retains it explicitly.

The exact upstream definition is `lfs.c` bytes `[10326,10418)`, 92 bytes,
SHA-256
`65f614cf5ed7152f7ad2176547453c329b1f15442e550ef6632b0f7773970f78`:

```c
static inline uint16_t lfs_tag_type2(lfs_tag_t tag) {
    return (tag & 0x78000000) >> 20;
}
```

The private type declaration is `typedef uint32_t lfs_tag_t;`, `lfs.c` bytes
`[9602,9629)`, 27 bytes, SHA-256
`cb4dcd6212b1a269371d86dddf98ed74853e2eb43753c5d8f8659abbca167ce2`.
The complete contract is consequently a pure unsigned 32-bit mask and shift
whose result is in `[0,0x780]` and fits exactly in `uint16_t`.

The local adaptation and header retain the upstream copyright notices and
BSD-3-Clause SPDX identifier. They do not import the pristine translation
unit wholesale.

## Authoritative images and stock boundary

| Input | Bytes | SHA-256 |
|---|---:|---|
| Official Apollo-main OTA `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Installed Apollo application after its 32-byte preamble | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Official Apollo bootloader | 148,599 | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` |

Apollo main loads at `0x00438000`. The helper begins at installed-application
offset `0x00092E90` and OTA file offset `0x00092EB0` (`601,776` decimal):

```text
span    [0x004CAE90,0x004CAE98)
size    8 bytes
bytes   000d10f4f0607047
sha256  a017094f8fc58d202d8c5a588f66dd319248578fa39e0f392ba3c7857d3500ef
```

Thumb semantics are:

```text
004cae90  000d       lsrs    r0, r0, #20
004cae92  10f4f060   ands.w  r0, r0, #0x780
004cae96  7047       bx      lr
```

The stock expression `(tag >> 20) & 0x780` is algebraically identical for
unsigned 32-bit `tag` to upstream `(tag & 0x78000000) >> 20`.

Boundary witnesses independently close the neighboring return sequences:

| Role | Span | Bytes | SHA-256 |
|---|---|---:|---|
| predecessor window | `[0x004CAE80,0x004CAE90)` | 16 | `8dadfcad7e63105ac780ef289a310c272fcdf7e29caf4a02a2143c14b44137a2` |
| replacement leaf | `[0x004CAE90,0x004CAE98)` | 8 | `a017094f8fc58d202d8c5a588f66dd319248578fa39e0f392ba3c7857d3500ef` |
| successor window | `[0x004CAE98,0x004CAEB0)` | 24 | `cd9738835b2eb4c365698eea3f3345ec70a2829d13238770a68145230711371d` |

The predecessor window ends in its own `bx lr`; the audited leaf ends in its
own `bx lr`; the successor begins at `0x004CAE98`. There is no shared tail,
fallthrough, literal pool, or outgoing edge in the replacement span.

The same eight bytes and identical boundary windows occur once in the
bootloader at `[0x00410B98,0x00410BA0)`, file offset 2,968. Its two relative
call sites are likewise mirrored at `0x0041182E` and `0x00411940`. That is
strong corroboration of the common littlefs source generation, but the
bootloader entry remains official opaque code and is outside this Apollo-main
promotion.

## Caller and complete-image ingress closure

Both Apollo-main callers are inside the authenticated generation of upstream
`lfs_dir_fetchmatch`. They correspond to the two uses in the directory commit
scan: testing whether the previous tag may be an erased commit CRC and testing
whether the current tag is a commit CRC.

| Call site | Encoding | Decoded target |
|---:|---|---:|
| `0x004CBB26` | `fff7b3f9` | `0x004CAE90` |
| `0x004CBC38` | `fff72af9` | `0x004CAE90` |

The exact caller evidence pins are:

| Record | SHA-256 |
|---|---|
| little-endian caller addresses | `358e54fd96099fb219db8ec7d846eddef29381ccc56fe839af29ff787c844732` |
| concatenated call encodings | `b88d9d1d5f3c95897a8c5bc1975e441efe3bb41764d6d4d55e24b24b6ec549a7` |
| address-plus-encoding records | `85f2f7613d51ea12e6fd297ec5c1f2f7d1a903e8d58a7a9de4893f0d0d90414a` |

A halfword-aligned scan of the complete installed application, including its
final halfword, found:

- exactly the two direct `BL` entries above;
- no `B.W` entry;
- no external branch to an interior halfword;
- no wide conditional, narrow unconditional, narrow conditional, `CBZ`, or
  `CBNZ` target into the span; and
- no byte-aligned stored even or Thumb address into the entry or interior.

The scan closes those decoded branch and stored-address classes. It is not a
universal whole-program data-flow proof and does not independently exclude an
address synthesized by an unrecognized multi-instruction sequence. The two
known direct callers, call-free body, explicit return, and lack of observed
alternate or interior ingress make a full-span entry redirect appropriate.
Neither caller is rewritten: both continue to call `0x004CAE90`, which becomes
the authenticated generated redirect.

## ABI, source, and generated-object closure

The callable ABI is AAPCS32 Thumb, little-endian:

| Register | Meaning |
|---|---|
| `r0` on entry | `lfs_tag_t`, exactly one unsigned 32-bit word |
| `r0` on return | zero-extended `uint16_t` tag type-2 value |

There are no stack arguments, pointer arguments, callee-observed structure
layouts, or provider calls. The local header isolates the ABI as
`typedef uint32_t open_cfw_littlefs_tag_t` and statically asserts the 32-bit
tag and integer widths and 16-bit return width.

| Local input | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/littlefs/runtime_littlefs_tag_type2.c` | 789 | `c2ea0965e62aa126fb4b8e752526b8a926a9088739811cba09dcf7d1ed6f3940` |
| `components/shared/littlefs/runtime_littlefs_tag_type2.h` | 883 | `17915b900db79e3e611379645a8780723410e5c826f6bfa7619d86bac28f0b13` |

The selected function is compiled independently for `thumbv7em-none-eabi`
at `-O2` with freestanding, no-builtin, no-jump-table, no-unaligned-access,
no-unwind, ROPI, function/data-section, warning-as-error, and deterministic
ident flags. Apple Clang 21.0.0 and exact-root Homebrew Clang 22.1.8 produce
the same reviewed object and function text:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| target ELF object | 788 | `8114a6a47e5e5f65517bc62afdfca88bae1c38961643a12940d62554a077887e` |
| `.text.open_cfw_littlefs_tag_type2` | 10 | `88be40d05d37142bf0bae8306026d8c405a4f8f441aabd87ee6731557d4149fd` |

Function text is:

```text
4ff4f06101ea10507047
```

The section is four-byte aligned. The function symbol is global/default,
Thumb, starts at section offset zero, and occupies all ten bytes. It has zero
undefined symbols and zero text relocations, so its required provider list is
empty. The only other allocated section is the canonical eight-byte
`.ARM.exidx.text.open_cfw_littlefs_tag_type2` CANTUNWIND record with its
metadata-only `R_ARM_PREL31` section relocation. The extractor authenticates
and discards that record. There is no allocated rodata, writable data, BSS,
literal, second function, AEABI helper, or runtime seam.

The focused differential gate compiles the actual 92-byte pristine upstream
definition alongside the adaptation. Eight directed values cover zero, all
ones, mask edges, the high bit, representative patterns, and nonselected bits.
It then exhausts all 65,536 possible upper 16-bit values with deterministic
nonzero lower-bit noise. All 65,544 comparisons match both the pristine source
and the mask/shift model. Because the result depends only on those upper bits,
the exhaustive portion covers every behaviorally relevant bit combination.

## Production overlay and safe patch fill

`overlay.json` registers this as one strict, relocation-free relocated leaf,
adds `open_cfw_littlefs_tag_type2` once to the callable function list, and
adds one `b_w` patch site authenticating the complete eight-byte stock span.
The builder emits one four-byte non-linking Thumb `B.W`, then two Thumb NOPs
(`00bf 00bf`). Filling all four trailing bytes prevents stale stock
instructions from remaining as a usable interior tail.

| Profile | Leaf offset | Runtime | Padding before | Entry replacement | Replacement SHA-256 |
|---|---:|---:|---:|---|---|
| Apple Clang 21.0.0 | 124,548 | `0x007B29A8` | 2 | `e7f28abd00bf00bf` | `659991e787790e45f3c2b41575292709cf44eb4b6342c9f6ff4b735426d188df` |
| Linux Clang 22.1.8 | 126,368 | `0x007B30C4` | 2 | `e8f218b900bf00bf` | `84c933a2887b7027c2904be21d89be5ef671b3ec83f7f7160974aa8fe17dbd4d` |

Each branch decodes back to its profile's exact appended runtime address. The
ten leaf bytes are identical before and after placement because there are no
relocations.

The recommended/registered leaf record is therefore:

```text
function                    open_cfw_littlefs_tag_type2
source                      components/shared/littlefs/runtime_littlefs_tag_type2.c
source size / sha256        789 / c2ea0965e62aa126fb4b8e752526b8a926a9088739811cba09dcf7d1ed6f3940
expected size / sha256      10 / 88be40d05d37142bf0bae8306026d8c405a4f8f441aabd87ee6731557d4149fd
alignment                   4
Apple offset                124548
Linux offset                126368
strict relocation contract  true
relocations                 []
```

The patch record is:

```text
name             replace_littlefs_tag_type2
runtime_address  0x004CAE90
expected_size    8
expected_sha256  a017094f8fc58d202d8c5a588f66dd319248578fa39e0f392ba3c7857d3500ef
branch           b_w
target_function  open_cfw_littlefs_tag_type2
```

## Aggregate artifacts and ownership deltas

The exact post-promotion artifacts are:

| Profile | Overlay bytes / SHA-256 | Apollo component bytes / SHA-256 | EVENOTA bytes / SHA-256 |
|---|---|---|---|
| Apple Clang | 124,558 / `8dc6206e0a6ed458401de46e5fa60d0a7eebc152eab4032d087fc4e667f7f378` | 3,647,954 / `ec9f098bf69029862df63ff0929f6bbd9c345f540b3565b6cfc7cd71edbc36c4` | 4,426,408 / `f31bef6e0faf8e3655f5c92c385ebe6ee3e7f5ef5635401ceb05cf98089976fe` |
| Linux Clang | 126,378 / `12ebf0aef9e1ce61c6f5f151515a8c4245b1b353ca921dcddfc6b521cf8f870a` | 3,649,774 / `eeaca07a2c4bec75f4652e9f2853a75ff45684584d5e6074d99d112a41e5ddfc` | 4,428,228 / `caa150eda201d91c8ec6046f5a9017ab87e7ee936fe0f542957bff4efdd4b37f` |

Relative to the immediately preceding fixed32 production aggregate, each
profile adds ten source text bytes and two alignment bytes, replaces eight
opaque stock bytes with generated entry bytes, and grows its component and
package by twelve bytes.

Builder component accounting is:

| Profile | Source-owned overlay/in-place | Generated wrapper | Generated patch sites | Opaque base | Replaced stock |
|---|---:|---:|---:|---:|---:|
| Apple Clang | 124,740 | 32 | 86,042 | 3,437,140 | 86,224 |
| Linux Clang | 126,560 | 32 | 86,208 | 3,436,974 | 86,390 |

The builder's source-owned column includes alignment inside the appended
overlay. The canonical manifest gives the Apple two-byte pad the more precise
`generated_alignment` status. Under that region classification, complete
Apple package ownership is 125,312 source-compiled bytes, 87,883 generated
bytes, and 4,213,213 opaque bytes. The Linux plan intentionally collapses the
compiler-dependent appended tail into one coarse `source_compiled` region;
its corresponding profile accounting is 127,219 source bytes, 87,796
generated bytes, and 4,213,213 opaque bytes.

Offline recomposition yields these flash-plan pins:

| Profile | Plan bytes | SHA-256 | Placed / unresolved / container-only |
|---|---:|---|---|
| Apple Clang | 698,204 | `3ac4c2dfdce764389721b2c81f87d6bd0730cfefcdd0cfbe98bf6afa32935bcd` | 971 / 2 / 5 |
| Linux Clang | 586,282 | `64522f68968b3a063fef934c0304c3d37caaff21b7650aa6d31c10f25e2cbda8` | 821 / 2 / 5 |

These are reproducibility and mapping artifacts only. Their safety block keeps
automatic flashing false.

## Manifest regions

The canonical Apple manifest splits the stock and appended boundaries into
five exact regions:

| Region | File offset | Runtime | Bytes | Ownership |
|---|---:|---:|---:|---|
| `opaque_between_littlefs_endian_utilities_and_littlefs_tag_type2` | 600,106 | `0x004CA80A` | 1,670 | `official_blob` |
| `littlefs_tag_type2_source_replacement` | 601,776 | `0x004CAE90` | 8 | `generated_source_entry_replacement` |
| `opaque_between_littlefs_tag_type2_and_littlefs_mlist_isopen` | 601,784 | `0x004CAE98` | 490 | `official_blob` |
| `apollo_littlefs_tag_type2_source_alignment` | 3,647,942 | `0x007B29A6` | 2 | `generated_alignment` |
| `apollo_littlefs_tag_type2_source_leaf` | 3,647,944 | `0x007B29A8` | 10 | `source_compiled` |

The source-appended boundary remains file offset 3,523,396. Noncanonical
compiler profiles retain the exact fixed-address stock split but represent the
tail from that boundary as the existing coarse toolchain-profile source
region; they do not pretend that Apple per-function offsets apply to Linux.

## Retained opacity and explicit safety boundary

This leaf promotion removes only eight opaque Apollo-main instructions. The
following remain outside its source-owned closure:

- both large calling paths inside the official `lfs_dir_fetchmatch` body;
- the bootloader's byte-identical `lfs_tag_type2` homolog;
- the rest of littlefs metadata traversal and commit validation;
- both image-specific G2 read/program/erase/sync block-device ports;
- configuration-sensitive cache, allocator, and power-loss behavior; and
- all actual filesystem contents and device-specific external-flash state.

The replacement cannot mount, read, write, program, erase, format, migrate,
or otherwise access a filesystem or hardware device. It receives one scalar
word, performs a mask and shift, and returns one scalar value. The pristine
littlefs translation units remain reference-only and are not linked wholesale.

No command in this qualification signed an artifact, entered a flashing mode,
accessed a G2 device, or invoked a filesystem operation. Promotion does not
authorize `lfs_format`, `lfs_migrate`, the recovered erase callback, or any
mutating hardware experiment. Those paths retain the separate read-only
golden-image, disposable-copy, power-loss, and explicit hardware-authorization
requirements recorded in the littlefs snapshot safety policy.

## Reproduction

All qualification is offline:

```sh
python3 -m unittest -v tests.test_runtime_littlefs_tag_type2
python3 third_party/littlefs/verify_snapshot.py
./make.sh source
./make.sh verify
```

The focused gate authenticates the official package before reading stock
bytes, scans the full installed application for the reviewed ingress classes,
compiles twice, inspects the exact ELF section/symbol/relocation closure, and
performs the exhaustive behavior comparison. The production build separately
authenticates source, toolchain profile, placement, stock patch span, aggregate
overlay/component/package pins, and manifest partition.

Passing these offline gates supports the scoped GO above. It is not evidence
that an image has been signed, flashed, booted, or validated on physical G2
hardware.
