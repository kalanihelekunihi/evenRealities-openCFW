# Cordio DM slave-security source recovery

Status date: 2026-08-23
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The complete stock `dm_sec_slave.c` unit occupies
`[0x0052BACC,0x0052BB64)`: all three public APIs contribute 148 code bytes
and a four-byte `dmCb` literal completes the 152-byte physical object,
SHA-256
`5156521de0630c8921394b506f309e416ed9c7a4d9adb6b0d7b0293943a52722`.
Six direct calls, zero stored entry pointers, and zero strict-interior pointers
close ingress. No source function is dead-stripped.

The three definition bodies are invariant between Packetcraft r19,
AmbiqSuite 2.x, Packetcraft r20.05, and Ambiq R4. Stock nevertheless selects
the r20/R4 configuration independently: `DmSecLtkRsp` writes internal event
`0x29`, the component-5 value under the three-bit message-ID ABI. The older
shift-four ABI would write `0x51`.

The selected public Apache-2.0 source is Packetcraft r20.05c blob
`bb8dd0d6fcf2eb0861f9f4b308498ee3b1a89c49`, 4,064 bytes, SHA-256
`7bbf923ff434d8ae73fad83b566c5359178079e046c99e9bb9909806f7bceb81`.
Official AmbiqSuite R4.4.1 as later imported by AmbiqAI/neuralSPOT is
byte-identical corroboration, not a historical producing-commit claim.

`DmSecPairRsp` allocates an eight-byte SMP message, masks both key-distribution
fields to three bits, and sends event 2. `DmSecSlaveReq` allocates six bytes
and sends security-request event 5. `DmSecLtkRsp` allocates 22 bytes, records
key presence and security level, conditionally copies the 16-byte LTK, and
sends event `0x29` to `dmCb.handlerId`. The six callers are bounded product
bodies but remain address-named because no retained source name is defensible.

The repository preserves
`research/readiness/dm-sec-slave/`, 5,325 bytes,
SHA-256
`5670c572f62859237ead6fe895bf7a2a6876da99a5e508ffff1a9767fb529b7c`.
Its fourteen inner hashes cover all three source functions, sixteen build
inputs, five provider seams, and two live Os/O1 zero-unresolved links. It
excludes firmware, licensed source/header bytes, objects, ELFs, disassembly,
maps, and caches.

```sh
python3 tools/analyze_g2_cordio_dm_sec_slave.py --json
python3 tools/verify_research_corpus.py --json
```

Production now routes all three functions through
`components/apollo_main/core_overlay/cordio_dm_sec_roles.c`. Three guarded
full-span redirects replace 148 stock code bytes with 160 compiled Thumb bytes
and four alignment bytes. Host tests cover key-distribution masking, allocation
failure, security-request formatting, present/absent LTK behavior, key copying,
handler routing, and untouched ABI padding. The analyzer authenticates the
stock closure, exact source identity, seven relocations, leaf outputs, and
redirects. No hardware was accessed or flashed; slave-role pairing timing,
controller message ownership, disconnect races, and peer interoperability are
blocked by unavailable authorized G2/EM9305 physical evidence.
