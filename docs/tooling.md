# Reverse-engineering and rebuild tooling

For download terms, account requirements and cost of each item, see
[`tooling-availability.md`](tooling-availability.md).

This page lists the tools that the decompile-and-rebuild process relies on,
why each one is needed for these particular CPUs, and how it is pinned. The
aim is to rebuild every payload byte for byte. Tools that only show that code
behaves the same way are useful for review, but they do not satisfy that aim.

Versions and commits marked **[V]** were checked against the upstream remote on
2026-09-29 (`git ls-remote` or a shallow fetch of the object). Unmarked entries
are recommendations whose exact pin still has to be recorded the first time the
tool is installed. [`tools/bootstrap/`](../tools/bootstrap/README.md) records
those pins.

## 1. Payloads, cores and original compilers

Byte identity depends on knowing the exact compiler that built each payload, so
this table sets the tool requirements. Evidence and open questions are in
[`g2/docs/reference/toolchains.md`](../g2/docs/reference/toolchains.md) and
[`r1/docs/toolchain-and-dependencies.md`](../r1/docs/toolchain-and-dependencies.md).

| Payload | Core | Original compiler (evidence strength) | Licence of that compiler |
| --- | --- | --- | --- |
| G2 Apollo main application and Even bootloader | Ambiq Apollo510B, Cortex-M55 (Armv8.1-M, MVE/Helium, FPU) | IAR EWARM with the DLIB runtime; release 9.20 or later, with 9.60.2 the leading candidate (strong) | commercial |
| G2 EM9305 BLE controller | EM Microelectronic EM9305, Synopsys ARCv2 EM | Synopsys MetaWare T-2022.09 build 004 (LLVM 14.0.6), `-Os`, EM9305 SDK v4.2 archives (proven from archive `.comment`) | commercial |
| G2 GX8002 voice codec | NationalChip GX8002B, C-SKY CK804EF | C-SKY GCC lineage; exact release not established | GPL toolchain |
| G2 touch controller | Infineon PSoC 4000T CY8C4046FNI, Cortex-M0+ | GCC indicated by the runtime (exact release open) | free |
| G2 charging case | STM32G0B1-class, Cortex-M0+ | GCC with STM32CubeG0 HAL (family proven, release open) | free |
| R1 application and bootloader | Nordic nRF52840, Cortex-M4F | Arm Compiler 5 (armcc/armlink), shown by the `__main` and `__scatterload` runtime | commercial (Keil MDK) |

**Consequence.** Clang, which the old overlay work used, cannot reproduce IAR,
MetaWare or armcc output byte for byte. The original compilers have to be
installed locally, under the owner's licence, and fingerprinted. Nothing in
this repository downloads a licensed compiler. `tools/bootstrap/bootstrap.sh
--licensed` only detects an installed compiler and records its version and
binary hash.

## 2. Disassembly and decompilation

| Tool | What it provides here | Known gaps | Pin |
| --- | --- | --- | --- |
| Ghidra 12.1.x + JDK 21 | Headless analysis for Cortex-M55/M4F/M0+, FunctionID, BSim, Version Tracking, PyGhidra. The existing scripts are in [`g2/tools/ghidra_scripts/`](../g2/tools/ghidra_scripts) and [`r1/tools/ghidra_scripts/`](../r1/tools/ghidra_scripts). | 12.1.4 has no MVE/Helium or low-overhead-loop decode, and no ARC or C-SKY processor | release `Ghidra_12.1.4_build` = `8b6bbb857accdfa20dc5b2f5dea471178c2e9fbc` [V] |
| Ghidra ARC module | EM9305 | NSA pull request 3006 (`d3fbf109ada6d051750e973779170c1758622530` [V]) is still open and covers **ARCompact only**, not the ARCv2 EM core in the EM9305. No maintained public ARCv2 Ghidra module was found. Use IDA Pro's ARC module or `arc-elf32-objdump` for disassembly, or extend the SLEIGH to ARCv2 in a project-owned fork. | fork and extend |
| `ghidra_csky_WinnerMicro` | C-SKY processor module for the GX8002 | Written for WinnerMicro W80x (CK804); DSP instructions are partial | `0daaa056e8c570ba514fc0d0226384ecf9f9df05` [V] |
| GhidraSVD | Loads SVD register maps as typed peripheral blocks | — | tag `v0.6.6` = `893dfbe02d889dfb7c4cf69b7a395051a8307828` [V] |
| GNU binutils `objdump` (arm-none-eabi ≥ 2.35, arc-elf32, csky-elfabiv2) | The reference instruction decoder wherever Ghidra is weak (MVE, ARCv2 EM, CK804EF) | The C-SKY GX8002 decode needs the official `c-sky/binutils-gdb` fork (see [`g2/docs/reference/toolchains.md`](../g2/docs/reference/toolchains.md)) | Arm GNU Toolchain 13.3.Rel1 and 9-2020-q2; Synopsys ARC GNU `arc-2026.03-release`; C-SKY `csky-script-3_2_0-release` = `96f037d8` [V] |
| rizin 0.9.1 + rz-ghidra 0.9.0 | Fast raw inspection and scripting | — | `c3a90e92` / `999df7b8` [V] |
| IDA Pro 9 + Hex-Rays, Binary Ninja | Optional second opinions; IDA has an ARC module and FLIRT | Commercial; not reproducible in CI | document only |

### FunctionID, BSim and signature databases

Building FunctionID and BSim databases from the pinned upstream sources and
libraries gives the most leverage. It names library code automatically and
narrows the compiler and options. Build one database per compiler and option
set, because the hashes depend on both. Inputs:

- IAR DLIB libraries from the licensed EWARM install (Apollo);
- AmbiqSuite 5.1.0 HAL/NemaGFX objects, Cordio, FreeRTOS, LVGL, littlefs,
  nanopb, FreeType and the other identified libraries (see
  [`third-party/README.md`](../third-party/README.md));
- EM9305 SDK v4.2 archives (MetaWare);
- NationalChip `lvp_kws` and gxDNN objects (GX8002);
- Infineon PDL/CAPSENSE (touch) and STM32CubeG0 at candidate tags (case);
- nRF5 SDK 17.1.0 with S140 7.2.0 (R1).

The databases are local build products under `build/`. The recipes belong in
the repository.

## 3. Byte-matching workflow

These are the tools that "matching decompilation" projects use. Their whole job
is to reach identical bytes, one function at a time.

| Tool | Role | Pin |
| --- | --- | --- |
| decomp-permuter | Randomly perturbs a C function until the original compiler emits the target bytes. It works with any compiler that can be scripted, including IAR, MetaWare and armcc. | `059609d4aec73eb0650726772954e1ad575825f8` [V] |
| asm-differ | Objdump-driven diff of target against built code for one function. Because it calls objdump, it extends easily to `arc-elf32-objdump` and `csky-elfabiv2-objdump`. | `0dd09af8f8008f1f880327cf0aca3b26d2562ea2` [V] |
| objdiff / objdiff-cli | Relocation-aware diff at object level, with a JSON progress report for CI. ARM support is aimed at older cores, so try it on the Cortex-M0+ payloads (touch, case) first. | `v3.8.1` = `fba10a617154f19b3fc25c8817dc81f81d8489b5` [V] |
| decomp.me (self-hosted) | Shared scratch space for difficult functions. It can use licensed compilers only on a private instance. | document only |
| Project splitter (to be written) | Emits per-function `.s`/`.c` stubs and a linker script that reproduces the stock placement, driven by the frozen pseudocode index and [`g2/symbols/`](../g2/symbols). This is the equivalent of splat for these targets. | in repository, after the freeze |

## 4. Register maps (SVD)

| Device | Source |
| --- | --- |
| Apollo510 / Apollo510B | CMSIS pack `AmbiqMicro::Apollo_DFP` 1.6.0 (`SVD/apollo510.svd`; anonymous download from download.ambiq.com) |
| PSoC 4000T | `devices/svd/psoc4000t.svd` in Infineon `mtb-pdl-cat2` (submodule `third-party/upstream/infineon-mtb-pdl-cat2`) |
| STM32G0B1 | ST `STM32G0B1.svd` via the ST pack or `cmsis-svd-data` |
| nRF52840 | `modules/nrfx/mdk/nrf52840.svd` in the nRF5 SDK 17.1.0 archive ([`third-party/fetched/`](../third-party/fetched)) |
| EM9305, GX8002 | No public SVD. Label them from vendor SDK headers (EM9305 SDK, `lvp_kws`) |

## 5. Emulation and dynamic analysis

| Tool | Relevance |
| --- | --- |
| G2 firmware emulator (`PaulMcMillan/g2-firmware-emulator`) | The project's chosen G2 simulator/emulator for testing, debugging and validating rebuilt images before they go on a device. It is not publicly reachable from this environment, so it has not been added yet; see [`third-party/README.md`](../third-party/README.md#g2-firmware-emulator). |
| Unicorn 2.1.4 | Differential execution of stock and rebuilt Thumb functions. No MVE, ARC or C-SKY. |
| Renode 1.17.0 | Has an nRF52840 platform, which suits R1 application, bootloader and SoftDevice bring-up. Ambiq support covers only Apollo4 Blue, so an Apollo510 `.repl` would have to be written. |
| XuanTie QEMU (`3287d345c7f5d60d5c8774d90752f5f710744f85` [V]) | Candidate C-SKY semantics oracle for the GX8002. Current XuanTie QEMU builds target RISC-V, and CK804 support is unconfirmed. Otherwise rely on `csky-elfabiv2` binutils and manual trace review |
| Synopsys ARC QEMU | ARCv2 EM semantics oracle for the EM9305 |
| angr 10 | Optional symbolic equivalence checks on Thumb code |

## 6. Containers, diffing and reproducibility

- **Kaitai Struct** (compiler 0.11): write formal `.ksy` specifications for
  EVENOTA, FWPK, the EM9305 record package, the case `EVEN` wrapper and the
  GX8002 BINH image, based on [`g2/docs/reference/firmware-formats.md`](../g2/docs/reference/firmware-formats.md).
  These specifications make the "account for every non-code byte" gate
  testable.
- **unblob / binwalk**: find nested assets.
- **diffoscope**: recursively diff a rebuilt bundle against the official one.
- **BinDiff 8 + BinExport**, **Diaphora**: match functions between the stock
  and rebuilt ELF files and transfer names.
- **LIEF**: ELF and section surgery in packaging scripts.
- Deterministic builds: `SOURCE_DATE_EPOCH`, `ar D`, and fixed paths through
  `-fdebug-prefix-map` or the compiler's equivalent option.

## 7. Hardware, radio and debug

These tools are documented only; they are not pinned.

- **Debug probes:** SEGGER J-Link (Ambiq, Nordic, ST, Infineon), pyOCD 0.45.1
  with the device packs, OpenOCD 0.12.0 (nRF52, STM32G0, PSoC 4; Apollo5 is not
  supported upstream).
- **BLE:** nRF Sniffer for Bluetooth LE with Wireshark 4.x; Android
  `btsnoop_hci.log` captures; nRF Connect.
- **Logic analyser:** needed for the pins, bus speeds and signalling that
  are still unmeasured and listed in
  [`docs/hardware/README.md`](hardware/README.md#open-questions).

## 8. Where each tool comes from

| Class | Items |
| --- | --- |
| Git submodules (`third-party/tools/`) | asm-differ, decomp-permuter, GhidraSVD, ghidra_csky_WinnerMicro; still to add: the Ghidra ARC module (after forking) and the G2 firmware emulator |
| `tools/bootstrap/` (pinned download and hash check) | Ghidra + JDK, rizin + rz-ghidra, Arm/ARC/C-SKY binutils and GCC, objdiff-cli, Renode, XuanTie QEMU, Python analysis environment (capstone, unicorn, lief, kaitaistruct, unblob, diffoscope), pyOCD, CMSIS packs |
| Documented only (licensed or proprietary) | IAR EWARM, Synopsys MetaWare, Keil MDK / Arm Compiler 5, J-Link, IDA, Binary Ninja, nRF Sniffer, the full AmbiqSuite 5.1.0 SDK, the official EM9305 SDK v4.2 |
