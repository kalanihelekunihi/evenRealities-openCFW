# R1 heart-rate FlashDB record merge C review, 2026-11-10

`r1/src/application/runtime/native_hr_flash_record_merge.c` owns the stock
callback at `0x40508`. It reads a 128-byte FlashDB record, filters future and
current-day data, merges a nonzero heart-rate sample into one of 24 hourly
builder slots, and flushes/reset the builder on a day or UTC-offset change.
Stock maps calendar hour zero to the previous day and slot 23; the C
callback preserves that rule.

The ignored probe `build/r1-hr-flash-20261110/compare.py` compared the locked
stock routine and the manifest-profile C object in 500 deterministic paired
Unicorn cases. Return value, all 148 builder bytes, and reset/flush/log calls
matched in all cases. Inputs cover FlashDB read lengths, timestamps, time
zones, midnight, current-day filtering, empty and populated samples, reused
slots, builder states, and log modes. The probe stubs FlashDB, clock,
calendar conversion, logging, reset, and flush identically on both sides;
hardware behavior and those dependencies remain unverified.

`./make.sh sources-check` passes with 983 R1 units and 770 source files.
The full source build compiles 901/901 application and 82/82 bootloader units
without duplicate strong symbols. The strict bootloader link and C vector
pass. The strict application link remains incomplete with 18 undefined
functions, 627,472 of 696,320 flash bytes used, and no overflow. Receipts:

- `build/sources-r1-hr-flash-final-20261110/report.json`
- `build/r1-link-hr-flash-final-20261110/report.json`
- `build/r1-boot-link-hr-flash-final-20261110/report.json`

This binding removes `r1_health_sync_provider_00040508` and adds 496 flash
bytes compared with the preceding activity record checkpoint. The link and
paired cases do not establish a complete C firmware or stock byte identity.
