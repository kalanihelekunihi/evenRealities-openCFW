# G2 littlefs `lfs_mlist_remove` source-boundary audit

Status: source-integrated in both Apollo-main and bootloader production
overlays

Scope: official G2 package `2.2.6.10`; authenticated binary/source analysis,
host/target validation, redirect-safety research, and subsequent dual-image
source-overlay integration; no signing, flashing, external-flash access, or
hardware use

## Result

The private littlefs v2.10.1 `lfs_mlist_remove` helper is unequivocally
identified in both official images:

| Property | Apollo main | Bootloader |
|---|---:|---:|
| Entry | `0x004CB0A0` | `0x00410DA8` |
| End-exclusive range | `[0x004CB0A0,0x004CB0BC)` | `[0x00410DA8,0x00410DC4)` |
| Installed-payload offset | `0x000930A0` | `0x00000DA8` |
| Package/file offset | `0x000930C0` | `0x00000DA8` |
| Size | 28 bytes | 28 bytes |
| SHA-256 | `55bb19e48e301285459cecc31d6177555f04d0b41ea3ae3c1ed3225fd357a8bd` | same |
| Direct callers | 2 | 2 |
| Non-linking or stored entries | none | none |
| External interior entries | none | none |
| Outgoing calls/literals | none | none |

The helper walks the pointer-to-pointer chain rooted at `lfs_t.mlist`, unlinks
the first node whose address equals its argument, and otherwise leaves the
list unchanged. It does not clear or otherwise mutate the removed node. That
is the complete pristine v2.10.1 operation.

The only target ABI dependencies are 32-bit pointers,
`offsetof(lfs_t, mlist) == 0x28`, and
`offsetof(struct lfs_mlist, next) == 0`. The official entry instruction and
loop shape authenticate both offsets. There is no configuration, allocation,
flash, filesystem-format, callback, or MSPI dependency.

## Authoritative inputs

| Image | Bytes | SHA-256 | Mapping |
|---|---:|---|---|
| `ota_s200_firmware_ota.bin` | `3,523,396` | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` | 32-byte preamble, payload at `0x00438000` |
| Apollo-main installed payload | `3,523,364` | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` | package bytes after preamble |
| `ota_s200_bootloader.bin` | `148,599` | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` | raw image at `0x00410000` |

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

## Exact source and binary boundary

Pristine v2.10.1 `lfs.c:522...529` is:

```c
static void lfs_mlist_remove(lfs_t *lfs, struct lfs_mlist *mlist) {
    for (struct lfs_mlist **p = &lfs->mlist; *p; p = &(*p)->next) {
        if (*p == mlist) {
            *p = (*p)->next;
            break;
        }
    }
}
```

Both complete official bodies contain:

```text
10 F1 28 02 00 E0 12 68 10 68 00 28 05 D0
10 68 88 42 F8 D1 10 68 00 68 10 60 70 47
```

Decoded:

```text
adds.w r2, r0, #0x28
b      test
advance:
ldr    r2, [r2]
test:
ldr    r0, [r2]
cmp    r0, #0
beq    return
ldr    r0, [r2]
cmp    r0, r1
bne    advance
ldr    r0, [r2]
ldr    r0, [r0]
str    r0, [r2]
return:
bx     lr
```

`r2` is the current pointer-to-pointer link. Because `next` is at offset zero,
the loaded node address is also the address of that node's `next` link; the
single `ldr r2, [r2]` therefore implements `p = &(*p)->next`. When a node
matches, loading through it obtains `(*p)->next`, which is written back to the
current link.

There is no omitted null check or second-match behavior. The function returns
after the first unlink, exactly matching `break` in the upstream source.

The neighboring dual-image source generation is identical:

| Function | Apollo main | Bootloader | Bytes | SHA-256 |
|---|---|---|---:|---|
| `lfs_mlist_isopen` | `[0x004CB082,0x004CB0A0)` | `[0x00410D8A,0x00410DA8)` | 30 | `e4963bfc9db9aa487d15261ebce9dd5b1429c708f6fe78ff47968718821c0c4e` |
| **`lfs_mlist_remove`** | `[0x004CB0A0,0x004CB0BC)` | `[0x00410DA8,0x00410DC4)` | **28** | `55bb19e48e301285459cecc31d6177555f04d0b41ea3ae3c1ed3225fd357a8bd` |
| `lfs_mlist_append` | `[0x004CB0BC,0x004CB0C4)` | `[0x00410DC4,0x00410DCC)` | 8 | `e3ed290e4e62fc9cce34b0530080dbc08efbca65f80ca1b7d182e18bb20c24b9` |

There is no fall-through, shared tail, or literal pool between these private
helpers.

## `lfs_t` and list-node ABI

The recovered 32-bit target layout is:

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

The integrated target implementation statically asserts every value. The
machine code proves
the two offsets that are actually accessed. The `next`/`id`/`type` prefix is
common to `struct lfs_mlist`, `lfs_dir_t`, and `lfs_file_t`; the two caller
families exercise the directory and file forms independently.

Apollo main's 84-byte configuration at `0x006E83A4` hashes to
`f38bd899e180d29ee60609a2452d25c2d2d6c6fef4eb455064e23a6ca7c6e813`.
The bootloader copy at `0x00431070` hashes to
`724c351d2136e3c2f10b59ad84d547da4632739ea1f20eb839e9af2cfbd5b6e8`.
This confirms that `LFS_THREADSAFE` and `LFS_MULTIVERSION` are disabled.
Neither option changes this private helper, and the helper never reads
`lfs->cfg`.

## Complete caller and entry topology

Both complete images were scanned at every halfword for Thumb-2 `BL` and
non-linking `B.W`, at every halfword for narrow unconditional, conditional,
`CBZ`, and `CBNZ` targets, and at every byte for stored even or Thumb entry
and interior addresses.

### Apollo main

| Call site | Encoding | Upstream context |
|---:|---|---|
| `0x004CD606` | `FD F7 4B FD` | `lfs_dir_close_`: unlink a closing directory |
| `0x004CDCF8` | `FD F7 D2 F9` | `lfs_file_close_`: unlink a closing file |

The ordered caller-address list hashes to
`6c4bb102d90b0b2fecf42e493f6ce815fee1e1b8cb34cebefa3aa20561c3c570`;
the concatenated call instructions hash to
`aea63c312924b0200829c0ae9d58bd332bee9c2c0cc3b7882a86e90623bcff3f`.

### Bootloader

| Call site | Encoding | Upstream context |
|---:|---|---|
| `0x0041320A` | `FD F7 CD FD` | `lfs_dir_close_`: unlink a closing directory |
| `0x00413848` | `FD F7 AE FA` | `lfs_file_close_`: unlink a closing file |

The ordered caller-address list hashes to
`a4062608f53073dab0c6980ec6c9b9d8bd1448f5aa200a7654b83a5eb45e7103`;
the concatenated call instructions hash to
`086fa8e91282e56652937f8dd939aefc1d4ec81edd03fadb877f41400fbdfdb1`.

For each image:

- exactly the two listed `BL` instructions target the entry;
- no non-linking wide or narrow branch targets the entry;
- no external call or branch targets an interior halfword;
- no stored even or Thumb pointer names the entry or an interior address;
- no vector, callback table, jump table, literal, or data object is owned;
- there are no outgoing code or data references.

## Integrated target implementation

The exact upstream loop compiled under the project's Cortex-M55 Thumb `-Oz`
flags produces an equivalent, shorter link-location loop:

```text
28 30 02 46 00 68 18 B1 88 42 FA D1 00 68 10 60 70 47
```

Decoded:

```text
adds r0, #0x28
mov  r2, r0
ldr  r0, [r0]
cbz  r0, return
cmp  r0, r1
bne  advance
ldr  r0, [r0]
str  r0, [r2]
return:
bx   lr
```

The backward branch to `mov r2, r0` makes the current node's zero-offset
`next` field the next link location. This is the same pointer-to-pointer
algorithm without the official compiler's separate test branch.

The complete target:

- has one 18-byte function symbol;
- hashes to
  `bb4d51fd66c1638dae0c38615feffb08286027539aede7f65197306491d44e4f`;
- is ten bytes smaller than the official body;
- has zero `.text` relocations and zero undefined symbols;
- has no literal, stack frame, call, or global data;
- preserves first-match removal and the removed node's unchanged `next`.

The source SHA-256 is
`806945d7657a1e8618da633305d1bc17b2cb6a88381d897b146877ef5c007ed1`.

## Focused semantic validation

The host candidate is compared with a separately compiled pristine v2.10.1
`lfs.c`/`lfs_util.c` oracle. Tests cover:

- removal from an empty list;
- an absent node in a nonempty list;
- head, middle, and tail removal;
- exact remaining and removed-node `next` values;
- preservation of all node `id` and `type` values;
- preservation of unrelated `lfs_t.seed` and `block_count`;
- host candidate/oracle layout agreement;
- target-only 32-bit ABI assertions;
- exact target symbol, opcodes, size, and dependency closure;
- official package, payload, bootloader, and configuration hashes;
- identical dual-image stock spans and neighboring generation;
- exhaustive entry/interior branch and stored-pointer topology.

All seven focused tests pass.

## Files

- [`runtime_littlefs_mlist_remove.c`](../../components/apollo_main/core_overlay/runtime_littlefs_mlist_remove.c)
- [`runtime_littlefs_mlist_remove_host.c`](../../tests/fixtures/runtime_littlefs_mlist_remove_host.c)
- [`runtime_littlefs_mlist_remove_upstream_oracle_host.c`](../../tests/fixtures/runtime_littlefs_mlist_remove_upstream_oracle_host.c)
- [`test_runtime_littlefs_mlist_remove.py`](../../tests/test_runtime_littlefs_mlist_remove.py)

## Applied integration

The shared source is integrated at:

- Apollo main `[0x004CB0A0,0x004CB0BC)`;
- bootloader `[0x00410DA8,0x00410DC4)`.

Each image uses its own entry redirect and the same 18-byte relocation-free
target. The integration pins the complete 28-byte stock hash, both callers per
image, absent non-linking/stored/interior references, target ABI assertions,
and target bytes.

This boundary does not justify changing littlefs's synchronization model.
`LFS_THREADSAFE` remains disabled in the official ABI, and callers retain the
official serialization assumptions. A future full `lfs.c` integration can
restore the upstream private symbol directly and remove the temporary
project-prefixed binding.
