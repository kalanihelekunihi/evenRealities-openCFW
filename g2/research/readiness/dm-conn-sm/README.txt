OpenCFW Cordio dm_conn_sm.c bounded readiness probe

Outcome
-------
* Packetcraft r20.05c source and exact include closure are authenticated by commit/tree/blob and SHA-256 ledgers.
* The translation unit contains one source function, dmConnSmExecute, plus an 80-byte constant state table and a 12-byte action-set array.
* Os and O1 compile successfully under the pinned ARM GCC 13.2.1 image. Their only external provider seams are dmConnSmActNone and WsfTrace.
* The authored live entry passes distinct 512-byte CCB/message buffers to dmConnSmExecute. Links deliberately omit section GC. Os retains 234 text and 1,036 BSS bytes; O1 retains 232 text and 1,036 BSS bytes. Both have zero undefined symbols, so closure is non-vacuous.
* No stock/Ambiq ABI source shim was mechanically required for this readiness build.

Packaging
---------
Contains only compact identities, ledgers, timings, configuration, README, and independently authored closure stubs. Excludes firmware, upstream source/header bytes, objects, ELFs, disassembly, maps, and caches.
