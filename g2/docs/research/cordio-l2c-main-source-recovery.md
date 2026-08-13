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

Production ownership remains zero, and compiler reproduction is deferred while
reverse engineering remains the priority.
