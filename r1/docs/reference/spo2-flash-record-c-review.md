# R1 SpO2 FlashDB record merge C review, 2026-11-11

`r1/src/application/runtime/native_spo2_flash_record_merge.c` owns the stock
`0x446b4` callback. It reads a 128-byte record, filters future and current-day
entries, places a nonzero three-byte SpO2 sample into an hourly builder
slot, and updates the latest timestamp. A day or UTC-offset change flushes
and resets the builder. Calendar hour zero belongs to the previous day and
slot 23, matching the stock control flow.

The ignored probe `build/r1-spo2-flash-20261111/compare.py` executed 600
deterministic paired stock/C cases. It compared return value, 148 builder
bytes, and reset/flush/log calls; all cases matched. FlashDB, clock,
calendar conversion, logging, reset, and flush were identically stubbed,
so those dependencies and board behavior remain unverified.

The R1 manifest passes `sources-check` with 985 units and 772 source files.
All 903 application and 82 bootloader units compile and compose without
duplicate strong symbols. The strict bootloader link and C vector pass. The
strict application link still has 16 undefined functions and uses 628,464
of 696,320 available flash bytes. Receipts:

- `build/sources-r1-spo2-flash-final-20261111/report.json`
- `build/r1-link-spo2-flash-final-20261111/report.json`
- `build/r1-boot-link-spo2-flash-final-20261111/report.json`

The binding removes `r1_health_sync_provider_000446b4` and adds 496 flash
bytes from the preceding HRV callback checkpoint. It does not prove
complete C firmware, stock byte identity, or safe hardware execution.
