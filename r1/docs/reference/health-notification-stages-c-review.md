# Health notification stages in C

Four stock application routines now have C implementations under
`r1/src/application/runtime/`: HR `0x8c150` in
`native_health_notification_hr.c`, SpO2 `0x8cd60` in
`native_health_notification_spo2.c`, HRV `0x8c750` in
`native_health_notification_hrv.c`, and activity `0x8baec` in
`native_health_notification_activity.c`. Their former instruction-literal
bodies and embedded string tables were removed from
`native_health_notification_stages.c`; the four replacement units are each
listed once in `r1/src/sources.json`. That file still owns the stage-kind and
pending-byte data and the separate C sleep-report stage.

Each C stage retains its persisted-record word, future-timestamp repair,
three-day FlashDB window, count query, empty-queue fast-forward, 128-byte
scratch allocation, day packet, flash iterator context, offline merge,
live-cache merge and both allocation-failure exits. The first offline-queue
check runs even after a nonzero FlashDB count. The packet layouts are:

| Stage | Record word | Builder bytes | Sample prefix | Caller halfword | Callback word | Offline flag |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| HR | 0 | 148 | 8 | 136 | 140 | 144 |
| SpO2 | 1 | 148 | 11 | 136 | 140 | 144 |
| HRV | 3 | 220 | 44 | 208 | 212 | 216 |
| Activity | 4 | 1,180 | 20 | 1,168 | 1,172 | 1,176 |

The ignored probes at `build/r1-health-hr-c-20261111/verify.py` and its
`verify-spo2.py`, `verify-hrv.py` and `verify-activity.py` variants execute
each locked stock body and each newly linked C body on Cortex-M4 Unicorn.
They stub all calls leaving the stage and compare provider order and
arguments, record writes, FlashDB iterator context, packet bytes excluding
the relocated callback pointer, logging, pending-byte read points,
allocation/free paths, and restored
stack and saved registers. Each stage passes 106 paired cases, 424 in all.
Cases include the timestamp validity threshold, future persisted timestamps,
day boundaries, three-day clamp, zero and nonzero flash counts, empty and
nonempty offline queues, both allocation failures, log modes and varied
caller data. The HR replay caught a skipped unconditional queue check in the
first C draft; the activity replay caught two mismatched allocation log
strings. Both defects were corrected before the final receipts. Providers
themselves are modeled here, so the result does not establish full FlashDB
behavior or physical-device operation.

`build/sources-r1-health-stages-c-final-20261111/report.json` compiles
961/961 application and 82/82 bootloader units with no failures or duplicate
strong symbols. The strict application link at
`build/r1-link-health-stages-c-final-20261111/report.json` has zero undefined
references, a 512-byte vector at `0x27000`, and uses 693,912 of 696,320
flash bytes. The strict bootloader link at
`build/r1-boot-link-health-stages-c-final-20261111/report.json` also passes.
The source check reports all 1,043 R1 units listed; `git diff --check`
passes. A source scan still finds 23 `__asm__` occurrences across nine R1 C
files. Stock byte identity, actual FlashDB/provider composition, stack peak
and device execution remain unverified.
