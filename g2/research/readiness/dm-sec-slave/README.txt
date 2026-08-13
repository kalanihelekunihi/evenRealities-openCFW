OpenCFW Cordio dm_sec_slave.c bounded readiness probe

Outcome
-------
* Official AmbiqSuite R4.4.1 dm_sec_slave.c is the strongest authenticated candidate. Its source, dm_sec.h, and smp_api.h are byte-identical to Packetcraft r20.05 through r20.05c; one source build is sufficient for those bytes.
* The verified build uses the exact public r20.05c dependency closure. Supplied R4.4.1 wsf_msg.h, dm_main.h, and dm_api.h differ and are authenticated but were not used, so a fully exact R4.4.1 configuration is not claimed.
* The translation unit inventories 3 source functions and compiles under Os/O1 with 5 identical provider seams.
* A live entry calls DmSecSlaveReq(1,0); the authored WsfMsgAlloc provider returns NULL, making execution bounded. Links deliberately omit section GC. Os retains 190 text and 4,096 BSS bytes; O1 retains 170 text and 4,096 BSS bytes. Both have zero undefined symbols.
* No stock/Ambiq ABI source shim was required.
* Caveat: current authenticated Cordio mapping has no retained-path or semantic anchor for dm_sec_slave.c. This proves official/public source identity and build readiness, not inclusion in stock firmware.

Packaging
---------
Contains compact identities, ledgers, timings, config, README, and independently authored stubs only. Excludes licensed upstream source/header bytes, firmware, objects, ELFs, decompilation, disassembly, maps, and caches.
