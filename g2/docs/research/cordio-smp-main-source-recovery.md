# Cordio SMP main source recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The linked `smp_main.c` translation unit is closed to twenty functions and
3,076 code bytes inside `[0x00537278,0x00537EEC)`. The 3,188-byte enclosing
interval contains 112 bytes of alignment, literals, and callback tables. The
only public API without a stock body is `SmpDmGetLtk`; the official source
tree has no external consumer, and the image has no caller or stored pointer,
so it is classified dead-stripped rather than opaque.

Stock is not explained by any one published file. It combines Packetcraft
r20.05-family `keyReady`/LESC behavior with AmbiqSuite 2.5.1's stale-AES-result
queue cleanup. The tracked Apache-2.0 reconstruction is therefore an explicit
patch over the authenticated public source, not a claim that an unpublished
vendor file has been recovered byte for byte.

## Upstream and patch pin

The selected public source is Packetcraft r20.05c:

- commit `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`;
- tree `0a76c7dde46d3b94bb9185a4a5327d0e3f38ec97`;
- Git blob `ba4889305cc903c7283972a12532a83c2a5b9cfe`;
- source SHA-256
  `c0d63cc679b63a0ad188a3a5b9ce36a5457812b077cc6a87d40bb189873d3810`.

The file is byte-identical from r20.05 through r20.05c. Compared with r19 it
adds `smpCcb_t.keyReady`, `SmpDmLescEnabled`, and the `keyReady` gate in
`SmpDmGetStk`; all three survive in stock. AmbiqSuite 2.5.1 instead carries
the older r19 body plus a stale-token handler that drains `secCb.aesEncQueue`.
Stock has both the r20 additions and that Ambiq queue drain.

[`smp_main-ambiq-aes-queue-cleanup.patch`](../../third_party/cordio/g2-patches/smp_main-ambiq-aes-queue-cleanup.patch)
applies cleanly to the exact r20.05c blob. Its SHA-256 is
`0b86bf4ff50cdae14662a9c06824404737993d966523421fd3a347d1c3fbdf52`;
the patched semantic candidate is 24,979 bytes with SHA-256
`dd813e9b3bdf5d4ea6c879a78b7c7e542518a573ea70d18d9e144eb8909b6d74`.
Retained source-line constants 307, 597, and 885 still differ from the patched
candidate by two to five lines, so it remains a semantic source candidate,
not exact downstream text.

## Stock map

| Function | Stock interval | Bytes | Status |
|---|---:|---:|---|
| `smpL2cDataCback` | `0x537278..0x537444` | 460 | registered L2CAP callback |
| `smpL2cCtrlCback` | `0x537444..0x53749C` | 88 | registered L2CAP callback |
| `smpResumeAttemptsState` | `0x53749C..0x537502` | 102 | linked helper |
| `smpDmConnCback` | `0x537502..0x5375C8` | 198 | registered DM callback |
| `smpCcbByHandle` | `0x5375C8..0x5375EE` | 38 | linked lookup |
| `smpCcbByConnId` | `0x5375FC..0x537742` | 326 | product-diagnostic lookup |
| `smpCalcC1Part1` | `0x537742..0x53786C` | 298 | linked crypto helper |
| `smpCalcC1Part2` | `0x53786C..0x537998` | 300 | linked crypto helper |
| `smpCalcS1` | `0x537998..0x5379F4` | 92 | linked crypto helper |
| `smpGenerateLtk` | `0x5379F4..0x537A5A` | 102 | linked key helper |
| `smpSendPkt` | `0x537A5A..0x537BB8` | 350 | retained-path send helper |
| `smpStateIdle` | `0x537BB8..0x537BCA` | 18 | linked state helper |
| `smpMsgAlloc` | `0x537BCA..0x537BD6` | 12 | linked allocation wrapper |
| `SmpDmMsgSend` | `0x537BD6..0x537BE6` | 16 | linked DM wrapper |
| `SmpDmEncryptInd` | `0x537BE6..0x537C00` | 26 | linked encryption callback |
| `smpGetScSecLevel` | `0x537C00..0x537C30` | 48 | LESC security helper |
| `SmpDmLescEnabled` | `0x537C30..0x537C4C` | 28 | r20-only public API |
| `SmpDmGetStk` | `0x537C4C..0x537CB2` | 102 | r20 `keyReady` gate |
| `SmpDmGetLtk` | no body | 0 | dead-stripped source API |
| `SmpHandlerInit` | `0x537CB2..0x537CF8` | 70 | callback registration/init |
| `SmpHandler` | `0x537D0C..0x537E9E` | 402 | Ambiq queue cleanup retained |

The linked body concatenation hashes to
`c70987596989d69f3828cc2d1d5515e7badce57caae5e611f052a75cc55fc88e`;
the enclosing interval hashes to
`bba2ea8b7c5ed581d8202b2b7c2978f0ae8f874eccea15cca7de17ff645732fb`.
The exact 58 direct BL sites, stock/source span hashes, and classifications
are in `tools/manifests/packetcraft-cordio-smp-main-function-map.tsv`.

Four intentional stored Thumb pointers close callback/handler ingress:

- `0x004B878C -> SmpHandler+1` for `WsfOsSetNextHandler`;
- `0x00537ED4 -> smpL2cCtrlCback+1`;
- `0x00537ED8 -> smpL2cDataCback+1`;
- `0x00537EDC -> smpDmConnCback+1`.

No other aligned pointer targets an entry or body interior. The sole retained
source-path cell is `0x00537EAC -> 0x006DE854`.

## SRAM ABI and effective configuration

`smpCb` begins at `0x20070AEC`, is 252 bytes, and contains three 76-byte
connection control blocks followed by the module-wide interface and policy
fields:

```text
smpCcb_t +0x00  16-byte response timer
         +0x10  16-byte wait timer
         +0x20  pairing request
         +0x27  pairing response
         +0x30  scratch pointer
         +0x34  queued-message pointer
         +0x38  connection handle
         +0x3D  connection ID
         +0x3E  state
         +0x41  AES token
         +0x42  attempts
         +0x44  r20 keyReady
         +0x48  secure-connections CCB pointer
         size   0x4C

smpCb    +0xE4  slave interface
         +0xE8  master interface
         +0xEC  handler ID
         +0xF0  pairing procedure callback
         +0xF4  authentication callback
         +0xF8  LESC-supported byte
         size   0xFC
```

The connection count is three. The stale-result cleanup references the
security control block at `0x20072CD8`. The linked SMP database event is
`0x20`, another independent r20 header discriminator.

## Lorelei handoff

The compact returned artifact is
`research/readiness/smp-main/`:

- 5,247 bytes, SHA-256
  `c85369fc50179deef071e6f4e6f48442ee0462097e0ac2515037aded7987f1cc`;
- eleven regular members and ten inner checksum entries;
- two base and two patched/hybrid ARM GCC builds;
- 30 base and 32 hybrid undefined-provider seams;
- two valid hybrid closure links with 1,969/2,159 retained text bytes,
  260 bytes BSS, and zero unresolved symbols.

The two base closure ELFs retained no text, data, or BSS. Their zero-undefined
status is therefore explicitly invalid as closure proof; the provider ledger
is the authority for the base build. This caveat is preserved both inside the
archive and in the distilled repository manifests.

The artifact excludes firmware, upstream and hybrid source, patch bodies,
decompilation, objects, ELFs, and caches. The durable patch, stub source,
identity/build/provider manifests, analyzer, and tests are stored separately
in the repository. Run:

```sh
python3 tools/analyze_g2_cordio_smp_main.py --json
python3 tools/verify_research_corpus.py --json
```

This tranche is source-identified and structurally build-ready, but remains
stock-retained. Production promotion still requires the exact FreeRTOS/IAR
configuration, logger seam, provider relocations, and placement closure.
