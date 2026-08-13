# G2 littlefs `lfs_alloc_drop` source-boundary audit

Status: source-integrated for Apollo main and the bootloader

Scope: official G2 package `2.2.6.10`; authenticated binary/source analysis,
host/target validation, and redirect-safety research; no signing, flashing,
external-flash access, or hardware use

## Result

The littlefs v2.10.1 private `lfs_alloc_drop` function is unequivocally
identified in both official images:

| Property | Apollo main | Bootloader |
|---|---:|---:|
| Entry | `0x004CB0E6` | `0x00410DEE` |
| End-exclusive range | `[0x004CB0E6,0x004CB0F6)` | `[0x00410DEE,0x00410DFE)` |
| Installed-payload offset | `0x000930E6` | `0x00000DEE` |
| Package/file offset | `0x00093106` | `0x00000DEE` |
| Size | 16 bytes | 16 bytes |
| Bytes | `80 B5 00 21 81 65 00 21 C1 65 FF F7 F6 FF 01 BD` | same |
| SHA-256 | `55b7d516bb75d425ebbc077729c8c03aef31b93897d422450084cfed8a771f66` | same |
| Direct entry callers | 2 | 2 |
| Non-linking wide/narrow entries | none | none |
| Stored entry/interior pointers | none | none |
| External interior entries | none | none |
| Outgoing calls | one, `lfs_alloc_ckpoint` | one, `lfs_alloc_ckpoint` |

The official bodies, the adjacent recovered checkpoint leaf, and pristine
littlefs v2.10.1 agree on the complete operation:

1. store zero to `lfs_t.lookahead.size` at offset `0x58`;
2. store zero to `lfs_t.lookahead.next` at offset `0x5c`;
3. copy `lfs_t.block_count` at offset `0x6c` to
   `lfs_t.lookahead.ckpoint` at offset `0x60`.

The function has no configuration, buffer, block-device callback, allocator,
MSPI, or flash dependency. Its only code dependency is the already
source-owned `lfs_alloc_ckpoint` leaf immediately before it in both images.
The isolated candidate closes that dependency by keeping the exact checkpoint
assignment source-local and inline. It is therefore a defensible next source
boundary for both images.

## Authoritative inputs

### Official images

| Image | Bytes | SHA-256 | Mapping |
|---|---:|---|---|
| `ota_s200_firmware_ota.bin` | `3,523,396` | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` | 32-byte preamble, payload at `0x00438000` |
| Apollo-main installed payload | `3,523,364` | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` | package bytes after preamble |
| `ota_s200_bootloader.bin` | `148,599` | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` | raw image at `0x00410000` |

### Upstream source

The authenticated source is the repository's pristine
[`../../third_party/littlefs`](../../third_party/littlefs) snapshot:

| Property | Value |
|---|---|
| Selected release | littlefs `v2.10.1` |
| Commit | `0494ce7169f06a734a7bd7585f49a9fa91fa7318` |
| Tree | `06dd0162169d3cb550cd24a3e34d0e4d02983ad3` |
| License | BSD-3-Clause |
| `lfs.c` SHA-256 | `81a209e8551754d13b24fc0a2b6707fb3b2475e14feba00bf0df722b98a31398` |
| `lfs.h` SHA-256 | `ee44e99d6b19119b3e577b969b80c9d5e6f96410c9593794afddf6d4b314c486` |
| `lfs_util.c` SHA-256 | `f2fbde533670560434bd9f5a547174cc7c5a4670a02c47b4bd85180dced8b2ec` |

This is an exact source-equivalent release pin; it is not a claim about the
name or revision of the stripped vendor checkout.

## Exact upstream boundary

The pristine implementation at `lfs.c:616...627` is:

```c
static void lfs_alloc_ckpoint(lfs_t *lfs) {
    lfs->lookahead.ckpoint = lfs->block_count;
}

// drop the lookahead buffer, this is done during mounting and failed
// traversals in order to avoid invalid lookahead state
static void lfs_alloc_drop(lfs_t *lfs) {
    lfs->lookahead.size = 0;
    lfs->lookahead.next = 0;
    lfs_alloc_ckpoint(lfs);
}
```

Both official `lfs_alloc_drop` bodies decode identically:

```text
push {r7, lr}
movs r1, #0
str  r1, [r0, #0x58]
movs r1, #0
str  r1, [r0, #0x5c]
bl   lfs_alloc_ckpoint
pop  {r0, pc}
```

The call at entry plus `0x0a` targets the adjacent authenticated checkpoint
leaf:

| Image | Call site | Target | Target bytes |
|---|---:|---:|---|
| Apollo main | `0x004CB0F0` | `0x004CB0E0` | `C1 6E 01 66 70 47` |
| Bootloader | `0x00410DF8` | `0x00410DE8` | same |

The target leaf loads a word at `0x6c`, stores it at `0x60`, and returns.
Together the two bodies authenticate every field access required by the
upstream source. The unusual stock epilogue restores the saved padding
register into `r0`, but `lfs_alloc_drop` returns `void` and `r0` is
caller-saved under the Arm ABI. The candidate is not required to reproduce
that irrelevant clobber.

## `lfs_t` ABI and configuration

The default v2.10.1 base `lfs_t` is `0x80` bytes on the 32-bit Apollo target.
The selected substructure is:

| Field | Offset | Size |
|---|---:|---:|
| `lookahead.start` | `0x54` | 4 |
| **`lookahead.size`** | **`0x58`** | **4** |
| **`lookahead.next`** | **`0x5c`** | **4** |
| **`lookahead.ckpoint`** | **`0x60`** | **4** |
| `lookahead.buffer` | `0x64` | 4 |
| `cfg` | `0x68` | 4 |
| **`block_count`** | **`0x6c`** | **4** |

The candidate has target-only static assertions for four-byte pointers and
scalars, the cache/gstate/lookahead substructure sizes, the `0x80` base
structure size, and all five relevant offsets.

Both authenticated 84-byte configuration objects retain the previously
recovered default ABI:

| Setting | Apollo main / bootloader |
|---|---:|
| `read_size` | 16 |
| `prog_size` | 256 |
| `block_size` | 4096 |
| `block_count` | 3008 |
| `block_cycles` | 500 |
| `cache_size` | 4096 |
| `lookahead_size` | 256 |
| optional buffers and limit overrides | zero |

`lfs_alloc_drop` does not dereference `cfg`; the configuration objects
corroborate the ABI but are not runtime dependencies of this boundary.

## Complete caller and reference topology

Both complete images were scanned at every halfword for Thumb-2 `BL` and
non-linking `B.W`, at every halfword for narrow unconditional, conditional,
`CBZ`, and `CBNZ` branches, and at every byte for stored even or Thumb entry
and interior addresses.

### Apollo main

| Call site | Encoding | Upstream context |
|---:|---|---|
| `0x004CB17A` | `FF F7 B4 FF` | `lfs_alloc_scan`: discard invalid lookahead state after traversal failure |
| `0x004CF266` | `FB F7 3E FF` | `lfs_mount_`: initialize lookahead after choosing `seed % block_count` |

The ordered caller-address list hashes to
`1bd8116bcd28734549add50348fa07c27f848a5fc5fb3f83d9805c92459ea819`;
the concatenated call instructions hash to
`349ba2c5ad9de3a017b91cd07056f91dbcf6eaf968806a5577f95f08be65a2d0`.

### Bootloader

| Call site | Encoding | Upstream context |
|---:|---|---|
| `0x00410E82` | `FF F7 B4 FF` | `lfs_alloc_scan`: traversal-failure reset |
| `0x0041493E` | `FC F7 56 FA` | `lfs_mount_`: mount-time initialization |

The ordered caller-address list hashes to
`a7b1297b66cff8986f860dc5df9c7d5612df6e46a930dfd9b1f477efbacffcef`;
the concatenated call instructions hash to
`db918078f3ebe1a093a99485e95ddc67da982e5703e77e24248b35d2e5e2c9b4`.

For each image:

- exactly the two listed `BL` instructions target the entry;
- no non-linking wide or narrow branch targets the entry;
- no external branch or call targets any interior halfword;
- no stored even or Thumb pointer names the entry or an interior address;
- no vector, callback table, literal, data object, or shared tail is owned;
- the only outgoing edge is the authenticated adjacent checkpoint call.

The stock function is one 16-byte, single-basic-block boundary. Apollo main
and boot need image-specific redirects, but they can share the same candidate
source.

## Closed target candidate

The isolated source keeps an inline source-local equivalent of
`lfs_alloc_ckpoint`. Under the project's Cortex-M55 Thumb `-Oz` flags, its
complete `.text` is:

```text
00 21 C1 65 81 65 C1 6E 01 66 70 47
```

This decodes to:

```text
movs r1, #0
str  r1, [r0, #0x5c]
str  r1, [r0, #0x58]
ldr  r1, [r0, #0x6c]
str  r1, [r0, #0x60]
bx   lr
```

The compiler reverses the two independent zero stores, which is
observationally equivalent for a valid `lfs_t`. The target object:

- has one 12-byte function symbol;
- hashes to
  `e5e78109621631cb174d82b06ba2542dfa669e1919c3d80982ab059844e5c4f8`;
- has zero relocations and zero undefined symbols;
- has no literal pool, stack frame, call, data object, or opaque callback;
- is four bytes smaller than the official call-based body.

This deliberate dependency closure is preferable for an isolated candidate.
An integrated build may instead call the already source-owned checkpoint
function if preserving the upstream private call graph is useful. Either
choice has the same defined C behavior.

## Focused semantic validation

The host candidate is compared with a separately compiled pristine v2.10.1
`lfs.c`/`lfs_util.c` oracle. Tests cover:

- zero, small, official `3008`, signed-boundary, and `UINT32_MAX` values;
- multiple complete-structure byte patterns;
- independent initial `size`, `next`, `checkpoint`, and `block_count`;
- exact zeroing of `size` and `next`;
- exact 32-bit propagation from `block_count` to `checkpoint`;
- a checksum over the complete structure;
- a checksum excluding only the three permitted destination words;
- repeated-call idempotence;
- native host layout agreement with pristine upstream;
- exact target symbol, bytes, opcodes, offsets, and dependency closure;
- official image/package hashes, stock span, checkpoint target, and exhaustive
  dual-image topology.

The focused suite passes all eight tests.

## Files

- [`runtime_littlefs_alloc_drop.c`](../../components/apollo_main/core_overlay/runtime_littlefs_alloc_drop.c)
- [`runtime_littlefs_alloc_drop_host.c`](../../tests/fixtures/runtime_littlefs_alloc_drop_host.c)
- [`runtime_littlefs_alloc_drop_upstream_oracle_host.c`](../../tests/fixtures/runtime_littlefs_alloc_drop_upstream_oracle_host.c)
- [`test_runtime_littlefs_alloc_drop.py`](../../tests/test_runtime_littlefs_alloc_drop.py)

The Apollo-main source SHA-256 is
`b5f6394bc8999324f69dd307d809aa9d8e7ac4f0d8fb09822a9b141c64ad797d`.
No overlay, package manifest, aggregate evidence document, coverage table, or
build artifact was modified.

## Redirect-safety decision

Both official entries are structurally safe for a future redirect:

- the complete boundary is 16 bytes;
- every entry and interior reference is closed;
- both caller purposes match pristine upstream;
- the only outgoing function is already source-owned;
- the closed candidate reproduces the complete defined state transition;
- no image-specific data or hardware port is acquired.

An eventual integration must allocate reachable Thumb destinations
separately for Apollo main and bootloader, replace each complete entry while
preserving its adjacent checkpoint and lookahead functions, retain the ABI
assertions, and rerun assembled-image topology/package validation. This audit
does not authorize signing, flashing, formatting, or hardware mutation.
