# littlefs revision audit

## Verdict

The official G2 firmware is source-equivalent to the upstream littlefs
`v2.10.1` release. For openCFW, the defensible vendoring pin is:

```text
tag:        v2.10.1
commit:     0494ce7169f06a734a7bd7585f49a9fa91fa7318
lfs.c blob: 7520f2ea7eb1d3d29ab29422ca3d6d0a3057397a
license:    BSD-3-Clause
```

This is an exact source-equivalent pin, not a claim that the original Even
Realities checkout was necessarily the tag commit. A stripped executable
cannot distinguish the tag's `lfs.c` from two later upstream source states
under the recovered configuration. No further G2 disassembly can resolve
that repository-provenance ambiguity.

Primary upstream references:

- [`v2.10.1` source tree](https://github.com/littlefs-project/littlefs/tree/v2.10.1)
- [`v2.10.1` tag commit `0494ce7`](https://github.com/littlefs-project/littlefs/commit/0494ce7169f06a734a7bd7585f49a9fa91fa7318)
- [seek-cache fix `366100b`](https://github.com/littlefs-project/littlefs/commit/366100b1403d2b680ed7a0f3bd0ba982c34d5c07)
- [later bool-cast change `152d030`](https://github.com/littlefs-project/littlefs/commit/152d03043ccab2ca6c454dd6cef43dc072d5810a)
- [later trace-format change `936919d`](https://github.com/littlefs-project/littlefs/commit/936919d13488f307731fa203981ffb62d9e43479)

## Inputs and address mapping

The audit used the untouched official inputs:

| Image | SHA-256 | Mapping |
|---|---|---|
| `ota_s200_firmware_ota.bin` | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` | 32-byte OTA header, installed payload at `0x00438000` |
| `ota_s200_bootloader.bin` | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` | Raw image at `0x00410000` |

Both images contain the same source path:

```text
D:\01_workspace\s200_ap510b_iar_git\third_party\littlefs\lfs.c
```

It is installed at `0x0070C264` in Apollo main and `0x0043168C` in
the bootloader. The paths, diagnostic formats, assertion expressions, line
numbers, and generated instruction shapes establish that both images were
built from one littlefs source generation.

## Configuration ABI

Apollo main has an 84-byte `struct lfs_config` at `0x006E83A4`,
SHA-256
`f38bd899e180d29ee60609a2452d25c2d2d6c6fef4eb455064e23a6ca7c6e813`.
The bootloader copy is at `0x00431070`, SHA-256
`724c351d2136e3c2f10b59ad84d547da4632739ea1f20eb839e9af2cfbd5b6e8`.

Decoded as the upstream `v2.10.1` layout, the words are:

| Offset | Field | Main | Boot |
|---:|---|---:|---:|
| `0x00` | `context` | `0` | `0` |
| `0x04` | `read` | `0x004763B9` | `0x004212D9` |
| `0x08` | `prog` | `0x004763F1` | `0x00421311` |
| `0x0C` | `erase` | `0x00476429` | `0x00421349` |
| `0x10` | `sync` | `0x004764DD` | `0x004213D5` |
| `0x14` | `read_size` | `16` | `16` |
| `0x18` | `prog_size` | `256` | `256` |
| `0x1C` | `block_size` | `4096` | `4096` |
| `0x20` | `block_count` | `3008` | `3008` |
| `0x24` | `block_cycles` | `500` | `500` |
| `0x28` | `cache_size` | `4096` | `4096` |
| `0x2C` | `lookahead_size` | `256` | `256` |
| `0x30` | `compact_thresh` | `0` | `0` |
| `0x34`, `0x38`, `0x3C` | three optional buffers | `0` | `0` |
| `0x40`, `0x44`, `0x48`, `0x4C`, `0x50` | `name_max` through `inline_max` | `0` | `0` |

The exact 84-byte size proves that `LFS_THREADSAFE` is disabled (there
are no `lock` and `unlock` pointers) and `LFS_MULTIVERSION` is disabled
(there is no trailing `disk_version`). The presence of all default
debug, warning, error, and assertion strings proves those diagnostics are
enabled. No littlefs trace strings are present, so `LFS_YES_TRACE` is
disabled. Null optional buffers plus the allocation paths establish dynamic
buffer allocation.

The selected upstream header defines library version `2.10` and on-disk
version `2.1`. Because multiversion is disabled, openCFW must preserve the
normal `v2.10.1` disk-writing behavior.

## Assertion-line fingerprint

Capstone 5.0.7 was used to scan halfword-aligned Thumb instructions for calls
to the two assertion helpers (`0x004D09B4` in main and `0x00415734` in the
bootloader). For each call, the preceding `r0`, `r1`, and `r2` assignments
recover the expression pointer, source-file pointer, and IAR line constant.

Apollo main contains 57 littlefs assertion calls with these source lines:

```text
107 118 179 183 221 232 233 262 276 278 965 2084 2248 2261
2335 2555 3556 3659 4216 4218 4219 4220 4225 4226 4227 4231
4232 4233 4236 4240 4248 4255 4257 4262 4264 4266 4296 4308
4314 4320 4326 4329 4331 4335 4396 4892 4893 4965 6119 6155
6171 6189 6207 6225 6258 6287 6318
```

The bootloader's linked subset contains 38 calls:

```text
3556 3659 4216 4218 4219 4220 4225 4226 4227 4231 4232 4233
4236 4240 4248 4255 4257 4262 4264 4266 4296 4308 4314 4320
4326 4329 4331 4335 4396 4892 4893 4965 6119 6155 6189 6207
6225 6318
```

Every recovered expression and line equals upstream `v2.10.1`. Selected
tag discriminators are:

| Assertion expression | G2 | `v2.9.3` | `v2.10.0` | `v2.10.1` | `v2.10.2` | `v2.11.0` |
|---|---:|---:|---:|---:|---:|---:|
| compact threshold lower bound | 4255 | 4208 | 4260 | 4255 | 4253 | 4257 |
| compact threshold upper bound | 4257 | 4210 | 4262 | 4257 | 4255 | 4259 |
| mount block-count check | 4396 | 4340 | 4401 | 4396 | 4394 | 4398 |
| first orphan-count invariant | 4892 | 4834 | 4897 | 4892 | 4890 | 4894 |
| demove tag invariant | 4965 | 4907 | 4970 | 4965 | 4963 | 4967 |
| directory-not-open invariant | 6318 | 6260 | 6323 | 6318 | 6316 | 6344 |

The complete 38-line fingerprint was compared against all 38 official
`v2.*` tags; only `v2.10.1` matched. It also confirms the seek-from-end
cache fix merged by the tag; `v2.10.0` has the pre-fix five-line offset.

## Why the original checkout commit is not recoverable

A history-wide comparison of the official upstream `v2` branch found three
`lfs.c` source states with the complete 38-line boot fingerprint:

| Source-changing commit | `lfs.c` Git blob | Relevant difference |
|---|---|---|
| `366100b1403d2b680ed7a0f3bd0ba982c34d5c07` | `7520f2ea7eb1d3d29ab29422ca3d6d0a3057397a` | Exact tree used by tag `v2.10.1` |
| `152d03043ccab2ca6c454dd6cef43dc072d5810a` | `00a0a5450b64e81de97e82be65c44ab1695ab373` | Adds an explicit `int8_t` cast to a value already converted to the same parameter type |
| `936919d13488f307731fa203981ffb62d9e43479` | `416ec7299046f1c31011c4f0fcbb654ff4e5e59f` | Reverts that cast and changes only a disabled `LFS_TRACE` format |

The G2 build timestamp, `2025-04-28T13:29:15Z`, postdates all three.
Timestamp ordering therefore does not eliminate any of them.

As a normalized code experiment, each candidate and both adjacent tags were
compiled for Cortex-M55 Thumb with Apple Clang 21 at `-Oz`, using identical
declarations, assertions, diagnostics, no thread-safe or multiversion field,
and trace disabled. The full relocatable objects were:

| Source | Object SHA-256 |
|---|---|
| `v2.10.0` | `6261ab2ba3b72b74dad5e38dec04a9b402fe66316cf4d7b35d9e3e7b618422a5` |
| `v2.10.1` | `46a202b18e71286c6bbc79202de21c615462eca714ec84d8442f5aab2d797f90` |
| `152d030` | `46a202b18e71286c6bbc79202de21c615462eca714ec84d8442f5aab2d797f90` |
| `936919d` | `46a202b18e71286c6bbc79202de21c615462eca714ec84d8442f5aab2d797f90` |
| `v2.10.2` | `22225d7736116a3ae4c02e74d4e3ad0c004085526310f9ab13e0f0ce34a797f4` |

The three candidates are not just behaviorally close: under the recovered
preprocessor configuration their complete generated objects are
byte-identical. The relevant G2 `lfs_dir_orphaningcommit` sequence at
`0x004CD280...0x004CD28D` also performs the same unsigned-byte extraction,
negation, signed-byte conversion, and call required by all three.

An exact IAR rebuild of that 14-byte span could test compiler equivalence for
the explicit-cast state, but it still could not distinguish `366100b` from
`936919d`: their executable source is the same when trace is disabled.
Recovering the historical checkout would require an external source-lock
file, submodule revision, original source archive, map/debug object, or
build-system provenance. It cannot be recovered from this stripped binary.

## Vendoring and validation decision

Use the released tag `v2.10.1` at commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. Preserve the upstream
BSD-3-Clause license and pin these file hashes:

| File | SHA-256 |
|---|---|
| `lfs.c` | `81a209e8551754d13b24fc0a2b6707fb3b2475e14feba00bf0df722b98a31398` |
| `lfs.h` | `ee44e99d6b19119b3e577b969b80c9d5e6f96410c9593794afddf6d4b314c486` |
| `lfs_util.c` | `f2fbde533670560434bd9f5a547174cc7c5a4670a02c47b4bd85180dced8b2ec` |
| `lfs_util.h` | `f5d249326646c818e62af3cefefe8a57e7b484446a0f48d1050b95e60925088e` |
| `LICENSE.md` | `0cb4ff1daf5fdc1359c6a6ee3116092f08fc100c9d58b1b77ab17bfd801f856d` |

Keep the main and boot callback/configuration tables in separate G2 port
files. Do not apply post-`v2.10.1` fixes opportunistically during the first
replacement; such changes should be isolated, justified patches after
format compatibility is established.

Before redirecting `lfs_mount`, `lfs_format`, or any mutating API on
hardware:

1. Capture a complete external-flash image.
2. Mount a copy read-only with the pinned upstream core and recovered
   geometry.
3. Verify the superblock, disk version, directory tree, file contents, and
   `lfs_fs_stat` results against the official implementation.
4. Exercise create/write/sync/rename/remove and power-loss cases only on
   disposable image copies.
5. Permit device formatting only after byte-level and behavioral golden-image
   tests pass.

## Reproduction commands

The upstream audit used only the official repository:

```sh
git clone https://github.com/littlefs-project/littlefs.git
git show v2.10.1:lfs.c
git ls-tree v2.10.1 lfs.c lfs.h lfs_util.c lfs_util.h
git diff v2.10.0..v2.10.1 -- lfs.c
git diff v2.10.1..v2.10.2 -- lfs.c
git log origin/v2 -- lfs.c
```

The normalized comparison used Apple Clang 21.0.0 and the following
invocation for each revision. `audit-include` contained declarations-only
freestanding `string.h`, `stdlib.h`, `stdio.h`, `inttypes.h`, and an
`assert` macro; it did not contain any littlefs implementation:

```sh
xcrun clang \
  --target=arm-none-eabi -mcpu=cortex-m55 -mthumb -Oz \
  -ffreestanding -nostdinc \
  -I audit-include -isystem "$(xcrun clang -print-resource-dir)/include" \
  -ffunction-sections -fdata-sections \
  -c lfs.c -o "lfs-${revision}.o"
```

The firmware input and configuration hashes are reproducible with:

```sh
shasum -a 256 \
  openCFW/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin \
  openCFW/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin

dd if=openCFW/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin \
  bs=1 skip=$((0x6e83a4-0x438000+32)) count=84 2>/dev/null |
  shasum -a 256

dd if=openCFW/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin \
  bs=1 skip=$((0x431070-0x410000)) count=84 2>/dev/null |
  shasum -a 256
```
