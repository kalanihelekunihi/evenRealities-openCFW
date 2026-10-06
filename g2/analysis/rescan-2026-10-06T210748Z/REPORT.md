# Current source rescan

Snapshot: 2026-10-06T21:07:48.032472+00:00. Baseline: `g2/analysis/rescan-2026-10-06T202904Z`.

- `g2/components/bootloader`: **142 → 161** C/header/assembly files.
- `g2/components/foundation`: **89 → 89** C/header/assembly files.
- Added: **19**; modified: **0**; removed: **0**; ignored source files: **0**.

Counts include headers, vendored code and tests; they do not measure firmware completeness. This is a live concurrent checkout snapshot, not a frozen corpus.

## Changed source files

- `g2/components/bootloader/clock_manager/clock_release_all.c` (added)
- `g2/components/bootloader/nor_mspi_init/control_read.c` (added)
- `g2/components/bootloader/nor_mspi_power/device_configure.c` (added)
- `g2/components/bootloader/nor_mspi_power/device_configure.h` (added)
- `g2/components/bootloader/nor_mspi_power/mspi_clockgen_control.c` (added)
- `g2/components/bootloader/nor_mspi_power/power_control.c` (added)
- `g2/components/bootloader/nor_mspi_power/power_control.h` (added)
- `g2/components/bootloader/nor_mspi_power/power_control_adapter.c` (added)
- `g2/components/bootloader/nor_mspi_power/power_control_adapter.h` (added)
- `g2/components/bootloader/nor_mspi_queue/nor_mspi_queue.c` (added)
- `g2/components/bootloader/nor_mspi_queue/nor_mspi_queue.h` (added)
- `g2/components/bootloader/nor_read/runtime_helpers.c` (added)
- `g2/components/bootloader/nor_read/runtime_helpers.h` (added)
- `g2/components/bootloader/nor_write/nor_write.c` (added)
- `g2/components/bootloader/nor_write/nor_write.h` (added)
- `g2/components/bootloader/platform_control/power_domains.c` (added)
- `g2/components/bootloader/platform_control/power_domains.h` (added)
- `g2/components/bootloader/platform_startup/platform_startup.c` (added)
- `g2/components/bootloader/platform_startup/platform_startup.h` (added)

## Validation evidence

Existing receipts were read and hashed, not rerun. The latest source NOR/power profile documents two passing modeled reset/update cases and 28,874 distinct original instruction bytes. Its hardware callbacks and external boundaries remain explicit; this does not establish hardware boot, complete source closure or byte equality. See [provider integration](../bootloader-completion-2026-10-06/integrated-status/nor-read-followup/REPORT.md).

Receipt contents, timestamps and hashes are saved in `snapshot.json`; source changes after a receipt mean it is historical evidence rather than a fresh validation of the current checkout. Git status is saved separately. No existing source or index was changed.
