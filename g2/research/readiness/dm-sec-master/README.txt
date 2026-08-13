OpenCFW Cordio dm_sec_master.c bounded readiness probe

Outcome
-------
* Official AmbiqSuite R4.4.1 dm_sec_master.c is the strongest authenticated candidate. Its source, dm_sec.h, dm_conn.h, and smp_api.h are byte-identical to Packetcraft r20.05 through r20.05c; one source build is sufficient for those bytes.
* The verified build uses the exact public r20.05c dependency closure. Supplied R4.4.1 wsf_msg.h, dm_main.h, and dm_api.h differ and are authenticated but were not used, so a fully exact R4.4.1 configuration is not claimed.
* The translation unit inventories 3 source functions and compiles under Os/O1 with 8 identical provider seams.
* A live entry calls DmSmpEncryptReq(0,0,NULL); dmConnCcbById returns NULL, making execution bounded. Links deliberately omit section GC. Os retains 196 text and 4,112 BSS bytes; O1 retains 176 text and 4,112 BSS bytes. Both have zero undefined symbols.
* No stock/Ambiq ABI source shim was required. An authored string declaration shim supplies the freestanding memcpy prototype.
* Caveat: current authenticated Cordio mapping has no retained-path or semantic anchor for dm_sec_master.c. This proves official/public source identity and build readiness, not inclusion in stock firmware.

Packaging
---------
Contains compact identities, ledgers, timings, config, README, and independently authored stubs/shim only. Excludes licensed upstream source/header bytes, firmware, objects, ELFs, decompilation, disassembly, maps, and caches.
