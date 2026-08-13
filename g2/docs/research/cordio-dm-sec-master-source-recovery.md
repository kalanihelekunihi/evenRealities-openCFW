# Cordio DM master-security source recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

All three `dm_sec_master.c` APIs survive in `[0x0055BBC4,0x0055BC5C)`:
144 code bytes plus an eight-byte literal pool form a 152-byte object,
SHA-256 `9e57f961ad2655c12eda32bb6d2fbb6c5a7e34b2588e3d399fb2ec77299bc43b`.
Four direct callers, zero stored pointers, and zero strict-interior ingress
close the unit; no source API is dead-stripped.

The bodies are invariant across r19 through r20/R4, but stock
`DmSecEncryptReq` writes event `0x28`, selecting the r20/R4 three-bit message
ABI over r19's `0x50`. The selected Apache-2.0 source is Packetcraft r20.05c
blob `a941ac7e6d4199d76e5cae0e157efcf8d16dfb64`, 4,026 bytes, SHA-256
`4a17020e0f7076e81ea4878f3423569ecdfb7deaf6b7d8fcd753cd04926c9ffe`;
official Ambiq R4.4.1 is byte-identical later corroboration.

`DmSmpEncryptReq` resolves the CCB, records temporary security state, and
starts encryption with `calc128Zeros = 0x007856B0`. `DmSecPairReq` formats
the eight-byte pair request, and `DmSecEncryptReq` sends a 32-byte internal
request through `dmCb = 0x20073B78`. This independently corrects the shared
DM-security labels: `dmSecCb = 0x20074114`, while `0x007856B0` is the 16-byte
zero block.

The verified readiness archive is
`research/readiness/dm-sec-master/`, 5,720 bytes,
SHA-256 `3bf1dc1ac4e70b03f3d5543d34fa075810ef837d21f5c631823b1b96e6f50839`.
Its fifteen inner hashes cover three functions, eighteen build inputs, eight
provider seams, and two live Os/O1 zero-unresolved links; licensed source and
build products are excluded.

```sh
python3 tools/analyze_g2_cordio_dm_sec_master.py --json
python3 tools/verify_research_corpus.py --json
```

Production replacement remains zero. The next evidence-led target is
`dm_conn_master.c`.
