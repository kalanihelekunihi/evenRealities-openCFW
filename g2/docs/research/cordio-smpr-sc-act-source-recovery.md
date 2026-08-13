# Cordio `smpr_sc_act.c` source recovery

## Result

The stock interval `[0x005E3D7C,0x005E4228)` is the complete Cordio Secure
Connections responder action unit
`ble-host/sources/stack/smp/smpr_sc_act.c`. All 20 source definitions survive:
1,162 code bytes and a 34-byte owned tail. No source definition is
dead-stripped.

Packetcraft r20.05 through r20.05c and the official later AmbiqSuite R4.4.1
import share Apache-2.0 Git blob
`062799ba7c52aff19cb29d07eb0fbfc38ae1d1e4`, 18,585 bytes, SHA-256
`6c98c9eb132b19a6b7870ae35d7e31f0480d2566a83590f09984e205b10567d5`.
The selected public pin is r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`; the exact R4.4.1 import is
later corroboration rather than the unresolved historical generating commit.

The r19/AmbiqSuite 2.x blob
`b8261ddbf130e4f5640e32e46688d0389460d6f7` omits the one implementation
line `pCcb->keyReady = TRUE` in `smprScActDHKeyCheckSend`. Stock writes one to
`smpCcb_t+0x44` at `0x005E41AA`, independently selecting the r20/R4 family.

## Boundary, table, and ingress

The 1,196-byte physical unit hashes to
`a93663591adfe7aeaad3c3fe562766e3cc447b5ebdda406e45160f549a9e6e2f`.
Its concatenated bodies hash to
`812d6e4df932f94837db3f980104e9432251aca1625a2b200f00c49e648ea86a`.
The tail `[0x005E4206,0x005E4228)` contains alignment, local `Cbi`/`Ca`
labels, calculation-label pointers, `calc128Zeros=0x007856B0`, and
`pSmpCfg=0x200004B8`; it hashes to
`55fdc0c2ce5baa59f5fb8b95f6209dc472b53c6543d5928733ac5e11a0c83e44`.
Unrelated code begins at `0x005E4228`.

All 20 entries are rooted once in the responder Secure Connections action
table `[0x006D0B64,0x006D0C40)`. Four direct calls are internal helper edges:
the two combined store-and-calculate wrappers call `smprScActPkStoreCnf`,
`smprScActStoreLescPin`, and `smprScActPkCalcCb`. There is no exterior direct
entry call or branch into a strict interior.

An exhaustive byte-window scan finds five even values that numerically land in
body interiors. They occur in packed non-pointer data and lack the Thumb bit;
the analyzer pins them separately. No stored Thumb body-interior pointer exists.
No `smpr_sc_act.c` path survives.

## Behavior and ABI

The actions store the authenticated LESC PIN, exchange public keys, implement
Just Works/Numeric Comparison and passkey F4/G2 flows, handle OOB confirm and
random values, wait for and calculate the shared secret, and send the responder
DH-key check. Successful DH-key checking truncates the LTK to the negotiated
key length, zero-pads the remainder, marks `keyReady`, and sends the check;
failure enters database-backed retry or maximum-attempt handling.

The implementation uses the already-closed common Secure Connections helpers,
security RNG, `calc128Zeros`, and SMP database failure tracking. The 20 body
hashes lock 59 decoded outbound BL sites.

## Reproducibility

`tools/analyze_g2_cordio_smpr_sc_act.py` pins the official image and manifests,
every body, the physical interval and tail, the complete action table, the
`keyReady` instruction sequence, all internal entry calls, every stored entry
pointer, the five non-pointer even byte windows, and the absence of direct or
stored strict-interior ingress. Source and stock hashes are in
`tools/manifests/packetcraft-cordio-smpr-sc-act-function-map.tsv`; provenance
is in `packetcraft-cordio-smpr-sc-act-provenance.tsv`.

This raises identified provenance only. No stock byte is replaced and no
source-owned production byte is added.
