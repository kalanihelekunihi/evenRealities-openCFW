OpenCFW G2 Cordio atts_ccc.c bounded readiness probe

Outcome
-------
* Five retained-path anchors conservatively bound 1,944 stock bytes: attsCccAllocTbl, attsCccGetTbl, attsCccFreeTbl, AttsCccInitTable, and AttsCccClearTable.
* With atts_csf.c and smp_db.c treated as closed prior tranches, atts_ccc.c ranks third among remaining public Packetcraft candidates by anchored bytes, behind dm_conn.c and attc_disc.c.
* Packetcraft r20.05 and AmbiqSuite 2.5.1 differ only in their copyright/license header. Bytes from the first #include through EOF are identical (SHA-256 5c5b7d71...).
* The source translation unit inventories 14 functions. Only the five current retained-path anchors are assigned comparison spans; all others remain explicitly outside this conservative ledger even where adjacency suggests an identity.
* Os and O1 compile with WSF_TRACE_ENABLED=1, WSF_ASSERT_ENABLED=1, and DM_CONN_MAX=3. Seven external seams are enumerated; isolated stub links resolve all of them with zero undefined symbols.
* Static helpers are heavily inlined by GCC. Stock bodies also retain IAR-style path/line assertion and logger expansion, so no broad matrix or normalized comparison was run.

Recommendation
--------------
Locate the remaining source functions through direct callers and the attsCccCb control-block reference before expanding comparisons. Model the IAR assert/logger seam and consider a no-inline profile only after those stock boundaries are independently firm.

Packaging
---------
The archive contains identities, hashes, ledgers, timings, and independently authored closure shims only. It excludes firmware, upstream source, decompilation, object, ELF, and cache bytes. Stock range ends are exclusive; candidate line constants are heuristic corroboration rather than standalone identity claims.
