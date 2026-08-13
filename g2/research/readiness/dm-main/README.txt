OpenCFW Cordio dm_main.c dual-lane bounded readiness probe

Outcome
-------
* Stock table counts (dmHciToIdTbl 90; dmEvtCbackLen 92) exactly match authenticated official AmbiqSuite R4.4.1 source, versus 86/90 in public Packetcraft r20.05c. R4.4.1 is the strongest stock-compatible source candidate.
* The official R4.4.1 dm_main.c extract is authenticated by SHA-256 ff9424de... and Git blob 6ffb4e76...; seven supplied official source/header inputs are individually hashed. The public r20.05c baseline is pinned by commit/tree/blob.
* Both lanes inventory the same 16 functions and compile under Os/O1. Both require the same four providers.
* Explicit live entry calls DmHandlerInit(7), updates module-owned dmCb, and invokes HciEvtRegister. No section GC is used. R4.4.1 Os/O1 retain 732/776 text, 84 data, 88 BSS; public r20 retains 744/788 text, 84 data, 88 BSS. All four closures have zero undefined symbols.
* R4.4.1 build caveat: only selected official headers were supplied. Remaining includes fall back to public r20.05c headers, and two board-defined vendor-event maximum lengths use explicit 1-byte structural placeholders. This is a useful source/table lane, not yet a fully exact R4.4.1 configuration reproduction.
* No retained-path dm_main.c entry exists in the current Cordio map; table shape is a strong history/version discriminator but not a per-function address anchor.

Packaging
---------
Contains compact hashes, inventories, closure/config ledgers, README, and independently authored stubs only. It does not redistribute AmbiqSuite or Packetcraft source/header bytes and excludes firmware, objects, ELFs, decompilation, disassembly, maps, and caches.
