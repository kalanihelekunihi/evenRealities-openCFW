# Temperature and stress cache layout

Normal composition now places each existing temperature/stress timestamp immediately after its cache. Temperature is an 80-byte prefix plus a four-byte timestamp. Stress remains inside the existing hourly-state owner: five eight-byte hourly rows, then its 80-byte prefix, then the timestamp. The kind5 alias into the beginning of stress remains intact. Both groups retain their cells under section garbage collection.

REA confirms native temperature/stress accessor bases `0x200165f4` and `0x20016670`. All 576 stock/source writer → accessor → hourly-reader → reset comparisons pass. They cover edge hours, sample/average truncation, timestamp extremes and offsets. The full 40-byte hourly-row region remains unchanged after each chain. Three linked layout defects are rejected: the earlier layout and reversed temperature/stress field ordering.

Another 864 HR/HRV/SpO2 chain and 12 activity-reset comparisons pass with the expanded production layout. The normal relocatable ELF independently verifies temperature size84/timestamp80 and hourly-stress size124/cache40/timestamp120. All 862 units compile, with 63 application and 22 bootloader imports, no failures or duplicate strong symbols. All 852 prior nongenerated objects are identical. No C, state definitions, manifest or source plan changes; R1 source checking passes.

The tests execute existing sample-writer assembly and actual C cache accessors/readers/resets/memory clear. Hour/average, nonzero time status and disabled logging are modeled. Writer text is aligned to four bytes in the fixture; its conversion/alignment in a complete final image remains separate work. The existing kind5 alias is preserved structurally; hourly arithmetic is outside this test. Private frames, caller scratch, APSR, concurrency, startup/scatter integration, physical sensors and boot remain unverified.

See the [receipt](scalar-cache-layout-review.json) for hashes and limits. Probes are under `build/goal-r1-scalar-cache-layout/`.
