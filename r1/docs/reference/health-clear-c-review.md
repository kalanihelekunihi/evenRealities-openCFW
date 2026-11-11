# R1 clear-all storage orchestration in C

`r1_health_clear_all_caches` now implements native `0x8b184` in ordinary C. It logs start, cleans a nonnull FlashDB provider, requests sleep-history deletion, captures the timezone halfword and local-day timestamp, then resets six existing caches in order. Each accessor is live and nullable. It writes a zeroed 24-byte sync record and logs completion regardless of service return values.

The four scalar caches clear bytes 0..71 and 75..79, then store offset at 72 and day at 80. Activity clears 576 bytes and stores offset 576/day 580. HRV clears 144 bytes and 147..152, then stores offset 144/day 156. Other bytes remain intact. Aliased and unaligned provider pointers retain the same ordered behavior as stock.

The database accessor at `0x70028` returns the existing database owner. It adds no storage and leaves every prior allocated section of the database-initialization object unchanged. The clear-all unit introduces no persistent state.

Validation passes 18,432 stock/C comparisons covering all 328 native instruction bytes, every nullable-cache combination, both database states, timezone truncation, day boundaries, logging modes, pointer alignment/aliasing and saved-register/mask/stack guards. Another 54 comparisons execute the actual six cache accessors, database accessor/owner and memory-clear routines. Seven compiled defects are rejected.

The final normal build compiles 863 units without duplicate strong symbols, leaving 64 application imports and 22 bootloader imports. Two imports close; sleep-history deletion becomes an explicit unresolved dependency. The tested clear-all/database objects match the build, and 851 other prior nongenerated objects remain identical. The manifest adds one unit; source-plan selections remain unchanged.

[The receipt](health-clear-c-review.json) records evidence hashes and proof boundaries. FlashDB cleaning, sleep deletion, time/logging and sync-record persistence remain modeled service boundaries. Physical erase, power-loss behavior, concurrency, final source linking and boot remain unverified.
