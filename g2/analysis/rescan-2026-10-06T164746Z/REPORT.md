# Refreshed source and saved-evidence scan

Snapshot: 2026-10-06T16:47:46.419601+00:00. Baseline: `g2/analysis/rescan-2026-10-06T154438Z`.

Bootloader C/header/assembly files: **43 → 53**. Foundation: **89 → 89**. Ignored source files in these two component trees: **0**.

Added: 10; modified: 0; removed: 0. Counts include headers, vendored code and host tests; they are not function or firmware completion counts.

## Source changes

- `g2/components/bootloader/main_callback/main_callback.c`
- `g2/components/bootloader/main_callback/main_callback.h`
- `g2/components/bootloader/main_init/main_init.c`
- `g2/components/bootloader/main_init/main_init.h`
- `g2/components/bootloader/startup/fpu.S`
- `g2/components/bootloader/startup/init_records.S`
- `g2/components/bootloader/startup/record_adapters.S`
- `g2/components/bootloader/startup/record_dispatch.c`
- `g2/components/bootloader/startup/reset.S`
- `g2/components/bootloader/startup/system_entry.c`

Modified:

## Saved comparison evidence

| Receipt | Status | Cases | Original bytes | Stale source bindings |
|---|---|---:|---:|---:|
| `g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read/nor-read-comparison.json` | PASS | 10 | None | 4/4 |
| `g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read-setup/nor-read-setup-comparison.json` | PASS | 17 | None | 6/6 |
| `g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read-setup/nor-read-setup-linked-status-comparison.json` | PASS | 7 | None | 6/6 |
| `g2/analysis/bootloader-completion-2026-10-06/inventory-worker/nor-read-status/nor-read-status-comparison.json` | PASS | 13 | None | 4/4 |
| `g2/analysis/bootloader-completion-2026-10-06/inventory-worker/queue-wrappers/queue-comparison.json` | PASS | 45 | None | 4/4 |
| `g2/analysis/bootloader-completion-2026-10-06/review-worker/independent-comparison.json` | PASS | 4514 | 1208 | 5/5 |
| `g2/analysis/bootloader-completion-2026-10-06/upstream-worker/mspi-cmdq-consumer/out/chain-comparison.json` | PASS | 12 | None | 8/8 |
| `g2/analysis/bootloader-completion-2026-10-06/upstream-worker/mspi-cmdq-consumer/out/chain-table-comparison.json` | PASS | 12 | None | 8/8 |
| `g2/analysis/bootloader-completion-2026-10-06/upstream-worker/mspi-cmdq-consumer/out/comparison.json` | PASS | 19 | None | 8/8 |
| `g2/analysis/bootloader-completion-2026-10-06/upstream-worker/mspi-cq-init/out/comparison.json` | PASS | 8 | None | 0/4 |
| `g2/analysis/bootloader-completion-2026-10-06/upstream-worker/mspi-enable/out/comparison.json` | PASS | 9 | None | 0/5 |
| `g2/build/bootloader-completion/allocator-compatible/comparison-first.json` | PASS | 265 | 1994 | 0/9 |
| `g2/build/bootloader-completion/dfu-context-compatible/comparison-first.json` | PASS | 37 | 310 | 8/8 |
| `g2/build/bootloader-completion/dfu-task-compatible/comparison-first.json` | PASS | 213 | 734 | 4/4 |
| `g2/build/bootloader-completion/main-callback-compatible/comparison-first.json` | PASS | 4 | 44 | 7/7 |
| `g2/build/bootloader-completion/main-callback-startup-integrated-compatible/comparison-first.json` | PASS | 4 | 370 | 0/16 |
| `g2/build/bootloader-completion/main-init/main-init-comparison-final.json` | PASS | 6 | 100 | 5/5 |
| `g2/build/bootloader-completion/main-init/main-init-comparison-first.json` | PASS | 6 | 98 | 5/5 |
| `g2/build/bootloader-completion/main-init/main-init-comparison.json` | PASS | 6 | 100 | 7/7 |
| `g2/build/bootloader-completion/main-init/startup-main-init-compatible/comparison-final.json` | PASS | 4 | 338 | 1/11 |
| `g2/build/bootloader-completion/mspi-compatible/comparison-first.json` | PASS | 37 | 48 | 0/86 |
| `g2/build/bootloader-completion/mutex-runtime-compatible/comparison-first.json` | PASS | 288 | 258 | 0/10 |
| `g2/build/bootloader-completion/nor-read-components/comparison-first.json` | PASS | 10 | None | 4/4 |
| `g2/build/bootloader-completion/platform-control-compatible/comparison-first.json` | PASS | 496 | 270 | 4/4 |
| `g2/build/bootloader-completion/platform-control-critical-rom-compatible/comparison-first.json` | PASS | 496 | 308 | 8/8 |
| `g2/build/bootloader-completion/platform-control-power-compatible/control-comparison-first.json` | PASS | 500 | 472 | 11/11 |
| `g2/build/bootloader-completion/platform-control-power-compatible/guards-comparison-first.json` | PASS | 14 | 164 | 1/12 |
| `g2/build/bootloader-completion/platform-control-rom-compatible/comparison-first.json` | PASS | 496 | 300 | 6/6 |
| `g2/build/bootloader-completion/queue-components/comparison-first.json` | PASS | 45 | None | 4/4 |
| `g2/build/bootloader-completion/queue-runtime/comparison-first.json` | PASS | 45 | None | 6/6 |
| `g2/build/bootloader-completion/startup-compatible/comparison-final.json` | PASS | 39 | 182 | 4/4 |
| `g2/build/bootloader-completion/startup-compatible/comparison-first.json` | PASS | 39 | 182 | 4/4 |
| `g2/build/bootloader-completion/startup-compatible/itcm-comparison-first.json` | PASS | 16 | None | 3/3 |
| `g2/build/bootloader-completion/startup-records-compatible/comparison-entry.json` | PASS | 4 | 242 | 13/13 |
| `g2/build/bootloader-completion/startup-records-compatible/comparison-first.json` | PASS | 3 | 212 | 12/12 |
| `g2/build/bootloader-completion/startup-records-compatible/comparison-fpu.json` | PASS | 7 | 276 | 15/15 |
| `g2/build/bootloader-completion/startup-records-table-compatible/comparison-final.json` | PASS | 7 | 276 | 17/17 |
| `g2/build/bootloader-completion/update-core-compatible/comparison-final.json` | PASS | 4542 | 1208 | 5/5 |
| `g2/build/bootloader-completion/update-core-compatible/comparison-first.json` | PASS | 4514 | 1208 | 5/5 |
| `g2/build/bootloader-completion/update-core-compatible/comparison-resources-final.json` | PASS | 4542 | 1208 | 7/7 |

Saved results were read and source hash bindings/original instruction bytes checked. Builds and emulation were not rerun. Superseded profiles overlap: do not sum their bytes. No source manifest means current source identity is unproven. Synthetic providers and compatibility-build limits remain those documented in each component.

Generated ELF/results under `g2/build/` and licensed SDK/toolchains under `third-party/local-vendor/` are ignored; recovered source in the component trees is visible. No complete source-built payload or byte-identical bundle is demonstrated. Global pseudocode/review footprints were not recomputed in this source scan.

Index preserved during this scan: True. No staging, cleanup, generator execution or hardware access.
