OpenCFW Cordio dm_phy.c bounded readiness probe

Outcome
-------
* Official AmbiqSuite R4.4.1 dm_phy.c is the strongest authenticated candidate. Its source, dm_phy.h, and dm_conn.h are byte-identical to Packetcraft r20.05 through r20.05c; one source build is sufficient for those bytes.
* The verified build uses the exact public r20.05c dependency closure. Supplied R4.4.1 dm_main.h, dm_api.h, and hci_api.h differ and are authenticated but were not used, so a fully exact R4.4.1 configuration is not claimed.
* The translation unit inventories 8 source functions and compiles under Os/O1 with 12 identical provider seams.
* A live entry calls DmPhyInit, executes task lock/unlock, writes the PHY interface slot, and invokes HciSetLeSupFeat. Links deliberately omit section GC. Os retains 322 text and 5,120 BSS bytes; O1 retains 366 text and 5,120 BSS bytes. Both have zero undefined symbols.
* No stock/Ambiq ABI source shim was required.
* Caveat: current authenticated Cordio mapping has no retained-path or semantic anchor for dm_phy.c. This proves official/public source identity and build readiness, not inclusion in stock firmware.

Packaging
---------
Contains compact identities, ledgers, timings, config, README, and independently authored stubs only. Excludes licensed upstream source/header bytes, firmware, objects, ELFs, decompilation, disassembly, maps, and caches.
