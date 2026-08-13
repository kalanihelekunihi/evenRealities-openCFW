# G2 littlefs next closed-leaf audit

Status: production-integrated; the original research forecast below is
retained as the pre-integration decision record

Scope: authenticated littlefs v2.10.1 utility and private-leaf identification
in the official G2 `2.2.6.10` Apollo-main and bootloader images; source and
target compilation experiments only; no signing, flashing, external-flash
access, or hardware use

## Result

The lowest-risk dual-image littlefs source tranche was not a structure
operation. It was the retained `lfs_util.h` helper cluster immediately before
the already source-owned `lfs_scmp` entry.

The first recommended production increment, now integrated, is:

1. `lfs_max`;
2. `lfs_min`;
3. `lfs_aligndown`;
4. `lfs_alignup`.

All four are unequivocal upstream v2.10.1 functions in both images. `max`,
`min`, and `aligndown` are call-free. `alignup` has one outgoing edge to
`aligndown`, so the four-function increment is source-closed. They have no
pointer, structure, global, configuration, literal, callback, allocation,
filesystem-format, block-device, or MSPI dependency.

The same scan closes seven additional dual-image utility functions:
`lfs_npw2`, `lfs_ctz`, `lfs_popc`, `lfs_fromle32`, `lfs_tole32`,
`lfs_frombe32`, and `lfs_tobe32`. The endian quartet and fallback-bitops trio
have since been production-integrated. `lfs_npw2` and `lfs_ctz` retain the
official fallback
selection by compiling their exact upstream fallback branch (equivalent to
`LFS_NO_INTRINSICS`) rather than letting Clang select its builtin branch.
That preserves the official deterministic edge behavior and removes a
needless caller-input proof.

After the utility tranche, these previously adjacent private helpers are
also source-ready:

- the `lfs_fs_disk_version_major` / `lfs_fs_disk_version_minor` pair, closed
  over the already source-owned `lfs_fs_disk_version`;
- `lfs_mlist_isopen`, a call-free list predicate used only by retained
  assertion sites.

`lfs_alloc_lookahead` is unequivocally identified and call-free, but ranks
after those helpers because it owns four `lfs_t` offsets, writes the
lookahead bitmap, and is reached through one stored Thumb callback pointer
per image.

## Authoritative inputs

| Image | Bytes | SHA-256 | Mapping |
|---|---:|---|---|
| `ota_s200_firmware_ota.bin` | `3,523,396` | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` | 32-byte preamble; installed payload at `0x00438000` |
| Apollo-main installed payload | `3,523,364` | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` | package bytes after the preamble |
| `ota_s200_bootloader.bin` | `148,599` | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` | raw image at `0x00410000` |

The source comparator is the pristine snapshot in
[`../../third_party/littlefs`](../../third_party/littlefs):

| Property | Value |
|---|---|
| Release | littlefs `v2.10.1` |
| Commit | `0494ce7169f06a734a7bd7585f49a9fa91fa7318` |
| Tree | `06dd0162169d3cb550cd24a3e34d0e4d02983ad3` |
| `lfs_util.h` SHA-256 | `f5d249326646c818e62af3cefefe8a57e7b484446a0f48d1050b95e60925088e` |
| `lfs.c` SHA-256 | `81a209e8551754d13b24fc0a2b6707fb3b2475e14feba00bf0df722b98a31398` |
| License | BSD-3-Clause |

This is the established exact source-equivalent release pin. It does not
claim that the stripped image can prove the historical private checkout
identity.

## Identical dual-image utility cluster

Apollo main contains the cluster at
`[0x004CA6F8,0x004CA80A)`. The bootloader contains it at
`[0x00410400,0x00410512)`. The complete 274-byte spans are byte-identical
and hash to:

```text
e45940528fb1cc4eed248f52fa91760b2fec4e2e6829a2acde4da43995fc72e5
```

The function order is exactly the order in pristine `lfs_util.h`. The
already integrated `lfs_scmp` occupies the only omitted row in the source
candidate set.

| Function | Apollo-main range | Bootloader range | Bytes | Stock SHA-256 |
|---|---|---|---:|---|
| `lfs_max` | `[0x004CA6F8,0x004CA700)` | `[0x00410400,0x00410408)` | 8 | `3caa49d8a68e47b2cd91fcb01cae26b6262c904e8b96d8b3ba35f7fb33d07464` |
| `lfs_min` | `[0x004CA700,0x004CA708)` | `[0x00410408,0x00410410)` | 8 | `7ec81166f84c44a60f4ecf93ad37d93f52ec00c77bb5db5a7dda659b1319c8a3` |
| `lfs_aligndown` | `[0x004CA708,0x004CA714)` | `[0x00410410,0x0041041C)` | 12 | `d0d7407bcf93abaef33623047467d1230d2176ce9b4a4e93bfcd8adde884f349` |
| `lfs_alignup` | `[0x004CA714,0x004CA720)` | `[0x0041041C,0x00410428)` | 12 | `18874b0eb5cf5c7bd6f20b2b29f787157294b9e9be16d14ab0d9064d44a97c37` |
| `lfs_npw2` | `[0x004CA720,0x004CA77A)` | `[0x00410428,0x00410482)` | 90 | `291ab0ccd15efe1085ce5bcdc6551581ed4eccf67fa84f6560c4500fd68b8b63` |
| `lfs_ctz` | `[0x004CA77A,0x004CA78A)` | `[0x00410482,0x00410492)` | 16 | `4ae07bfa492e5dfad5869ea491ca43f720e6fc153315a126e2e686313c3de08c` |
| `lfs_popc` | `[0x004CA78A,0x004CA7B2)` | `[0x00410492,0x004104BA)` | 40 | `2cc25090f38dd5c2121cb4bfc7ddf0bd71df984312c9b9c52e87feeef5aea872` |
| `lfs_scmp` | `[0x004CA7B2,0x004CA7B6)` | `[0x004104BA,0x004104BE)` | 4 | `787fad2973d1b4f1c6c585f29ee07707e6951499c3772a9e8e4e1bc997ba94fe` |
| `lfs_fromle32` | `[0x004CA7B6,0x004CA7D8)` | `[0x004104BE,0x004104E0)` | 34 | `0666243f83f942c21b4428e4027b6f7815771c2f8a51dcddc550ffa9710add76` |
| `lfs_tole32` | `[0x004CA7D8,0x004CA7E0)` | `[0x004104E0,0x004104E8)` | 8 | `b217ac730c7d1b392e0f57a67477d6db88a751a8d3afb3a50ff5bebe0e273f66` |
| `lfs_frombe32` | `[0x004CA7E0,0x004CA802)` | `[0x004104E8,0x0041050A)` | 34 | `a0fc2d34d780abf4de23efe08746eefee5cb84cae2728950c4123464e0f952c9` |
| `lfs_tobe32` | `[0x004CA802,0x004CA80A)` | `[0x0041050A,0x00410512)` | 8 | `b217ac730c7d1b392e0f57a67477d6db88a751a8d3afb3a50ff5bebe0e273f66` |

There is no padding, shared tail, literal pool, or fall-through between these
entries. Each predecessor returns before the next entry.

### Exact source identities

The first four pristine expressions are:

```c
static inline uint32_t lfs_max(uint32_t a, uint32_t b) {
    return (a > b) ? a : b;
}

static inline uint32_t lfs_min(uint32_t a, uint32_t b) {
    return (a < b) ? a : b;
}

static inline uint32_t lfs_aligndown(uint32_t a, uint32_t alignment) {
    return a - (a % alignment);
}

static inline uint32_t lfs_alignup(uint32_t a, uint32_t alignment) {
    return lfs_aligndown(a + alignment-1, alignment);
}
```

The official machine code is a direct translation:

```text
lfs_max:       compare; choose larger unsigned argument; return
lfs_min:       compare; choose smaller unsigned argument; return
lfs_aligndown: UDIV quotient; multiply quotient by alignment; return
lfs_alignup:   a += alignment; a -= 1; BL lfs_aligndown; return
```

The unsigned addition in `alignup` deliberately wraps modulo `2^32`.
`alignment == 0` has never been supported: the official `UDIV` has the same
nonzero divisor precondition as the source `%`. The retained callers pass
validated filesystem geometry sizes or fixed nonzero alignments, so source
replacement does not introduce that precondition.

The endian helpers also match the exact upstream fallback bodies in the
official IAR images. Apollo510 is little-endian, so the reviewed Clang
profiles select these equivalent forms:

```text
lfs_fromle32 / lfs_tole32: identity
lfs_frombe32 / lfs_tobe32: REV (32-bit byte swap)
```

No filesystem or structure state participates in any utility helper.

## Complete utility entry topology

Both complete images were scanned:

- at every halfword for Thumb-2 `BL` and non-linking `B.W`;
- at every halfword for narrow unconditional, conditional, `CBZ`, and
  `CBNZ` branches;
- at every byte for stored even and Thumb entry or interior addresses.

For all eleven unintegrated utility functions:

- the only direct entry edges are the `BL` callers counted below;
- no non-linking wide or narrow external branch enters an entry;
- no external branch or call enters an interior halfword;
- no stored entry or interior pointer exists;
- no vector, callback table, jump table, or data object is owned.

The ordered caller-address hash is SHA-256 over packed little-endian
addresses. The call hash is SHA-256 over the concatenated four-byte call
instructions in address order.

| Function | Image | Callers | Caller-address SHA-256 | Call-instruction SHA-256 |
|---|---|---:|---|---|
| `lfs_max` | main | 4 | `fece20308dc407f9471f6d36dfbdbc428aa11c36c2823f5092d2732e775418e8` | `68172fa84c89c7fbbd5a9e08f189f35a4be945974525084959622cf881e462a9` |
|  | boot | 4 | `db4b59cfd0ea98dea6de8e0a949da3b85005c8d4ccf8ee56c482aaab8e40f47d` | `5dc0f81da4685dbfc6ab840aa1ab56b7a7ba46374241f4da0b4f55e2edcc72a5` |
| `lfs_min` | main | 31 | `4e9fac593edd2cadf944644ec1765ab713b67cd5fe231d7f192f93b995bd4e4f` | `e4917521d25965b50e5cdfe96fe1041608e982a74c83dc0690106b219827605c` |
|  | boot | 31 | `23f4e3fc136f9b700f199c96ea41b9f9fbf6367639ee252741cc429bb7c07cda` | `374b6e58126272c30f80399882fbc6936679b18f37c1c7b1e7b948828a323ca2` |
| `lfs_aligndown` | main | 5 | `f9adfb18cf7cf54a61ff58d1742d9b7f2d35b49b49c6c9e68012901990ae1300` | `baa14112e260232011181911b0b0007a27decab41d76ed26ca8ef9116baba430` |
|  | boot | 5 | `e4bb189342524b004da5d76f0367be7cbaa25bbb7f7156d173910e7cb712fa25` | `baa14112e260232011181911b0b0007a27decab41d76ed26ca8ef9116baba430` |
| `lfs_alignup` | main | 6 | `27ff14b7bd0f16a971476b04e6fa0b686a7112eb4d1cd3d79ab1c1ed19b8cbbc` | `7b50bb0e437bca66c10228b7a3838d93091233bd4a6e486e058fdd533124aeac` |
|  | boot | 6 | `cd6b5e56cecea062ed551ff9653ddbb8feac40514f7620b5e424e441f5da6bb9` | `693c7a6c42892fc0b2991be36ca9a1d878608518a9db3061e26b3ce15a3fb331` |
| `lfs_npw2` | main | 3 | `38012844589378f3550200486b07880ede473e5ad35899ef3cf35ca6725206b5` | `facb27dc7efa9757918b3952902469bece6d65f277e931dccd27978e56c8936a` |
|  | boot | 3 | `cdb2363fa879cb8c7273771bcfad2072a11b2171f6aa21a56942d6e30ff54587` | `b03d4d0b64009006778957e5c191fa4953daf1472e011037ffa225c73652a703` |
| `lfs_ctz` | main | 2 | `be6b83ffb1ee769987dc6d8a66c895baba503001529250ff8bca47e8ce0920d1` | `58694e5cb022a1ad58966c161ff8ea2da2ed7eb65c80994a73be44c8e69217be` |
|  | boot | 2 | `eb712fed392b1618739d675addfa5041c81828ec77490aa5a28c186e7af16d2b` | `5249923c7b5f4ed7ecc8cc9a0c0019d2f56453a9ee5a758f6d2edb7130561bb8` |
| `lfs_popc` | main | 2 | `48ae20e70e24a9b415df273660b96f9c194571d71e52dc07696b02c547700e34` | `69e1ae3dc7a2d3c6c7584f985bdb4f8e4b4d7d7ea0cfa8c070e85f392e543494` |
|  | boot | 2 | `419d1a09391db2dbceebe2cbc55e8abacf40e287c111284186b06fa087ced7be` | `eac3e107bb3693f04569336f6c7ccd2bd111f67e99af9266ef2c143a8b6a44f9` |
| `lfs_fromle32` | main | 26 | `e31d5e49b0d3d9add81d5c1b715999de65c24f03ecf77f26bc45ca79fe738b2d` | `bcdf80fe96884b8c1ea2420f735095c7f6a57fd6ba20ab719015a2574a88493c` |
|  | boot | 26 | `264efba92915eabc31125f55e64c976874594e100517c37c0a158105dcd635d0` | `05dd81fda3b837996366dd91d47c8fd632d43a2f8054550104904bab92908976` |
| `lfs_tole32` | main | 19 | `48db1319f5574c43bb4d05dcdcfd08684d212c75cb96e5d36111ebe854861f4f` | `44e91dd2102b812487ae2481038cb3e3f96e2094bb7917a336ce8752deffaa75` |
|  | boot | 19 | `006824bf38a74c325ecbcd802d36eb495a8f44d19081d9365cb148c83ada9def` | `9dbb2c053d8fbcc91c2355be96d1eb32384da8322ad83c00cd90ea6788deb512` |
| `lfs_frombe32` | main | 4 | `22bd22451a943a39a30b54a7309da70c08cf86ced375d654b5ed83be4ce4d7d9` | `19531d5ffc21ba2a338dfa396b607ed2f8a43d4c3de8142d395fd778f5c53dd5` |
|  | boot | 4 | `87b688ea884e40a88a40ffd0d13163090109f8149abcf140c6c072e4fb013861` | `19531d5ffc21ba2a338dfa396b607ed2f8a43d4c3de8142d395fd778f5c53dd5` |
| `lfs_tobe32` | main | 2 | `2b184d419a0bf749247a7ba30e596b01ba778f824ce5fd01c5a7b96828b6cc3c` | `c4bc23d34a3b86a0bb2c9f3e0bee2f8714747023d114c0ae55239d586b27febd` |
|  | boot | 2 | `c27e310b5184d4c38df655d98707dc68d1fef93ac0b3e2f5185a3ed308f9784d` | `21c2a7f67248b726b8f3ab8d5cc50d7de2b88c85afa60d0998110e2d8f3c00c2` |

The complete caller lists for the first recommended increment are:

```text
lfs_max main:
0x004CACC8 0x004CDF3A 0x004CE1BC 0x004CE480

lfs_max boot:
0x004109D0 0x00413A8A 0x00413D0C 0x00413FCC

lfs_min main:
0x004CA87C 0x004CA8CA 0x004CA8F0 0x004CA91C 0x004CA9B0
0x004CA9BC 0x004CAA48 0x004CAAC6 0x004CAC92 0x004CB150
0x004CB36E 0x004CB422 0x004CB46E 0x004CB496 0x004CB4C2
0x004CB4E8 0x004CBE8A 0x004CC002 0x004CC304 0x004CC32A
0x004CC344 0x004CCA16 0x004CD78C 0x004CDC84 0x004CE064
0x004CE080 0x004CE28E 0x004CEDA6 0x004CEDB0 0x004CEE74
0x004CF0DA

lfs_min boot:
0x00410584 0x004105D2 0x004105F8 0x00410624 0x004106B8
0x004106C4 0x00410750 0x004107CE 0x0041099A 0x00410E58
0x00411076 0x0041112A 0x00411176 0x0041119E 0x004111CA
0x004111F0 0x00411B92 0x00411C62 0x00411F64 0x00411F8A
0x00411FA4 0x0041261E 0x004132DC 0x004137D4 0x00413BB4
0x00413BD0 0x00413DDE 0x0041448A 0x00414494 0x00414558
0x004147B2

lfs_aligndown main:
0x004CA71A 0x004CA942 0x004CA998 0x004CAD18 0x004CB4D0

lfs_aligndown boot:
0x00410422 0x0041064A 0x004106A0 0x00410A20 0x004111D8

lfs_alignup main:
0x004CA9A8 0x004CAB38 0x004CB4E0 0x004CC30C 0x004CC57C
0x004CCA0A

lfs_alignup boot:
0x004106B0 0x00410840 0x004111E8 0x00411F6C 0x004121DC
0x00412612
```

The first `aligndown` caller in each image is the sole outgoing call from
`alignup`. Therefore redirecting both entries closes that edge entirely in
source.

## Official intrinsic selection and the focused gap it closes

The official IAR build selected the fallback branches of `lfs_npw2`,
`lfs_ctz`, and `lfs_popc`; the 90-, 16-, and 40-byte bodies are identical in
both images and match those fallback expressions.

Compiling pristine `lfs_util.h` under Clang without controlling this choice
would select `__builtin_clz` / `__builtin_ctz`. That is not a faithful first
replacement:

- the C builtins have undefined zero-input cases;
- the official fallback has deterministic instruction behavior at those
  edges;
- Clang's generated `CLZ` / `RBIT; CLZ` bodies are only 12 / 10 bytes and
  therefore visibly select a different conditional source branch.

The focused resolution is to compile these functions with the exact upstream
fallback branch, as if `LFS_NO_INTRINSICS` were defined. No decompilation or
caller-value assumption is necessary.

Under the production image profiles, the fallback bodies are:

| Function | Main `-O2` target | Boot `-Oz` target | Closure |
|---|---:|---:|---|
| `lfs_npw2` fallback | 72 B, SHA `ef17f9ce9257384acd6010c107338f9d45b2c43b60ef635e970ba54416d3496a` | 56 B, SHA `1048afe6eb2c306231e410f0a864ab5bfab3c9b0567e1fba6ec61f8bae53094a` | call-free |
| `lfs_ctz` fallback | 16 B, SHA `743d892e08268653cd97dcfd35b494def81aff4745bd7467ef6de217189bee1a` | same | one `R_ARM_THM_CALL` to source `lfs_npw2` |
| `lfs_popc` fallback | 42 B, SHA `7b7c7ddb5d9680c5dc736cd13fe67090824cbceece86d99c4f14690abeb230ff` | 42 B, SHA `e537e00ef37eced668a9d421f28e84d54a2b6ea09ea1cfda00f96ec1d65891f7` | call-free |

The `lfs_ctz` hashes in this research table describe the unlinked object
body. Its image-specific hashes after resolving the internal call relocation
are recorded in the current production result below.

This turns the only utility configuration ambiguity into an explicit,
reviewable source-build parameter.

## Target compilation under both image profiles

The exact upstream expressions were compiled with the current production
profiles:

```text
Apollo main:
--target=thumbv7em-none-eabi -mthumb -O2 -ffreestanding
-fno-jump-tables -fomit-frame-pointer -fno-builtin
-mno-unaligned-access -fno-unwind-tables
-fno-asynchronous-unwind-tables -fropi -Wall -Wextra -Werror

Bootloader:
--target=arm-none-eabi -mcpu=cortex-m55 -mthumb -Oz -ffreestanding
-fno-jump-tables -fomit-frame-pointer -fno-builtin
-mno-unaligned-access -fno-unwind-tables
-fno-asynchronous-unwind-tables -fropi -Wall -Wextra -Werror
```

| Function | Main target bytes / SHA-256 | Boot target bytes / SHA-256 | `.text` dependency |
|---|---|---|---|
| `lfs_max` | 8 B / `49828a023d7febe0a7005f10d64021e7ffebe5354dfb50fdfbef19490a76dac0` | 8 B / `00cbab254132bf12554d58b011edf1b5e3b1e36ff5d55a671d2ab04e5b8428a5` | none |
| `lfs_min` | 8 B / `761921b20c0aec1b2d8aacbcffd07ba9baf30f1c57c0a89311028adc55e8c126` | 8 B / `36bb5e2d905d59628b5170a2cfecbf56f3200abb3207bfa30b50eaf3b4b44ab4` | none |
| `lfs_aligndown` | 8 B / `965ce09e34fe2ef897bc091faf02f8211bf344c025d769cf440c747fb5f555ee` | same | none |
| `lfs_alignup` | 8 B / `977169907db28276dc49c7f55020c30af81d04b8fe43d98393cea03b49fccdd1` | same | one `R_ARM_THM_JUMP24` to source `lfs_aligndown` |
| `lfs_fromle32` | 2 B / `c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8` | same | none |
| `lfs_tole32` | 2 B / `c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8` | same | none after optimization |
| `lfs_frombe32` | 4 B / `7a8f0cc1ae130c65908d3dbd4e89f7c7bd898743a4ee62deced9203383df3d11` | same | none |
| `lfs_tobe32` | 4 B / `90a54a1f68a806a1795bd044856908235426b3c0f67be605fb94d3d5344a747f` | same | one `R_ARM_THM_JUMP24` to source `lfs_frombe32` |

All arguments and returns are 32-bit scalars in the standard Arm registers.
There are no data relocations, literals, undefined runtime helpers, or
global-state references. The branch relocations listed above resolve wholly
inside the proposed source tranche.

The target bodies need not reproduce the IAR instruction choices. They
compile the exact selected upstream semantics and fit the existing overlay
model, where a complete four-byte stock entry redirect transfers control to
source-owned text.

## Disk-version major/minor pair

The next source-closed private pair sits between the already source-owned
`lfs_fs_disk_version` and `lfs_alloc_ckpoint` leaves:

| Property | Major | Minor |
|---|---|---|
| Main range | `[0x004CB0CA,0x004CB0D6)` | `[0x004CB0D6,0x004CB0E0)` |
| Boot range | `[0x00410DD2,0x00410DDE)` | `[0x00410DDE,0x00410DE8)` |
| Stock bytes | 12 | 10 |
| Stock SHA-256 | `c9ab0025e9e77a75e9240efbd5b15da22807bdaa9f9deaf2cb425d4850f3bf08` | `c03343d554dbdd887485eff548d1f2852a1e2f1fe86e662759d478f1d28c7253` |
| Main callers | `0x004CF03A`, `0x004CF06C`, `0x004CF130` | `0x004CF046`, `0x004CF056`, `0x004CF064`, `0x004CF128` |
| Boot callers | `0x00414712`, `0x00414744`, `0x00414808` | `0x0041471E`, `0x0041472E`, `0x0041473C`, `0x00414800` |

All callers belong to the retained `lfs_mount_` disk-version validation and
diagnostic paths. Each helper has one outgoing `BL` to the immediately
preceding, already source-owned `lfs_fs_disk_version` entry. There are no
non-linking branches, stored pointers, or interior entries.

The exact source is:

```c
static uint16_t lfs_fs_disk_version_major(lfs_t *lfs) {
    return 0xffff & (lfs_fs_disk_version(lfs) >> 16);
}

static uint16_t lfs_fs_disk_version_minor(lfs_t *lfs) {
    return 0xffff & (lfs_fs_disk_version(lfs) >> 0);
}
```

Both target profiles emit 10 bytes per helper. The raw object bodies hash to
`ebb72edfdb508cbf5b617452eb60cbceb58bfdfc879dcece076544efa75c092f`
for major and
`da349b05b3a26d6a22ba3f707c4c21e1591915aeb8451e21f7509905926a4b9d`
for minor. Each has one `R_ARM_THM_CALL` relocation to
`open_cfw_littlefs_disk_version`; there are no other dependencies.

`LFS_MULTIVERSION` is disabled in both authenticated 84-byte configuration
objects, and the source-owned disk-version function ignores `lfs`. The pair
therefore owns no `lfs_t` field offset.

## `lfs_mlist_isopen`

The call-free private list predicate is identical in both images:

| Property | Apollo main | Bootloader |
|---|---:|---:|
| Range | `[0x004CB082,0x004CB0A0)` | `[0x00410D8A,0x00410DA8)` |
| Size | 30 B | 30 B |
| SHA-256 | `e4963bfc9db9aa487d15261ebce9dd5b1429c708f6fe78ff47968718821c0c4e` | same |
| Direct callers | 9 | 6 |
| Stored/non-linking/interior entries | none | none |

Main callers:

```text
0x004CFAA4 0x004CFADC 0x004CFB14 0x004CFB50 0x004CFB8C
0x004CFBC2 0x004CFBF4 0x004CFC3A 0x004CFC74
```

Boot callers:

```text
0x00415156 0x0041518C 0x004151D0 0x0041520C 0x00415242
0x00415296
```

The retained call sites correspond exactly to the assertion-line fingerprint:

- main: upstream lines `6119`, `6155`, `6171`, `6189`, `6207`, `6225`,
  `6258`, `6287`, and `6318`;
- boot: lines `6119`, `6155`, `6189`, `6207`, `6225`, and `6318`.

This is independent corroboration that assertions are enabled. The source
function itself does not call the assertion machinery.

The only ABI contract is:

- 32-bit pointers;
- `struct lfs_mlist.next` at offset zero;
- 32-bit C `bool` return convention through `r0`.

It does not receive or dereference `lfs_t`. The main `-O2` target is 44 bytes,
SHA-256
`6161db6d0867e47749654ae90b560ae499a03f8c7708b98b2f1f916e6ef450f1`.
The boot `-Oz` target is 18 bytes, SHA-256
`9b7caac591f8aea5d0eff0dc2b5ff7ff15ba85ab156ba5f95d47b1e4181db489`.
Both are call-, literal-, relocation-, and undefined-symbol-free.

## `lfs_alloc_lookahead`

This exact source-equivalent leaf was originally audited at:

| Property | Apollo main | Bootloader |
|---|---:|---:|
| Range | `[0x004CB0F6,0x004CB12E)` | `[0x00410DFE,0x00410E36)` |
| Size | 56 B | 56 B |
| SHA-256 | `58285c138461a673be0bed2c5376f8d739e40e2aea753ad05d5061bfbc9265cf` | same |
| Direct calls | none | none |
| Stored Thumb entry | `0x004CBED8 -> 0x004CB0F7` | `0x00411BE0 -> 0x00410DFF` |
| Non-linking/interior entries | none | none |

The stored entries are the callback literal consumed by `lfs_alloc_scan`
before its `lfs_fs_traverse_` call. They name the official entry plus the
Thumb bit, not an interior instruction. A complete entry redirect remains
safe, but production evidence must pin these literals because this function
is callback-reached rather than directly called.

The exact ABI fields proved by both official bodies are:

| Field | Offset |
|---|---:|
| `lfs_t.lookahead.start` | `0x54` |
| `lfs_t.lookahead.size` | `0x58` |
| `lfs_t.lookahead.buffer` | `0x64` |
| `lfs_t.block_count` | `0x6C` |

The already authenticated target layout also has 32-bit pointers and
`sizeof(lfs_t) == 0x80`. `lfs_alloc_lookahead` does not dereference
`lfs->cfg`, invoke a block callback, allocate, or access flash. It updates
only one bit in the in-memory lookahead bitmap and returns zero.

The main `-O2` target is 50 bytes, SHA-256
`ff36aeaff70307ae466d9f7fafacad678c706db1551b18d98d7fe68bf3dc5eef`.
The boot `-Oz` target is 48 bytes, SHA-256
`bd8e7c926d98a940f215cd41a2fb5932bfbf1abcf7378839dcadd537ae55324d`.
Both have zero `.text` relocations and undefined symbols.

This candidate was subsequently promoted after a focused host/oracle bitmap
test; the historical ranking below explains why the lower-ABI utility
helpers were promoted first.

## Ranked production order

| Rank | Source increment | Readiness | Reason |
|---:|---|---|---|
| 1 | `lfs_max` + `lfs_min` | integrated | two pure call-free scalar selectors; exact dual-image boundaries and complete topology |
| 2 | `lfs_aligndown` + `lfs_alignup` | integrated | one call-free scalar leaf plus one source-closed tail; no state |
| 3 | endian quartet | integrated | pure scalar identity/byte-swap operations; Apollo510 endianness is unequivocal |
| 4 | `lfs_npw2` + `lfs_ctz` + `lfs_popc` fallback tranche | integrated with explicit `LFS_NO_INTRINSICS` selection | preserves official IAR fallback semantics and closes `ctz -> npw2` |
| 5 | disk-version major/minor pair | integrated | source-closed over the already integrated constant disk-version leaf |
| 6 | `lfs_mlist_isopen` | integrated | call-free; only zero-offset list linkage and assertions-enabled retention |
| 7 | `lfs_alloc_lookahead` | integrated | four `lfs_t` offsets, one RAM bitmap write, and stored callback topology |

No candidate in ranks 1 through 7 requires decompiling an upstream
algorithm. The focused disassembly was needed only to establish entry
boundaries, compiler-conditional selection, call closure, stored-pointer
topology, and ABI offsets.

## Validation performed

This audit:

- authenticated both complete official inputs and the installed main
  payload;
- rehashed every selected stock span and the complete identical 274-byte
  utility cluster;
- decoded each selected body with Capstone;
- scanned both complete images for wide and narrow entry/interior branches;
- scanned both complete images byte-by-byte for stored entry/interior
  addresses;
- pinned all utility caller counts plus ordered address and call hashes;
- mapped the list-predicate callers to the authenticated v2.10.1 assertion
  line fingerprint;
- compiled the exact selected expressions with both production target
  profiles;
- inspected function sizes, bytes, relocations, and undefined-symbol
  closure;
- compared the fallback utility source against 10,012 deterministic 32-bit
  values and 80,096 nonzero-alignment pairs on the host.

At the time of this research pass, no production source, overlay, manifest,
aggregate test, or shared source-coverage document was modified. That
statement is historical; the scalar/alignment quartet, endian quartet,
fallback-bitops trio, disk-version major/minor pair, and `lfs_mlist_isopen`
have since been integrated.

## Initial scalar/alignment production integration

The decision below has now been implemented with one shared freestanding
source file,
`components/apollo_main/core_overlay/runtime_littlefs_util.c`, SHA-256
`2730d0f39e02d7b6e07396894b796b26d9f73332deff23a685b5a06da0f7fb22`.
The source retains the copyright and BSD-3-Clause SPDX identifier of
littlefs v2.10.1 commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`, tree
`06dd0162169d3cb550cd24a3e34d0e4d02983ad3`, whose pristine `lfs_util.h`
has SHA-256
`f5d249326646c818e62af3cefefe8a57e7b484446a0f48d1050b95e60925088e`.
The complete license terms remain in `third_party/littlefs/LICENSE.md`.

The exact stock spans and SHA-256 identities remain those in “Identical
dual-image utility cluster” above. All 4/4 `lfs_max`, 31/31 `lfs_min`, 5/5
`lfs_aligndown`, and 6/6 `lfs_alignup` direct callers remain closed by four
authenticated entry redirects per image. The sole outgoing edge is
`lfs_alignup -> lfs_aligndown`; each target build resolves that relocation
inside the shared source unit. There are no external interior entries or
stored pointers. The production mutation is therefore exactly eight
non-linking Thumb `B.W` redirects, with NOP fill across the remainder of each
8- or 12-byte stock entry.

Apollo main places the four eight-byte bodies at overlay offsets 109,616,
109,624, 109,632, and 109,640, respectively, which map to
`[0x007AEF54,0x007AEF74)`. Its complete 114,136-byte overlay has SHA-256
`33e4b70baf06cf5e7b173c127c26972990be29af151bd5e5490b9928f67d0e67`;
the 3,637,532-byte provider has SHA-256
`26efb41119a584cd8b1093ca35fcd87de8c39e051ce715b7719392f13ee9c536`
and ends at `0x007B00FC`.

The bootloader places the bodies at offsets 58, 66, 74, and 82, mapping to
`[0x004344B2,0x004344D2)`. Its complete 140-byte overlay has SHA-256
`671f04e7d78bb2502ea5ca0c8e8752c04fc2939f63793b4bb57ba5f7dd90d0e1`;
the 148,740-byte provider has SHA-256
`23e73b9134cde9822880b678f4df7a7fbc13cf3722a806b7891dca1f96af8460`
and ends at `0x00434504`.

All work was local and offline. No device, serial endpoint, debugger,
flasher, erase path, or hardware execution was accessed.

## Preceding fallback-bitops production result

All artifact pins in this section describe the preceding fallback-bitops
milestone and are superseded by the disk-version and allocator-lookahead
results below.
The current release compiles the exact littlefs v2.10.1
`LFS_NO_INTRINSICS` implementations of `lfs_npw2`, `lfs_ctz`, and
`lfs_popc` from
`components/apollo_main/core_overlay/runtime_littlefs_util_bitops.c`. The
2,795-byte shared source has SHA-256
`405092c6e8fc65a740f951cb2affaad8766e2553c7b8d290ff58f435e8830f47`.
It preserves the upstream edge semantics `npw2(0) == 32`, `npw2(1) == 1`,
`ctz(0) == 0`, and `popc(0) == 0`. The only relocation is the internal
Thumb call `lfs_ctz -> lfs_npw2`; no function has an external, undefined,
literal, or data dependency.

Apollo main places the 72-, 16-, and 42-byte post-link bodies at overlay
offsets 109,648, 109,720, and 109,736, mapping to `0x007AEF74`,
`0x007AEFBC`, and `0x007AEFCC`. Their post-link SHA-256 values are
`ef17f9ce9257384acd6010c107338f9d45b2c43b60ef635e970ba54416d3496a`,
`b4282c027702526c28364bd68157a143a064aa0e277ee1f245890bd6beb56c9c`,
and
`7b7c7ddb5d9680c5dc736cd13fe67090824cbceece86d99c4f14690abeb230ff`.
The complete 114,324-byte overlay has SHA-256
`00318de9ff51e19f77d889fa691a3a2a54e035b1287843bda857f944af58e065`;
the 3,637,720-byte provider has SHA-256
`f0da043e234dc38481059459755e091622d689313cd12e5c8d5155c7b4ba3202`.
Its 3,637,688 installed bytes have SHA-256
`cfa3e79abf4ac4d932d3612ced595f950c1c2355b1890fd9a13e9635c59c2e85`
and end at `0x007B01B8`.

The bootloader places the 56-, 16-, and 42-byte post-link bodies at overlay
offsets 90, 146, and 162, mapping to `0x004344D2`, `0x0043450A`, and
`0x0043451A`. Their post-link SHA-256 values are
`1048afe6eb2c306231e410f0a864ab5bfab3c9b0567e1fba6ec61f8bae53094a`,
`a5616df42c6d3705e9906d0cdce4d6d5b59d0f02b647c59efeb6594c64004ab1`,
and
`e537e00ef37eced668a9d421f28e84d54a2b6ea09ea1cfda00f96ec1d65891f7`.
The complete 282-byte overlay has SHA-256
`b934dbea7624660c3c774eb0f4edd5e73a738fc59023fc69cfac96417dfe2fee`;
the 148,882-byte provider has SHA-256
`1aa7920a16ed2857a2743394c0f62395a2f2477f95c965da47d1e29c4d2d8247`
and ends at `0x00434592`.

The 4,415,834-byte EVENOTA package has SHA-256
`058782604ab6cb946aff0acedbbef7d367bb1d82114f28c9a70276bcdf178e9a`,
boot/main CRC-32C/MSB values `0x1162559F` and `0xB436A24C`, and flash-plan
SHA-256
`2015673f529e550e67c2f219d789746cceef1b022bdcf2db16f1ba451a8aa05e`.
The manifest reports 745 placed, two unresolved, and five container-only
regions, with 114,638 source bytes, 81,477 generated bytes, and 4,219,719
opaque bytes.

The focused production gate passes 6/6 tests in 13.693 seconds.
`./make.sh source` and `./make.sh verify` pass; the EVENOTA analyzer and both
main-only inspectors accept the current package, while rejecting bootloader
transfer by policy. Three output-isolated lanes at
`build/repro-littlefs-bitops-output-{a,b,c}` reproduce both overlays, both
providers, the package, and the flash plan byte-for-byte. Aggregate and
full-suite results are not claimed pending their final gates. No physical
device or serial endpoint was accessed.

## Prior disk-version major/minor production result

The current release compiles the exact littlefs v2.10.1
`lfs_fs_disk_version_major` and `lfs_fs_disk_version_minor` bodies from
`components/apollo_main/core_overlay/runtime_littlefs_disk_version_parts.c`.
The 1,734-byte shared source has SHA-256
`920d03e80c9d16a1d0b4299f8151eefe4d9f3ac1ba89c2d40bcc5830335eb5a7`
and is pinned to `lfs.c` at commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. The upstream copyright,
BSD-3-Clause SPDX identifier, and complete
`third_party/littlefs/LICENSE.md` terms are retained.

Focused disassembly closed the configuration rather than recreating either
algorithm. `LFS_MULTIVERSION` is disabled in both authenticated 84-byte G2
configuration objects, so the exact upstream wrappers ignore `lfs_t *`.
Each raw ten-byte function section has precisely one ordered
`R_ARM_THM_CALL` relocation at offset `+0x02` to the already source-owned
disk-version provider. There is no other external symbol, data, structure
offset, stored pointer, non-linking branch, interior entry, callback,
allocation, or hardware dependency.

| Image/leaf | Runtime span | Provider target | Raw SHA-256 | Relocated SHA-256 |
|---|---|---:|---|---|
| Apollo main major | `[0x007B01B8,0x007B01C2)` | `0x007AED1C` | `ebb72edfdb508cbf5b617452eb60cbceb58bfdfc879dcece076544efa75c092f` | `cffc852c2243f51e8a52543b4f2410b192e2365c25f161cfd12f69cae8544122` |
| Apollo main minor | `[0x007B01C4,0x007B01CE)` | `0x007AED1C` | `da349b05b3a26d6a22ba3f707c4c21e1591915aeb8451e21f7509905926a4b9d` | `e0494044bcf077ed5b67a33cf3eb526bb9b8b6f31dcfefb5ce347a197b100012` |
| bootloader major | `[0x00434592,0x0043459C)` | `0x00434490` | `ebb72edfdb508cbf5b617452eb60cbceb58bfdfc879dcece076544efa75c092f` | `15251b134de5617995984b9d8140d6fb88dca904ef8ef72e480b99f3c0250b2a` |
| bootloader minor | `[0x0043459C,0x004345A6)` | `0x00434490` | `da349b05b3a26d6a22ba3f707c4c21e1591915aeb8451e21f7509905926a4b9d` | `685d7f3e70053272d9a3920aaf7867d0a84e8adb402bbccd4ef3afc76195b2b7` |

Apollo main inserts a single authenticated two-byte alignment interval at
`[0x007B01C2,0x007B01C4)`; the bootloader requires no relocated-leaf
padding. Complete stock-entry redirects preserve the three-major/four-minor
caller topology in each image.

That Apollo-main overlay/provider pair is 114,346 bytes,
`bdc1e353d1adcb0075231afb6c423616dcc0da8335b4b430afe51763a0b9df20`,
and 3,637,742 bytes,
`d69c4834f65b0661834f990da8167ca6989a1b1c97fda838edc488a4ed0b3e8e`.
That bootloader overlay/provider pair is 302 bytes,
`e94e33658aca89d3830182bc6c17c656256a194262835c041fecc93e1d72dc59`,
and 148,902 bytes,
`abc583d976a01e237ffa4ed29e4be1b6ff0e5ae2d9756bccec58d1779fe20239`.

The resulting 4,415,876-byte package has SHA-256
`60cd913a716266b349ce18295064f2484749a7dbad2ab9244c923c927bd56c2f`;
boot/main CRC-32C/MSB values are `0x12EAC8F8`/`0x7E9838B8`. The
546,404-byte flash plan has SHA-256
`52124c17205ae10e47f0b02d0cd6bae7c2b30e10d65d787aa34201a53fe0dc68`.
The manifest reports 757 placed, two unresolved, five container-only, and
six protected regions, with 114,860 source bytes, 81,523 generated bytes,
4,219,493 opaque bytes, and 196,383 controlled bytes.

`./make.sh source` and core-source manifest verification pass. No physical
device, serial endpoint, debugger, or flasher was accessed.

## Current allocator-lookahead production result

The current release compiles the exact littlefs v2.10.1
`lfs_alloc_lookahead` algorithm from
`components/apollo_main/core_overlay/runtime_littlefs_alloc_lookahead.c`.
The 5,445-byte shared source has SHA-256
`44ab9037747a4cb209404423d52cf817b035cbab5177a8c0cb05090df4b68491`
and is pinned to `lfs.c` at commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. The upstream copyright,
BSD-3-Clause SPDX identifier, and complete
`third_party/littlefs/LICENSE.md` terms are retained.

Focused disassembly supplies the ABI rather than the algorithm:
`lfs_t.lookahead.start=0x54`, `lookahead.size=0x58`,
`lookahead.buffer=0x64`, and `block_count=0x6C`. Both official spans are
`[0x004CB0F6,0x004CB12E)` in Apollo main and
`[0x00410DFE,0x00410E36)` in the bootloader. Each is 56 bytes with
SHA-256
`58285c138461a673be0bed2c5376f8d739e40e2aea753ad05d5061bfbc9265cf`.
Their callback values are stored by `lfs_alloc_scan`; there is no branch or
stored pointer into either function interior. The authenticated callback
words are `0x004CB0F7` at main address `0x004CBED8` and `0x00410DFF` at
bootloader address `0x00411BE0`; they continue to enter the complete stock
entry, whose generated `B.W` redirect transfers to the source leaf.

| Image | Source span | Alignment/padding | Raw SHA-256 |
|---|---|---|---|
| Apollo main | `[0x007B01D0,0x007B0202)` / 50 bytes | 4 / 2 bytes at `[0x007B01CE,0x007B01D0)` | `ff36aeaff70307ae466d9f7fafacad678c706db1551b18d98d7fe68bf3dc5eef` |
| bootloader | `[0x004345A6,0x004345D6)` / 48 bytes | 2 / 0 bytes | `bd8e7c926d98a940f215cd41a2fb5932bfbf1abcf7378839dcadd537ae55324d` |

Both target sections have zero text relocations and undefined symbols.
Twenty thousand deterministic host cases compare the production wrapper to
the authenticated upstream implementation, including unsigned wraparound,
in-window and out-of-window blocks, bitmap byte boundaries, and all bit
positions.

The Apollo-main overlay/provider pins are 114,398 bytes,
`2189ec69f7076e216c2ba7388f4eb9d19647feb9f89c382864012902be4e0fdf`,
and 3,637,794 bytes,
`557fe93fdf79c5cb332c7db731db29ed7cfc42be3daa49fb0d022f81e7fe0ba8`.
The bootloader overlay/provider pins are 350 bytes,
`1b8bb2893a33a18b8481b785a57d49c2849396cc05c5ef20d86f8cf5cef255a5`,
and 148,950 bytes,
`9af8b65041bbd576b49b4f88e2f7427daf7bb445981d608799d86e1987468736`.

The resulting 4,415,976-byte package has SHA-256
`3d4b2f3e22a10d0755642c0544786c9a881b2ab7c2271d8a184a83f5d3d7d13f`;
boot/main CRC-32C/MSB values are `0xB7E2DD07`/`0x4A5981CF`. The
550,026-byte flash plan has SHA-256
`73978705e32bbb968a9741620a80e1a70f866b5e43db60f4a9f08b4404ce34d1`.
The manifest reports 762 placed, two unresolved, five container-only, and
six protected regions, with 114,958 source bytes, 81,637 generated bytes,
4,219,381 opaque bytes, and 196,595 controlled bytes.

No physical device, serial endpoint, debugger, or flasher was accessed.

## Historical decision

Use the authenticated v2.10.1 source directly. The next integration pass
should start with `lfs_max`, `lfs_min`, `lfs_aligndown`, and `lfs_alignup`
in both images, with separate stock entry redirects and one shared
freestanding source implementation.

Then integrate the remaining pure utility helpers while explicitly selecting
the official fallback branch for `npw2`, `ctz`, and `popc`. Do not spend
decompilation effort recreating these algorithms.
