# R1 sleep-sector finalization in ordinary C

`r1_sleep_sector_finalize` at `0x901e4` now uses C. It captures the completion-marker target before querying the sector count, scans the counter at offset 8 of every sector header, logs the next count, then writes a 16-byte marker. The target remains fixed while partition/read/write providers reload at the native boundaries.

The next count is the unsigned minimum plus one. An empty scan or all-`FFFFFFFF` counters produces one. The marker words are `CCFFAABB`, `66889977`, count and zero. Header scratch initializes once and retains bytes across partial or failed reads. Read status is ignored; only a zero write status returns success. The scan does not validate header magic or CRCs.

Validation passes 19,280 stock/C comparisons covering all 192 native instruction bytes, every byte-sized sector count, unsigned/empty counter cases, partial reads, count-query and live provider changes, logging variants, address wrap and write statuses. Another 1,458 cases execute the C sector-write/finalize chain with actual sector-count, CRC and memory-clear routines. Eight compiled defects are rejected.

The tested finalizer and write objects match the normal build. The other 852 prior nongenerated objects remain identical. The strong-symbol set, manifest, source-plan selections, persistent state and imports are unchanged: 863 compiled units, 63 application imports and 22 bootloader imports.

[The receipt](sleep-sector-finalize-pure-c-review.json) records hashes and proof boundaries. FAL I/O and logging remain modeled. Physical NOR programming, power-loss behavior, concurrency, final source linking and boot remain unverified. The subsequent [C selector/fallback conversion](sleep-sector-select-pure-c-review.md) closes those assembly entries and adds a full record-store/flash-model comparison. Other sleep-storage assembly remains separate work.
