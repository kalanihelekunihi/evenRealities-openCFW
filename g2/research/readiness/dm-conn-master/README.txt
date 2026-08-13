OpenCFW Cordio dm_conn_master.c bounded readiness probe

Outcome
-------
* Official AmbiqSuite R4.4.1 dm_conn_master.c is the strongest authenticated candidate and is byte-identical to Packetcraft r20.05 through r20.05c. The official dm_conn.h, dm_dev.h, and l2c_api.h inputs are also byte-identical; one source build covers those bytes.
* The verified build uses the complete public r20.05c dependency closure. Official R4.4.1 dm_main.h, dm_api.h, and wsf_os.h differ and are authenticated as identity-only inputs, so this artifact does not claim a fully exact R4.4.1 configuration build.
* The translation unit inventories all 6 source functions, including typed-return DmConnOpen, and compiles under Os/O1 with the same 10 provider seams.
* A live entry calls DmConnOpen(0,1,0,NULL); its dmConnOpenAccept provider returns zero. Links deliberately omit section GC, retaining the full module and action table. Both profiles retain 206 text, 0 data, and 4,096 authored dmCb BSS bytes, with zero undefined symbols.
* No stock/Ambiq ABI source shim was required. The authored string declaration shim supports the freestanding public include closure.
* Caveat: no defensible retained-path or semantic stock anchor was found for this translation unit in the current authenticated manifests. This proves exact official/public source identity and build readiness, not stock inclusion or an address mapping.

Packaging
---------
Contains compact identities, inventories, dependency/provider ledgers, timings, build configuration, README, and independently authored stubs/shim only. Excludes licensed upstream source/header bytes, firmware, objects, ELFs, decompilation, disassembly, link maps, and caches.
