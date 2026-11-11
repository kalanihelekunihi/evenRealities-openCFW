# Shared R1 health cache ownership

HR, HRV and SpO2 accessors previously allocated separate caches from the existing sample-writer/latest-reader prefixes. Stock uses one base for each: HR `0x2001654c`, HRV `0x200169c0`, SpO2 `0x200165a0`. REA confirms accessor literals and writer pool words. The accessors and resets now share those existing prefixes; six duplicate arrays/gaps totaling 310 definition bytes are removed.

Normal source composition now includes `native_health_cache.ld`. It assembles each prefix with the existing timestamp: HR/SpO2 at offset80, HRV at156, activity at580. The groups retain their cells under linker garbage collection. Resets reference the timestamp owners by name, retaining explicit ownership rather than writing past a bounded prefix to reach a separate object.

All 864 stock/source writer → accessor → latest-reader → reset comparisons pass, including all three cache kinds, edge hours, byte/halfword truncation, full-width averages, timestamp wrap and offset values. Twelve additional activity-reset comparisons pass. Four compiled defects, including restoration of the old duplicate owner, are rejected. These tests exposed and fixed garbage collection of activity offset/gap cells, which otherwise shifted the timestamp.

The normal build compiles 862 units with 63 application and 22 bootloader imports, without failures or duplicate strong symbols. The other 851 prior nongenerated objects are identical. Only the cache C object changes; the manifest adds the cache layout to composition. Source plan remains unchanged; R1 source checking passes. The tested cache object equals the final normal object, and normal relocatable ELF sections independently prove relative cache/timestamp placement.

The test links normal source objects with the production cache layout at controlled native addresses. Existing sample-writer assembly executes with four-byte alignment in the fixture; it remains separate C-conversion work. Hour/average and disabled logging boundaries are modeled; actual packed readers, accessors, resets and memory clear execute. Caller scratch, APSR, private frames and concurrency are excluded. Other health-state ownership, final startup/scatter placement, full application linking and physical sensor/reset behavior remain unverified.

See the [receipt](health-cache-ownership-review.json) for artifact hashes. Probes are under `build/goal-r1-cache-ownership/`.
