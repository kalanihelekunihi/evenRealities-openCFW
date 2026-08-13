# G2 littlefs `lfs_file_tell_` source-boundary audit

Status: implementation-ready source-replacement recommendation for official
G2 package `2.2.6.10`

Scope: Apollo-main application only; read-only binary and source analysis; no
firmware assembly, signing, flashing, external-flash access, or hardware use

## Result

The next smallest safe littlefs source-replacement boundary is the private
upstream v2.10.1 `lfs_file_tell_` leaf:

| Property | Recovered value |
|---|---|
| Official range | `0x004CE45C...0x004CE45F` |
| End-exclusive range | `[0x004CE45C,0x004CE460)` |
| Installed-payload offset | `0x0009645C` |
| OTA-package offset | `0x0009647C` |
| Size | 4 bytes |
| Official bytes | `48 6B 70 47` |
| SHA-256 | `efdc6e5a708e49cc1158aec6dfbde6a0115558c29a0f8c6a6ba9c4075df0fb5f` |
| Upstream source | littlefs v2.10.1 `lfs.c:3836...3839` |
| Direct callers | one, `BL` at `0x004CFC10` |
| Entry/interior stored pointers | none |
| External interior branches | none |
| Calls or data references made | none |
| Flash/MSPI/config dependency | none |

This is a live, unequivocally identified upstream function, not a generic
four-byte accessor assigned a speculative name. Its only direct caller is the
stock public `lfs_file_tell` wrapper. That wrapper is reached by both the
shared file runtime and the LVGL littlefs filesystem callback.

Use the pinned v2.10.1 source body directly. It is a behavioral and ABI
drop-in and needs no G2 block-device adapter. Because upstream declares the
helper `static`, an incremental overlay still needs a project-prefixed,
non-inlined entry and a four-byte entry redirect. That is link/overlay
binding, not a re-created algorithm or a G2 functional adapter.

## Authoritative inputs

The reviewed official image is:

| Property | Value |
|---|---|
| File | `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` |
| Package bytes | `3,523,396` |
| Package SHA-256 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| OTA preamble | 32 bytes |
| Installed application bytes | `3,523,364` |
| Installed application SHA-256 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Application load address | `0x00438000` |

The source comparator is the authenticated snapshot already present at
[`../../third_party/littlefs`](../../third_party/littlefs):

| Property | Value |
|---|---|
| Selected release | littlefs `v2.10.1` |
| Commit | `0494ce7169f06a734a7bd7585f49a9fa91fa7318` |
| Tree | `06dd0162169d3cb550cd24a3e34d0e4d02983ad3` |
| License | BSD-3-Clause |
| `lfs.c` bytes / SHA-256 | `196,753` / `81a209e8551754d13b24fc0a2b6707fb3b2475e14feba00bf0df722b98a31398` |
| `lfs.h` bytes / SHA-256 | `26,439` / `ee44e99d6b19119b3e577b969b80c9d5e6f96410c9593794afddf6d4b314c486` |

As established by the broader littlefs revision audit, v2.10.1 is an exact
source-equivalent release pin. It is not a claim that the stripped firmware
proves Even Realities' historical Git checkout identity.

The bootloader does not retain `lfs_file_tell` or this private helper in its
linker-selected littlefs subset. This boundary is therefore Apollo-main only;
there is no bootloader entry to redirect.

## Exact binary-to-source proof

The complete official body is:

```text
004CE45C  ldr  r0, [r1, #0x34]
004CE45E  bx   lr
```

Under the Arm procedure-call ABI:

- `r0` receives `lfs_t *lfs`;
- `r1` receives `lfs_file_t *file`;
- `r0` returns the 32-bit `lfs_soff_t` result.

The pinned upstream function is:

```c
static lfs_soff_t lfs_file_tell_(lfs_t *lfs, lfs_file_t *file) {
    (void)lfs;
    return file->pos;
}
```

On the recovered 32-bit ABI, `lfs_file_t.pos` is exactly `+0x34`. The load
therefore implements the complete source body: ignore `lfs`, load `file->pos`,
and return its unchanged 32-bit representation. There is no omitted check,
lock, trace, conversion helper, callback, or error path.

A normalized Cortex-M55 Thumb `-Oz` compilation of that source against the
pinned header emitted:

```text
ldr  r0, [r1, #52]
bx   lr
```

Those instructions have the same `48 6B 70 47` encoding as the official
function.

The source association is independently anchored by all of the following:

1. The public wrapper at `[0x004CFBE8,0x004CFC16)` calls this entry at
   `0x004CFC10`.
2. That wrapper contains the upstream line-6258 assertion
   `lfs_mlist_isopen(lfs->mlist, (struct lfs_mlist*)file)`.
3. The private functions occur in exact upstream order:
   `lfs_file_seek_`, `lfs_file_tell_`, `lfs_file_rewind_`, then
   `lfs_file_size_`.
4. The selected source generation and configuration were previously fixed by
   the complete littlefs assertion-line fingerprint.

The neighboring callable boundaries are:

| Range | Upstream function | Bytes | SHA-256 |
|---|---|---:|---|
| `[0x004CE3BC,0x004CE45C)` | `lfs_file_seek_` | 160 | `368a3e58188f71ad37233eaca687cd3939a9f06406702a176f9731f22bcaf61f` |
| `[0x004CE45C,0x004CE460)` | **`lfs_file_tell_`** | **4** | `efdc6e5a708e49cc1158aec6dfbde6a0115558c29a0f8c6a6ba9c4075df0fb5f` |
| `[0x004CE460,0x004CE472)` | `lfs_file_rewind_` | 18 | `be02691b2e7339d7dd1d54b31712c3e8563e5a86f4406a469888640fad9435cd` |
| `[0x004CE472,0x004CE48A)` | `lfs_file_size_` | 24 | `98ba58dac7de35e47c75240c0671b11e6b403a1bffed50a617c6543eb26a83cc` |

`lfs_file_seek_` returns before `0x004CE45C`, the selected leaf returns at
`0x004CE45E`, and `lfs_file_rewind_` begins with its own prologue at
`0x004CE460`. There is no shared tail, literal pool, or fall-through ownership
inside the selected four bytes.

## Complete caller and reference topology

The installed application's complete direct-branch topology for the selected
entry is:

```text
0x004CFC10  BL  0x004CE45C
```

The call is inside the official public `lfs_file_tell` wrapper:

| Property | Value |
|---|---|
| Wrapper range | `[0x004CFBE8,0x004CFC16)` |
| Wrapper bytes | 46 |
| Wrapper SHA-256 | `94d0448e342cf969f6a4553a19ef9d638a75e0d41cdf8d842e7f8b4900cb3675` |
| Private-helper call | `0x004CFC10 -> 0x004CE45C` |
| Call instruction bytes | `FE F7 24 FC` |
| Call-instruction SHA-256 | `8ad7ac585f86ce23cb246bcd9c95988ba5b50881b256f3b0da0c90a0428f3d31` |

The ordered little-endian caller-address list `[0x004CFC10]` hashes to
`ec5bf1b540555e7fb3a4630a6b4edb1c00c08d3c3c2f9ee2fce252de4c16f7f8`.

The public wrapper remains live through two official direct callers:

| Caller | Function range | Call site |
|---|---|---|
| Shared file-runtime tell wrapper | `[0x00474870,0x004748B4)` | `0x0047489A` |
| LVGL littlefs tell callback | `[0x004C9064,0x004C9080)` | `0x004C906A` |

Their function hashes are
`55718ee2e6b4d6b5d2c45ab93ed5a96cf932afc8eee9dc4e37e7796316013f20`
and
`5df35250b618fce7b50853b3bc8468643ba5e7defe2f9e29774c3f22313f04c0`,
respectively. The ordered public-wrapper call-site list
`[0x0047489A, 0x004C906A]` hashes to
`1ecea10b4064a3a5afa47fec5f195e0ff6fd258e7c04478f71efcdda01af8281`.

The current openCFW overlay already source-replaces the shared wrapper at
`0x00474870`, but its source intentionally calls the retained public
littlefs entry at Thumb address `0x004CFBE9`. The selected private leaf
therefore remains part of that source-generated runtime path as well as the
retained LVGL path.

### Whole-image closure

The complete installed payload was scanned at every halfword for Cortex-M
immediate `B`, conditional `B`, `CBZ`/`CBNZ`, `B.W`, and `BL` targets, and at
every byte for stored 32-bit addresses.

The results were:

- exactly one direct branch to the entry, the `BL` at `0x004CFC10`;
- no direct branch to the sole interior instruction at `0x004CE45E`;
- no stored even or Thumb entry address (`0x004CE45C` or `0x004CE45D`);
- no stored even or Thumb interior address (`0x004CE45E` or `0x004CE45F`);
- no literal, data, vector, callback-table, or jump-table reference owned by
  the function.

Rizin full-image analysis independently reports a four-byte pure function,
one code xref at `0x004CFC10`, zero call refs, zero data refs, and zero
external interior xrefs.

No caller rewrite or callback rebinding is required. A complete entry redirect
preserves the one existing call edge.

## ABI and configuration dependencies

The replacement must preserve:

| Type or field | Recovered value |
|---|---:|
| Pointer | 4 bytes |
| Endianness | little |
| `sizeof(lfs_off_t)` | 4 bytes |
| `sizeof(lfs_soff_t)` | 4 bytes |
| `sizeof(lfs_file_t)` | `0x54` bytes |
| `offsetof(lfs_file_t, pos)` | `0x34` |
| `lfs_file_t.pos` source type | unsigned `lfs_off_t` |
| Return source type | signed `lfs_soff_t` |

Cortex-M55 cross-target compile-time assertions against the pinned `lfs.h`
passed for every size and offset above.

The unsigned-to-signed return conversion preserves the register bits. Valid
file positions are at most the default `LFS_FILE_MAX` of `0x7FFFFFFF`, so
normal successful values are representable as `lfs_soff_t`. The replacement
must still use the upstream types rather than changing the field or return
type to a host-sized integer.

This private function is independent of:

- `struct lfs_config` contents and the main/boot configuration tables;
- `LFS_THREADSAFE`, `LFS_YES_TRACE`, `LFS_READONLY`, and
  `LFS_MULTIVERSION`;
- dynamic allocation and the three optional littlefs buffers;
- read/program/erase/sync callbacks;
- filesystem geometry, on-disk format, cache sizing, and block cycles;
- MSPI initialization, XIP state, mutexes, timing, and power policy.

The public wrapper still owns the open-file assertion. The source replacement
must remain private to that call path; it must not be promoted as a checked
public API or called with an unvalidated/null `lfs_file_t *`.

## Source-replacement contract

An incremental source replacement should:

1. retain the authenticated littlefs v2.10.1 BSD-3-Clause notice;
2. include the pinned `lfs.h` types;
3. expose a project-prefixed entry such as
   `open_cfw_lfs_file_tell_private`;
4. preserve the exact upstream body:
   `(void)lfs; return file->pos;`;
5. force the incremental entry to remain emitted and non-inlined;
6. assert the pointer/type sizes, `sizeof(lfs_file_t) == 0x54`, and
   `offsetof(lfs_file_t, pos) == 0x34`;
7. redirect the complete four-byte entry at `0x004CE45C` with the overlay's
   normal non-linking `B.W`, preserving the caller's link register;
8. leave the public wrapper at `0x004CFBE8` unchanged so its assertion and
   existing callers remain intact;
9. pin the official body hash, single caller, and absent stored/interior
   references in focused tests;
10. test positions `0`, `1`, `0x7FFFFFFF`, and bit-preserving edge fixtures
    without mounting a filesystem or touching flash.

This recommendation does not require compiling the complete `lfs.c` yet. A
future full-core integration can use upstream's original static function
unchanged and remove the temporary project-prefixed binding.

## Why this boundary precedes `lfs_unmount`

`lfs_unmount` initially appears smaller at ten public bytes, but it is not a
closed source boundary:

```text
public lfs_unmount
  -> private lfs_unmount_
  -> lfs_deinit
  -> allocator free helper, up to three calls
```

The 50-byte `lfs_deinit` body is also shared by two other littlefs cleanup
paths. Replacing only the public wrapper would require a fixed-address call to
a retained private function; replacing the full behavior would expand into
shared lifetime and allocator ownership.

By contrast, `lfs_file_tell_` is:

- smaller;
- a complete leaf;
- source-identical;
- live through two application-facing paths;
- free of private callees, allocation, configuration, flash, or hardware
  state;
- redirectable without changing its caller.

`lfs_file_rewind_`, `lfs_file_size_`, the public wrappers, and the
unmount/deinitialization closure remain good later boundaries, but each adds
control flow, calls, assertions, or shared state that this first core leaf
does not.

## Validation performed

The read-only littlefs snapshot verifier passed:

```text
littlefs v2.10.1 source-equivalent snapshot, BSD-3-Clause notice,
provenance, hashes, ABI, and no-format/no-erase policy: OK;
official config spans checked: Apollo main, bootloader
```

The audit also:

- rehashed the complete OTA package and installed payload;
- rehashed the selected and neighboring function ranges from the
  authenticated package;
- decoded the selected body independently with Capstone and Rizin;
- completed full Rizin function/xref analysis;
- scanned the whole installed image for direct branches and stored
  entry/interior addresses;
- cross-compiled the pinned 32-bit structure assertions for Cortex-M55;
- compiled the exact upstream body at `-Oz` and reproduced the official two
  instructions.

## Historical decision

Replace `[0x004CE45C,0x004CE460)` with the pinned littlefs v2.10.1
`lfs_file_tell_` source body as the next littlefs core boundary.

No decompilation, algorithm recreation, G2 MSPI adapter, filesystem mount, or
hardware access is needed to establish this leaf's source identity. Normal
host-side and eventual integration testing still applies. The only
incremental glue is the overlay-visible entry required to redirect an
upstream-static function.

## Subsequent production status

The `lfs_file_tell_` recommendation above was subsequently promoted and remains
source-owned. The next main-only private accessor, `lfs_file_size_` at
`[0x004CE472,0x004CE48A)`, is now also production-integrated from the same
authenticated littlefs v2.10.1 source-equivalent snapshot. Its writing-state
maximum closes over the already source-owned `open_cfw_littlefs_util_max`;
neither accessor admits a G2 block-device callback, filesystem mount, format,
erase, or other hardware mutation. Current file-size stock, ABI, caller,
dependency, placement, and artifact evidence is recorded in
`docs/research/littlefs-file-size-source-audit.md`.
