# R1 crash snapshot builder in C

The public snapshot builder now uses ordinary C, replacing its assembly frame adapter and private helper. Its initialized sum/count outputs remain four bytes apart. Ordered activity packing, signed offset clamping, timestamp wrap, live cache access, partial query writes and the stock scalar return values are preserved.

REA bytes for the 170-byte head at `0x5a324` and 180-byte shared tail at `0x3f47c` match the locked application. All 350 instruction bytes execute across 17,088 stock/C comparisons, covering all hours, nullable caches, metadata gates, partial query outputs and output/cache aliases. Another 216 comparisons execute the actual C initializer, payload getter, snapshot, cache/query owners and CRC chain. Eight compiled defects are rejected.

The normal build compiles 862 units with 63 application and 22 bootloader imports, without failures or duplicate strong symbols. The other 851 prior nongenerated objects are identical; the manifest, source plan and persistent state allocation are unchanged. Direct and integration probe objects equal the normal build object. R1 source checking passes.

The actual getter reports 736 bytes and does not satisfy the initializer's distinct 896-byte copy rule. Its producer lifecycle remains open. Private frame locations, caller scratch registers, APSR, concurrency and faults are outside these comparisons. Physical retention, final image linking and device boot remain unverified; relocatable composition establishes none of those gates.

Machine-readable results and evidence hashes: [review receipt](crash-snapshot-builder-pure-c-review.json). Probe scripts and artifacts are under `build/goal-r1-crash-builder-c/`.
