# Cordio `smpr_act.c` source recovery

## Result

The stock G2 interval `[0x005E38C8,0x005E3D7C)` is the complete Cordio
`ble-host/sources/stack/smp/smpr_act.c` translation unit. All ten source
definitions survive: 1,160 code bytes plus 44 bytes of trace categories,
literal data, and alignment. No source definition is dead-stripped.

The selected Apache-2.0 oracle is Packetcraft r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`, Git blob
`086a013a445e9222a367fb3eb5383beead662af2`, 12,676 bytes, SHA-256
`9dde00f83bdadb7445935522fad83a86a48b75be220f877ab94a9a483736ba05`.
The same blob appears in r20.05, r20.05a, r20.05b, and the official later
AmbiqSuite R4.4.1 import. That later import is exact corroboration, not the
resolved historical G2 generating commit.

Packetcraft r19.02 and AmbiqSuite 2.4.2/2.5.1 instead use blob
`54c5dbec582ea011a798f5b083f0a123afbffe21`, SHA-256
`da8f66711e27e5aa6b7438467ff8d368101429ffb2577eb3191bc37dcde0511a`.
Their only implementation delta is material: after saving and zero-padding
the responder STK, r20 sets `pCcb->keyReady = TRUE`. Stock performs the exact
byte write at `0x005E3C18`, storing one at `smpCcb_t+0x44`, before starting
the response timer. This independently selects the r20/R4 source family.

## Physical boundary and ownership

The 1,204-byte physical object hashes to
`4bf1a9f59712e18f019e3bfb7a6345b05a5def9124d334765ba8961b36c08355`.
Its ten concatenated bodies hash to
`61d343559a58cb00766599071ad054ab33df207b999e43be5d4830c8cc9e6663`.
Owned non-code ranges are:

- `[0x005E3BC6,0x005E3BD0)`: alignment and `ERR`/`SMP` trace categories;
- `[0x005E3D2C,0x005E3D4C)`: `HCI`, diagnostic, retained-path,
  `pSmpCfg`, and `smpCb` literals;
- `[0x005E3D7A,0x005E3D7C)`: final two-byte alignment.

The retained NUL-terminated IAR path occupies
`[0x006DE914,0x006DE971)` and has one pointer cell at `0x005E3D38`. The
literal pool also fixes `pSmpCfg=0x200004B8` and `smpCb=0x20070AEC`. The
next unrelated translation unit begins at `0x005E3D7C`.

## Ingress and action tables

All ten functions are rooted in both responder action families:

- the Secure Connections table `[0x006D0B64,0x006D0C40)` contains ten
  pointers into this TU;
- the legacy table `[0x006D7E7C,0x006D7EE8)` contains the other ten.

The only direct entry calls are internal: `smprActProcPairCnfCalc1` calls
`smprActProcPairCnf` at `0x005E3B42`, and `smprActSetupKeyDist` calls
`smprActSendKey` at `0x005E3C9C`. A whole-image bytewise scan therefore closes
20 stored exact-entry pointers and two direct calls. It finds no stored
strict-interior address.

The Secure Connections table orders the final receive/send actions according
to its state-machine numbering, while the legacy table preserves the source
order. This is expected table ownership, not conflicting function identity.

## Behavior and ABI

The stock bodies implement the complete responder legacy path:

- send the security request and start the response timer;
- allocate the 64-byte scratch record and forward the parsed pairing request
  through `DmSmpCbackExec`;
- build the pairing response, choose legacy-confirm or public-key input, and
  invoke the registered authentication callback;
- save and calculate confirm values, enforce repeated-attempt tracking through
  `SmpDbPairingFailed`, and derive the STK;
- set `keyReady`, send the responder random value, and distribute or receive
  encryption, identity, and signing keys;
- synthesize pairing-complete events when no more keys remain.

Relevant `smpCcb_t` offsets are the request/response buffers at `+0x20/+0x27`,
scratch pointer at `+0x30`, connection ID at `+0x3D`, next command at `+0x3F`,
attempt count at `+0x42`, `keyReady` at `+0x44`, and the Secure Connections
record pointer at `+0x48`. Fifty decoded outbound BL sites resolve to the
previously closed common SMP, database, DM, security, buffer, memory, and
diagnostic providers. The exact provider sites remain locked indirectly by
the per-body hashes.

## Reproducibility

`tools/analyze_g2_cordio_smpr_act.py` pins the official image, both manifests,
every body, all owned gaps, both responder tables, the retained path and
globals, the r20 `keyReady` instruction sequence, the complete direct-call and
stored-pointer ingress, and the absence of an interior pointer. The source and
stock body ledger is
`tools/manifests/packetcraft-cordio-smpr-act-function-map.tsv`; release
identity is in `packetcraft-cordio-smpr-act-provenance.tsv`.

This work changes identified provenance only: zero stock bytes are replaced
and zero source-owned production bytes are added.
