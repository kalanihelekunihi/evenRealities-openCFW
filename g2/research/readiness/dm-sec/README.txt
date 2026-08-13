OpenCFW Cordio dm_sec.c bounded readiness probe

Outcome
-------
* Official AmbiqSuite R4.4.1 dm_sec.c is the strongest authenticated candidate. Its source, dm_sec.h, dm_conn.h, and smp_api.h are byte-identical to Packetcraft r20.05 through r20.05c; one source build is sufficient for those bytes.
* The verified build uses the exact public r20.05c dependency closure. The supplied R4.4.1 dm_api.h differs and is authenticated in the identity ledger but was not used, so a fully exact R4.4.1 configuration is not claimed.
* The translation unit inventories 12 source functions and compiles under Os/O1 with 22 identical provider seams.
* A live entry calls DmSecInit, writes the security interface slot, and initializes both local key pointers to authored calc128Zeros storage. Links deliberately omit section GC. Os retains 762 text and 9,240 BSS bytes; O1 retains 758 text and 9,240 BSS bytes. Both have zero undefined symbols.
* No stock/Ambiq ABI source shim was required. An independently authored string declaration shim supplies freestanding prototypes and is included for reproducibility.
* Caveat: current authenticated Cordio mapping has no retained-path or semantic anchor for dm_sec.c. This proves official/public source identity and build readiness, not inclusion in stock firmware.

Packaging
---------
Contains compact identities, ledgers, timings, config, README, and independently authored stubs/shim only. Excludes licensed upstream source/header bytes, firmware, objects, ELFs, decompilation, disassembly, maps, and caches.
