# Cordio L2CAP slave source recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

Six of seven `l2c_slave.c` functions survive in the complete 1,148-byte stock
object `[0x00536B40,0x00536FBC)`, SHA-256
`30c891402f75994a7da4fb6457a4e4f6738ddb49a85e2eb7896fdf839d089bc1`.
They contribute 1,078 code bytes; the remaining 70 bytes are authenticated
inline trace categories, literals, the retained source-path pointer, and
alignment. Four direct calls, two registered pointers, and zero interior
pointers close ingress. `L2cDmSigReq` is source-only/dead-stripped.

Packetcraft r20.05c blob `e9a1ff23544bd7e987d53ff7fb6fbfa9b70beef3`,
10,519 bytes, SHA-256 `2f350e0fd27cdc205736df065099da356b9fa8be6e2ce4df014435cde53cbf73`,
is the selected Apache-2.0 source. Stock exactly contains the r20 semantic
change: received signaling and outgoing connection-update requests call
`DmConnIdByHandle`, reject unknown handles, and index per-connection state as
`connId-1`. The r19/AmbiqSuite 2.x source indexes directly by HCI handle and
is excluded. The retained path is at `0x006DD594`.

The object includes timeout handling, signaling-response parsing, slave
initialization, fixed connection-update request construction, handler
initialization, and the WSF handler. The generic `L2cDmSigReq` has no body,
caller, or pointer. Production ownership remains zero; all bytes are still
cut from stock while compiler reproduction is intentionally deferred.

```sh
python3 tools/analyze_g2_cordio_l2c_slave.py --json
```

The adjacent `l2c_master.c` begins at `0x00536FBC` and is the next natural
bounded target; its stored receive callback is already visible at
`0x00537228`.
