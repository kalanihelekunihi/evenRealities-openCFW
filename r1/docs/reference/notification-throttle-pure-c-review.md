# Sensor-data notification throttle in C

`native_health_notification_throttle.c` now expresses stock entry `0x8b138` in ordinary C. The existing timestamp word remains the sole state owner. Connection-handle presence gates the operation; the historical helper name does not establish authentication.

After obtaining the clock value, the throttle reads the live timestamp. A zero timestamp, unsigned clock rollback, or elapsed interval of at least 10,800 seconds invokes the five existing notification stages in stock order. Only after all five calls does it commit the original clock result. The input kind is unused. The first four stage prologues overwrite incoming R1 before using it, so their existing two-argument C interfaces receive a defined zero second argument.

REA matches all 72 stock instruction bytes and the first four stage prologues. All throttle instructions execute across 2,832 direct comparisons. Another 4,032 comparisons execute the actual connection predicate and backend thunk. Timestamp reads and writes match in width, order and value, including mutations during the gate, backend and individual stages. Eight compiled defects are rejected. Saved integer/floating-point registers, SP, masks, FPSCR and caller/state guards are checked.

The normal serial source build compiles all 862 units with no duplicate strong symbols and unchanged imports (63 application, 22 bootloader). The tested object equals the normal-build object; 851 other prior nongenerated objects are unchanged. The manifest, source plan and cache layout are unchanged.

The backend getter and notification stages are modeled. Five external direct transfers are recorded; indirect consumers are not exhaustively proven. Void returns, caller scratch, APSR and private frame addresses are excluded. Downstream stage correctness, physical clock/sensors/delivery, concurrency, final application linking and boot remain unverified.

The [machine-readable receipt](notification-throttle-pure-c-review.json) contains source, build and probe hashes. Probe scripts/logs are under `build/goal-r1-notification-throttle-pure-c/`; the final normal-build report is `build/sources-goal-r1-notification-throttle-pure-c-abi/report.json`.
