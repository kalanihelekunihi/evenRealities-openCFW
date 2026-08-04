# `lfs_file_size_` stock/source audit

Date: 2026-08-01

Scope: Apollo main image from official G2 `2.2.6.10`; bootloader checked only for presence

Decision: **GO (high confidence)**, subject to the integration conditions below

## Result

The stock routine at `[0x004ce472, 0x004ce48a)` is a complete, independently
replaceable implementation of upstream littlefs `lfs_file_size_`. Its instruction
semantics, ABI field accesses, two direct callers, and sole outgoing dependency
all match the authenticated v2.10.1 source-equivalent snapshot. There are no
external references to the routine's interior and no stored entry/interior
pointers in the installed application image.

The routine is not present in the bootloader image, so this finding authorizes an
Apollo-main replacement only.

## Authoritative stock bytes

The source image is:

- OTA package: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`
- OTA size: `3,523,396` bytes
- OTA SHA-256: `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`
- Installed application load address: `0x00438000`
- OTA preamble: `32` bytes
- Installed application size: `3,523,364` bytes
- Installed application SHA-256:
  `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`

For `lfs_file_size_`:

- Installed span: `[0x004ce472, 0x004ce48a)`
- Installed payload offset: `0x00096472`
- OTA file offset: `0x00096492` (`615570` decimal)
- Length: `24` bytes
- Bytes:
  `80b50800016b890304d5c16a406bfcf73af900e0c06a02bd`
- SHA-256:
  `98ba58dac7de35e47c75240c0671b11e6b403a1bffed50a617c6543eb26a83cc`
- Occurrences in the Apollo OTA: exactly one
- Occurrences in the official bootloader image: zero

Thumb disassembly:

```text
004ce472  80b5       push  {r7, lr}
004ce474  0800       movs  r0, r1
004ce476  016b       ldr   r1, [r0, #0x30]
004ce478  8903       lsls  r1, r1, #0x0e
004ce47a  04d5       bpl   0x004ce486
004ce47c  c16a       ldr   r1, [r0, #0x2c]
004ce47e  406b       ldr   r0, [r0, #0x34]
004ce480  fcf73af9   bl    0x004ca6f8
004ce484  00e0       b     0x004ce488
004ce486  c06a       ldr   r0, [r0, #0x2c]
004ce488  02bd       pop   {r1, pc}
```

This tests bit 17 of `file->flags` by left-shifting it by 14 and branching on
the sign flag. If `LFS_F_WRITING` is set, it returns the unsigned maximum of
`file->pos` and `file->ctz.size`; otherwise it returns `file->ctz.size`.
The first `movs` discards the unused `lfs` argument and moves the `file`
argument into `r0`.

The only internal control-flow edges are:

- `0x004ce47a -> 0x004ce486`
- `0x004ce484 -> 0x004ce488`

Boundary evidence:

- Predecessor `lfs_file_rewind_`: `[0x004ce460, 0x004ce472)`, 18 bytes,
  SHA-256 `be02691b2e7339d7dd1d54b31712c3e8563e5a86f4406a469888640fad9435cd`
- Successor `lfs_stat_` starts at `0x004ce48a` with its own prologue
- There is no shared tail, fallthrough, or literal pool at either boundary

## Call graph and reference closure

A halfword-aligned scan of the complete installed application found exactly two
direct calls to `0x004ce472`:

| Call site | Encoding | Enclosing routine | Evidence |
|---|---|---|---|
| `0x004ce3e2` | `00f046f8` | `lfs_file_seek_` | `[0x004ce3bc, 0x004ce45c)`, 160 bytes, SHA-256 `368a3e58188f71ad37233eaca687cd3939a9f06406702a176f9731f22bcaf61f` |
| `0x004cfc56` | `fef70cfc` | public `lfs_file_size` | `[0x004cfc2e, 0x004cfc5c)`, 46 bytes, SHA-256 `a1758f1321e8dce4b67a40f8ddaaf00ba3a258f00e05d1a04b3e5f2fa199114b` |

The first call is the `LFS_SEEK_END` case in upstream `lfs_file_seek_`. The
public wrapper performs the open-file membership assertion before calling this
private leaf. That assertion is deliberately not part of `lfs_file_size_`.

Caller-scan fingerprints:

- Little-endian caller-address list SHA-256:
  `08c4f1b6d7e4d33e74e7f8f8ba04a1f58705a427f6fb311bae15155d97050078`
- Concatenated call encodings SHA-256:
  `dc423fe38476315c1f5e2cf48da42fccc183860944a880c5fa015779e039fb6d`
- Address-plus-encoding records SHA-256:
  `c2204bc8396ba7c2b46a99555fff1ca71d1deb431ab2dda71abb9b1580a02b85`

The whole-image scan found no external narrow, wide, or conditional branch to
an interior halfword; no CBZ/CBNZ edge to the span; and no stored even or Thumb
entry/interior pointer at any byte alignment.

For context, the public `lfs_file_size` wrapper has two direct callers:

- `0x004748ee`, encoding `5bf09ef9`, inside the shared file-size wrapper at
  `[0x004748b4, 0x00474910)`; this wrapper is already source replaced and its
  source uses the public littlefs entry at `0x004cfc2f`.
- `0x0057fab2`, encoding `50f7bcf8`, in the stock `file2xip` path.

Public-wrapper caller fingerprints are address-list SHA-256
`1978380e5587b13b8278a36c2b633df8bd7705618c6f52f9051b34f37bf649d0`,
encoding SHA-256
`28697a9ceed6a8c846b4933f6be779d6807053710e1051eb5cb6b81e9ef6916c`,
and combined-record SHA-256
`b662c8139ba29da85bab1ce18d3cfcf69bcde30261d47e237c5868204fed6d43`.

## Sole outgoing dependency

The routine has one call:

- Call site: `0x004ce480`
- Encoding: `fcf73af9`
- Target: `lfs_max` at `0x004ca6f8`
- Dependency-address SHA-256:
  `716268d273b4f1584da7105c00345a9e7969222a0c12c88dc9d6de96c7149f00`
- Dependency-encoding SHA-256:
  `01d45de3ad484fbffe83aa3c324f5a5f7db5fbbe7f3f14b00672ca987658211a`
- Combined dependency-record SHA-256:
  `e2ea144b5dcc696c5170bd3bb9e579c3c05fc6372248ab12a2568889c4c29314`

Stock `lfs_max` is `[0x004ca6f8, 0x004ca700)`, with bytes
`814200d308007047` and SHA-256
`3caa49d8a68e47b2cd91fcb01cae26b6262c904e8b96d8b3ba35f7fb33d07464`:

```text
004ca6f8  8142  cmp   r1, r0
004ca6fa  00d3  blo   0x004ca6fe
004ca6fc  0800  movs  r0, r1
004ca6fe  7047  bx    lr
```

This is an unsigned maximum, matching upstream `lfs_max`. The existing overlay
already redirects this entry through `replace_littlefs_util_max` to
`open_cfw_littlefs_util_max`, whose source implementation has the same unsigned
semantics. The new routine should preferably call that source symbol directly,
or permit the compiler to inline the exact expression. It does not need to retain
a dependency on unrelated stock code.

## ABI and structure layout

The callable ABI is AAPCS32/Thumb:

- `r0`: `lfs_t *lfs` (unused)
- `r1`: `lfs_file_t *file`
- return `r0`: `lfs_soff_t` (signed 32-bit)
- pointers: 4 bytes; little-endian
- `lfs_size_t`, `lfs_off_t`, `lfs_block_t`: unsigned 32-bit
- `lfs_soff_t`: signed 32-bit

Authenticated layout values:

- `sizeof(lfs_mdir_t) = 0x20`
- `sizeof(lfs_cache_t) = 0x10`
- `sizeof(lfs_file_t) = 0x54`

`lfs_file_t` offsets relevant to this routine and its ABI neighborhood:

| Field | Offset |
|---|---:|
| `next` | `0x00` |
| `id` | `0x04` |
| `type` | `0x06` |
| `m` | `0x08` |
| `ctz.head` | `0x28` |
| `ctz.size` | `0x2c` |
| `flags` | `0x30` |
| `pos` | `0x34` |
| `block` | `0x38` |
| `off` | `0x3c` |
| `cache` | `0x40` |
| `cfg` | `0x50` |

`LFS_F_WRITING` is `0x00020000`. The observed writing branch proves
`LFS_READONLY` was not defined for this build. The authenticated Apollo build
also has `LFS_THREADSAFE`, `LFS_MULTIVERSION`, and trace disabled, with
assertions enabled. The leaf itself is independent of storage callbacks, block
geometry, MSPI details, allocation policy, and disk-format variation.

The default `LFS_FILE_MAX` is `2147483647`, so a valid file size is representable
by the signed `lfs_soff_t` return type.

## Authenticated upstream source

The repository snapshot is:

- Directory: `third_party/littlefs`
- Release: littlefs `v2.10.1`
- Commit: `0494ce7169f06a734a7bd7585f49a9fa91fa7318`
- Tree: `06dd0162169d3cb550cd24a3e34d0e4d02983ad3`
- License: BSD-3-Clause
- Status: authenticated source-equivalent snapshot, not asserted to be the
  device vendor's exact historical checkout

`lfs.c` has size `196,753` bytes and SHA-256
`81a209e8551754d13b24fc0a2b6707fb3b2475e14feba00bf0df722b98a31398`.
The relevant function is lines 3850-3860, byte span `[118350, 118584)`, length
234 bytes, SHA-256
`cec9cc73f29ca37438fee4f95aacdfd75bdb8444c9c4a9c7f6099b589c13975e`:

```c
static lfs_soff_t lfs_file_size_(lfs_t *lfs, lfs_file_t *file) {
    (void)lfs;

#ifndef LFS_READONLY
    if (file->flags & LFS_F_WRITING) {
        return lfs_max(file->pos, file->ctz.size);
    }
#endif

    return file->ctz.size;
}
```

`lfs_util.h` has size `7,954` bytes and SHA-256
`f5d249326646c818e62af3cefefe8a57e7b484446a0f48d1050b95e60925088e`.
The `lfs_max` definition is lines 126-128, byte span `[3073, 3159)`, length
86 bytes, SHA-256
`fa43dc19c29a73ca7c1ecd45173ac597e9bffd7d19258d891536b9a6a57e8abb`.

The recorded Apollo configuration object is at `0x006e83a4`, length 84 bytes,
SHA-256
`f38bd899e180d29ee60609a2452d25c2d2d6c6fef4eb455064e23a6ca7c6e813`.
The repository littlefs provenance verifier passes for both official image
configuration spans.

## Replacement conditions

Proceed with a source replacement if all of the following are preserved:

1. Compile the exact upstream behavior, including the writing-state maximum and
   unsigned comparison semantics.
2. Assert the AAPCS argument/return types, `sizeof(lfs_file_t) == 0x54`, and the
   `ctz.size`, `flags`, and `pos` offsets at compile time.
3. Close the sole dependency through the already source-owned littlefs utility
   maximum (direct source-symbol binding is preferred).
4. Patch only the 24-byte entry span, using the standard Thumb entry branch and
   Thumb NOP fill for the remaining bytes.
5. Pin both direct callers, the sole dependency, the exact stock bytes/hash, and
   the no-interior-reference result in validation.
6. Do not apply the replacement to the bootloader.

Confidence is approximately `0.99` for identity and boundaries, and `0.98` for
integration safety under these conditions. No evidence supports a NO-GO.
