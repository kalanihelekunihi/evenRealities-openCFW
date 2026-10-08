# OpenCFW change scan — 2026-10-08T03:14:13 UTC

Compared with the 02:02:10 UTC scan. Read-only inspection; only this scan directory was written. No generators, builds or execution tests ran. Existing receipts were inspected and candidate ELF hashes freshly verified. Concurrent campaign progress after capture is outside this report.

Canonical bootloader/foundation C, headers and assembly increased **467 → 475**: **8 added, 0 modified, 0 removed**. Of these, **384 are tracked/indexed, 91 untracked, 0 ignored**. A tracked-only browser therefore misses 91 readable source files. The eight additions are listed below.

The previously pending native-delay checkpoint now has an acceptance receipt (238 objects). Five terminal/fatal paths are integrated and accepted (239); full diagnostic argument adapters and timestamp/DFU coupling are accepted (240); source-defined diagnostic literals and the ADC descriptor are accepted (242). All four on-disk candidate ELF hashes match both their candidate records and completion receipts.

The integrated ownership ledger advanced **29 bodies / 8,574 original bytes → 38 bodies / 9,472 bytes**. It separately accounts for **37 readonly ranges / 1,166 bytes**. These are bounded mapped footprints, not whole-image completeness. Two independent memory helpers also have new readable C/header and recorded **840 original-instruction Cortex-M55 comparisons**, but are not integrated into the 242-object checkpoint or counted in that integrated ledger.

Existing evidence records 768 native scheduler/list comparisons for delay; 120 terminal body comparisons plus 48 actual mask/exit-child cases; 213 task-log, 88 log-packaging and 48 timestamp cases; and 97 update-core full-log cases on the 241 intermediate with tested code/data inherited by 242. The final 242 receipt records 7 fresh integration cases and 13 affected jobs; the 240 checkpoint's broader 76-job suite is inherited, not freshly rerun by 242 or by this scan. Controlled child calls, synthetic scheduler state and relocated QEMU oracle limits remain applicable.

**110 sealed audit input hashes were freshly checked: 0 changed.** Git still ignores build ELFs through `.gitignore:15:build/` and raw logs through `*.log`; no canonical source addition is ignored. Ignore rules affect artifact visibility but do not explain an absence of new source work.

Production payloads still use official blobs. No inspected receipt proves a complete source-built or byte-identical OTA, or hardware execution. Whole-image coverage, producing compiler/configuration and physical scheduler/peripheral behavior remain distinct gaps. Resident ROM is external to OTA; absent ROM limits emulation of external routines, not accounting for known calls inside the image.

See `g2/analysis/dependency-closure-2026-10-08/REPORT.md` and `KNOWLEDGE.md` for recovered behavior, hashes, validation limits and function navigation. This scan preserved shared state, source files, staging and existing evidence.

## Newly present canonical files

- `g2/components/bootloader/initializer_callbacks/iar_memory_native/memory.c`
- `g2/components/bootloader/initializer_callbacks/iar_memory_native/memory.h`
- `g2/components/bootloader/initializer_callbacks/platform_log_literals/platform_literals.c`
- `g2/components/bootloader/log_call_adapters/log_adapters.c`
- `g2/components/bootloader/log_call_adapters/log_adapters.h`
- `g2/components/bootloader/log_call_adapters/task_with_log_detail.c`
- `g2/components/bootloader/thread_creation/terminal_paths_native/terminal_paths.c`
- `g2/components/bootloader/update_core/log_literals/log_literals.c`
