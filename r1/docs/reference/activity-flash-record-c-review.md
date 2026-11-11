# R1 activity FlashDB record merge C review, 2026-11-10

`r1/src/application/runtime/native_activity_flash_record_merge.c` owns the
application callback at stock address `0x3c958`. The callback reads one
128-byte FlashDB activity record, rejects future timestamps, assigns six
packed ten-minute samples to the source-owned day builder, flushes when its
day or UTC offset changes, and tracks the latest accepted timestamp. Stock
routes calendar hour zero to the previous day and to slots 138–143; the C
implementation preserves this behavior.

An ignored Unicorn harness at `build/r1-activity-flash-20261110/compare.py`
ran 400 deterministic paired cases against the locked stock application and
the C object compiled with the manifest's `r1-health-db-c` profile. It
compared return value, all 1,180 builder bytes, and reset/flush/log calls.
The cases vary FlashDB read sizes, future and past timestamps, signed UTC
offsets, calendar hours, day rollover, current-day exclusion, populated
slots, builder day/offset, and log modes. All 400 matched. FlashDB, clock,
calendar conversion, logging, reset, and flush are stubbed with identical
inputs and effects in both executions; this does not validate those
dependencies or board behavior.

`./make.sh sources-check` passes with 982 R1 units, 769 source files, and
zero unbuilt units. The full source build compiles and composes 900/900
application and 82/82 bootloader units with no duplicate strong symbols.
The strict bootloader link passes with a valid C vector. The strict
application link remains incomplete: 19 undefined references and 626,976
of 696,320 available flash bytes used, with no overflow. Receipts:

- `build/sources-r1-activity-flash-final-20261110/report.json`
- `build/r1-link-activity-flash-final-20261110/report.json`
- `build/r1-boot-link-activity-flash-final-20261110/report.json`

The C binding removes `r1_health_sync_provider_0003c958` from the strict
undefined list and adds 568 flash bytes versus the preceding EAT TX
registry checkpoint. These checks do not establish a complete C firmware,
stock byte identity, or safe hardware operation.
