# Touch ready reader uses ordinary C

`r1_touch_ready_level_read` in `native_touch_transport.c` now initializes a local word to zero, dispatches the input-ready read and returns the resulting low byte. There are no fixed-register declarations or inline assembly left in this unit. The request read/write wrappers remain unchanged.

The only source caller is the ordinary C identity probe, which consumes the low-byte readiness value. Stock already clears that byte before dispatch and ignores provider status. The C migration retires the incidental full-word R3 return and unused upper scratch bytes. This does not change the declared return type or low-byte behavior.

The [receipt](touch-ready-pure-c-review.json) records 928 direct stock/C ready-reader cases and 2,592 complete identity-probe cases. Cases cover all ready-byte values, untouched/partial/full provider writes, raw statuses, incoming scratch seeds, cached-handle changes, early readiness, the last allowed read, exhaustion and late ID-buffer mutations. Production C request, ready-reader and probe functions execute. Requests, operation order, polling count, delays, low-byte results, shared state, stack balance, saved registers and masks agree. Controls with a nonzero initial byte, wrong returned byte or wrong input handle are rejected.

REA returned the raw stock ready-reader bytes. GPIO, power, delay and final registry operations remain modeled; no memory-read hooks are used. Unused scratch bytes and caller-clobbered registers are excluded from this C API proof. Electrical operation, physical identity, timing, arbitrary aliases/faults and concurrency remain unverified.

The normal report is `build/sources-goal-r1-touch-ready-pure-c/report.json`: all 727 units compile without failures or duplicate strong symbols. Imports remain 178 application and 34 bootloader. Only the transport object changed; 726 objects remain unchanged from the probe checkpoint. Both manifests pass `make sources-check`. The broader firmware build and hardware-startup goal remains unfinished.
