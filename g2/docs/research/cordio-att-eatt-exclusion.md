# Cordio enhanced ATT core exclusion audit

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The optional `att_eatt.c` translation unit is not linked into stock G2. All
26 Packetcraft r20.05c definitions are source-only/dead-stripped for this
product. No stock interval is assigned to them.

This is a positive initializer and dependency-closure result. `EattInit` must
register PSM `0x0027` with L2CAP CoC and then write three `attCb` fields:
`eattHandler` at `+0x4C`, `eattDmCback` at `+0x50`, and
`eattL2cDataReq` at `+0x54`. The whole authenticated image has exactly five
literal cells for `attCb=0x200610AC`; all five belong to already-closed ATT,
ATTC, and ATTS objects. None performs these writes.

The separately audited `l2c_coc.c` source inventory has zero linked
definitions. Consequently `L2cCocRegister`, enhanced connect/reconfigure,
and CoC data delivery cannot root `EattInit`, channel establishment, channel
reconfiguration, or any callback path. In the official source tree the three
public channel APIs have no C consumer outside this TU; the channel-count leaf
is referenced only internally. The image also contains no `att_eatt.c`,
`EattEstablishChannels`, `EattReconfigureChannels`, or
`eattReqNextChannels` marker.

The 26-function inventory covers the connection/channel accessors, backoff and
channel state machine, five L2CAP event handlers, DM and WSF callbacks, public
establish/count/reconfigure APIs, data transmit path, and `EattInit`. Exact
source-span hashes are pinned in
`packetcraft-cordio-att-eatt-function-map.tsv`.

## Optional source lineage

Packetcraft r20.05 through r20.05c provides the compatible Apache-2.0 source:

```text
blob    330d9efe93ef9c994dc996b54efcd3c3d6a2b135
bytes   26,769
sha256  16cee15a33f157fc560a8983c057fd5e5186f686ee0d1a8424b0a364d36861d1
```

The later official AmbiqSuite R4.4.1 import is not byte-identical: it adds an
`AM_BLE_EATT` guard around automatic channel establishment because that
product moves the action to the L2CAP callback. Its blob is
`a00610aceb87cc04538b921b9277ee28f908743d`, SHA-256
`f0ba94715e834d7d7761091c495e24104a43aca6dbdd63775716d56d9a215e67`.
No stock body survives to choose between those optional implementations.

Public source routes:

- [Packetcraft r20.05c `att_eatt.c`](https://github.com/packetcraft-inc/cordio/blob/3656312d6b73e2a2c1c8b33ee0385bc199dd97e6/ble-host/sources/stack/att/att_eatt.c)
- [Official later AmbiqSuite R4.4.1 import](https://github.com/AmbiqAI/neuralSPOT/blob/4264b9309e03064ffad13a0468d5d0c1110c5288/extern/AmbiqSuite/R4.4.1/third_party/cordio/ble-host/sources/stack/att/att_eatt.c)

## Reproduction

```sh
python3 tools/analyze_g2_cordio_att_eatt.py --json
python3 -m unittest tests.test_analyze_g2_cordio_att_eatt
```

Production ownership and source replacement remain zero.
