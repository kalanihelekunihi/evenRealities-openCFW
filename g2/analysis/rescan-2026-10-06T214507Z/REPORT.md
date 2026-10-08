# Current source rescan

Snapshot: 2026-10-06T21:45:07.716316+00:00. Baseline: `g2/analysis/rescan-2026-10-06T210748Z`.

- `g2/components/bootloader`: **161 → 172** C/header/assembly files.
- `g2/components/foundation`: **89 → 89** C/header/assembly files.
- Added: **11**; modified: **3**; removed: **0**; ignored source files: **0**.

Counts include headers, vendored sources and tests; they do not measure firmware completeness. This is a live concurrent snapshot. No generators or tests were run by this scan.

## Changed source files

- `g2/components/bootloader/application_storage/device_info.c` (added)
- `g2/components/bootloader/application_storage/device_info.h` (added)
- `g2/components/bootloader/application_storage/storage_callback_veneers.S` (added)
- `g2/components/bootloader/application_storage/storage_callbacks.c` (added)
- `g2/components/bootloader/application_storage/storage_callbacks.h` (added)
- `g2/components/bootloader/nor_mspi_init/control_remaining.c` (added)
- `g2/components/bootloader/nor_mspi_init/control_remaining.h` (added)
- `g2/components/bootloader/nor_mspi_init/hal_leaves.c` (modified)
- `g2/components/bootloader/nor_mspi_power/device_configure.c` (modified)
- `g2/components/bootloader/nor_mspi_queue/nor_mspi_queue.c` (modified)
- `g2/components/bootloader/nor_mspi_queue/queue_descriptors.c` (added)
- `g2/components/bootloader/nor_mspi_queue/queue_descriptors.h` (added)
- `g2/components/bootloader/nor_mspi_queue/resources.c` (added)
- `g2/components/bootloader/platform_control/cache_runtime.c` (added)

## Validation and meaning

The current source-image verification log reports two passing modeled reset/update cases (29,868 distinct original trace bytes) and three passing malformed-update cases (28,966 distinct original trace bytes). These are separate workloads, not additive coverage. Receipts are inventoried and hashed in `snapshot.json`; ongoing edits can make an existing receipt historical.

New sources cover application storage callbacks and device information, cache maintenance, remaining MSPI controls, queue descriptors, and startup integration. Existing MSPI device configuration and HAL leaf sources were corrected. Earlier device-configuration testing used the wrong MMIO base; use the corrected real-base evidence rather than the older passing fixture.

This confirms real C/header/assembly work exists on disk and is not hidden by ignore rules in these source roots. It does not establish a standalone source-complete image, physical hardware boot, or byte equality. Resident ROM, remaining internal control/initialization paths, peripheral models and interruption behavior remain separate limits.

All existing source, staging and running analysis were preserved. Build outputs can be ignored intentionally; the source inventory above checks actual files rather than relying on Git status.
