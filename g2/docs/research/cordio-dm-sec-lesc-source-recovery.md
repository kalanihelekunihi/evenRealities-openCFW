# Cordio DM LE Secure Connections source recovery

Status date: 2026-08-23
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

## Production admission

`components/apollo_main/core_overlay/cordio_dm_sec_lesc.c` now routes every
live entry. Seven guarded full-span redirects replace the 222 authenticated
stock bytes with seven independently compiled Thumb leaves totaling 278 bytes,
plus six alignment bytes. Ten strict relocations bind only to the retained WSF
buffer/message, ECC, SMP, and Calc128 seams plus the already source-owned
memory-copy leaf. The retained three-word function interface still reaches the
handler through the patched stock entry, and component ID 8 is initialized to
that authenticated interface.

Host tests cover both message events, OOB buffer lifetime and copied values,
ECC generation, 96-byte key set/get, allocation failure, valid/invalid numeric
comparison responses, six-digit formatting, and interface registration. The
target gate proves exactly seven global text symbols. The four public functions
not present in G2 remain documented dead-stripped configuration exclusions;
they are not runtime gaps.

Canonical Apple overlay/component/package identities are
`166576/3689972/4468466` bytes with SHA-256
`1f5c6afeb137b90b18d8feb1378047bc38393525eff6926c26bbe33847fd1cff`,
`9ca58f6db1a98b7604aa86b4f29ad827ba4c7770d93ad71441c0b421830e7ff2`, and
`eb2d45acb2419ec4ec92ddfdb7e54838404a626eb150d8ee7547b35b05662985`.
No hardware was accessed or flashed. Live pairing, controller-event timing,
buffer-pool pressure, disconnect races, and peer interoperability remain
explicitly blocked by unavailable authorized G2/EM9305 physical evidence.

```sh
python3 tools/analyze_g2_cordio_dm_sec_lesc.py --json
python3 tools/verify_research_corpus.py --json
```

The next defensible bounded target is component-9 `dm_phy.c`.
