# R1 HRV FlashDB record merge C review, 2026-11-11

`r1/src/application/runtime/native_hrv_flash_record_merge.c` owns the stock
`0x41438` callback. It reads a 128-byte record, filters future and current-day
entries, places a nonzero six-byte HRV sample into an hourly builder slot,
and updates the latest timestamp. A day or UTC-offset change flushes and
resets the builder. Calendar hour zero belongs to the previous day and slot
23, matching the stock control flow.

The ignored probe `build/r1-hrv-flash-20261111/compare.py` executed 600
deterministic paired stock/C cases. It compared return value, 232 builder
bytes, and reset/flush/log calls; all cases matched. FlashDB, clock,
calendar conversion, logging, reset, and flush were identically stubbed,
so those dependencies and board behavior remain unverified.

The R1 manifest passes `sources-check` with 984 units and 771 source files.
All 902 application and 82 bootloader units compile and compose without
duplicate strong symbols. The strict bootloader link and C vector pass. The
strict application link still has 17 undefined functions and uses 627,968
of 696,320 available flash bytes. Receipts:

- `build/sources-r1-hrv-flash-final-20261111/report.json`
- `build/r1-link-hrv-flash-final-20261111/report.json`
- `build/r1-boot-link-hrv-flash-final-20261111/report.json`

The binding removes `r1_health_sync_provider_00041438` and adds 496 flash
bytes from the preceding heart-rate callback checkpoint. It does not prove
complete C firmware, stock byte identity, or safe hardware execution.
