# Cordio DM legacy-master connection source recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The complete stock `dm_conn_master_leg.c` object is bounded at
`[0x00536A28,0x00536AC8)`: three linked functions contribute 136 code bytes
and a 24-byte literal pool completes the 160-byte span, SHA-256
`b68a143267080514feaba249003d8cfd14b41a1c7714ceda7d274ce1cf4ccc30`.
Two direct calls, one registered entry pointer, and zero strict-interior
pointers close ingress. No source function is dead-stripped.

The selected Apache-2.0 source is Packetcraft r20.05c blob
`bdf160b21e58d3e2c34901b1829d81d4890d2b56`, 3,405 bytes, SHA-256
`a0ad6fdc783da5e96979b622ab05ecb2a46dc05b6a7eb2ede2740fc50a3fa656`.
The stock architecture exactly matches the r20 delta: the legacy main action
table shrinks from four entries to `{open,cancel}`, while `DmConnMasterInit`
installs both that table and the new two-entry update table under
`WsfTaskLock`. The r19/AmbiqSuite 2.x file instead uses one unlocked
four-entry table and is excluded.

`dmConnOpen` selects the 1M scan PHY index, submits the legacy HCI create
connection command from `dmConnCb`/`dmCb`, and notifies the optional device
privacy component that initiation started. `dmConnSmActOpen` unpacks the open
message and calls it. `DmConnMasterInit` stores the main table at
`dmConnActSet[1]` and the update table at `dmConnUpdActSet[1]`. The main-table
entry at `0x0078D424` is the sole stored pointer into this object.

```sh
python3 tools/analyze_g2_cordio_dm_conn_master_leg.py --json
```

Compiler readiness is deliberately deferred: the local environment has no
`arm-none-eabi` toolchain, while the source/binary/table proof is independent
and complete. Production still cuts these 160 bytes forward. The adjacent
legacy-slave and extended-master modules are the next action-table-driven
candidates.
