# Apollo bootloader inventory for completion work

Date: 2026-10-06. Scope: the locked G2 2.2.6.10 Apollo bootloader payload only. This is an inventory and dependency handoff; no firmware source, shared index, build, or device state was changed.

## Identity and address model

- Official file: `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`.
- Size: **148,599 bytes** (`0x24477`); SHA-256: `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` (verified against file).
- Format/load: raw ARM little-endian Cortex-M55 / `ARM:LE:32:v8-m`, linked at `0x00410000`; runtime address = file offset + `0x00410000`. Bundle payload begins at byte `629104` (`0x998F0`), so bundle offset = file offset + `629104`.
- Runtime interval: `[0x00410000, 0x00434477)`; next partition boundary `0x00438000`. Manifest identity: `g2/manifests/g2-2.2.6.10.json`, entry 5. Corpus run identity matches exactly (`RUN.json`).

## Existing executable evidence and omissions

`g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/` is the available static export. It used Ghidra 12.1.4, base `0x00410000`, vector seeding across 128 words, and `g2/symbols/bootloader.tsv`. Census: **903 functions**, 292 seeded names, 1 thunk, 1,935 symbols; function bodies cover **120,432 bytes** in the candidate catalogue. Export contains **849 decompilations / 54 failures**. Failed bodies account for **7,926 bytes**; successful-decompilation bodies account for **112,506 bytes**. Failed entries are those with `decompiled:false` in `functions-000.jsonl`; first failure is `0x00417C7C`, last is `0x0042E39C`. Check those functions for unsupported instructions/data-in-code as described in `g2/docs/reference/decompilation-status.md`.

The union of candidate function bodies leaves **28,167 bytes in 245 address gaps** outside that catalogue. These are omissions, not data labels: there may be code, tables, literal pools, vector/config metadata, padding, or mixed content. Every exact gap and its payload-file offsets is in `catalogue-gaps.tsv`. The 849 successful decompilations cover **112,506 raw-pseudocode-addressed bytes**; this is 75.71% of the stored payload. It is a raw evidence footprint, not a whole-image executable denominator. The current assessment's independently linked scoped-review footprint is **101,936 bytes / 68.60% of payload**, and **84.64% of the 120,432 catalogued body bytes**. Neither footprint proves full-path semantic review or executable coverage.

Largest uncovered catalogue gaps (all still unclassified):
- `[0x004329D2, 0x00434477)` (6821 B; payload offsets `0x229D2–0x24477`)
- `[0x00430B3C, 0x0043194C)` (3600 B; payload offsets `0x20B3C–0x2194C`)
- `[0x00431E70, 0x00432910)` (2720 B; payload offsets `0x21E70–0x22910`)
- `[0x0042F674, 0x0042FF00)` (2188 B; payload offsets `0x1F674–0x1FF00`)
- `[0x0043198A, 0x00431E38)` (1198 B; payload offsets `0x2198A–0x21E38`)
- `[0x0043063C, 0x00430A60)` (1060 B; payload offsets `0x2063C–0x20A60`)
- `[0x00410000, 0x00410400)` (1024 B; payload offsets `0x0–0x400`)
- `[0x00426628, 0x004267F8)` (464 B; payload offsets `0x16628–0x167F8`)
- `[0x0042891E, 0x00428A94)` (374 B; payload offsets `0x1891E–0x18A94`)
- `[0x00429DF6, 0x00429F68)` (370 B; payload offsets `0x19DF6–0x19F68`)
- `[0x0041F612, 0x0041F776)` (356 B; payload offsets `0xF612–0xF776`)
- `[0x004172DA, 0x00417438)` (350 B; payload offsets `0x72DA–0x7438`)
- `[0x00419546, 0x00419684)` (318 B; payload offsets `0x9546–0x9684`)
- `[0x0041CAF8, 0x0041CC04)` (268 B; payload offsets `0xCAF8–0xCC04`)
- `[0x00419406, 0x00419508)` (258 B; payload offsets `0x9406–0x9508`)
- `[0x0042D5C2, 0x0042D6C0)` (254 B; payload offsets `0x1D5C2–0x1D6C0`)
- `[0x0041E10E, 0x0041E1E8)` (218 B; payload offsets `0xE10E–0xE1E8`)
- `[0x0042F3DA, 0x0042F4B2)` (216 B; payload offsets `0x1F3DA–0x1F4B2`)
- `[0x00422AD2, 0x00422BA8)` (214 B; payload offsets `0x12AD2–0x12BA8`)
- `[0x00420FF2, 0x004210C8)` (214 B; payload offsets `0x10FF2–0x110C8`)

The initial gap `[0x00410000,0x00410400)` (1,024 B) includes the 128-word vector region (512 B) plus 512 bytes not assigned to a function. Do not call the full 1 KiB a vector table. The image-byte review explicitly left internal bootloader metadata/data boundaries undecoded. No evidence currently establishes a complete stored-byte code/data/resource partition for this component.

## Entry, startup, and reset dependencies

The first 128 words at `0x00410000` seed the Cortex-M vector table. Word 0 is initial SP `0x2007FB00`; word 1 is reset vector `0x0043291B` (Thumb entry `0x0043291A`). Other vectors resolve mainly to local handler/default stubs; preserve the actual 128-word vector data and independently review every live vector/call path. Reset starts at Thumb address `0x0043291B`, the `stack_limits_init_43291a` entry. This routine sets MSP/PSP limits from `DAT_00432934`, calls `process_stack_init_43293c`, and loops if that call returns. The process-stack path checks privilege, sets PSP when privileged, enables the FPU, and calls `runtime_start_43297c`; the return path configures a vector register and CPACR then issues DSB/ISB. This reset chain is inferred from the Ghidra export and must be checked against instructions. From `runtime_start_43297c`:

1. `0x00432910` (`vector_table_relocate`) writes the literal `0x2007D000` to SCB VTOR at `0xE000ED08`, then returns 1. Confirm what pre-populates/copies the RAM vector table at `0x2007D000` and which handlers it contains; the relocation helper itself does not show that copy.
2. `0x0043297C` invokes that routine, conditionally calls init-array processing at `0x0043299C`, then calls `FUN_0041B862(0)`.
3. `0x0043299C` iterates a relative-pointer range described by words at `0x004329BC/0x004329C0`; `init_array_run` repeats a similar relative-pointer loop. Table bounds, individual constructors, and alignment/tail bytes need explicit data recovery.
4. `FUN_0041B862` calls initialization/services at `0x0041F9D8`, `0x0041F9F8`, `0x0041F846`, `0x0041AC44/5A`, `0x0041FA50`, `0x0041E1E8/266`, `0x0041BA80`, `0x0041FD70`, `0x00420476`, and `0x00421210`; emits an EasyLogger message; then calls an indirect pointer at `DAT_0041B8DC`. The export shows a nonreturning loop after it. Resolve that indirect target and init dependencies before claiming reset-to-service closure.
5. A fallback terminal loop at `0x004329C4` repeatedly calls `FUN_0041B298`. Startup/task relationship, scheduler activation, and relation to DFU dispatch remain incomplete.

Known component behavior anchors from `g2/docs/reference/memory-map.md` and `g2/docs/reference/protocols.md`: bootloader-local littlefs, MX25U25643G flash driver, EasyLogger, TLSF, CMSIS-RTOS2-style runtime, AmbiqSuite 5.1.0 MSPI HAL, platform bring-up at `0x00430000`, and DFU service task at `0x0042DE58`. Documented DFU subranges: image-header/CRC `[0x0042D890,0x0042D9F0)`, program/compare `[0x0042DAE8,0x0042DC90)`, task `[0x0042DE58,0x0042E104)`. The task parses the 32-byte image header, validates CRC, skips header while programming chunks, normalizes app vector base to `0x00438000`, checks stack vector, and hands off. Related source-closure Markdown filenames cited by docs are not present as files in this checkout; verify claims from the available binary corpus, reference docs, symbols, and manifests.

## Non-payload/external boundaries

The Ambiq secure bootloader/SBL occupies `[0x00400000,0x00410000)` and is absent from this EVENOTA payload. It is an external predecessor/dependency; do not fold those 64 KiB into bootloader source coverage or claim SBL reconstruction. The payload is the Even bootloader at `0x00410000`, followed by free partition headroom up to `0x00438000`. The latter is outside this component. Apollo main is a separate payload and DFU handoff target. The 16-byte update record at `0x007FE000` is bootloader-owned persistent state but is also outside this file.

## Completion checklist for component pseudocode/source work

1. Pin every claimed address/range to the exact locked SHA above and preserve file-offset/runtime/bundle-offset conversions.
2. Recover all 128 vector words; identify reserved entries, default handlers, actual IRQ handlers, and reset transition. Decode remaining bytes in `[0x00410000,0x00410400)` rather than assuming padding.
3. Recover executable code omitted from the 120,432-byte catalogue; disassemble/resolve all 54 failed functions (`functions-000.jsonl`, `decompiled:false`) and assess all 245 catalogue gaps in `catalogue-gaps.tsv`; prove each stored byte as code, table/resource/data, or fill with evidence. Do not treat catalogue density as an executable denominator.
4. Close reset/runtime: VTOR/vector relocation, data/BSS initialization, init-array table and constructors, clock/peripheral setup, indirect callbacks, RTOS/task startup/IRQ ownership, steady-state loop, error/fault paths, and event path to DFU.
5. Close referenced local providers/data: bootloader-specific RTOS/CMSIS, IAR/DLIB runtime, Ambiq HAL/MSPI, flash driver, littlefs config/core, EasyLogger, TLSF, persistent flag layout, flash map, image header/CRC/program/compare, and app handoff. Track ROM/SBL services as explicit external calls/contracts where addresses or behavior leave this payload.
6. Independently review resulting pseudocode against bytes/assembly and record boundaries, evidence hashes, unknowns, data/code classification, and a per-range completion receipt. Keep pseudocode completion separate from source replacement and exact whole-bundle byte identity.

## Inputs inspected

`AGENTS.md`; `g2/workflow/README.md`; `g2/docs/reference/{memory-map,firmware-formats,decompilation-status,protocols,capabilities}.md`; `g2/manifests/g2-2.2.6.10.json`; `g2/symbols/bootloader.tsv`; `g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/{RUN.json,census.txt,functions-000.jsonl,decomp/*}`; `g2/analysis/firmware-byte-map-2026-10-05/{summary.json,apollo-review.json}`; `g2/analysis/current-assessment-2026-10-06T132057Z/{REPORT.md,bundle-metrics.json,reviewed-pseudocode-metrics.json}`.
