# G2 littlefs `lfs_fs_disk_version` source-boundary audit

Status: source-integrated in both Apollo-main and bootloader production
overlays

Scope: official G2 package `2.2.6.10`; authenticated binary/source analysis,
host/target validation, redirect-safety research, and subsequent dual-image
source-overlay integration; no signing, flashing, external-flash access, or
hardware use

## Result

The private littlefs v2.10.1 `lfs_fs_disk_version` helper is unequivocally
identified in both official images:

| Property | Apollo main | Bootloader |
|---|---:|---:|
| Entry | `0x004CB0C4` | `0x00410DCC` |
| End-exclusive body | `[0x004CB0C4,0x004CB0CA)` | `[0x00410DCC,0x00410DD2)` |
| Installed-payload offset | `0x000930C4` | `0x00000DCC` |
| Package/file offset | `0x000930E4` | `0x00000DCC` |
| Body size | 6 bytes | 6 bytes |
| Body bytes | `DF F8 9C 08 70 47` | same |
| Body SHA-256 | `1ff8f5ac86a29e52674a91191c4ed763fe635aed200e701063e8224aa15c3870` | same |
| Literal address | `0x004CB964` | `0x0041166C` |
| Literal value | `0x00020001` | same |
| Direct entry callers | 4 | 4 |
| Non-linking or stored entries | none | none |
| External interior entries | none | none |
| Structure/configuration dereferences | none | none |

The helper ignores its `lfs_t *` argument and returns littlefs on-disk
version `2.1`, exactly matching pristine v2.10.1. The official
`struct lfs_config` is 84 bytes in both images and therefore has no
`LFS_MULTIVERSION` `disk_version` field. The two official bodies independently
confirm the resulting constant-return preprocessor path.

This is a safe, closed incremental boundary. The production-integrated source
emits its own source-generated constant pool, so it has no dependency on either
stock image's distant literal pool. Its target object has no relocation,
undefined symbol, call, structure access, block callback, allocator operation,
or MSPI dependency.

## Authoritative inputs

### Official images

| Image | Bytes | SHA-256 | Mapping |
|---|---:|---|---|
| `ota_s200_firmware_ota.bin` | `3,523,396` | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` | 32-byte preamble, payload at `0x00438000` |
| Apollo-main installed payload | `3,523,364` | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` | package bytes after preamble |
| `ota_s200_bootloader.bin` | `148,599` | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` | raw image at `0x00410000` |

### Upstream source

The comparator is the repository's authenticated pristine
[`third_party/littlefs`](../../third_party/littlefs) snapshot:

| Property | Value |
|---|---|
| Selected release | littlefs `v2.10.1` |
| Commit | `0494ce7169f06a734a7bd7585f49a9fa91fa7318` |
| Tree | `06dd0162169d3cb550cd24a3e34d0e4d02983ad3` |
| License | BSD-3-Clause |
| `lfs.c` SHA-256 | `81a209e8551754d13b24fc0a2b6707fb3b2475e14feba00bf0df722b98a31398` |
| `lfs.h` SHA-256 | `ee44e99d6b19119b3e577b969b80c9d5e6f96410c9593794afddf6d4b314c486` |

This is an exact source-equivalent release pin, not a claim that the stripped
firmware proves the historical vendor checkout identity.

## Exact source and preprocessor boundary

Pristine v2.10.1 defines:

```c
#define LFS_DISK_VERSION 0x00020001
```

Its `lfs.c:537...547` helper is:

```c
static uint32_t lfs_fs_disk_version(lfs_t *lfs) {
    (void)lfs;
#ifdef LFS_MULTIVERSION
    if (lfs->cfg->disk_version) {
        return lfs->cfg->disk_version;
    } else
#endif
    {
        return LFS_DISK_VERSION;
    }
}
```

Both G2 bodies decode identically:

```text
ldr.w r0, [pc, #0x89c]
bx    lr
```

The instruction addresses differ by the same amount as their literal pools,
so the identical positive displacement resolves to the image-specific word:

| Image | Load | PC base | Literal | Bytes / value |
|---|---:|---:|---:|---|
| Apollo main | `0x004CB0C4` | `0x004CB0C8` | `0x004CB964` | `01 00 02 00` / `0x00020001` |
| Bootloader | `0x00410DCC` | `0x00410DD0` | `0x0041166C` | `01 00 02 00` / `0x00020001` |

The four-byte literal hashes to
`7b11c1133330cd161071bf23a0c9b6ce5320a8f3a0f83620035a72be46df4104`
in both images. The return does not dereference `r0`; this is the complete
non-multiversion upstream behavior.

## Configuration closure

Apollo main retains its 84-byte configuration at `0x006E83A4`, SHA-256
`f38bd899e180d29ee60609a2452d25c2d2d6c6fef4eb455064e23a6ca7c6e813`.
The bootloader copy at `0x00431070` hashes to
`724c351d2136e3c2f10b59ad84d547da4632739ea1f20eb839e9af2cfbd5b6e8`.

That exact v2.10.1 base layout ends at `inline_max` at offset `0x50`.
`LFS_MULTIVERSION` would append a `disk_version` word and make the structure
88 bytes. Its absence, plus the constant-only machine code, closes the sole
preprocessor ambiguity relevant to this helper. `LFS_THREADSAFE` is also
absent, but it would not change this function.

The helper is independent of all recovered geometry:

- it does not read `cfg`, `block_count`, cache, lookahead, or filesystem
  state;
- it does not call read/program/erase/sync callbacks;
- it has no allocator or diagnostic dependency;
- it does not select or initialize MSPI transport state;
- it cannot read, write, erase, mount, or format external flash.

The constant identifies the littlefs `2.1` on-disk format, not the library
release number `2.10.1`.

## Complete caller and entry topology

Both complete images were scanned at every halfword for Thumb-2 `BL` and
non-linking `B.W`, at every halfword for narrow unconditional, conditional,
`CBZ`, and `CBNZ` targets, and at every byte for stored even or Thumb entry
and interior addresses.

### Apollo main

| Call site | Encoding | Upstream context |
|---:|---|---|
| `0x004CB0CC` | `FF F7 FA FF` | `lfs_fs_disk_version_major` |
| `0x004CB0D8` | `FF F7 F4 FF` | `lfs_fs_disk_version_minor` |
| `0x004CEE94` | `FC F7 16 F9` | `lfs_format_`: initialize superblock version |
| `0x004CF68A` | `FB F7 1B FD` | `lfs_fs_stat_`: report current disk version |

The ordered caller-address list hashes to
`ae0e36961355004428510eea6826a916179f361d3bf07704794f30b35a415282`;
the concatenated call instructions hash to
`dc5088b616be119cacfa263c84d67dd1da2777ab79f7c2d4b0cdc87b30780145`.

### Bootloader

| Call site | Encoding | Upstream context |
|---:|---|---|
| `0x00410DD4` | `FF F7 FA FF` | `lfs_fs_disk_version_major` |
| `0x00410DE0` | `FF F7 F4 FF` | `lfs_fs_disk_version_minor` |
| `0x00414578` | `FC F7 28 FC` | `lfs_format_`: initialize superblock version |
| `0x00414D5A` | `FC F7 37 F8` | `lfs_fs_stat_`: report current disk version |

The ordered caller-address list hashes to
`9215d01804e2d711a345ab86fb61165fb893208336866f3bd8687586a3c8167b`;
the concatenated call instructions hash to
`91c49e14baa9ef7c6fe7570f766c745d8831ee0e1a70262bb09382809edd2f6d`.

For each image:

- exactly the four listed `BL` instructions target the entry;
- no non-linking wide or narrow branch targets the entry;
- no external branch or call targets the interior return instruction;
- no stored even or Thumb pointer names the entry or an interior halfword;
- no vector, callback table, jump table, or shared tail is owned;
- the six-byte stock boundary has no fall-through from its predecessor;
- its only outgoing dependency is the authenticated literal load.

Upstream has additional source references in compile-time comparisons. The
official compiler folds those constant comparisons, which is consistent with
the selected non-multiversion constant path and explains why they do not add
binary callers.

## Literal ownership and closure

The stock literal is not adjacent to the helper. It occupies one word in an
IAR literal pool between larger littlefs functions. A complete halfword scan
finds exactly one narrow-or-wide PC-relative load to each selected word: the
corresponding `lfs_fs_disk_version` entry. Neither literal's even nor Thumb
address is stored anywhere in its image.

The value `0x00020001` naturally occurs elsewhere as an immediate or data
value; those equal-value words are not references to this helper's literal
address and are not part of this boundary.

The applied redirect replaces the complete six-byte entry with a four-byte
non-linking Thumb branch and one two-byte NOP. The old pool word remains as
unreachable opaque data until its containing pool is split during a larger
littlefs translation-unit replacement. The integrated target implementation
does not use it.

## Integrated target implementation

The integrated freestanding implementation preserves the exact
constant-return source body and emits:

```text
00 48 70 47 01 00 02 00
```

This decodes as:

```text
ldr  r0, [pc, #0]
bx   lr
.word 0x00020001
```

The complete eight-byte source-generated function and local pool hash to
`72eba3f48315967708b8128a1c2c9b4273ac363d25ec821bb9a03ea58ed9ce24`.
The target object:

- has one eight-byte function symbol;
- has zero `.text` relocations;
- has zero undefined symbols;
- has no call, external literal, global data, or structure access;
- is position-independent within the emitted function-plus-pool span;
- is two bytes larger than the stock body alone but two bytes smaller than
  the stock body plus its four-byte external literal dependency.

The source SHA-256 is
`70eee1465927f45712617297763217459c5194e41bac6985323f7fc177340572`.

## Focused validation

The isolated host candidate is compared with a separately compiled pristine
v2.10.1 `lfs.c`/`lfs_util.c` oracle. The focused suite checks:

- exact 32-bit result and scalar width over repeated calls;
- exact target symbol, bytes, local pool, and opcodes;
- zero target relocations and undefined symbols;
- authenticated upstream source/header/provenance hashes;
- complete official package, payload, and bootloader hashes;
- both official configuration hashes and the 84-byte non-multiversion ABI;
- identical stock bodies, literals, and neighboring function generation;
- exhaustive dual-image entry/interior branch and stored-pointer topology;
- exhaustive PC-relative references and stored addresses for each literal.

All seven focused tests pass.

## Files

- [`runtime_littlefs_disk_version.c`](../../components/apollo_main/core_overlay/runtime_littlefs_disk_version.c)
- [`runtime_littlefs_disk_version_host.c`](../../tests/fixtures/runtime_littlefs_disk_version_host.c)
- [`runtime_littlefs_disk_version_upstream_oracle_host.c`](../../tests/fixtures/runtime_littlefs_disk_version_upstream_oracle_host.c)
- [`test_runtime_littlefs_disk_version.py`](../../tests/test_runtime_littlefs_disk_version.py)

## Applied integration

The shared source is integrated at:

- Apollo main `[0x004CB0C4,0x004CB0CA)`;
- bootloader `[0x00410DCC,0x00410DD2)`.

Each image uses its own entry redirect and the same source-generated function
body. The integration pins the six-byte stock hash, all four direct callers
per image, the absent entry/interior/stored references, and the eight-byte
relocation-free target. The distant stock literal word remains opaque; its
ownership should move only when the surrounding IAR literal pool is split with
corroborating evidence.

No decompilation or G2-specific algorithm recreation is needed for this
helper. A future full `lfs.c` integration can restore the upstream private
symbol directly and remove the temporary project-prefixed binding.

## Follow-on major/minor source reuse

The two adjacent private helpers are now production-integrated from
`components/apollo_main/core_overlay/runtime_littlefs_disk_version_parts.c`.
That 1,734-byte source has SHA-256
`920d03e80c9d16a1d0b4299f8151eefe4d9f3ac1ba89c2d40bcc5830335eb5a7`
and reuses the exact littlefs v2.10.1 `lfs.c` bodies for
`lfs_fs_disk_version_major` and `lfs_fs_disk_version_minor` at commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. Copyright and BSD-3-Clause
license provenance are retained in the source and
`third_party/littlefs/LICENSE.md`.

The focused boundary audit closes the only configuration question:
`LFS_MULTIVERSION` is disabled in both authenticated 84-byte G2
configuration objects. Therefore the upstream bodies ignore their `lfs_t *`
argument and depend only on the already integrated
`open_cfw_littlefs_disk_version` provider. The major and minor functions
each emit a ten-byte raw target section and one `R_ARM_THM_CALL` relocation
at function offset `+0x02`. Their raw SHA-256 values are:

| Leaf | Raw bytes | Raw SHA-256 |
|---|---:|---|
| major | 10 | `ebb72edfdb508cbf5b617452eb60cbceb58bfdfc879dcece076544efa75c092f` |
| minor | 10 | `da349b05b3a26d6a22ba3f707c4c21e1591915aeb8451e21f7509905926a4b9d` |

Complete dual-image scans find no non-linking branch, stored pointer, or
interior entry. The complete caller sets remain in `lfs_mount_` version
validation and diagnostics:

| Image | Major callers | Minor callers |
|---|---|---|
| Apollo main | `0x004CF03A`, `0x004CF06C`, `0x004CF130` | `0x004CF046`, `0x004CF056`, `0x004CF064`, `0x004CF128` |
| bootloader | `0x00414712`, `0x00414744`, `0x00414808` | `0x0041471E`, `0x0041472E`, `0x0041473C`, `0x00414800` |

### Exact relocated-leaf contracts

The Apollo-main linker places major at `[0x007B01B8,0x007B01C2)` and minor
at `[0x007B01C4,0x007B01CE)`. It inserts exactly two generated alignment
bytes at `[0x007B01C2,0x007B01C4)`, SHA-256
`96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7`.
The respective calls are at `0x007B01BA` and `0x007B01C6`, both targeting
the source-owned provider at `0x007AED1C`. The relocated leaf SHA-256 values
are:

- major:
  `cffc852c2243f51e8a52543b4f2410b192e2365c25f161cfd12f69cae8544122`;
- minor:
  `e0494044bcf077ed5b67a33cf3eb526bb9b8b6f31dcfefb5ce347a197b100012`.

The bootloader linker places major at `[0x00434592,0x0043459C)` and minor at
`[0x0043459C,0x004345A6)` without padding. Their calls at `0x00434594` and
`0x0043459E` both target the source-owned provider at `0x00434490`. The
relocated leaf SHA-256 values are:

- major:
  `15251b134de5617995984b9d8140d6fb88dca904ef8ef72e480b99f3c0250b2a`;
- minor:
  `685d7f3e70053272d9a3920aaf7867d0a84e8adb402bbccd4ef3afc76195b2b7`.

These are ordered, fail-closed link contracts: any extra relocation, symbol,
padding change, address change, or body-hash change is rejected.

### Current production pins

The current Apollo-main overlay is 114,346 bytes with SHA-256
`bdc1e353d1adcb0075231afb6c423616dcc0da8335b4b430afe51763a0b9df20`;
its 3,637,742-byte provider has SHA-256
`d69c4834f65b0661834f990da8167ca6989a1b1c97fda838edc488a4ed0b3e8e`.
The bootloader overlay is 302 bytes with SHA-256
`e94e33658aca89d3830182bc6c17c656256a194262835c041fecc93e1d72dc59`;
its 148,902-byte provider has SHA-256
`abc583d976a01e237ffa4ed29e4be1b6ff0e5ae2d9756bccec58d1779fe20239`.

The 4,415,876-byte package has SHA-256
`60cd913a716266b349ce18295064f2484749a7dbad2ab9244c923c927bd56c2f`.
Boot/main CRC-32C/MSB values are `0x12EAC8F8`/`0x7E9838B8`; the
546,404-byte flash plan has SHA-256
`52124c17205ae10e47f0b02d0cd6bae7c2b30e10d65d787aa34201a53fe0dc68`.
The manifest reports 757 placed, two unresolved, five container-only, and
six protected regions. It classifies 114,860 source bytes, 81,523 generated
bytes, and 4,219,493 opaque bytes; 196,383 bytes are controlled.

`./make.sh source` and core-source manifest verification pass. These results
establish deterministic offline integration, not successful execution on
G2 hardware.
