# G2 littlefs `lfs_scmp` source-boundary audit

Status: source-integrated for both Apollo main and the bootloader in official
G2 package `2.2.6.10`

Scope: Apollo-main application and bootloader; binary/source analysis and
candidate validation plus offline package assembly; no signing, flashing,
external-flash access, or hardware use

## Result

The next smallest safe exact-upstream littlefs boundary after
`lfs_file_tell_` is the v2.10.1 `lfs_scmp` utility leaf:

| Property | Apollo main | Bootloader |
|---|---:|---:|
| Entry | `0x004CA7B2` | `0x004104BA` |
| End-exclusive range | `[0x004CA7B2,0x004CA7B6)` | `[0x004104BA,0x004104BE)` |
| Installed-payload offset | `0x000927B2` | `0x000004BA` |
| Package/file offset | `0x000927D2` | `0x000004BA` |
| Size | 4 bytes | 4 bytes |
| Bytes | `40 1A 70 47` | `40 1A 70 47` |
| SHA-256 | `787fad2973d1b4f1c6c585f29ee07707e6951499c3772a9e8e4e1bc997ba94fe` | same |
| Direct callers | `0x004CB9CA` | `0x004116D2` |
| Wide non-linking branches | none | none |
| Narrow branches | none | none |
| Stored entry/interior pointers | none | none |
| External interior entries | none | none |
| Calls/data/literals owned | none | none |

This is the only other four-byte callable leaf in the retained littlefs core.
It is present with identical bytes and relative call shape in both official
images. Each copy has exactly one direct caller, in the same upstream
`lfs_dir_fetchmatch` revision-selection path.

Use the pinned v2.10.1 source expression directly. No decompilation,
vendor-algorithm recreation, G2 adapter, littlefs configuration table,
block-device callback, MSPI state, allocation, or filesystem structure ABI is
involved.

## Authoritative inputs

The official images are:

| Image | Bytes | SHA-256 | Mapping |
|---|---:|---|---|
| `ota_s200_firmware_ota.bin` | `3,523,396` | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` | 32-byte preamble, payload at `0x00438000` |
| Apollo-main installed payload | `3,523,364` | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` | package bytes after the preamble |
| `ota_s200_bootloader.bin` | `148,599` | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` | raw image at `0x00410000` |

The comparator is the authenticated littlefs snapshot at
[`third_party/littlefs`](../../third_party/littlefs):

| Property | Value |
|---|---|
| Selected release | littlefs `v2.10.1` |
| Commit | `0494ce7169f06a734a7bd7585f49a9fa91fa7318` |
| Tree | `06dd0162169d3cb550cd24a3e34d0e4d02983ad3` |
| License | BSD-3-Clause |
| `lfs_util.h` bytes | `7,954` |
| `lfs_util.h` SHA-256 | `f5d249326646c818e62af3cefefe8a57e7b484446a0f48d1050b95e60925088e` |
| `lfs_util.h` Git blob | `0aec48855359df6e39d2f5bb3c45ca22b4a28811` |

As in the broader revision audit, v2.10.1 is an exact source-equivalent
release pin. This does not overclaim the original private checkout identity.

## Exact binary-to-source proof

Both official bodies decode identically:

```text
Apollo main
004CA7B2  subs  r0, r0, r1
004CA7B4  bx    lr

Bootloader
004104BA  subs  r0, r0, r1
004104BC  bx    lr
```

The pinned upstream source is
[`lfs_util.h:180...184`](../../third_party/littlefs/lfs_util.h):

```c
// Find the sequence comparison of a and b, this is the distance
// between a and b ignoring overflow
static inline int lfs_scmp(uint32_t a, uint32_t b) {
    return (int)(unsigned)(a - b);
}
```

Under the 32-bit Arm procedure-call ABI:

- `r0` receives unsigned 32-bit `a`;
- `r1` receives unsigned 32-bit `b`;
- `r0` returns signed 32-bit `int`;
- `subs r0, r0, r1` performs the required modulo-`2^32` subtraction;
- `bx lr` returns the unchanged result bits.

There is no missing sign normalization. `lfs_scmp` deliberately returns the
signed interpretation of the complete unsigned distance, not only `-1`, `0`,
or `1`.

A normalized Cortex-M55 Thumb `-Oz` compilation of the exact upstream
expression emitted:

```text
subs  r0, r0, r1
bx    lr
```

The encoding is the same official `40 1A 70 47`, with no relocation.

### Neighboring source order

The selected function sits between the retained upstream `lfs_popc` and
`lfs_fromle32` helper bodies. All three spans are byte-identical between
Apollo main and the bootloader:

| Upstream function | Apollo-main range | Bootloader range | Bytes | SHA-256 |
|---|---|---|---:|---|
| `lfs_popc` | `[0x004CA78A,0x004CA7B2)` | `[0x00410492,0x004104BA)` | 40 | `2cc25090f38dd5c2121cb4bfc7ddf0bd71df984312c9b9c52e87feeef5aea872` |
| **`lfs_scmp`** | `[0x004CA7B2,0x004CA7B6)` | `[0x004104BA,0x004104BE)` | **4** | `787fad2973d1b4f1c6c585f29ee07707e6951499c3772a9e8e4e1bc997ba94fe` |
| `lfs_fromle32` helper body | `[0x004CA7B6,0x004CA7D8)` | `[0x004104BE,0x004104E0)` | 34 | `0666243f83f942c21b4428e4027b6f7815771c2f8a51dcddc550ffa9710add76` |

The preceding helper returns at the byte before each `lfs_scmp` entry. The
selected helper returns at its second instruction, and the following helper
begins immediately at the end-exclusive boundary. There is no padding,
literal pool, shared tail, or fall-through ownership within the selected
span.

The identical helper cluster in independently linked main and boot images is
strong compiler/source-order corroboration, not merely a match to a common
subtract-return instruction pair.

## Pristine semantics

`lfs_scmp` compares wrapping 32-bit sequence numbers by interpreting the
unsigned distance `a-b` as signed:

| `a` | `b` | Unsigned distance | Returned `int` | Interpretation |
|---:|---:|---:|---:|---|
| `0x00000000` | `0x00000000` | `0x00000000` | `0` | equal |
| `0x00000001` | `0x00000000` | `0x00000001` | `1` | `a` is newer |
| `0x00000000` | `0x00000001` | `0xFFFFFFFF` | `-1` | `a` is older |
| `0x00000000` | `0xFFFFFFFF` | `0x00000001` | `1` | wrap: `a` is newer |
| `0xFFFFFFFF` | `0x00000000` | `0xFFFFFFFF` | `-1` | wrap: `a` is older |
| `0x80000000` | `0x00000000` | `0x80000000` | `INT32_MIN` | half-range boundary |

The upstream subtraction is unsigned and therefore cannot invoke signed
overflow. The subsequent out-of-range unsigned-to-`int` conversion uses the
32-bit two's-complement interpretation established by both official Arm
binaries.

A replacement must preserve the exact upstream expression. Rewriting it as
signed `a-b` would introduce undefined overflow; rewriting it as a relational
three-way comparator would change return magnitudes and wrapping behavior.

## Complete dual-image topology

Both complete images were scanned at every halfword for Thumb-2 `BL` and
non-linking `B.W`, at every halfword for narrow unconditional, conditional,
and `CBZ`/`CBNZ` branches, and at every byte for stored even or Thumb entry
and interior addresses.

### Apollo main

```text
0x004CB9CA  BL  0x004CA7B2
```

Results:

- one linked wide branch to the entry;
- no non-linking wide branch;
- no narrow branch to the entry or `0x004CA7B4` interior instruction;
- no stored `0x004CA7B2`, `0x004CA7B3`, `0x004CA7B4`, or `0x004CA7B5`;
- no vector, callback-table, jump-table, literal, or data reference;
- no external entry into the second instruction.

The call instruction is `FE F7 F2 FE`, SHA-256
`d77a3cd87c4c95d7dbf4c0ba35c2c96298b6b41a880cdbe425c9867632ce51a8`.
The ordered little-endian caller-address list `[0x004CB9CA]` hashes to
`ab3abbc52e7e8885f61d1fd5cbd86926d22efbe07a5a1038e8eec32a0e84952d`.

Rizin full-image analysis independently reports a four-byte function with
one code xref at `0x004CB9CA`, no call refs, and no data refs.

### Bootloader

```text
0x004116D2  BL  0x004104BA
```

Results:

- one linked wide branch to the entry;
- no non-linking wide branch;
- no narrow branch to the entry or `0x004104BC` interior instruction;
- no stored `0x004104BA`, `0x004104BB`, `0x004104BC`, or `0x004104BD`;
- no vector, callback-table, jump-table, literal, or data reference;
- no external entry into the second instruction.

The boot call has the same `FE F7 F2 FE` encoding and instruction hash. The
ordered little-endian caller-address list `[0x004116D2]` hashes to
`43167613e139eae1bf7f26330e9a733b8d7dde264d87a627dc9d10a1b5e0f3a9`.

Rizin independently reports the same one-caller, zero-callee, zero-data-ref
topology.

No caller rewrite, function-pointer rebinding, veneer, or interior patch is
required. A complete four-byte entry redirect preserves each existing call
edge.

## Sole caller: `lfs_dir_fetchmatch`

In each image the call belongs to the upstream `lfs_dir_fetchmatch`
implementation:

| Property | Apollo main | Bootloader |
|---|---:|---:|
| Function range | `[0x004CB968,0x004CBED8)` | `[0x00411670,0x00411BE0)` |
| Size | 1,392 bytes | 1,392 bytes |
| SHA-256 | `42e16b94a318ea88b3d8b455a6c29a0dc981a4ea1a4c9e0836c2f177d1b2334f` | `bc4d8bb238b61ffd72ee3d370a8342eb1bee167aaa385c98dccb869f1e2761fc` |
| Call site | `0x004CB9CA` | `0x004116D2` |

The 30-byte instruction sequence around the call is byte-identical:

| Apollo-main range | Bootloader range | SHA-256 |
|---|---|---|
| `[0x004CB9B4,0x004CB9D2)` | `[0x004116BC,0x004116DA)` | `d3f06c054fb74ac6230d2573c0efd7abe3baea977e447e8e7ed6ec65259b3bd0` |

It computes `(i+1)%2`, loads `revs[(i+1)%2]` into `r1`, loads `revs[i]`
into `r0`, calls `lfs_scmp`, and tests whether the signed result is at least
one. This is exactly upstream `lfs.c:1125...1141`:

```c
if (err != LFS_ERR_CORRUPT &&
        lfs_scmp(revs[i], revs[(i+1)%2]) > 0) {
    r = i;
}
```

The caller reads two metadata-block revision words before this comparison.
Those block reads and little-endian conversions belong to
`lfs_dir_fetchmatch`, not to the selected helper. Replacing `lfs_scmp`
therefore does not acquire block-device, cache, partition, or MSPI ownership.

The optional v1 migration source contains another `lfs_scmp` expression, but
that migration path is absent from the retained official callable topology.
The audited entry has only the one call listed per image. This boundary does
not claim source ownership for any compiler-inlined comparison elsewhere.

## ABI and configuration dependencies

The complete ABI contract is:

| Item | Requirement |
|---|---|
| `uint32_t` | unsigned 32-bit |
| `unsigned int` | unsigned 32-bit |
| `int` | signed 32-bit, two's complement |
| Argument `a` | `r0` |
| Argument `b` | `r1` |
| Return | `r0` |
| Stack frame | none |
| Callee-saved registers | none |

The helper has no pointer arguments and touches no memory. It is independent
of:

- `lfs_t`, `lfs_file_t`, `lfs_dir_t`, and `struct lfs_config` layouts;
- main and boot configuration-table addresses or contents;
- filesystem geometry and on-disk object layout;
- `LFS_THREADSAFE`, `LFS_READONLY`, `LFS_MULTIVERSION`, tracing, assertions,
  diagnostics, dynamic allocation, and optional buffer choices;
- read/program/erase/sync callbacks;
- flash partition bounds;
- MSPI initialization, timing, XIP, mutexes, power, and status handling.

The definition itself is outside the utility header's intrinsic-selection
conditionals. `LFS_NO_INTRINSICS` does not change `lfs_scmp`.

## Source-replacement contract

A later integration should:

1. retain the authenticated v2.10.1 BSD-3-Clause notice;
2. expose a uniquely named entry such as `open_cfw_littlefs_scmp`;
3. use 32-bit unsigned arguments and a 32-bit signed return;
4. preserve the exact upstream expression
   `return (int)(unsigned)(a - b);`;
5. keep the entry emitted and non-inlined for the incremental boundary;
6. assert `sizeof(uint32_t) == sizeof(unsigned) == sizeof(int) == 4`;
7. redirect the complete four-byte official entry in each selected image
   with a non-linking Thumb `B.W`, preserving the caller's link register;
8. require a four-byte target body `40 1A 70 47`;
9. require zero relocations, undefined symbols, literals, calls, and data
   dependencies;
10. pin the image-specific entry/caller addresses and the absence of
    wide, narrow, stored, and interior references;
11. compare edge and wrapping cases against the pristine v2.10.1 header
    function on the host.

Apollo main and the bootloader need separate entry redirects because their
stock addresses differ. They may share one source implementation if the
build's placement and per-image overlay policy allow it.

## Why this is the next boundary

`lfs_dir_tell_` would have repeated the prior four-byte accessor shape, but
the official linker did not retain that unused API in either reviewed image.
It is not an actionable stock boundary.

Among the live alternatives:

| Candidate | Bytes | Additional ownership |
|---|---:|---|
| **`lfs_scmp`** | **4** | pure 32-bit arithmetic only |
| `lfs_fs_disk_version` | 6 | disk-version constant/literal and multiversion selection |
| `lfs_alloc_ckpoint` | 6 | mutable `lfs_t` allocator state and field offsets |
| `lfs_mlist_append` | 8 | mutable open-object list and `lfs_t`/list-node layouts |
| `lfs_mlist_isopen` | 30 | list traversal and assertion-only build selection |

`lfs_scmp` is smaller, dual-image corroborated, call-free, stateless,
literal-free, layout-free, and configuration-independent. It is the lowest
risk exact-upstream successor to `lfs_file_tell_`.

## Validation performed

The audit:

- authenticated the complete main package, installed payload, and bootloader;
- rehashed both selected spans and all listed neighboring/caller ranges;
- decoded both bodies independently with Capstone and Rizin;
- completed full Rizin function/xref analysis in both images;
- scanned both complete images for wide and narrow direct branches;
- scanned both complete images byte-by-byte for stored entry/interior
  addresses;
- verified the single caller and source-line argument order;
- compiled the pristine expression for Cortex-M55 Thumb and reproduced the
  exact two instructions;
- reran the existing littlefs snapshot verifier, including both official
  configuration-span checks.

## Decision

Use the pinned littlefs v2.10.1 `lfs_scmp` implementation directly for
`[0x004CA7B2,0x004CA7B6)` in Apollo main and
`[0x004104BA,0x004104BE)` in the bootloader.

No focused decompilation, G2 port adapter, flash access, or hardware work is
needed to establish or test this leaf's source identity.

## Isolated source candidate

The audited expression is now available as one unregistered, freestanding
source candidate:

- [`runtime_littlefs_scmp.c`](../../components/apollo_main/core_overlay/runtime_littlefs_scmp.c)
- [`runtime_littlefs_scmp_host.c`](../../tests/fixtures/runtime_littlefs_scmp_host.c)
- [`runtime_littlefs_scmp_upstream_oracle_host.c`](../../tests/fixtures/runtime_littlefs_scmp_upstream_oracle_host.c)
- [`test_runtime_littlefs_scmp.py`](../../tests/test_runtime_littlefs_scmp.py)

The single source function is compatible with both audited images. Image
integration still requires distinct entry redirects at `0x004CA7B2` and
`0x004104BA`; those redirects are intentionally absent. The candidate has no
image-specific state or address dependency. Its source SHA-256 is
`c89c32261a206e82e7da871ec4f1da21eb1fe0f9b329d59d28eaea6bb3546c88`.

The focused test compiles the candidate and the pristine v2.10.1
`lfs_util.h` oracle as separate host libraries. It compares:

- the complete 10-by-10 edge and wrap matrix;
- 4,096 deterministic full-width input pairs;
- non-normalized distance magnitudes, including the half-range boundary;
- the 32-bit `uint32_t`, `unsigned`, and `int` ABI assumptions.

The same test cross-compiles the isolated candidate for Cortex-M55 Thumb with
the normalized recovery flags. Its complete `.text` remains the official
four bytes `40 1A 70 47`, SHA-256
`787fad2973d1b4f1c6c585f29ee07707e6951499c3772a9e8e4e1bc997ba94fe`,
with one four-byte function symbol and no relocations or undefined symbols.

Finally, the test authenticates both complete official images, the two stock
spans and neighbor hashes, the identical call instructions, and the absence
of wide, narrow, stored, and interior references. This makes the candidate
integration-ready without changing an overlay, manifest, aggregate test, or
shared source-coverage inventory.

## Next exact-upstream leaf identified

The next focused littlefs boundary should be `lfs_alloc_ckpoint`, but it has
not been implemented or registered in this pass:

| Property | Apollo main | Bootloader |
|---|---:|---:|
| Range | `[0x004CB0E0,0x004CB0E6)` | `[0x00410DE8,0x00410DEE)` |
| Bytes | `C1 6E 01 66 70 47` | same |
| SHA-256 | `74d41d77541fa368dfc90160c9fc3a8dfd62d891ea72f29ef9c115465b71a32c` | same |
| Direct callers | `0x004CB0F0`, `0x004CD400`, `0x004CDE38`, `0x004CE1F4`, `0x004CE256`, `0x004CEE80` | `0x00410DF8`, `0x00413004`, `0x00413988`, `0x00413D44`, `0x00413DA6`, `0x00414564` |
| Wide/narrow non-call entry branches | none | none |
| External interior entries | none | none |
| Stored entry/interior pointers | none | none |

The dual-image body decodes as:

```text
ldr  r1, [r0, #0x6c]
str  r1, [r0, #0x60]
bx   lr
```

This is exact v2.10.1 source:

```c
static void lfs_alloc_ckpoint(lfs_t *lfs) {
    lfs->lookahead.ckpoint = lfs->block_count;
}
```

A normalized isolated Cortex-M55 Thumb compile reproduces all six bytes.
The eight bytes before and ten bytes after the leaf are also identical
between the images, strengthening the source-order identification.

Unlike `lfs_scmp`, this successor mutates `lfs_t` and therefore owns two
structure offsets: `lookahead.ckpoint == 0x60` and
`block_count == 0x6c`. A later implementation pass should authenticate the
complete `lfs_t` layout and six caller contexts before accepting the
otherwise closed leaf. `lfs_fs_disk_version` remains a less attractive
same-size candidate because its function depends on an adjacent
`LFS_DISK_VERSION` literal and the recovered disabled-`LFS_MULTIVERSION`
configuration.
