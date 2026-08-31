# Cordio DM legacy-slave connection source recovery

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The complete stock `dm_conn_slave_leg.c` object is bounded at
`[0x00536AC8,0x00536B40)`: five linked functions contribute 104 code bytes
and a 16-byte literal pool completes the 120-byte span, SHA-256
`4a261efbbef393ad9bb9c28d0ad1060ef7c5342cdd2cff83e38e469f6bc2a109`.
One direct call, four registered entry pointers, and zero strict-interior
pointers close ingress. No source function is dead-stripped.

The selected Apache-2.0 source is Packetcraft r20.05c blob
`d714da9f52fc08aa963a280dcdaafda1eff2eb39`, 4,043 bytes, SHA-256
`3bfa84746595aee9bd692db41a0df930b2ec1a4c59adbff4c62cc82b0804eef7`.
The stock architecture exactly matches the r20 delta: the legacy slave main
action table has four entries, while `DmConnSlaveInit` installs it and the
new two-entry update table under `WsfTaskLock`. The r19/AmbiqSuite 2.x file
instead uses one unlocked six-entry table and is excluded.

The four actions start directed advertising, stop it and report failure,
report an accepted connection, or report an advertising failure. Their
table is `[0x00785BE0,0x00785BF0)`; the separate slave update table is
`[0x0078D42C,0x0078D434)`. `DmConnSlaveInit` stores the two tables at the
slave slots of `dmConnActSet` and `dmConnUpdActSet` respectively. The action
table provides the only stored pointers into this object.

```sh
python3 tools/analyze_g2_cordio_dm_conn_slave_leg.py --json
```

All five definitions now have maintained, host-tested C. Six Cortex-M55
profiles (the complete unit plus five isolated selectors) compile cleanly.
Five guarded redirects replace all 104 bounded stock body bytes with 156
compiled bytes plus eight alignment bytes under nine strict relocations. The
14 manifest regions, component, deterministic package, and flash plan are
fail-closed and pinned by `make cordio-dm-conn-slave-leg-closure`.

Live directed-advertising, accepted/failed connection callbacks, retained
table installation, BLE peer/controller timing, RF behavior, and paired-temple
interoperation qualification is blocked by unavailable physical evidence. The earlier
nonresponsive-fault inference is superseded: the charging case was
accidentally bumped during lunch and caused that test disconnect, not a device
or flashing fault. Future acceptance still requires authorized peer,
controller-timing, RF, and paired-temple evidence. No hardware-dependent
functional-completeness claim is made. The adjacent `dm_conn_slave.c`
update/API unit is the next bounded software closure candidate.
