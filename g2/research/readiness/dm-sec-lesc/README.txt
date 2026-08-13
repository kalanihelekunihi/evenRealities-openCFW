OpenCFW Cordio dm_sec_lesc.c bounded readiness probe

Outcome
-------
* Official AmbiqSuite R4.4.1 dm_sec_lesc.c is the strongest authenticated candidate. Its source, dm_sec.h, dm_conn.h, and smp_api.h are byte-identical to Packetcraft r20.05 through r20.05c; one source build is sufficient for those bytes.
* The verified build uses the exact public r20.05c dependency closure. Supplied R4.4.1 dm_api.h differs and is authenticated but was not used, so a fully exact R4.4.1 configuration is not claimed.
* The translation unit inventories 11 source functions and compiles under Os/O1 with 18 identical provider seams.
* A live entry calls DmSecLescInit and writes the LESC interface slot. Links deliberately omit section GC. Os retains 774 text and 5,220 BSS bytes; O1 retains 822 text and 5,220 BSS bytes. Both have zero undefined symbols.
* No stock/Ambiq ABI source shim was required. An independently authored string declaration shim supplies freestanding prototypes and is included for reproducibility.
* Caveat: current authenticated Cordio mapping has no retained-path or semantic anchor for dm_sec_lesc.c. This proves official/public source identity and build readiness, not inclusion in stock firmware.

Packaging
---------
Contains compact identities, ledgers, timings, config, README, and independently authored stubs/shim only. Excludes licensed upstream source/header bytes, firmware, objects, ELFs, decompilation, disassembly, maps, and caches.
