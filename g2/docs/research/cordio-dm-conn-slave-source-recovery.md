# Cordio DM slave connection source recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

Five of six `dm_conn_slave.c` functions survive in the stock image. Their
206 code bytes and six-byte tail form the complete 212-byte object at
`[0x0056E4F8,0x0056E5CC)`, SHA-256
`69b64b7e5f7a5a2e6cb6666a88a25d06373a5c1f778086526836307bd7858f45`.
Five direct calls, two registered action pointers, and zero strict-interior
pointers close ingress. `DmConnAccept` is source-only/dead-stripped.

The selected Apache-2.0 source is Packetcraft r20.05c blob
`9422ae8e45e12c3ea26aa6dbdc5730ed40e74cdd`, 6,492 bytes, SHA-256
`4fc01fd9a83d370f3899d75c0bda7ce7473067cde17efe41b5e6b87b4c15847e`.
The exact two-entry action table at `[0x0078D42C,0x0078D434)` points to
`dmConnUpdActUpdateSlave` and `dmConnUpdActL2cUpdateCnf`. The retained L2CAP
completion wrapper emits event `0x73` and calls `dmConnUpdExecute`, proving
r20/R4's component-14 update architecture. The r19/AmbiqSuite 2.x source
instead uses unified connection-state actions and `dmConnSmExecute`.

The update action chooses the controller procedure when both peers support
it, otherwise starts one L2CAP update or reports command-disallowed when one
is already pending. The confirmation action clears that pending flag and
reports failures. The two public L2CAP bridges forward an update confirmation
to the update state machine or emit `DM_L2C_CMD_REJ_IND` to the application.

An exhaustive unaligned scan finds one apparent interior value at odd address
`0x00643397`; it is a four-byte window in unrelated packed data, not an
aligned pointer. The analyzer pins that false positive explicitly. No body,
call, or stored-pointer candidate remains for `DmConnAccept`, and the only
stock call to `dmConnOpenAccept` belongs to the separately closed master API.

```sh
python3 tools/analyze_g2_cordio_dm_conn_slave.py --json
```

Compiler readiness is deferred with the neighboring connection units because
the local ARM cross-toolchain is unavailable. Production ownership remains
zero; all 212 bytes are still cut from stock. The next target should follow
the now-authenticated L2CAP caller bodies into `l2c_slave.c` or close the
extended connection role modules if their action tables provide tighter
bounds.
