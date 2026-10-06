# Current source rescan

Snapshot: 2026-10-06T20:29:04.028282+00:00. Baseline: `g2/analysis/rescan-2026-10-06T194959Z`.

- `g2/components/bootloader`: **125 → 142** C/header/assembly files.
- `g2/components/foundation`: **89 → 89** C/header/assembly files.
- Added: **17**; modified: **0**; removed: **0**; ignored source files: **0**.

Counts include headers, vendored source and tests; they do not measure firmware completeness.

## Changed source files

- `g2/components/bootloader/filesystem/boot_mount.c` (added)
- `g2/components/bootloader/filesystem/boot_mount.h` (added)
- `g2/components/bootloader/filesystem/boot_mount_test.c` (added)
- `g2/components/bootloader/nor_init/nor_runtime.c` (added)
- `g2/components/bootloader/nor_mspi_init/blocking_transfer.c` (added)
- `g2/components/bootloader/nor_mspi_init/fifo_transfer.c` (added)
- `g2/components/bootloader/nor_mspi_init/hal_leaves.c` (added)
- `g2/components/bootloader/nor_mspi_init/irq_guard.S` (added)
- `g2/components/bootloader/nor_mspi_init/status_poll.c` (added)
- `g2/components/bootloader/platform_control/runtime.c` (added)
- `g2/components/bootloader/platform_control/runtime.h` (added)
- `g2/components/bootloader/platform_control/runtime_query.c` (added)
- `g2/components/bootloader/platform_control/runtime_query.h` (added)
- `g2/components/bootloader/platform_control/runtime_resources.c` (added)
- `g2/components/bootloader/platform_control/runtime_transition.c` (added)
- `g2/components/bootloader/platform_control/runtime_transition.h` (added)
- `g2/components/bootloader/platform_control/runtime_wait_adapter.c` (added)

## Functional change

The source reset integration now reaches application reset entry on normal and synthetic-update branches, replacing prior runtime-enable/file-open stops. Direct storage comparison passes two cases / 24,382 distinct original instruction bytes; runtime comparison passes eight cases / 11,384 bytes. Source mount/file services, runtime transition/query, finite MSPI HAL, FIFO movement and polling have been added or integrated. Storage/peripheral callbacks remain modeled; no hardware boot, full source closure or byte equality claim. See [current integration report](../bootloader-completion-2026-10-06/integrated-status/REPORT.md) for actual current combined-run status and boundaries.

The scan reads on-disk source and Git ignore/status views. It does not modify existing sources or index.
