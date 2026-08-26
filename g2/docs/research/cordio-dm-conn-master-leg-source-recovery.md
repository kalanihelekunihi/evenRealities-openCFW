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

`runtime_cordio_dm_conn_master_leg.c` now implements and target-compiles all
three definitions. Three guarded redirects replace all 136 linked stock body
bytes with 176 compiled Cortex-M55 bytes plus two alignment bytes under seven
strict relocations. Host tests cover scan/connection parameters, address
mapping, HCI submission, privacy notification, malformed input, action-message
unpacking, and locked installation of both retained action tables. Exact
routing, manifest, component, deterministic package, and flash-plan gates
pass. The canonical overlay/component/package sizes are 358,498 / 3,881,894 /
4,660,388 bytes; the 3,633,825-byte flash plan has 5,226 placed, two
unresolved, five container-only, and six protected regions. No image was
signed, flashed, or installed. Live connection creation, controller/privacy
ordering, peer/RF/timing, and paired-temple validation remain blocked by
unavailable authorized responsive G2/EM9305 physical evidence.
