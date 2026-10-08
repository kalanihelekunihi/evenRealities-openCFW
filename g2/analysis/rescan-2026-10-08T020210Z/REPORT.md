# OpenCFW change scan — 2026-10-08T02:02:10.860706+00:00

Read-only inspection against `g2/analysis/rescan-2026-10-08T005713Z`; only this scan directory was written. No generator, build or new test was started. A previously running delay validation completed during inspection; its existing receipts are included. Concurrent campaign work may advance after this capture.

Canonical bootloader/foundation C/header/assembly: **453 → 467 files**, **14 added, 0 modified, 0 removed**. This is a file inventory, not a function or completeness metric. 384 tracked/indexed, 83 untracked, 0 ignored. No added canonical source is ignored.

## Material progress since the previous scan

The previous formatter draft is now an accepted **237-object bounded native formatter checkpoint**, `dbbd73cfd6b5…`. Its on-disk ELF matches the sealed receipt. That receipt records **7 integration cases, 76 regression jobs, 1,511 current-source nonfloating cases, 216 native-wrapper cases and 5,062 Cortex-M55 QEMU cases**, including full FPSCR checks across five caller-frame patterns. Eight canonical objects reproduce and match the QEMU-tested objects; the frozen relink matches exactly. The earlier `%%:%q:%` failure was resolved as a synthetic callback fixture problem; original failure evidence remains preserved. Read `iar-format-native-integrated/REPORT.md` and `FIXTURE-REPAIRS.md` under `g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-initialize` for provenance and limits.

The successor mapping ledger `g2/analysis/source-replacement-ledger-2026-10-08-format-engine` now admits **29 bodies / 8,574 original bytes**, up from **20 / 4,932** (+9 / +3,642). Parser/cursor fragments are not double-counted inside the engine. This remains a bounded mapped lower bound.

A second accepted 237-object checkpoint, `ea0134ca1671…`, binds the existing native initializer instead of original address `0x41c4b5`. Its receipt records **64 coupled caller/root comparisons, 7 fresh integration cases and 13 affected regression jobs**; the earlier 76-job suite is inherited, not rerun. All 237 objects are unchanged, two root source objects reproduce, and relink is exact.

The **238-object native delay candidate** `e5aeae5297c6…` now has **7 integration cases and 13 affected jobs, no failures**, plus **768 integrated native scheduler/list comparisons**. Its ELF identity matches the candidate record, but **no completion receipt exists at scan time**; do not promote it to an accepted checkpoint yet. Standalone delay evidence also records 270 controlled body cases. CMSIS delay(0) returns without yielding; the underlying kernel delay(0) yields. UINT32_MAX is a finite wrapping delay in this path, not an infinite wait. Exception delivery, actual task switching and elapsed hardware time are outside these tests.

Five terminal/fatal functions also have readable reconstructed C and **120 controlled original-instruction comparisons** under `g2/analysis/bootloader-completion-2026-10-06/inventory-worker/terminal-paths-native`. They remain standalone, with declared child contracts, and are not integrated or added to the accepted byte ledger. Logging/fatal paths and DFU terminal looping are explained there; no hardware reset behavior is inferred from a mock.

## Visibility, preservation and remaining boundary

**110 sealed audit inputs checked; 0 changed.** Build ELF output remains hidden by `.gitignore:15:build/	g2/build/bootloader-completion/runtime-delay-native-integrated/e5aeae5297c6aa35c78a5f4c558365d2d47a0f8f6505f3ed2431914278ef6c32/candidate.elf`. The existing `*.log` ignore rule hides raw logs. Canonical readable sources are on disk outside that tree; a tracked-only browser misses untracked additions. Ignore rules therefore explain output visibility, not absence of source work. No ignore, shared state, index or existing source was edited by this scan.

These are bounded offline reconstructions. Production payloads still use official blobs; no receipt establishes a complete source-built bootloader/payload or byte-identical source-built OTA. Resident ROM dependencies, uncontrolled scheduler/hardware behavior and exact producing toolchain/configuration remain separate unresolved boundaries.

## Canonical additions

- `g2/components/bootloader/initializer_callbacks/iar_format_native/engine.c`
- `g2/components/bootloader/initializer_callbacks/iar_format_native/engine.h`
- `g2/components/bootloader/initializer_callbacks/iar_format_native/entry.c`
- `g2/components/bootloader/initializer_callbacks/iar_format_native/float_render.c`
- `g2/components/bootloader/initializer_callbacks/iar_format_native/format_parser.c`
- `g2/components/bootloader/initializer_callbacks/iar_format_native/format_parser.h`
- `g2/components/bootloader/initializer_callbacks/iar_format_native/fp_primitives.c`
- `g2/components/bootloader/initializer_callbacks/iar_format_native/integer_cursor.c`
- `g2/components/bootloader/initializer_callbacks/iar_format_native/integer_cursor.h`
- `g2/components/bootloader/initializer_callbacks/iar_format_native/integer_render.c`
- `g2/components/bootloader/initializer_callbacks/iar_format_native/record.h`
- `g2/components/bootloader/initializer_callbacks/iar_format_native/termination.c`
- `g2/components/bootloader/thread_creation/task_delay_native/task_delay.c`
- `g2/components/bootloader/thread_creation/task_delay_native/task_delay.h`
