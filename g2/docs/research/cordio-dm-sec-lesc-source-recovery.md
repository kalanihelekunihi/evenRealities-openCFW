# Cordio DM LE Secure Connections source recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The stock `dm_sec_lesc.c` unit is bounded at
`[0x00534894,0x0053498C)`: seven linked functions contribute 222 code bytes
and a 26-byte tail brings the physical object to 248 bytes, SHA-256
`de5c29697f858f7bb0d0b83cacb0722df7d4410e96af85b456044eedfea45eae`.
Ten direct calls, one stored module-entry pointer, and zero strict-interior
pointers close ingress. Four APIs are dead-stripped: `DmSecKeypressReq`,
`DmSecSetOob`, `DmSecCalcOobReq`, and `DmSecSetDebugEccKey`. The standard
debug-key constants are absent from the image.

Packetcraft r19/AmbiqSuite 2.x and Packetcraft r20/Ambiq R4 have identical
function bodies; only license formatting changes. Stock is assigned to the
r20/R4 configuration through the surrounding shift-three ABI and the handler's
exact internal events `0x40/0x41`, not through a false body-version claim.
The selected public Apache-2.0 source is Packetcraft r20.05c blob
`a8790951d69484687728d74669888931a9aa2971`, 11,436 bytes, SHA-256
`a8bd51525ec11fa7f5ea8c2aee5c76ed8885aa191cb76fcfcb54ddf72e886e8d`.

`dmSecLescFcnIf [0x0078A8A4,0x0078A8B0)` retains default reset/HCI handlers
and `dmSecLescMsgHandler`, SHA-256
`ed14ab53083e48de966c42b4f3ca570a421921b41e002c61dec9ddcab49e85d7`.
`DmSecLescInit` installs it at component ID 8. The 96-byte ECC key occupies
`[0x200726D0,0x20072730)`; `dmSecOobRand` is a pointer at `0x200744F8`.
The message handler forwards ECC completion and reconstructs OOB confirmation
events, while the public leaves generate, set, return, compare, and format ECC
state.

The repository preserves
`research/readiness/dm-sec-lesc/`, 6,363 bytes,
SHA-256
`241239ad18461de2d012a3855d80853f0ea19e2d75dd7858faecc322920b8351`.
Its fifteen inner hashes cover all 11 source functions, 26 build inputs, 18
provider seams, and two live Os/O1 zero-unresolved links. It excludes firmware,
licensed source/header bytes, objects, ELFs, disassembly, and caches.

```sh
python3 tools/analyze_g2_cordio_dm_sec_lesc.py --json
python3 tools/verify_research_corpus.py --json
```

The next defensible bounded target is component-9 `dm_phy.c`.
