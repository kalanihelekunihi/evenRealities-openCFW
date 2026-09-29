# Decompilation status (open tooling)

These are raw machine exports: P2 raw evidence under
[`../../workflow/PROCEDURE.md`](../../workflow/PROCEDURE.md). None of it is
reviewed pseudocode yet. Everything was produced with open tools only, and
[`../../../MISSING-TOOLCHAIN.md`](../../../MISSING-TOOLCHAIN.md) lists
what is still gated. The exports are in `g2/research/corpus/`, indexed by
`MANIFEST.sha256`, and each carries its own `SHA256SUMS` and `RUN.json`.

## Runs of 2026-09-29

| Payload | Tool | Load base / language | Functions | Decompiled | Seed names applied | Export |
| --- | --- | --- | ---: | ---: | ---: | --- |
| touch (PSoC 4000T) | Ghidra 12.1.4 | `0x3300`, `ARM:LE:32:Cortex` | 308 | 308 | 290 | `touch/ghidra/open-2026-09-29/` |
| case (STM32G0) | Ghidra 12.1.4 | `0x08000000`, `ARM:LE:32:Cortex` | 435 | 435 | 315 | `case/ghidra/open-2026-09-29/` |
| Even bootloader (Apollo510B) | Ghidra 12.1.4 | `0x00410000`, `ARM:LE:32:v8-m` | 903 | 849 | 292 | `apollo-bootloader/ghidra/open-2026-09-29/` |
| codec UART boot stage 1 | Ghidra 12.1.4 + C-SKY module `0daaa056` | `0x10000000`, `CSKY_V2:LE:32:default` | 32 | 32 | 32 | `codec/ghidra/open-2026-09-29/uart_boot_stage1/` |
| codec UART boot stage 2 | same | `0x10002800` | 96 | 96 | 10 | `.../uart_boot_stage2/` |
| codec image A XIP text | same | `0x10203004` | 362 | 362 | 362 | `.../image_a_xip/` |
| codec image A SRAM text+data | same | `0x10023400` | 151 | 151 | 151 | `.../image_a_sram/` |
| codec image B SRAM text+data | same | `0x10003000` | 288 | 288 | 62 | `.../image_b_sram/` |
| EM9305 record 3 (controller) | GNU binutils 2.42 `arc-linux-gnu-objdump`, ARCv2 EM carrier from `arc-linux-gnu-gcc` 13.3 | `0x302400..0x335BC8` | disassembly only (71,924 lines) | — (`TC-ARCV2-DECOMP`) | — | `em9305/objdump/open-2026-09-29/` |
| Apollo main | Ghidra 12.1.2 (2026-08-08 run) | `0x00438000` | 7,449 | 7,449 | — | `apollo-main/ghidra/decomp/` |

Reproduce a run with `g2/tools/run_raw_image_ghidra_export.sh`. Set
`GHIDRA_INSTALL_DIR`, and set `OPENCFW_SEEDS=g2/symbols/<payload>.tsv` to
apply the naming seeds. The script checks the image hash first. Install the
C-SKY module by copying `third-party/tools/ghidra-csky/C-SKY/{data,Module.manifest}`
into `<ghidra>/Ghidra/Processors/CSKY/` and compiling
`csky_v2.slaspec` with `<ghidra>/support/sleigh`. The EM9305 disassembly
comes from `g2/tools/disassemble_em9305_arcompact.py --binutils-dir <dir
with arc objcopy/objdump>`.

## Findings from these runs

- **The touch image is linked at `0x3300`, not 0.** With base `0x3300`, the
  reset vector lands on the recovered reset entry and 276 of 291 named seeds
  match discovered entries. `memory-map.md` §6 and `firmware-formats.md` §6
  are corrected.
- **54 Even-bootloader functions did not decompile.** Their entries are
  listed with `decompiled: false` in `functions-000.jsonl`. They are the
  first to check against `arm-none-eabi-objdump` 13.3 for MVE/Helium or
  data-in-code.
- **The seeds only partly cover codec UART stage 2 (10 of 96) and image B
  (62 of 288).** These are the next identification targets against
  NationalChip `lvp_kws` (`third-party/upstream/nationalchip-lvp-kws`).
- **The EM9305 controller disassembles cleanly as ARCv2 EM with open
  binutils.** Decompilation waits on `TC-ARCV2-DECOMP`.

## Next steps (open tooling, no missing component)

1. Review queue: touch → case → codec → bootloader. Review each function
   against the disassembly and record it in the workflow's result format.
2. Identify upstream code by building `third-party/upstream/infineon-mtb-pdl-cat2`,
   `stm32g0xx-hal-driver`, `freertos-kernel` and `nationalchip-lvp-kws`
   with candidate GCC releases (Arm GNU 13.3 and 9-2020-q2; C-SKY GCC).
   Match the objects against the exports with BSim or FunctionID, and pin
   the matching releases.
3. Apollo main: re-export at `0x00438000` with the seeds applied, using
   Ghidra 12.1.4, for a named P2 raw corpus.
