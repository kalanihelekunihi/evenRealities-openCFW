# Cordio SMP Secure Connections utility recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The complete stock `smp_sc_main.c` object is `[0x0056CDC0,0x0056D8C4)`,
2,820 bytes, SHA-256
`dfc0e2f6db94885e44328a855dcba1ee1fa1ca0fddca8aa1191f6820ddda2315`.
Eighteen linked functions contribute 2,626 bytes; three bounded data gaps
contribute 194 bytes. Four of the 22 public definitions are dead-stripped:
`SmpScFree`, `smpGetPeerPublicKey`, `smpSetPeerPublicKey`, and
`SmpScSetOobCfg`. There are 111 direct calls into exact entries, no registered
function pointer, and no real strict-interior stored pointer.

The retained path is `0x006DE8B4`, referenced by literal cell `0x0056D838`.
The apparent event/state helpers at `0x00537F24` and `0x00538114` are the
initiator/responder diagnostic consumers in `smpi_sc_sm.c` and
`smpr_sc_sm.c`, not the start of this translation unit. Their complete
ownership is closed separately in the
[SC state-machine audit](cordio-smp-sc-state-machines-source-recovery.md).
The actual common event and state helpers are `0x0056D31E` and `0x0056D454`.
The next function at `0x0056D8C4` is `WStrReverseCpy` and is excluded.

## Source and release result

The selected Apache-2.0 source is Packetcraft r20.05c blob
`00515542371b1403f2716a02676064bf4aac2dcb`, 22,613 bytes, SHA-256
`cc2e97537c11f7eb0df9b713100ad0165c34e1e39d6c5b6846d9772f14b01c33`.
The same blob is present from r20.05 through r20.05c. Packetcraft r19.02 and
AmbiqSuite 2.x use blob `abf41289efdc01eb3ef79631dc06b85e1efe0ed1`,
22,523 bytes, SHA-256
`f76887f827260493ce4d355c4ad4349e4197b45add5188c0970763b527000256`.

All definitions except `smpEventStr` are source-identical between r19 and r20.
r20 adds `SMP_MSG_INT_CLEANUP`; the stock switch contains that event as value
`0x1F`. This independently selects the r20 source family rather than merely
inheriting a neighboring ABI classification.

## Recovered behavior and ABI

`SmpScInit` binds three 28-byte `SMP_ScCcb` records to the three 76-byte SMP
connection records, installs the initiator/responder pairing hooks, and sets
LE Secure Connections support. Scratch allocation lazily supplies 96-, 64-,
32-, 64-, and 32-byte buffers and frees the same five slots. The CMAC/F4
helpers route allocation or cryptographic failure into the SMP cancel state
machine.

The four send helpers construct public-key, DH-key-check, random, and confirm
PDUs after marking the connection busy and starting the response timer.
Repeated-attempt handling increments the per-connection counter, informs the
SMP database, and selects cancel versus maximum-attempt events from the active
configuration. The diagnostic byte-array formatter and r20 event table remain
linked because the product trace configuration uses them.

Two unaligned four-byte windows (`0x00643377` and `0x0064A903`) happen to
decode to strict-interior values. Both overlap unrelated instructions/data and
are not aligned pointers; the analyzer pins them explicitly so they cannot be
mistaken for ingress.

```sh
python3 tools/analyze_g2_cordio_smp_sc_main.py --json
```

Production ownership remains zero. The authenticated stock object is still
cut forward; source recreation and compiler/linker equivalence remain future
promotion gates.
