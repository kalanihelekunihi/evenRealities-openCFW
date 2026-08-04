# G2 bootloader core-overlay evidence

Status: source-build component registered by
`manifests/g2-2.2.6.10-core-source.json` for official G2 firmware
`2.2.6.10`; assembled and validated offline, not exercised on hardware

The initial bootloader source-overlay milestone replaced six complete leaves
with non-linking
Thumb-2 entry redirects to functions compiled from authenticated littlefs
v2.10.1 source-equivalent ports:

| Function | Stock entry span / size | Source overlay span / size |
|---|---|---|
| `lfs_scmp` | `[0x004104BA, 0x004104BE)` / 4 bytes | `[0x00434478, 0x0043447C)` / 4 bytes |
| `lfs_alloc_ckpoint` | `[0x00410DE8, 0x00410DEE)` / 6 bytes | `[0x0043447C, 0x00434482)` / 6 bytes |
| `lfs_alloc_drop` | `[0x00410DEE, 0x00410DFE)` / 16 bytes | `[0x00434482, 0x0043448E)` / 12 bytes |
| `lfs_fs_disk_version` | `[0x00410DCC, 0x00410DD2)` / 6 bytes | `[0x00434490, 0x00434498)` / 8 bytes |
| `lfs_mlist_append` | `[0x00410DC4, 0x00410DCC)` / 8 bytes | `[0x00434498, 0x004344A0)` / 8 bytes |
| `lfs_mlist_remove` | `[0x00410DA8, 0x00410DC4)` / 28 bytes | `[0x004344A0, 0x004344B2)` / 18 bytes |

The two bytes at `[0x0043448E, 0x00434490)` are compiler/linker alignment
inside the 58-byte source overlay. Existing callers continue to call the
stock entries. Each entry now tail-branches to its source function, which
returns through the caller's unchanged link register. The remaining bytes in
stock spans larger than a four-byte `B.W` are explicit Thumb NOPs; adjacent
functions and all callers remain untouched.

Binary/source identity, ABI and configuration recovery, caller topology, and
absence of interior references are recorded in:

- `docs/research/littlefs-scmp-source-boundary-audit.md`
- `docs/research/littlefs-alloc-ckpoint-source-boundary-audit.md`
- `docs/research/littlefs-alloc-drop-source-boundary-audit.md`
- `docs/research/littlefs-disk-version-source-boundary-audit.md`
- `docs/research/littlefs-mlist-append-source-boundary-audit.md`
- `docs/research/littlefs-mlist-remove-source-boundary-audit.md`
- `docs/research/littlefs-next-closed-leaves-audit.md`

## Reproducible provider contract

| Property | Value |
|---|---:|
| Official provider SHA-256 | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` |
| Raw bootloader base | `0x00410000` |
| Official raw size | `0x00024477` / 148,599 bytes |
| Official end-exclusive | `0x00434477` |
| Main application boundary | `0x00438000` |
| Alignment padding | one `0x00` byte at `0x00434477` |
| Source overlay | `[0x00434478, 0x004344B2)` / 58 bytes |
| Source overlay SHA-256 | `77a8601995931d5ca7dad2f1ff90100b6f8e6cb88cf248198142498f588a5e65` |
| Generated provider size | `0x000244B2` / 148,658 bytes |
| Generated provider SHA-256 | `b55f3619d135aef87b1cea1b8c1128b067c189b89bc74ea1811c2523a33fa560` |
| Remaining partition headroom | `0x00003B4E` / 15,182 bytes |
| Generated provider CRC-32C/MSB | `0xE7D39054` |
| Ownership regions | 12 |

The provider is a raw vector image: file offset zero maps to `0x00410000`.
The initial stack pointer is `0x2007FB00`, and the Thumb reset vector is
`0x0043291B`. The builder authenticates the whole official provider before
using its fixed end. The generated provider ends at `0x004344B2`, below the
bootloader partition boundary at `0x00438000`, and therefore does not touch
the main application.

Compilation uses the pinned Cortex-M55 Thumb `-Oz` contract. The six emitted
function sizes and offsets are build-time invariants. The overlay has no
resolved relocations or read-only-data sections. `lfs_scmp`,
`lfs_alloc_ckpoint`, and `lfs_mlist_append` reproduce their official body
sizes; the other source bodies are allowed to differ in size while preserving
the reviewed semantics and ABI:

- `lfs_alloc_drop` uses the recovered `lfs_t` lookahead offsets `0x58`,
  `0x5c`, `0x60`, and block-count offset `0x6c`, with checkpoint behavior
  source-local.
- `lfs_fs_disk_version` closes the stock literal dependency with the
  authenticated `LFS_DISK_VERSION == 0x00020001` configuration.
- `lfs_mlist_append` and `lfs_mlist_remove` use the recovered `lfs_t.mlist`
  offset and node-link prefix. The official ABI has `LFS_THREADSAFE`
  disabled, so no lock callback belongs in either leaf.

The builder decodes every emitted `B.W`, checks its destination and range,
authenticates every complete stock entry before replacement, and records each
official, generated-redirect, alignment, and source-compiled interval. The
result is 12 non-overlapping ownership regions with complete provider
coverage.

## Integrity and exact mutation set

The generated raw provider contains:

- 148,531 byte-identical opaque bytes from the authenticated official
  provider;
- 68 generated entry-replacement bytes across the six complete stock spans;
- one generated alignment byte; and
- 58 source-compiled overlay bytes.

No other official byte changes. The 68 replacement bytes comprise one
non-linking Thumb `B.W` per function and NOP fill where the complete stock
span is larger than four bytes.

The raw bootloader has no private staging header ahead of its vector. The
outer EVENOTA container owns the mutable transport fields: its 128-byte
component header stores payload length at offset `0x08` and non-reflected,
zero-init/zero-xorout CRC-32C at offset `0x0C`; the TOC stores
`128 + payload length` and repeats the same CRC. For the generated provider
the payload length is 148,658 and the CRC is `0xE7D39054`.

The core-source manifest selects this component through a `source_build`
provider pinned to the generated size and SHA-256. Package assembly
regenerates the outer length and CRC fields rather than reusing official
transport metadata.

Focused tests rebuild in a temporary directory; authenticate the source,
stock spans, vectors, function layout, and provider digest; decode all six
redirects; verify ownership accounting and partition bounds; and confirm that
the build reports no hardware operations.

## Safety boundary and build

The component builder writes only local build artifacts. It does not sign or
transmit a package, access a debugger, flash or erase storage, reset a device,
or perform any hardware operation. Hardware execution and flashing remain
unverified.

From `openCFW`:

```sh
python3 components/bootloader/core_overlay/build_component.py
```

The command writes local artifacts below
`components/bootloader/core_overlay/build/`.

## Prior authenticated AmbiqSuite leaf increment

The preceding sections preserve the six-littlefs-leaf milestone. The current
builder also compiles the complete, unmodified AmbiqSuite 5.1.0
`am_hal_mspi.c` translation unit from commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`, with source SHA-256
`5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f`.
Section garbage collection
retains only `am_hal_mspi_interrupt_clear`: 48 bytes with SHA-256
`87505e035fa5fe7c0dfd7c4d85b66c6b8f3b57ced45dc7afd787db6c52b0fd7b`,
four-byte alignment, zero relocations, and no `g_MSPIState`.

The complete authenticated stock body at
`[0x00426506,0x00426536)` has SHA-256
`4b01a25a8075cf158eb59da277f8730e36c751ee01c67bae86bc172ec877bd48`.
It is replaced by a non-linking Thumb redirect to the retained upstream leaf
at `[0x004344B4,0x004344E4)`. Two generated zero bytes align the leaf after
the existing 58-byte littlefs overlay.

| Property | Current value |
|---|---:|
| Complete overlay | `[0x00434478,0x004344E4)` / 108 bytes |
| Overlay SHA-256 | `9301c246ea058eb31ba1e04f068a6891343f095981d2b33e693764c8885dc40f` |
| Source-compiled bytes | 106 |
| Generated alignment bytes | 3 |
| Generated patch bytes | 116 |
| Remaining opaque bytes | 148,483 |
| Provider size | 148,708 bytes |
| Provider SHA-256 | `ca8edf74faffd28bc9ef34eda742863e45a947731aa1674176cef60f77fa03d2` |
| Provider CRC-32C/MSB | `0xD91E64B0` |
| Generated provider end | `0x004344E4` |
| Headroom before Apollo main | 15,132 bytes |
| Ownership regions | 16 |

The provider contract separately records the one-byte stock-to-overlay
alignment and the two-byte isolated-leaf alignment, so its 16 regions exactly
partition the complete raw provider and match the manifest. Focused tests
authenticate both source repositories, build flags, extracted leaf, discarded
sections, complete stock body, redirect, caller edges, vector table, CRC,
ownership, and partition bound. This remains an offline build artifact: no
device, serial endpoint, debugger, flasher, or hardware reset was accessed.

## Prior littlefs utility quartet

The preceding AmbiqSuite section is retained as the prior bootloader
milestone. That historical build also compiled the shared
`components/apollo_main/core_overlay/runtime_littlefs_util.c`, SHA-256
`2730d0f39e02d7b6e07396894b796b26d9f73332deff23a685b5a06da0f7fb22`,
under the bootloader's Cortex-M55 `-Oz` profile.

The source is a bounded freestanding port of the exact `lfs_max`, `lfs_min`,
`lfs_aligndown`, and `lfs_alignup` expressions from littlefs v2.10.1 commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`, tree
`06dd0162169d3cb550cd24a3e34d0e4d02983ad3`. The pristine `lfs_util.h`
has SHA-256
`f5d249326646c818e62af3cefefe8a57e7b484446a0f48d1050b95e60925088e`;
the integration source retains its copyright and SPDX identifier, and the
complete BSD-3-Clause terms remain in `third_party/littlefs/LICENSE.md`.

The complete dual-image stock identities are:

| Function | Apollo-main stock span | Bootloader stock span | Bytes | Stock SHA-256 |
|---|---|---|---:|---|
| `lfs_max` | `[0x004CA6F8,0x004CA700)` | `[0x00410400,0x00410408)` | 8 | `3caa49d8a68e47b2cd91fcb01cae26b6262c904e8b96d8b3ba35f7fb33d07464` |
| `lfs_min` | `[0x004CA700,0x004CA708)` | `[0x00410408,0x00410410)` | 8 | `7ec81166f84c44a60f4ecf93ad37d93f52ec00c77bb5db5a7dda659b1319c8a3` |
| `lfs_aligndown` | `[0x004CA708,0x004CA714)` | `[0x00410410,0x0041041C)` | 12 | `d0d7407bcf93abaef33623047467d1230d2176ce9b4a4e93bfcd8adde884f349` |
| `lfs_alignup` | `[0x004CA714,0x004CA720)` | `[0x0041041C,0x00410428)` | 12 | `18874b0eb5cf5c7bd6f20b2b29f787157294b9e9be16d14ab0d9064d44a97c37` |

The complete-image scan pins 4/4 `lfs_max`, 31/31 `lfs_min`, 5/5
`lfs_aligndown`, and 6/6 `lfs_alignup` direct callers in
Apollo-main/bootloader, with no external interior entry or stored pointer.
Only `lfs_alignup` has an outgoing edge; its sole
`R_ARM_THM_JUMP24` relocation resolves to source-owned `lfs_aligndown`.
This closes the quartet entirely in source.

The bootloader placements are:

| Overlay offset | Source span | Function |
|---:|---|---|
| 58 | `[0x004344B2,0x004344BA)` | `lfs_max` |
| 66 | `[0x004344BA,0x004344C2)` | `lfs_min` |
| 74 | `[0x004344C2,0x004344CA)` | `lfs_aligndown` |
| 82 | `[0x004344CA,0x004344D2)` | `lfs_alignup` |

Four authenticated bootloader entries and their four Apollo-main
counterparts are replaced with eight total non-linking Thumb `B.W`
redirects. NOP fill owns the remainder of every 8- or 12-byte stock span;
adjacent functions and caller link registers remain unchanged.

That milestone's bootloader overlay was 140 bytes with SHA-256
`671f04e7d78bb2502ea5ca0c8e8752c04fc2939f63793b4bb57ba5f7dd90d0e1`,
and ends at `0x00434504`. The 148,740-byte provider has SHA-256
`23e73b9134cde9822880b678f4df7a7fbc13cf3722a806b7891dca1f96af8460`.
The scalar utility quartet performs no filesystem, block-device, MSPI,
format, erase, or hardware operation. The build and inspection were local
and offline; no serial endpoint, debugger, flasher, reset, or device was
accessed. The assembled package is 4,415,504 bytes with SHA-256
`e8432777db3619478f32f5f57ca862ffeb0799857dde2274aa09b33a51dac96b`;
the boot and Apollo-main outer CRC-32C/MSB values are respectively
`0xAAC48E02` and `0xD49AD455`.

## Prior dual-image littlefs metadata-list predicate

The preceding utility-quartet section remains the prior reproducibility
milestone. That historical builder also compiled the shared
`components/apollo_main/core_overlay/runtime_littlefs_mlist_isopen.c`,
1,801 bytes with SHA-256
`7d0bc398c8ecd85fd00b34cc6dcc2b9fc75c754e1aed0bfbca01dd58ae9d6e0c`.
It is a bounded source-equivalent adaptation of littlefs v2.10.1
`lfs_mlist_isopen` at commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`, under BSD-3-Clause.

The byte-identical complete stock body is
`[0x00410D8A,0x00410DA8)`, 30 bytes with SHA-256
`e4963bfc9db9aa487d15261ebce9dd5b1429c708f6fe78ff47968718821c0c4e`.
Its six direct callers correspond to assertions-enabled littlefs file and
directory API paths. There is no stored entry pointer, non-linking incoming
edge, external interior entry, outgoing call, literal, configuration access,
block callback, allocation, or hardware operation.

The owned ABI is limited to 32-bit pointers, `struct lfs_mlist.next` at
offset zero, and an unsigned 32-bit 0/1 return. The Cortex-M55 Thumb `-Oz`
profile emits an 18-byte relocation- and undefined-symbol-free body with
SHA-256
`9b7caac591f8aea5d0eff0dc2b5ff7ff15ba85ab156ba5f95d47b1e4181db489`.
It is appended at overlay offset 140,
`[0x00434504,0x00434516)`. The builder authenticates the complete stock
entry and replaces it with a non-linking `B.W` plus NOP fill.

That milestone's overlay was 158 bytes at `[0x00434478,0x00434516)` with SHA-256
`958c5368f6cba88e2cd812e89d2eb19179e4c522203790e69b49526fba010965`.
The 148,758-byte provider has SHA-256
`0c08766d691c40d86e5bc1fefd4ab7a0abc890fbb848c8ebe249efdbcea69052`,
CRC-32C/MSB `0x6E4E0A6C`, and 15,082 bytes of remaining headroom before
Apollo main. Its 23 ownership regions account for 148,413 opaque bytes,
186 generated redirect/NOP bytes, three generated alignment bytes, and
156 source-compiled bytes without overlap or gap.

The complete 4,415,566-byte package has SHA-256
`297f2cded60e2f63ed2cf56a63842802f169ef9ff8e17045aca110edf6880483`
and flash-plan SHA-256
`1dab3311848f1d09b566527cc8592139f674c39ffa26eeddc5dacff4b715dcc3`.
Assembly places 724 regions and retains two deliberately unresolved codec
regions. Building and inspection were local and offline; no serial endpoint,
debugger, flasher, reset, external-flash operation, or device was accessed.

The release gate passed 50 combined focused tests, all 247 Apollo-main
aggregate tests in 518.563 seconds, and all 1,794 repository tests in 879.239
seconds. Three output-isolated builds reproduce the boot overlay and provider
byte-for-byte. `make.sh verify` and the independent offline analyzers accept
the package while both transfer inspectors continue to reject bootloader
flashing by policy.

## Prior dual-image littlefs endian-conversion quartet

The preceding metadata-list predicate section remains the prior milestone.
That historical bootloader build additionally compiled the shared
`components/apollo_main/core_overlay/runtime_littlefs_util_endian.c`,
2,222 bytes with SHA-256
`830d49b043181d270ac0aedda432c5e232ce8d6ce65e8e537b80b1a706fd6cac`.
It is a bounded BSD-3-Clause adaptation of littlefs v2.10.1
`lfs_fromle32`, `lfs_tole32`, `lfs_frombe32`, and `lfs_tobe32` from
`lfs_util.h` at commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`.

The complete stock cluster is `[0x004104BE,0x00410512)`. Its individual
functions are:

| Function | Complete stock span | Bytes | Stock SHA-256 |
|---|---|---:|---|
| `lfs_fromle32` | `[0x004104BE,0x004104E0)` | 34 | `0666243f83f942c21b4428e4027b6f7815771c2f8a51dcddc550ffa9710add76` |
| `lfs_tole32` | `[0x004104E0,0x004104E8)` | 8 | `b217ac730c7d1b392e0f57a67477d6db88a751a8d3afb3a50ff5bebe0e273f66` |
| `lfs_frombe32` | `[0x004104E8,0x0041050A)` | 34 | `a0fc2d34d780abf4de23efe08746eefee5cb84cae2728950c4123464e0f952c9` |
| `lfs_tobe32` | `[0x0041050A,0x00410512)` | 8 | `b217ac730c7d1b392e0f57a67477d6db88a751a8d3afb3a50ff5bebe0e273f66` |

The complete-image scan pins 26, 19, 4, and 2 direct callers respectively,
with no stored pointer, non-linking incoming edge, external interior entry,
shared tail, fallthrough, or neighboring literal. The bootloader
little-endian profile emits two-byte identity bodies for `fromle32` and
`tole32`, and four-byte byte-swap/return bodies for `frombe32` and `tobe32`.
Every body is relocation-, literal-, data-, and undefined-symbol-free.

The four isolated leaves are contiguous at overlay offsets 158, 160, 162,
and 166:

| Function | Bootloader source span | Bytes | Body SHA-256 |
|---|---|---:|---|
| `lfs_fromle32` | `[0x00434516,0x00434518)` | 2 | `c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8` |
| `lfs_tole32` | `[0x00434518,0x0043451A)` | 2 | `c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8` |
| `lfs_frombe32` | `[0x0043451A,0x0043451E)` | 4 | `7a8f0cc1ae130c65908d3dbd4e89f7c7bd898743a4ee62deced9203383df3d11` |
| `lfs_tobe32` | `[0x0043451E,0x00434522)` | 4 | `7a8f0cc1ae130c65908d3dbd4e89f7c7bd898743a4ee62deced9203383df3d11` |

Four authenticated non-linking `B.W` redirects plus NOP fill replace all 84
stock bytes. That milestone's bootloader overlay was 170 bytes at
`[0x00434478,0x00434522)` with SHA-256
`9c41f38d0d6fdde4dcbb40222adb637bbfe7625e6117eb1f475594bad8a613e8`.
The 148,770-byte provider has SHA-256
`b2922a93cf19d63a057c473e8937410efe32a8ad9202607972d34dac12e6f19e`,
ends at `0x00434522`, and leaves 15,070 bytes before Apollo main.

The complete 4,415,594-byte package has SHA-256
`cbfc505c73900cc15c0ccfa7956f6adb27d62a0d60d2d98417ac9a516ccd0c98`,
boot and main entry CRC-32C/MSB values `0xB08D0A80` and `0x70351378`, and
flash-plan SHA-256
`fd195b0f2954ff20bac946ebaf33b430f1a4fc92da873dfcd567ba3a418a4cbb`.
Assembly places 742 regions and retains two deliberately unresolved codec
regions. Focused tests authenticate the source, upstream provenance, stock
spans, topology, target code, isolated placements, redirects, artifact pins,
and partition bound. The complete release gate passes 55 focused tests in
41.693 seconds, all 248 Apollo-main aggregate tests in 521.732 seconds, and
all 1,800 repository tests in 916.875 seconds. `./make.sh verify` accepts all
authenticated inputs, analyzers, providers, and manifests. Three
output-isolated lanes at `build/repro-littlefs-endian-output-{a,b,c}`
reproduce both overlays, both providers, the package, and the flash plan
byte-for-byte. Independent offline inspection accepts the main payload while
continuing to reject bootloader transfer by policy. Building and inspection
remained local and offline; no serial endpoint, debugger, flasher, reset,
external-flash operation, or device was accessed.

## Preceding dual-image littlefs fallback-bitops tranche

All artifact pins in this section describe the preceding fallback-bitops
milestone and are superseded by the later disk-version-parts and
allocator-lookahead sections below.
The preceding endian section remains the historical milestone. The current
bootloader build additionally compiles shared
`runtime_littlefs_util_bitops.c`, 2,795 bytes with SHA-256
`405092c6e8fc65a740f951cb2affaad8766e2553c7b8d290ff58f435e8830f47`,
using the exact littlefs v2.10.1 `LFS_NO_INTRINSICS` `lfs_npw2`, `lfs_ctz`,
and `lfs_popc` expressions. The stock cluster is
`[0x00410428,0x004104BA)`, byte-identical to Apollo main. It preserves
`lfs_npw2(0) == 32`, `lfs_npw2(1) == 1`, and `lfs_ctz(0) == 0`.

| Function | Overlay offset | Runtime span | Bytes | Post-link SHA-256 |
|---|---:|---|---:|---|
| `lfs_npw2` | 90 | `[0x004344D2,0x0043450A)` | 56 | `1048afe6eb2c306231e410f0a864ab5bfab3c9b0567e1fba6ec61f8bae53094a` |
| `lfs_ctz` | 146 | `[0x0043450A,0x0043451A)` | 16 | `a5616df42c6d3705e9906d0cdce4d6d5b59d0f02b647c59efeb6594c64004ab1` |
| `lfs_popc` | 162 | `[0x0043451A,0x00434544)` | 42 | `e537e00ef37eced668a9d421f28e84d54a2b6ea09ea1cfda00f96ec1d65891f7` |

The sole new relocation is the internal `lfs_ctz -> lfs_npw2` Thumb call.
There is no external, undefined, literal, data, filesystem-state, callback,
allocation, or hardware dependency. The existing AmbiqSuite,
`lfs_mlist_isopen`, and endian leaves now occupy `[0x00434544,0x00434574)`,
`[0x00434574,0x00434586)`, and `[0x00434586,0x00434592)`.

The final bootloader link contains 204 bytes of primary text, no read-only
data, 78 bytes of isolated source, no isolated padding, and two resolved
relocations.

The current bootloader overlay is 282 bytes at
`[0x00434478,0x00434592)` with SHA-256
`b934dbea7624660c3c774eb0f4edd5e73a738fc59023fc69cfac96417dfe2fee`.
The 148,882-byte provider has SHA-256
`1aa7920a16ed2857a2743394c0f62395a2f2477f95c965da47d1e29c4d2d8247`,
ends at `0x00434592`, and leaves 14,958 bytes before Apollo main.

The complete 4,415,834-byte package has SHA-256
`058782604ab6cb946aff0acedbbef7d367bb1d82114f28c9a70276bcdf178e9a`;
boot/main entry CRC-32C/MSB values are `0x1162559F`/`0xB436A24C`, and the
flash-plan SHA-256 is
`2015673f529e550e67c2f219d789746cceef1b022bdcf2db16f1ba451a8aa05e`.
The new focused production test passes 6/6 cases in 13.693 seconds, and the
inherited focused gate passes 55/55 tests in 39.997 seconds: 61 tests across
the two isolated suites in 53.690 seconds summed. The relocation-repin audit
reviewed 22 shifted compiled-body pins; every function boundary and all 185
relocation records remained unchanged, and all 100 differing bytes were
relocation write sites. All five rodata sections in Apollo main were
byte-identical and shifted by 128 bytes. The canonical repository run passed
all 1,806 tests in 1,139.177 seconds; inside that run, all 248 Apollo-main
aggregate methods passed. `./make.sh source` and `./make.sh verify` pass, and
three isolated `build/repro-littlefs-bitops-output-{a,b,c}` lanes reproduce
both overlays, both providers, the package, and the flash plan byte-for-byte.
Offline
inspection accepts the main payload and rejects bootloader transfer by
policy.

## Prior littlefs disk-version major/minor source tranche

That bootloader build compiled the same 1,734-byte
`components/apollo_main/core_overlay/runtime_littlefs_disk_version_parts.c`
source used by Apollo main. Its SHA-256 is
`920d03e80c9d16a1d0b4299f8151eefe4d9f3ac1ba89c2d40bcc5830335eb5a7`.
The file reuses the exact `lfs_fs_disk_version_major` and
`lfs_fs_disk_version_minor` bodies from littlefs v2.10.1 `lfs.c`, commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`, under the retained
BSD-3-Clause terms in `third_party/littlefs/LICENSE.md`.

Focused disassembly proves that the authenticated 84-byte bootloader
`lfs_config` disables `LFS_MULTIVERSION`. The pair therefore has no
`lfs_t`-layout dependency. Each leaf makes exactly one call to the already
source-owned `lfs_fs_disk_version` provider, and has no other external,
literal, data, filesystem-state, callback, allocation, or hardware
dependency. The complete caller sets remain within retained `lfs_mount_`
disk-version validation and diagnostic paths:

- major callers: `0x00414712`, `0x00414744`, and `0x00414808`;
- minor callers: `0x0041471E`, `0x0041472E`, `0x0041473C`, and
  `0x00414800`.

There is no non-linking branch, stored pointer, or interior entry into
either stock or relocated function.

### Relocated-leaf link contracts

Each function section is extracted and authenticated independently. The
builder accepts exactly one ordered `R_ARM_THM_CALL` relocation per leaf:

| Leaf | Overlay offset | Runtime span | Alignment/padding | Raw SHA-256 | Relocated SHA-256 | Ordered relocation |
|---|---:|---|---|---|---|---|
| `lfs_fs_disk_version_major` | 282 | `[0x00434592,0x0043459C)` | 2/0 | `ebb72edfdb508cbf5b617452eb60cbceb58bfdfc879dcece076544efa75c092f` | `15251b134de5617995984b9d8140d6fb88dca904ef8ef72e480b99f3c0250b2a` | function `+0x02`, runtime `0x00434594`, target `0x00434490` |
| `lfs_fs_disk_version_minor` | 292 | `[0x0043459C,0x004345A6)` | 2/0 | `da349b05b3a26d6a22ba3f707c4c21e1591915aeb8451e21f7509905926a4b9d` | `685d7f3e70053272d9a3920aaf7867d0a84e8adb402bbccd4ef3afc76195b2b7` | function `+0x02`, runtime `0x0043459E`, target `0x00434490` |

The stock entry hashes are shared with Apollo main. The authenticated
bootloader replacements are:

| Leaf | Stock span | Stock SHA-256 | Replacement bytes | Replacement SHA-256 |
|---|---|---|---|---|
| major | `[0x00410DD2,0x00410DDE)` | `c9ab0025e9e77a75e9240efbd5b15da22807bdaa9f9deaf2cb425d4850f3bf08` | `23f0debb00bf00bf00bf00bf` | `f615105ee8f35be3357a04f96780f7ec2bb7786fe1c157811fc41fbd24247d3d` |
| minor | `[0x00410DDE,0x00410DE8)` | `c03343d554dbdd887485eff548d1f2852a1e2f1fe86e662759d478f1d28c7253` | `23f0ddbb00bf00bf00bf` | `5f0b90be06a317752818cc4b5ac292725b561e10ff8043f34dc1bc0772702f24` |

Both replacements are complete non-linking Thumb `B.W` redirects with NOP
fill.

### Disk-version artifacts and package accounting

The final bootloader link contains 204 bytes of primary text, no read-only
data, 78 bytes of isolated source, 20 bytes of relocated-leaf text, and no
isolated or relocated padding. It resolves two primary relocations across 21
functions and installs 21 authenticated patch sites covering 438 generated
bytes.

The 302-byte overlay occupies `[0x00434478,0x004345A6)`, has SHA-256
`e94e33658aca89d3830182bc6c17c656256a194262835c041fecc93e1d72dc59`,
and leaves 14,938 bytes before Apollo main. The 148,902-byte bootloader
provider has SHA-256
`abc583d976a01e237ffa4ed29e4be1b6ff0e5ae2d9756bccec58d1779fe20239`;
component accounting is 302 source-owned bytes, 148,161 opaque bytes, one
generated alignment byte, and 438 generated patch bytes.

Together with that 3,637,742-byte Apollo-main provider, the
4,415,876-byte package has SHA-256
`60cd913a716266b349ce18295064f2484749a7dbad2ab9244c923c927bd56c2f`.
Boot and main entry CRC-32C/MSB values are `0x12EAC8F8` and `0x7E9838B8`.
The 546,404-byte flash plan has SHA-256
`52124c17205ae10e47f0b02d0cd6bae7c2b30e10d65d787aa34201a53fe0dc68`.
That manifest contains 757 placed, two deliberately unresolved, five
container-only, and six protected regions. It classifies 114,860 source
bytes, 81,523 generated bytes, and 4,219,493 opaque bytes; 196,383 bytes are
controlled.

`./make.sh source` and core-source manifest verification pass. All building
and inspection remained local and offline; no device, serial endpoint,
debugger, flasher, reset, or external-flash operation was accessed.

## Prior littlefs allocator-lookahead source tranche

That bootloader build additionally compiled the exact littlefs v2.10.1
`lfs_alloc_lookahead` algorithm from the shared 5,445-byte
`components/apollo_main/core_overlay/runtime_littlefs_alloc_lookahead.c`,
SHA-256
`44ab9037747a4cb209404423d52cf817b035cbab5177a8c0cb05090df4b68491`.
The source retains the upstream copyright and BSD-3-Clause SPDX identifier;
the complete terms remain in `third_party/littlefs/LICENSE.md`.

Focused disassembly supplies only the compatible 32-bit `lfs_t` offsets
`0x54`, `0x58`, `0x64`, and `0x6C`. The complete stock callback is
`[0x00410DFE,0x00410E36)`, 56 bytes with SHA-256
`58285c138461a673be0bed2c5376f8d739e40e2aea753ad05d5061bfbc9265cf`.
Its callback word at `0x00411BE0` remains `0x00410DFF` for
`lfs_alloc_scan` and reaches the generated complete-entry redirect;
whole-image scans find no branch or stored pointer into its interior.

The `-Oz` profile emits a 48-byte, two-byte-aligned, relocation-free
function at `[0x004345A6,0x004345D6)` with SHA-256
`bd8e7c926d98a940f215cd41a2fb5932bfbf1abcf7378839dcadd537ae55324d`.
Twenty thousand deterministic host cases compare the same source wrapper to
the authenticated upstream implementation across modular block arithmetic,
lookahead-window bounds, and bitmap positions.

The final bootloader link contains 204 bytes of primary text, 78 bytes of
isolated source, and 68 bytes of separately compiled littlefs text. It
installs 22 authenticated patch sites covering 494 generated bytes.
The 350-byte overlay occupies `[0x00434478,0x004345D6)`, has SHA-256
`1b8bb2893a33a18b8481b785a57d49c2849396cc05c5ef20d86f8cf5cef255a5`,
and leaves 14,890 bytes before Apollo main. The 148,950-byte provider has
SHA-256
`9af8b65041bbd576b49b4f88e2f7427daf7bb445981d608799d86e1987468736`;
component accounting is 350 source-owned bytes, 148,105 opaque bytes, one
generated alignment byte, and 494 generated patch bytes.

Together with the 3,637,794-byte Apollo-main provider, the 4,415,976-byte
package has SHA-256
`3d4b2f3e22a10d0755642c0544786c9a881b2ab7c2271d8a184a83f5d3d7d13f`.
Boot and main entry CRC-32C/MSB values are `0xB7E2DD07` and `0x4A5981CF`.
The 550,026-byte flash plan has SHA-256
`73978705e32bbb968a9741620a80e1a70f866b5e43db60f4a9f08b4404ce34d1`.
The manifest contains 762 placed, two deliberately unresolved, five
container-only, and six protected regions. It classifies 114,958 source
bytes, 81,637 generated bytes, and 4,219,381 opaque bytes; 196,595 bytes are
controlled.

All building and inspection remained local and offline; no device, serial
endpoint, debugger, flasher, reset, or external-flash operation was accessed.

The subsequent main-only CMSIS `osMessageQueueNew` tranche leaves this
bootloader overlay/provider unchanged at 350/148,950 bytes and advances the
complete package to 4,416,102 bytes, SHA-256
`c7baf50cd5386a5e27b4c284cc0084e8cf5d0b83d74eb08b8d4a997bf66474f4`.
Its 552,937-byte flash plan has SHA-256
`79da631918503c668516e1af5d3844e3dab65c9e63d8add4834a43536ef69407`;
boot/main CRC-32C/MSB values are `0xB7E2DD07`/`0xF2170DD9`.

## Preceding dual-image EasyLogger helper increment

The current bootloader build source-owns the source-equivalent EasyLogger
`get_fmt_enabled`, unsigned-argument format predicate, pointer-argument
format predicate, and `elog_strcpy` algorithms. Their authenticated stock
spans are:

| Function | Stock span | Bytes | Stock SHA-256 |
|---|---|---:|---|
| `get_fmt_enabled` | `[0x00417AD4,0x00417B3E)` | 106 | `eb04732c56e958be0b715c98f23dafc9aa9c29a6321a1b58297529e39eb3eb5a` |
| unsigned-argument predicate | `[0x00417B48,0x00417B62)` | 26 | `95bba933ae9e65022ef0ff0daa76324678aa539c2ba79435b80181ce34a23db7` |
| pointer-argument predicate | `[0x00417B62,0x00417B7C)` | 26 | `3af2631ad7a44be557a9454da2df68862b6458bf2359f58d41c3d6d2ff86c8a2` |
| `elog_strcpy` | `[0x0041B158,0x0041B1FA)` | 162 | `9708f61ea38bbac62f5542fdd2701a950ba1bde9fd480c5baf7cb0be6a8461b5` |

The ordered direct caller counts are 10, 3, 6, and 23. Complete-image scans
find no non-linking entry branch, stored function pointer, or external
interior entry. Generated non-linking `B.W` branches and NOP fill replace all
320 stock bytes without moving any caller.

The shared 4,975-byte source and 6,505-byte header have SHA-256 values
`8f2850f789fba3b08bdc3e1fa8f3a4646aaef7e4b16862f3be53478071aa22b5`
and
`f3a7e9bce0f136a2ff4a76929c317aef7bbc7c29dfc60d58311d94e58f6e2393`.
The 7,068-byte image-seam source hashes to
`78dc5aa9a7eb4f072b3169ae1837855007f25e1adccec7deaefecc486c8f0823`.
All retain MIT terms.

The seam source binds the algorithms to the boot logger object at
`0x20026700` and assertion-hook word at `0x200270E4`. The official assertion
strings, stock `elog_output` at `0x004176CE`, and wait wrapper at
`0x0041AC8A` remain explicit binary seams. The helper algorithms, boot image
selection, 32-bit `size_t`, six-level/1,024-byte configuration, and corrected
tag record layout (`level +0`, `tag +1`, `tag_use_flag +0x20`) are
source-owned.

Two generated alignment bytes at `[0x004345D6,0x004345D8)` precede 270
source bytes:

| Source function | Runtime span | Bytes |
|---|---|---:|
| logger-object provider | `[0x004345D8,0x004345E0)` | 8 |
| assertion-policy provider | `[0x004345E0,0x00434664)` | 132 |
| `get_fmt_enabled` | `[0x00434664,0x0043468A)` | 38 |
| unsigned-argument predicate | `[0x0043468A,0x0043469E)` | 20 |
| pointer-argument predicate | `[0x0043469E,0x004346B2)` | 20 |
| `elog_strcpy` | `[0x004346B2,0x004346E6)` | 52 |

The six leaves have six reviewed `R_ARM_THM_CALL` relocations and no
writable section, read-only-data relocation, or undefined dependency. The
622-byte overlay hashes to
`fc02cf66854adace4d213e08764e435e27c8c2bc7cc4f7caac6ff286f3adf813`.
The 149,222-byte provider hashes to
`b4a5b0f2028842a2d6fde9424fff05fac2db3bf0e26e7f01d16a990e67ed9052`,
ends at `0x004346E6`, and leaves 14,618 bytes before Apollo main.
Accounting is 620 source-owned bytes, 814 generated patch-site bytes, three
generated alignment bytes, and 147,785 opaque bytes.

The complete 4,417,760-byte package hashes to
`fb662322f26e06aa04eb1d3f55f8c8f18606e510fac9c35885de3e4f92864c4d`;
boot/main entry CRC-32C/MSB values are `0x4ABC7690` and `0x3A071E66`. Its
592,687-byte flash plan hashes to
`c06c84e277bad2160479e0ec1f7a626abb804574f42ecee0709f0978657cd1b3`
and records 822 placed, two unresolved, five container-only, and six
protected regions. All validation was offline; no hardware was accessed.

## Preceding dual-image littlefs tag-chunk increment

The bootloader now participates in the atomic production replacement of
littlefs `lfs_tag_chunk`. Its authenticated stock body is
`[0x00410BA8,0x00410BAE)`, six bytes `000dc0b27047`, SHA-256
`63fc572597119c756fa5d4ee0904c8c34dfa545495b77bba02e2ff3298ce23ae`.
Exactly four direct callers target its first halfword and reviewed
complete-image scans find no alternate or interior ingress.

The common source text is six bytes, relocation-free, and hashes to
`db1dfda72afb267e96cd4e11eaf5d44659195b0afecbdcd8ed8572c34049df74`.
It is placed at overlay offset 622 / `[0x004346E6,0x004346EC)` under Apple and
Linux. The complete stock body becomes a non-linking `B.W` plus one NOP.

Apple's 628-byte overlay hashes to
`10dce6ad20335a583b4ab2fad4b916ed335d65f126af06b77a935be9702149f6`;
the 149,228-byte component hashes to
`ecfe0087fef4eab3a75f41a2db28d31b3e31c589fdaceec3c209e6e503eb295f`.
Linux uses the same sizes with hashes
`e7619c604912ded4b5ac4513287bb68560bba2a09f84cda42dd9f1cf2d080a63`
and `64d87f89085988da184b7cf3b9758e702093e35f0e4b2afb6da22971b8532f1b`.
Accounting is 626 source, 820 generated patch, three generated alignment,
and 147,779 opaque bytes. The config has 29 functions, 27 patches, and ten
relocated leaves.

The source is a bounded BSD-3-Clause adaptation of authenticated littlefs
v2.10.1, which establishes compatible source behavior but not the precise
vendor checkout. It has no filesystem-object or block-device dependency.
Qualification was offline; no signing, flashing, format, erase, reset, boot,
or hardware operation occurred.

## Preceding atomic littlefs tag-validity/type1 increment

The bootloader now additionally replaces `lfs_tag_isvalid` at
`[0x00410B72,0x00410B7C)` and `lfs_tag_type1` at
`[0x00410B90,0x00410B98)`. The byte-identical Apollo-main homologs are at
`[0x004CAE6A,0x004CAE74)` and `[0x004CAE88,0x004CAE90)`. Complete-image scans
authenticate three/eight direct callers per image and no reviewed alternate
or interior ingress. Full-span boot patches are
`23f0bbbd00bf00bf00bf` and `23f0afbd00bf00bf`.

The provider- and relocation-free source leaves are placed at offsets 628 /
`0x004346EC` and 634 / `0x004346F2`. Apple produces a 644-byte overlay,
SHA-256
`959923a9b5253bd6409fedb82427b7ff666e2d52bc09ac5c391bc28bfbcc70c2`,
and 149,244-byte component, SHA-256
`e8924fe19f6f768d01fa7c6ec111a4db5790eb28c423c5be84e09b0996423e20`.
Linux uses the same sizes with SHA-256
`078b88569f6adb147d3c12c727f29c5f3a6ddeb2f66de7d68122b4096f6ac794`
and `6fff06068442ab3203d124c0adfd5052f216459642f67aa32cc39afffd2c0593`.
Accounting is 642 source, 838 patch, three alignment, and 147,761 opaque
bytes; the config census is 31 functions, 29 patches, and 12 relocated leaves.

The sources retain littlefs BSD-3-Clause terms and use authenticated v2.10.1
as a source-equivalent baseline, not proof of the vendor's exact checkout.
Offline assembly is GO; signing, flashing, filesystem mutation, reset, boot,
and hardware operation remain NO-GO.

## Preceding atomic littlefs tag-ID increment

The bootloader now source-replaces the complete private `lfs_tag_id` body at
`[0x00410BB8,0x00410BC0)`. Its bytes `800a8005800d7047` and SHA-256
`0843abb3e9ef39afac8e69ae1e181efa0b5b5c8ebf53e20844b53fdf245b1036`
match Apollo main at `[0x004CAEB0,0x004CAEB8)`. Complete-image scans close 41
boot and 50 main direct callers, with no reviewed alternate start, interior
ingress, stored pointer, or outgoing branch.

The source is the bounded BSD-3-Clause adaptation of authenticated littlefs
v2.10.1 `lfs.c[10702:10793]`, SHA-256
`50140c563689852013dfad180ec3b6464c6b6c5b22854f5492d63cf5de57fbe2`,
at commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`. The six-byte production
text `c0f389207047` hashes to
`6194594e24288e708887a0e938b2a54401c8c732210d91af7a5927d03bd3604c`
and has zero providers and zero relocations.

| Profile | Boot placement | Complete boot patch | Boot overlay/component |
|---|---|---|---|
| Apple Clang 21.0.0 | offset `650` / `0x00434702` | `23f0a3bd00bf00bf` | `656` / `432f0c91a6db142a951db076fc89a4a80e740675d63f62263f45c21e37777ad3`; `149,256` / `6d96308ea4e5851ab137831d6da991184b6611551a01fa18e4cef3f1877f4694` |
| exact-root Linux Clang 22.1.8 | offset `650` / `0x00434702` | `23f0a3bd00bf00bf` | `656` / `4cadbf422b57b1905b38df77ab0d24932839aa28f883f57e56a09183d577edb8`; `149,256` / `a3ca91bb744c777d7d98d8b34a044e613ad251a972d6e6d54a8a48b959795ad2` |

The boot config census is `33/31/14`. Both final build reports classify 654
source-owned, 854 generated-patch, three generated-alignment, and 147,745
opaque bytes.
The source-equivalent identity is not a vendor-checkout claim, and this pure
scalar integration authorizes no signing, flashing, filesystem mutation,
reset, boot, or hardware operation.

## Preceding atomic littlefs tag-type3 increment

The bootloader now also replaces the complete `lfs_tag_type3` body at
`[0x00410BA0,0x00410BA8)`. Its bytes `000d4005400d7047` and SHA-256
`818012c47ba81ee18e2996d51a8a29a96a78ced50854b6fefcebf92e7b9ed9d6`
match Apollo main at `[0x004CAE98,0x004CAEA0)`. Complete-image scans close 17
boot and 30 main direct callers with no reviewed alternate or interior ingress.

The provider- and relocation-free source leaf is six bytes
`c0f30a507047`, SHA-256
`a6781f0a92086cca25476ca00824d8f0fd736ac7d800aa9e3f6e4d6544490921`.
Both profiles place it at offset 644 / `[0x004346FC,0x00434702)` and use the
complete patch `23f0acbd00bf00bf`. Apple produces a 650-byte overlay,
SHA-256
`efc0bc7a5fa7351a9aa372bec40d1a88fde0284b251486db11a9877947da6d50`,
and 149,250-byte component, SHA-256
`826358deb7400e8c25b744487979c0c7f32b7e1db63588b5a244c3375e885a62`.
Linux uses the same sizes with SHA-256
`968dbeac7adef3acc5151cd15189bba3528de295147ecca60832f1cf87b425e3`
and `bb3d7eef87a59529f67de9996324a91575d6e1218471a5330b153eb28950742a`.

Boot accounting is now 648 source, 846 patch, three alignment, and 147,753
opaque bytes. The authenticated littlefs v2.10.1 commit is a
source-equivalent baseline rather than proof of the vendor's exact checkout.
Offline assembly is GO; signing, flashing, filesystem mutation, reset, boot,
and hardware operation remain NO-GO.

## Preceding littlefs tag-size production increment

The production bootloader replacement owns the complete private `lfs_tag_size`
body at `[0x00410BC0,0x00410BC6)`, file offset `0x00000BC0`. Its bytes
`8005800d7047`, SHA-256
`8596106584e598a657aea7fdd2e1156a748158d2d63d9c121c92587fabbdf8ca`,
match Apollo main at `[0x004CAEB8,0x004CAEBE)`. Complete-image scans close
14 boot and 15 main direct callers with no reviewed alternate start, interior
ingress, stored pointer, outgoing branch, shared tail, or literal pool.

The selected source is the bounded BSD-3-Clause adaptation of authenticated
littlefs v2.10.1 `lfs.c[10793:10880]`, SHA-256
`9df85bc43ca9f90ef58c425c5fd9bbbbf53585093be5fad0cc580fc88814ea5c`,
at commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`. Apple production
compilation emits provider- and relocation-free six-byte text `6ff39f207047`,
SHA-256
`35890ebcdee5cb7f51b3e8d874201b7e0214f6111eebe56c772133f259cf9b54`.

| Profile | Boot placement | Complete boot patch | Boot overlay/component |
|---|---|---|---|
| Apple Clang 21.0.0 | `656` / `0x00434708` | `23f0a2bd00bf` | `662` / `7cb3c17a03dda3b8576d8288ffa61df1332d89f1f24d6c5877bf0143e233902b`; `149262` / `695688b7cc4d9583e9e5c854db44980acab9a58d367bc7e02fa5e51eb00e3267` |
| exact-root Linux Clang 22.1.8 | `656` / `0x00434708` | `23f0a2bd00bf` | `662` / `e4c743531f56c190b7e3129768d410480a2f3433a5b680c7bf432ef0b05a7021`; `149262` / `fc3d07c8a59e1c33f26965cdb1888114412c3ca671d6137f7c3166acc81c8d74` |

The final boot function/patch/relocated-leaf config census is
`34/32/15`;
Apple boot component accounting remains
`660 source-owned /
860 generated patch /
3 generated alignment /
147739 opaque`; Linux boot is
`660 /
860 /
3 /
147739` in the same order. The
settled tag-ID increment is the preceding milestone. This promotion
authorizes no signing, flashing, filesystem mutation, reset, boot, or
hardware operation.

## Preceding nanopb fixed64 bootloader exclusion witness

The Apollo-main `pb_decode_fixed64` promotion has no authenticated bootloader
homolog. The official 148,599-byte boot image hashes to
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`
and maps to `[0x00410000,0x00434477)`. Exhaustive checks find no complete
fixed64 body, read-prologue/success-store signature, matching `pb_read`
provider, `decode_basic_field` signature, or nanopb runtime error strings.
The two call-adjacent sites among 21 aligned `movs r2,#8` instructions are
unrelated configuration/function-table paths without fixed64 topology.

Consequently boot configuration and ownership remain `34/32/15`, 67 manifest
regions, and `660 / 860 / 3 / 147739` source/patch/alignment/opaque bytes. The
Apple boot overlay/component remain 662 /
`7cb3c17a03dda3b8576d8288ffa61df1332d89f1f24d6c5877bf0143e233902b`
and 149,262 /
`695688b7cc4d9583e9e5c854db44980acab9a58d367bc7e02fa5e51eb00e3267`;
Linux remains 662 /
`e4c743531f56c190b7e3129768d410480a2f3433a5b680c7bf432ef0b05a7021`
and 149,262 /
`fc3d07c8a59e1c33f26965cdb1888114412c3ca671d6137f7c3166acc81c8d74`.

## Current nanopb `pb_read` bootloader exclusion witness

The Apollo-main `pb_read` promotion has no authenticated bootloader homolog.
The official 148,599-byte boot image contains neither the complete 150-byte
`pb_read` body nor the private 26-byte `buf_read` body, and it contains neither
NUL-terminated nanopb runtime error string used by the main implementation.
The production source replacement is therefore intentionally Apollo-main
only; no boot byte or ownership class changes in this tranche.

Boot configuration remains `34/32/15`, the manifest remains 67 regions, and
component accounting remains `660 / 860 / 3 / 147739` source/patch/alignment/
opaque bytes. Apple boot stays 662 bytes /
`7cb3c17a03dda3b8576d8288ffa61df1332d89f1f24d6c5877bf0143e233902b`
and 149,262 bytes /
`695688b7cc4d9583e9e5c854db44980acab9a58d367bc7e02fa5e51eb00e3267`;
Linux remains 662 /
`e4c743531f56c190b7e3129768d410480a2f3433a5b680c7bf432ef0b05a7021`
and 149,262 /
`fc3d07c8a59e1c33f26965cdb1888114412c3ca671d6137f7c3166acc81c8d74`.
This is an offline exclusion result and authorizes no signing, flashing,
reset, boot, or hardware operation.
