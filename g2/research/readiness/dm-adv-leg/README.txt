OpenCFW G2 Cordio dm_adv_leg.c bounded readiness probe

Outcome
-------
* Five retained-path anchors conservatively bound 1,914 stock bytes: dmAdvActConfig, dmAdvStartDirected, dmAdvStopDirected, dmAdvConnected, and dmAdvConnectFailed.
* With completed prior tranches removed, dm_adv_leg.c ranks second among remaining public Packetcraft modules by anchored bytes, behind dm_conn.c.
* Exact source/dependency identity is Packetcraft r20.05c commit 3656312d..., tree 0a76c7dd..., blob d2da987b.... The source blob is unchanged across r20.05 through r20.05c; this probe uses the exact r20.05c header tree.
* AmbiqSuite 2.5.1 has identical implementation bytes after the license header, providing independent corroboration.
* The source inventories 18 functions. Only the five current anchors receive stock comparison spans; the remainder are explicitly unbounded here.
* Os and O1 compile with stock-oriented trace/assert and legacy advertising configuration. Twenty external providers are enumerated; isolated closure links resolve all with zero undefined symbols.
* Stock retains IAR-style source-path/line instrumentation. No broad matrix or normalized comparison was run.

Packaging
---------
Contains identities, hashes, ledgers, timings, and independently authored shims only. Excludes firmware, upstream source, decompilation, objects, ELFs, and caches. Stock range ends are exclusive.
