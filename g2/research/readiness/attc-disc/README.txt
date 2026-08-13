OpenCFW G2 Cordio attc_disc.c bounded readiness probe

Outcome
-------
* Four retained-path anchors conservatively bound 2,154 stock bytes: attcDiscProcDescPair, attcDiscProcCharDecl, AttcDiscServiceCmpl, and AttcDiscCharCmpl.
* After previously completed tranches are removed, attc_disc.c ranks second among remaining public Packetcraft modules by anchored bytes, behind dm_conn.c.
* Packetcraft r20.05 is the authenticated implementation candidate. AmbiqSuite 2.5.1 is materially older: public r20.05 adds included-service discovery support (three source functions), and stock line constants align with r20.05 rather than the older copy.
* The r20.05 source inventories 18 functions, including the first static helper attcUuidCmp. Only the four current anchors receive comparison spans; all remaining functions stay explicitly outside the conservative ledger. attcDiscProcIncSvc, AttcDiscIncSvcStart, and AttcDiscIncSvcCmpl are pending stock closure; this artifact does not classify them as dead-stripped.
* Os and O1 compile with tracing enabled. Eleven external providers are enumerated, and isolated closure links resolve all with zero undefined symbols.
* GCC folds several static workers into public completion routines. Stock also retains IAR-style path/line trace expansion, so a broad matrix and normalized comparisons were intentionally deferred.

Recommendation
--------------
Preserve the four proven spans and use included-service call topology plus the control-block state machine to bound the remaining r20.05 functions. Model the IAR trace/logger seam before expanding compiler profiles.

Packaging
---------
The archive contains identities, hashes, ledgers, timings, version evidence, and independently authored closure shims only. It excludes firmware, upstream source, decompilation, object, ELF, and cache bytes. Stock range ends are exclusive.
