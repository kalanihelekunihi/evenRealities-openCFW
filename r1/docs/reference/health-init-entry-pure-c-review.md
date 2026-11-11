# Health initialization entries in C

`native_health_init.c` now contains ordinary C for stock entries `0x8a866` (24 bytes) and `0x8d380` (68 bytes). The publisher retains the complete status word while gating on low-byte values 0–3, then sends event `0x1001` with length 1. The service preserves live diagnostic-mode queries and publishes status 1 after diagnostics.

REA bytes match the locked application. All 92 native instruction bytes execute across 2,560 publisher and 2,880 service comparisons. Another 3,456 comparisons execute the publisher/enqueue/memory-movement chain with modeled queue and flags ports. Eight compiled defects are rejected. Saved registers, floating-point state, SP, masks and guards are checked.

The normal serial source build compiles all 862 units with no duplicate strong symbols and unchanged imports (63 application, 22 bootloader). The tested object equals the normal-build object; 851 other prior nongenerated objects are unchanged. The manifest, source plan and cache layout are unchanged.

Callback `0x42840` calls the initialization service without consuming its result. Indirect consumers remain unproven. Caller scratch, void returns, APSR, private frame addresses and the queue record's uninitialized leading word are excluded. The nested publisher retains its frame bridge. Physical sensors, concurrency, scheduler delivery, final application linking, startup and boot remain unverified.

The [machine-readable receipt](health-init-entry-pure-c-review.json) records hashes and checks. Probe scripts and logs are under `build/goal-r1-health-init-entry-pure-c/`; the normal build report is `build/sources-goal-r1-health-init-entry-pure-c/report.json`.
