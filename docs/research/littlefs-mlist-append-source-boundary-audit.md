# G2 littlefs `lfs_mlist_append` source-boundary audit

Status: source-integrated in both Apollo-main and bootloader production
overlays

Scope: official G2 package `2.2.6.10`; authenticated binary/source analysis,
host/target validation, redirect-safety research, and subsequent dual-image
source-overlay integration; no signing, flashing, external-flash access, or
hardware use

## Result

The private littlefs v2.10.1 `lfs_mlist_append` helper is unequivocally
identified in both official images:

| Property | Apollo main | Bootloader |
|---|---:|---:|
| Entry | `0x004CB0BC` | `0x00410DC4` |
| End-exclusive range | `[0x004CB0BC,0x004CB0C4)` | `[0x00410DC4,0x00410DCC)` |
| Installed-payload offset | `0x000930BC` | `0x00000DC4` |
| Package/file offset | `0x000930DC` | `0x00000DC4` |
| Size | 8 bytes | 8 bytes |
| Bytes | `82 6A 0A 60 81 62 70 47` | same |
| SHA-256 | `e3ed290e4e62fc9cce34b0530080dbc08efbca65f80ca1b7d182e18bb20c24b9` | same |
| Direct callers | 2 | 2 |
| Non-linking or stored entries | none | none |
| External interior entries | none | none |
| Outgoing calls/literals | none | none |

The complete operation is visible in the three memory instructions:

1. load the old `lfs_t.mlist` head at offset `0x28`;
2. store that pointer to `mlist->next` at offset `0`;
3. store `mlist` as the new `lfs_t.mlist` head.

That is the complete pristine v2.10.1 source body. The only ABI dependencies
are 32-bit pointers, `offsetof(lfs_t, mlist) == 0x28`, and
`offsetof(struct lfs_mlist, next) == 0`. Both official bodies and their two
call contexts independently authenticate those offsets. The helper has no
configuration, allocation, flash, filesystem-format, callback, or MSPI
dependency.

## Authoritative inputs

### Official images

| Image | Bytes | SHA-256 | Mapping |
|---|---:|---|---|
| `ota_s200_firmware_ota.bin` | `3,523,396` | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` | 32-byte preamble, payload at `0x00438000` |
| Apollo-main installed payload | `3,523,364` | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` | package bytes after preamble |
| `ota_s200_bootloader.bin` | `148,599` | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` | raw image at `0x00410000` |

### Upstream source

The comparator is the authenticated pristine
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

## Exact source boundary

Pristine v2.10.1 `lfs.c:531...534` is:

```c
static void lfs_mlist_append(lfs_t *lfs, struct lfs_mlist *mlist) {
    mlist->next = lfs->mlist;
    lfs->mlist = mlist;
}
```

Both official bodies decode identically:

```text
ldr r2, [r0, #0x28]
str r2, [r1]
str r1, [r0, #0x28]
bx  lr
```

Under the Arm procedure-call ABI:

- `r0` is `lfs_t *lfs`;
- `r1` is `struct lfs_mlist *mlist`;
- `r2` holds the old head temporarily;
- the function returns `void`.

No instruction lies outside the two upstream assignments and return. There is
no prologue, epilogue stack adjustment, literal pool, branch, shared tail, or
fall-through ownership.

The neighboring dual-image generation is also identical:

| Function | Apollo main | Bootloader | Bytes | SHA-256 |
|---|---|---|---:|---|
| `lfs_mlist_remove` | `[0x004CB0A0,0x004CB0BC)` | `[0x00410DA8,0x00410DC4)` | 28 | `55bb19e48e301285459cecc31d6177555f04d0b41ea3ae3c1ed3225fd357a8bd` |
| **`lfs_mlist_append`** | `[0x004CB0BC,0x004CB0C4)` | `[0x00410DC4,0x00410DCC)` | **8** | `e3ed290e4e62fc9cce34b0530080dbc08efbca65f80ca1b7d182e18bb20c24b9` |
| `lfs_fs_disk_version` body | `[0x004CB0C4,0x004CB0CA)` | `[0x00410DCC,0x00410DD2)` | 6 | `1ff8f5ac86a29e52674a91191c4ed763fe635aed200e701063e8224aa15c3870` |

The same ordered source neighborhood in both linker-selected littlefs copies
is additional evidence for the function identity and exact boundaries.

## `lfs_t` and open-list ABI

On the recovered 32-bit target ABI:

| Type/field | Offset or size |
|---|---:|
| pointer | 4 bytes |
| `lfs_cache_t` | `0x10` bytes |
| `lfs_gstate_t` | `0x0C` bytes |
| `struct lfs_lookahead` | `0x14` bytes |
| `lfs_t` | `0x80` bytes |
| `lfs_t.mlist` | `0x28` |
| `struct lfs_mlist.next` | `0x00` |
| `struct lfs_mlist.id` | `0x04` |
| `struct lfs_mlist.type` | `0x06` |

The integrated target implementation statically asserts all of these values.
The official instructions independently prove the two offsets that the
function actually dereferences.

The open-list prefix is deliberately common to `struct lfs_mlist`,
`lfs_dir_t`, and `lfs_file_t`: `next`, `id`, and `type` are the first fields
of all three. The two retained caller families pass a directory and a file,
respectively, corroborating this prefix ABI rather than relying on one
structure alone.

Apollo main's 84-byte configuration at `0x006E83A4` hashes to
`f38bd899e180d29ee60609a2452d25c2d2d6c6fef4eb455064e23a6ca7c6e813`.
The bootloader copy at `0x00431070` hashes to
`724c351d2136e3c2f10b59ad84d547da4632739ea1f20eb839e9af2cfbd5b6e8`.
That layout confirms `LFS_THREADSAFE` and `LFS_MULTIVERSION` are disabled.
Neither option changes the private list-node layout, and
`lfs_mlist_append` does not dereference the configuration.

## Complete caller and reference topology

Both complete images were scanned at every halfword for Thumb-2 `BL` and
non-linking `B.W`, at every halfword for narrow unconditional, conditional,
`CBZ`, and `CBNZ` targets, and at every byte for stored even or Thumb entry
and interior addresses.

### Apollo main

| Call site | Encoding | Upstream context |
|---:|---|---|
| `0x004CD5F4` | `FD F7 62 FD` | `lfs_dir_open_`: publish an initialized directory |
| `0x004CDAAA` | `FD F7 07 FB` | `lfs_file_opencfg_`: publish an initialized file |

The ordered caller-address list hashes to
`dbbe7397e4ecf1b2c9535637caa149ca627a9531428133e533971fa4a451f7ec`;
the concatenated call instructions hash to
`63144dc6aa6984dddee9b7e399c556e24177098bb6caf66027ce9cf360b825d8`.

### Bootloader

| Call site | Encoding | Upstream context |
|---:|---|---|
| `0x004131F8` | `FD F7 E4 FD` | `lfs_dir_open_`: publish an initialized directory |
| `0x004135FA` | `FD F7 E3 FB` | `lfs_file_opencfg_`: publish an initialized file |

The ordered caller-address list hashes to
`2ce88c3e92d29a79f7c72b7ba6305d54f2937c904bd82e5a06ecb0f72e2ecb1c`;
the concatenated call instructions hash to
`07a3265b9641f941e913aacaa2546384cb031a8b669e62c851ca7b978ba9a3b8`.

For each image:

- exactly the two listed `BL` instructions target the entry;
- no non-linking wide or narrow branch targets the entry;
- no external call or branch targets an interior halfword;
- no stored even or Thumb pointer names the entry or an interior address;
- no vector, callback table, jump table, literal, or data object is owned;
- there are no outgoing code or data references.

The callers finish initializing each node's identity and state before the
call. The helper links the node to the old head before publishing it as the
new head, matching the upstream source and official instruction order.

## Integrated target implementation

Plain optimizing C is permitted to reorder the two non-volatile stores under
the non-thread-safe littlefs configuration. That is equivalent for valid
single-threaded calls, but it would publish the new head before its `next`
link at the instruction boundary.

The integrated implementation keeps the pristine assignments and places an
instruction-free compiler memory barrier between them. This does not add a
call, state, runtime instruction, or opaque dependency. It only preserves the
upstream link-before-publish source order in the generated target object.

Under the project's Cortex-M55 Thumb `-Oz` flags, the complete target is:

```text
82 6A 0A 60 81 62 70 47
```

It exactly matches both official bodies. The target object:

- has one eight-byte function symbol;
- hashes to
  `e3ed290e4e62fc9cce34b0530080dbc08efbca65f80ca1b7d182e18bb20c24b9`;
- has zero `.text` relocations and zero undefined symbols;
- has no literal, stack frame, call, branch, or global data;
- authenticates target offsets `0x28` and `0` directly in its opcodes.

The source SHA-256 is
`385a7dacce093c5c1c41e7f580530e0574ad9af50b6714c89cf390620085b4a9`.

## Focused semantic validation

The host candidate is compared with a separately compiled pristine v2.10.1
`lfs.c`/`lfs_util.c` oracle. Tests cover:

- empty-list append;
- append ahead of an existing node;
- two successive valid appends and complete `next` topology;
- preservation of every node's `id` and `type`;
- preservation of unrelated `lfs_t.seed` and `block_count` state;
- host candidate/oracle layout agreement;
- target-only ABI assertions for the 32-bit layout;
- exact target symbol, bytes, field opcodes, and dependency closure;
- official package, payload, bootloader, and configuration hashes;
- identical dual-image stock spans and neighboring generation;
- exhaustive entry/interior branch and stored-pointer topology.

All seven focused tests pass.

## Files

- [`runtime_littlefs_mlist_append.c`](../../components/apollo_main/core_overlay/runtime_littlefs_mlist_append.c)
- [`runtime_littlefs_mlist_append_host.c`](../../tests/fixtures/runtime_littlefs_mlist_append_host.c)
- [`runtime_littlefs_mlist_append_upstream_oracle_host.c`](../../tests/fixtures/runtime_littlefs_mlist_append_upstream_oracle_host.c)
- [`test_runtime_littlefs_mlist_append.py`](../../tests/test_runtime_littlefs_mlist_append.py)

## Applied integration

The shared source is integrated at:

- Apollo main `[0x004CB0BC,0x004CB0C4)`;
- bootloader `[0x00410DC4,0x00410DCC)`.

Each image uses its own entry redirect and the same eight-byte source-generated
body. The integration pins the complete stock hash, both callers per image,
the absent non-linking/stored/interior references, the target ABI assertions,
and the relocation-free exact target bytes.

This boundary replaces an unequivocal upstream list primitive. It does not
justify changing littlefs's synchronization model: `LFS_THREADSAFE` remains
disabled in the official ABI, and callers remain responsible for the same
serialization assumptions as the official implementation. A future full
`lfs.c` integration can restore the upstream private symbol directly and
remove the temporary project-prefixed binding.
