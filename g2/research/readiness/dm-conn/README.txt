OpenCFW G2 Cordio dm_conn.c bounded readiness probe (corrected v2)

Outcome
-------
* Packetcraft r20.05c source/dependency identity is commit 3656312d..., tree 0a76c7dd..., blob 746a7c10..., SHA-256 4bc0ba34.... The source blob is unchanged across r20.05 through r20.05c.
* The translation unit inventories 61 source functions. Os/O1 compile successfully against the exact r20.05c headers; 51 standalone function symbols remain after compiler inlining.
* Thirty external provider seams are enumerated and stubbed. The authored live entry calls DmConnInit. Links deliberately omit section GC: Os retains 3,586 text and 4,800 BSS bytes; O1 retains 3,862 text and 4,800 BSS bytes. Both have zero undefined symbols, so closure is non-vacuous.
* No stock/Ambiq ABI source shim was mechanically required for this bounded readiness build.
* Nine conservative Cordio anchors cover 3,652 stock bytes. The final three are corrected for source-line drift: 0x4B6F28 DmConnPeerRpa, 0x4B707C DmConnLocalRpa, and 0x4B71DC DmConnSetIdle. A provisional 606-byte anchor at 0x5D2BAE is rejected: it is unrelated product math that uses the retained path address as arithmetic data, not dm_conn source.
* Stock retains IAR-style path/line instrumentation; broad compiler matrices and normalized comparisons remain deferred.

Packaging
---------
Contains compact ledgers, hashes, timings, source-function inventory, README, and the independently authored closure shim only. Excludes firmware, upstream/proprietary source, objects, ELFs, decompilation, maps, and caches. Stock range ends are exclusive. This v2 changes anchor labels and the corresponding size-ledger rows only; build and closure results are preserved from the verified v1 probe without rerunning compilation.
