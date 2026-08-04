# G2 littlefs `lfs_alloc_ckpoint` source-boundary audit

Status: source-integrated for both Apollo main and the bootloader in official
G2 package `2.2.6.10`

Scope: Apollo-main application and bootloader; authenticated binary/source
analysis, host/target validation, and offline package assembly; no signing,
flashing, external-flash access, or hardware use

## Result

The littlefs v2.10.1 `lfs_alloc_ckpoint` private leaf is recovered in both
official images:

| Property | Apollo main | Bootloader |
|---|---:|---:|
| Entry | `0x004CB0E0` | `0x00410DE8` |
| End-exclusive range | `[0x004CB0E0,0x004CB0E6)` | `[0x00410DE8,0x00410DEE)` |
| Installed-payload offset | `0x000930E0` | `0x00000DE8` |
| Package/file offset | `0x00093100` | `0x00000DE8` |
| Size | 6 bytes | 6 bytes |
| Bytes | `C1 6E 01 66 70 47` | same |
| SHA-256 | `74d41d77541fa368dfc90160c9fc3a8dfd62d891ea72f29ef9c115465b71a32c` | same |
| Direct callers | 6 | 6 |
| Wide non-linking branches | none | none |
| Narrow branches | none | none |
| Stored entry/interior pointers | none | none |
| External interior entries | none | none |
| Calls/literals/relocations owned | none | none |

The official body and authenticated upstream layout independently agree that:

- `lfs_t.lookahead.ckpoint` is at offset `0x60`;
- `lfs_t.block_count` is at offset `0x6c`;
- the function copies the complete 32-bit `block_count` value to
  `lookahead.ckpoint`;
- no configuration pointer is dereferenced;
- no block-device, cache-buffer, allocator callback, or MSPI operation is
  acquired by this boundary.

Both copies have closed direct-entry topology and are safely redirectable as
complete six-byte entries. Main and boot require separate redirects because
their stock and overlay-placement addresses differ, but they can use the same
source implementation.

## Authoritative inputs

### Official images

| Image | Bytes | SHA-256 | Mapping |
|---|---:|---|---|
| `ota_s200_firmware_ota.bin` | `3,523,396` | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` | 32-byte preamble, payload at `0x00438000` |
| Apollo-main installed payload | `3,523,364` | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` | package bytes after preamble |
| `ota_s200_bootloader.bin` | `148,599` | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` | raw image at `0x00410000` |

### Upstream source

The authenticated snapshot is [`third_party/littlefs`](../../third_party/littlefs):

| Property | Value |
|---|---|
| Selected release | littlefs `v2.10.1` |
| Commit | `0494ce7169f06a734a7bd7585f49a9fa91fa7318` |
| Tree | `06dd0162169d3cb550cd24a3e34d0e4d02983ad3` |
| License | BSD-3-Clause |
| `lfs.c` SHA-256 | `81a209e8551754d13b24fc0a2b6707fb3b2475e14feba00bf0df722b98a31398` |
| `lfs.h` SHA-256 | `ee44e99d6b19119b3e577b969b80c9d5e6f96410c9593794afddf6d4b314c486` |
| `lfs_util.c` SHA-256 | `f2fbde533670560434bd9f5a547174cc7c5a4670a02c47b4bd85180dced8b2ec` |

As established by the broader revision audit, this is an exact
source-equivalent release pin. It does not overclaim the identity of the
original private checkout.

## Exact source and binary identity

The upstream implementation at `lfs.c:616...618` is:

```c
static void lfs_alloc_ckpoint(lfs_t *lfs) {
    lfs->lookahead.ckpoint = lfs->block_count;
}
```

Both official bodies decode identically:

```text
ldr  r1, [r0, #0x6c]
str  r1, [r0, #0x60]
bx   lr
```

The 16-bit encodings establish the access widths and offsets without relying
on pseudocode:

| Bytes | Instruction class | Base | Value | Scaled immediate |
|---|---|---:|---:|---:|
| `C1 6E` | Thumb `LDR (immediate)` | `r0` | `r1` | `27 * 4 = 0x6c` |
| `01 66` | Thumb `STR (immediate)` | `r0` | `r1` | `24 * 4 = 0x60` |
| `70 47` | `BX` | `lr` | — | — |

The ABI contract is one 32-bit pointer in `r0`, one 32-bit load, one 32-bit
store, and return through `lr`. The function has no stack frame and changes
no register required to be callee-saved.

A normalized Cortex-M55 Thumb `-Oz` compilation of the isolated source emits
the exact official `C1 6E 01 66 70 47`. Its complete `.text`:

- is 6 bytes;
- hashes to
  `74d41d77541fa368dfc90160c9fc3a8dfd62d891ea72f29ef9c115465b71a32c`;
- contains one six-byte function symbol;
- has zero relocations;
- has zero undefined symbols;
- contains no literal pool, veneer, call, or data object.

## `lfs_t` ABI derivation

The default v2.10.1 `lfs_t` base layout uses 32-bit littlefs scalars and, on
Apollo510, 32-bit pointers:

| Field | Offset | Size |
|---|---:|---:|
| `rcache` | `0x00` | `0x10` |
| `pcache` | `0x10` | `0x10` |
| `root[2]` | `0x20` | `0x08` |
| `mlist` | `0x28` | `0x04` |
| `seed` | `0x2c` | `0x04` |
| `gstate` | `0x30` | `0x0c` |
| `gdisk` | `0x3c` | `0x0c` |
| `gdelta` | `0x48` | `0x0c` |
| `lookahead.start` | `0x54` | `0x04` |
| `lookahead.size` | `0x58` | `0x04` |
| `lookahead.next` | `0x5c` | `0x04` |
| **`lookahead.ckpoint`** | **`0x60`** | **`0x04`** |
| `lookahead.buffer` | `0x64` | `0x04` |
| `cfg` | `0x68` | `0x04` |
| **`block_count`** | **`0x6c`** | **`0x04`** |
| `name_max` | `0x70` | `0x04` |
| `file_max` | `0x74` | `0x04` |
| `attr_max` | `0x78` | `0x04` |
| `inline_max` | `0x7c` | `0x04` |

The base structure is `0x80` bytes. Optional `LFS_MIGRATE` state, when
compiled, is appended after these fields and cannot change either selected
offset. The official six-caller topology contains the default non-migration
call set and no optional migration caller.

The candidate contains target-only static assertions for:

- four-byte pointers and littlefs scalar width;
- `lfs_cache_t == 0x10`;
- `lfs_gstate_t == 0x0c`;
- the lookahead substructure size `0x14`;
- base `lfs_t == 0x80`;
- `lookahead == 0x54`;
- `lookahead.ckpoint == 0x60`;
- `block_count == 0x6c`.

These assertions compile before the exact six-byte body is measured.

## Official binary layout corroboration

The surrounding allocator cluster is byte-identical between the two
independently linked images:

| Source boundary | Apollo-main range | Boot range | Bytes | SHA-256 |
|---|---|---|---:|---|
| preceding disk-version-minor tail | `[0x004CB0D8,0x004CB0E0)` | `[0x00410DE0,0x00410DE8)` | 8 | `4a6d9e118e5aa8e7142d434ea2b710efaa2cb2b34c03d88d68b35c9e4d92216b` |
| **`lfs_alloc_ckpoint`** | `[0x004CB0E0,0x004CB0E6)` | `[0x00410DE8,0x00410DEE)` | **6** | `74d41d77541fa368dfc90160c9fc3a8dfd62d891ea72f29ef9c115465b71a32c` |
| `lfs_alloc_drop` | `[0x004CB0E6,0x004CB0F6)` | `[0x00410DEE,0x00410DFE)` | 16 | `55b7d516bb75d425ebbc077729c8c03aef31b93897d422450084cfed8a771f66` |
| `lfs_alloc_lookahead` | `[0x004CB0F6,0x004CB12E)` | `[0x00410DFE,0x00410E36)` | 56 | `58285c138461a673be0bed2c5376f8d739e40e2aea753ad05d5061bfbc9265cf` |

This cluster proves the complete contiguous lookahead layout in executable
code:

- `lfs_alloc_drop` stores zero at `0x58` and `0x5c`, then calls the selected
  helper;
- `lfs_alloc_lookahead` reads `start` at `0x54`, `size` at `0x58`, and
  `buffer` at `0x64`;
- it reads `block_count` at `0x6c` twice for wrapping arithmetic;
- `lfs_alloc_scan`, immediately afterward, reads `ckpoint` at `0x60`, `cfg`
  at `0x68`, and again uses `block_count` at `0x6c`;
- the later allocator loop increments `next` at `0x5c` and decrements
  `ckpoint` at `0x60`.

Thus the selected field names and offsets are supported by the upstream type
layout, the selected body, and adjacent official functions using every
neighboring member.

## Authenticated G2 littlefs configuration

The official configuration objects remain the recovered 84-byte,
21-word, non-threadsafe, non-multiversion ABI:

| Image | Address | SHA-256 |
|---|---:|---|
| Apollo main | `0x006E83A4` | `f38bd899e180d29ee60609a2452d25c2d2d6c6fef4eb455064e23a6ca7c6e813` |
| Bootloader | `0x00431070` | `724c351d2136e3c2f10b59ad84d547da4632739ea1f20eb839e9af2cfbd5b6e8` |

Both contain:

| Setting | Value |
|---|---:|
| `read_size` | 16 |
| `prog_size` | 256 |
| `block_size` | 4096 |
| `block_count` | 3008 |
| `block_cycles` | 500 |
| `cache_size` | 4096 |
| `lookahead_size` | 256 |
| optional buffers and limit overrides | zero |

The configuration establishes the recovered scalar/pointer ABI and normal
runtime block count. The leaf nevertheless copies whatever 32-bit value is
currently in `lfs_t.block_count`; it does not read the configuration object
or hardcode 3008.

## Complete dual-image topology

Both complete images were scanned at every halfword for Thumb-2 `BL` and
non-linking `B.W`, at every halfword for narrow unconditional, conditional,
`CBZ`, and `CBNZ` branches, and at every byte for stored even or Thumb entry
and interior addresses.

### Apollo main

| Call site | Encoding | Upstream context |
|---:|---|---|
| `0x004CB0F0` | `FF F7 F6 FF` | `lfs_alloc_drop` |
| `0x004CD400` | `FD F7 6E FE` | `lfs_mkdir_` |
| `0x004CDE38` | `FD F7 52 F9` | `lfs_file_outline` |
| `0x004CE1F4` | `FC F7 74 FF` | `lfs_file_flushedwrite` |
| `0x004CE256` | `FC F7 43 FF` | `lfs_file_flushedwrite` |
| `0x004CEE80` | `FC F7 2E F9` | `lfs_format_` |

The ordered caller-address list hashes to
`828e65cef40bf49a49b33ea1862e6c0dad727e58dba5704905674e88a6a4ffd8`.
The concatenated call instructions hash to
`35e674b64e228e851c69f3c0e5b0a8e2ace176c2f59f34a9717e8fe435ece924`.

### Bootloader

| Call site | Encoding | Upstream context |
|---:|---|---|
| `0x00410DF8` | `FF F7 F6 FF` | `lfs_alloc_drop` |
| `0x00413004` | `FD F7 F0 FE` | `lfs_mkdir_` |
| `0x00413988` | `FD F7 2E FA` | `lfs_file_outline` |
| `0x00413D44` | `FD F7 50 F8` | `lfs_file_flushedwrite` |
| `0x00413DA6` | `FD F7 1F F8` | `lfs_file_flushedwrite` |
| `0x00414564` | `FC F7 40 FC` | `lfs_format_` |

The ordered caller-address list hashes to
`0b8d579b980802287ea289ed468130308d20ad59838a3e31e596fd993ba48fa4`.
The concatenated call instructions hash to
`db2e6169825dcaec817f284ed47d08a02e9bda9ae163fd26c4053561579eaca9`.

For each complete image:

- exactly the six listed `BL` instructions target the entry;
- no non-linking wide branch targets the entry;
- no narrow branch targets the entry or either interior instruction;
- no wide call or branch externally targets `entry+2` or `entry+4`;
- no stored even or Thumb pointer names the entry or interior;
- no vector, callback table, jump table, literal, or data reference exists.

Rizin full-image reference analysis independently recovers a six-byte,
single-basic-block function with six code xrefs, zero call refs, zero data
refs, zero outgoing edges, and no stack frame in each image. Its xref lists
match the exhaustive decoder scans above exactly.

No caller rewrite, function-pointer rebinding, shared-tail preservation, or
interior veneer is required. A complete entry redirect preserves every call
edge and each caller's link register.

## Pristine semantics

`lfs_alloc_ckpoint` marks every block currently known to the mounted
filesystem as available for future allocation scanning. Its semantics are a
plain 32-bit assignment:

1. read `lfs->block_count`;
2. store the unchanged value into `lfs->lookahead.ckpoint`;
3. leave every other byte of `lfs_t` unchanged.

It does not validate the value, clamp it to the configured block count, reset
`lookahead.start`, `size`, or `next`, touch the bitmap buffer, or begin a
scan. Those actions belong to its callers and neighboring allocator
functions.

The focused host test compares the isolated candidate against a separately
compiled pristine v2.10.1 `lfs.c` oracle for:

- three complete-memory initialization patterns;
- zero, one, the official 3008-block count, both signed-bit boundaries, and
  `UINT32_MAX`;
- complete structure checksums;
- checksums excluding the only permitted four-byte destination;
- repeated-call idempotence;
- native host layout agreement between the reproduced and upstream types.

## Isolated candidate

The source and validation files are:

- [`runtime_littlefs_alloc_ckpoint.c`](../../components/apollo_main/core_overlay/runtime_littlefs_alloc_ckpoint.c)
- [`runtime_littlefs_alloc_ckpoint_host.c`](../../tests/fixtures/runtime_littlefs_alloc_ckpoint_host.c)
- [`runtime_littlefs_alloc_ckpoint_upstream_oracle_host.c`](../../tests/fixtures/runtime_littlefs_alloc_ckpoint_upstream_oracle_host.c)
- [`test_runtime_littlefs_alloc_ckpoint.py`](../../tests/test_runtime_littlefs_alloc_ckpoint.py)

The candidate source SHA-256 is
`16acfce3da9211512631113cb717abd012a0d551ceed36c57b4af300c21e7395`.
It is freestanding and deliberately not included by an overlay or manifest.

## Redirect-safety decision

Both official entries are structurally safe to redirect:

- the complete function boundary is six bytes;
- the replacement target body is exact;
- all entry callers are direct and authenticated;
- there are no interior entries or stored pointers;
- no literal or data ownership crosses the boundary;
- the only state dependency is the fully authenticated `lfs_t` layout;
- the operation is independent of the block/MSPI port.

An eventual integration must still:

1. allocate a valid reachable Thumb target separately for each image;
2. replace each complete six-byte stock entry without changing neighboring
   bytes;
3. preserve the target `lfs_t` static assertions and exact six-byte body;
4. rerun the whole-image topology and assembled-image checks;
5. avoid interpreting source replacement as permission to format, erase, or
   mutate hardware flash.

No hardware access is needed to establish this source boundary.
