OpenCFW Cordio dm_priv.c bounded readiness probe

Outcome
-------
* Official AmbiqSuite R4.4.1 dm_priv.c is the strongest authenticated candidate. Its source and dm_priv.h bytes are exactly identical to Packetcraft r20.05 through r20.05c, so one source build is sufficient for those bytes.
* The verified build uses the exact public r20.05c dependency closure. Two supplied R4.4.1 supporting headers (dm_api.h and dm_main.h) differ and are authenticated in the identity ledger but were not used; therefore a fully exact R4.4.1 configuration is not claimed.
* The translation unit inventories 25 source functions. Os/O1 compile with 24 identical provider seams.
* A live entry calls DmPrivInit, executes task lock/unlock, and writes both privacy interface slots in authored dmFcnIfTbl storage. Links deliberately omit section GC. Os retains 1,246 text and 5,148 BSS bytes; O1 retains 1,278 text and 5,148 BSS bytes. Both have zero undefined symbols.
* No stock/Ambiq ABI source shim was required. A string declaration shim supplies freestanding memcmp/memcpy/memset prototypes and is included for reproducibility.
* Caveat: current authenticated Cordio mapping has no retained-path or semantic anchor for dm_priv.c. This proves official/public source identity and build readiness, not inclusion in stock firmware.

Packaging
---------
Contains compact identities, ledgers, timings, config, README, and independently authored stubs/shim only. Excludes licensed upstream source/header bytes, firmware, objects, ELFs, decompilation, disassembly, maps, and caches.
