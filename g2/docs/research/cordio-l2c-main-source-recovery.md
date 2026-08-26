# Cordio L2CAP core source recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

All 11 `l2c_main.c` definitions survive in the complete 1,736-byte object
`[0x00530538,0x00530C00)`, SHA-256
`561273571edcc15932fba3b4f5b4f5c3fc766a8a60ae933885a7173d02f8ccd9`.
The functions contribute 1,636 code bytes; diagnostic data, literals, callback
cells, and alignment account for the remaining 100 bytes. Sixteen direct calls,
six intentional stored Thumb entries, and zero strict-interior pointers close
ingress. The eight-byte wrapper at `0x00530C00` belongs to the following unit
and is deliberately excluded.

The selected Apache-2.0 source is Packetcraft r20.05c blob
`988b73a635704e49059871a2e2e59a59166b29c4`, 11,008 bytes, SHA-256
`b76edc13a463028e60c6b148d90c47bc9dbb8f2a8783ac8efc1f765fc722d951`.
Its implementation bodies are identical to Packetcraft r19/AmbiqSuite 2.x;
this translation unit therefore does not independently discriminate releases.
The r20 selection is qualified by the neighboring L2CAP/DM objects that do
contain r20-only connection-update behavior.

## Recovered integration

The retained source path is at `0x006DD4D4`, referenced by literal cell
`0x00530B80`. `l2cCb` is at `0x200737D8`. `L2cInit` installs the default ATT
and SMP data callbacks at offsets `+0x00/+0x04`, signaling receive at `+0x08`,
the three default control callbacks at `+0x0C/+0x10/+0x14`, the default
CID callback at `+0x20`, and identifier value one at `+0x24`. It then registers
the ACL and flow callbacks with HCI.

The six stored Thumb entries are confined to the initializer pool:

- `0x00530BA4 -> l2cDefaultDataCback`
- `0x00530BA8 -> l2cRxSignalingPkt`
- `0x00530BAC -> l2cDefaultCtrlCback`
- `0x00530BB0 -> l2cDefaultDataCidCback`
- `0x00530BB4 -> l2cHciFlowCback`
- `0x00530BB8 -> l2cHciAclCback`

The ACL callback validates HCI/L2CAP lengths and dispatches signaling, ATT,
SMP, or arbitrary-CID payloads. The signaling callback validates the connection
handle and routes by master/slave role. Flow events fan out to ATT, SMP, and
connection-oriented-channel control callbacks. `l2cSendCmdReject` and
`L2cDataReq` construct the standard signaling and ACL/L2CAP headers; all
source definitions are accounted for and none is dead-stripped.

```sh
python3 tools/analyze_g2_cordio_l2c_main.py --json
```

## Production admission

`runtime_cordio_l2c_main.c` now owns all eleven definitions. Ten guarded
redirects plus one exact two-byte in-place copy replace all 1,636 bounded stock
body bytes with 552 compiled Cortex-M55 bytes plus 12 alignment bytes under 11
strict relocations. The implementation rejects malformed ACL/L2CAP/signaling
lengths, invalid connection IDs and roles, unregistered arbitrary CIDs, and
allocation-size overflow before dispatch or transmit.

The canonical overlay is 354,692 bytes, SHA-256
`a679ebaf7c8ad06233ca8f4cc2750f46b256bd4d809420bc1369e87ca2921ee9`;
the Apollo component is 3,878,088 bytes, SHA-256
`bdff58228eeea5586a7c901caa713fb824587e491bccda35ae8d6dcf16ffcf85`;
and the deterministic package is 4,656,582 bytes, SHA-256
`41b32b257fb4a97b21e6b8db77009e3ce626a1432388c8c43ac57b215e8d3fe5`.
`make cordio-l2c-runtime-closure` is green. Live ATT/SMP/signaling,
peer/controller flow-control, timing, and buffer-lifetime validation is blocked
by unavailable authorized responsive G2/EM9305 physical evidence.
