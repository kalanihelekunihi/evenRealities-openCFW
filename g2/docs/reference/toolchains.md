# G2 toolchains and runtimes by payload

This document records what is known about the compiler, runtime, and link
configuration of each payload in `s200_v2.2.6.10`. It also records what is
still missing for a byte-identical rebuild.

Citations are `path:line` at commit `832137ec`. Confidence levels:

- **Proven**: byte or hash evidence.
- **Strong**: several independent indicators.
- **Inferred**: one indicator.
- **Unverified**: not checked.

A rule applies to every row below. When modern Clang or GCC reproduces a single
small leaf body byte-for-byte, that does not identify the original compiler.
The legacy campaign reproduced many short bootloader leaves with Apple
Clang 21 and Linux Clang 22 (for example
`g2/docs/research/g2-bootloader-dfu-image-crc-check-42d890-source-closure.md:3-5`).
Those images were nevertheless built with IAR.

## Summary

| Payload | Compiler family | Exact release | Runtime library | Confidence |
|---|---|---|---|---|
| Apollo main | IAR Embedded Workbench for Arm (ICCARM/ILINK) | unknown; practical floor 9.20; 9.60.2 is the leading candidate | IAR DLIB (`dl7M_tl{n\|f}`, `m7M_tl{v\|s}`, `rt7M_tl` family) | family Proven, release Unverified |
| Apollo bootloader | IAR (same project family) | unknown | IAR DLIB/CLIB C11 runtime pieces | Strong |
| EM9305 | Synopsys MetaWare ARC (LLVM-based) | T-2022.09 build 004, LLVM 14.0.6, EM-Micro ARCv2 EM, `-Os` (SDK archives) | MetaWare runtime (SDK `MW_VERSION=2019.09` runtime directory) | Proven for SDK objects; the vendor's own objects are Inferred |
| GX8002 | C-SKY GNU (`csky-abiv2-elf-`), `-mcpu=ck804ef`, hard float | unknown | SDK `utility/libc` (tinyprintf and others), newlib-lineage libm, libgcc | family Strong, release Unverified |
| Touch (PSoC 4000T) | GNU Arm GCC plus newlib | unknown | newlib | Strong (idioms only) |
| Case (STM32G0) | GNU Arm GCC plus newlib | unknown | newlib; STM32CubeG0 HAL; FreeRTOS GCC `ARM_CM0` port | Strong |

## 1. Apollo main: IAR EWARM with DLIB

### Evidence

**Project path** (Proven). Every retained source path is rooted at
`D:\01_workspace\s200_ap510b_iar_git\`
(`g2/docs/research/iar-dlib-runtime-census.md:9-12`;
`g2/docs/research/apollo-embedded-source-path-census.md:8-13`). The same root
appears in the Cordio `__FILE__` strings
(`g2/docs/research/cordio-ble-stack-identity-audit.md:21-24`).

**No release string** (Proven). The image contains no IAR, ICCARM, EWARM, or
DLIB version string (`g2/docs/research/iar-dlib-runtime-census.md:10-12`).

**Build banners** (Proven). Three banners read `Jul  6 2026`, at times
21:37:30, 21:37:47 and 21:37:52. They are stored at `0x0078A3AC`,
`0x0078B594` and `0x0078B984` (`iar-dlib-runtime-census.md:14-19`).

**FreeRTOS port** (Strong). The FreeRTOS port matches
`portable/IAR/ARM_CM55_NTZ/non_secure` with `configENABLE_MPU=0` and no
TrustZone (`g2/docs/research/freertos-g2-config-port-audit.md:12-22,111-144`).

**IAR-style startup** (Strong). Startup runs a scatter/decompress table: the
table is at `0x0075D3C8` and holds a compressed initializer stream that loads
ITCM (`g2/docs/memory-map.md:1328-1336`).

**DLIB formatted I/O** (Proven identity). The DLIB formatted-I/O cluster is
present. It includes:

- `printf_core` at `0x00481836`, 3,256 B;
- `scanf_core` at `0x004D1638`, 2,778 B;
- `strtod`;
- Annex-K `printf_s`/`scanf_s` diagnostics;
- the IAR `q`/`L` length modifiers.

Sources: `g2/docs/research/g2-iar-dlib-format-io-recovery.md:33-46,74,123-172`.

**DLIB runtime units** (Proven identity; release not identified). Thirteen
bounded units are recorded
(`iar-dlib-runtime-census.md:64-79`;
`g2/docs/research/iar-dlib-frexpf-ldexpf-recovery.md:9-43`):

- `__aeabi_memmove`;
- VFP `sqrtf`;
- `__aeabi_memcpy`, public entry and aligned interior entry `0x00439C04`;
- the EDOM (33) and ERANGE (34) setters;
- the errno accessor (`errno @ 0x20074F14`);
- `frexpf`, its helper, and `ldexpf`;
- 64-bit `__aeabi_{u}ldivmod` and wrappers.

The memory routines use a void-EABI calling convention.

**Library by-products** (Proven identity):

- The mpaland/printf formatter lineage, commit `d3b98468`, is linked
  separately for application logging. It carries G2 `%PV`/`%pV` extensions
  (`g2/docs/research/third-party-utility-gap-priority.md:168`).
- The Nema/NemaVG GPU objects in stock use IAR code generation. The public
  AmbiqSuite packages ship only GCC archives, so the public archives cannot be
  linked as-is (`g2/docs/research/nemagfx-ambiq-g2-provenance-audit.md:28-35`).

### Release and variant inference

These are Inferred (`iar-dlib-runtime-census.md:21-60,136-147`):

- **Release floor.** Cortex-M55 support first appears in EWARM 9.20, so 9.20
  is the practical floor.
- **Release candidates.** Try 9.60.2 first; Ambiq's own Apollo510 /
  AmbiqSuite 5.3 environment names ICCARM 9.60.2. Then 9.60.3, 9.70.x, and
  9.50.x.
- **Archive family.** The code is Thumb, little-endian, and VFP. It uses
  absolute errno literals, so it is non-RWPI and not `7Mx`. That gives:
  - math `m7M_tl{v|s}.a`;
  - runtime `rt7M_tl.a`;
  - C library `dl7M_tl{n|f}.a`.
- **Unresolved variants.** Two choices remain open:
  - Normal or Full DLIB configuration;
  - full VFP or single-precision-only math.
- **Best discriminators.** For release selection, compare `sqrtf` and the errno
  helpers against real EWARM archives. No EWARM archive or `iccarm` has been
  available for comparison so far.

Corpus evidence is in `g2/research/corpus/iar/`:

- `math-errno/` holds stock and recreated `sqrtf`/errno objects and an
  emulator;
- `memory-qualify/` holds the stock memory island and recreated memcpy/memmove;
- `runtime-shards/` holds 16 Ghidra shards of the early runtime island.

### Other ABI facts affecting byte equality

**Enum and pointer size** (Strong). The ABI uses short enums and 32-bit
pointers. Both LVGL and FlashDB layouts require
`-fshort-enums`-compatible behavior
(`g2/third_party/lvgl/g2-config/lvgl_g2_abi.json`, `target.enum_abi`;
`g2/third_party/flashdb/g2-config/fdb_cfg.h:24-26`).

**Floating point** (Strong).

- Hard-float VFP with the `s0` ABI (`iar-dlib-frexpf-ldexpf-recovery.md:13-16`).
- Floating-point code does not introduce `__aeabi_f2d`/`d2f` helpers
  (`iar-dlib-runtime-census.md:82-84`).

**MVE** (Unverified). `configENABLE_MVE` is unresolved; the FreeRTOS port
assembly is identical either way
(`freertos-g2-config-port-audit.md:254-261`).

## 2. Apollo bootloader

This section is Strong. Evidence that the bootloader was also built with IAR:

- It has an IAR thread-pointer/TLS leaf that returns the SRAM anchor
  `0x20000518` (`g2/docs/memory-map.md:4371-4377`).
- It contains the string `"constraint handler: bad message"`, from the IAR C11
  runtime constraint handler (a constraint dispatcher at `0x422590`), plus
  `memchr`, double-precision helpers, and 64-bit divmod
  (`g2/docs/research/g2-bootloader-bl006-retained-seam-survey.md:147-150`;
  `g2/docs/memory-map.md:4340-4395`).
- Its introspective qsort and Floyd heap-sift runtime match a C library
  implementation (`g2/docs/memory-map.md:4527-4541`).

The bootloader carries its own copies of several libraries, and they are not
proven to be the same compilation as main:

- littlefs 2.10.1;
- EasyLogger 2.2.99 (`elog.c` and `elog_utils.c` only);
- TLSF;
- the AmbiqSuite 5.1.0 MSPI HAL;
- FreeRTOS with a CMSIS-RTOS2-style wrapper.

Sources: `g2/docs/upstream-inventory.md:817-820`;
`g2/docs/research/peripheral-oss-library-provenance-audit.md:26-28`. The
bootloader's FreeRTOS revision is **not** inherited from main (Unverified).

## 3. EM9305: Synopsys MetaWare ARC

**Compiler identity** (Proven). The `.comment` sections of the authenticated
SDK v4.2 archives read: MetaWare ARC Compiler **T-2022.09 build 004**,
**LLVM 14.0.6**, EM-Micro target, ARCv2 EM, **`-Os`**
(`g2/docs/research/em9305-sdk-archive-match-audit.md:37-42`;
`g2/docs/memory-map.md:1792-1795`). The SDK's `MW_VERSION=2019.09` selects
only the bundled runtime-library directory; it is not the compiler version
(`em9305-sdk-archive-match-audit.md:40-42`).

**SDK oracle** (Proven hashes; not an authoritative source). The SDK v4.2
reference is the third-party public mirror `github.com/C0R3YY2/em9305_original`
at commit `e4412bc98d4e76d441d1226ca3696e53cfae5f54`, tree
`f5cb9ba00df71c2612d6d64cf39e05615a2feb64`
(`g2/docs/research/em9305-sdk-link-order-recovery.md:67-69`;
`g2/docs/research/em9305-qpc-arcompact-audit.md:413`). The mirror has no
repository license. Some Packetcraft files carry confidential notices
(`em9305-sdk-archive-match-audit.md:116-119`;
`g2/docs/research/em9305-expanded-sdk-archive-census.md:157-160`).

**Archive coverage** (Proven). Relocation-normalized comparisons match exact
bodies from 48 archives:

- 1,494 functions / 157,122 bytes of the 210,888-byte application
  (74.50%);
- 167,684 bytes (79.51%) once function provenance is included.

Sources: `em9305-expanded-sdk-archive-census.md:6-9,49-68`.

The key archives are:

| Archive | Git blob |
|---|---|
| `lib_emb_controller.a` | `6a1a8e3d…` |
| `lib_emb_controller_iso.a` | (ISO controller variant) |
| `lib_QPC.a` | `26fc11bf…` |
| `lib_pml.a` | — |
| `lib_sleep_manager.a` | — |
| `lib_sleep_timer.a` | — |
| `lib_prot_timer.a` | — |
| `lib_unitimer.a` | — |
| `lib_em_system_di03.a` | — |
| `lib_aoad.a` | — |

Sources: `em9305-sdk-archive-match-audit.md:28-35`;
`em9305-expanded-sdk-archive-census.md:80-121`.

**Link order** (Strong). Symbol order in `lib_emb_controller_iso.a` is 99.6%
monotonic with stock addresses. This is consistent with a final placement
sorted by `.text.*` section name
(`em9305-sdk-link-order-recovery.md:5-10`). The ledger records 202 link-order
placements, 50 of them exact. There are also 51 same-size or size-delta
vendor-modified functions (`em9305-expanded-sdk-archive-census.md:186-193`).

**Vector table** (Proven). ARC IRQ entries start at vector word 16
(`em9305-sdk-link-order-recovery.md:66-81`).

**Runtime helpers** (Strong). The residual MetaWare runtime islands have a
clean-room candidate, but the exact MetaWare EABI helper names and ABI remain
unconfirmed (`g2/docs/research/em9305-metaware-runtime-islands-candidate.md:11-26,65-74`).

## 4. GX8002 codec: C-SKY GNU

### What is known

**SDK build settings** (Strong). The public NationalChip `lvp_kws` SDK is at
commit `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`. Its Makefile selects:

- the `csky-abiv2-elf-` toolchain prefix;
- `-mcpu=ck804ef`;
- hard float;
- prebuilt driver, speech, decoder, and DSP libraries; `drivers_lib/` holds
  relocatable C-SKY objects.

Source: `g2/docs/research/gx8002-upstream-object-candidates.md:5-15`.

**Precompiled object matches** (Strong identity). Of 151 eligible SDK object
sections, 102 match stock occurrences. They carry 68 distinct symbols and cover
5,374 bytes (`gx8002-upstream-object-candidates.md:25-38`).

**Build banners** (Proven). Each BINH image carries an
`[LVP]Copyright (C) 2001-2020 NationalChip` banner and the board string
`grus_gx8002b_dev_1v`. The build dates are:

| Image | Build date |
|---|---|
| A | `2026-03-26, 17:07:25` |
| B | `2026-03-26, 17:07:19` |

Source: `g2/docs/research/peripheral-oss-library-provenance-audit.md:82-89`.

**Codec stage 1** (Strong family). Codec stage 1 contains a U-Boot-derived
simple CLI core (`peripheral-oss-library-provenance-audit.md:19,103-108`).

**CRT0** (Proven). All four reset entries share the canonical GX8002 CRT0
sequence (`g2/docs/research/g2-codec-stage2-sections-recovery.md:27-31`).

### Disassembly and analysis tools

These are Proven as working tools:

- **Disassembler.** Use the C-SKY binutils fork `github.com/c-sky/binutils-gdb`
  at commit `2409f5af709d5fef4f41cbeb30ef59bc1046b252`, built as
  `csky-elfabiv2-objdump` (`g2-codec-stage2-sections-recovery.md:13-23`).
  - Upstream GNU binutils 2.43.1 mis-decodes the 32-bit forms
    (`mtcr`, `bsr`, `lrw`).
  - Capstone and LLVM have no C-SKY target.
- **Native compiler build.** `g2/tools/build_g2_csky_macos.py:18-24,42-55`
  builds binutils and a GCC for `csky-unknown-elf` from pinned revisions:

  | Component | Revision |
  |---|---|
  | build-scripts repository (`c-sky/toolchain-build`) | `20c6b74f00ac3f464cb43ef2189a069d656933d5` |
  | binutils | `32f97f3473656ee5d64e8e8c01a6006312c5828a` |
  | GCC | `1e9b70447a8417f5c692370de4533e43d754e8fa` (13.0.1) |

  The GCC is configured with `--with-cpu=ck804ef --with-endian=little
  --with-float=hard --with-newlib --without-headers`. Libgcc was later built
  from the same GCC commit (`g2/docs/source-only-goal.md:6485-6496`).
- **macOS host fix.** `g2/tools/toolchain-patches/gcc-safe-ctype.patch` is the
  unmodified upstream GCC commit `9970b576`. It is a macOS build fix only
  (`g2/tools/toolchain-patches/README.md:1-20`).
- **Candidate compile flags.** Current candidates compile with:

  ```
  -Os -mcpu=ck804ef -mhard-float -ffreestanding -fno-builtin
  -ffunction-sections -fdata-sections -fwrapv
  ```

  (`g2/tools/build_gx8002_tinyprintf_candidate.py:21-22`). These are chosen
  settings, not recovered vendor flags.

### Runtime-library findings

These affect byte equality.

**tinyprintf** (Strong). The formatter is the SDK `utility/libc/tinyprintf.c`.
Stock `putchw` fits a 212-byte envelope only with a loop-shape edit
(`g2/tools/upstream-patches/tinyprintf-padding-loop.patch`) plus
`-fno-tree-loop-optimize`, giving 204 bytes. The stock compiler therefore
differs from the pinned GCC 13 in loop code generation
(`g2/docs/research/gx8002-printf-recovery.md:96-109`).

**libm scaling** (Strong). Stock `scalbnf` uses the underflow cutoff
`exponent < -22`. That is newlib's `FLT_SMALLEST_EXP -22` from
`fdlibm.h`/`sf_scalbn.c` (newlib mirror commit `4aa696c8`), which gives a
newlib libm lineage
(`g2/components/shared/gx8002/scalbnf-underflow-correction.md:1-28`).

**libgcc** (Strong). The binary64 soft-float helpers come from GCC
`libgcc/fp-bit.c` (for example `__fixunsdfsi`, `_fpadd_parts`). They match
the pinned GCC commit's source (`g2/docs/source-only-goal.md:13481,13553`).

**fp-bit correction patch.** `g2/components/shared/gx8002/gcc-fp-bit-sticky-rounding.md`
documents a local correction that intentionally differs from stock. It must
**not** be used for a byte-equal build.

## 5. Touch: PSoC 4000T

The toolchain family is GNU and is Strong from idioms only
(`g2/docs/research/g2-touch-identity-recovery.md:56-61,176-177`):

- a GCC/newlib startup, with init-array iterators at `0x00C0`;
- the GCC `mov pc, r3` switch idiom;
- EasyLogger-style log strings (firmware `2.2.0.1`).

No library is positively identified. Whether the build used ModusToolbox/PDL
or bare metal is unresolved. No compiler version evidence has been recovered
(`g2/docs/research/peripheral-oss-library-provenance-audit.md:23`).

## 6. Case: STM32G0

The toolchain is GNU Arm GCC with newlib (Strong)
(`g2/docs/research/g2-box-stm32g0-platform-recovery.md:54-80,98-116`).

**Startup.** The startup chain matches GNU/newlib:

1. reset trampoline at `0x08000144`;
2. `SystemInit`;
3. `_start`.

**FreeRTOS.** The kernel is FreeRTOS with the **GCC** `ARM_CM0` port.

- `xPortPendSVHandler` is instruction-identical to the upstream `port.c`.
- The SVC vector is a bare `bx lr`, which excludes the IAR port.
- The kernel is V10.x (V10.0.0–V10.6.x). The likely range is V10.3.1–V10.5.1
  via STM32CubeG0; this is Inferred.

**HAL.** The HAL lineage is STM32CubeG0 HAL/LL. It has no version strings.

**Version.** The case firmware is version 1.2.57.

## Open questions blocking byte equality

1. **Apollo IAR release and configuration.** The following are unknown:
   - the exact EWARM/ICCARM/ILINK version;
   - the DLIB configuration (Normal or Full), and the math variant (VFP or
     single-precision);
   - per-file optimization levels and flags;
   - the `.icf` linker configuration;
   - the object and library link order;
   - the scatter/initializer compression choices.

   Real EWARM archives are needed for any comparison
   (`iar-dlib-runtime-census.md:133-147`).
2. **Apollo precompiled vendor objects.** The following were linked as IAR
   objects of unknown provenance:
   - the NemaGFX/NemaVG libraries and the GPU patch (the public packages ship
     only GCC archives);
   - the proprietary AmbiqSuite Cordio WSF/HCI port archive (the AmbiqSuite
     2.5.1-family port `87b03680…`);
   - private AmbiqSuite 5.1.0 pre-release HAL sources
     (`nemagfx-ambiq-g2-provenance-audit.md:28-35`;
     `third-party-utility-gap-priority.md:154,159,173`).
3. **Apollo vendor patches and generated inputs.** Several inputs are vendor
   forks or generated files:
   - the LVGL tree is a hybrid fork, and its private display port is not
     public;
   - the Cordio tree carries rebased Ambiq patches;
   - FreeRTOS carries a TCB patch (recovered; see `config-recovered/`);
   - generated nanopb `.pb.c` files, fonts, images, UI assets, and the
     FreeType/LVGL configuration are all inputs;
   - none of these is present as source.
4. **Bootloader.** The same IAR unknowns apply. In addition, its FreeRTOS
   revision and configuration are independent of main and unrecovered.
5. **EM9305.** Several items block a rebuild:
   - it needs a licensed MetaWare T-2022.09 installation;
   - it needs the SDK v4.2 archives, which are not redistributable;
   - it needs vendor sources for about 25% unmatched bytes, including
     modified controller functions;
   - the linker script and exact archive set/order are unknown;
   - it is unconfirmed whether vendor objects used the same flags as the SDK.
6. **GX8002.** The build depends on several unknowns:
   - the exact NationalChip C-SKY GCC release and its libc/libm/libgcc builds
     (tinyprintf code generation shows the pinned GCC 13 differs);
   - the prebuilt SDK driver, speech, decoder, and DSP libraries;
   - the private `lvp_kws`-derived application;
   - the U-Boot-derived stage-1 CLI source;
   - the trained KWS model: 9,164-byte command stream and 120,800 weights.
7. **Touch.** The build depends on several unknowns:
   - the GCC and newlib versions;
   - whether ModusToolbox/PDL was used;
   - the CapSense configuration and tuning tables;
   - the extent of the resident flash region.
8. **Case.** The build depends on several unknowns:
   - the GCC and newlib versions;
   - the STM32CubeG0 HAL version;
   - the FreeRTOS point release and configuration;
   - the linker script (initial SP `0x20002C88` is not the top of RAM).
9. **Checkout identity (all payloads).** For most libraries the exact private
   checkout is binary-unobservable. Only a compatible commit interval is known;
   see [libraries.md](libraries.md). A byte-equal build therefore needs a
   selected commit per library whose compiled bodies match. Identity alone is
   not enough.
