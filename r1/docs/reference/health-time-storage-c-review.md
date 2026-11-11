# Time-transition storage callback in C

The remaining database subscription at `0x5e698` now resolves to a typed C callback with a 12-byte event: signed old/new offset halfwords, then old/new timestamp words. Null input returns immediately. The initializer now declares this argument-bearing interface; its compiled object is unchanged. Existing FlashDB, sync-record, replay, calendar, cache-reset and storage owners are reused.

The callback preserves these stock distinctions:

- A backward jump of at least 3,600 seconds cleans FlashDB and zeros sync-record words 0, 1, 3 and 4, preserving words 2 and 5.
- An old timestamp below `0x38640900` and new timestamp at or above it converts the new local calendar to midnight, allocates/clears 128 bytes, replays that day's records and frees the buffer. Allocation failure logs and returns; failed conversion status is ignored as in stock. If both timestamps are below the threshold, it logs and skips the day check.
- For an old valid timestamp, local-day comparison reloads event fields after preceding providers. Signed offsets are multiplied by 60, added with unsigned 32-bit wrap, then divided unsigned by 86,400. Crossing a day resets all enabled caches using the current day-start/offset providers, rather than the incoming event's offset.
- Only a new timestamp strictly above the threshold enters future-sync clamping. It clamps words 0, 1, 3 and 4 and writes only when at least one changes. Record-read failure is ignored, but the 24-byte temporary starts cleared.

The [REA literal read](health-time-storage-c-rea.json) confirms the threshold, recovery log pointers and replay callback address. Logging retains stock strings, levels, live mode reads and distinct SDK metadata for sync-record updates.

The [machine-readable receipt](health-time-storage-c-review.json) records 385 direct stock/C comparisons covering threshold/backward-time edges, signed offset extremes and unsigned wrap, partial/failed record reads, all four-field clamp masks, allocation/conversion failures, synthetic reset masks and event mutation during FlashDB clean. Actual C resets and cache owners execute; FlashDB, sync-record, clock/calendar, allocation and logging boundaries are modeled. Direct query tests validate replay identity/buffer but do not execute replay.

Another 457 startup comparisons dispatch both actual registered callback pointers after actual C startup, replay and snapshot restoration. They execute 256 C time callbacks, 162 hourly appends, 313 replay calls, 163 snapshot calls and 1,878 cache writes. Sync-record read/write and external service boundaries remain modeled; replay and reset bodies execute actual C.

Six separately compiled defects fail runtime assertions: an incorrect backward-jump boundary, incorrect first-valid-time boundary, unsigned timezone interpretation, wrong clamp fields, stale event fields and omitted day-crossing resets. All 737 prior objects remain identical. `make sources-check` passes; 664 application and 74 bootloader units compile/compose without failures or duplicate strong symbols. Application imports decrease from 160 to 159; bootloader imports remain 34.

Both database subscription bodies now have C providers. The four lower clock-invalid record-dispatch providers introduced by hourly reads remain unresolved, alongside other firmware dependencies. This does not prove physical persistence, asynchronous interrupt behavior, arbitrary pointer/fault cases or complete firmware linkage. No exact source-plan selection or image-integration claim is added.
