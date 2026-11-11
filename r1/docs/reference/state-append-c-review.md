# R1 previous-state append in C

The native two-argument flash append entry at `0x6bbb0` now uses the existing GoMore append algorithm through optional hooks. The seven-argument API remains available with its strict error and capacity semantics. There is one append implementation.

The adapter binds the existing pkey storage, uses live partition/device operations, preserves successful-I/O diagnostics and three-slot selection, and allocates scratch only for compaction. Native fallback to slot zero is an explicit hook policy. The adapter uses 32-bit enums and compile-time structure-size assertions to match the shared core ABI across compiler profiles.

Validation includes 17,370 stock/C comparisons covering all 824 native instruction bytes, 17,922 old/current strict-API comparisons, and 768 manager/worker/payload/append/status/reset chain cases. The fixtures compare flash bytes, operation and log ordering, live callback mutations, and scratch cleanup. Unused imports in the monolithic core are bound only in probes and protected by execution allowlists.

Two deliberate changes improve failure handling: negative FAL status stops subsequent commands, and overflowing lengths or metadata are rejected before writes or erase. Twenty-four I/O scenarios reach nineteen failing-operation stops; six overflow cases issue no write or erase. The caller must provide the rounded source extent; the actual exit caller supplies 736 aligned bytes.

All eight compiled defect variants are rejected, including skipped read-failure stops, wrong slot geometry and removed overflow guards.

The normal source build compiles 862 units with no duplicate strong symbols. The native append import closes, leaving 65 application imports and 22 bootloader imports. The adapter and shared core match the tested objects; 850 other prior nongenerated objects remain byte-for-byte unchanged. The manifest adds one unit with an explicit enum-width flag; source-plan selections remain unchanged.

See [the machine-readable receipt](state-append-c-review.json) for hashes, defect controls and detailed boundaries. This establishes relocatable composition and modeled behavior. Physical flash programming, power-loss atomicity, concurrency, payload production, final application linking and boot remain unverified.
