# R1 HR sample writer in C

The writer at `0x5ad90` now uses ordinary C, sharing the existing HR cache owner. It retains null input handling, hour capture followed by live average-kind0 inputs, byte extrema with the zero-minimum sentinel, low-byte stored average, five-byte latest metadata and live diagnostics across providers.

REA matches the 220-byte stock body. All 220 instruction bytes execute across 34,586 stock/C comparisons covering all log branches, mode sequences, provider mutations, sample/cache aliases, null input and every hour. Seven compiled defects are rejected. Another 864 HR/HRV/SpO2 chain and 12 activity-reset checks pass, as do 103,758 comparisons for the other three C writers.

The serial normal build compiles 862 units with 63 application and 22 bootloader imports, without failures or duplicate strong symbols. Its sample object equals the separately compiled probe. The other 851 prior nongenerated objects are identical. All other C writer bodies, HRV assembly code/relocations and storage sections remain unchanged. Manifest, source plan and cache layout are unchanged; R1 source checking passes. Compiler-provided four-byte HR section alignment removes its embedded-pool dependency. HRV is the only remaining assembly writer in this unit.

Direct hour/average/log providers are modeled. The chain executes actual writer/accessor/latest/reset and memory-clear code with modeled hour/average and disabled logging; HRV assembly is aligned4 in that fixture. Void return, caller scratch, private frames and APSR are excluded; saved integer/FP state, SP, masks and guards are checked. Atomic access widths, concurrency, complete application linking, final startup/scatter integration, physical sensors and boot remain unverified.

See the [receipt](hr-store-pure-c-review.json) for hashes. Probes are under `build/goal-r1-hr-store-pure-c/`.
