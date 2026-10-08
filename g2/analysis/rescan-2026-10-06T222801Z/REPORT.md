# Source and evidence rescan

Snapshot: 2026-10-06T22:28:01.114915+00:00. Baseline: `g2/analysis/rescan-2026-10-06T214507Z`.

Bootloader C/header/assembly inventory grew **172 → 192**; foundation remained **89**. There are **20 added, 3 modified, 0 removed** source files and **0 ignored source files** in those two roots. Counts include headers and test/vendored code, and do not measure completeness.

## Actual changes

New source covers device-info dispatch and feature layout, INFO memory read dispatch and resident-ROM thunk, initializer-table handling, MSPI pause/DMA and requests31/33, FPU setup and delay arithmetic. Storage callbacks and remaining-control routing changed. The current dispatcher visibly routes requests31/33 to reconstructed providers.

- `g2/components/bootloader/application_storage/device_info_dispatch.c` (added)
- `g2/components/bootloader/application_storage/device_info_dispatch.h` (added)
- `g2/components/bootloader/application_storage/device_info_layout.h` (added)
- `g2/components/bootloader/application_storage/device_info_mode0.c` (added)
- `g2/components/bootloader/application_storage/device_info_mode0.h` (added)
- `g2/components/bootloader/application_storage/device_mode_wait.c` (added)
- `g2/components/bootloader/application_storage/device_mode_wait.h` (added)
- `g2/components/bootloader/application_storage/device_wait_service.c` (added)
- `g2/components/bootloader/application_storage/device_wait_service.h` (added)
- `g2/components/bootloader/application_storage/info_read_rom_thunk.S` (added)
- `g2/components/bootloader/application_storage/storage_callbacks.c` (modified)
- `g2/components/bootloader/init_table/init_table.c` (added)
- `g2/components/bootloader/init_table/init_table.h` (added)
- `g2/components/bootloader/init_table/sort_cut.S` (added)
- `g2/components/bootloader/nor_mspi_init/control_remaining.c` (modified)
- `g2/components/bootloader/nor_mspi_init/control_remaining.h` (modified)
- `g2/components/bootloader/nor_mspi_init/control_request_extension.c` (added)
- `g2/components/bootloader/nor_mspi_init/control_request_extension.h` (added)
- `g2/components/bootloader/nor_mspi_queue/mspi_pause_dma.c` (added)
- `g2/components/bootloader/nor_mspi_queue/mspi_pause_dma.h` (added)
- `g2/components/bootloader/platform_startup/delay_math.S` (added)
- `g2/components/bootloader/platform_startup/local_providers.S` (added)
- `g2/components/bootloader/platform_startup/local_providers.h` (added)

## Evidence and limits

The immutable `8cd9ed1a115ec00bfbed9f58c4e118b3250efb96b7e8ee88e57c070b215fc1db` ELF still matches its saved hash. Its seven passing modeled cases cover normal/update, malformed updates, and interruption/reboot; union observed original instruction bytes:30,814. The current mutable build ELF instead hashes `3234118f1f93c53ac3354bb23641c00b5e975062b408265b2f6a2ea6a7f4ca0e`. The current normal/update receipt matches the newer ELF and passes2 cases, but the current malformed-update receipt still identifies8cd9. The integrated manifest and seven-case summary identify the older immutable image; their conclusions must not be transferred wholesale to the newer image.

Direct INFO-service evidence reports8,064 dispatch cases,4 null cases and2 thunk cases PASS (8,070 total); the integrated prose still says8,068, a reporting discrepancy. Requests31/33 independently pass20 cases with native critical-save assembly; the formerly copied stock critical leaf has been removed from that fixture. The972-case tail suite does not exercise the newly routed31/33 switch cases.

Initializer source still has a sort-provider cut; source counts do not prove that algorithm is reconstructed. Remaining HAL controls26–27,29–30,34, initialization callbacks, timing/XIP and asynchronous runtime paths remain source closure work. Resident ROM internals, physical power failure/timing, hardware boot and byte equality remain unverified.

This scan ran no generator, build, emulator or hardware operation and changed only this new report/snapshot directory. Concurrent source work, staging and previous evidence were preserved. `snapshot.json` records actual source hashes and selected receipt contents; `git-status.txt` records the live Git view.
