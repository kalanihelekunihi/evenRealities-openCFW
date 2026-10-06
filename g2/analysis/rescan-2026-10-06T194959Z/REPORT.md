# Current source rescan

Snapshot: 2026-10-06T19:49:59.091189+00:00. Baseline: `g2/analysis/rescan-2026-10-06T190206Z`.

- `g2/components/bootloader`: **111 → 125** C/header/assembly files.
- `g2/components/foundation`: **89 → 89** C/header/assembly files.
- Added: **14**; modified: **4**; removed: **0**; ignored source files: **0**.

Counts include headers, vendored source and tests; they do not measure firmware completeness.

## Changed source files

- `g2/components/bootloader/dfu_task/context.c` (modified)
- `g2/components/bootloader/dfu_task/runtime_context.c` (added)
- `g2/components/bootloader/dfu_task/runtime_context.h` (added)
- `g2/components/bootloader/manager_task/manager_handshake.c` (modified)
- `g2/components/bootloader/manager_task/manager_task.c` (modified)
- `g2/components/bootloader/thread_creation/event_waiter_wake.c` (added)
- `g2/components/bootloader/thread_creation/event_waiter_wake.h` (added)
- `g2/components/bootloader/thread_creation/queue_buffer_release.c` (added)
- `g2/components/bootloader/thread_creation/queue_buffer_release.h` (added)
- `g2/components/bootloader/thread_creation/queue_send.c` (added)
- `g2/components/bootloader/thread_creation/queue_send.h` (added)
- `g2/components/bootloader/thread_creation/resource_creators.c` (added)
- `g2/components/bootloader/thread_creation/resource_creators.h` (added)
- `g2/components/bootloader/thread_creation/task_entry_adapters.S` (modified)
- `g2/components/bootloader/thread_creation/timer_commands.c` (added)
- `g2/components/bootloader/thread_creation/timer_commands.h` (added)
- `g2/components/bootloader/thread_creation/timer_expiration.c` (added)
- `g2/components/bootloader/thread_creation/timer_expiration.h` (added)

## Functional evidence

The current integrated checkpoint records a passing source-driven reset → scheduler → manager → DFU queue-consumption comparison (four policy cases, 9,632 distinct original instruction bytes). Timer/mutex constructors now execute source rather than controlled handles. Queue send, waiter wake, priority release, timer command drain and expiration/rollover are now source providers.

The combined regression checkpoint records PASS with no current C/header/assembly receipt-binding mismatches. This scan inspected saved evidence; it did not rerun builds or emulation. See `../bootloader-completion-2026-10-06/integrated-status/REPORT.md` for adapter/stub limits and the documented aggregate target-name repair.

Normal DFU stops before runtime-enable 0x42ddf2; update DFU stops before file-open 0x4153a4. Hardware boot, full source completeness and byte equality remain unproved.

No existing source, index, campaign state or hardware was changed by this scan.
