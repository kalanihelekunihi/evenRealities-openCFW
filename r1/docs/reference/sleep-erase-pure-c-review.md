# R1 sleep-sector erase in ordinary C

Three entries in `native_sleep_record.c` now use C: sector count at `0x8fe14`, erase-all at `0x5b2f8`, and its registered event thunk at `0x8dd88`. The existing three-word sleep context remains the sole state owner.

The count is zero for a null partition; otherwise it is `(partition.length >> 12) & 255`. Erase snapshots that count, then issues a 4 KiB command per sector. It reloads the partition, device and erase callback before each command, preserving live provider changes. It continues after failed erase returns, as stock. A positive count requires valid partition/device providers throughout the operation.

Validation passes 18,651 stock/C comparisons covering all 66 instruction bytes across the three entries. The matrix includes all 256 byte counts, partial sectors, larger sizes that wrap the byte count, address wrap, both interrupt masks, live partition/device/offset/size changes and failed/successful erases. Another 2,880 comparisons execute the existing record-store recovery path with the C count and erase routines. Seven compiled defects are rejected; the invalid callback-slot defect is rejected by an emulated invalid fetch, while the others fail behavioral assertions.

The normal build still compiles 863 units with 64 application imports and 22 bootloader imports. The tested object matches the build. The other 852 prior nongenerated objects remain identical. The two retained parent assembly sections and their normalized relocations are unchanged. The manifest, source-plan selections and persistent state are unchanged.

See [the receipt](sleep-erase-pure-c-review.json) for hashes and coverage boundaries. FAL callbacks remain modeled; physical NOR erase, power-loss behavior, concurrency, final source linking and boot remain unverified. Other sleep-storage assembly remains separate work.
