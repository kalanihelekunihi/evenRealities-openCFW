# HR, HRV and SpO2 latest-sample entries in C

The three entries at `0x8d6ac`, `0x8d858` and `0x8e524` now allocate their provider scratch in C. The shared C packing body is unchanged. Null output, per-kind clear widths/padding, eight initialized scratch bytes, partial writes, unaligned timestamp extraction, public output and full 32-bit scalar results are preserved. This translation unit no longer contains inline assembly.

REA matches all 128 stock instruction bytes; every byte executes. All 300 actual packed-provider comparisons and 20,520 controlled-provider comparisons pass. Coverage includes unaligned output, cache aliases, caller-owned stack output, partial writes from zero through eight bytes, arbitrary result bits and callback mutations. Public memory widths/order/values, integer/FP saved state, SP, masks, FPSCR and guards match. Seven compiled defects are rejected. Another 864 actual C writer → public latest entry → reset comparisons and 12 activity-reset checks pass.

Three direct call sites were identified in the get dispatcher. Its functional paths consume scalar/output data, without relying on restored R2/R3 values from the old private frame. Caller-scratch restoration and private frame addresses are excluded from the C interface. Indirect or nonstandard ABI consumers are not exhaustively proven; outputs targeting callee-private stack storage are outside the supported interface.

The serial normal build compiles 862 units with 63 application and 22 bootloader imports, no failures or duplicate strong symbols. The final object equals the probe. The other 851 prior nongenerated objects, manifest, cache layout, source plan and persistent state remain unchanged; R1 source checking passes.

Controlled providers execute BX LR stubs. The chain executes actual C writers, accessors, packed providers, new entries, resets and memory clear; hour/average and disabled logging are modeled. APSR, other caller scratch, physical scheduling/concurrency, SRAM faults, full application linking, startup/scatter integration, physical sensors and boot remain unverified.

See the [receipt](latest-entry-pure-c-review.json) for hashes. Probes and the direct-caller scan are under `build/goal-r1-latest-entry-pure-c/`.
