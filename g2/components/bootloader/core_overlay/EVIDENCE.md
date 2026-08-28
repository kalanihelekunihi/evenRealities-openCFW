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

## Current S200 redirect-initializer increment

The current provider additionally source-owns the complete 88-byte
`product/s200/bootloader/config/redirect.c` `redirect_init` entry at
`[0x00415590,0x004155E8)`. The authenticated stock SHA-256 is
`b53b1d0eae9d2787d431ae1950d956c54429fb339a67ee7f219ff7c01ffc0cd6`.
The recovered entry creates and publishes the stdout/stderr-side IAR stream
mutex handles at `0x2002712C` and `0x20027130`, checks both results after both
attempts, preserves the exact success/failure return values, and emits the
authenticated EasyLogger diagnostics through retained `elog_output`.

The clean-room source and ABI header are 2,295 and 1,982 bytes with SHA-256
values `9df4daeea0af317c1556361a15f1625d5b1e9d00b3c72ae9b753de4608c3294f`
and `d59de5e4176f72b95aa93c3e497de815bc29ac1ea816d2e3b8512d4349125414`.
Canonical Apple clang emits a 132-byte function at `0x00434710` and a
143-byte authenticated diagnostic string section. The 275-byte closure has
SHA-256
`ddb1d064bf765803fac4fc89c0b6c585f13b0ea7bcfc3b5ad7b78ee7d8e50922`.
Twelve strict relocations bind four calls only to retained `osMutexNew` and
`elog_output`, and bind the remaining eight references only to strings inside
the same source closure. The stock entry receives one non-linking Thumb
redirect plus 42 NOPs.

Current canonical accounting is 5,025 source-owned bytes, 6,112 generated
patch bytes, 12 generated alignment bytes, and 142,487 retained official
bytes. The 5,036-byte overlay hashes to
`ca2f967d2d107381559bdac96d16c4c44f1eb63a4b767ae54026cfac003aa218`;
the 153,636-byte provider hashes to
`57252d4ad8cecfa2d960789e1d0b1eeab8680616a51bc3d16a700a10b61fdd76`,
has CRC-32C/MSB `0x3CBFB040`, and leaves `0x27DC` bytes before Apollo main.
The independent Homebrew clang 22.1.8 profile has separately pinned hashes
for the same layout and relocation graph.

Host failure/success tests, isolated target builds, the fail-closed analyzer,
provider/manifest ownership checks, and both compiler profiles pass offline.
The neighboring IAR `FILE` wrappers remain outside this source boundary.
Hardware execution is unverified and explicitly blocked by unavailable
authorized responsive hardware. See
`docs/research/g2-bootloader-redirect-init-source-closure.md`.

The corresponding unsigned Apple package is 4,735,214 bytes with SHA-256
`3ccadb3747bb097b66052e79255808a5c91d78870d8ed661210095de6934e2b6`;
its flash plan hashes to
`20397421f1a52eb9649ea0f824332de42bcc8f785f1044c14acff8c31c965f4d`.
The refreshed Homebrew clang 22.1.8 whole-source profile produces a
4,511,208-byte package with SHA-256
`5694aaecec246a5494baefed9c9ac67183fc7e18ef01d43c486933dce7bf88c3`.
Both remain local unsigned build artifacts.

## Current Arm EABI byte-fill increment

The complete authenticated 102-byte entry at `[0x0041560C,0x00415672)`
now redirects to `runtime_aeabi_memset.c`. A whole-image halfword scan pins 20
direct Thumb callers and no strict-interior ingress. Both reviewed compilers
emit the same relocation-free 12-byte leaf at `0x00434824`, SHA-256
`57aa3a55299e81fefe7ae3b0807a149cf0d3d6c56adfcd6bf507f3850e6c229e`.
The stock entry is replaced by a non-linking branch plus 49 NOPs. Host tests,
target compilation, provider accounting, manifest ownership, and dual-package
pins are fail-closed. Live boot validation remains blocked by unavailable
authorized responsive hardware. See
`docs/research/g2-bootloader-aeabi-memset-source-closure.md`.

## Current Arm EABI forward-copy increment

The complete authenticated 166-byte entry at `[0x0041568C,0x00415732)`
now redirects to `runtime_aeabi_memcpy.c`. A whole-image scan pins 33 direct
Thumb callers and no strict-interior or stored-pointer ingress. Both reviewed
compilers emit the same relocation-free 16-byte leaf at `0x00434830`, SHA-256
`d2d832a0c13fc4c0b9b47396bfb6d68fb7e07925ad0fa4eedc9c14c5b062590d`.
The stock entry is replaced by a non-linking branch plus 81 NOPs. Host tests,
target compilation, provider accounting, manifest ownership, and dual-package
pins are fail-closed. Live boot validation remains blocked by unavailable
authorized responsive hardware. See
`docs/research/g2-bootloader-aeabi-memcpy-source-closure.md`.

## Current bounded byte-comparison increment

The authenticated 104-byte entry at `[0x00415758,0x004157C0)` now redirects
to `runtime_memcmp.c`. Six direct callers and no strict-interior/stored-pointer
ingress are pinned. Both compilers emit the same relocation-free 28-byte leaf
at `0x00434840`, SHA-256
`27a66a6c870f14f8ff02ed06584fc60e5e6bb17274f13e4234314e5fcbb2ece1`.
Host equality, difference-sign, prefix, and unaligned tests pass. Live boot
validation remains blocked by unavailable authorized responsive hardware. See
`docs/research/g2-bootloader-memcmp-source-closure.md`.

## Current string-span increment

The adjacent authenticated 34-byte entries at
`[0x004157F8,0x0041581A)` and `[0x0041581A,0x0041583C)` now redirect to
the clean-room `runtime_strcspn.c` and `runtime_strspn.c` implementations.
Each entry has three pinned direct callers and no strict-interior or stored-
pointer ingress. Both reviewed compilers emit the same relocation-free leaves:
30 bytes at `0x0043485C`, SHA-256
`d331d9fb8cccb8f60badaf3dfab936298bdf11cf61320cca6ce19008d42e3096`,
and 28 bytes at `0x0043487A`, SHA-256
`f955f2e0febe0b7b844837f389b4eb1e601e349bf6f9183426b2e16de8961d22`.
Empty-set, first-match, no-match, prefix, and stop semantics pass on the host.
Live boot validation remains blocked by unavailable authorized responsive
hardware. See `docs/research/g2-bootloader-string-spans-source-closure.md`.

## Current reflected CRC-32 increment

The authenticated 56-byte entry at `[0x004157C0,0x004157F8)` now redirects
to the clean-room bitwise `runtime_crc32.c` implementation. Six direct callers
and the standard reflected `0xEDB88320` nibble-table polynomial are pinned.
Apple clang emits a relocation-free 44-byte leaf at `0x00434898` after two
alignment bytes. Host tests cover empty, standard, all-byte, embedded-NUL, and
incremental updates. Live CRC/boot validation remains blocked by unavailable
authorized responsive hardware. See
`docs/research/g2-bootloader-crc32-source-closure.md`.

## Current SRAM-word setter increment

The authenticated eight-byte entry at `[0x0041583C,0x00415844)` now redirects
to `runtime_store_200270cc.c`. Its sole caller and the literal target
`0x200270CC` are pinned without assigning an unsupported semantic label to the
cell. Both reviewed compilers emit the same relocation-free 12-byte leaf at
`0x004348C4`. Host tests cover complete-word stores. Live SRAM/boot validation
remains blocked by unavailable authorized responsive hardware. See
`docs/research/g2-bootloader-store-200270cc-source-closure.md`.

## Preceding numeric/runtime/event-flags/bit-helper increment

The 41 authenticated runtime entries from `0x00415844` through
`0x004169FC` now route to C for unsigned 64-bit division by ten,
digit counts, wrapping decimal parsing, unsigned decimal/hexadecimal output,
nullable string length, repeated-character output, fixed-point float
conversion, the complete IAR logging formatter core, and its variadic dispatch
wrapper, substring search, critical-context detection, runtime-state gate
acquisition, four-state mapping and release, critical-context value dispatch,
the address-identified runtime dispatcher at `0x004160FE`, and the retained-
value wrapper at `0x004161C6`, and the validated runtime-call wrapper at
`0x004161CE`, the guarded runtime-action wrapper at `0x00416200`, and the
two-phase runtime-transfer wrapper at `0x0041623A`, the masked runtime-wait
wrapper at `0x004162C4`, the optional runtime-notification wrapper at
`0x00416378`, the registered runtime-callback adapter at `0x0041639A`, and the
registered runtime-object constructor at `0x004163B2`, guarded submission,
object creation, event-flags set/wait/create, tagged-handle acquire/release,
semaphore creation, message-queue creation, message-queue put/get, unsigned
bit width, count-trailing-zeros, and floor-log2. Their 171 direct caller
edges, two registered-pointer ingress paths, and complete 4,486 stock bytes
are pinned. Apple clang emits 3,822 Thumb bytes. Ninety-five
strict relocations bind
only this source-owned cluster.

Host tests cover quotient boundaries and deterministic random values, signed
extrema, digit boundaries, parser behavior, decimal/hex output, case selection,
nullable outputs/strings, repeat counts, every supported formatter conversion,
width/precision, CRLF insertion, float fallbacks, and null-output quirks. Both
compiler profiles, exact stock redirects, provider ownership, and complete
unsigned packages reproduce. At this milestone the aggregate was 83 routed functions,
4,927 source bytes, 5,938 patch bytes, 12 alignment bytes, and 142,661
retained official bytes. Live boot and formatter/parser caller-path validation
remains blocked by unavailable authorized responsive hardware. The literal
pool at `0x00415FDA`, the SRAM literal at `0x0041658C`, and the queue-wrapper
literal pool `[0x0041699A,0x004169A4)` remain authenticated data; the next
distinct executable complete body starts at `0x004169FC`. See
`docs/research/g2-bootloader-runtime-bit-helpers-4169a4-4169fc-source-closure.md`.

## Current TLSF v3.1 block-header, topology, alignment, and mapping increment

The twelve complete authenticated entries at `[0x004169FC,0x00416AAA)` now
route to the bounded BSD-3-Clause TLSF v3.1 source adaptation. The 174 stock
bytes and 43 direct callers are pinned. Both reviewed compiler profiles emit
the same 98 relocation-free Thumb bytes. Host tests cover size/status masking,
flag preservation and mutation, last-block detection, the eight-byte
block/user-pointer transform, and offset arithmetic.

The following eight complete entries at `[0x00416AAA,0x00416BCE)` now route
to the bounded TLSF physical-block and alignment adaptation. Their 292 stock
bytes, 15 direct callers, 280 compiled bytes, and 12 strict source-to-source
relocations are pinned. Host tests cover previous/next/link topology, free/used
state propagation, integer and pointer alignment, and all recovered assertion
seams.

The following three complete entries at `[0x00416BCE,0x00416C4E)` route to
the request-size and class-mapping adaptation. Their 128 stock bytes, five
direct callers, 118 compiled bytes, and four strict relocations are pinned.
Host tests cover size limits, small/large insertion classes, and rounded
allocation-search classes.

The following three complete entries at `[0x00416C4E,0x00416E04)` route to
the free-list selection and mutation adaptation. Their 438 stock bytes, four
direct callers, 384 Apple-compiled bytes, and five strict relocations are
pinned. Host tests cover current/next-class search, exhaustion, sentinel
links, head/non-head removal, insertion, and both bitmap levels.

The following ten complete entries at `[0x00416E04,0x0041711C)` route to the
TLSF allocator-operation adaptation. Their 792 stock bytes, 748 Apple-compiled
bytes, and 58 strict relocations are pinned. Host tests cover bounds, split,
leading/trailing trim, absorption, both coalescing directions, free-block
lookup, exhaustion, and used-block preparation.

The following seven complete entries at `[0x0041711C,0x004172DA)` route to the
TLSF public allocator adaptation. Their 446 stock bytes, 376 Apple-compiled
bytes, and seven strict relocations are pinned. Host tests cover control
initialization, pool bounds/alignment and sentinel setup, creation failure and
success, malloc exhaustion, pointer conversion, null-free, coalescing, and
reinsertion.

The aggregate is now 126 routed functions and 84 runtime functions: 6,756
authenticated runtime stock bytes, 5,826 compiled runtime bytes, 259
fail-closed direct topology entries, two registered-pointer ingress paths, and
181 strict relocations. Provider accounting is 6,931 source bytes, 8,208 patch
bytes, 14 alignment bytes, and 140,391 retained official bytes. Apple produces
a 6,944-byte overlay and 155,544-byte provider; Linux produces a 6,924-byte
overlay and 155,524-byte provider. The retained transition data ends at
`0x0041733C`; the 1,944-byte EasyLogger service block through `0x00417AD4`
remains a software gap.

No image was signed, flashed, installed, reset, or booted. Live allocator and
caller-path validation is explicitly blocked by unavailable authorized
responsive G2 hardware evidence. See
`docs/research/g2-bootloader-tlsf-block-primitives-4169fc-416aaa-source-closure.md`.
The succeeding topology tranche is documented in
`docs/research/g2-bootloader-tlsf-block-topology-416aaa-416bce-source-closure.md`.
The succeeding mapping tranche is documented in
`docs/research/g2-bootloader-tlsf-mapping-416bce-416c4e-source-closure.md`.
The succeeding free-list tranche is documented in
`docs/research/g2-bootloader-tlsf-free-lists-416c4e-416e04-source-closure.md`.
The allocator-operation and public-API tranches are documented in
`docs/research/g2-bootloader-tlsf-allocator-416e04-41711c-source-closure.md`
and `docs/research/g2-bootloader-tlsf-public-41711c-4172da-source-closure.md`.

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

## MX25U25643G JEDEC-ID closure through 0x004205F4

The complete authenticated `[0x0042059E,0x004205F4)` entry routes to a
relocation-free 100-byte clean-room leaf in both reviewed toolchains. Host
tests pin command `0x9F`, receive length three, failure logging and output
preservation, and big-endian three-byte packing. Apple/Linux overlay/provider
identities are 12,168/160,768 and 12,148/160,748 bytes. Accounting is 12,153
source-owned, 13,466 generated patch, 16 alignment, and 135,133 retained
official bytes across 178 functions, 159 relocated leaves, and 176 patch
sites. Packages are 4,742,346 / 4,518,336 bytes with 6,507 / 3,454 placed
regions. No hardware operation occurred; physical JEDEC/MSPI/XIP/cold-boot
evidence is unavailable and retained executable bodies from `0x004205F4`
prevent a completeness claim. See
`docs/research/g2-bootloader-mspi-read-id-42059e-4205f4-source-closure.md`.

## MX25U25643G read-transfer closure through 0x0042069E

The complete authenticated `[0x004205F4,0x0042069E)` entry routes to the same
relocation-free 172-byte clean-room leaf under both reviewed compilers. Host
tests pin all validation statuses, the exact 24-byte descriptor, timeout,
HAL-status propagation, and failure diagnostics. Apple/Linux overlay/provider
identities are 12,340/160,940 and 12,324/160,924 bytes. Accounting is 12,325
source-owned, 13,636 generated patch, 16 canonical alignment, and 134,963
retained official bytes across 179 functions, 160 relocated leaves, and 177
patch sites. Packages are 4,742,518 / 4,518,512 bytes with 6,509 / 3,455
placed regions. No hardware operation occurred; physical descriptor/HAL/MSPI/
XIP/cold-boot evidence is unavailable and retained executable bodies from
`0x0042069E` prevent a completeness claim. See
`docs/research/g2-bootloader-mspi-read-transfer-4205f4-42069e-source-closure.md`.

## MX25U25643G write-transfer closure through 0x0042074E

The complete authenticated `[0x0042069E,0x0042074E)` entry routes to
`open_cfw_bootloader_mspi_write_transfer_42069e`. Stock SHA-256 is
`18bdd1fb9df8bf0b73bb5ed09e8f9ed218ba263f8f11caf97c98fc17af2aa20e`;
the 5,396-byte clean-room source hashes to
`7fa590ec5cd0fbd87feb193c9bdec3becb0a6acea6334555c84683e3565451c1`.
Host and stock checks cover statuses, both bounds, null/zero acceptance, exact
descriptor bytes, eight callers, HAL propagation, and failure-only logging.
Both reviewed toolchains emit the same relocation-free 148-byte leaf,
`dac51840015d8553b2684538ff0a5a092d6c03122aa933a3af8d706a2e9d2b73`.

Canonical accounting is 12,473 source-owned, 13,812 generated patch, 16
alignment, and 134,787 retained official bytes across 180 functions, 161
relocated leaves, and 178 patch sites. Apple/Linux packages contain 6,511 /
3,456 placed regions plus two unresolved physical regions. No hardware action
occurred. Authorized responsive right-temple evidence is unavailable, the
left temple must remain stock, and later executable bodies beginning at
`0x0042074E` prevent a completeness claim. See
`docs/research/g2-bootloader-mspi-write-transfer-42069e-42074e-source-closure.md`.

## MX25U25643G busy-status closure through 0x004207A2

The complete authenticated `[0x0042074E,0x004207A2)` entry routes to
`open_cfw_bootloader_mspi_busy_status_42074e`. Stock SHA-256 is
`33e47f7e0bf37502f2f2dd20196d15b67a1f3ef336cd48538ac99f6ceed0e6e5`;
the 3,114-byte clean-room source hashes to
`361432557372303651f41bb8d3446d1f18f1753914fb8227fd6a4c57355685b8`.
Host and stock checks cover the zeroed scratch object, command `0x05`, exact
one-byte read contract, two callers, raw failure status and diagnostic, and
bit-7 Boolean return. The reviewed compilers emit relocation-free 88-byte
leaves with profile-specific pinned hashes.

Canonical accounting is 12,561 source-owned, 13,896 generated patch, 16
alignment, and 134,703 retained official bytes across 181 functions, 162
relocated leaves, and 179 patch sites. Apple/Linux packages contain 6,513 /
3,457 placed regions plus two unresolved physical regions. No hardware action
occurred. Authorized responsive right-temple evidence is unavailable, the
left temple must remain stock, and later executable bodies beginning at
`0x004207A2` prevent a completeness claim. See
`docs/research/g2-bootloader-mspi-busy-status-42074e-4207a2-source-closure.md`.

## MX25U25643G ready-poll closure through 0x00420800

The complete authenticated `[0x004207A2,0x00420800)` cluster routes to
`open_cfw_bootloader_mspi_wait_ready_4207a2` and
`open_cfw_bootloader_mspi_wait_ready_default_4207f4`. Its 82- and 12-byte
stock bodies and 3,531-byte clean-room source are hash-pinned. Host and stock
checks cover the 200-poll fast phase, five-unit delay, caller-bounded
context-aware phase, notification/delay selection, fixed bound 500,
success/timeout returns, and all callers. Both reviewed compilers emit
dependency-free 88- and 12-byte leaves.

Canonical accounting is 12,661 source-owned, 13,990 generated patch, 16
alignment, and 134,609 retained official bytes across 183 functions, 164
relocated leaves, and 181 patch sites. Apple/Linux packages contain 6,517 /
3,459 placed regions plus two unresolved physical regions. No hardware action
occurred. Authorized responsive right-temple evidence is unavailable, the
left temple must remain stock, and later executable bodies beginning at
`0x00420800` prevent a completeness claim. See
`docs/research/g2-bootloader-mspi-wait-ready-4207a2-420800-source-closure.md`.

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

## Current EasyLogger control, output, lock-enable, and boot-port closure

The production provider replaces all ten authenticated EasyLogger control
entries in `[0x0041733C,0x004176CE)`, the complete 1,026-byte `elog_output`
entry `[0x004176CE,0x00417AD0)`, and the complete 60-byte
`elog_output_lock_enabled` entry `[0x00417B7C,0x00417BB8)`. Eleven complete
boot-port entries in `[0x0041A648,0x0041A700)` are also source-routed; the
22-byte `[0x0041A6DA,0x0041A6F0)` format/literal island remains official.
The four bytes at
`[0x00417AD0,0x00417AD4)` remain authenticated CSI-start literal/alignment
data.

The `elog_output` source is 30,999 bytes, SHA-256
`60859f54b54e14e4a22c180d61ea76bd63b358d6896c4787d2d0f7d40816a500`.
Its Apple leaf is 1,060 bytes at `0x004362DC`, SHA-256
`b64c49b0615fd3cb4d5aba393ea929024fc05a7e884eea41019777b6b667d4ce`,
with zero relocations. The lock-enable source is 2,981 bytes, SHA-256
`dde99764f5b84ceec45b30880708b2793443395deb715646c15fd14299c5c8af`;
both toolchains emit the same relocation-free 36-byte leaf, SHA-256
`9ea9783eda65110ea7b7df1bfe4fdfbff1bc670a9bbc91e929f694110ef3cf3f`.
The 12,540-byte port source hashes to
`2d2196f1eed0c4d3e712e6ae8cffef60793dfdeecdb9327c24c9083b31f39677`;
both profiles emit the same eleven relocation-free leaves totaling 204 bytes.

Current Apple overlay/provider identities are 9,088 bytes /
`aeceaf38dee61ece3a1fc9518d5d08dd5eb4148d3ff8811659fe695a24cb1578`
and 157,688 bytes /
`48bc79d2391b5842316fe9c045727b90da96009ecd2dbc21d70fd3af5e3acff7`.
Linux identities are 9,072 bytes /
`34d79ac61578fb5c189b06a15c44731506c9cf92f7642f21b531fedc0c0dc2d3`
and 157,672 bytes /
`9fcb060ca96964b71da9b1c6f75b1afc5d923a285ce07f6d7e43de31c311be75`.
Canonical Apple accounting is 9,075 source-owned, 10,370 generated
patch-site, 14 alignment, and 138,229 retained official bytes across 130
relocated leaves, 149 functions, and 147 patch sites.

Behavioral, stock/caller, target-compile, exact-mutation, dual-profile,
manifest, package, and flash-plan checks are offline. No signer, device,
debugger, serial endpoint, flasher, reset, or boot operation was accessed.
Live mutex/scheduler/transport/exception behavior remains blocked by
unavailable authorized responsive right-temple hardware; the authorized left
temple must remain stock. The remaining bootloader body prevents a
firmware-wide completeness claim.

## Current EasyLogger channel-driver and transfer-transport closure

The production provider additionally replaces the complete 14-byte
level-dropping channel-one driver `[0x0041B854,0x0041B862)` and complete
158-byte four-channel descriptor transport `[0x0041F918,0x0041F9B6)`. The
10,235-byte clean-room source hashes to
`23a5180d3de5e45625f8323a226291d9f5ced532d7d73a320e57640794161d1c`.
Both reviewed toolchains emit identical relocation-free 16-byte and 120-byte
leaves.

Current Apple overlay/provider identities are 9,224 / 157,824 bytes with
SHA-256 `790603494de6a154f9032c4e7257b4c203e477893619c0b25325b972b39c45da`
and `ed616af6c46214891f25e3102f04554129a989fc83422700eb29d6242d3e68f5`.
Linux identities are 9,208 / 157,808 bytes with SHA-256
`ffd38e6fd268398b0c8c5cc5afd0d898e2fe3cb62d000f2c91b96e4682f8b9a8` and
`1d4c130d0e9ac6de37b8bfe9c682b096eff5d85048faaa22fd414b1da3bc622c`.
Canonical accounting is 9,211 source-owned, 10,542 generated patch, 14
alignment, and 138,057 retained official bytes across 151 functions, 132
relocated leaves, and 149 patch sites.

Host tests cover validation, descriptor fields, level discard/channel-one
routing, completion clearing/polling, start failure, and timeout return policy.
No hardware operation occurred. Live transfer/DMA/interrupt/timing evidence is
blocked by unavailable authorized responsive right-temple hardware; the left
temple must remain stock. Later retained executable bodies prevent a
firmware-wide completeness claim.

## Current boot delay and initializer-service closure

The production provider additionally replaces the complete millisecond delay
`[0x0041F9D8,0x0041F9E6)`, raw delay `[0x0041F9E6,0x0041F9EE)`, initializer
priority comparator `[0x0041F9F0,0x0041F9F8)`, and initializer runner
`[0x0041F9F8,0x0041FA40)`. The 6,978-byte clean-room source hashes to
`99aa433811660dd98b1e927d99fdbdb3d2214ad7a88d30ed36803305873cf693`.
The four authenticated stock bodies total 102 executable bytes; their four
relocation-free source leaves total 96 Thumb bytes.

The stock and host oracles pin wrapping millisecond conversion, raw-delay
forwarding, priority comparison, the four-record table at
`[0x00433440,0x00433460)`, scratch `0x20022E00`, 256-record cap, sort seam,
stored odd comparator pointer, stable dispatch order, and null-callback skip.
All direct callers and the comparator pointer at `0x0041FA4C` are
authenticated.

Current Apple overlay/provider identities are 9,320 / 157,920 bytes with
SHA-256 `aaefcef3e31df12ec06a2ee7f505430f17daba8061099677143b24505ea96dc7`
and `56350fb0fc8d663dc2202f11389573b52ddd30536e81f44539006f7810f2744d`.
Linux identities are 9,304 / 157,904 bytes with SHA-256
`6be4f564d6ef9ace9c98de17bf2cc082142440a3da3716521a9e3e529ebb017b` and
`3961d3432af2cbeb83731d79792071161980decbc6cf635c57b6a396f09f3504`.
Canonical accounting is 9,307 source-owned, 10,644 generated patch, 14
alignment, and 137,955 retained official bytes across 155 functions, 136
relocated leaves, and 153 patch sites.

`make source`, focused host/target tests, dual-profile routing, exact mutation,
manifest, unsigned package, and flash-plan checks pass. No hardware operation
occurred. Live delay accuracy, scheduler interaction, initializer ordering,
callback effects, and cold-boot evidence remain blocked by unavailable
authorized responsive right-temple hardware; the left temple must remain
stock. Later retained executable bodies prevent a firmware-wide completeness
claim.

## MX25U25643G public initializer closure through 0x0042052A

The complete authenticated `[0x00420476,0x0042052A)` entry now routes to
`open_cfw_bootloader_mspi_driver_init_420476`. Stock and host evidence pin
low-level-init failure, exact delay and device/timing preparation, JEDEC-ID
read and diagnostics, final-mode setup, event-flags initialization, MSPI
enable, and both short-circuiting error returns.

Both profiles emit a 204-byte leaf with five strict source-owned call
relocations. Apple/Linux overlay/provider identities are 11,932/160,532 and
11,912/160,512 bytes. Canonical accounting is 11,917 source-owned, 13,264
generated patch, 16 alignment, and 135,335 retained official bytes across 176
functions, 157 relocated leaves, and 174 patch sites. Unsigned packages are
4,742,110 / 4,518,100 bytes. No hardware operation occurred. Live JEDEC, HAL,
RTOS, interrupt, MSPI, external-flash, XIP, timing, and cold-boot evidence is
blocked by unavailable authorized responsive right-temple hardware; the left
temple must remain stock. Executable bodies after `0x0042052A` prevent a
completeness claim.

## MX25U25643G soft-reset closure through 0x0042059E

The complete authenticated `[0x0042052A,0x0042059E)` entry now routes to a
136-byte clean-room leaf in both profiles. Stock and host evidence pins reset
enable `0x66`, reset `0x99`, 1/50-ms delays, failure-only logs, and continued
execution after failures. Canonical accounting is 12,053 source-owned, 13,380
generated patch, 16 alignment, and 135,219 retained official bytes across 177
functions, 158 relocated leaves, and 175 patch sites. Apple/Linux packages are
4,742,246 / 4,518,236 bytes. No hardware operation occurred; live reset,
MSPI/XIP, external-flash, timing, and cold-boot evidence is blocked by
unavailable authorized responsive hardware. Executable bodies after
`0x0042059E` prevent a completeness claim.

## Current allocator-initializer closure

The provider now replaces the complete 56-byte TLSF pool initializer
`[0x0041FD70,0x0041FDA8)`. Its 2,940-byte clean-room source hashes to
`53dc0ff1c3c47d2afcb585f6753e4eaaa29ae9494c705e0f73ff5929dd487713`.
Apple/Linux clang emit distinct relocation-free 88-byte bodies at offsets
9,916 / 9,900, with SHA-256
`1a588b40d59408de4b8f541890868a18a827a77c7333c958687ebeae21f30ddc`
and `98ad36432a4e12f52535ab869d025cbbf03f57d63bdba9553541169b73a9e190`.

Stock, caller, literal-pool, and host oracles pin the pool clear at
`0x20081000` for `0x70800` bytes, retained TLSF create call, handle publication
at `0x2002718C`, complete diagnostic record, zero return, and sole caller at
`0x0041B89E`. Apple overlay/provider identities are 10,004 / 158,604 bytes
with SHA-256
`a27f7ba39fdfe6a7364d59577cfa387a0a601aedf773612d1cb1b77700c6538d`
and `da312bd3b1a4105f75788107d147d5397edba0014c72d11584d5c9552c24cab7`;
Linux identities are 9,988 / 158,588 bytes with SHA-256
`15784fef039b93caaa26b202c61b115b4d0947f0ec253b7232dd43e828787b50`
and `a64974dce84415f4031847e1f71b5397cd0c366a31b8786d6f6e311ff53bd7b2`.
Canonical accounting is 9,991 source-owned, 11,366 generated patch, 14
alignment, and 137,233 retained official bytes across 159 functions, 140
relocated leaves, and 157 patch sites.

Unsigned Apple/Linux packages are 4,740,182 / 4,516,176 bytes with SHA-256
`8041ac27ae80d9cb331d27363281d7dfb259024a4276e80783bcca4b3e7a04a2`
and `7591a1ab14efac218d2610f2192f1b554c1f366ceb917ba911fc9059c8965bd6`.
No hardware operation occurred. Live allocator, SRAM, logging, and cold-boot
evidence remains blocked by unavailable authorized responsive right-temple
hardware; the left temple must remain stock. Executable bodies after
`0x0041FDA8` prevent a firmware-wide completeness claim.

## Current IRQ-service closure

The provider now replaces the three complete IRQ-service entries
`[0x0041FDC0,0x0041FE28)`. The shared 3,518-byte clean-room source hashes to
`c1b495b5d4de6ab8045e8e9f225736c9d3b0cabbe93d712b4b347675394a377b`.
Both reviewed toolchains emit the same relocation-free 32-, 32-, and 48-byte
NVIC-enable, priority, and MSPI-ISR leaves. Stock/caller/vector and host oracles
pin signed IRQ gating, NVIC/SCB indexing, four-bit priority encoding, MSPI
handle/status propagation, and status-get/clear/service order.

Apple overlay/provider identities are 10,116 / 158,716 bytes with SHA-256
`f8088800044634921e2446b45e7133e0a9d3232e5ce5ad78f31eb6990b1e32b8`
and `1594aefde3a94be29dec7c4d3ab3ac20cf57e2a6f220f7eeca8609ffb222dede`;
Linux identities are 10,100 / 158,700 bytes with SHA-256
`ae413000d796c164e5bc06f197ff9bbf2543140d2ed6a50bfc62eecb225bb213`
and `34259f9296124eed2b7cebc3488994087b3308fc26383d78f82fd9948e568eae`.
Accounting is 10,103 source-owned, 11,470 generated patch, 14 alignment, and
137,129 retained official bytes across 162 functions, 143 relocated leaves,
and 160 patch sites. Unsigned packages are 4,740,294 / 4,516,288 bytes with
SHA-256 `b2ce7f54b0d6fb58fe46c78d715f7498d9188dba826197225ad203db0bc64181`
and `c8c34b6acf8ed5b356f61334121e5c6d3bfc8628302bd3af4398192c83403a88`.
No hardware operation occurred. Live NVIC/MSPI/interrupt/cold-boot evidence is
blocked by unavailable authorized responsive right-temple hardware; the left
temple must remain stock. Executable bodies after `0x0041FE28` prevent a
firmware-wide completeness claim.

## Current MSPI-control closure

The complete `[0x0041FE28,0x0041FE62)` enable/disable pair now routes to two
relocation-free clean-room leaves. Host and stock evidence pins idempotence,
handle/mode/flag arguments, state updates, and all callers. Apple/Linux
overlay/provider identities are 10,180/158,780 and 10,164/158,764 bytes;
accounting is 10,167 source-owned, 11,528 generated patch, 14 alignment, and
137,071 retained official bytes across 164 functions, 145 relocated leaves,
and 162 patch sites. Unsigned packages are 4,740,358 / 4,516,352 bytes. No
hardware operation occurred. Live MSPI behavior is physically blocked and
executable bodies after `0x0041FE62` prevent a completeness claim.

## Event-flags service closure through 0x0041FF08

The complete `[0x0041FE62,0x0041FF08)` init/acquire/release cluster now routes
to three clean-room relocation-free leaves. Authenticated stock identities,
all three direct callers, SRAM handle/configuration addresses, retained
create/acquire/release calls, wait-forever semantics, and exact failure-only
EasyLogger records are pinned by the host and stock-topology tests.

The later MSPI guard and XIP-config entries are now source-owned as well.
Apple/Linux overlay identities are 10,500 / 10,484 bytes; provider identities
are 159,100 / 159,084 bytes. Canonical accounting is 10,487 source-owned,
11,782 generated patch, 14 alignment, and 136,817 retained official bytes
across 170 functions, 151 relocated leaves, and 168 patch sites. Unsigned
packages are 4,740,678 / 4,516,672 bytes. No hardware operation occurred.
Live RTOS contention, logger, and cold-boot evidence is blocked because no
authorized responsive right temple is available and the left must remain
stock. Executable bodies after `0x0041FF60` prevent a completeness claim.

## Paired MSPI guard closure through 0x0041FF34

The complete `[0x0041FF08,0x0041FF34)` guard pair now routes to two
relocation-free clean-room leaves. The authenticated stock bodies are 22 bytes
each with SHA-256 `02963ef6…0dc5` and `ecb3a585…dddd`. Stock scans pin three
callers per entry and the shared `0x200271C5` bypass-byte literal. Host tests
prove that enter always acquires before conditionally disabling MSPI, while
exit conditionally enables MSPI before always releasing.

Apple/Linux leaves are identically 36 / 32 bytes with SHA-256
`e9000427…07eb` / `dfb2fdd9…e40`. With the later XIP-config entry included,
the cumulative provider accounts for 10,487 source-owned, 11,782 generated
patch, 14 alignment, and 136,817 retained
official bytes. Both unsigned packages and flash plans reproduce; no hardware
operation occurred. Live contention, MSPI timing, and cold-boot evidence is
blocked because no authorized responsive right temple is available and the
left must remain stock. Executable bodies after `0x0041FF60` prevent a
completeness claim.

## MSPI XIP-config closure through 0x0041FF60

The complete authenticated `[0x0041FF34,0x0041FF60)` entry now routes to the
relocation-free clean-room function
`open_cfw_bootloader_mspi_xip_config_41ff34`. Its stock body is 44 bytes with
SHA-256 `384a53a6…eabe76`; stock scans authenticate callers `0x004203B0`,
`0x00420ED6`, and `0x00420F36`, configuration `0x2000023C`, handle word
`0x200270DC`, and retained control entry `0x004251C0`. Host tests prove the
low-byte selector, config-byte-five `8`/`0` mutation, write-before-call order,
request 16, exact arguments, and ignored status.

Both profiles emit the same 36-byte leaf with SHA-256 `0cc0ac05…87eb`.
Canonical accounting is 10,487 source-owned, 11,782 generated patch, 14
alignment, and 136,817 retained official bytes across 170 functions, 151
relocated leaves, and 168 patch sites. Apple/Linux packages are 4,740,678 /
4,516,672 bytes. No hardware operation occurred. Live XIP transition,
external-flash timing, and cold-boot evidence is blocked because no authorized
responsive right temple is available and the left must remain stock.
Executable bodies after `0x0041FF60` prevent a completeness claim.

## Bit-run helper closure through 0x00420002

The complete authenticated `[0x0041FF60,0x00420002)` pair now routes to the
relocation-free clean-room functions
`open_cfw_bootloader_longest_ones_run_41ff60` and
`open_cfw_bootloader_longest_ones_center_41ff74`. Their stock bodies are 20 /
142 bytes with SHA-256 `93e9d3dc…c4ad2` / `3c89f5f4…679ed`; stock scans pin
sole callers `0x004200BE` and `0x00420158`. Host tests prove the exact scalar
contract across boundary patterns and 2,048 deterministic random words.

Apple leaves are 16 / 126 bytes; Linux leaves are 16 / 110 bytes. Canonical
accounting is 10,629 source-owned, 11,944 generated patch, 14 alignment, and
136,655 retained official bytes across 172 functions, 153 relocated leaves,
and 170 patch sites. Apple/Linux packages are 4,740,820 / 4,516,798 bytes. No
hardware operation occurred. Live mask meaning, MSPI training/timing,
external-flash, and cold-boot evidence is blocked because no authorized
responsive right temple is available and the left must remain stock.
Executable bodies after `0x00420002` prevent a completeness claim.

## MSPI timing-scan closure through 0x004201BA

The complete authenticated `[0x00420002,0x004201BA)` entry now routes to
`open_cfw_bootloader_mspi_timing_scan_420002`. Its 440-byte stock body has
SHA-256 `9618b6be…d6dcb6`; the retained caller is `0x004201CA`. Stock evidence
also pins the 36-by-6 table at `0x20000244`, expected packed JEDEC ID
`0x002539C2`, control/read seams at `0x004251C0` / `0x0042059E`, and helper
calls to `0x0041FF60` / `0x0041FF74`.

Host tests execute all 1,152 row/fine candidates and prove pass-mask
construction, first-strictly-longer row selection, centered output, the
all-failed edge case, and all three diagnostic records. Apple and Linux each
emit a 420-byte leaf with exactly two strict `R_ARM_THM_CALL` relocations.
Canonical accounting is 11,049 source-owned, 12,384 generated patch, 16
alignment, and 136,215 retained official bytes across 173 functions, 154
relocated leaves, and 171 patch sites. Apple/Linux packages are 4,741,242 /
4,517,220 bytes. No hardware operation occurred. Electrical timing-window,
external-flash, XIP, and cold-boot evidence remains blocked because no
authorized responsive right temple is available and the left must remain
stock. Executable bodies after `0x004201BA` prevent a completeness claim.

## Automatic MSPI timing-selection closure through 0x00420254

The complete authenticated `[0x004201BA,0x00420254)` entry now routes to
`open_cfw_bootloader_mspi_timing_auto_4201ba`. Its 154-byte stock body has
SHA-256 `a31a2497…f2b9b7`; the sole retained caller is `0x004204BA`. Stock
evidence pins the zero-fill seam, the call to the source-owned exhaustive scan,
both diagnostic calls, the active six-byte configuration at `0x2000023C`, and
the success/failure record metadata.

Host tests prove zero initialization, success publication, failure preservation,
diagnostics, and preservation of the two adjacent bytes touched only by the
stock compiler's widened copy. Apple emits a 172-byte leaf and Linux a 184-byte
leaf; each has exactly one strict `R_ARM_THM_CALL` relocation to the timing scan.
Canonical accounting is 11,221 source-owned, 12,538 generated patch, 16
alignment, and 136,061 retained official bytes across 174 functions, 155
relocated leaves, and 172 patch sites. Apple/Linux packages are 4,741,414 /
4,517,404 bytes. No hardware operation occurred. Electrical timing-window,
external-flash, XIP, and cold-boot evidence remains blocked because no
authorized responsive right temple is available and the left must remain stock.
Executable bodies after `0x00420254` prevent a completeness claim.

## Low-level MSPI initializer closure through 0x00420476

The complete authenticated `[0x00420254,0x00420476)` entry now routes to
`open_cfw_bootloader_mspi_low_level_init_420254`. Its 546-byte stock body has
SHA-256 `a3c3fab2…cb94`; the sole retained caller is `0x00420480`. Stock and
host evidence pin the busy rejection, initialize/power/configure/device/enable
sequence, default/custom device configuration, cleanup and error policy, TCB
configuration, XIP/pin setup, interrupt mask `0x1A80`, IRQ 21/priority 4,
state/output publication, and diagnostics.

Apple and Linux each emit a 492-byte leaf with four strict source-owned call
relocations. Overlay/provider identities are 11,728/160,328 and
11,708/160,308 bytes. Canonical accounting is 11,713 source-owned, 13,084
generated patch, 16 alignment, and 135,515 retained official bytes across 175
functions, 156 relocated leaves, and 173 patch sites. Unsigned packages are
4,741,906 / 4,517,896 bytes. No hardware operation occurred. Live HAL,
interrupt, MSPI, external-flash, XIP, timing, and cold-boot evidence is blocked
by unavailable authorized responsive right-temple hardware; the left temple
must remain stock. Executable bodies after `0x00420476` prevent a completeness
claim.

## Current pin-group dispatcher closure

The production provider additionally replaces `[0x0041FADC,0x0041FCF6)`, a
538-byte two-bank pin-group dispatcher, with a 428-byte relocation-free leaf.
Stock/caller and host oracles pin both callers, low-byte subtype selection,
cumulative group ordering, 30 SRAM configuration-word slots, every pin
number, and all no-op cases. The 4,772-byte source hashes to
`2608a97a8a2fc3e8e63e3eeae78dbec81646e4d650b407bbcb9ebae86e9fff86`.

Apple overlay/provider identities are 9,916 / 158,516 bytes with SHA-256
`f00be08414c7e4731ed8e2e61ed1f8041f105c520d941c0b26d16ba4f4e8143a`
and `5ec3947c373c9d765d8c3385c0f7d436f8c4599ddae90429bc48263f1f80783a`;
Linux identities are 9,900 / 158,500 bytes with SHA-256
`1b531362e7f7ce06225ecdc068dcc0b124eeb5c84a1570f7f071e11497acdd93`
and `06e369900458478ec088319400809d6bfb7883c3ddeb0808e3fff0f8bb52e4f5`.
Canonical accounting is 9,903 source-owned, 11,310 generated patch, 14
alignment, and 137,289 retained official bytes across 158 functions, 139
relocated leaves, and 156 patch sites. Live pinmux/GPIO/electrical behavior is
blocked by unavailable authorized responsive right-temple hardware; later
retained executable bodies prevent a firmware-wide completeness claim.

## Current guarded-teardown closure

The production provider additionally replaces the complete 56-byte guarded
teardown entry `[0x0041FA98,0x0041FAD0)`. Its 4,521-byte clean-room source
hashes to
`ad8f5eba68fce82f9e3d7807f2aed0ef207e76fff8840e7497429f9c06e960e9`.
Both reviewed toolchains emit the same relocation-free 72-byte leaf at Apple
/ Linux overlay offsets 9,320 / 9,304.

The stock, caller, and host oracles pin the exact-active guard, both
status-stage orderings, independent fail-stop branches, state-word clear,
pin-28 configuration word and call, final guard clear, sole caller, and
following literal pool. Current Apple overlay/provider identities are 9,392 /
157,992 bytes with SHA-256
`2764ebb28ccde7977522ee318869a03805dfa2e0bc718c16de51c2ce4579828f` and
`0fa99abd573ab6a8845c3807cef69d29ee29d46606f1044bae6b571971dff659`.
Linux identities are 9,376 / 157,976 bytes with SHA-256
`66bb62b17d33dbdec3f1015299fee2f04cb435a15d8a335b98c64eb6d000dac6`
and `bddf904854256b0403d5750d756ca2b98d379434362918a94f876fa7c69e3427`.
Canonical accounting is 9,379 source-owned, 10,700 generated patch, 14
alignment, and 137,899 retained official bytes across 156 functions, 137
relocated leaves, and 154 patch sites.

The unsigned Apple/Linux packages are 4,739,570 / 4,515,564 bytes with
SHA-256 `f69e3c8e9d8fc2408a48eeff99e6d96cbbf55f77e052881a3260223bf2c7b779`
and `f92667c2f10b51cbd49129924bd4bf10c77145dccdc460e18840d4ebeadf8a72`.
No hardware operation occurred. Live fail-stop, pin, power-state, caller-path,
and cold-boot evidence remains blocked by unavailable authorized responsive
right-temple hardware; the left temple must remain stock. Later retained
executable bodies prevent a firmware-wide completeness claim.

## Current platform-setup closure

The production provider additionally replaces the complete 72-byte platform
setup `[0x0041FA50,0x0041FA98)`. Its 5,487-byte clean-room source hashes to
`5126096f05bd4d66f7148fd564c7defdb9b4b49729d358f6a768579fcfe372d1`.
Both reviewed toolchains emit the same relocation-free 96-byte leaf at Apple
/ Linux offsets 9,392 / 9,376, SHA-256
`e064ce74a17db06a9bb9d6dab1bbaf807c01215d270c916c02782c90a55a4a67`.

Stock/caller and host oracles pin guarded teardown, reset, zero mode
arguments, hard-float `25.0f` derive, exact 20-byte configuration copy and
submit, channels four/five, call order, and the sole caller at `0x0041B87E`.
Apple overlay/provider identities are 9,488 / 158,088 bytes with SHA-256
`da89534353b40e8787963c24dc0aa6209b11948cd128b8d05115525685b53adc`
and `5283432f02f86b2c62dea8eac44c567f99b3c4d261c3412ab638b67535486145`;
Linux identities are 9,472 / 158,072 bytes with SHA-256
`1b97e43f2615b0281850b16c5f14aeb31bd6af3d792008bb62a9c60cff2b4b5b`
and `991fc763c08fdf890d18840d84b6a386864dae812757035faa4e216a1c4663e3`.
Canonical accounting is 9,475 source-owned, 10,772 generated patch, 14
alignment, and 137,827 retained official bytes across 157 functions, 138
relocated leaves, and 155 patch sites.

The unsigned Apple/Linux packages are 4,739,666 / 4,515,660 bytes with
SHA-256 `761b09380b08493d69eee02b2912cb1edeb6f14c584973df52d6bcf3e058dae1`
and `8a447d867e6303ed6075ad83067c53350a1e189956d2dc8c7ae6e93b287c12ea`.
No hardware operation occurred. Live reset, VFP callee, configuration,
channel, pin/power, and cold-boot behavior remains blocked by unavailable
authorized responsive right-temple hardware; the left temple must remain
stock. Later retained executable bodies prevent a firmware-wide completeness
claim.
## MX25U25643G address-mode closure through 0x0042086C

The authenticated 108-byte body reads command `0x15`, preserves raw transport
errors, tests bit 5, and emits distinct read-failure and three-byte-mode
diagnostics. It now routes to a relocation-free 124-byte leaf on both reviewed
toolchains. Offline tests and exact routing are green; live MSPI, flash, and
cold-boot evidence remains unavailable. See
`docs/research/g2-bootloader-mspi-4byte-mode-420800-42086c-source-closure.md`.

## MX25U25643G enter-four-byte-mode closure through 0x00420978

The authenticated 232-byte body checks the fixed MSPI handle and ready state,
write-enables the device, issues command `0xB7`, performs the stock ignored
post-command ready poll, verifies address mode with the stock nonzero-success
quirk, and write-disables the device. It now routes to a relocation-free
220-byte leaf on both reviewed toolchains. Host evidence pins all branches,
statuses, diagnostics, calls, and ordering; exact routing, manifest, package,
and analyzer gates are green. The 36-byte predecessor literal region remains
retained and authenticated.

Canonical provider accounting is 13,005 source-owned, 14,330 generated patch,
16 alignment, and 134,269 retained official bytes. The unsigned canonical
package is 4,743,198 bytes with SHA-256
`f7d74c7ae574671b3677c8b94500305482fd89180e17eaa367c9358caaff44e7`.
No hardware operation occurred; live MSPI, status-register, external-flash,
XIP, and cold-boot evidence remains unavailable. See
`docs/research/g2-bootloader-mspi-enter-4byte-mode-420890-420978-source-closure.md`.

## MX25U25643G write-latch closure through 0x004209FC

The complete 58-byte write-enable and 56-byte write-disable wrappers submit
commands `0x06` and `0x04` with otherwise zero transfer fields, return the raw
transport result, and log only failures with their exact stock records. They
now route to two relocation-free 72-byte leaves on both reviewed toolchains.
Host evidence pins success/failure behavior, all seven callers, and the three
surrounding retained literal pools; exact routing, manifest, package, and
analyzer gates are green.

Canonical provider accounting is 13,149 source-owned, 14,444 generated patch,
16 alignment, and 134,155 retained official bytes. The unsigned canonical
package is 4,743,342 bytes with SHA-256
`f0fa1999e7992a0a20ea3897185447b060ae3510e38e2ba3560c8651a9f69d7c`.
No hardware operation occurred; live write-latch, MSPI, external-flash, XIP,
and cold-boot evidence remains unavailable. See
`docs/research/g2-bootloader-mspi-write-latch-420984-4209fc-source-closure.md`.

## MX25U25643G sector-erase closure through 0x00420ADA

The complete authenticated 210-byte body validates the fixed handle, 4-KiB
alignment, and 32-MiB address bound, then executes guarded serial-mode command
`0x20` with ready-poll and write-latch sequencing. It now routes to a
relocation-free 244-byte leaf on both reviewed toolchains. Host evidence pins
every validation and failure stage, raw status propagation, exact diagnostics,
unconditional guarded cleanup, the transfer tuple, the sole caller, and the
preceding retained literal pool.

Canonical provider accounting is 13,393 source-owned, 14,654 generated patch,
16 alignment, and 133,945 retained official bytes. The unsigned canonical
package is 4,743,586 bytes with SHA-256
`9451c86c90a52643fa43cea465f2a82419a5d345b82f4b44e41ef02a5de39da0`.
No hardware operation occurred; live erase, write-latch, MSPI, external-flash,
XIP, and cold-boot evidence remains unavailable. See
`docs/research/g2-bootloader-mspi-sector-erase-420a08-420ada-source-closure.md`.

## MX25U25643G page-program closure through 0x00420C14

The complete authenticated 264-byte body validates the fixed handle, buffer,
length, and 32-MiB start bound, then divides command `0x02` writes across
256-byte page boundaries with guarded serial-mode, ready-poll, and write-latch
sequencing. It now routes to the same relocation-free 256-byte leaf on both
reviewed toolchains. Host evidence pins every validation and failure stage,
multi-page address/buffer/length advancement, raw status propagation, exact
diagnostics, guarded cleanup, transfer tuples, the sole caller, and both
surrounding retained pools.

Canonical provider accounting is 13,649 source-owned, 14,918 generated patch,
16 alignment, and 133,681 retained official bytes. The unsigned canonical
package is 4,743,842 bytes with SHA-256
`1f3191b816b1e30cb82cd06653f63514a2174eebd942b44b92cf43152c4769dd`.
No hardware operation occurred; live page programming, write-latch, MSPI,
external-flash, XIP, and cold-boot evidence remains unavailable. See
`docs/research/g2-bootloader-mspi-program-420b0c-420c14-source-closure.md`.

## MX25U25643G QE closure through 0x00420DFA

The complete authenticated 414-byte body checks the fixed MSPI handle, reads
status register 2 with command `0x05`, compares QE bit 6, and requires
protection bits `0x3C` to be clear before accepting an unchanged state. When
an update is needed, it write-enables, sets or clears QE, clears the protection
bits, writes command `0x01`, and verifies the register. Both stock readiness
results are deliberately ignored. It now routes to the same relocation-free
364-byte leaf on both reviewed toolchains.

Canonical provider accounting is 14,013 source-owned, 15,332 generated patch,
16 alignment, and 133,267 retained official bytes. Apple/Linux overlay
identities are 14,028 /
`ed9269c05166de01a402d2a2be5a975ea36a35d4db0edd13ac879afb836f0407`
and 14,012 /
`de523ff3514355dfccc201ca23b6f06fe95b75671f1c71835e898808d635c974`;
provider identities are 162,628 /
`bd830dafab1c1e9de59e7abce980e7461f3d440b0e5121ab27735513903ffd10`
and 162,612 /
`5d6c596921690cadc11cd902d6c21dc988d48fd6e9675b481423187a6afe35ab`.
The unsigned canonical package is 4,744,206 bytes with SHA-256
`43022429372d51be6a9083eed987cb6fb0c38b1e4504e0fbe82e81c2f34d5971`.

No hardware operation occurred; live QE/status-register/write-latch/MSPI/
external-flash/XIP and cold-boot evidence remains unavailable. See
`docs/research/g2-bootloader-mspi-quad-enable-420c5c-420dfa-source-closure.md`.

## MSPI device-reconfiguration closure through 0x00420E8C

The complete authenticated 132-byte body disables the active MSPI handle,
applies the supplied device configuration, re-enables the controller, and
reapplies pin-group configuration using the published instance and the
configuration byte at offset `+8`. Every nonzero HAL result is diagnosed and
collapsed to status `1`, matching stock behavior. Apple/Linux emit 136/128
bytes with one strict relocation to the source-owned pin-group dispatcher.

Canonical provider accounting is 14,149 source-owned, 15,464 generated patch,
16 alignment, and 133,135 retained official bytes. Apple/Linux overlays are
14,164 / 14,140 bytes; providers are 162,764 / 162,740 bytes. Unsigned packages
are 4,744,342 / 4,520,328 bytes. No hardware operation occurred; live HAL,
pinmux, MSPI, XIP, external-flash, and cold-boot evidence remains unavailable.
See `docs/research/g2-bootloader-mspi-device-reconfigure-420e08-420e8c-source-closure.md`.

## MX25U25643G quad-mode closure through 0x00420F0C

The complete authenticated 128-byte body clones the 24-byte initialized-SRAM
quad template, sets turnaround `8`, read command `0x006C`, device selector
`0x10`, and turnaround-enable `1`, then runs the source-owned device
reconfiguration service. Success enables source-owned XIP policy and submits
HAL control request `0x18` with mode byte `0x10`; either failure is diagnosed
with the exact stock logger identity. The three stock callers are
`0x00420ACE`, `0x00420C08`, and `0x00420F9C`.

Apple/Linux emit 152-byte leaves at overlay offsets 14,164/14,140, with three
strict relocations to source-owned memcpy, device reconfiguration, and XIP
configuration. Canonical provider accounting is 14,301 source-owned, 15,592
generated patch, 16 alignment, and 133,007 retained official bytes. The
Apple/Linux providers are 162,916/162,892 bytes; unsigned packages are
4,744,494/4,520,480 bytes.

No hardware operation occurred. Live initialized-SRAM, HAL, pinmux, MSPI,
XIP, external-flash, and cold-boot evidence remains unavailable. See
`docs/research/g2-bootloader-mspi-set-quad-mode-420e8c-420f0c-source-closure.md`.

## MX25U25643G serial-mode closure through 0x00420F6A

The complete authenticated 90-byte body at `[0x00420F10,0x00420F6A)` invokes
the source-owned device-reconfiguration service with the initialized-SRAM
serial template at `0x2000020C`. Success disables source-owned XIP policy and
submits retained HAL control request `0x18` with mode byte `0`; either failure
is diagnosed with the exact stock logger tag, file, line, and format identity.
The four stock callers are `0x004204B6`, `0x004204BE`, `0x00420A4C`, and
`0x00420B58`; completion is void.

Apple/Linux emit 124-byte leaves at overlay offsets 14,316/14,292, each with
strict relocations to source-owned device reconfiguration and XIP
configuration. Canonical provider accounting is 14,425 source-owned, 15,682
generated patch, 16 alignment, and 132,917 retained official bytes. The
Apple/Linux providers are 163,040/163,016 bytes; unsigned packages are
4,744,618/4,520,604 bytes.

No hardware operation occurred. Live initialized-SRAM, HAL, pinmux, MSPI,
XIP, external-flash, and cold-boot evidence remains unavailable. See
`docs/research/g2-bootloader-mspi-set-serial-mode-420f10-420f6a-source-closure.md`.

## MX25U25643G guarded read closure through 0x00420FF2

The complete authenticated 130-byte body validates the published handle,
buffer, nonzero length, and 32 MiB address limit; enters the source-owned
transaction guard; selects source-owned quad mode; invokes the source-owned
fixed ready wait; constructs the exact 24-byte `0x006C` read descriptor; and
calls the retained Ambiq blocking-transfer boundary with timeout `1000000`.
It always releases the guard after the transfer and returns the raw HAL status.
The ready-wait result is intentionally ignored, matching stock. The direct
littlefs caller is `0x004212EE`.

Apple/Linux emit 152-byte leaves at overlay offsets 14,440/14,416, with four
strict source-to-source relocations. Canonical provider accounting is 14,577
source-owned, 15,812 generated patch, 16 alignment, and 132,787 retained
official bytes. Apple/Linux providers are 163,192/163,168 bytes; unsigned
packages are 4,744,770/4,520,756 bytes.

No hardware operation occurred. Live HAL, pinmux, MSPI, external-flash read,
XIP, littlefs, and cold-boot evidence remains unavailable. See
`docs/research/g2-bootloader-mspi-read-420f70-420ff2-source-closure.md`.

## LittleFS directory-bootstrap closure through 0x004211B0

The complete authenticated 232-byte body checks `/firmware`, `/ota`, `/user`,
and `/log` with the retained LittleFS directory-open ABI. Missing directories
are created; `LFS_ERR_EXIST` and other mkdir errors are diagnosed and
iteration continues; present directories are closed with the close result
ignored; an unexpected open result is diagnosed and returns `-1`. Two stock
initialization callers at `0x004211EC` and `0x00421252` are preserved.

Apple/Linux emit 220/224-byte leaves at overlay offsets 14,592/14,568 with
two strict relocations to source-owned EasyLogger. Canonical provider
accounting is 14,797 source-owned, 16,044 generated patch, 16 alignment, and
132,555 retained official bytes across 195 functions, 176 relocated leaves,
and 193 patch sites. Apple/Linux providers are 163,412/163,392 bytes; unsigned
packages are 4,744,990/4,520,980 bytes.

No hardware operation occurred. Live LittleFS mount/directory mutation,
external-flash persistence, power-loss, logging, and cold-boot evidence is
blocked by unavailable authorized physical evidence. The successor entry at
`0x004211B0` remains the software frontier; firmware-wide functional
completeness is not claimed. See
`docs/research/g2-bootloader-fs-directories-4210c8-4211b0-source-closure.md`.

## LittleFS format/bootstrap closure through 0x00421210

The complete authenticated 96-byte body calls retained public LittleFS
unmount, format, and mount wrappers over the fixed filesystem/configuration
objects. Unmount and format results are deliberately ignored. Mount failure
or source-owned directory-bootstrap failure is diagnosed and mapped to `9`;
success returns `0`. The stock caller at `0x0042126E` is preserved.

Apple/Linux emit 108/112-byte leaves at overlay offsets 14,812/14,792 with
two strict source-to-source relocations. Canonical provider accounting is
14,905 source-owned, 16,140 generated patch, 16 alignment, and 132,459
retained official bytes across 196 functions, 177 relocated leaves, and 194
patch sites. Apple/Linux providers are 163,520/163,504 bytes; unsigned
packages are 4,745,098/4,521,092 bytes.

No hardware operation occurred. Live unmount/format/mount, external-flash
erase/program/persistence, power-loss, diagnostics, and cold-boot evidence is
blocked by unavailable authorized physical evidence. The successor entry at
`0x00421210` remains the software frontier; firmware-wide functional
completeness is not claimed. See
`docs/research/g2-bootloader-littlefs-format-4211b0-421210-source-closure.md`.

## LittleFS initializer/boot-counter closure through 0x004212D8

The complete authenticated 200-byte body mounts the fixed LittleFS instance;
on failure it formats and retries, logging and returning `9` if the retry also
fails. It invokes the source-owned directory bootstrap, logs and calls the
source-owned recovery-format service on directory failure, publishes the
ready word, then opens `boot_count` with flags `0x103`, reads a four-byte value
initialized to zero, increments it, rewinds, writes, closes, and logs the new
count. Recovery and all file-operation statuses are intentionally ignored.
The sole stock caller at `0x0041B8A6` is preserved.

Apple/Linux emit 260-byte leaves at overlay offsets 14,920/14,904 with five
strict source-to-source relocations. Canonical provider accounting is 15,165
source-owned, 16,340 generated patch, 16 alignment, and 132,259 retained
official bytes across 197 functions, 178 relocated leaves, and 195 patch
sites. Apple/Linux providers are 163,780/163,764 bytes; unsigned packages are
4,745,358/4,521,352 bytes.

No hardware operation occurred. Live mount/format, directory mutation,
external-flash persistence, power-loss, readiness, boot-counter, diagnostics,
and cold-boot evidence is blocked by unavailable authorized physical
evidence. The successor entry at `0x004212D8` remains the software frontier;
firmware-wide functional completeness is not claimed. See
`docs/research/g2-bootloader-littlefs-init-421210-4212d8-source-closure.md`.

## LittleFS block-read closure through 0x00421310

The complete authenticated 56-byte callback ignores the configuration
pointer, computes the fixed-partition address with 32-bit arithmetic, and
calls the source-owned guarded MX25U25643G reader. Success returns zero. Every
nonzero device result is logged with block, offset, size, address, and status,
then collapsed to `LFS_ERR_IO` (`-5`). The bootloader LittleFS configuration at
`0x00431070` continues to point at the stock entry, which now redirects to the
source leaf.

Apple/Linux emit 60-byte leaves at overlay offsets 15,180/15,164 with strict
relocations to the source-owned reader and logging dispatcher. Canonical
provider accounting is 15,225 source-owned, 16,396 generated patch, 16
alignment, and 132,203 retained official bytes across 198 functions, 179
relocated leaves, and 196 patch sites. Apple/Linux providers are
163,840/163,824 bytes; unsigned packages are 4,745,418/4,521,412 bytes.

No hardware operation occurred. Live MSPI/NOR reads, filesystem reads,
concurrency, diagnostics, and cold-boot evidence is blocked by unavailable
authorized physical evidence. Apple closes exactly at the protected
`0x00438000` boundary, so later source leaves require authenticated reclaimed
body space. The successor entry at `0x00421310` remains the software frontier;
firmware-wide functional completeness is not claimed. See
`docs/research/g2-bootloader-littlefs-read-4212d8-421310-source-closure.md`.

## LittleFS block-program closure through 0x00421348

The complete authenticated 56-byte callback computes the fixed-partition
address, calls the source-owned MX25U25643G program service, returns zero on
success, and logs block, offset, size, address, and status before collapsing
every failure to `LFS_ERR_IO` (`-5`). The configuration pointer at
`0x00431078` remains the Thumb stock entry, now redirected to source.

Apple/Linux emit 60-byte fixed-address leaves at
`[0x00421214,0x00421250)` with strict relocations to the source-owned program
driver and logger. The builder authenticates the containing initializer body,
its generated NOP tail, cave placement, and cave digest before installation.
Canonical accounting is 15,285 source-owned, 16,392 generated patch, 16
alignment, and 132,147 retained official bytes across 199 routed functions,
179 relocated leaves, one fixed cave, and 197 patch sites.

No hardware operation occurred. Live MSPI/NOR programming, filesystem writes,
persistence, power-loss, diagnostics, and cold-boot evidence is blocked by
unavailable authorized physical evidence. The successor erase entry at
`0x00421348` remains the software frontier; firmware-wide functional
completeness is not claimed. See
`docs/research/g2-bootloader-littlefs-program-421310-421348-source-closure.md`.

## LittleFS block-erase closure through 0x00421372

The complete authenticated 42-byte callback computes the fixed-partition
sector address, calls the source-owned MX25U25643G erase service, and logs the
block/address/status tuple before mapping failure to `LFS_ERR_IO`. Apple/Linux
emit 48-byte fixed-address leaves at `[0x00421250,0x00421280)` with strict
source-to-source relocations. It is a second authenticated cave in the
initializer replacement tail.

Canonical accounting is 15,333 source-owned, 16,386 generated patch, 16
alignment, and 132,105 retained official bytes across 200 routed functions,
179 relocated leaves, two fixed caves, and 198 patch sites. No hardware
operation occurred. The sync entry at `0x004213D4` remains the software
frontier; live erase and persistence evidence is blocked. See
`docs/research/g2-bootloader-littlefs-erase-421348-421372-source-closure.md`.

## LittleFS sync and address-index closure through 0x004213E6

The constant-success sync callback now redirects to the four-byte compiled C
leaf at `[0x00421280,0x00421284)`, the third authenticated initializer cave.
The two adjacent address-index helpers compile directly at
`[0x004213D8,0x004213E6)` and reproduce their complete stock bodies exactly.

Canonical accounting is 15,351 source-owned, 16,386 generated patch, 16
alignment, and 132,087 retained official bytes; 112 bytes are authenticated
caves and 14 are exact in-place leaves. No hardware operation occurred. The
next retained executable body begins at `0x004213E6`; physical filesystem and
flash qualification remains blocked. See
`docs/research/g2-bootloader-littlefs-sync-4213d4-4213d8-source-closure.md` and
`docs/research/g2-bootloader-address-map-4213d8-4213e6-source-closure.md`.

## Mapped-memory selector closure through 0x00421584

`runtime_memory_select_copy_4213e6.c` implements the complete authenticated
mapped-memory selector/copy service and odd-selector wrapper. The primary
entry routes into a 220-byte cave and the wrapper into a 30-byte cave, both
inside authenticated generated NOP space in the primary stock replacement.
Strict relocations bind only to the exact in-place identity/threshold helpers,
the retained authenticated copy provider, and the sibling source cave.

The implementation preserves the six selector kinds, four mapped-memory
roots, compact/full capacity choices, security gate, wrapped bounds check,
status codes, exact copy length, and wrapper filter. Canonical accounting is
15,601 source-owned, 16,528 generated patch, 16 alignment, and 131,695 retained
official bytes. The 22-byte literal/alignment pool through `0x00421584` remains
authenticated retained data. No hardware operation occurred; physical
qualification remains blocked and firmware-wide completeness is not claimed.
See `docs/research/g2-bootloader-memory-select-copy-4213e6-421584-source-closure.md`.

## Population-count closure through 0x004215AE

`runtime_popcount_421584.c` implements the complete authenticated 32-bit
population-count helper at `[0x00421584,0x004215AE)`. Apple clang 21 and
Homebrew clang 22.1.8 reproduce the same 42-byte, zero-relocation stock body
at its exact address. Host tests cover boundary patterns and deterministic
random values; the sole direct caller at `0x0042161C` is pinned.

Canonical accounting is 15,643 source-owned, 16,528 generated patch, 16
alignment, and 131,653 retained official bytes. No hardware operation
occurred. The next retained executable body begins at `0x004215AE`; firmware-
wide completeness is not claimed. See
`docs/research/g2-bootloader-popcount-421584-4215ae-source-closure.md`.

## Two-word bitmap-helper closure through 0x00421632

`runtime_bitmap_helpers_4215ae.c` implements the complete authenticated
nonempty, membership, and population-count helpers over the two-word table
rooted at `0x20026E74`. Apple clang 21 and Homebrew clang 22.1.8 reproduce all
132 installed stock bytes at their exact addresses. The count leaf has one
strict call to the exact source-owned population-count helper; the other two
leaves have no relocations. Host tests cover selector narrowing, both words,
boundary bits, nonempty results, and combined count.

Canonical accounting is 15,775 source-owned, 16,528 generated patch, 16
alignment, and 131,521 retained official bytes. No hardware operation
occurred. The next retained executable body begins at `0x00421632`; live
table ownership and concurrency evidence is unavailable and firmware-wide
completeness is not claimed. See
`docs/research/g2-bootloader-bitmap-helpers-4215ae-421632-source-closure.md`.

## Validated bitmap-update closure through 0x004216B2

`runtime_bitmap_update_421632.c` implements the complete authenticated
read-modify-write helper over the table at `0x20026E74`. It preserves the
low-byte selector/bit/enable behavior, selector and bit bounds, status 6
validation failure, two-word addressing, and set/clear semantics. Apple clang
21 and Homebrew clang 22.1.8 reproduce the same 128-byte, zero-executable-
relocation stock body at its exact address.

Canonical accounting is 15,903 source-owned, 16,528 generated patch, 16
alignment, and 131,393 retained official bytes. No hardware operation
occurred. The next retained executable body begins at `0x004216B2`; live table
ownership, concurrency and atomicity evidence is unavailable and firmware-wide
completeness is not claimed. See
`docs/research/g2-bootloader-bitmap-update-421632-4216b2-source-closure.md`.

## Bounded poll-delay closure through 0x004216D4

`runtime_poll_delay_4216b2.c` implements the complete authenticated volatile
flag/counter polling loop. It preserves both short circuits, duration 10,
delay-before-decrement ordering, and the current-iteration decrement after an
asynchronous flag clear. Apple clang 21 and Homebrew clang 22.1.8 reproduce
the same 34-byte installed body with one strict call to `0x0041D1C0`.

Canonical accounting is 15,937 source-owned, 16,528 generated patch, 16
alignment, and 131,359 retained official bytes. No hardware operation
occurred. The next retained executable body begins at `0x004216D4`; live
timing and memory-visibility evidence is unavailable and firmware-wide
completeness is not claimed. See
`docs/research/g2-bootloader-poll-delay-4216b2-4216d4-source-closure.md`.

## Mode/configuration-service closure through 0x004217D2

`runtime_mode_service_4216d4.c` implements the complete authenticated
validation, optional query/default merge, critical section, bitmap-state
policy, apply/disable fallback, state clearing, configuration copy and
publication transaction. Apple clang 21 and Homebrew clang 22.1.8 reproduce
the same 254-byte installed body with eight reviewed call relocations.

Canonical accounting is 16,191 source-owned, 16,528 generated patch, 16
alignment, and 131,105 retained official bytes. No hardware operation
occurred. The next retained executable body begins at `0x004217D2`; live
interrupt, register and physical mode evidence is unavailable and firmware-
wide completeness is not claimed. See
`docs/research/g2-bootloader-mode-service-4216d4-4217d2-source-closure.md`.

## Dual-mode transaction closure through 0x00421978

`runtime_dual_mode_service_4217d2.c` implements the complete authenticated
dual-controller transaction at `[0x004217D2,0x00421978)`. Apple clang 21 and
Homebrew clang 22.1.8 reproduce the same 422 installed bytes. Sixteen strict
relocations bind query, critical-save, source-owned bitmap count and copy,
mode-zero/mode-one enable and disable, and commit providers. Host tests cover
validation, both controller paths, early failures, busy-state policy,
successful commit/cleanup, and failure cleanup.

Canonical accounting is 16,613 source-owned, 16,528 generated patch, 16
alignment, and 130,683 retained official bytes. No hardware operation
occurred. The next retained executable body begins at `0x00421978`; physical
interrupt, controller/register, state and mode qualification remains blocked
and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-dual-mode-service-4217d2-421978-source-closure.md`.

## Bitmap-client service closure through 0x00421B08

`runtime_bitmap_clients_421978.c` implements the authenticated controller-
selected configuration publisher and four idempotent row-zero/row-one bitmap
mutation helpers at `[0x00421978,0x00421B08)`. Apple clang 21 and Homebrew
clang 22.1.8 reproduce all 400 installed bytes. Sixteen strict relocations
bind query, critical-save, source-owned bitmap count/test/update and copy.

Canonical accounting is 17,013 source-owned, 16,528 generated patch, 16
alignment, and 130,283 retained official bytes. No hardware operation
occurred. The next retained executable body begins at `0x00421B08`; physical
interrupt, controller/register, bitmap/state and client qualification remains
blocked and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-bitmap-clients-421978-421b08-source-closure.md`.

## Mode-one service closure through 0x00421BD2

`runtime_mode1_services_421b08.c` implements authenticated mode-one enable,
last-client disable and poll/state cleanup at `[0x00421B08,0x00421BD2)`.
Apple clang 21 and Homebrew clang 22.1.8 reproduce all 202 installed bytes;
11 strict relocations bind source-owned bitmap/poll helpers, critical-save and
retained control.

Canonical accounting is 17,215 source-owned, 16,528 generated patch, 16
alignment, and 130,081 retained official bytes. No hardware operation
occurred. The next retained executable body begins at `0x00421BD2`; physical
interrupt, control/register, bitmap/state and mode qualification remains
blocked and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-mode1-services-421b08-421bd2-source-closure.md`.

## Mode-zero enable closure through 0x00421CCE

`runtime_mode0_enable_421bd2.c` implements the authenticated controller-
guarded row-two client activation, state compatibility policy, control,
publication and bounded cleanup transaction at `[0x00421BD2,0x00421CCE)`.
Apple clang 21 and Homebrew clang 22.1.8 reproduce all 252 installed bytes;
nine strict relocations bind source-owned bitmap/cleanup helpers,
critical-save and retained state-query/control providers.

Canonical accounting is 17,467 source-owned, 16,528 generated patch, 16
alignment, and 129,829 retained official bytes. No hardware operation
occurred. The next retained executable body begins at `0x00421CCE`; physical
interrupt, controller/register, bitmap/state, polling and mode qualification
remains blocked and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-mode0-enable-421bd2-421cce-source-closure.md`.

## Mode-zero disable and cleanup closure through 0x00421D5E

`runtime_mode0_disable_421cce.c` implements authenticated idempotent row-two
client disable, last-client control/state clearing, and active poll/completion
cleanup at `[0x00421CCE,0x00421D5E)`. Apple clang 21 and Homebrew clang 22.1.8
reproduce all 144 installed bytes; seven strict relocations bind source-owned
bitmap/poll helpers, critical-save and retained control.

Canonical accounting is 17,611 source-owned, 16,528 generated patch, 16
alignment, and 129,685 retained official bytes. No hardware operation
occurred. The next retained executable body begins at `0x00421D5E`; physical
interrupt, controller/register, bitmap/state, polling and mode qualification
remains blocked and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-mode0-disable-421cce-421d5e-source-closure.md`.

## Row-four enable closure through 0x00421E4A

`runtime_row4_enable_421d5e.c` implements the authenticated row-four client
activation, timeout refresh, readiness, first-client switch/configuration,
rollback, publication and cleanup transaction at `[0x00421D5E,0x00421E4A)`.
Apple clang 21 and Homebrew clang 22.1.8 reproduce all 236 installed bytes;
ten strict relocations bind source-owned bitmap/cleanup helpers, critical-save
and retained switch/apply providers.

Canonical accounting is 17,847 source-owned, 16,528 generated patch, 16
alignment, and 129,449 retained official bytes. No hardware operation
occurred. The next retained executable body begins at `0x00421E4A`; physical
interrupt, switch/apply, bitmap/state, polling and mode qualification remains
blocked and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-row4-enable-421d5e-421e4a-source-closure.md`.

## Row-four disable and cleanup closure through 0x00421EBA

`runtime_row4_disable_421e4a.c` implements authenticated idempotent row-four
client disable, last-client switch-off and active poll/state cleanup at
`[0x00421E4A,0x00421EBA)`. Apple clang 21 and Homebrew clang 22.1.8 reproduce
all 112 installed bytes; seven strict relocations bind source-owned bitmap/
poll helpers, critical-save and retained switch.

Canonical accounting is 17,959 source-owned, 16,528 generated patch, 16
alignment, and 129,337 retained official bytes. No hardware operation
occurred. The next retained executable body begins at `0x00421EBA`; physical
interrupt, switch, bitmap/state, polling and mode qualification remains
blocked and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-row4-disable-421e4a-421eba-source-closure.md`.

## Row-five client-service closure through 0x004220B2

`runtime_row5_services_421eba.c` implements authenticated row-five client
enable/disable, timeout publication, selector-mode coordination, retained dual
switch/commit rollback and last-client state cleanup at
`[0x00421EBA,0x004220B2)`. Apple clang 21 and Homebrew clang 22.1.8 reproduce
all 504 installed bytes; 26 strict relocations bind source-owned bitmap,
critical, selector and cleanup helpers plus retained dual providers.

Canonical accounting is 18,463 source-owned, 16,528 generated patch, 16
alignment, and 128,833 retained official bytes. No hardware operation
occurred. The next retained executable body begins at `0x004220B2`; physical
interrupt, retained-provider, bitmap/state, selector-mode and timing
qualification remains blocked and firmware-wide completeness is not claimed.
See `docs/research/g2-bootloader-row5-services-421eba-4220b2-source-closure.md`.

## Row-six and mode-dispatch closure through 0x004222D2

`runtime_row6_services_4220b2.c` implements authenticated row-six client
enable/disable, retained handle lifecycle and mode-family dispatch. Apple
clang 21 and Homebrew clang 22.1.8 reproduce all 508 executable bytes at
`[0x004220B2,0x004222D2)`; two intervening 18-byte literal seams remain
separately retained data. Thirty-one strict relocations bind maintained
bitmap, critical, selector and mode-family services plus retained providers.

Canonical accounting is 18,971 source-owned, 16,528 generated patch, 16
alignment, and 128,325 retained official bytes. No hardware operation
occurred. The next executable body begins at `0x004222F0` after authenticated
padding/literals; physical interrupt, retained-provider, bitmap/state,
selector-mode and timing qualification remains blocked and firmware-wide
completeness is not claimed. See
`docs/research/g2-bootloader-row6-services-4220b2-4222d2-source-closure.md`.

## Mode-routing and cleanup closure through 0x00422430

`runtime_mode_routes_4222f0.c` implements authenticated seven-kind enable and
disable routing, selective seven-row client cleanup, and fixed 20-byte
configuration copy. Apple clang 21 and Homebrew clang 22.1.8 reproduce all 320
executable bytes at `[0x004222F0,0x00422430)`; the adjacent 30-byte and 56-byte
padding/literal pools remain separately retained data. Seventeen strict
relocations bind maintained row services and bitmap query plus the reviewed
disable-route alias and retained memcpy provider.

Canonical accounting is 19,291 source-owned, 16,528 generated patch, 16
alignment, and 128,005 retained official bytes. No hardware operation
occurred. The next executable body begins at `0x00422468`; physical bitmap,
service, concurrency and configuration-persistence qualification remains
blocked and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-mode-routes-4222f0-422430-source-closure.md`.

## Ambiq debug-service closure through 0x00422574

`runtime_debug_services_422468.c` implements the authenticated general debug
shutdown, debug-domain power ownership and trace-disable bodies from the
public AmbiqSuite SDK 5.1.0 behavior. Apple clang 21 and Homebrew clang 22.1.8
reproduce all 268 executable bytes at `[0x00422468,0x00422574)`; adjacent
literal pools remain separately retained data. Nine strict relocations bind
critical state, retained power-domain services, register polling and reviewed
same-cluster aliases.

Canonical accounting is 19,559 source-owned, 16,528 generated patch, 16
alignment, and 127,737 retained official bytes. No hardware operation
occurred. The next executable body begins at `0x00422590`; physical debug
power, MCUCTRL/DCB, trace and timing qualification remains blocked and
firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-debug-services-422468-422574-source-closure.md`.
## Constraint-dispatch and memchr closure through 0x00422628

`runtime_constraint_memchr_422590.c` implements the authenticated constraint
dispatcher and optimized `memchr`. Apple clang 21 and Homebrew clang 22.1.8
reproduce the exact 28- and 88-byte bodies at
`[0x00422590,0x00422628)`; the intervening 36-byte handler/message pool remains
separately retained official data. One strict relocation binds the retained
default constraint handler.

Canonical accounting is 19,675 source-owned, 16,528 generated patch, 16
alignment, and 127,621 retained official bytes. No hardware operation
occurred. The next executable body begins at `0x00422628`; physical
handler-cell, retained-handler and memory/fault qualification remains blocked
and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-constraint-memchr-422590-422628-source-closure.md`.
## Double-runtime closure through 0x00422872

`runtime_double_helpers_422628.c` implements thirteen authenticated
IAR-compatible binary64 helpers. Apple clang 21 and Homebrew clang 22.1.8
reproduce all 584 executable bytes at `[0x00422628,0x00422872)`; the internal
two-byte alignment remains separately retained data. Three strict relocations
bind two wrapper/core edges and the retained range-error tail.

Canonical accounting is 20,259 source-owned, 16,528 generated patch, 16
alignment, and 127,037 retained official bytes. No hardware operation
occurred. The next executable body begins at `0x00422874`; physical VFP,
exception-state and ABI qualification remains blocked and firmware-wide
completeness is not claimed. See
`docs/research/g2-bootloader-double-helpers-422628-422872-source-closure.md`.
## Thread-pointer closure through 0x0042287C

`runtime_thread_pointer_422874.c` implements the authenticated eight-byte IAR
thread-pointer body and its `0x20000518` anchor literal. Both reviewed
compilers reproduce the complete leaf exactly without relocation. Canonical
accounting is 20,267 source-owned, 16,528 generated patch, 16 alignment, and
127,029 retained official bytes. No hardware operation occurred. The next
executable body begins at `0x0042287C`; physical anchor qualification remains
blocked and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-thread-pointer-422874-42287c-source-closure.md`.
## Unsigned 64-bit divmod closure through 0x00422AAC

`runtime_u64_divmod_42287c.c` implements the complete authenticated 560-byte
IAR-compatible quotient/remainder runtime. Both reviewed compilers reproduce
the body exactly; one strict jump binds the retained divide-by-zero handler.
Canonical accounting is 20,827 source-owned, 16,528 generated patch, 16
alignment, and 126,469 retained official bytes. No hardware operation
occurred. The next executable body begins at `0x00422AAC`; physical trap and
register-ABI qualification remains blocked and firmware-wide completeness is
not claimed. See
`docs/research/g2-bootloader-u64-divmod-42287c-422aac-source-closure.md`.
## Atomic snapshot and wrappers closure through 0x00422AD2

`runtime_atomic_wrappers_422aac.c` implements the authenticated three-sample
interrupt-atomic snapshot, no-op and retained-query wrapper. Both reviewed
compilers reproduce all 38 bytes exactly; one strict call binds the retained
query provider. Canonical accounting is 20,865 source-owned, 16,528 generated
patch, 16 alignment, and 126,431 retained official bytes. No hardware
operation occurred. The next executable body begins at `0x00422AD4`; physical
interrupt/volatile/provider qualification remains blocked and firmware-wide
completeness is not claimed. See
`docs/research/g2-bootloader-atomic-wrappers-422aac-422ad2-source-closure.md`.

## Four-instance hardware-service initializer closure through 0x00422BA8

`runtime_hw_instance_init_422ad4.c` implements the complete authenticated
212-byte initializer. Both reviewed compilers reproduce it exactly without
relocation. Its sole caller, three retained pool words, predecessor alignment,
four-slot host behavior and successor are pinned. Canonical accounting is
21,077 source-owned, 16,528 generated patch, 16 alignment, and 126,219 retained
official bytes. No hardware operation occurred. The next executable body
begins at `0x00422BA8`; physical SRAM/pool/concurrency/cold-boot qualification
remains explicitly blocked and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-hw-instance-init-422ad4-422ba8-source-closure.md`.

## Instance register-service closure through 0x00422D20

`runtime_hw_instance_service_422ba8.c` implements the complete authenticated
376-byte service. Both reviewed compilers reproduce it exactly under five
strict calls. Three callers, four MMIO/revision literals, all validation and
action paths, four register banks, clock gating, mode routing and teardown
order are pinned. Canonical accounting is 21,453 source-owned, 16,528 generated
patch, 16 alignment, and 125,843 retained official bytes. No hardware operation
occurred. The next executable body begins at `0x00422D20`; physical MMIO,
clock, mode, resource and lifecycle qualification remains explicitly blocked,
and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-hw-instance-service-422ba8-422d20-source-closure.md`.

## Per-instance register-clear closure through 0x00422D7A

`runtime_hw_register_clear_422d20.c` implements the exact 44- and 46-byte
register-clear leaves. Both reviewed compilers reproduce them without
relocation; all four banks and exact bit preservation are host-tested.
Canonical accounting is 21,543 source-owned, 16,528 generated patch, 16
alignment, and 125,753 retained official bytes. No hardware operation occurred.
A four-byte datum remains retained before the next executable body at
`0x00422D7E`; physical MMIO/bank/peripheral qualification remains explicitly
blocked and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-hw-register-clear-422d20-422d7a-source-closure.md`.

## Per-instance status-map closure through 0x00422DC6

`runtime_hw_status_map_422d7e.c` implements the authenticated 72-byte status
mapper. Both reviewed compilers reproduce it exactly without relocation. Its
six retained result literals, preceding datum, successor, four-bank host model,
bit priority and fallback behavior are pinned. Canonical accounting is 21,615
source-owned, 16,528 generated patch, 16 alignment, and 125,681 retained
official bytes. No hardware operation occurred. The next executable body
begins at `0x00422DC6`; physical MMIO/status/bank/timing qualification remains
explicitly blocked and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-hw-status-map-422d7e-422dc6-source-closure.md`.

## Dual-descriptor initializer closure through 0x00422E28

`runtime_hw_descriptor_init_422dc6.c` implements the authenticated 98-byte
guarded initializer. Both reviewed compilers reproduce it exactly under two
strict calls to the retained 24-byte descriptor constructor. Its caller,
signature literal, provider, successor, validation, pair gating, publication
flags, descriptor contents and order are pinned. Canonical accounting is
21,713 source-owned, 16,528 generated patch, 16 alignment, and 125,583 retained
official bytes. No hardware operation occurred. The next executable body
begins at `0x00422E28`; physical descriptor/DMA/buffer/timing qualification
remains explicitly blocked and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-hw-descriptor-init-422dc6-422e28-source-closure.md`.

## Per-instance clock-divider closure through 0x00422EE2

`runtime_hw_clock_divider_422e28.c` implements the authenticated 186-byte
service. Both reviewed compilers reproduce it exactly under one strict call to
the source-owned divmod runtime. Its caller, reference/status pools, successor,
six mode mappings, invalid/range paths, divider registers and achieved-rate
calculation are pinned. Canonical accounting is 21,899 source-owned, 16,528
generated patch, 16 alignment, and 125,397 retained official bytes. No
hardware operation occurred. The next executable body begins at `0x00422EE2`;
physical clock/MMIO/rate qualification remains explicitly blocked and firmware-
wide completeness is not claimed. See
`docs/research/g2-bootloader-hw-clock-divider-422e28-422ee2-source-closure.md`.

## Per-instance configuration-latch closure through 0x00422F4C

`runtime_hw_config_latch_422ee2.c` implements the authenticated 106-byte
interrupt-atomic service. Both reviewed compilers reproduce it exactly under
one strict retained critical-section call. Its caller, busy-status pool,
provider, successor, exact payload copy, duplicate rejection and `PRIMASK`
restoration are pinned. Canonical accounting is 22,005 source-owned, 16,528
generated patch, 16 alignment, and 125,291 retained official bytes. No
hardware operation occurred. The next executable body begins at `0x00422F4C`;
physical interrupt/concurrency/SRAM/MMIO qualification remains explicitly
blocked and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-hw-config-latch-422ee2-422f4c-source-closure.md`.

## Secondary configuration-latch closure through 0x00422FA2

`runtime_hw_config_latch_secondary_422f4c.c` implements the authenticated
86-byte interrupt-atomic service. Both reviewed compilers reproduce it exactly
under one strict retained critical-section call. Its caller, busy-status pool,
provider, successor, exact payload copy, duplicate rejection and `PRIMASK`
restoration are pinned. Canonical accounting is 22,091 source-owned, 16,528
generated patch, 16 alignment, and 125,205 retained official bytes. No
hardware operation occurred. The next executable body begins at `0x00422FA2`;
physical interrupt/concurrency/SRAM/MMIO qualification remains explicitly
blocked and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-hw-config-latch-secondary-422f4c-422fa2-source-closure.md`.

## Secondary configuration-release closure through 0x00422FDE

`runtime_hw_config_release_secondary_422fa2.c` implements the authenticated
60-byte interrupt-atomic reset. Both reviewed compilers reproduce it exactly
under strict retained critical-section and memset calls. Its caller, providers,
successor, state gate, exact reset span and `PRIMASK` restoration are pinned.
Canonical accounting is 22,151 source-owned, 16,528 generated patch, 16
alignment, and 125,145 retained official bytes. No hardware operation occurred.
The next executable body begins at `0x00422FDE`; physical interrupt,
concurrency, SRAM/MMIO and provider qualification remains explicitly blocked
and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-hw-config-release-secondary-422fa2-422fde-source-closure.md`.

## Per-instance hardware-shutdown closure through 0x0042308E

`runtime_hw_shutdown_422fde.c` implements the authenticated 176-byte register-
quiesce and shutdown service. Both reviewed compilers reproduce it exactly
under four strict calls. Its caller, literals, providers, successor, all four
banks, masks, delay, conditional clear, provider order and restore policy are
pinned. Canonical accounting is 22,327 source-owned, 16,528 generated patch,
16 alignment, and 124,969 retained official bytes. No hardware operation
occurred. The next executable body begins at `0x0042308E`; physical
MMIO/clock/delay/concurrency/provider qualification remains explicitly blocked
and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-hw-shutdown-422fde-42308e-source-closure.md`.

## Per-instance FIFO closure at 0x004232C8 through 0x00423350

`runtime_hw_fifo_4232c8.c` and `runtime_hw_fifo_drain_423342.c` implement the
authenticated 70-byte read, 52-byte write and 14-byte drain bodies. Both
reviewed compilers reproduce them exactly; the wrapper has one strict call to
the source-owned reader. Bodies, bank literal, successor, polling, counts,
error/empty/partial behavior and drain arguments are pinned. Canonical
accounting is 22,463 source-owned, 16,528 generated patch, 16 alignment, and
124,833 retained official bytes. No hardware operation occurred. The earliest
retained executable body remains `0x0042308E`; physical FIFO/MMIO/concurrency
qualification remains explicitly blocked and firmware-wide completeness is not
claimed. See `docs/research/g2-bootloader-hw-fifo-4232c8-423350-source-closure.md`.

## Critical-section FIFO adapters at 0x00423350 through 0x004233E0

`runtime_hw_fifo_adapters_423350.c` implements the authenticated 64-byte FIFO
snapshot and 80-byte FIFO pump bodies. Both reviewed compilers reproduce them
exactly under six strict calls. Bodies, status literal, successor data, FIFO
and descriptor interactions, termination behavior, bank selection and saved
interrupt-token restoration are pinned. Canonical accounting is 22,607 source-
owned, 16,528 generated patch, 16 alignment, and 124,689 retained official
bytes. No hardware operation occurred. The earliest retained executable body
remains `0x0042308E`; physical FIFO/MMIO/descriptor/interrupt/concurrency
qualification remains explicitly blocked and firmware-wide completeness is not
claimed. See `docs/research/g2-bootloader-hw-fifo-adapters-423350-4233e0-source-closure.md`.

## Per-instance mode-dispatch closure through 0x00423524

`runtime_hw_mode_dispatch_4233e8.c` and `runtime_hw_mode_wait_423444.c`
implement all five executable bodies in the authenticated mode-dispatch cluster,
296 bytes total. Both reviewed compilers reproduce them exactly under 14 strict
calls. Type validation, all routes, independent latches, status clearing,
progress gating, timeout policy, active-byte clearing and delays are pinned.
Canonical accounting is 22,903 source-owned, 16,528 generated patch, 16
alignment, and 124,393 retained official bytes. No hardware operation occurred.
The earliest retained executable body remains `0x0042308E`; physical
MMIO/timer/interrupt/concurrency/peripheral qualification remains explicitly
blocked and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-hw-mode-dispatch-4233e8-423524-source-closure.md`.

## Primary and secondary progress closure through 0x004236CE

`runtime_hw_progress_423524.c` implements the authenticated 228-byte primary
and 198-byte secondary transfer-progress services. Both reviewed compilers
reproduce them exactly under eight strict calls. Descriptor/FIFO selection,
bounded transfer counts, progress publication, exhaustion/completion callbacks,
FIFO pump/snapshot behavior, active-state clearing and `PRIMASK` restoration
are pinned. Canonical accounting is 23,329 source-owned, 16,528 generated
patch, 16 alignment, and 123,967 retained official bytes. No hardware operation
occurred. The earliest retained executable body remains `0x0042308E`; physical
FIFO/descriptor/interrupt/DMA/callback/concurrency/MMIO qualification remains
explicitly blocked and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-hw-progress-423524-4236ce-source-closure.md`.

## Per-instance register-service closure through 0x00423764

`runtime_hw_register_services_4236ce.c` implements three authenticated
relocation-free register services totaling 144 bytes. Both reviewed compilers
reproduce them exactly. Type validation, bank selection, OR/write/query
register offsets, selector handling, and status-two rejection are pinned.
Canonical accounting is 23,473 source-owned, 16,528 generated patch, 16
alignment, and 123,823 retained official bytes. No hardware operation occurred.
The earliest retained executable body remains `0x0042308E`; physical
register/MMIO/concurrency/peripheral qualification remains explicitly blocked
and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-hw-register-services-4236ce-423764-source-closure.md`.

## Per-instance service-dispatch closure through 0x0042382C

`runtime_hw_service_dispatch_42377c.c` implements the authenticated 176-byte
dispatcher. Both reviewed compilers reproduce it exactly under six strict
calls. Type validation, active/inactive routing, register-relative progress,
shutdown/clear paths, callback status/context, cleanup and latch publication
are pinned. Canonical accounting is 23,649 source-owned, 16,528 generated
patch, 16 alignment, and 123,647 retained official bytes. No hardware operation
occurred. The earliest retained executable body remains `0x0042308E`; physical
interrupt/register/callback/concurrency/MMIO qualification remains explicitly
blocked and firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-hw-service-dispatch-42377c-42382c-source-closure.md`.

## Bounded memory-exchange closure through 0x00423928

`runtime_memory_exchange_423864.c` implements the authenticated 86-byte
two-buffer exchange and 110-byte three-buffer rotation. Both reviewed
compilers reproduce them exactly under seven strict calls to the authenticated
copy primitive. Zero, direct-byte, threshold, 128-byte and multi-chunk behavior
are pinned. Canonical accounting is 23,845 source-owned, 16,528 generated
patch, 16 alignment, and 123,451 retained official bytes. No hardware operation
occurred. The earliest retained executable body remains `0x0042308E`; the next
sequential executable frontier is `0x00423928`. Firmware-wide completeness is
not claimed. See
`docs/research/g2-bootloader-memory-exchange-423864-423928-source-closure.md`.

## Rotate-to-front closure through 0x00423972

`runtime_memory_rotate_front_423928.c` implements the authenticated 74-byte
bounded rotate-to-front helper. Both reviewed compilers reproduce it exactly
under two strict copy calls and one overlap-safe move call. Zero, first-element,
threshold and multi-chunk behavior are pinned. Canonical accounting is 23,919
source-owned, 16,528 generated patch, 16 alignment, and 123,377 retained
official bytes. No hardware operation occurred. The earliest retained
executable body remains `0x0042308E`; the next sequential executable frontier
is `0x00423972`. Firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-memory-rotate-front-423928-423972-source-closure.md`.

## Three-element comparator/exchange closure through 0x004239C2

`runtime_memory_sort3_423972.c` implements the exact 80-byte three-comparison
sorting network. Both reviewed compilers reproduce it, and all permutations,
duplicates, comparison order, and target compilation are pinned. Canonical
accounting is 23,999 source-owned and 123,297 retained official bytes. No
hardware operation occurred. The sequential frontier is `0x004239C2` and
firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-memory-sort3-423972-4239c2-source-closure.md`.

## Floyd max-heap sift closure through 0x00423A48

`runtime_memory_heap_sift_4239c2.c` implements the exact 134-byte Floyd
max-heap sift helper under two strict calls to the source-owned exchange
primitive. Both reviewed compilers reproduce it exactly; exclusive count,
child selection, descent, upward repair, subtree isolation, no-op behavior and
comparator order are pinned. Canonical accounting is 24,133 source-owned and
123,163 retained official bytes across 291 functions and 88 exact in-place
leaves. The byte-identical package remains unchanged; the 4,648,863-byte flash
plan has 6,679 placed and zero unresolved regions. No hardware operation
occurred. The sequential frontier is `0x00423A48`; firmware-wide completeness
is not claimed. See
`docs/research/g2-bootloader-memory-heap-sift-4239c2-423a48-source-closure.md`.

## Introspective qsort closure through 0x00423D20

`runtime_memory_qsort_423a48.c` implements the exact 704-byte introspective
sort core and 24-byte public wrapper. Both reviewed compilers reproduce all
728 bytes under 17 strict helper relocations and one authenticated fixed call.
Whole-record sorting, duplicates, null/no-op behavior, randomized arrays, the
33-element threshold and target compilation are pinned. Canonical accounting
is 24,861 source-owned and 122,435 retained official bytes across 293 functions
and 90 exact in-place leaves. The byte-identical package remains unchanged;
the 4,650,270-byte flash plan has 6,681 placed and zero unresolved regions. No
hardware operation occurred. The sequential frontier is `0x00423D20`;
firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-memory-qsort-423a48-423d20-source-closure.md`.

## Global hardware-control closure through 0x00423E0C

`runtime_hw_control_services_423d20.c` implements six exact bodies totaling
228 bytes. Both reviewed compilers reproduce them under seven strict provider
calls and four fixed sibling calls. Register arguments, initialization status,
delay, control-bit clearing, debug normalization, countdown/latch behavior and
PRIMASK restoration are host-pinned. Canonical accounting is 25,089
source-owned and 122,207 retained official bytes across 299 functions and 96
exact in-place leaves. The byte-identical package remains unchanged; the
4,656,017-byte flash plan has 6,689 placed and zero unresolved regions. No
hardware operation occurred. Live qualification is explicitly blocked by
unavailable authorized responsive hardware. The sequential executable frontier
is `0x00423E14`; firmware-wide completeness is not claimed. See
`docs/research/g2-bootloader-hw-control-services-423d20-423e0c-source-closure.md`.

## Hardware-control state mapper through 0x00423E40

`runtime_hw_control_state_423e14.c` implements the exact 44-byte body at
`[0x00423E14,0x00423E40)`. Both reviewed compilers reproduce the relocation-free
body, and five host tests pin every state/flag path plus the authenticated
successor. Canonical accounting is 25,133 source-owned and 122,163 retained
official bytes across 300 functions and 97 exact in-place leaves. The
byte-identical package remains unchanged; the 4,657,431-byte flash plan has
6,691 placed and zero unresolved regions. No hardware operation occurred.
Live qualification is explicitly blocked by unavailable authorized responsive
hardware. The sequential executable frontier is `0x00423E40`; firmware-wide
completeness is not claimed. See
`docs/research/g2-bootloader-hw-control-state-423e14-423e40-source-closure.md`.

## MSPI FIFO, command-queue, and DMA-programming closure through 0x004240AA

Eight exact target bodies totaling 618 bytes cover FIFO write/read,
command-queue init/term/enable/disable/pause, and high-priority DMA programming
at `[0x00423E40,0x004240AA)`. Both reviewed compilers match stock after ten
typed call relocations. Host tests cover all software-visible validation,
timeout, partial-word, handle, clock, queue-index, DMA-register-order, and
provider-status paths. Canonical accounting is 25,751 source-owned and 121,545
retained official bytes across 308 functions and 105 exact in-place leaves. The
provider and unsigned package remain byte-identical; the 4,663,145-byte flash
plan has SHA-256
`910dc1ab8c79edd6d7a06ced0f54d7ae0f395e6c9262f5de50f30893831d6e53`
with 6,699 placed and zero unresolved regions. No hardware operation occurred.
Physical qualification is explicitly blocked by unavailable authorized
responsive G2 evidence. The sequential frontier is `0x004240AA`; firmware-wide
completeness is not claimed.

## Post-MSPI interrupt and power closure through 0x00426BFE

The exact AmbiqSuite 5.1.0 `am_hal_mspi_interrupt_service` and
`am_hal_mspi_power_control` bodies at `[0x00426536,0x004267FE)` and
`[0x00426808,0x00426BFE)` add 1,726 BSD-3-Clause source-owned bytes. Independent
Apollo-main links preserve the same sizes and all but 20 and 29 address-coupled
bytes respectively. `runtime_mspi_interrupt_power_426536.S` expresses every
executable instruction as a reviewable Thumb-2 mnemonic, with semantic block
comments and no raw instruction-encoding directives. Apple Clang 21 and
Homebrew Clang 22 emit identical sections; strict eight- and twelve-call
provider relocations produce both stock-exact bodies. The intervening 10-byte
pool and following 18-byte pool remain typed official data. Canonical
accounting is 36,721 source-owned
and 110,575 retained official bytes; the 163,840-byte provider remains
byte-identical with SHA-256
`3ae28d27b81ca70d96fd5846d04fa1a4f0add5a8514cee21f9f34bdaa1455eac`.

The complete `[0x00426536,0x00434477)` suffix now has an exhaustive 253-span
function/mixed/data ledger with zero unclassified bytes. Fifty-eight exact
Apollo-main matches totaling 4,550 bytes remain candidates rather than source
claims. The pinned AmbiqSuite upstream commit is
`5efc0228528a8adce5eae0d226fac85d2551eb3b`. Hardware validation is deferred
by project direction; this admission
performed no hardware operation, flashing, signing, packaging, or release.
