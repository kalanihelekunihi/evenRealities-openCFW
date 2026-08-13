OpenCFW G2 Cordio smp_db.c bounded readiness probe

Outcome
-------
* smp_db.c has seven defensible retained-path anchors totaling 2,688 stock bytes. It ranks second among remaining public Packetcraft modules by anchored bytes, behind dm_conn.c (4,258 bytes), and was selected as the smaller high-confidence bounded tranche.
* Every retained diagnostic line marker (133, 167, 182, 228, 247, 270, 289, and 333) lands exactly on the corresponding Packetcraft r20.05 statement.
* AmbiqSuite 2.5.1 and Packetcraft r20.05 differ only in the copyright/license header. Their bytes from the first #include through EOF are identical (SHA-256 f2d3c41a...).
* The source translation unit inventories 13 functions. Seven have bounded stock spans here; six remain deliberately unbounded. smpDbAddDevice is a bounded stock function but is inlined into smpDbGetRecord by both GCC probe profiles.
* Os and O1 compile successfully with SMP_DB_MAX_DEVICES=3. Eleven external seams are enumerated and the isolated stub links have zero undefined symbols.
* Candidate sizes differ materially from stock because stock retains path/line instrumentation and likely IAR whole-program trace/logger expansion. No normalized comparison or broad profile matrix was run.

Recommendation
--------------
Preserve the seven proven stock spans and next locate the six unanchored source functions through callers/control-block references. For structural matching, add a no-inline profile only after those boundaries are firm and model the IAR trace/logger seam before attempting broad compiler matrices.

Packaging
---------
The archive contains only identities, hashes, ledgers, timings, and independently authored closure shims. It excludes firmware, upstream source, decompilation, object, ELF, and cache bytes. Stock range ends are exclusive.
