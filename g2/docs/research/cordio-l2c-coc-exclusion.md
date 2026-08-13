# Cordio L2CAP CoC exclusion audit

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The optional `l2c_coc.c` translation unit is not linked into the stock G2
image. All 67 Packetcraft r20.05c definitions are source-only/dead-stripped
for this product configuration. No stock function address or byte span is
assigned to them.

This is a positive initialization-contract result. A linked `L2cCocInit` must
replace the signaling, CoC-control, and arbitrary-CID callbacks in `l2cCb` at
`0x200737D8`, then call `DmConnRegister(DM_CLIENT_ID_L2C, ...)`. The complete
image contains exactly three literals for `l2cCb`, owned by the already-closed
core, slave, and master initializers at `0x00530B90`, `0x00536FA0`, and
`0x0053722C`. It also contains exactly three calls to `DmConnRegister`, at
`0x004B5140`, `0x004B7ED2`, and `0x00537CF2`; none is an L2CAP CoC initializer.

The image additionally contains no `l2c_coc.c`, `l2cCoc`, `L2cCoc`,
`l2cRegCbAlloc`, or `l2cChanCbAlloc` marker. The default callbacks installed by
`L2cInit` therefore remain in place, safely rejecting unregistered dynamic
channel traffic.

## Optional source oracle

The compatible Apache-2.0 optional source is Packetcraft r20.05c:

```text
commit  3656312d6b73e2a2c1c8b33ee0385bc199dd97e6
blob    f78873f1435e1f4298c9e22b5114b7061f0d1e9c
bytes   91,003
sha256  d6d41daaccc204cc9b4da200d9baf0f5004dfc7ef57690c47fb2526d7722ffb6
```

Packetcraft r19.02/AmbiqSuite 2.x uses the smaller blob
`316c1292fb77c999147f3426a0188a8c7be5dad2` (57,998 bytes, SHA-256
`f4f341db33c294fa3a480fae6a2055f46f46c9337a4323dd0047225f1864bcd6`).
r20 adds enhanced-credit-based connection/reconfiguration support and expands
the control blocks substantially. No stock body survives to discriminate
these versions; r20 is selected only as the compatible optional source beside
the independently proven r20/R4 L2CAP and DM architecture.

The complete 67-definition inventory and source-span hashes are pinned in the
two `packetcraft-cordio-l2c-coc-*` manifests. Reproduce the exclusion proof:

```sh
python3 tools/analyze_g2_cordio_l2c_coc.py --json
```

Production ownership and source replacement remain zero. Compiler readiness is
deferred because the optional subsystem is absent and reverse engineering is
the current priority.
