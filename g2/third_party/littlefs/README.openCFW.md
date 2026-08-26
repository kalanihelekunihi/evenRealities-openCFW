# littlefs v2.10.1 source-equivalent snapshot

This directory contains pristine upstream littlefs source from the official
[`v2.10.1`](https://github.com/littlefs-project/littlefs/tree/v2.10.1)
tag at commit
[`0494ce7169f06a734a7bd7585f49a9fa91fa7318`](https://github.com/littlefs-project/littlefs/commit/0494ce7169f06a734a7bd7585f49a9fa91fa7318).
The five upstream files are byte-identical to that commit and are pinned by
size, Git blob identity, and SHA-256 in `PROVENANCE.json`.

## Qualification

This is an exact **source-equivalent release baseline**, not proof of the
original Even Realities checkout. The complete 38-assertion bootloader line
fingerprint matches only the official `v2.10.1` release among the 38 `v2`
tags inspected, and Apollo main contains the same littlefs source generation.
However, two later upstream source states generate the same complete object
under the recovered G2 configuration. With trace disabled, a stripped
executable cannot resolve that remaining repository-history ambiguity.

The full derivation is recorded in
`openCFW/docs/research/littlefs-version-audit.md`. No post-`v2.10.1` change is
folded into this pristine baseline.

## Snapshot contents

- `lfs.c` and `lfs.h`: upstream filesystem implementation and public ABI
- `lfs_util.c` and `lfs_util.h`: upstream utility implementation
- `LICENSE.md`: complete upstream BSD-3-Clause license
- `PROVENANCE.json`: source identity, file hashes, recovered G2 parameters,
  firmware-span identities, and the safety policy
- `verify_snapshot.py`: offline, read-only integrity and configuration check

The source declares littlefs library version `2.10` and on-disk version `2.1`.
The recovered 32-bit G2 configuration ABI is 84 bytes:

| Parameter | Recovered value |
|---|---:|
| read / program size | 16 / 256 bytes |
| block size / count | 4096 bytes / 3008 |
| block cycles | 500 |
| cache / lookahead size | 4096 / 256 bytes |
| compact threshold | 0 |
| optional buffers and maximum overrides | null / 0 |
| `LFS_THREADSAFE` | disabled |
| `LFS_MULTIVERSION` | disabled |
| `LFS_YES_TRACE` | disabled |
| assertions and debug/warn/error diagnostics | enabled |

Apollo main and the bootloader use different block-device callback tables.
Those G2-specific ports must remain outside this pristine upstream directory.

## Source-integrated utility quartet

openCFW now compiles a shared, bounded freestanding port of the exact
`lfs_max`, `lfs_min`, `lfs_aligndown`, and `lfs_alignup` expressions from
this snapshot's `lfs_util.h`. The openCFW source is
`components/apollo_main/core_overlay/runtime_littlefs_util.c`, SHA-256
`2730d0f39e02d7b6e07396894b796b26d9f73332deff23a685b5a06da0f7fb22`.
It is compiled independently under the Apollo-main and bootloader target
profiles.

The upstream identity for this use is release `v2.10.1`, commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`, tree
`06dd0162169d3cb550cd24a3e34d0e4d02983ad3`, and `lfs_util.h` SHA-256
`f5d249326646c818e62af3cefefe8a57e7b484446a0f48d1050b95e60925088e`.
Its complete BSD-3-Clause terms are retained in `LICENSE.md`; the integration
source retains the upstream copyright and SPDX identifier.

The quartet is scalar-only. `lfs_max`, `lfs_min`, and `lfs_aligndown` are
call-free; `lfs_alignup` resolves its only target relocation directly to the
source-owned `lfs_aligndown`. It owns no filesystem state, configuration
object, literal, callback, block-device operation, or flash access. Four
authenticated stock entries in each image are replaced by non-linking Thumb
`B.W` redirects, for eight redirects total. This integration does not change
the no-format/no-erase hardware safety boundary below.

## Source-integrated Apollo-main file-size accessor

Apollo main now also compiles a bounded freestanding adaptation of the exact
v2.10.1 private `lfs_file_size_` behavior from this authenticated snapshot.
The integration source is
`components/apollo_main/core_overlay/runtime_littlefs_file_size_private.c`,
1,233 bytes with SHA-256
`149094dca037bf50fd389b146446cc55babac0bfa011cf2429688838f94626fb`.
Its header is 4,240 bytes with SHA-256
`3afdf02b583c7b81b5d31d599043f3a8b606d0dbcc3251abb5384a1be9a414c1`.

The source asserts the recovered 32-bit `lfs_file_t` layout and preserves the
upstream writing-state rule: return `max(file->pos, file->ctz.size)` while
`LFS_F_WRITING` is set, otherwise return `file->ctz.size`. Its sole relocation
binds directly to the already source-owned `open_cfw_littlefs_util_max`, so the
runtime closure remains authenticated BSD-3-Clause source reuse. Only the
Apollo-main helper exists in the official images; no bootloader redirect is
added.

This scalar accessor neither includes nor calls a G2 block-device port. It does
not mount a filesystem, mutate media, or authorize hardware format or erase.
Full stock/source evidence is in
`docs/research/littlefs-file-size-source-audit.md`.

## Source-integrated Apollo-main file-rewind leaf

Apollo main also compiles the bounded altered adaptation
`open_cfw_littlefs_file_rewind_private`. Its compatibility baseline is the
exact 192-byte `lfs_file_rewind_` definition at `lfs.c` bytes
`[118157,118349)`, SHA-256
`74638292061613417c2ce7c6bbed200d2bee046c35a7a835fb4d9bb183ab755a`.
This authenticates the selected v2.10.1 source-equivalent behavior; it does not
prove the exact historical Even Realities vendor checkout.

The altered local source is
`components/apollo_main/core_overlay/runtime_littlefs_file_rewind_private.c`,
1,239 bytes with SHA-256
`e6afb5b67671b3219971b19c20290c601568752d814064147f5ccd4118f5acc8`.
Its bounded ABI header is 1,743 bytes with SHA-256
`7430dcd1ad1ea3973d619f2d67d8d8b11a688018d48a3bc26a40e407d1fedb56`.
Both are included in the snapshot verifier's exact production allowlist
alongside the existing bounded littlefs leaves.

The authenticated official function occupies `[0x004CE460,0x004CE472)`:
18 bytes, SHA-256
`be02691b2e7339d7dd1d54b31712c3e8563e5a86f4406a469888640fad9435cd`.
Its sole call seam is the retained private `lfs_file_seek_` at `0x004CE3BC`.
The generated leaf has one relocation, at offset 6, of type
`R_ARM_THM_CALL`, binding
`open_cfw_littlefs_file_seek_private` directly to that seam.

The reviewed Apple-clang leaf is 16 bytes at overlay offset 124,480 and
runtime address `0x007B2964`; its relocated SHA-256 is
`1c2e2b1fded0de515345b90fe34de51a9c0f08a02a5ad983c1120481c51c5783`.
The reviewed Linux-clang leaf is 16 bytes at overlay offset 126,300 and
runtime address `0x007C19E8`; its relocated SHA-256 is
`741669f767e0aa5b9a663f7bae6e5b44e01259efdc15135719394874c917ee62`.
Both unrelocated leaves have SHA-256
`46e8bab056ad39ced45edb5da2612f6470674ab5a428df7f08822f6c2d9e184b`.

## Source-integrated Apollo-main tag-type leaf

Apollo main now also compiles the scalar-only altered adaptation
`open_cfw_littlefs_tag_type2`. Its source authority is the exact 92-byte
`lfs_tag_type2` definition at `lfs.c` bytes `[10326,10418)`, SHA-256
`65f614cf5ed7152f7ad2176547453c329b1f15442e550ef6632b0f7773970f78`.
This identifies the v2.10.1 source-equivalent behavior without claiming the
exact historical Even Realities checkout.

The bounded production files are
`components/shared/littlefs/runtime_littlefs_tag_type2.c`, 789 bytes with
SHA-256
`c2ea0965e62aa126fb4b8e752526b8a926a9088739811cba09dcf7d1ed6f3940`,
and its 883-byte header, SHA-256
`17915b900db79e3e611379645a8780723410e5c826f6bfa7619d86bac28f0b13`.
They expose only the recovered 32-bit `lfs_tag_t` scalar ABI. The leaf has no
relocation, provider, global state, allocation, filesystem object, callback,
or block-device dependency.

The authenticated official body is `[0x004CAE90,0x004CAE98)`, eight bytes,
SHA-256
`a017094f8fc58d202d8c5a588f66dd319248578fa39e0f392ba3c7857d3500ef`.
Its two complete-image direct callers are `0x004CBB26` and `0x004CBC38`.
Apple Clang places the ten-byte source leaf at overlay offset 124,548,
runtime `0x007B29A8`; exact-root Linux places the same ten bytes at offset
186,120, runtime `0x007C1A2C`. Both leaf hashes are
`88be40d05d37142bf0bae8306026d8c405a4f8f441aabd87ee6731557d4149fd`,
with zero relocations.

This promotion is an executable scalar replacement only. It does not mount,
read, program, erase, format, or otherwise access a G2 filesystem or device.

## Source-integrated dual-image tag-chunk leaf

Apollo main and the bootloader both compile the shared scalar-only adaptation
`open_cfw_littlefs_tag_chunk`. Its source authority is the exact 93-byte
`lfs_tag_chunk` definition at `lfs.c` bytes `[10514,10607)`, SHA-256
`406b74c2d10482c959cf1048d9589d00d8b416ee4661203bd339144baa74cd09`,
including the two trailing newlines. The separately authenticated 32-bit
`lfs_tag_t` typedef is at bytes `[9602,9629)`, SHA-256
`cb4dcd6212b1a269371d86dddf98ed74853e2eb43753c5d8f8659abbca167ce2`.

The bounded production source and header are 773 and 879 bytes, with SHA-256
`71851bd05e26e703b8697b9994b556db46511c37e9500da98e3406b37a92c8da`
and
`1061f5d68ff6f81a6f1853bfefe37b77f5f3b8b09e627b1bfa0d191842d1f6f5`.
Both official images contain the same six-byte stock leaf
`000dc0b27047`; each has exactly four authenticated direct callers and no
observed alternate or interior ingress. The compiled six-byte source leaf has
SHA-256
`db1dfda72afb267e96cd4e11eaf5d44659195b0afecbdcd8ed8572c34049df74`
and zero relocations.

Apple Clang places the Apollo-main leaf at overlay offset 124,560, runtime
`0x007B29B4`; exact-root Linux places it at offset 126,380, runtime
`0x007B30D0`. Both profiles place the bootloader leaf at offset 622, runtime
`0x004346E6`. This atomic dual-image promotion only replaces a pure mask and
shift helper; it does not access filesystem state or hardware.

The preceding tag-validity/type1 aggregate included the subsequent atomic
`lfs_tag_isvalid` and `lfs_tag_type1` promotion. Its Apple main/boot overlays
were 124,586/644 bytes
with SHA-256
`043dbfb45fcfb9707616c486ac2e736227f7186af8b25fc71a5e355a8e0ba79a`
and `959923a9b5253bd6409fedb82427b7ff666e2d52bc09ac5c391bc28bfbcc70c2`;
their 3,647,982/149,244-byte components hash to
`1227c4953bfcaeb62fb497b8a6911462a2d25fd3ed7b2bb88eea9dd3fdf13a18`
and `e8924fe19f6f768d01fa7c6ec111a4db5790eb28c423c5be84e09b0996423e20`.
The 4,426,458-byte package hashes to
`f0e7e4c5e090ea558968b6293f3eec0a7f88a6126ea164547c25c8462b60be23`.

Exact-root Linux main/boot overlays are 126,406/644 bytes with SHA-256
`7196c0d0d456b46e125b793d7ab4c6175768067589f4153d9b3ee997011c0314`
and `078b88569f6adb147d3c12c727f29c5f3a6ddeb2f66de7d68122b4096f6ac794`;
their 3,649,802/149,244-byte components hash to
`a8684ae43a99cc692dd6cb95c8d4835cc138492d49bf9fd4a3689d32523913ef`
and `6fff06068442ab3203d124c0adfd5052f216459642f67aa32cc39afffd2c0593`.
The 4,428,278-byte package hashes to
`07cee183416db26bbe13673c1123e4ef19593d6343caa63c6c94791a210dc0dc`.

That preceding tranche's exact Apple package ownership was 125,371 source,
88,074 generated, and 4,213,013 opaque bytes. Apple/Linux flash plans are
712,116/594,109 bytes,
hashing to
`3dc88a1ad27c9fd1720806e190cff629116749b2e38766d331dfee786a05f3a8`
and `f59945999bdff46a4d86cc0d886adafae75ba23d136b7de448adbb1f7c12f3a4`.
These pins establish deterministic offline assembly only; they do not prove
the vendor's exact checkout or authorize hardware use.

## Source-integrated dual-image tag-validity and tag-type1 leaves

Both images compile the shared scalar-only adaptations
`open_cfw_littlefs_tag_isvalid` and `open_cfw_littlefs_tag_type1`. Their exact
upstream definitions are `lfs.c` bytes `[10042,10129)` and `[10232,10326)`,
SHA-256
`bb8e571d6dbddd1fe446ec7b4838979a4ab9bd6d6184e2f8d9b6c00cc0835b13`
and `ebf0229d6e0f78175c43641b09906fea19575fc3f34ac8862ae60159df1ec743`.
The selected v2.10.1 commit is an authenticated source-equivalent baseline,
not proof of Even Realities' exact historical checkout.

The validity source/header are 848/928 bytes with SHA-256
`a91417d6193cdfb9589cd9e62f9b6eebe65e1e11a75ca36d0f42d85c36d907a2`
and `6efcd1b229fb0477285f8fbdfbc6f1c92701a787fb17995a6115bfa5a944c6cd`.
The type1 source/header are 857/893 bytes with SHA-256
`7c0df44bd2ebce1eae4cacbfa174c0f963dd03dcc5719ab386c0400201357b46`
and `0993093546ead7b159179c7aaebbef926be24b39ca5202d04b17f0569ca830f6`.
Their emitted six-/ten-byte text hashes to
`65e477818b1c6002b2ceb88812da258524e438ded36dfa059e034c3bce19624e`
and `079f868da6ae04c0d4ace93e9e9d9132247224f81903b57fba51d407f49ddfcf`,
with no providers or relocations.

Apple main placements are `0x007B29BC` / `0x007B29C4`; Linux uses
`0x007C1A40` / `0x007C1A48`; boot uses `0x004346EC` / `0x004346F2`. This
atomic promotion replaces pure scalar helpers only. It does not mount, read,
program, erase, format, or otherwise access a G2 filesystem or device.

## Source-integrated dual-image tag-type3 leaf

Both images now also compile the shared scalar-only adaptation
`open_cfw_littlefs_tag_type3`. Its source authority is the exact 94-byte
`lfs_tag_type3` definition at `lfs.c` bytes `[10420,10514)`, SHA-256
`3cc2c9ec46ebb7fc3d3d71c6b39b235a5da0cde23adf2c182cafd24d6410b53e`.
The selected v2.10.1 commit remains an authenticated source-equivalent
baseline, not proof of Even Realities' exact historical checkout.

The production source/header are 857/893 bytes with SHA-256
`6940b4ac0622dc1f2b84a0c663dc1522dfc7b198f59d6f452828adfd299e37c8`
and `4e3b70d5ad8e8fce0e5dc2bd43fc8459c62c742d84a93f949bf0dd4fb44fe869`.
Both official images contain the same eight-byte stock body
`000d4005400d7047`; complete-image scans authenticate 30 main and 17 boot
direct callers. The compiled six-byte source leaf hashes to
`a6781f0a92086cca25476ca00824d8f0fd736ac7d800aa9e3f6e4d6544490921`
and has zero providers and zero relocations.

Apple main places the leaf at offset 124,588 / `0x007B29D0`; exact-root Linux
uses 186,160 / `0x007C1A54`; boot uses 644 / `0x004346FC` under both profiles.
At that preceding tranche, the Apple main/boot overlays were 124,594/650 bytes and components were
3,647,990/149,250 bytes. The 4,426,472-byte package hashes to
`96f5309c2f77834a2c034b00d04618f0fa42ea3019924d5d51047f7a54c3db4d`.
Linux produces 126,414/650-byte overlays, 3,649,810/149,250-byte components,
and a 4,428,292-byte package hashing to
`e56f78421dd83283e3d4e3f4a6b61a3400260c2618719cc6051453dd9e249bc1`.

Focused production qualification passes five tests. At that preceding
milestone, the separate bounded `lfs_tag_size` candidate also passed five tests
but remained absent from the production allowlist, configs, manifests, and
flash map. `lfs_tag_id` advanced to the now-preceding atomic dual-image
production boundary below; tag-size is promoted by the current boundary that
follows it. None of these scalar helpers imports a G2 block-device port
or authorizes signing, flashing, mount, format, erase, reset, boot, or
hardware operation.

## Source-integrated dual-image tag-ID leaf

Both images now also compile the shared scalar-only adaptation
`open_cfw_littlefs_tag_id`. Its source authority is the exact 91-byte private
definition at `lfs.c` bytes `[10702,10793)`, SHA-256
`50140c563689852013dfad180ec3b6464c6b6c5b22854f5492d63cf5de57fbe2`.
The private 32-bit tag typedef is independently pinned at
`lfs.c[9602:9629]`, SHA-256
`cb4dcd6212b1a269371d86dddf98ed74853e2eb43753c5d8f8659abbca167ce2`.
The selected v2.10.1 commit remains an authenticated source-equivalent
baseline, not proof of Even Realities' exact historical checkout.

The production source/header are 845/872 bytes with SHA-256
`5b6c3ce0f4236d6c6bc0a12891e41929e9034a7ddc2f68bd4f6a1d5d4fa07638`
and `5d6d1c5df9a0fb31f80ad0f6a876795cb154b039fa72df17c615b38cd5e2099e`.
Both official images contain the same eight-byte stock body
`800a8005800d7047`, SHA-256
`0843abb3e9ef39afac8e69ae1e181efa0b5b5c8ebf53e20844b53fdf245b1036`;
complete-image scans authenticate 50 main and 41 boot direct callers. The
compiled six-byte source leaf `c0f389207047` hashes to
`6194594e24288e708887a0e938b2a54401c8c732210d91af7a5927d03bd3604c`
and has zero providers and zero relocations.

Apple main/boot placements remain
`124,596` / `0x007B29D8`
and `650` /
`0x00434702`; exact-root Linux uses
`186,168` / `0x007C1A5C`
and `650` /
`0x00434702`. These final placements are reproduced by both reviewed build
profiles. This scalar promotion does not
mount, read, program, erase, format, or otherwise access a G2 filesystem or
device.

## Current source-integrated dual-image tag-size leaf

The current atomic production boundary selects the shared scalar-only
`open_cfw_littlefs_tag_size` adaptation for both images. Its source authority
is the exact 87-byte private definition at `lfs.c[10793:10880]`, SHA-256
`9df85bc43ca9f90ef58c425c5fd9bbbbf53585093be5fad0cc580fc88814ea5c`.
The exact `lfs_tag_t` and `lfs_size_t` declarations are independently pinned
at `lfs.c[9602:9629]` and `lfs.h[974:1002]`, with SHA-256
`cb4dcd6212b1a269371d86dddf98ed74853e2eb43753c5d8f8659abbca167ce2`
and `e61a4bdad54f4bb8a78f53764fd1043376bd4d922f34d2dd554beab89cd0561f`.
The selected v2.10.1 commit is an authenticated source-equivalent baseline,
not proof of the exact vendor checkout.

The local source/header are 854/1,000 bytes with SHA-256
`533bbfcbfc2440e02b79692a2a7ccff87c3cb62cbb0788c1d5bf806fd3bca849`
and `0f29febdc25b081de1821a41c9065870c02154375985bf648d8e1b63f6cc3528`.
Apollo main `[0x004CAEB8,0x004CAEBE)` and bootloader
`[0x00410BC0,0x00410BC6)` contain the same six-byte stock body `8005800d7047`,
SHA-256
`8596106584e598a657aea7fdd2e1156a748158d2d63d9c121c92587fabbdf8ca`;
complete scans authenticate 15 main and 14 boot callers. Apple production
builds emit provider- and relocation-free text `6ff39f207047`, SHA-256
`35890ebcdee5cb7f51b3e8d874201b7e0214f6111eebe56c772133f259cf9b54`.

Final Apple/Linux placements, patches, and aggregate identities are closed in
the explicit build-evidence ledgers. Tag-ID remains the settled preceding
source-integrated milestone. The production tag-size leaf performs only
`tag & 0x000003ff`; it does not mount, read, program, erase, format, or
otherwise access a G2 filesystem or device.

## Safety boundary: no format or erase

The pristine library translation units in this subtree are **reference-only**
and are not linked wholesale into an openCFW image. Only exact allowlisted,
bounded local adaptations are production-registered. Neither the snapshot nor
those adaptations contain a G2 block-device port or authorize a hardware
format/erase workflow.

Do not call `lfs_format`, `lfs_migrate`, the recovered erase callback, or any
mutating littlefs API on G2 hardware. Before any mutating redirect is enabled:

1. Capture a complete external-flash image.
2. Mount a copy read-only with this exact core and the recovered geometry.
3. Validate the superblock, disk version, directory tree, file contents, and
   `lfs_fs_stat` results against the official implementation.
4. Exercise writes, rename/remove, sync, and power-loss behavior only on
   disposable image copies.
5. Require reviewed byte-level golden-image results before any device format
   or erase operation can be introduced.

`verify_snapshot.py` only reads local files. If the official main and
bootloader images are available, it authenticates each complete image before
reading and checking the two 84-byte configuration spans. It never invokes
filesystem code and never writes an image:

```sh
python3 openCFW/third_party/littlefs/verify_snapshot.py
```

## License

littlefs is distributed under the BSD-3-Clause license. The complete,
unchanged upstream license is in `LICENSE.md`; each source/header also retains
its SPDX identifier and upstream copyright notice.
