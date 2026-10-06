# Current source rescan

Snapshot: 2026-10-06T19:02:06.059670+00:00. Baseline: `g2/analysis/rescan-2026-10-06T182640Z`.

- `g2/components/bootloader`: **92 → 111** C/header/assembly files.
- `g2/components/foundation`: **89 → 89** C/header/assembly files.
- Added: **19**; modified: **1**; removed: **0**; ignored source files: **0**.

Counts include headers, vendored source and tests; they do not measure firmware completeness.

## Changed source directories

- `g2/components/bootloader/clock_manager`: 6 added or modified files.
- `g2/components/bootloader/dfu_task`: 1 added or modified files.
- `g2/components/bootloader/flags_runtime`: 3 added or modified files.
- `g2/components/bootloader/manager_task`: 1 added or modified files.
- `g2/components/bootloader/thread_creation`: 9 added or modified files.

## Evidence and limits

25 saved comparison receipts were created or updated after the baseline. Exact paths and recorded results are in snapshot.json. This scan did not rerun tests or establish that every receipt binds to the latest concurrently edited source.

New source includes clock classes 2/5/6, timer waits, queue reception, thread notifications, event flag operations and manager/DFU handshake helpers. The manager bridge receipt must be interpreted with its explicit exception adapter and peripheral cuts; it is not a hardware boot or full source-built image.

Git index preserved: True. No builds, generator execution, emulation, commits, staging, cleanup or hardware access. Concurrent edits may continue after this timestamp.
