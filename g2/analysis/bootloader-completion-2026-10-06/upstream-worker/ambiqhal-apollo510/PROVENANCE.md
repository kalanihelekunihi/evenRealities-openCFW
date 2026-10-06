# Apollo510 MSPI HAL source candidate

## Acquisition and identity

This directory contains an auditable source closure for the public Ambiq Apollo510 MSPI HAL. The source origin is the repository gitlink recorded in this checkout:

- Repository: `https://github.com/AmbiqMicro/ambiqhal_ambiq`
- Exact gitlink: `5efc0228528a8adce5eae0d226fac85d2551eb3b`
- Release marker in source: `release_sdk5p1p0-366b80e084`
- Downloaded archive: GitHub codeload archive for that exact commit
- Archive SHA-256: `d3c76022eb38fe04e3f55b056fcdfa1ce8911ccf816c62cd0e9f86f5e7c3db35`

The target source files are `ambiqhal/mcu/apollo510/hal/mcu/am_hal_mspi.c` and `.h`. The `.c` source itself identifies the SDK 5.1.0 release lineage. The repo-pinned gitlink was checked with `git ls-tree HEAD third-party/upstream/ambiqhal-apollo510`; it was not initialized or changed. Source copy hashes and per-file upstream paths are recorded in `FILE-PROVENANCE.tsv` and `SHA256SUMS`.

The source and its included Ambiq headers carry Ambiq Micro 2025 copyright notices and BSD 3-Clause license text in-file. The checkout has no top-level Ambiq license file. The header include closure reaches 70 Ambiq headers because the official `am_mcu_apollo.h` umbrella includes the full HAL surface. Only one Ambiq C translation unit was copied: `am_hal_mspi.c`. The imported CMSIS 5 dependency is separately pinned to the existing CMSIS 5.9.0 commit `2b7495b8535bdcb306dac29b9ded4cfb679d7e5c`; its 7 required headers and `LICENSE.txt` have Apache-2.0 attribution in `FILE-PROVENANCE.tsv`.

This is a bounded public HAL source candidate, not a full AmbiqSuite SDK import. It does not include SBL source, ROM implementation, IAR runtime, or unrelated peripheral `.c` implementations.

## Build check

The MSPI translation unit compiles as a freestanding ARM object with the available Clang compiler and Cortex-M55 target:

```sh
clang --target=arm-none-eabi -mcpu=cortex-m55 -mthumb -std=c99 -O0 \
  -ffreestanding -fno-builtin \
  -I ambiqhal/mcu/apollo510 \
  -I ambiqhal/CMSIS/AmbiqMicro/Include \
  -I cmsis-5-590/CMSIS/Core/Include \
  -c ambiqhal/mcu/apollo510/hal/mcu/am_hal_mspi.c -o am_hal_mspi.o
```

Status: successful, ELF 32-bit little-endian ARM EABI5 relocatable object. Object SHA-256 from the successful run: `c4795a2ec817d91c01588d8b732b171092ce1da447076b8d22e7cda6285db3a0`. This checks syntax, headers, and ARM code generation only. It does not reproduce the IAR build flags, target executable bytes, complete link, or runtime behavior.

`arm-none-eabi-nm -u` reports unresolved external dependencies on clock-manager request/release, command-queue allocation/enable/status/post/recovery/termination APIs, delay helpers, interrupt master disable/set, and peripheral power enable/disable. Those dependencies identify the next platform boundary; this acquisition intentionally does not add their implementation translation units. They must be satisfied by the actual pinned project/platform sources or explicit interfaces before this candidate can link.

## Target correspondence and limits

The bootloader analysis attributes these named target routines to the MSPI HAL:

| Target symbol | Firmware range | Size | Public candidate |
|---|---:|---:|---|
| `initialize` | `0x00424A5A–0x00424AE9` | 144 B | `am_hal_mspi_initialize` |
| `configure` | `0x00424AF0–0x00424BD3` | 228 B | `am_hal_mspi_configure` |
| `interrupt_clear` | `0x00426506–0x00426535` | 48 B | `am_hal_mspi_interrupt_clear` |
| `interrupt_service` | `0x00426536–0x0042661F` | 234 B | `am_hal_mspi_interrupt_service` |
| `power_control` | `0x00426808–0x00426BFD` | 1014 B | `am_hal_mspi_power_control` |

The raw decompiler extracts are under `g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/decomp/` (files `00424a5a.c`, `00424af0.c`, `00426506.c`, `00426536.c`, `00426808.c`). They are raw analysis evidence, not reviewed source. Consolidated evidence in `g2/docs/reference/libraries.md:237` marks `am_hal_mspi_interrupt_clear` as an exact translation-unit leaf and `interrupt_service`/`power_control` as Strong attribution. The public source contains the named routines, but the service and power paths have target-specific helper routes and are not exact-body claims. No IAR object or full executable byte comparison was performed. `initialize` and `configure` are useful source candidates, but matching names and decompiler attribution alone do not prove exact source/build equivalence.

The strongest immediate reuse is the public HAL register/protocol implementation and its interrupt-clear leaf. The exact original executable still requires recovered startup/linker/runtime inputs and exact IAR settings; this source candidate alone cannot prove byte identity. It also does not supply ROM or proprietary IAR runtime code.

## Audit commands

```sh
sha256sum -c SHA256SUMS
```

`FILE-PROVENANCE.tsv` records each copied file's repository-relative upstream path, exact source commit, SHA-256, owner/copyright notice, license marker, and release marker.
