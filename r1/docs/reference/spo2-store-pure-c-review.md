# R1 SpO2 sample storage in C

The writer at `0x5bb2c` now uses ordinary C. It captures the hour, reloads value/timestamp for average kind1, preserves maximum/minimum with the zero-minimum sentinel, stores the byte average and five-byte latest sample, and keeps live diagnostic mode/sample/cache reads. Common declarations move before their C users; no providers or state are added.

REA matches the 224-byte extent. All 222 reachable instruction bytes execute across 34,586 stock/C comparisons; the isolated branch at `0x5bc02` is unreachable. Logging branches, changing modes, provider mutations, sample/cache aliases, null input and every hour are covered. Seven compiled defects are rejected. Another 864 HR/HRV/SpO2 chain and 12 activity-reset checks pass, along with 25,946 stress and 43,226 temperature regression comparisons.

The final serial normal build compiles 862 units with 63 application and 22 bootloader imports, without failures or duplicate strong symbols. Two earlier builds had GCC processes terminate with 137; a fresh `--jobs 1` build completed. The final sample object equals the tested object. The other 851 prior nongenerated objects are identical. HR/HRV assembly code/relocations, storage sections, and stress/temperature C source remain unchanged. Manifest, cache layout and source plan are unchanged; R1 source checking passes. Compiler-provided four-byte SpO2 section alignment removes its embedded-pool dependency.

Direct hour/average/log providers are modeled. The chain executes actual writer/accessor/latest/reset and memory-clear code with modeled hour/average and disabled logging; HR/HRV assembly is aligned4 in that fixture. Void return, caller scratch, private frames and APSR are excluded; saved integer/FP state, SP, masks and guards are checked. Atomic access widths, concurrency, final startup/scatter integration, complete application linking, physical sensors and boot remain unverified.

See the [receipt](spo2-store-pure-c-review.json) for hashes and limits. Probes are under `build/goal-r1-spo2-store-pure-c/`.
