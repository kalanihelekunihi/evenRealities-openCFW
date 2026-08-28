# Component source-replacement contract

The reference manifest selects six `official_blob` providers. The
`ring-source` profile selects five official providers plus a source-built
Apollo-main provider. The `core-source` profile selects four official
providers plus source-built Apollo-main and Apollo-bootloader providers. A
component is ready to become a
`source_build` provider only when its build is reproducible and produces the
complete payload expected by the EVENOTA container.

Planned component roots:

| Component | Owner | Current payload contract | Address status |
|---|---|---|---|
| `apollo_main` | Each glasses temple, Apollo510B | 32-byte OTA preamble plus raw Cortex-M55 image | Confirmed; the preceding constructor milestone used a 124,916-byte Apple source overlay at `[0x00794324,0x007B2B18)` and exact-root Linux used 126,742 bytes through `0x007B323A`; the signed-varint increment is documented below |
| `apollo_bootloader` | Each glasses temple, Apollo510B | Raw Cortex-M55 image | Confirmed; unchanged current 662-byte source overlay at `[0x00434478,0x0043470E)` |
| `case` | Charging case, STM32G0 | 32-byte EVEN wrapper plus raw Cortex-M0+ image | Confirmed |
| `touch` | Touch controller | 32-byte FWPK wrapper plus raw Cortex-M image | Vector base inferred |
| `ble_em9305` | Bluetooth controller | Record-table package with explicit record addresses | Confirmed per record |
| `codec` | Audio codec/DSP | Two-segment FWPK package | Community source profile resolves the UART boot stages to GX8002 IRAM and the dual BINH image to codec SPI NOR; payload source remains a proprietary boundary |

A future `components/<name>/` implementation should contain:

- all human-authored source and linker configuration;
- a reviewed compiler release-family/toolchain description;
- a deterministic build entry point;
- tests for its native wrapper and checksum format;
- a generated complete payload at a stable path; and
- hardware validation notes tied to a payload SHA-256.

The `main`, `case`, and `touch` wrapper generators already exist in
`tools/open_cfw.py`. They let future compiler output remain a conventional raw
image while preserving the reviewed vendor staging format.

## Current production TinyFrame G2 source boundary

`components/shared/tinyframe/runtime_tinyframe_g2_adapter_candidate.c/.h`
wraps the exact MIT upstream core in the recovered G2 bookended allocation:
prefix `0xA5A5A5A5`, pristine `0x7158`-byte core at `+4`, and suffix
`0x5A5A5A5A` at `+0x715C`. It isolates allocation, format logging, and the
first-party write port while leaving `TinyFrame.c/.h` immutable. The complete
stock census proves one mode-selected instance at `0x200749C4`: role 1 is
master/peer bit 1 and role 2 is slave/peer bit 0. Host-linked exact-core tests
and Cortex-M55 layout assertions pass. Its companion concrete-port candidate uses the
source-owned `heap_4` allocation boundary and the authenticated retained sync
write wrapper at `0x00541790`; host behavior and exact target relocation pins
pass. The stateless atomic-boundary variant removes writable port state and is
production-routed as one eight-entry set. It pins the exact 14-function live
closure under Apple and Linux Clang while selecting no-op diagnostic logging.
Placement, redirects, and ownership accounting are complete; only hardware
golden-frame validation remains. See
`docs/research/tinyframe-source-admission-boundary-audit.md`.

## Current production-excluded Cordio WSF timer candidate

`components/shared/cordio/runtime_cordio_wsf_timer_candidate.c/.h` records a
clean-room behavioral reconstruction of all eleven functions / 536 code bytes
in the bounded timer translation unit. It uses the recovered stock field order
(`ticks +4`, `msg +8`) and stock `sec*100`/`ms/10` conversions, not the
incompatible public r20.05c layout and extra-tick macros. Host tests close
initialization, callback, sorted queue, start/stop/update/service, lock,
elapsed-tick, and FreeRTOS period-command behavior. The candidate is absent
from every overlay and production manifest. The exact proprietary AmbiqSuite
2.5.1 implementation/source family is pinned without redistributing it; minor
local text/config drift, IAR output, logging/assert integration, placement,
and production relocations remain pending. See
`docs/research/cordio-wsf-timer-source-recovery.md`.

## Current production-excluded Cordio WSF buffer/message candidates

`components/shared/cordio/runtime_cordio_wsf_buf_candidate.c/.h` independently
recreates the three bounded G2 buffer-pool functions / 430 code bytes. It
preserves the 4-byte input descriptor, 8-byte block, 12-byte pool, first-fit
fallback, descending free classification, and `0xFAABD00D` marker behavior.
The proprietary Ambiq source family is pinned only as an oracle and is not
copied.

`runtime_cordio_wsf_msg_candidate.c/.h` covers the adjacent seven-function,
126-byte WSF message layer through the exact Apache-2.0 Packetcraft r19.02
source route. It closes the temporary OS dispatcher dequeue/free seams and
uses the recovered eight-byte hidden message header. Focused host and ARM
compile tests pass; neither candidate is present in a production manifest.
Exact IAR output, the local allocation-warning logger seam, relocation and
placement closure, and target validation remain pending. See
`docs/research/cordio-wsf-buffer-message-source-recovery.md`.

## Current production-excluded Cordio WSF assert/trace candidate

`components/shared/cordio/runtime_cordio_wsf_assert_trace_candidate.c/.h`
recreates the two linked stock functions / 208 code bytes behind narrow
formatter, EasyLogger, hook, and reset seams. It intentionally preserves the
1,024-byte unbounded formatting buffer and double-format debug behavior for
compatibility, and records the downstream hook-null reset path plus debugger
escape loop. Focused host and ARM compile tests pass. The proprietary Ambiq
sources are identity/behavior oracles only; Packetcraft's public bodies are
not exact implementations. The candidate is absent from every production
manifest pending exact local logger/IAR comparison, placement/relocation, and
target validation. See
`docs/research/cordio-wsf-assert-trace-source-recovery.md`.

## Current production-excluded Cordio WSF string-helper candidate

`components/shared/cordio/runtime_cordio_wstr_candidate.c/.h` implements the
two linked reverse helpers / 118 stock bytes through their exact Apache-2.0
Packetcraft definitions. Host and ARM compile tests pass. `WstrnCpy` is not
included because all upstream consumers belong to the absent WDXS family.
The candidate is absent from production manifests pending exact IAR placement,
relocation closure, and target validation. See
`docs/research/cordio-wstr-source-recovery.md`.

An earlier dual-image release appended the relocation-free littlefs
v2.10.1 endian-conversion quartet to both Apollo providers. Its main provider
was
3,637,592 bytes with SHA-256
`0a55496307eee536a60196c7e7bcec3f2d92501418756877e790bac11756573f`;
the bootloader provider was 148,770 bytes with SHA-256
`b2922a93cf19d63a057c473e8937410efe32a8ad9202607972d34dac12e6f19e`.
Their assembled 4,415,594-byte package had SHA-256
`cbfc505c73900cc15c0ccfa7956f6adb27d62a0d60d2d98417ac9a516ccd0c98`.
The release gate passed 55 focused tests, all 248 Apollo-main aggregate tests,
all 1,800 repository tests, standard verification, and three byte-identical
output-isolated reproducibility lanes. Those results remain the historical
endian milestone.

The subsequent fallback-bitops milestone additionally mini-linked the
authenticated
`LFS_NO_INTRINSICS` implementations of littlefs v2.10.1 `lfs_npw2`,
`lfs_ctz`, and `lfs_popc` from the 2,795-byte shared source with SHA-256
`405092c6e8fc65a740f951cb2affaad8766e2553c7b8d290ff58f435e8830f47`.
Its main provider was 3,637,720 bytes with SHA-256
`f0da043e234dc38481059459755e091622d689313cd12e5c8d5155c7b4ba3202`;
the bootloader provider was 148,882 bytes with SHA-256
`1aa7920a16ed2857a2743394c0f62395a2f2477f95c965da47d1e29c4d2d8247`.
Their 4,415,834-byte package had SHA-256
`058782604ab6cb946aff0acedbbef7d367bb1d82114f28c9a70276bcdf178e9a`.
Its focused production gate passed 6/6 tests in 13.693 seconds, and the
inherited focused gate passed 55/55 tests in 39.997 seconds: 61 tests across
the two isolated suites in 53.690 seconds summed. The relocation-repin audit
reviewed 22 shifted compiled-body pins; their boundaries and all 185
relocation records remained unchanged, all 100 differing bytes were
relocation write sites, and all five rodata sections were byte-identical and
shifted by 128 bytes. The canonical repository run passed all 1,806 tests in
1,139.177 seconds; inside that run, all 248 Apollo-main aggregate methods
passed. `./make.sh source` and `./make.sh verify` passed, all three offline
inspection lanes accepted the package, and three output-isolated builds
reproduced both overlays, both providers, the package, and the flash plan
byte-for-byte.

## Preceding Apollo-main FreeRTOS NTZ in-place milestone

That milestone compiled five MIT-licensed
FreeRTOS-Kernel V10.5.1 `ARM_CM55_NTZ/non_secure` port leaves from the
5,487-byte `runtime_freertos_ntz_port.S` adapter, SHA-256
`38c6a259ca2fbfbefb373ef5a80216f2e5f1cad998173ca2b4c9cfde6c01aee8`.
`vRestoreContextOfFirstTask`, `vRaisePrivilege`, `vStartFirstTask`,
`PendSV_Handler`, and `SVC_Handler` source-own 182 bytes at their original
spans from `0x005FA058` through `0x005FA132`, excluding the already
source-owned interrupt-mask pair. Their five exact stock hashes are pinned in
`overlay.json`; the four PC-relative literal loads and two fixed branch seams
are the complete six-relocation allowlist.

`in_place_leaves` are deliberately absent from both the appended overlay
function ABI and `patch_sites`. The builder authenticates the common source,
reviewed Apple Clang 21 flags, stock and expected body pins, exact relocation
records, literal words at `0x005FA134` and `0x005FA138`, nonoverlapping
fixed-address placement, and final byte identity before changing the base
image. Its appended 114,324-byte overlay and 3,637,720-byte provider had
SHA-256 values
`00318de9ff51e19f77d889fa691a3a2a54e035b1287843bda857f944af58e065`
and
`f0da043e234dc38481059459755e091622d689313cd12e5c8d5155c7b4ba3202`.
The component report recorded `source_owned_in_place_bytes=182`,
`source_owned_bytes=114506`, and `opaque_base_bytes=3443066`.

Its byte-identical 4,415,834-byte package had SHA-256
`058782604ab6cb946aff0acedbbef7d367bb1d82114f28c9a70276bcdf178e9a`.
Its 750 placed, two unresolved, and five container-only regions produced
flash-plan SHA-256
`eda45c2cc276bd70bc123267d9fbdc09b0ae4aa030a7557f874c259ca7f5fee8`
and classified 114,820 source bytes (2.600188%), 81,477 generated bytes
(1.845110%), 4,219,537 opaque bytes (95.554702%), and 196,297 controlled
bytes (4.445298%). The focused production gates passed 23/23 tests in 18.333
seconds; the linker and inherited focused gates passed 21/21 in 0.705
seconds. The standard source build and core-source manifest verification
passed.
Three lanes at `build/repro-freertos-ntz-output-{a,b,c}` reproduced the main
and boot overlays/providers, package, and flash plan byte-for-byte; their
temporary manifests were moved to Trash. All 248 Apollo-main tests passed in
582.904 seconds. `./make.sh test` passed all 1,838 tests in 1,038.709 seconds,
including all six CMSIS constructor compile-closure tests.

The authenticated CMSIS-FreeRTOS v10.5.1/CMSIS_5 5.9.0 snapshot remains the
compile-input proof for constructor candidates. Candidate-only shims live at
`components/apollo_main/core_overlay/candidates/cmsis_freertos_constructors/`
as `{FreeRTOSConfig.h,portmacro.h,cmsis_freertos_target.h,string.h}`. They let
the authenticated, unmodified `cmsis_os2.c` compile for Cortex-M55 with
`-Oz -Werror`. Garbage collection retains 370 text bytes (`IRQ_Context` 46,
`osMessageQueueNew` 88, `osMutexNew` 98, `osSemaphoreNew` 138), zero
read-only or writable data, and four 8-byte EHABI `.ARM.exidx` sections.
The isolated candidate gate passes 6/6 tests in 0.231 seconds.

The broad proof remains candidate-only for unrelated CMSIS services. The
bounded `osMessageQueueNew`, `osMutexNew`, and `osSemaphoreNew` algorithms
are production-integrated after separately authenticating their stock
topology, G2 ABI/configuration, IRQ policies, and direct source-owned
dependencies. The semaphore cleanup path now closes through source-owned
`vQueueDelete` and `heap_4`; the authenticated V10.5.1 allocator algorithms
are selected through a bounded G2 adapter. The unresolved device-header, clock, MVE, broad
`INCLUDE_*`, assert/NVIC/libc, and `StaticTask_t` questions remain outside
that leaf. Apache-2.0 wrapper/header notices and the separate FreeRTOS MIT
notice remain in force.

## Prior dual-image littlefs disk-version-parts tranche

That release source-integrated littlefs v2.10.1
`lfs_fs_disk_version_major` and `lfs_fs_disk_version_minor` in both Apollo
images. The common 1,734-byte BSD-3-Clause adapter is
`apollo_main/core_overlay/runtime_littlefs_disk_version_parts.c`, SHA-256
`920d03e80c9d16a1d0b4299f8151eefe4d9f3ac1ba89c2d40bcc5830335eb5a7`,
derived from littlefs commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. Each ten-byte function is
compiled as a separate `relocated_leaves` entry and has exactly one
`R_ARM_THM_CALL` at offset two to the already source-owned
`open_cfw_littlefs_disk_version` provider. The source/toolchain, raw section,
final linked bytes, alignment, placement, exact symbol identity, and ordered
relocation are all pinned.

Apollo main places the major leaf at overlay offset 114,324,
`0x007B01B8`, with SHA-256
`cffc852c2243f51e8a52543b4f2410b192e2365c25f161cfd12f69cae8544122`;
two zero bytes align the minor leaf at offset 114,336, `0x007B01C4`, with
SHA-256
`e0494044bcf077ed5b67a33cf3eb526bb9b8b6f31dcfefb5ce347a197b100012`.
The bootloader places them without padding at offsets 282 and 292,
`0x00434592` and `0x0043459C`, with SHA-256 values
`15251b134de5617995984b9d8140d6fb88dca904ef8ef72e480b99f3c0250b2a`
and
`685d7f3e70053272d9a3920aaf7867d0a84e8adb402bbccd4ef3afc76195b2b7`.
Complete non-linking `B.W` redirects plus NOP fill replace the authenticated
12-byte major and ten-byte minor stock spans in each image; exhaustive
topology gates retain every caller at the original entry.

That main overlay is 114,346 bytes at
`[0x00794324,0x007B01CE)` with SHA-256
`bdc1e353d1adcb0075231afb6c423616dcc0da8335b4b430afe51763a0b9df20`.
Its 3,637,742-byte provider has SHA-256
`d69c4834f65b0661834f990da8167ca6989a1b1c97fda838edc488a4ed0b3e8e`
and leaves 261,682 bytes below the conservative `0x007F0000` MRAM ceiling.
The component accounts for 114,528 source-owned bytes, including 182
fixed-address source bytes; 80,138 generated patch-site bytes; 32 generated
wrapper bytes; and 3,443,044 opaque base bytes. Its authenticated replacement
spans total 80,320 bytes.

That bootloader overlay is 302 bytes at
`[0x00434478,0x004345A6)` with SHA-256
`e94e33658aca89d3830182bc6c17c656256a194262835c041fecc93e1d72dc59`.
Its 148,902-byte provider has SHA-256
`abc583d976a01e237ffa4ed29e4be1b6ff0e5ae2d9756bccec58d1779fe20239`
and leaves 14,938 bytes (`0x3A5A`) before Apollo main. The boot component
accounts for 302 source-owned bytes, 438 generated patch-site bytes, one
generated alignment byte, and 148,161 opaque base bytes.

The complete 4,415,876-byte core-source package has SHA-256
`60cd913a716266b349ce18295064f2484749a7dbad2ab9244c923c927bd56c2f`.
Its 757 placed, two unresolved, and five container-only regions produce a
546,404-byte flash plan with SHA-256
`52124c17205ae10e47f0b02d0cd6bae7c2b30e10d65d787aa34201a53fe0dc68`.
The package classifies 114,860 source bytes (2.601069%), 81,523 generated
bytes (1.846134%), 4,219,493 opaque bytes (95.552796%), and 196,383
controlled bytes (4.447204%).

## Prior dual-image littlefs allocator-lookahead tranche

That release additionally compiled the exact littlefs v2.10.1
`lfs_alloc_lookahead` algorithm from the shared
`apollo_main/core_overlay/runtime_littlefs_alloc_lookahead.c`, SHA-256
`44ab9037747a4cb209404423d52cf817b035cbab5177a8c0cb05090df4b68491`.
Both authenticated stock spans are 56 bytes with SHA-256
`58285c138461a673be0bed2c5376f8d739e40e2aea753ad05d5061bfbc9265cf`.
Focused disassembly supplies the `lfs_t` field offsets `0x54`, `0x58`,
`0x64`, and `0x6C`; the upstream algorithm itself is not decompiled.

Apollo main redirects `0x004CB0F6` to a 50-byte source leaf at
`[0x007B01D0,0x007B0202)`, after two alignment bytes. Its raw SHA-256 is
`ff36aeaff70307ae466d9f7fafacad678c706db1551b18d98d7fe68bf3dc5eef`.
The bootloader redirects `0x00410DFE` to a 48-byte leaf at
`[0x004345A6,0x004345D6)`, SHA-256
`bd8e7c926d98a940f215cd41a2fb5932bfbf1abcf7378839dcadd537ae55324d`.
Both are relocation-free and pass a 20,000-case upstream-oracle comparison.

The main overlay is 114,398 bytes with SHA-256
`2189ec69f7076e216c2ba7388f4eb9d19647feb9f89c382864012902be4e0fdf`;
its 3,637,794-byte provider has SHA-256
`557fe93fdf79c5cb332c7db731db29ed7cfc42be3daa49fb0d022f81e7fe0ba8`.
The boot overlay is 350 bytes with SHA-256
`1b8bb2893a33a18b8481b785a57d49c2849396cc05c5ef20d86f8cf5cef255a5`;
its 148,950-byte provider has SHA-256
`9af8b65041bbd576b49b4f88e2f7427daf7bb445981d608799d86e1987468736`.
The complete 4,415,976-byte package has SHA-256
`3d4b2f3e22a10d0755642c0544786c9a881b2ab7c2271d8a184a83f5d3d7d13f`.
Its 762 placed, two unresolved, and five container-only regions produce a
550,026-byte flash plan with SHA-256
`73978705e32bbb968a9741620a80e1a70f866b5e43db60f4a9f08b4404ce34d1`.
The package classifies 114,958 source bytes (2.603230%), 81,637 generated
bytes (1.848674%), 4,219,381 opaque bytes (95.548096%), and 196,595
controlled bytes (4.451904%).

## Prior Apollo-main CMSIS `osMessageQueueNew` tranche

That release integrated the exact CMSIS-FreeRTOS v10.5.1
`osMessageQueueNew` allocation/validation algorithm from authenticated
commit `d213f261b5be6bb29a7cce8b84071706b72f4d53`. The bounded 8,427-byte
Apache-2.0 source,
`apollo_main/core_overlay/runtime_cmsis_message_queue_new.c`, has SHA-256
`8897019aa7a2beca32a88dc60808fb1f99b1538933b8ab4fbd9ed4fed38d433c`.
Focused disassembly supplies the enabled static/dynamic allocation policy,
disabled queue registry, 80-byte `StaticQueue_t`, 24-byte attribute ABI, and
the exact `IPSR`/`PRIMASK`/`BASEPRI` rejection policy.

The authenticated 140-byte stock span `[0x00449A32,0x00449ABE)` has SHA-256
`52d0abf097914cc84b2cdfe7f628dc61f9efb40bac880112062315d2b1bfba47`;
its 15 callers have ordered digest
`7974f375f4b38120a6df7ce5416cef9fa65031d5768226b8785d2916d0f96f18`.
The complete generated replacement hashes to
`b9e761042539e109acea61b03a522bb5795539850f0751906c6e06d0da198a47`.
Two alignment bytes at `[0x007B0202,0x007B0204)` precede the 124-byte
relocated leaf at `[0x007B0204,0x007B0280)`, SHA-256
`afbba4f9f08b2df17a4350d7a7e83d99b8439283ee40c1a1604bd879dff75f04`.
The raw leaf hashes to
`543fb1ef418aeadd05e2f3b3e60c3f48c0f3521dfa995a3079a86b86ccc58eee`;
its three relocations at `+0x10`, `+0x44`, and `+0x78` bind directly to the
source-owned scheduler-state getter and static/dynamic generic queue creators.

The main overlay is 114,524 bytes with SHA-256
`de76f5db2f04f48c81ea480c348a3c9151d4441c522eba68621ad812290153e2`;
its 3,637,920-byte provider has SHA-256
`874bdc621a6cd91848dee66038c3ba97d7e4b7c7ab1fb5063739bf69fc3047e1`.
The 4,416,102-byte package has SHA-256
`c7baf50cd5386a5e27b4c284cc0084e8cf5d0b83d74eb08b8d4a997bf66474f4`.
Its 766 placed, two unresolved, and five container-only regions produce a
552,937-byte flash plan with SHA-256
`79da631918503c668516e1af5d3844e3dab65c9e63d8add4834a43536ef69407`.
The package classifies 115,082 source bytes (2.605963%), 81,779 generated
bytes (1.851837%), 4,219,241 opaque bytes (95.542200%), and 196,861
controlled bytes (4.457800%).

The focused production gate passes 10/10 tests, offline. At that point,
`osMutexNew` and `osSemaphoreNew` remained candidate-only.

No component may borrow an EVENOTA package offset as a flash address. Unknown
addresses remain unresolved in `build/flash-plan.json`.

The preserved first implementation lives at `apollo_main/ring_gesture/`; the
current progressive implementation lives at `apollo_main/core_overlay/`. Each
`overlay.json` is the ABI and reproducibility contract: exact source and base
hashes, compiler release family and flags, exported functions, stock call-site
bytes, and expected output hashes. Apple Clang patch builds within the reviewed
major release are accepted only when they reproduce those exact output hashes.
`build_component.py` rejects unresolved
relocations outside the supported mini-linker families, unexpected functions,
compiler drift, branch-range errors, exact-copy size mismatches, changed stock
bytes, inconsistent scatter-load record/stream/literal metadata, invalid Apollo
wrapper metadata, and MRAM boundary violations.

`tools/apollo_overlay.py` now supports multiple source files in one translation
unit. It resolves only intra-overlay Thumb calls/jumps and `-fropi`
read-only-data references. Writable sections are forbidden: persistent source
state must first receive an explicit, reviewed RAM ABI allocation.

## Prior Apollo-main FreeRTOS task-name tranche

The subsequent Apollo-main increment additionally source-integrated FreeRTOS
V10.5.1 `pcTaskGetName`. Its complete 34-byte stock entry at
`[0x00454F16,0x00454F38)` redirects to the 38-byte source leaf at
`[0x007B0280,0x007B02A6)`. The leaf's sole relocation binds directly to the
source-owned `ulSetInterruptMask` function. That overlay/provider's pins
are 114,562 bytes/
`188a9b26fce7b7899e3c0eebd698552edc6a453396b9b05107841c63d488e8ee`
and 3,637,958 bytes/
`6830ed33f567b4ac8b4c401612b83b56caa38d107bb9b1fc5d210dce9add9214`.

## Prior Apollo-main CMSIS `osMutexNew` tranche

That increment ports the exact CMSIS-FreeRTOS v10.5.1 `osMutexNew`
algorithm from authenticated commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. The 9,798-byte Apache-2.0
source has SHA-256
`28081734a384c089635681014ed028414b75d375c22f0a52a64f53e22842cf2d`;
the separately reached FreeRTOS V10.5.1 dependencies retain MIT terms.
Recovered G2 configuration pins static/dynamic allocation, recursive mutexes,
disabled queue registry, robust rejection, the recursive-handle low bit, the
80-byte static semaphore control block, the 16-byte 32-bit attribute ABI, and
the exact IRQ-context policy.

The 154-byte stock span `[0x0044971C,0x004497B6)` has SHA-256
`09f88d8a6a64730936a52aa0c2f90d9bcb0152f6e2439919f6409110148999ec`.
Its 30 callers have ordered digest
`14d18197e409351bfa6ded1310c61c1f27246ebd93ecf86452d19ac0bdadbfd0`,
with no alternate, interior, or stored entry. Two alignment bytes at
`[0x007B02A6,0x007B02A8)` precede the 116-byte source leaf at
`[0x007B02A8,0x007B031C)`. Its five relocations bind only to the source-owned
scheduler-state getter and static/dynamic mutex creators.

That release's overlay is 114,680 bytes with SHA-256
`7603cf2a0de6e8b05d66dc356bf3e0701f6157536d29bdac8ad692dc56e0362c`;
the 3,638,076-byte main component hashes to
`f696c6dfbd8ab1f7b5cc44fdc06fcdc5baf44f368ad55130e7571d82ee31ec82`.
The 4,416,258-byte package hashes to
`11d40cd1b3648f96b5ec98c9fa2dff6de121e878978206a0a9694ede38d3a0ff`.
The focused production gate passes 10/10 tests offline; no hardware was
accessed.

At that point `osSemaphoreNew` remained candidate-only pending production
closure of `heap_4`; the following atomic tranche closes that boundary.

## Prior Apollo-main FreeRTOS heap and CMSIS semaphore tranche

That increment source-integrated the four FreeRTOS-Kernel V10.5.1
`heap_4` algorithms, `vQueueDelete`, and CMSIS-FreeRTOS v10.5.1
`osSemaphoreNew`. The 16,885-byte MIT heap adapter preserves the recovered
G2 heap and accounting globals; the 5,851-byte MIT queue-delete adapter
closes cleanup over source heap free; and the 11,566-byte Apache-2.0
semaphore adapter has SHA-256
`a947868d3fbcfc7f41d021210355e0ff777d49d3db84fa0da71a255d319c1527`.

The four stock heap spans at `[0x00456110,0x00456338)`, the 34-byte
`vQueueDelete` span at `[0x00441EA2,0x00441EC4)`, and the 180-byte
`osSemaphoreNew` span at `[0x0044989A,0x0044994E)` are fully redirected.
Six source leaves and eight alignment bytes append
`[0x007B031C,0x007B065A)`. All sixteen relocations resolve to source-owned
heap, interrupt-mask, scheduler, queue, and semaphore dependencies.

The overlay is 115,510 bytes with SHA-256
`6359e4e8c824af3cea36280a1aabd6ad671027e38fb3263fe9ac0cbb292660b4`;
the 3,638,906-byte main component hashes to
`00d112e265f40dd8bf98fc9021bba54b3bcc94f159111b2f4815d5484e91c67c`.
The 4,417,088-byte package hashes to
`064c9429352132cee2a5dfe45c2bf52349e10111b89db91f093b1ce16ed0c2b0`;
its 570,697-byte flash plan hashes to
`8334c9308a7ae7f03d7a2a214cca946063963b1636a9088fe730a15303dd2975`.
The dedicated heap, queue-delete, and semaphore gates pass 13/13, 7/7, and
8/8 tests offline.

## Prior dual-image EasyLogger helper tranche

That increment replaced `get_fmt_enabled`, its unsigned-argument and
pointer-argument predicates, and `elog_strcpy` in both Apollo images. Each
image retires 320 authenticated stock bytes. Shared MIT sources
`runtime_easylogger_helpers.c` and `.h` are 4,975 and 6,505 bytes with
SHA-256 values
`8f2850f789fba3b08bdc3e1fa8f3a4646aaef7e4b16862f3be53478071aa22b5`
and
`f3a7e9bce0f136a2ff4a76929c317aef7bbc7c29dfc60d58311d94e58f6e2393`.
The 7,068-byte MIT seam source hashes to
`78dc5aa9a7eb4f072b3169ae1837855007f25e1adccec7deaefecc486c8f0823`.
It binds the same algorithms to the main logger at `0x20070BE8` and the boot
logger at `0x20026700`, while preserving the distinct hook globals,
diagnostic-output calls, and wait wrappers. Official assertion strings,
`elog_output`, and wait functions remain explicit binary seams. The
algorithms, image selection, and corrected record layout (`level +0`,
`tag +1`, `tag_use_flag +0x20`) are source-owned.

Apollo main appends 390 source bytes plus ten alignment bytes. Its
115,910-byte overlay and 3,639,306-byte component hash to
`e59da6e6753c0c8a9fa73bad8cd555313d0e2ae6ed95006c818e6697e4fbe32d`
and
`00f5f11dd18c13c56137d0f527da3ecd8ae850a9ae35dc96d671a4b998d79b61`.
The bootloader appends 270 source bytes plus two alignment bytes. Its
622-byte overlay and 149,222-byte provider hash to
`fc02cf66854adace4d213e08764e435e27c8c2bc7cc4f7caac6ff286f3adf813`
and
`b4a5b0f2028842a2d6fde9424fff05fac2db3bf0e26e7f01d16a990e67ed9052`.

The complete 4,417,760-byte package hashes to
`fb662322f26e06aa04eb1d3f55f8c8f18606e510fac9c35885de3e4f92864c4d`;
its 592,687-byte flash plan hashes to
`c06c84e277bad2160479e0ec1f7a626abb804574f42ecee0709f0978657cd1b3`
and records 822 placed, two unresolved, five container-only, and six
protected regions.

## Preceding Apollo-main FreeRTOS tick-getter tranche

FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` supplies the MIT
`xTaskGetTickCount` and `xTaskGetTickCountFromISR` algorithms. Its pinned
223,695-byte `tasks.c` hashes to
`14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463`.
The 3,412-byte bounded adapter and 1,186-byte header hash to
`948d1b2de6026adc7cf84a34a359c859c32126b3afcafe92c2347f5f7ab56363`
and
`adc4065b3504a7eacb2e29e2d357636917e2b690afc49b265689e36d66171dae`.

The corrected stock spans are `[0x00454EFE,0x00454F06)` and
`[0x00454F06,0x00454F10)`; `0x00454F08` is an interior ISR instruction.
Their aggregate 18-byte SHA-256 is
`d0b93ff29439d26b92dcd56fd012a9dab842364f7c5f4b4f7f39a27ed8cfe077`.
The source provider at `[0x007B07EC,0x007B07F8)` binds the recovered
`xTickCount` seam at `0x20074A34`. The normal and ISR getter leaves occupy
`[0x007B07F8,0x007B07FC)` and `[0x007B07FC,0x007B0800)`, each with one
`R_ARM_THM_JUMP24` relocation to the provider. Two generated alignment bytes
precede those 20 source bytes; complete `B.W` plus NOP redirects own the 18
stock bytes.

The 115,932-byte main overlay and 3,639,328-byte component hash to
`272ba0e0492b0c6b721adec53a007809158d6871ccdb7ec52d4b6ceadd4b4529`
and
`615304858150f5ee6b7b4c62a714629375010c6f4ab20bea1b6958daa6a5b4af`.
The raw main application partitions into 116,118 source, 81,622 generated,
and 3,441,556 opaque bytes. Builder accounting reports 116,114 source-owned
bytes including 182 in place, 81,626 generated patch-site bytes, 81,808
replaced-stock bytes, 3,441,556 opaque base bytes, and the 32-byte wrapper.

The complete 4,417,782-byte package hashes to
`3bf635fb81439451e67642dc5ce11dde47a1773bda8ef11c12b35cd9bbbec01d`.
It contains 116,738 source bytes (2.642457%), 83,415 generated bytes
(1.888165%), and 4,217,629 opaque bytes (95.469378%); 200,153 bytes
(4.530622%) are controlled. Its 596,957-byte flash plan hashes to
`2b89447a0a867d1ec34f51e5798a4da7b28effe8bc5d7e27b1b7f24ce1c9cd3c`
and records 828 placed, two unresolved, five container-only, and six
protected regions. The placed set contains 53 source regions, 574 generated
entry-replacement regions, and 18 generated alignment regions. Package
ownership is 116,738 source bytes (2.642457%), 83,415 generated bytes
(1.888165%), and 4,217,629 opaque bytes (95.469378%); 200,153 bytes
(4.530622%) are controlled. Boot remains unchanged at 620 source, 817
generated, and 147,785 opaque bytes.

## Preceding Apollo-main FreeRTOS missed-yield tranche

The shared FreeRTOS component now adapts the exact MIT-licensed
FreeRTOS-Kernel V10.5.1 `vTaskMissedYield` body from commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. The official ten-byte function
at `[0x004555E6,0x004555F0)` performs only
`xYieldPending = pdTRUE`; focused disassembly binds that kernel-global word
to `0x20074A44`. Its only direct callers are `0x00441FA2` and
`0x00441FD8`, with no interior or stored entry reference.

Apple clang 21 emits a relocation-free 14-byte source leaf at
`[0x007B0800,0x007B080E)`. Homebrew clang 22.1.8 emits the same leaf bytes;
its existing profile layout places the leaf at
`[0x007B0F38,0x007B0F46)` after two alignment bytes. The canonical overlay
is 115,946 bytes with SHA-256
`a24cd67ac1d308b8812c329a294f3f07cbe9db4bc815be3fe081ba0c2fd9008c`;
the 3,639,342-byte Apollo-main component hashes to
`f037745e9b85d16fc048ba2fedb282f7fc498a524a90b803b652556e286cf77d`.
It records 592 functions and 559 replacement sites, 116,128 source-owned
bytes including 182 in place, 81,636 generated patch bytes, 81,818
replaced-stock bytes, and 3,441,546 opaque bytes.

The canonical 4,417,796-byte package hashes to
`f06fdc7a1e9034e72321680b35fbd542b12dad06135e6f01f701d670dba676ae`.
The Linux profile pins a 117,794-byte overlay, 3,641,190-byte component, and
4,419,644-byte package with SHA-256 values
`00cbcf99a63f69fa7fd2af607685179ac73edeafd0fc8c4e1ad49b6a13a02c0e`,
`f134beba731634fd81b42b143e3b1e414b4b8c07a9e3f009cc49e7c8258b1657`,
and
`13409c4d615651f1b8cb5618d6d1cb1a4d5095e8245c41b41c585a258c9114e1`.
The focused boundary and source-root qualification are documented in
[`../docs/research/freertos-missed-yield-source-boundary-audit.md`](../docs/research/freertos-missed-yield-source-boundary-audit.md).

## Prior Apollo-main FreeRTOS task-leaf tranche

The shared FreeRTOS component now also adapts the exact MIT-licensed
FreeRTOS-Kernel V10.5.1 `uxTaskResetEventItemValue` and
`pvTaskIncrementMutexHeldCount` bodies from commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. Their complete 22-byte stock
spans are `[0x00455ACA,0x00455AE0)` and
`[0x00455AE0,0x00455AF6)`, with SHA-256 values
`76463ec53fbc06884c159bf5b7d01708c06e404e9b51bdcaab307b219179c049`
and
`3cca7b821687976e59eccd737dc20b2064b86d66195c6f60f6a7cc2353f40d2f`.
The sole direct callers are `0x0047ECCE` and `0x00441D46`.

Both leaves retain the upstream volatile `pxCurrentTCB` evaluations at
`0x20074A20`. Reset binds offsets `+0x18` and `+0x2C` with 56 priorities;
mutex-held binds offset `+0x64` with `configUSE_MUTEXES=1`. Canonical
placement is `[0x007B0810,0x007B082A)` and
`[0x007B082C,0x007B0844)`, after two generated alignment bytes before each.

The same source tranche owns `vTaskSuspendAll` and
`vTaskInternalSetTimeOutState`. Their stock spans are
`[0x00454D7C,0x00454D88)` and `[0x00455556,0x00455566)`; canonical source
placement is `[0x007B0844,0x007B0854)` and
`[0x007B0854,0x007B0866)` without padding. Suspend binds the nested
`uxSchedulerSuspended` depth at `0x20074A58`; timeout capture binds
`xNumOfOverflows` at `0x20074A48`, `xTickCount` at `0x20074A34`, and the
two-word `TimeOut_t` layout.

The 116,034-byte canonical overlay, 3,639,430-byte component, and
4,417,884-byte package hash to
`d0b36ab3661f3b3487e3962bfe58d9f588f6a6f1ea14e1d9389f7e45d98094bd`,
`8a747653cc4d938e447197f2bec199933b68072318f0743e3cd85dcf656db8bc`,
and
`e3b7f29a19a4b3c19a14377a8ea8a77d14458a48678955d406ef7eea274dd6e7`.
The overlay records 596 functions and 563 replacement sites. Builder
accounting is 116,216 source-owned bytes including 182 in place, 81,708
generated patch bytes, 81,890 replaced-stock bytes, and 3,441,474 opaque
bytes.

The package contains 116,836 source, 83,501 generated, and 4,217,547 opaque
bytes; 200,337 bytes are controlled. Its 608,608-byte flash plan hashes to
`c6cde87716d8ff407e06998aadaaa0da6e78e5689ea1ac2963f104178447cae2`
and records 844 placed, two unresolved, and five container-only regions.

Linux places the reset and mutex-held leaves at
`[0x007B0F48,0x007B0F62)` and `[0x007B0F64,0x007B0F7C)`, followed by
suspend and timeout at `[0x007B0F7C,0x007B0F8C)` and
`[0x007B0F8C,0x007B0F9E)`. Its overlay, component, and package are
117,882, 3,641,278, and 4,419,732 bytes, with
SHA-256 values
`5c3c381342bb57ec4f33192ea89c2d40e8f0018c39c7092551243be7159dc326`,
`6bead197d657c26fa6ba84210949c8e28b266fbf63a8f908edda1d64516a3163`,
and
`a801d1ecbf83780701cbb7fdc1ae14401a656ba79102877458a3a88c73bc3fc4`.
Focused boundaries are documented in the
[reset audit](../docs/research/freertos-reset-event-item-value-source-boundary-audit.md)
and [mutex-held audit](../docs/research/freertos-mutex-held-source-boundary-audit.md),
and the paired scheduler-depth evidence is in the
[suspend audit](../docs/research/freertos-suspend-all-source-boundary-audit.md).

## Prior Apollo-main FreeRTOS queue/task closure tranche

The shared FreeRTOS component now production-integrates the authenticated
V10.5.1 `xTaskRemoveFromEventList`, `xQueueGiveFromISR`, and
`prvTaskCheckFreeStackSpace` algorithms. Complete stock replacements cover
246 bytes at `0x00455370`, 200 bytes at `0x00441A42`, and 22 bytes at
`0x00455820`; their maintained source leaves add 216, 212, and 62 bytes plus
one two-byte alignment region. The queue leaf's selected defined-sibling
relocation is constrained to the whole, global function section for the
simultaneously selected task-removal leaf.

Apple's overlay/component/package are 119,066, 3,642,462, and 4,420,916
bytes with SHA-256 values
`da056ac28814f1b07c90d3651b290cd459bfde5e3cbcf30fed9a75a72729a0ae`,
`0081322ddf2222bc8f6ab3848fab05cec68f39e999ec2e6e11bca6bb7bd3293d`,
and
`1b3ea44cc1cbd8004585e0208e33605c4e5f59229fdc5cb23395d19e0ba120f2`.
The qualified Linux artifacts are 120,942, 3,644,338, and 4,422,792 bytes,
hashing to
`8d56bdf484f3b1d67378f53eef89d7aea88282c6d552b8b2b1ee2bb7e0cb6905`,
`9532d9051a424453fda38d383aa303e4783c9832430d816554e2c861ea7afac0`,
and
`b93b39eb8e6f70e144b517dd7d770adcea67f62aa1100d722d4d1d0e6f8907ea`.
The sources and packages were validated offline; no hardware was accessed.

## Preceding Apollo-main FreeRTOS timeout-check tranche

The current provider adds authenticated FreeRTOS-Kernel V10.5.1
`xTaskCheckForTimeOut`. The complete stock range
`[0x00455566,0x004555E6)` is a 128-byte generated redirect/NOP replacement.
The source implementation is a four-byte-aligned, relocation-free 136-byte
leaf, preceded by two alignment bytes in both reviewed profiles. Apple places
it at `[0x007B1440,0x007B14C8)`; Linux places it at
`[0x007B1B94,0x007B1C1C)`.

The Apple overlay, Apollo-main component, and package are 119,204,
3,642,600, and 4,421,054 bytes with SHA-256 values
`4b3071e64d0e183efbb59788c94dca8ae01fba6d952aecbb9682893844171a79`,
`eaa59756edb47e85be46959cb2242200f51bc4a3acaea1fc4365ee1f6a59e152`,
and
`4fb13f64e81b8a6ef9bdf784ac38d5fc08ed03e4d310601a48bf4b395c20ab37`.
The Linux overlay, component, and package are 121,080, 3,644,476, and
4,422,930 bytes with SHA-256 values
`75054c31d8ca3e50659443c470f11a604fb715db430e08b3ad4c468042282324`,
`29c48306a2f8fab7b87af6c90b38786e4ee36d19f9eb68122614df4b355472ce`,
and
`22c0e367882b005c1b85ee40d138e596c423d5a6335b8d93bc5a68873323c3ab`.

The canonical manifest now contains 821 main regions and 884 whole-package
regions, with 877 placed, two unresolved, and five container-only. Apple
records 609 effective functions and 573 patches; raw configuration and Linux
record 613 functions and 577 patches. The promotion was compiled, assembled,
and checked offline. No hardware was connected, signed, flashed, reset, or
executed.

## Prior Apollo-main EasyLogger output/async tranche

The shared EasyLogger component now supplies the production `elog_output`
adaptation, while Apollo main supplies the G2 `(buffer,length,level)` submit
wrapper and stock-compatible private record builder. The three strict leaves
replace 1,182 complete stock bytes and append at
`[0x007B14C8,0x007B1CF6)` on Apple or `[0x007B1C1C,0x007B2346)` on Linux.
This tranche initially retained stock's enqueue-failure double recycle. The
corrected single-owner builder supersedes it in the current production overlay.

Apple's 121,298-byte overlay, 3,644,694-byte component, and 4,423,148-byte
package hash to
`02bfc227db4ad32c51303ea0dc49f908b277b78db1f2e5d7a5108559d863b249`,
`eecf209bf4df5f61252099b16fb0a17f4493ec5db3c29eb266d07e6cf64d956b`,
and `2b1008c2fc533f1257ee58bd6d0c08b449d2e12bc57d918f101586ba1d3e3d29`.
Linux's 123,170-byte overlay, 3,646,566-byte component, and 4,425,020-byte
package hash to
`36479ef84126bc0075a2bcfa93c86591376eb4f18eb32983f84865f9d51e72e9`,
`43d02017caa63a2bbe96e7dda056fa61009abcdb2913a12b2298dde131eb0a9c`,
and `12386dc6f165053c3a308b4ec64bf2df90becf2b793a2404830a598b62b7a33d`.
Both builds are deterministic and offline; no hardware was operated.

## Preceding Apollo-main FreeRTOS semaphore-take tranche

The broader queue source no longer emits its legacy semaphore body in the
production order. Apollo main appends the authenticated V10.5.1
`xQueueSemaphoreTake` adaptation after its relocation-free timeout-disinherit
helper and redirects `[0x00441C44,0x00441DA6)` to it. The only candidate
relocation binds to that helper. The stock helper at
`[0x00441EC4,0x00441ED8)` remains exact and unpatched because assembled-image
branch and pointer scans prove it unreachable. Apple overlay/component/package
pins are 121,330 / 3,644,726 / 4,423,180 bytes; Linux pins are 123,184 /
3,646,580 / 4,425,034 bytes. No hardware was operated.

## Preceding Apollo-main corrected EasyLogger ownership tranche

Apollo main now production-selects
`runtime_easylogger_async_record_build_single_owner.c` for the complete stock
entry `[0x00448D4E,0x00448DD2)`. The retained allocator, enqueue, and
diagnostic providers remain binary ABI seams. Enqueue is explicitly consuming;
there is no recycle relocation in the Apple or Linux closure, so enqueue
failure has one owner and one recycle. The submit wrapper still calls the same
builder entry and preserves the official caller topology.

Apple overlay/component/package pins are 121,706 / 3,645,102 / 4,423,556
bytes with SHA-256 `03dd692b55204fc36f67469ece0175e981b6281123a1b20b3db592ee2dd0b44c`,
`ae123c6a119bfebd0420898aef590a9ba1fd7f7dc7da00b3d347f6573bba43ec`,
and `7cf86c7311b4684eb6d2fdd4f832989317c858733f8438dc01ee649fcd1cf250`.
Exact-root Linux pins are 123,558 / 3,646,954 / 4,425,408 bytes with SHA-256
`f2c33def6131981c1a283968bc02bd55cde32536f4f33a7fa3cbf905d42693fc`,
`5ff7dd5894b74573971912371f22d0b463c32552ea1037441e1de992a6a8d3b9`,
and `fe49c0d9830327a0fdd0e7815a147bb6b810e27b9a9277b3bbfe9021de247a75`.
No hardware was operated.

## Current production-excluded EasyLogger queue/consumer candidates

`components/shared/easylogger/runtime_easylogger_async_queue_candidate.c/.h`
now recreates the complete bounded downstream G2 queue lifecycle: 256-record
pool initialization, dummy reset, allocation, recycling, enqueue, dequeue, and
one-shot state initialization. The deterministic host oracle covers capacity,
FIFO/dummy rotation, all retry ceilings and statistics, contention schedules,
failure ownership, and stock's deliberate failure to copy `level` during
dequeue. Apple and Linux target objects and every relocation are pinned. The
companion `runtime_easylogger_async_consumer_candidate.c/.h` closes the two
callback setters, default-metadata setter, and bounded 256-record drain. Its
ready/callback/metadata gates, payload delivery, unconditional recycling, and
cumulative processed statistic are host-oracle tested and independently pinned
under both compiler profiles. The third
`runtime_easylogger_async_worker_candidate.c/.h` preserves the stock event
order, per-bit clears, all 16 flag combinations, exact CMSIS thread attributes,
and explicit first-party persistence seams. The candidates remain outside
production pending target concurrency/hardware stress and atomic integration.

## Preceding production EasyLogger hexdump tranche

Apollo main now source-owns authenticated `elog_hexdump`, its two-argument
raw-submit wrapper, and its level-less record builder. Full-span `B.W` plus
NOP-fill replacements cover `[0x0043DACC,0x0043DC88)`,
`[0x00448CCC,0x00448D4E)`, and `[0x0044AA76,0x0044AA80)`. The latter
two end exactly at the existing level-aware builder and formatted-submit
entries. Ten strict leaves preserve the 41/1/1 stock caller topology and the
hexdump literal pool.

The main function is derived from authenticated EasyLogger under MIT; bounded
formatters and the G2 transport adapter are clean-room MIT code.
Independent leaves use arithmetic uppercase conversion instead of sharing
unowned digit-table rodata. The raw route leaves record byte `+0x0C`
untouched and has no recycler, event-set, level-aware, or formatted-submit
route. Its enqueue dependency is consuming.

| Profile | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 123,197 / `bb870969ad9913e2cc4f012c0abec05b5a946bfbcaff4ab3cf7d7ac3b1e08966` | 3,646,593 / `24bb10715c6650429bcdbe0b2942f8b1a16ddd9b2f6aa2a65a69361df2611c7f` | 4,425,047 / `24d4b6527621c87622a5fdee96c63d266f10c3452e0a52322386ad717084b81c` |
| exact-root Linux Clang 22.1.8 | 125,023 / `47f588845f4bd202d1d184282996cf45dd2cb514b4795ac9cdd5a7835da90d02` | 3,648,419 / `df9a1b00038d07ea0137258cc879547ecc86a11a737d1954bd1f4babd259c8e3` | 4,426,873 / `2eef6375f1ac218701f438afd8f5b5752b789a20db1e73f6dfd71486acc94423` |

The canonical package accounts for 123,979 source, 87,051 generated, and
4,214,017 opaque bytes. Exact-root Linux accounts for 125,862 source, 86,994
generated, and the same 4,214,017 opaque bytes. The manifest has 864
Apollo-main regions; Apple exposes 625 functions and 581 patch sites. The
dedicated production suite executes all 256 byte-format values and boundary
cases, checks exact stock topology and relocation closure, and verifies
literal/NOP preservation. Qualification was offline; no image was signed or
flashed and no hardware was operated.

## Preceding production FreeRTOS+CLI parameter-accessor-only tranche

This phase added the independently named
production `FreeRTOS_CLIGetParameter` adaptation. Apollo main replaces the
complete 100-byte official entry `[0x005848FC,0x00584960)` with a `B.W` and
NOP fill, and copies the source-owned `CMP R0,#127` fragment over the exact
collector halfword at `0x00541708`. This keeps input lengths 0 through 127
unchanged while reserving the array's last byte for NUL. The separately named
candidate remains production-excluded.

The placement and artifact values below are phase-local. The later
complete-console promotion retains this accessor and removes the standalone
capacity fragment.

The production accessor and capacity fragment contain 252 and two bytes,
respectively, with no text relocations. Apple placement is
`[0x007B2464,0x007B2562)`; Linux placement is
`[0x007B2B84,0x007B2C82)`. A whole-component ingress gate finds only the
intended stock-entry `B.W` to the accessor, no branch or stored pointer to an
interior address, and no ingress to the copied fragment.

| Profile | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 123,454 / `9e5004af49fb14a22e7e7ed7357e4c10f87dc8da3a7fb4d7b97fcffcde804c43` | 3,646,850 / `8722e5565bf54dade66fb751155c11ebd128d7a12853e3e4b8671c3c97807827` | 4,425,304 / `f2688fb35061283c05e9eb165d4f3eeb2cb2c4abd18cd28d074e58cb9da021db` |
| exact-root Linux Clang 22.1.8 | 125,278 / `a0a520069e497613b397af1d7327752201ced44c876d6925a7561ae45c91fa7c` | 3,648,674 / `8c477d28a9f58feaf722bd1e00b9767a8ca745ba618515d46339271cd0288c1a` | 4,427,128 / `5598cb1f2a3b9a8b6101f61afcc5e24de54b01c3d5aa45396bf161344b3618bb` |

Exact manifest ownership is 124,236 source, 87,305 generated, and 4,213,763
opaque bytes for Apple; Linux is 126,117 source, 87,248 generated, and
4,213,763 opaque bytes. The coarser Apple flash-plan accounting is 124,221
source, 87,168 generated, and 4,213,915 opaque bytes. The Apollo-main manifest
has 871 exactly tiled regions. Cross-profile overlay configuration registers
631 functions and 587 patches; the Apple-effective build report emits 627/583
and Linux emits 631/587 because four CRC/TinyFrame leaves are
Linux-profile-only. All qualification was offline; no image was signed or
flashed and no G2 hardware was operated.

## Prior phase-local nanopb varint production increment

Apollo main now replaces the complete 112-byte nanopb-compatible
`pb_decode_varint` body at `[0x0048F5B8,0x0048F628)` with a full-span B.W and
NOP fill to an altered Zlib-licensed production source leaf. Authenticated
nanopb 0.4.9 commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824` is the
selected compatibility baseline, not a vendor point-release claim. The sole
external leaf relocation binds to reviewed stock `pb_readbyte` at
`0x0048F454`; the 16-byte overflow diagnostic is local closure data. The
separately named candidate remains production-excluded.

| Profile | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple Clang 21.0.0 | 123,600 / `ea8a43a1c6e674cb3f2b1df4adc75887b39e92da7ff9c22fc400a634b09ae1e2` | 3,646,996 / `a897f9ae6215d4669b540f0142c356dc8e6610543884694e856308e303826b68` | 4,425,450 / `cdbc1c41607d4623625ce25d0757457c72c550915c60d4b5ab7077c5760d0812` |
| exact-root Linux Clang 22.1.8 | 125,420 / `dfc052f153f99c1fb153dd06cfcbd5380733d47d6e376ce902dbc2dc63413692` | 3,648,816 / `24a02cdaf64fb9d761fb896a4d09d72cfbe48f08b799cb49a95e0a61ad69892f` | 4,427,270 / `81729530e02fc666dfdef831933b44ec74e45bc3412c81d7c1161e03a5055152` |

The canonical manifest tiles 876 Apollo-main regions and registers 632
cross-profile functions and 588 patches. Qualification was offline; nothing
was signed, flashed, reset, booted, or executed on G2 hardware.

## Preceding CmBacktrace production increment

Apollo main now replaces `[0x00593AF6,0x00593AFE)` with a bounded CmBacktrace
MIT compatibility leaf and a separate exact G2 current-task-name adapter. The
Apple adapter/helper placements are `0x007B25F4` / `0x007B2604`; exact-root
Linux uses `0x007B2D10` / `0x007B2D20`. The two-byte alignment gap and the
single entry `B.W` are generated and pinned per profile.

| Toolchain | Overlay | Component | Package |
|---|---|---|---|
| Apple Clang 21.0.0 | 123,620 / `923b7774901565fe513290e23719eef52fc42566c8d49b6aeea4e1e2050fff09` | 3,647,016 / `df1c954ec9eed002669ee6c9f3bf3893dca8d1dbf28234f0f2c2858d7d257335` | 4,425,470 / `8663f87ee132fcfd80709bd32517331663f2c984c8909694eef419064567feab` |
| exact-root Linux Clang 22.1.8 | 125,440 / `d577a1faefb80857c9cf1aba83e3ae59cf90ee9747b208b8a187cd7a11bdb4ae` | 3,648,836 / `c1c6c563167c2451cb896e482dfaa58da075d6fea8ebc147dcb68dd74247da51` | 4,427,290 / `03d082df4a74448bcdfed86f4fea7d09454a03e87c9deb8ab178b444a3546222` |

The canonical manifest tiles 881 Apollo-main regions and registers 634
cross-profile functions, 589 patches, and 65 relocated leaves. Qualification
was offline; nothing was signed, flashed, booted, or run on G2 hardware.

## Prior phase-local complete FreeRTOS+CLI console-task increment

The shared FreeRTOS+CLI component now provides seven production source leaves
for the recovered G2 console task: fill, state initialization, registration,
command processing, byte consumption, one receive iteration, and the task
entry. These files are clean-room MIT G2 glue. The complete stock
task span `[0x00541600,0x0054171C)` redirects to the source entry and is
NOP-filled; the sole initializer pointer to `0x00541601` remains unchanged.

Production preserves the retained `FreeRTOS_CLIProcessCommand` call ABI,
22-group order, 76 proprietary descriptors, display functions, ring-read
tuple, and fixed input/output SRAM arrays. The source task intentionally
reserves byte 127 for NUL and accepts a receive only when its result is exactly
one. Because the payload guard now lives in the complete source task, the old
two-byte collector-capacity patch and appended capacity leaf are removed.

Neither the independently named task candidate nor the authenticated
FreeRTOS-Plus-CLI snapshot is a production input. The selected classic
FreeRTOS-Plus-CLI commit is only a compatibility baseline for the retained MIT
interpreter ABI; no exact vendor-provenance claim is made. The earlier bounded
nanopb and CmBacktrace leaves are compactly repinned and retain their existing
licenses and attribution limits. Apple Clang produces 124,212 / 3,647,608 /
4,426,062-byte overlay, component, and package artifacts with SHA-256 values
`913d0b39126eac6d13ac05baa44c745cd2a0c7317957293e34bbf418547d96bd`,
`cbe9f7361b47ef2150f2c3a01fca6f03f82e1ff3e2c805b7bbe774ba2154a354`,
and `0c257168dfc07a39e4603847329f6ac542d093719f0ea9c5a4cf904707b83670`.
Exact-root Linux produces 126,032 / 3,649,428 / 4,427,882 bytes with SHA-256
values
`bdc8bf69d75b7ff8354e12aa392416956a2afa04442488e7653e79b89ce62f1f`,
`d90824df529385ae5fba464c88b0c1e4e7d145a939024632c0806c4462d68d00`,
and `3aa279193bf67b50a75ad5490a8cd2e22ffb32d36f6de1e5befe0a11368fe743`.
Exact package ownership is 124,987 / 87,714 / 4,213,361
source/generated/opaque bytes for Apple and 126,868 / 87,653 / 4,213,361
for Linux.
The manifest has 890 exact regions; config census is 640 functions, 589 patch
sites, and 71 relocated leaves. Qualification was offline with no signing,
flashing, or hardware operation.

## Prior phase-local Apollo-main FreeRTOS queue-message-count increment

The shared FreeRTOS runtime now provides separate production translation
units for `uxQueueMessagesWaiting` and `uxQueueMessagesWaitingFromISR`. They
are bounded MIT-licensed adaptations of authenticated FreeRTOS-Kernel V10.5.1
commit `def7d2df2b0506d3d249334974f51e427c17a41c`, instantiated with the
recovered G2 `Queue_t` layout and existing source-owned assertion and critical-
section providers. Production replaces the complete 36-byte and 24-byte stock
bodies at `0x00441E66` and `0x00441E8A`; it does not redirect an interior
instruction or claim ownership of the six retained CMSIS wrappers.

Both Apple and Linux objects extract the same relocation-free 50-byte and
34-byte leaves. Apple places them at `0x007B2858` and `0x007B288C`, while
Linux places them at `0x007B2F74` and `0x007B2FA8`. Their exact artifact pins
are 124,298 / 3,647,694 / 4,426,148 bytes for Apple and
126,118 / 3,649,514 / 4,427,968 bytes for exact-root Linux, with SHA-256
triples `09c6c86c…` / `7cc8f0b5…` / `7209ad9d…` and
`db4f80dd…` / `45ee630e…` / `44a43f3c…`, respectively.

The config census is 642 functions, 591 patch sites, and 73 relocated leaves.
The 895 canonical Apollo-main regions exactly tile 3,647,694 bytes, including
92/124,436 source regions, 577/85,626 generated entry replacements, and
177/3,437,380 official bytes. The preceding console figures are phase-local.
Qualification was entirely offline with no signing, flashing, or hardware.

## Prior phase-local Apollo-main nanopb `pb_skip_varint` increment

The shared nanopb runtime now supplies a bounded Zlib-licensed
`open_cfw_nanopb_skip_varint` source leaf. It replaces the complete official
span `[0x0048F628,0x0048F64C)` and retains the sole stock caller at
`0x0048F6B6`. Its one strict `R_ARM_THM_CALL` relocation binds
`open_cfw_nanopb_read` to reviewed stock `pb_read` at `0x0048F3BE`; no broad
pristine nanopb translation unit is registered.

The 1,925-byte source and 2,401-byte header hash to
`89e53ebc01a2d28c4a94ac4a38313b8213788a23ed55bf767a9e8a5c6d961225`
and
`30a8aea087894af29396746a31bbebfc9195e12ee4d66e79b4b637828eeab103`.
Both toolchains produce the same 932-byte object and 36-byte unrelocated text.
Apple places the leaf at `0x007B28B0`; Linux uses `0x007B2FCC`.

Apple overlay/component/package artifacts are 124,336 / 3,647,732 /
4,426,186 bytes with SHA-256 values `97c57c110eb7b5fb7474bf945f35121432dfd713c02fcd47931da699c1da739a`,
`6f58d53a7f747ef8e9f701d01eb9fe1364dd3770df23aed58d9d6f0e7f743d99`,
and `21becb0b47e98f4bb50a296f4e9211a8b43ee57645e0c84e6d2053a15c5340ec`.
Exact-root Linux artifacts are 126,156 / 3,649,552 / 4,428,006 bytes with
hashes `e7f3d94e8a7253f761c5d535dba918b765c9f3f2aba82a5cdc5372bd0ebf9d62`,
`160c431d1ff7ea9bd941583705fd2ebfb9cb6b7037298bf3d0bd8f2bd72dbd71`,
and `44adc5125db5e459bc0e32f258a02fbf2f564f8f4f739b542d7406741c046ab1`.

The config census is 643/592/74 functions/patches/relocated leaves, and the
898 canonical regions exactly tile the 3,647,732-byte component. nanopb 0.4.9
is a compatibility selection within authenticated pristine 0.4.7–0.4.9, not
vendor revision proof. The preceding queue figures are phase-local. All work
was offline; nothing was signed, flashed, or executed on hardware.

## Preceding Apollo-main littlefs tag-type increment

`components/shared/littlefs/runtime_littlefs_tag_type2.c` and its header now
provide the bounded production symbol `open_cfw_littlefs_tag_type2`. This is
an altered BSD-3-Clause adaptation of the 92-byte `lfs_tag_type2` definition
in the authenticated littlefs v2.10.1 source-equivalent baseline at commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`; the complete unchanged license
is retained at `third_party/littlefs/LICENSE.md`.

The production patch authenticates and replaces `[0x004CAE90,0x004CAE98)`.
Exactly two direct callers enter the stock start, while the ten-byte source
leaf is scalar-only, relocation-free, and provider-free. Apple places it at
`[0x007B29A8,0x007B29B2)` and exact-root Linux at
`[0x007B30C4,0x007B30CE)`. Both text sections hash to
`88be40d05d37142bf0bae8306026d8c405a4f8f441aabd87ee6731557d4149fd`.

Current Apple overlay/component/package sizes are 124,558 / 3,647,954 /
4,426,408 bytes with SHA-256 values
`8dc6206e0a6ed458401de46e5fa60d0a7eebc152eab4032d087fc4e667f7f378`,
`ec9f098bf69029862df63ff0929f6bbd9c345f540b3565b6cfc7cd71edbc36c4`,
and `f31bef6e0faf8e3655f5c92c385ebe6ee3e7f5ef5635401ceb05cf98089976fe`.
Exact-root Linux uses 126,378 / 3,649,774 / 4,428,228 bytes with hashes
`12ebf0aef9e1ce61c6f5f151515a8c4245b1b353ca921dcddfc6b521cf8f870a`,
`eeaca07a2c4bec75f4652e9f2853a75ff45684584d5e6074d99d112a41e5ddfc`,
and `caa150eda201d91c8ec6046f5a9017ab87e7ee936fe0f542957bff4efdd4b37f`.

The shared config census is 649 functions, 598 patches, and 80 relocated
leaves. The Apple report records 645 overlay functions and 594 generated
patch records. Its 971-record plan hashes to
`3ac4c2dfdce764389721b2c81f87d6bd0730cfefcdd0cfbe98bf6afa32935bcd`
and the canonical manifest has 915 regions. This component does not link a G2
block-device port or authorize signing, flashing, format, erase, or any
hardware operation.

## Preceding Apollo-main littlefs `lfs_file_size_` increment

Apollo main now redirects the complete private littlefs span
`[0x004CE472,0x004CE48A)` to the 20-byte
`open_cfw_littlefs_file_size_private` source leaf. The bounded BSD-3-Clause
adaptation uses the authenticated littlefs v2.10.1 source-equivalent snapshot,
preserves `ctz.size +0x2C`, `flags +0x30`, `pos +0x34`, and
`LFS_F_WRITING = 0x00020000`, and closes its sole relocation over the existing
source-owned `open_cfw_littlefs_util_max`. The two official callers remain
unchanged and no interior ingress is admitted.

Apple overlay/component/package artifacts are 124,356 / 3,647,752 / 4,426,206
bytes with SHA-256 values
`ab16010088fc71b58ed32c7bf28867900301bd92baa871a441f18fdf10ee0b1a`,
`43ad32acb3e6a09dde1d47681803400da2b7ecead348f60ae08443d2565fcc88`,
and `51f840accc7663cee93764068da124231ea1e26cafb2f135a43b74ca5c247040`.
Exact-root Linux artifacts are 126,176 / 3,649,572 / 4,428,026 bytes with
hashes `45ddc376dc3943a1b2aaff981566cbd55a89197ddfe65ac368cedd6f607b4fd3`,
`d8ae148bbb44df20a66fef2815ed2276d7bf1608a11ed833c44260e4178da4fb`,
and `dba4d48dccef97ad4b1559f239553b467632f6a546e0ec908977ea395b13f9b7`.

The config census is 644/593/75 functions/patches/relocated leaves. The 901
canonical regions exactly tile the Apple component, including 579/85,686
generated source-entry replacement, 178/3,437,320 official, and 94/124,492
source-compiled regions. Exact package ownership is
125,127/87,838/4,213,241 source/generated/opaque bytes. The preceding nanopb
and queue figures are phase-local. This integration does not provide a G2
filesystem port or authorize hardware format or erase; all qualification was
offline.

## Preceding Apollo-main FreeRTOS task-list initializer increment

The shared FreeRTOS runtime now provides
`open_cfw_freertos_task_lists_initialize`, a bounded MIT adaptation of the
authenticated V10.5.1 `prvInitialiseTaskLists` operation. Its compile-time
contract preserves 56 ready lists, the recovered 20-byte `List_t`, five
special lists, and two volatile selector-word stores. The header declares the
existing list provider with its exact
`struct open_cfw_freertos_list_initialise_list` tag; all six calls explicitly
convert through `void *` to that provider type, closing the prior C prototype
blocker with diagnostic-clean host and Cortex-M55 combined checks.

Production registers `open_cfw_freertos_task_lists_initialize` and the exact
`replace_freertos_task_lists_initialize` patch. The common 88-byte text has
six `R_ARM_THM_CALL` relocations and no dependency other than
`open_cfw_freertos_list_initialise`. Apple/Linux placements are
`0x007B28E8`/`0x007B3004`; the complete stock span
`[0x0045568C,0x004556E0)` is replaced, while its sole caller remains intact.

Apple overlay/component/package artifacts are 124,444 / 3,647,840 / 4,426,294
bytes with SHA-256 values
`34c6d23ea9e1c3f01440222e44fe2af38121a02309b61efb2b15a806e0e77158`,
`fd4625c32ee413abe058ffabc6a719be7af0af3d0096ce4f06b8535f01463b8b`,
and `188702b9f1b8c52e3ea46f33765bd9555395dd3ada0aa1233503930b0e594c97`.
Exact-root Linux artifacts are 126,264 / 3,649,660 / 4,428,114 bytes with
hashes `62d8e21bec02a7505a39296f2e474e703b6a3989c252c6cda3fda43e12e7d236`,
`5a098690012093defe0573e7f5c4cfb20ae79f77ff3aa88ce6adda3279c73764`,
and `0c446de88f84b8b81049b54efc94e0c40b411bfc9b2c8655cbf5b762bb846068`.

The config census is 645/594/76 functions/patches/relocated leaves. The 904
canonical Apple regions include 580/85,770 source-entry replacements,
179/3,437,236 official regions, and 95/124,580 source-compiled regions. The
distinct bootloader homolog remains outside this Apollo-main-only increment;
all qualification was offline.

## Preceding Apollo-main nanopb close-substream increment

The shared nanopb runtime now provides the third bounded Zlib production leaf,
`open_cfw_nanopb_close_string_substream`. It replaces the exact 42-byte stock
span `[0x0048F7CA,0x0048F7F4)`, SHA-256
`439bbeecb6a0b8266dc3dcd913e98793352b6b346a7a58cdd44322c734621818`.
Its source/header pins are 2,061 bytes /
`736e7ec228f9282ba5b093fd482441e6e2017fff860d989dc3aadb2bdeff0fcb`
and 2,537 bytes /
`851af370162d79f4bd0be8b8bb9a5731d47cf02527078b9e278019340f2d65d4`.
The 36-byte leaf has exactly one relocation, binding the already qualified
`open_cfw_nanopb_read` seam to stock `pb_read` at `0x0048F3BE`.

Authenticated pristine nanopb 0.4.7, 0.4.8, and 0.4.9 have the same relevant
semantics. OpenCFW selects the authenticated 0.4.9 snapshot as a compatibility
baseline only; this does not prove the vendor's historical nanopb revision.
Focused disassembly supplies the G2 stream ABI, exact stock body and callers,
read seam, and entry topology. Broader retained firmware remains opaque and is
not thereby source-authenticated.

Apple places the leaf at overlay offset 124,444 / `0x007B2940` and produces
124,480 / 3,647,876 / 4,426,330-byte overlay, component, and package artifacts.
Exact-root Linux places it at offset 126,264 / `0x007B305C` and produces
126,300 / 3,649,696 / 4,428,150 bytes. Their relocated leaf hashes are
`c838be0dfb478fe7fa03d9d71069a200a6477eb5783b631d7d977cd501475438`
and
`a90a09f0f98c5b4cf7d885af34c914ae5d492ac7352b5e359ba68ad482cb3044`.
The config census is 646/595/77 functions/patches/relocated leaves; the
canonical manifest has 907 regions and 96 source-compiled leaves.

## Preceding Apollo-main littlefs private rewind increment

`runtime_littlefs_file_rewind_private.c` is the next bounded littlefs v2.10.1
production leaf. It replaces `[0x004CE460,0x004CE472)` in full and binds its
only relocation to retained private `lfs_file_seek_` at `0x004CE3BC`. The
source/header pins are 1,239 /
`e6afb5b67671b3219971b19c20290c601568752d814064147f5ccd4118f5acc8`
and 1,743 /
`7430dcd1ad1ea3973d619f2d67d8d8b11a688018d48a3bc26a40e407d1fedb56`.
The common 16-byte unrelocated leaf hashes to
`46e8bab056ad39ced45edb5da2612f6470674ab5a428df7f08822f6c2d9e184b`.

Apple produces 124,496 / 3,647,892 / 4,426,346-byte overlay, component,
and package artifacts; exact-root Linux produces 126,316 / 3,649,712 /
4,428,166 bytes. That tranche's census was 647/596/78 and its canonical
manifest had 908 regions, including 582 source-entry replacements and 97
compiled source regions. The authenticated upstream reuse does not include a
block-device port, mount policy, erase path, or hardware qualification.

## Preceding dual-image littlefs tag-chunk increment

The shared littlefs runtime now supplies
`open_cfw_littlefs_tag_chunk` to both Apollo main and the bootloader. It is a
773-byte altered BSD-3-Clause adaptation of the authenticated littlefs
v2.10.1 source-equivalent baseline; its 879-byte header exposes only the
recovered 32-bit scalar tag ABI. The files hash to
`71851bd05e26e703b8697b9994b556db46511c37e9500da98e3406b37a92c8da`
and
`1061f5d68ff6f81a6f1853bfefe37b77f5f3b8b09e627b1bfa0d191842d1f6f5`.
The selected commit is compatibility evidence, not proof of the vendor's
exact checkout.

Both official images contain the same six-byte stock helper and each has four
authenticated direct callers. The complete stock spans
`[0x004CAEA0,0x004CAEA6)` and `[0x00410BA8,0x00410BAE)` become generated
`B.W`-plus-NOP redirects. The six-byte source text is relocation- and
provider-free and hashes to
`db1dfda72afb267e96cd4e11eaf5d44659195b0afecbdcd8ed8572c34049df74`.

Apple main/boot overlays are 124,566/628 bytes with SHA-256
`0339a938dd13e8b89997cd6e75d7dc56e2300125039304f751b802af1dd73da8`
and `10dce6ad20335a583b4ab2fad4b916ed335d65f126af06b77a935be9702149f6`;
their components are 3,647,962/149,228 bytes with SHA-256
`ac8b3c62d32e849bfd1e71f4950f7ee58d02dc56dd8595c6706a453fe1cf402e`
and `ecfe0087fef4eab3a75f41a2db28d31b3e31c589fdaceec3c209e6e503eb295f`.
The 4,426,422-byte Apple package hashes to
`441bc7dd753518464afa0ac8ab84c26aedcd18228dbab3427d8c20ff66a8d914`.

Exact-root Linux main/boot overlays are 126,386/628 bytes with SHA-256
`5ebdb04c602ff59241f9d376caa474180f1e9c90ba2ea05581e2b247528b814a`
and `e7619c604912ded4b5ac4513287bb68560bba2a09f84cda42dd9f1cf2d080a63`;
their components are 3,649,782/149,228 bytes with SHA-256
`3ad0a8692694132ce30b266ae8ec4ffb66617de173cb1e3d96ee90335945c70d`
and `64d87f89085988da184b7cf3b9758e702093e35f0e4b2afb6da22971b8532f1b`.
The 4,428,242-byte Linux package hashes to
`8f62cf0ffb7d861ca1e6f9881e3221557f0da4640491489c7468129c5d57f1ba`.

The configs now contain 650/599/81 main functions/patches/relocated leaves
and 29/27/10 for boot. Exact Apple package ownership is
125,339/88,034/4,213,049 source/generated/opaque bytes. The scalar helper
does not mount or mutate a filesystem, and this offline integration does not
authorize signing, flashing, format, erase, reset, or hardware operation.

## Preceding atomic dual-image littlefs tag-validity/type1 increment

The shared littlefs runtime now additionally supplies
`open_cfw_littlefs_tag_isvalid` and `open_cfw_littlefs_tag_type1` to both
Apollo images. The altered BSD-3-Clause sources are bounded adaptations of the
exact definitions in the authenticated v2.10.1 source-equivalent baseline,
not evidence of the vendor's exact checkout. Focused disassembly supplies the
32-bit scalar ABI, the two byte-identical stock spans, three/eight caller sets,
and complete entry topology; both emitted leaves are provider- and
relocation-free.

Apple places the main leaves at `0x007B29BC` and `0x007B29C4`, and boot at
`0x004346EC` and `0x004346F2`. Exact-root Linux moves only the main leaves to
`0x007B30D8` and `0x007B30E0`. Final Apple main/boot overlays are 124,586/644
bytes and components are 3,647,982/149,244 bytes; the 4,426,458-byte package
hashes to
`f0e7e4c5e090ea558968b6293f3eec0a7f88a6126ea164547c25c8462b60be23`.
Linux uses 126,406/644-byte overlays, 3,649,802/149,244-byte components, and a
4,428,278-byte package hashing to
`07cee183416db26bbe13673c1123e4ef19593d6343caa63c6c94791a210dc0dc`.

The canonical manifest contains 926 main and 60 boot regions. Exact Apple
ownership is 125,371 source, 88,074 generated, and 4,213,013 opaque bytes.
This is deterministic offline assembly only; signing, flashing, format,
erase, reset, boot, and hardware operation remain outside the approved scope.

## Preceding atomic dual-image littlefs tag-type3 increment

The shared littlefs runtime now also supplies
`open_cfw_littlefs_tag_type3` to Apollo main and the bootloader. Focused
disassembly authenticates byte-identical eight-byte stock bodies, complete
30/17-caller sets, the 32-bit scalar ABI, and complete entry topology. The
bounded BSD-3-Clause adaptation comes from the authenticated v2.10.1
source-equivalent baseline and has no providers or relocations.

Apple main appends two alignment bytes and the six-byte leaf at
`[0x007B29D0,0x007B29D6)`; exact-root Linux uses
`[0x007B30EC,0x007B30F2)`. Both boot profiles append the leaf at
`[0x004346FC,0x00434702)`. Final Apple main/boot overlays are 124,594/650
bytes and components are 3,647,990/149,250 bytes; the 4,426,472-byte package
hashes to
`96f5309c2f77834a2c034b00d04618f0fa42ea3019924d5d51047f7a54c3db4d`.
Linux uses 126,414/650-byte overlays, 3,649,810/149,250-byte components, and a
4,428,292-byte package hashing to
`e56f78421dd83283e3d4e3f4a6b61a3400260c2618719cc6051453dd9e249bc1`.

At that preceding milestone, the `lfs_tag_size` source candidate passed five
focused tests and remained absent from production configs and manifests;
at that milestone nanopb `pb_decode_fixed64` had passed seven tests but was
still awaiting promotion; the current Apollo-main-only increment now
promotes it.
`lfs_tag_id` advanced to the now-preceding increment below, and tag-size is
promoted by the current increment that follows it. The type3 result is
deterministic offline assembly only;
signing, flashing, mount, format, erase, reset, boot, and hardware operation
remain NO-GO.

## Preceding atomic dual-image littlefs tag-ID increment

The shared runtime now supplies `open_cfw_littlefs_tag_id` to Apollo main and
the bootloader. Its complete byte-identical stock bodies occupy
`[0x004CAEB0,0x004CAEB8)` and `[0x00410BB8,0x00410BC0)`, hash to
`0843abb3e9ef39afac8e69ae1e181efa0b5b5c8ebf53e20844b53fdf245b1036`,
and have 50/41 authenticated direct callers with no reviewed alternate or
interior ingress. The source implements the exact ten-bit ID extraction
`(tag & 0x000ffc00) >> 10` from authenticated littlefs v2.10.1 commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`.

The altered BSD-3-Clause C source/header are 845/872 bytes with SHA-256
`5b6c3ce0f4236d6c6bc0a12891e41929e9034a7ddc2f68bd4f6a1d5d4fa07638`
and `5d6d1c5df9a0fb31f80ad0f6a876795cb154b039fa72df17c615b38cd5e2099e`.
Both reviewed profiles emit `c0f389207047`, SHA-256
`6194594e24288e708887a0e938b2a54401c8c732210d91af7a5927d03bd3604c`,
with no providers or relocations.

Final Apple/Linux placements, patch encodings, and aggregate artifacts are
pinned in the root README and the profile-specific evidence documents.
The production censuses are `654/603/85` main and
`33/31/14` boot, with manifest region counts
`932 main / 65 boot`. This pure scalar helper does not
mount or mutate a filesystem and authorizes no signing, flashing, format,
erase, reset, boot, or hardware operation.

## Preceding atomic dual-image littlefs tag-size increment

The current component-contract increment registers the shared
`open_cfw_littlefs_tag_size` scalar leaf in Apollo main and the bootloader.
Its complete official spans are `[0x004CAEB8,0x004CAEBE)` and
`[0x00410BC0,0x00410BC6)`, with byte-identical body `8005800d7047`, exactly
15/14 direct callers, and no reviewed alternate or interior ingress. The
altered BSD-3-Clause source implements authenticated littlefs v2.10.1
`lfs.c[10793:10880]` behavior, SHA-256
`9df85bc43ca9f90ef58c425c5fd9bbbbf53585093be5fad0cc580fc88814ea5c`,
`tag & 0x000003ff`, from commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`.

Final main/boot placements, patch encodings, component/package artifacts, and
flash-plan pins are closed in the explicit root and evidence ledgers. The
final function/patch/relocated-leaf config censuses are
`655/604/86` main and
`34/32/15` boot;
manifest counts remain
`935 main /
67 boot`. The tag-ID increment above is the settled preceding production
milestone. This promotion owns only a pure scalar mask and authorizes no filesystem
or hardware mutation.

## Preceding Apollo-main nanopb fixed64 increment

The Apollo-main overlay registers `open_cfw_nanopb_decode_fixed64` as the
source replacement for `[0x004901AC,0x004901CC)`. At that preceding milestone
its call resolved through the binary `pb_read` ABI entry at `0x0048F3BE`; the
current increment source-owns that entry. The leaf has one strict call
relocation and no data, global, allocator, schema, or hardware closure. No
bootloader homolog was authenticated, so the boot overlay is unchanged.

Apple places 28 text bytes at `0x007B29E8` after two alignment bytes and emits
the full entry patch
`22f31cbc00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf`.
Exact-root Linux places 30 bytes at `0x007B3104` and emits
`22f3aabf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf`.
Final main overlay/component sizes are 124,640/3,648,036 for Apple and
126,462/3,649,858 for Linux. Config censuses close at `656/605/87` main and
`34/32/15` boot, with `938/67` manifest regions. The exact package pins are
4,426,530 / `a3d06dd732722859a7cd4da1582cea49464cbbfccdb90e329afa6ec9352195d4`
and 4,428,352 /
`75af4c1facb8c663cff2a8d4469625261ffa04d9c9587dc0db9ecf2c2f401b6d`.

## Preceding Apollo-main nanopb `pb_read` increment

At this preceding milestone the shared nanopb runtime supplied
`open_cfw_nanopb_read` for Apollo main.
The complete stock span `[0x0048F3BE,0x0048F454)` becomes a generated
four-byte `B.W` plus 73 Thumb NOPs. All 13 authenticated external callers keep
the stable stock ABI entry; exhaustive branch and pointer scans find no
external interior ingress. The bootloader contains no authenticated homolog.

The altered Zlib source is selected against authenticated nanopb 0.4.9 within
the source-identical 0.4.7--0.4.9 range. Both profiles emit identical
158-byte relocated text. Apple places it at `0x007B2A04`; exact-root Linux
places it at `0x007B3124` after two alignment bytes. Its only retained binary
dependencies are the private buffer-reader Thumb identity and two immutable
runtime error strings.

At that milestone, main overlay/component sizes were `124798/3648194` for Apple and
`126622/3650018` for Linux. Packages are `4426688` / SHA-256
`f861d049873d497b44f25b265bad4a6ba9409aef3ff3abb4ed6abc1a031a4804`
and `4428512` /
`0269400751d0ffa0f58c5cf8658b4dbc6e8af90a875d13bc2e5f684a436d26a9`.
The milestone census was `657/606/88` main and `34/32/15` boot, with `941/67`
manifest regions. Those values belong to the preceding `pb_read` milestone.
The following constructor milestone superseded them, and the subsequent
signed-varint section records the later Apple aggregates and censuses. This
is an offline source/build
integration and authorizes no signing, flashing, reset, boot, filesystem
mutation, or hardware operation.

## Preceding Apollo-main nanopb stream-constructor milestone

`components/shared/nanopb/runtime_nanopb_istream_from_buffer.c` was the ninth
bounded nanopb production function. Apollo main replaced the complete 28-byte
stock entry and appended a 20-byte Apple source leaf at `0x007B2B04`, retaining
callback identity `0x0048F3A5` and all 30 callers. The Zlib source uses
authenticated nanopb 0.4.9 as a compatibility baseline; this was not proof of
the vendor point release. The bootloader was unchanged.
At that preceding milestone, the Apple overlay/component/package sizes were
`124916/3648312/4426806`; exact-root Linux used
`126742/3650138/4428632`. The main config census was `660/609/91`, and
the manifest contained `949/67` main/boot regions. Detailed hashes and
reproduction evidence are recorded in
`docs/research/nanopb-istream-from-buffer-source-audit.md` and
`docs/linux-reproducible-build.md`.

The subsequent, now-preceding Apple signed-varint increment added
`open_cfw_nanopb_decode_svarint` as nanopb's tenth bounded altered function.
Its 54-byte leaf is appended at overlay offset `124916` / runtime
`0x007B2B18`, with its sole call relocated directly to
`open_cfw_nanopb_decode_varint`; the full 64-byte stock span at `0x00490150`
was replaced. Apple overlay/component/package sizes at that milestone were
`124970/3648366/4426860`, and the Apollo-main manifest had 951 regions. The
exact-root Linux Clang 22.1.8 replay emits a 50-byte leaf at overlay offset
`126744` and records `126794/3650190/4428684` as the Linux
overlay/component/package sizes. Its sole relocation remains a direct call to
the source-owned unsigned decoder.

At the preceding varint32 milestone the private/public pair brought the
allowlist to twelve; the current skip-string increment below brings it to
thirteen.
Apple installs 222-byte private text plus its 16-byte literal at
`0x007B2B50`/`0x007B2C2E`, and 10-byte public text at `0x007B2C40`, with two
separate full-span stock patches and two alignment regions. Current
overlay/component/package sizes are `125222/3648618/4427112`; the main
manifest has 957 regions. Exact-root Linux independently records the private
leaf/literal at offsets `126796/127018`, the public leaf at `127036`, and
overlay/component/package sizes `127046/3650442/4428936`.

## Current Apollo-main nanopb skip-string increment

`open_cfw_nanopb_skip_string` is the thirteenth bounded altered nanopb
function. It replaces all 32 stock bytes at `0x0048F64C`, calls the
source-owned varint32 and read providers, and emits identical 34-byte text in
both reviewed compilers. Apple/Linux place it at `0x007B2C4C`/`0x007B336C`.
The current 960-region build closes at overlay/component/package sizes
`125258/3648654/4427148` and `127082/3650478/4428972`, respectively. Both are
current fail-closed profiles; neither establishes a vendor checkout or any
hardware execution.

## Current Apollo-main nanopb Boolean decoder pair

`runtime_nanopb_decode_bool.c` and `runtime_nanopb_dec_bool.c` provide the
seventeenth and eighteenth bounded altered nanopb functions. Apple places 28
and 6 source bytes at `0x007B2DCC` and `0x007B2DE8`, replacing complete stock
entries at `0x0049012C` and `0x004901CC`. Both dependency edges resolve within
the source overlay. The Apple overlay/component/package closes at
`125642/3649038/4427532`; exact-root Linux replay remains pending.

## Current Apollo-main nanopb private field-varint adapter

`runtime_nanopb_dec_varint.c` is the nineteenth bounded altered nanopb
function. It replaces all 380 stock bytes at `0x004901D6` with a redirect to
304 bytes of Apple text at `0x007B2DF0` and a 36-byte diagnostic closure at
`0x007B2F20`. Its three executable dependencies resolve to source-owned
unsigned- and signed-varint decoders. The Apple overlay/component/package
closes at `125984/3649380/4427874`; exact-root Linux replay remains pending.

`runtime_nanopb_dec_bytes.c` is the twentieth bounded altered nanopb
function. It replaces all 146 stock bytes at `0x00490358` with a redirect to
98 bytes of Apple text at `0x007B2F44` and a 48-byte diagnostic closure at
`0x007B2FA6`. Its varint32 and stream-read dependencies are source-owned, and
the no-malloc 16-bit configuration is explicit. The Apple
overlay/component/package closes at `126130/3649526/4428020`; exact-root Linux
replay remains pending.

`runtime_nanopb_dec_string.c` is the twenty-first bounded altered nanopb
function. It replaces all 158 stock bytes at `0x004903EA` with a redirect to
114 bytes of Apple text at `0x007B2FD8` and a 49-byte diagnostic closure at
`0x007B304A`. Its varint32 and stream-read dependencies are source-owned; the
no-malloc/no-UTF8-validation target configuration is explicit. The Apple
overlay/component/package closes at `126295/3649691/4428185`; exact-root Linux
replay remains pending.

`runtime_nanopb_dec_submessage.c` is the twenty-second bounded altered nanopb
function. It replaces all 172 stock bytes at `0x0049048C` with a redirect to
138 bytes of Apple text at `0x007B307C` and a 25-byte diagnostic closure at
`0x007B3106`. Its substream make/close providers are source-owned. The larger
private `pb_decode_inner` dependency remains a deliberate fixed-address stock
seam at `0x0048FE98`; the indirect callback remains application/schema ABI.
The Apple overlay/component/package closes at `126459/3649855/4428349`;
exact-root Linux replay remains pending.

## Current Apollo-main nanopb iterator cluster

`runtime_nanopb_iterator_cluster.c` and its shared header provide nine
selector-isolated Zlib-licensed leaves for the descriptor provider, seven
iterator APIs, and default field callback. Eight full-span stock-entry patches
route all live entries to source and close six calls from the decoder/defaults
frontier. The production nanopb allowlist is now thirty-three functions.

Apple closes at overlay/component/package sizes
`128264/3651660/4430154`. The manifest contains 1,022 Apollo-main regions and
package ownership is 129,014 source, 90,977 generated, and 4,210,163 opaque
bytes. The 536 bytes of unreachable private iterator implementation stay
opaque. Exact-root Linux replay and hardware execution remain pending. See
`../docs/research/nanopb-iterator-cluster-source-audit.md`.

## Current Apollo-main nanopb defaults pair

`runtime_nanopb_defaults_pair.c` adds selector-isolated implementations of
private `pb_message_set_to_defaults` and `pb_field_set_to_default`. Their 158-
and 256-byte Apple leaves live at `0x007B382C` and `0x007B38CC`; both complete
stock entries at `[0x0048FCE2,0x0048FE98)` redirect to source. Recursive
defaults and iterator operations are source-owned, while `decode_field @
0x0048FBE4` remains the sole fixed executable seam. The nanopb production
allowlist is now thirty-five functions.

Apple closes at `128680/3652076/4430570`; package ownership is 129,428 source,
91,417 generated, and 4,209,725 opaque bytes. Exact-root Linux replay and
hardware execution remain pending.

## Current Apollo-main IAR math/errno closure

`candidates/iar_runtime_math_errno.S` supplies selector-isolated hard-float
`sqrtf`, EDOM, ERANGE, and errno-address candidates. The 28/20/20/10-byte
sections are identical under reviewed Apple and Linux Clang profiles. Lorelei
Unicorn matched 5,500 candidate executions to stock. Four guarded redirects
install the leaves at `[0x007B42A2,0x007B42F0)` on Apple and
`[0x007B49EE,0x007B4A3C)` on Linux. Both profiles and packages replay twice;
all ten bounded IAR code units are now production-integrated.

## Current Apollo-main IAR memory-provider closure

`candidates/iar_runtime_memory.S` provides three selector-isolated,
relocation-free clean-room leaves for the authenticated void-EABI memcpy,
aligned memcpy, and memmove providers. Apple places 626 source bytes at
`[0x007B4030,0x007B42A2)`; Linux places the identical sections at
`[0x007B477C,0x007B49EE)`. Three guarded stock redirects reclassify 316 bytes
from opaque to generated ownership.

Apple closes at `130942/3654338/4432832`; Linux closes at
`132810/3656206/4434700`. Package ownership is 131,677 source, 93,352
generated, and 4,207,803 opaque bytes. Both toolchain profiles were replayed
twice; hardware timing remains deferred.

## Current Apollo-main nanopb dispatch/extension trio

`runtime_nanopb_dispatch_extension.c` and `.h` add selector-isolated
implementations of private `decode_field`, `default_extension_decoder`, and
`decode_extension`. Apple places their 71-byte closure, one alignment byte,
92-byte closure, and 80-byte leaf at `0x007B39CC`, `0x007B3A13`,
`0x007B3A14`, and `0x007B3A70`. All three stock entries are full-span guarded
redirects; dynamic extension callbacks remain application/schema ABI.

The nanopb allowlist is now 38 functions. Apple closes at
`128924/3652320/4430814`; package ownership is 129,671 source, 91,656
generated, and 4,209,487 opaque bytes. Exact-root Linux replay and hardware
execution remain pending.

## Current Apollo-main nanopb field-decoder cluster

`runtime_nanopb_field_decoder_cluster.c` and `.h` add selector-isolated
implementations of private `decode_basic_field`, `decode_static_field`, the
no-malloc `decode_pointer_field`, `decode_callback_field`, and
`pb_dec_fixed_length_bytes`. Five guarded full-span redirects replace 1,116
stock executable bytes; 1,132 source bytes and eight alignment bytes occupy
`[0x007B3AC0,0x007B3F34)`. All fixed calls bind source-owned nanopb leaves;
two dynamic schema callbacks remain intentional ABI.

The nanopb allowlist is now 43 functions. Apple closes at
`130064/3653460/4431954`; package ownership is 130,803 source, 92,780
generated, and 4,208,371 opaque bytes. Exact-root Linux replay and hardware
execution remain pending.

## Current Apollo-main AndersKaloer/Ring-Buffer closure

`runtime_ring_buffer.c` provides seven selector-isolated MIT-licensed leaves
for the complete dynamic-buffer API. Their 248 source bytes and four alignment
bytes occupy `[0x007B3F34,0x007B4030)`. Seven guarded redirects replace all
252 callable stock-span bytes (250 instructions plus two alignment bytes) at
`[0x00598134,0x0059823C)` while retaining the
authenticated assert provider and strings.

Apple closes at `130316/3653712/4432206`; package ownership is 131,051 source,
93,036 generated, and 4,208,119 opaque bytes. Exact-root Linux replay and
hardware execution remain pending.

## Apollo-main CMSIS-FreeRTOS core-leaf milestone

`apollo_main/core_overlay/runtime_cmsis_core_leaves.c` adds bounded
Apache-2.0 implementations of private `IRQ_Context`,
`osKernelGetTickCount`, `osThreadGetId`, and
`osMessageQueueGetCapacity` from the authenticated CMSIS-FreeRTOS v10.5.1
source. Four guarded complete-entry redirects replace 88 stock bytes with 84
source bytes plus four alignment bytes. Every direct dependency is already
source-owned, and the leaves never inspect the G2 112-byte TCB.

Apple Clang 21 closes at `132042/3655438/4433932`; Linux Clang 22.1.8 closes
at `133910/3657306/4435800`. The canonical package owns 132,773 source bytes,
93,428 generated bytes, and leaves 4,207,731 bytes opaque. See
`docs/research/cmsis-freertos-core-leaves-source-boundary-audit.md` for the
stock spans, dependency proof, hashes, and reproduction commands.

## Apollo-main CMSIS-FreeRTOS count-leaf milestone

`apollo_main/core_overlay/runtime_cmsis_count_leaves.c` adds bounded
Apache-2.0 implementations of `osSemaphoreGetCount` and
`osMessageQueueGetCount`. The two complete 36-byte stock entries redirect to
identical 36-byte unrelocated source bodies; all three outgoing edges bind to
the source-owned IRQ and normal/ISR queue-count providers. No TCB field is
read.

Apple Clang 21 closes at `132116/3655512/4434006`; Linux Clang 22.1.8 closes
at `133984/3657380/4435874`. The canonical package owns 132,845 source bytes,
93,430 generated bytes, and leaves 4,207,731 bytes opaque. See
`docs/research/cmsis-freertos-count-leaves-source-boundary-audit.md`.

## Apollo-main CMSIS-FreeRTOS queue-delete milestone

`apollo_main/core_overlay/runtime_cmsis_message_queue_delete.c` adds the
bounded Apache-2.0 `osMessageQueueDelete` wrapper. Its 36-byte target replaces
the complete 40-byte stock entry and calls only the source-owned IRQ classifier
and FreeRTOS `vQueueDelete` provider.

Apple Clang 21 closes at `132152/3655548/4434042`; Linux Clang 22.1.8 closes
at `134020/3657416/4435910`. Canonical package ownership is 132,881 source,
93,430 generated, and 4,207,731 opaque bytes.

## Apollo-main CMSIS-FreeRTOS four-leaf milestone

The current tranche adds bounded Apache-2.0 implementations of
`osThreadYield`, `osKernelGetState`, `osMutexDelete`, and
`osTimerIsRunning`. Their 138 complete stock bytes redirect to 126 source
bytes plus four alignment bytes, with all calls closed over already
source-owned providers. Apple Clang 21 closes at
`131758/3655154/4433648`; exact-root Linux Clang 22.1.8 closes at
`133626/3657022/4435516`. CMSIS production ownership is now thirteen public
APIs plus private `IRQ_Context`; 25 public APIs and four private helpers remain
stock-backed at that milestone.

## Prior Apollo-main CMSIS-FreeRTOS synchronization milestone

`apollo_main/core_overlay/runtime_cmsis_sync_ops.c` adds bounded Apache-2.0
implementations of `osMutexAcquire`, `osMutexRelease`, and
`osSemaphoreRelease`. The 270 complete stock bytes redirect to 220 source
bytes plus two alignment bytes, closing 292 external callers over the already
source-owned IRQ and FreeRTOS queue providers. Apple Clang 21 closes at
`131980/3655376/4433870`; exact-root Linux Clang 22.1.8 closes at
`133848/3657244/4435738`. CMSIS production ownership is now sixteen public
APIs plus private `IRQ_Context`; 22 public APIs and four private helpers remain
stock-backed at that milestone.

## Prior Apollo-main CMSIS-FreeRTOS timer-operation milestone

`apollo_main/core_overlay/runtime_cmsis_timer_ops.c` adds bounded Apache-2.0
implementations of `osTimerStart`, `osTimerStop`, and `osTimerDelete`. Their
220 complete stock bytes and 46 external callers redirect to 234 source bytes
plus four alignment bytes. The wrappers call only the already source-owned IRQ,
FreeRTOS timer-command/state/context, and heap-free providers, and preserve the
tagged callback-allocation ABI. Apple Clang 21 closes at
`132218/3655614/4434108`; exact-root Linux Clang 22.1.8 closes at
`134086/3657482/4435976`. CMSIS production ownership is now nineteen public
APIs plus private `IRQ_Context`; 19 public APIs and four private helpers remain
stock-backed.

## Prior Apollo-main CMSIS-FreeRTOS event-flags closure

`apollo_main/core_overlay/runtime_cmsis_event_flags.c` source-owns the complete
linked event-flags family: `osEventFlagsNew`, `osEventFlagsSet`,
`osEventFlagsClear`, and `osEventFlagsWait`. Their 388 complete stock bytes and
38 external callers redirect to 334 source bytes plus four alignment bytes.
Every fixed dependency is already source-owned, including task/ISR event-group
operations and the PendSV paths. Apple Clang 21 closes at
`132556/3655952/4434446`; exact-root Linux Clang 22.1.8 closes at
`134424/3657820/4436314`. CMSIS production ownership is now twenty-three public
APIs plus private `IRQ_Context`; 15 public APIs and four private helpers remain
stock-backed.

## Prior Apollo-main CMSIS-FreeRTOS timer-constructor closure

`apollo_main/core_overlay/runtime_cmsis_timer_new.c` source-owns public
`osTimerNew` and private `TimerCallback` as one tagged callback-record ABI.
Only the complete 232-byte public stock entry is redirected; the new
constructor stores the source callback, so the adjacent private stock helper
is unreachable from admitted timers while remaining intact as evidence. The
Apple bodies add 236 source bytes; Clang 22.1.8 emits a 248-byte equivalent.
Apple closes at `132792/3656188/4434682`; exact-root Linux closes at
`134672/3658068/4436562`. CMSIS production ownership is now twenty-four public
APIs plus private `IRQ_Context` and `TimerCallback`; 14 public APIs and three
private memory-pool helpers remain stock-backed.

## Current Apollo-main CMSIS-FreeRTOS memory-pool constructor closure

`apollo_main/core_overlay/runtime_cmsis_memory_pool_new.c` source-owns public
`osMemoryPoolNew` from the authenticated CMSIS-FreeRTOS v10.5.1 source. Its
complete 298-byte stock entry redirects to a 254-byte Apple leaf or 250-byte
exact-root Linux leaf. The adapter preserves the recovered 116-byte control
block, embedded static counting semaphore, storage ownership bits, 32-bit
rounding/wrap behavior, and the upstream undersized-buffer compatibility
quirks. All fixed calls resolve to existing source-owned IRQ, heap_4, and
queue-constructor providers. Apple closes at `133046/3656442/4434936`;
exact-root Linux closes at `134922/3658318/4436812`. CMSIS production
ownership is now twenty-five public APIs plus private `IRQ_Context` and
`TimerCallback`; 13 public APIs and three private pool helpers remain.

## Current Apollo-main FreeRTOS queue and CMSIS operation closure

`shared/freertos/runtime_freertos_queue_receive_from_isr.c` and
`runtime_freertos_queue_copy_data_from_queue.c` source-own the complete
V10.5.1 ISR receive path. `apollo_main/core_overlay/runtime_cmsis_semaphore_acquire.c`
then closes `osSemaphoreAcquire`, while
`runtime_cmsis_memory_pool_ops.c` closes both public pool operations and all
three private pool-list helpers. The subsequent send closure adds
`xQueueGenericSendFromISR`, `prvCopyDataToQueue`, and
`xTaskPriorityDisinherit`, admitting `osMessageQueuePut`. The task receive
closure adds `xQueueReceive`, `prvUnlockQueue`, `vTaskPlaceOnEventList`, and
`prvAddCurrentTaskToDelayedList`, admitting `osMessageQueueGet`. The following
delay and thread-priority pairs source-own `vTaskDelay`/`osDelay` and
`vTaskPrioritySet`/`osThreadSetPriority`. The next closed unit adds
`eTaskGetState`, `prvDeleteTCB`, `vTaskDelete`, and `osThreadTerminate`. The
thread-flags unit then adds all three V10.5.1 notification providers and the
two linked CMSIS wrappers while preserving the stock pre-`bb8a350a` wait loop.
Apple closes at `137090/3660486/4438980`; exact-root Linux closes at
`138970/3662366/4440860`. CMSIS production ownership is now 35 public APIs and
all five private helpers; three public APIs remain.

## Current G2 FreeRTOS TCB compatibility patch

`shared/freertos/g2-tcb-v10.5.1.patch` reduces the stock 112-byte TCB delta to
one explicit 32-bit field over authenticated FreeRTOS-Kernel V10.5.1. It adds
the creation stack depth after `pcTaskName[32]`, mirrors it in `StaticTask_t`,
and assigns it during task initialization. Applying the patch and compiling
for Cortex-M55 reproduces size `0x70` and all observed later trace, mutex,
notification, and provenance offsets. The vendor's original field name and
private patch commit remain unobservable; the reconstructed semantics and
upstream MIT base are kept distinct. See
`docs/research/freertos-g2-tcb-vendor-patch-audit.md`.

## Current CMSIS-FreeRTOS thread-creation closure

`apollo_main/core_overlay/runtime_cmsis_thread_new.c` source-owns the complete
200-byte stock `osThreadNew` entry. The Apache-2.0 wrapper is pinned to
CMSIS-FreeRTOS v10.5.1 commit `d213f261b5be6bb29a7cce8b84071706b72f4d53`
and calls the authenticated retained V10.5.1 `xTaskCreateStatic` and
`xTaskCreate` entries. It preserves the recovered G2 `StaticTask_t` threshold
`0x70` and 16-bit dynamic stack-depth ABI. Apple closes at
`137260/3660656/4439150`; exact-root Linux closes at
`139138/3662534/4441028`. CMSIS production ownership is now 36 public APIs and
all five private helpers; only the coupled kernel initialize/start pair
remains stock-backed.

## Current CMSIS-FreeRTOS kernel-lifecycle closure

`runtime_cmsis_kernel_lifecycle.c` atomically source-owns the final
`osKernelInitialize` and `osKernelStart` wrappers from CMSIS-FreeRTOS v10.5.1
commit `d213f261b5be6bb29a7cce8b84071706b72f4d53`. Both use the same fixed
`KernelState` word as the source-owned get-state wrapper. Initialization binds
only to source-owned IRQ/scheduler-state providers; start additionally calls
the authenticated retained FreeRTOS V10.5.1 `vTaskStartScheduler` span at
`[0x00454CEC,0x00454D7C)`. Apple closes at
`137368/3660764/4439258`; exact-root Linux closes at
`139248/3662644/4441138`. All 38 linked public CMSIS APIs and all five private
helpers are now production source-owned.

The retained scheduler provider now has a separate production-excluded
`runtime_freertos_task_start_scheduler.c/.h` adaptation pinned to authenticated
V10.5.1. It closes idle/timer creation and scheduler-state semantics under both
compiler profiles while leaving all G2 globals and the Apollo port explicit.
Production still retains the stock entry until those boot-critical seams can
be migrated and hardware-validated atomically.

Companion production-excluded candidates now close the exact 46-byte
`xPortStartScheduler` body and 88-byte G2 Apollo STIMER setup. They preserve
the two SHPR3 volatile updates, first-task tail topology, IRQ 32, compare A,
32-count/1,024-Hz tick, and saved-configuration merge. Apple/Linux function
bodies and relocations are pinned. Two further production-excluded candidates
close elapsed-tick/IRQ delivery and the complete tickless power path. They pin
the IRQ-32 vector, wrap quirk, compare re-arm, PendSV aggregation, abort/clamp,
pre/post hooks, optional WFI, and capped tick stepping under both profiles.
Every bounded STIMER algorithm is now represented; hardware and atomic
production integration remain.

`shared/freertos/runtime_freertos_task_switch_context.c/.h` is the companion
production-excluded candidate for the complete V10.5.1 generic context-switch
selector. It retains the G2 `0x70` TCB offsets, four-word stack guard, 56
ready lists, and 64-entry task-number trace ring. Host and dual-profile target
tests qualify the bounded algorithm; production still uses stock pending an
atomic kernel/port migration and hardware scheduling validation.
