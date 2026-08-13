# Cordio `smp_sc_act.c` source recovery

## Result

The stock interval `[0x005E267C,0x005E3118)` is the complete shared Cordio
Secure Connections action unit `ble-host/sources/stack/smp/smp_sc_act.c`.
Twenty definitions survive as 2,662 code bytes, followed by a 54-byte owned
tail. `SmpScEnableZeroDhKey` is the only absent definition: it is guarded by
`SMP_DHKEY_QUAL_INCLUDED`, whose file-local default is `FALSE`, so this is a
configuration exclusion rather than unexplained linker removal.

The best exact later oracle is the official AmbiqSuite R4.4.1 import at
`4264b9309e03064ffad13a0468d5d0c1110c5288`: Apache-2.0 Git blob
`65d79f72b9e7536e554bb183c56f14bccc00b5af`, 33,145 bytes, SHA-256
`6e77a1429fe3bee3c0638c39d3784cfe7a9a789f3cf55be4b3e48a10ef360e34`.
That later import is a reconstruction oracle, not a claim about the historical
commit used to produce G2.

This unit exposes a useful hybrid-history detail. Packetcraft r20.05 through
r20.05c removed an `smpScProcPairing` branch that forces `justWorks=FALSE`
when either peer reports `SMP_IO_NO_IN_NO_OUT`. Stock retains the branch at
`0x005E2938..0x005E294E`, exactly like Packetcraft r19/AmbiqSuite 2.x and the
later R4.4.1 import. The surrounding linked stack nevertheless uses the
r20 three-bit SMP/DM message ABI and r20 action-table topology. The accurate
classification is therefore an R4-style vendor hybrid, not a whole-file
Packetcraft-r20 identity. All other definitions are invariant between the
selected sources.

## Boundary, constants, and ingress

The 2,716-byte physical unit hashes to
`241c1ba219999a6194f12f6a338ac39e80d1e1e3dd4535adadd64c4b48b7cd43`;
the concatenated bodies hash to
`cee95996181d0a9836a45338891e214d755c23cdd0d6263372d73c498d0ffbd6`.
The tail `[0x005E30E2,0x005E3118)` hashes to
`4f3f441888b40377d33f10e898c18f0a4714116b06dd5dc389b4527ae9f03867`.
It contains the F5 text length `0x54`, local labels `MAC` and `LTK`, and
literals for `smpCb=0x20070AEC`, `pSmpCfg=0x200004B8`, the F4/JWNC/DH-key
trace labels, the 16-byte F5 salt at `0x007890D0`, and the `btle` F5 key at
`0x0078F3FC`. The next closed unit begins at `0x005E3118`.

The common SMP interface stores `smpScProcPairing` and `smpScAuthReq` at
`0x0056D824` and `0x0056D828`. The initiator and responder Secure Connections
action tables add 24 pointer cells, for 26 exact stored entry pointers across
15 unique roots. Nineteen direct calls reach exact entries, ten within this
unit and nine from the two role-action units. No accepted stored or branched
address reaches a strict body interior.

Two packed-data byte windows happen to decode to the even value `0x005E2F00`
and therefore lack the Thumb bit. Two other raw BL-like candidates begin on
the second halfword of valid 32-bit arithmetic instructions. The analyzer
pins all four false candidates explicitly so a future image change cannot be
mistaken for stable ingress.

## Behavior and ABI

The shared actions select the association model; concatenate initiator and
responder addresses; request authentication; clean up or cancel pairing; and
perform the common F4, G2, F5, F6, passkey, numeric-comparison, and shared-DH
key calculations. `smpScProcPairing` selects OOB, passkey, numeric comparison,
or Just Works from both pairing requests, rejects unavailable Secure
Connections, allocates SC scratch buffers, copies the active ECC key, and
enforces authentication and minimum-key-length policy. Stock's retained
no-input/no-output branch preserves the R4/r19 behavior of setting the MITM
result even for that Just Works case.

The common F5 path derives `T`, then `MacKey`, then the LTK from the shared
secret, nonces, addresses, the `btle` key ID, and length 256. F6 derives the
initiator and responder DH-key checks from the negotiated IO capabilities and
address concatenations. The 20 body hashes lock 112 decoded outbound BL sites.

## Reproducibility

`tools/analyze_g2_cordio_smp_sc_act.py` pins the official image and manifests,
all linked bodies, the complete physical unit and tail, the historical pairing
branch, all 19 direct entry calls, all 26 stored entry pointers, 112 outbound
calls, and every false interior-looking candidate. Source and stock hashes are
in `tools/manifests/packetcraft-cordio-smp-sc-act-function-map.tsv`; provenance
is in `packetcraft-cordio-smp-sc-act-provenance.tsv`.

This raises identified provenance only. No stock byte is replaced and no
source-owned production byte is added.
