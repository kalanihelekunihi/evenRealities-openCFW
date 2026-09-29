# Missing toolchain components and component blockers

This file lists every part of the firmware whose byte-identical reconstruction
is gated by a tool, compiler or vendor object that the project does not yet
have. The rest of the work continues with open-source tooling in the meantime.

Two rules apply:

1. **Work continues around a blocker.** Decompilation, review, library
   identification and container work use open tools: Ghidra, GNU binutils
   and GCC, the ARC and C-SKY GNU toolchains, BinDiff, rizin and Unicorn.
   Only the steps that need the missing component wait.
2. **Blocked code is pulled forward as cut binary.** A payload region that
   cannot yet be rebuilt from source is cut from the official image and
   carried as a *retained segment*. Region manifests (see
   [`firmware cutting`](#firmware-cutting-and-retained-segments) below)
   describe the segments. Each retained segment names its blocker ID from the
   table below. The rest of the image can then be rebuilt, reassembled and
   checked byte for byte. Retained segments never count toward source
   completeness or the final byte-identity goal. They are listed debt, and
   are removed once their blocker clears.

Availability and access terms for each missing item are in
[`docs/tooling-availability.md`](docs/tooling-availability.md).

## Blocker register

| ID | Missing component | Kind | What it blocks | What still proceeds with open tools | Clears when |
| --- | --- | --- | --- | --- | --- |
| `TC-IAR` | IAR EWARM with DLIB. 9.60.2 is the candidate; the floor is 9.20 | licensed compiler | byte-matching C for the G2 Apollo main application and Even bootloader, including the upstream libraries IAR compiled into them (FreeRTOS, Cordio, LVGL, littlefs, nanopb, FreeType, liblc3, LZ4, ...) and the IAR DLIB runtime | full decompilation in Ghidra; review and freeze; upstream identification by strings, source paths and GCC/clang-built BSim; link-map recovery; recovering configuration from constants | IAR EWARM at the identified release is installed and fingerprinted (`tools/bootstrap/bootstrap.py --licensed`) |
| `TC-METAWARE` | Synopsys MetaWare T-2022.09 build 004 | licensed compiler | byte-matching C for the G2 EM9305 controller | disassembly with `arc-elf32-objdump`; record-package and container work; function identity from SDK archive matching | MetaWare installed (from MIPS/Synopsys, or supplied by EM Microelectronic) |
| `TC-ARMCC5` | Arm Compiler 5.06 (armcc/armlink) with an MDK Professional licence | licensed compiler | byte-matching C for the R1 application and bootloader | full decompilation in Ghidra; nRF5 SDK and FreeRTOS identification; scatter-layout recovery | Arm Compiler 5.06 installed and fingerprinted |
| `TC-ARMCLANG6` | Arm Compiler 6 (armclang, armlink, Arm C library) from Keil MDK; release to identify | licensed compiler (MDK v6 Community is free for non-commercial use with a Keil account) | byte-matching C for the G2 charging case | full decompilation; open LLVM clang 11–20 as a near proxy (identical register allocation; one scheduling difference, see `tools/matching/experiments.md`) | armclang is installed and its release is identified by matching |
| `TC-ARCV2-DECOMP` | a decompiler for ARCv2 EM (Ghidra has none; pull request 3006 is ARCompact only) | analysis tool | EM9305 *pseudocode* (disassembly-level review is still possible) | objdump-based disassembly review, control-flow recovery, SDK function matching | an ARCv2 SLEIGH module in a project-owned Ghidra fork, or IDA Pro with its ARC module |
| `TC-CSKY-EMU` | an emulator for C-SKY CK804 | analysis tool (soft) | dynamic confirmation of GX8002 behaviour only | static decompilation with the C-SKY Ghidra module and `csky-elfabiv2` binutils; compiler identification with the open C-SKY GCC | a CK804-capable QEMU or Unicorn port is found or built |
| `VO-NEMAGFX` | NemaGFX / NemaVG libraries built with the stock compiler | binary-only vendor object | the GPU library functions in the Apollo main application | decompilation and review; header types from the pinned `ambiqhal-nema` submodule | the IAR-built NemaGFX objects are obtained from Ambiq, or those functions are byte-matched after `TC-IAR` clears |
| `VO-PACKETCRAFT-LL` | Packetcraft/EM BLE link-layer controller (`LL_VER_NUM=28992`) | binary-only vendor object | the EM9305 controller core | disassembly; matching against the EM9305 SDK archives | the EM9305 SDK v4.2 archives are obtained from EM Microelectronic |
| `VO-GOODIX` | Goodix GH3x2x algorithm libraries (HR, SpO2, HRV, NADT) | binary-only vendor object | the matching R1 functions | decompilation; the demo/driver layer is public (`third-party/upstream/goodix-gh3x2x`) | Goodix supplies the objects, or the functions are byte-matched after `TC-ARMCC5` clears |
| `VO-GOMORE` | GoMore health and sleep algorithm library | binary-only vendor object | the matching R1 functions (362) | decompilation; reference pseudocode in `r1/reconstructed/` | GoMore supplies the objects, or the functions are byte-matched after `TC-ARMCC5` clears |
| `IN-R1-CAPTURE` | captured R1 bootloader, UICR and APPROTECT images | missing input | R1 bootloader work and the full R1 flash oracle | R1 application work; the SDK bootloader source is public | the captures are placed in `r1/blobs/official/2.2.6.0009/` |

Process states, used in region manifests alongside the blocker IDs above.
They are not missing tools:

| ID | Meaning | Clears when |
| --- | --- | --- |
| `GATE-FREEZE` | the region's toolchain is open, but G2 C work waits for the whole-artifact pseudocode freeze (AGENTS.md, workflow gate G3/G4) | the G2 corpus is frozen and the C phase is authorized |
| `OPEN-PENDING` | open work that has not been done yet: decompilation, identification or matching; no missing tool | the region is rebuilt from source and switched to `source` |
| `CONTAINER` | container metadata (headers, CRCs, record tables) that `open_cfw.py` and the record-package tools already regenerate | the container generator is wired into the per-payload rebuild |

Not blockers:

- the S140 7.2.0 SoftDevice, which is Nordic's binary as distributed in the
  nRF5 SDK and is carried as Nordic ships it;
- the GX8002 compiler, which is open-source C-SKY GCC whose exact release
  still has to be identified;
- the touch compiler: open-source Arm GNU GCC ≥ 10.3 at `-Og`, confirmed by
  an exact byte match.

## Component status

"Open work" is what proceeds now. "Gated" is what waits.

| Device | Payload | Size | Open work now | Gated on |
| --- | --- | ---: | --- | --- |
| G2 | EVENOTA container | 4,301,227 B | done: byte-identical repack (`make g2-verify`) | — |
| G2 | touch (PSoC 4000T, Cortex-M0+) | 34,464 B | **raw decompilation done** (308 functions); **compiler identified**: open Arm GNU GCC ≥ 10.3 at `-Og`, with an exact byte match of official Infineon PDL code (`tools/matching/experiments.md`); next: match the remaining PDL, CAPSENSE and emEEPROM functions | — (fully open) |
| G2 | case (STM32G0B1-class, Cortex-M0+) | 55,784 B | **raw decompilation done** (435 functions); review; STM32CubeG0 and FreeRTOS identification with open clang as proxy | `TC-ARMCLANG6` (compiler identified as Keil MDK / Arm Compiler 6) |
| G2 | codec (GX8002B, C-SKY CK804EF) | 326,092 B | **raw decompilation done** for all five code regions (929 functions); `lvp_kws` identification; C-SKY GCC release identification | `TC-CSKY-EMU` (dynamic checks only) |
| G2 | EM9305 (ARCv2 EM) | 211,948 B | **full ARCv2 EM disassembly done** (open binutils); disassembly review; SDK archive matching | `TC-ARCV2-DECOMP`, `TC-METAWARE`, `VO-PACKETCRAFT-LL` |
| G2 | Even bootloader (Apollo510B) | 148,599 B | **raw decompilation done** (903 functions, 849 decompiled); review, library identification | `TC-IAR` |
| G2 | Apollo main application | 3,523,396 B | decompilation (all 7,449 functions already exported), review, library identification | `TC-IAR`, `VO-NEMAGFX` |
| R1 | application (nRF52840) | 646,408 B | decompilation (2,687 functions exported and attributed), review, nRF5 SDK matching | `TC-ARMCC5`, `VO-GOODIX`, `VO-GOMORE` |
| R1 | bootloader | 24,576 B | SDK Secure DFU source identification | `IN-R1-CAPTURE`, `TC-ARMCC5` |
| R1 | S140 SoftDevice | 159,744 B region | carried as Nordic's binary | — |

Run details and findings are in
[`g2/docs/reference/decompilation-status.md`](g2/docs/reference/decompilation-status.md).

G2 C reconstruction additionally waits for the whole-artifact pseudocode
freeze required by [`AGENTS.md`](AGENTS.md) and
[`g2/workflow/PROCEDURE.md`](g2/workflow/PROCEDURE.md). The touch and case
payloads are therefore the first to be fully decompiled and reviewed, and
their compiler releases the first to be identified. They are also the first
whose retained segments can be replaced once C work is allowed.

## Firmware cutting and retained segments

[`tools/cutting/firmware_cut.py`](tools/cutting/README.md) does the cutting.
Each payload has a region manifest under
[`tools/cutting/manifests/`](tools/cutting/manifests). The manifest is an
ordered, gap-free list of byte ranges covering the whole payload. Each range
has one of these states:

| State | Meaning | Counts toward source completeness |
| --- | --- | --- |
| `retained` | cut from the official image and carried as bytes, with a blocker ID or `pending` | no |
| `source` | produced by the rebuild from source (only after the relevant gate) | yes |
| `vendor-binary` | a vendor binary carried by design, such as the S140 SoftDevice | not applicable |

`firmware_cut.py verify` reassembles every payload from its segments and
checks the result against the locked SHA-256. `firmware_cut.py report`
prints the retained bytes per blocker ID. At the start every region is
`retained`, and the report is the debt ledger.
