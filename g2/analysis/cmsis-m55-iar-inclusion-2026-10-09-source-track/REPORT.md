# Finite CMSIS M55 IAR stock-inclusion discriminator

No stock-inclusion target was established for the newly available CMSIS M55 DSP IAR archive. Stop this candidate at the bounded negative result; do not acquire another source checkout or repeat these probes without new address-bound evidence.

## Authenticated scope and method

Input SDK archive member `CMSIS/ARM/Lib/ARM/DSP_LIB_CM55/iar_cortexM55f_math.a`, SHA-256 `034dfb178804c3885b73e15c28bd3ff72c34d5fc9800409c44c453061662c772`, producer IAR 9.60.4.438. Read directly from the authenticated SDK ZIP in memory, without extracting or executing SDK objects. Reference Apollo package SHA-256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`; searched complete main payload after its 0x20-byte header, mapped at 0x438000.

The authored static parser inventories all 15 archive objects and 638 nonempty sized executable function symbols. `FUNCTION-INVENTORY.json` retains complete object/function hashes, section sizes, symbol extents and explicit relocations. A preselected set of 20 named signal/math functions spans FIR, biquad, matrix, FFT, trigonometry and statistics; all requested names were present. Fourteen functions met the 128-byte minimum. From each, search at most three longest unchanged relocation-free spans of at least 64 bytes, excluding a conservative eight bytes at every relocation. No bytes were masked or rewritten.

## Results

- Twenty qualifying spans, lengths 66 through 1626 bytes: zero exact stock hits.
- Fourteen complete unlinked function bodies: zero exact stock hits. Relocation-bearing bodies are not claimed to be linked comparators.
- Four substantial functions had zero relocations and therefore were compared in full: `arm_biquad_cascade_df1_f32` (266), `arm_biquad_cascade_df2T_f32` (590), `arm_fir_q15` (694), and `arm_mat_inverse_f32` (1626).
- Four complete nonrelocated distinctive tables were absent: `armBitRevTable` (2048), `sinTable_f32` (2052), `twiddleCoef_4096` (32768), `twiddleCoef_rfft_4096` (16384). Hashes in `CONSTANT-CHECK.json`.
- Canonical Apollo symbols have none of the 20 requested API names, consolidated library references have no CMSIS-DSP mention, and selected literal names have zero hits. Stripped-name absence is contextual, not an exclusion proof. Existing CMSIS Core/RTOS provenance does not imply CMSIS DSP.

Correction to the progress commentary: there are **four** relocation-free complete-function comparisons in the qualifying set, not five. The machine-readable extents and relocation rows are authoritative; this report explicitly preserves the correction.

## Limits

These raw negatives exclude exact presence of the tested spans/functions/tables from this archive in this main payload. They do not establish global absence of CMSIS DSP, exclude differently compiled implementations, linker relaxation, untested functions/tables, other revisions, or other payloads. No semantic simulator or instruction execution was used. Private runtime inputs and compiler/configuration remain distinct from this DSP library.

Deliverables: `RESULT.json`, `FUNCTION-INVENTORY.json`, `CONSTANT-CHECK.json`, `PROVENANCE-CHECK.json`, reproducible authored `discriminate.py`. Prior DSP, LZ4, Nema findings, canonical ledgers, firmware sources, index and seals were untouched. No public redistribution or new source registration occurred.
