# R1 temperature sample writer in C

The writer at `0x5be7c` now uses ordinary C. Stored values remain bytes: average, maximum/minimum and latest sample receive no 250-unit adjustment. Diagnostics add250 to live samples, full 32-bit averages and extrema, preserving unsigned wrap. Hour capture, input reloads, zero-minimum handling, changing log modes and callback mutations remain native.

REA matches the 246-byte instruction extent. All 244 reachable bytes execute across 43,226 stock/C comparisons; the isolated branch at `0x5bf66` is unreachable. Tests cover diagnostic overflow, all logging branches, sample/cache aliases, null input and every hour. Seven compiled defects are rejected. Another 576 temperature/stress writer/read/reset checks and 25,946 stock/stress regression comparisons pass.

The normal build compiles 862 units with 63 application and 22 bootloader imports, without failures or duplicate strong symbols. The other 851 prior nongenerated objects are identical. HR/HRV/SpO2 assembly sections and relocations, storage sections and stress function bytes remain unchanged. Manifest, cache layout and source plan remain unchanged; R1 source checking passes. Compiler-provided four-byte alignment removes the temperature writer's embedded literal-pool dependency.

Direct hour/average/log providers are modeled. The chain executes actual C writers, accessors, hourly readers, resets and memory clear, with hour/average, nonzero time status and disabled logging modeled. Void return, caller scratch, private frames and APSR are excluded; saved integer/FP state, SP, masks and guards are checked. Atomic access widths, concurrency, complete application linking, startup/scatter integration, physical sensors and boot remain unverified. Three sample writers still contain assembly.

See the [receipt](temperature-store-pure-c-review.json) for hashes and scope. Probes are under `build/goal-r1-temperature-store-pure-c/`.
