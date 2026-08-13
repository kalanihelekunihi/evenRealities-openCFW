OpenCFW Cordio dm_dev_priv.c bounded readiness probe

Outcome
-------
* Packetcraft r20.05c is the selected exact public candidate. Its dm_dev_priv.c blob is identical at the authenticated r20.05 endpoint.
* The translation unit inventories 18 source functions; all 18 remain standalone in Os and O1. The exact used closure is 18 inputs (source, 16 upstream headers, and an independently authored string declaration shim).
* Twenty-four provider seams are enumerated. A live entry calls DmDevPrivInit, exercising task-lock/unlock and writes into authored dmFcnIfTbl/dmDevCb storage. Links deliberately omit section GC. Os retains 1,422 text and 5,416 BSS bytes; O1 retains 1,478 text and 5,416 BSS bytes. Both have zero undefined symbols.
* No stock/Ambiq ABI source shim was mechanically required.
* Caveat: the current authenticated Cordio map contains no retained-path or semantic anchor for dm_dev_priv.c. This artifact proves public-source identity and build/closure readiness, not inclusion in stock firmware.

Packaging
---------
Contains compact identities, ledgers, timings, configuration, README, and independently authored stubs only. Excludes firmware, proprietary/upstream source and header bytes, objects, ELFs, decompilation, disassembly, maps, and caches.
