# R1 stress sample storage in C

The writer at `0x5bcec` now uses ordinary C. It retains null-input handling, hour capture followed by live average inputs, maximum/minimum updates with the zero-minimum sentinel, low-byte stored average and five-byte latest sample. Logging keeps separate live mode reads, full-width average values and reloads after callbacks. The existing hourly/stress owner is unchanged.

REA matches the 220-byte stock instruction body. All 220 instruction bytes execute across 25,946 paired comparisons, including every log branch, changing mode sequences, provider mutations, null input, every hour, min/max edges and samples aliased with cache rows/latest metadata. Seven compiled defects are rejected. Another 576 temperature/stress writer/read/reset comparisons pass with the shared production layout.

The normal build compiles 862 units with 63 application and 22 bootloader imports, no failures or duplicate strong symbols. The other 851 prior nongenerated objects remain identical. Within the changed unit, all four other sample-writer code sections and relocations, state sections and shared stress text remain identical. Manifest, source plan and cache layout are unchanged; R1 source checking passes. The C stress section has compiler-provided four-byte alignment, removing its former embedded literal-pool dependency.

Direct hour/average/logging providers are modeled. The chain executes actual cache accessors, readers, resets and memory clear, with hour/average, nonzero time status and disabled logging modeled. Temperature assembly remains aligned4 in that fixture. Void return, caller scratch, APSR and private frames are excluded; saved integer/FP state, SP, masks and guards are checked. Atomic access widths, concurrency, final startup/scatter linking, physical sensors and boot remain unverified. The remaining sample-writer assembly is separate work.

See the [receipt](stress-sample-pure-c-review.json) for hashes. Probes are under `build/goal-r1-stress-sample-c/`.
