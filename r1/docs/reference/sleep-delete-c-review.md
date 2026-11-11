# R1 sleep-header scan and delete-all in C

The native sleep delete dependency now has one C implementation in `native_sleep_record.c`, using the existing C sector-count and erase routines. It adds no persistent state. The scan counts occupied headers; it does not validate record CRCs or payloads.

The scan snapshots the byte-truncated sector count and initializes a 24-byte header once. For each sector it captures the live base plus 16, then reads up to eight headers at stride 24. The read callback reloads for each header. Either word at offset 8 or 12 equal to `FFFFFFFF` ends that sector's scan. The accepted-header count wraps modulo 256. Partial/failed reads retain untouched header bytes, and read status is ignored as stock.

Delete-all erases only when the captured byte count is nonzero, then logs that count. The erase routine takes a fresh sector-count snapshot. Consequently, 256 occupied headers wrap to zero and suppress deletion; compatibility with that native behavior is not a reliability guarantee.

Validation passes 14,680 direct stock/C comparisons across every byte-sized sector count, both empty markers, record-count wrap, failed/partial reads, address wrap, live provider changes and logging/mask variants. All 186 reachable native instruction bytes execute. The scan has a 108-byte extent containing a two-byte unreachable alignment NOP. Another 480 comparisons vary the supplied read prefix on every call. Eight compiled defects are rejected.

A further 972 comparisons execute the actual clear-all path, cache accessors, database owner/getter, memory clear, sleep scan/delete and erase core. FlashDB cleaning, FAL I/O, time/logging and sync-record writes remain modeled boundaries.

The normal build compiles 863 units with 63 application imports and 22 bootloader imports. The tested object matches the normal build, 852 other prior nongenerated objects remain identical, and every prior allocated section/normalized relocation in the changed unit is unchanged. The manifest, source-plan selections and persistent state are unchanged.

[The receipt](sleep-delete-c-review.json) records hashes and proof boundaries. Physical NOR behavior, power-loss behavior, concurrency, final source linking and boot remain unverified. Other sleep-storage assembly remains separate work.
