# Complete activity-storage unit in C

The activity writer at `0x5aa14` now uses ordinary C alongside its existing C bucket helper. It reloads the timestamp for the second bucket call, rejects either unsigned bucket at or above 144, logs cross-bucket records, and updates only the start row. Three separate volatile writes preserve the low 12-bit, middle 10-bit and upper 10-bit fields, including local wrap and payload aliases. Diagnostics retain their live reads and original metadata.

REA matches all 246 stock instruction bytes; every byte executes across 41,627 comparisons. Cache/payload memory widths, order and values match across every row, invalid wide indices, packed-field wraps, null input, aliases and bucket/mode/logger mutations. Nine compiled defects are rejected. Another 936 real RTC/calendar and 2,594 activity-caller comparisons pass with only logging modeled. The probes no longer force activity assembly alignment.

Both functions in `native_activity_storage.c` are now C. The bucket helper's code and relocations and shared diagnostic strings remain unchanged. The unit explicitly selects its SRAM unaligned-access requirement. No persistent state is added. The serial normal build compiles 862 units with 63 application and 22 bootloader imports, no failures or duplicate strong symbols. Its object equals the probe. The other 851 prior nongenerated objects, cache layout and source plan remain identical; R1 source checking passes.

The known direct caller discards the writer result by loading 4 before the throttle tail call. Void return, caller scratch, private frames and APSR are excluded; indirect/nonstandard ABI consumers are not exhaustively proven. Saved integer/FP state, SP, masks, FPSCR and guards are checked. Physical atomicity/concurrency, hardware faults, full application linking, startup/scatter integration, physical activity sensors/clock and boot remain unverified.

See the [receipt](activity-store-pure-c-review.json) for hashes. Probes and the direct-call scan are under `build/goal-r1-activity-store-pure-c/`.
