# Cordio `smpi_sc_act.c` source recovery

## Result

All 16 linked initiator actions are now implemented in production C at
`components/apollo_main/core_overlay/cordio_smpi_sc_act.c`, compiled as
independent Thumb leaves, and routed over their complete stock bodies.  The
reviewed Apple Clang build contributes 942 compiled bytes plus 14 alignment
bytes (956 source-owned bytes total) and replaces 1,070 stock code bytes.
Host tests execute authentication/public-key setup, JWNC, passkey, OOB, DH-key
success with LTK truncation and `keyReady`, and retry/max-attempt failure paths.

Physical validation remains explicitly blocked: no authorized G2/EM9305 is
available to demonstrate initiator numeric-comparison, passkey/key-press, OOB,
DH-key/encryption, retry, and peer-interoperability behavior.

The stock interval `[0x005E3474,0x005E38C8)` is the complete Cordio Secure
Connections initiator action unit
`ble-host/sources/stack/smp/smpi_sc_act.c`. All 16 source definitions survive:
1,070 code bytes and a 38-byte owned tail. No source definition is
dead-stripped.

Packetcraft r20.05 through r20.05c and the official later AmbiqSuite R4.4.1
import share Apache-2.0 Git blob
`38ed4197099e84e5dd17dac4a05385e42fe556fb`, 16,295 bytes, SHA-256
`195b7619013e746462ee1cb2cb4db7ccce3f68a1fe7dd15d0d05e1ca2567c952`.
The selected public pin is r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`. The Ambiq import at
`4264b9309e03064ffad13a0468d5d0c1110c5288` is exact later corroboration,
not a claim about G2's historical generating commit.

The r19/AmbiqSuite 2.x blob
`ed53928ee9d86e94ef7985abb2c783aa3ee16069` differs in one implementation
line: it omits `pCcb->keyReady = TRUE` in
`smpiScActDHKeyCheckVerify`. Stock writes one to `smpCcb_t+0x44` at
`0x005E3840`. This independently selects the r20/R4 source family.

## Boundary, table, and ingress

The 1,108-byte physical unit hashes to
`00ae4d04166a1c435a3447b11bff93001fba191080f6468062aab4e3e064aace`.
Its concatenated bodies hash to
`ca0b592a6ba9df5a6ed2065dab1a88ff428d0383c5563f13ab4453d816fcd1ac`.
The tail `[0x005E38A2,0x005E38C8)` contains alignment, the local labels `Cai`
and `Cbi`, calculation-label pointers, `calc128Zeros=0x007856B0`, and
`pSmpCfg=0x200004B8`; it hashes to
`574667b863570d2d3aa362f1834ccfd7203dabcea661586853dc5a1ed0cd60ae`.
The next closed unit begins at `0x005E38C8`.

All 16 entries are rooted once in the initiator Secure Connections action
table `[0x006D1214,0x006D12E0)`. There is no direct call to any TU entry, no
stored body-interior address, and no exterior direct branch into a strict
interior. No `smpi_sc_act.c` path survives, so ownership rests on exact source
order, behavior, table roots, and the two adjacent closed object boundaries.

## Behavior and ABI

The actions cover association-model selection, public-key exchange,
Just-Works/Numeric-Comparison setup, F4/G2 calculations, passkey confirms and
randoms, out-of-band confirmation, shared-secret processing, and DH-key-check
send/verification. Verification success truncates and zero-pads the LTK to the
negotiated key length, marks `keyReady`, and starts encryption. Failure marks
the pairing failed and enters retry or maximum-attempt handling.

The implementation uses the already-closed common Secure Connections helpers,
security RNG, `calc128Zeros`, `DmSmpEncryptReq`, and SMP database failure
tracking. The 16 body hashes lock 56 decoded outbound BL sites.

## Reproducibility

`tools/analyze_g2_cordio_smpi_sc_act.py` pins the official image and manifests,
every body, the physical interval and tail, the complete action table, the
`keyReady` instruction sequence, every stored entry pointer, all direct-entry
and strict-interior branches, and the absence of a body-interior pointer.
Source and stock hashes are in
`tools/manifests/packetcraft-cordio-smpi-sc-act-function-map.tsv`; provenance
is in `packetcraft-cordio-smpi-sc-act-provenance.tsv`.

The analyzer now pins the production source, every compiled leaf and stock
redirect, the r20/R4 `keyReady` behavior, and the unavailable-hardware block.
