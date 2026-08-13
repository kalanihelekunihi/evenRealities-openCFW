# EM9305 expanded SDK archive census

Status date: 2026-08-08  
Status: two discovery rounds covering 48 SDK archives authenticated and
scanned; boundary-qualified scanning proves 1,435 exact stock functions /
154,966 bytes, and strict/NOP-aware link order plus vector-ABI recovery raises
the exact map to 1,494 / 157,122 bytes; all bytes remain stock-retained.

## Result

The first six-library audit proved 98 exact functions / 7,172 bytes. The
expanded census applies the same relocation-normalized comparison to 16 more
archives from the authenticated EM9305 SDK v4.2 oracle. Discovery requires at
least 16 non-relocated compared bytes, a unique halfword-aligned location in
the 210,888-byte stock application, the exact archive Git blob and SHA-256,
and the exact MetaWare compiler anchors.

After removing archive/profile aliases, the expanded lane proves **1,146
distinct exact stock functions / 132,610 non-overlapping bytes**. The earlier
six enforced archives are disjoint and bring the first-round result to **1,244
exact functions / 139,782 bytes**.

A second 32-archive Lorelei lane produced 8,542 raw unique-location match
records. Global address/body deduplication shows that 1,134 of its 1,201
distinct functions were already proven by the earlier lanes. The **67 new
functions / 13,078 new bytes** comprise 62 Packetcraft ISO/BIG controller
functions (12,624 bytes), four EM system NVM erase/write functions (328
bytes), and `AOAD_Init` (126 bytes). At the conservative 16-byte floor this
produces 1,311 exact functions / 152,860 bytes.

An authenticated 8-compared-byte replay then exposes 129 additional short or
relocation-heavy candidates / 2,196 bytes. The analyzer promotes only the 124
functions / 2,106 bytes with an independent entry-boundary or code/pointer
reference and rejects five uncorroborated candidates, including one 10-byte
body nested inside a known 20-byte function. The boundary-qualified scanner
result is therefore **1,435 exact functions / 154,966 non-overlapping bytes**,
or **73.482607%** of the complete EM9305 application record. A subsequent
strict exact-neighbor link-order pass resolves 16 duplicate-location exact
functions / 784 bytes. Its NOP-aware extension adds 34 exact bodies / 774
bytes and 123 non-exact placements / 9,080 bytes. Vector-table ABI resolution
adds three exact interrupt bodies / 574 bytes and identifies one 186-byte
modified radio-TX body. The current exact result is
**1,494 functions / 157,122 bytes (74.504950%)**. The exact complement is
53,766 bytes and mixes modified executable code, constants, tables, padding,
and alignment; it is not all anonymous proprietary source.

| Measure | Functions/records | Bytes | Application share |
|---|---:|---:|---:|
| Expanded 16-archive records before alias removal | 2,180 | — | — |
| Expanded distinct address/body fingerprints | 1,146 | 132,610 | 62.881719% |
| Earlier six enforced archives | 98 | 7,172 | 3.400857% |
| First-round combined exact coverage | 1,244 | 139,782 | 66.282577% |
| Round-two raw match records | 8,542 | — | — |
| Round-two distinct address/body fingerprints | 1,201 | 144,740 | 68.633587% |
| Round-two incremental after global deduplication | 67 | 13,078 | 6.201396% |
| 16-byte-floor combined exact coverage | 1,311 | 152,860 | 72.483973% |
| Boundary-qualified 8-byte-floor increment | 124 | 2,106 | 0.998634% |
| Boundary-qualified scanner coverage | 1,435 | 154,966 | 73.482607% |
| Link-order-resolved exact increment | 16 | 784 | 0.371761% |
| NOP-aware link-order exact increment | 34 | 774 | 0.367019% |
| Vector-ABI-resolved exact interrupt increment | 3 | 574 | 0.272182% |
| Current combined exact function coverage | 1,494 | 157,122 | 74.504950% |
| Not exact-function matched | — | 53,766 | 25.495050% |
| Function provenance identified, including non-exact placements | 1,647 placed identities | 167,684 | 79.513296% |
| Not function-provenance identified | — | 43,204 | 20.486704% |

All 1,146 address/body groups agree. There are no conflicting bodies and no
overlapping distinct function spans. Eight addresses have legitimate symbol
aliases, including shared SWI/timer handlers and source-identical wrapper
names; the analyzer retains every alias rather than guessing which symbol the
linker selected.

## Archive results

The manifest is `tools/manifests/em9305-sdk-discovery.tsv`. Zero-match rows are
kept because they are useful negative configuration evidence.

| Archive label | Git blob | Unique match records | Deterministic report SHA-256 |
|---|---|---:|---|
| `app_entry` | `ffca8a5bc6b956f8899d05971e0dce040ada7902` | 3 | `89f51de5cd749f3f49b63ad07c47b5f11ea8750955898146d0f867815d33332b` |
| `em_core` | `47b2d5fd0adacaec2913ec0f5d2a7b0e7f1e1394` | 3 | `6f49ee753cba0882a0eb40fc66cf00c485a789275f6a5829f9698548f9b05e9e` |
| `em_hw_api` | `729ca978bb728f0289db4b3ee743e333670e4dc1` | 37 | `8c501926a8950b2086106144a03283eea7641143f4c4aeb57bc56496dcd3fd77` |
| `em_system` | `47acd3c20c78d983b605267b18d4f8d6eb1e50d1` | 27 | `b0f868849611b734c2a573f0c8373a4d4121572cdf6c625a73299bb996777708` |
| `em_system_stack` | `88605d53ff5322789a101b52c885e5f0de1989b4` | 2 | `d02ed501ebf6e4a81f3a1dc5d038d900c3b3a7d46e96bd5e0f2ae62ffd5aaedc` |
| `memory_manager` | `6c6106a9bcc80df1230c85a849a3261422373465` | 0 | `d4b12043265376f580858259894b021d843c26f14def95ba9c1ba84c4f7e45b9` |
| `nvm_fix` | `d5bef24c4c9a5288a8e7c52394d993f1d5d02043` | 3 | `5acb80e3dee07e408c5234dd98121e85852699ab9bcff7ad397102fb828805ab` |
| `nvm_entry` | `b42f99d5cb9f9ffedef5fa3095e92a3e2da3a970` | 1 | `331a110b0a4bffa90e6822b525eeae1fbad3f7091ad77b25bf423dfd65ebb054` |
| `radio` | `00ce66bc3ff9968c8b233fd740332fde85d061b4` | 34 | `e3bb729a1ee7c47b46cf84347e0b0cc3c94ece6d0c3d90cec390e757fb69f55f` |
| `rc_calib` | `2a19d0c43bf03121a5a85117cc160e0b67033535` | 2 | `032badc6aa95a14705b8db74b0e53ab3fa2116f2ce72c027a66c68cae012274a` |
| `rtc` | `307432195b55958ed992bd2565efb4ce3b498e31` | 0 | `48e58d68f0ebf48af194a36f1b0b704dea38a7a1db5dabe3fb27cb3b85853665` |
| `emb_controller` | `6a1a8e3df756a97e0afbcf7d10482eecc7856336` | 1,057 | `d9320ce9cc048ff7adc88252aa4886810a3e9f0935eca8012c3de8fc6e6ad0ba` |
| `emb_database` | `d0261d8f2a8edc72178234f44f35166dfe423128` | 0 | `cf4e1f227e30084f428721d8f2b3c40b99b161b31de47fd6bef632c5bba4d877` |
| `emb_ll_pal` | `1a175c48bdd6a0cb7cae5f96d7bff3350799ae6f` | 30 | `1565c05cdf96d901b86e0362e6f29bfda9b6fcb690125a60544b6b27efe609a8` |
| `emb_peripheral` | `c9e2ee6f0762fb710aa987000cb0fd6eb4bcce79` | 980 | `56625d6bc61fbc9671a9714a740b388ab4518e6927bd068b606cbf23cfd455de` |
| `transport` | `3d0e76655f2fdcc5e4bbca697b79a72010581580` | 1 | `6ba1e79739e7887d72f73b848e03dc704f58ecf6bacff2b95e1599f676806dbe` |

The `emb_peripheral` address set is a subset of `emb_controller`; 77 distinct
controller addresses are absent from the peripheral artifact. `emb_ll_pal`
is also contained in the controller result. These are corroborating archive
profiles, not 2,067 different stock functions, which is why the address/body
deduplication is mandatory.

## Round-two results

The second manifest is `tools/manifests/em9305-sdk-discovery-round2.tsv`. It
tests 20 EM peripheral/system archives and 12 alternate Packetcraft profiles.
Only three artifacts add globally new addresses:

| Archive | Raw unique-location records | New functions | New bytes | Result |
|---|---:|---:|---:|---|
| `lib_emb_controller_iso.a` | 1,119 | 62 | 12,624 | Exact ISO/BIG link-time bodies added |
| `lib_em_system_di03.a` | 31 | 4 | 328 | `EMSMM_NVMEraseFull/Main/Page`, `EMSMM_WriteContinue` |
| `lib_aoad.a` | 1 | 1 | 126 | `AOAD_Init` |
| Other 29 archives | 7,391 | 0 | 0 | Corroborating aliases or zero-match negative evidence |

No address/body conflicts and no overlapping distinct function spans occur in
either 16-byte-floor round or across the six enforced lanes. The
boundary-qualified low-floor result has 867 merged intervals. Adding the
link-order-resolved exact bodies merges adjacent spans and leaves 858. Alternate
central, peripheral, advanced-advertising, audio,
CTE, and PAwR profiles corroborate already-matched controller bodies without
adding coverage; ADC, DMA, firmware-update, GPIO, I2C/I2S, NVM scheduler,
QDEC, security, SPI, temperature, printf, and UART archives add no unique
16-byte-floor match.

## Packetcraft/EM Bleu identity and configuration

The exact controller artifact is `lib_emb_controller.a`, Git blob
`6a1a8e3df756a97e0afbcf7d10482eecc7856336`, SHA-256
`3b256ac3352955dc4bd9b49554e011e1587be7fdb58538f0ac7b9d4fe42ac971`.
It supplies 1,057 unique-match records at 1,055 address/body fingerprints.
Controller-only matches include PAWR paths and `LlExtCreateConnV2`, excluding
the SDK's Bluetooth-5.2 peripheral profile as a complete explanation of stock.

The header shipped beside the baseline controller archive describes Bluetooth
**5.4** (`BT_VER=13`), all four roles enabled, encryption enabled, PAST and
power control enabled, CTE and ISO disabled, `LL_MAX_CONN=4`, `LL_MAX_FRAG=8`, `LL_NUM_ADV_FILT=8`,
`LL_MAX_ADV_SETS=2`, `LL_SCAN_PHY_MAX=3`, and `LL_MAX_PER_SCAN=6`. Its header
is Git blob `628db5e2b144e268e12fb11a896cfd0bc11940f2`, SHA-256
`a76f0d2e25c95280469a87c5f8f1498fb7de45e29df2e6b622e68569488d1df3`.
The exact second-round `lib_emb_controller_iso.a` matches 62 additional
ISO/BIG bodies in stock. Consequently this header is exact evidence for that
archive/profile but is not a complete description of the final stock link;
link-time presence alone also does not prove that every ISO path is enabled at
runtime.

The bundled Packetcraft `ll_api.h` records `LL_VER_NUM=28992`, Git blob
`e0520e13cdf260efc9363420e41eead2bf0ee05d`, SHA-256
`e88417326161c50aec5adb15193324fa5b4a7cced9f1496d978b39f66756ea46`.
Packetcraft's official public `stacks` repository ends at r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`, whose corresponding header uses
`LL_VER_NUM=1366` and Git blob `c677bd4e007a8afc823a5ae4318ee0e3bb2206cd`.
The public commit is therefore an older comparator, not the stock source pin.
The exact later source state is pinned only to the third-party SDK oracle's
file blobs; no authoritative public Packetcraft commit has been found.

The included Packetcraft files carry confidential/proprietary license notices.
Exact matching does not grant redistribution or production-source rights.
Until an applicable licensed source release is available, these spans remain
authenticated firmware-cutting boundaries.

## Representative recovered map

The full 1,435-function scanner map, 67-function round-two increment,
124-function low-floor promotion, and five rejected low-floor candidates are emitted by
`tools/analyze_em9305_sdk_discovery.py --include-functions` when all three
evidence locations are supplied. Representative
anchors include:

| Address | Identity |
|---:|---|
| `0x00302AE8` | `BOOT_BootUp` |
| `0x003032CC` | `BbBleInit` |
| `0x0030B974` | Bluetooth-5.4 `LlExtCreateConnV2` |
| `0x0030FB4C` | `PalBbBleSetChannelParam` |
| `0x0031028C` | `PalRadioInit` |
| `0x00313F54` | `WsfCsEnter` |
| `0x003140D0` | `WsfOsStartOnly` |
| `0x00333C44` | `wsfDispatcherThread` |

The map also names 96 HCI-related and 29 WSF-named distinct functions, plus
link-layer manager, baseband, scheduler, radio/PAL, NVM, EM system, and boot
closures. This closes the earlier `WsfOs` family-only lead at the artifact and
function level, while keeping the unavailable authoritative source commit and
license as explicit unresolved provenance.

`tools/analyze_em9305_sdk_link_order.py` consumes that dynamic map and the
authenticated ISO-controller archive report. It enforces 156 strict and
NOP-aware ranges / 202 placements, including 50 exact bodies and 51 same-size
or size-delta modified functions. Vector-table ABI recovery adds four
interrupt-handler placements / 760 bytes, including three exact bodies. The
complete dynamic address/status map and
modified-body semantics are in the
[link-order recovery report](em9305-sdk-link-order-recovery.md); the
[residual census](em9305-residual-segment-census.md) partitions every
remaining byte.

## Parallel reproduction and evidence

The optimized matcher uses the longest unmasked byte run as a `bytes.find()`
anchor and validates every remaining non-relocated byte at each hit. Its result
is equivalent to the earlier exhaustive halfword scan and is regression-tested.
The known QP/C archive now scans in 0.32 seconds on Lorelei. The 16-archive
batch completed with zero failures at 16 jobs; the largest controller profile
finished in 12.228 seconds.

```sh
python3 tools/run_em9305_sdk_archive_batch.py \
  --manifest tools/manifests/em9305-sdk-discovery.tsv \
  --archive-root /path/to/authenticated/sdk/tree \
  --comparator tools/compare_em9305_sdk_archive.py \
  --image blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin \
  --binutils-dir /path/to/arc-linux-gnu/bin \
  --output-dir /new/empty/output \
  --jobs 16 \
  --minimum-compared-bytes 16

python3 tools/analyze_em9305_sdk_discovery.py \
  --batch-output /path/to/round1/output \
  --enforced-output /path/to/six/enforced/reports \
  --round2-output /path/to/round2/output \
  --round1-min8-output /path/to/round1/min8/output \
  --round2-min8-output /path/to/round2/min8/output \
  --application-objdump /path/to/authenticated/application-objdump.txt
```

The observed minimum-16 batch hashes are `9ceba48429ed1dd3e3f82da7fd2220032d0a3370aa8f4653ff074fdf30b45c8b`
for `results.tsv`, `4cd26a8f8a8843d4b9e8321b30bfc1c92b9c77aceab8bbce22719b9e35d6a6ae`
for `INPUTS.tsv`, `aca2b78f5db46a399dbb6080ea9157ca6d3a8c48cb97ebd7a599af74388dff50`
for `CONFIG.json`, and `4986e7a6927b1653b7ecaea0869663724d636b8e1aae6f38e6700f472f6b6bbb`
for `SHA256SUMS`. `results.tsv` contains timings and is an observed-run hash;
the per-archive report hashes above are deterministic acceptance identities.

The verified return is preserved under
`opencfw-em9305-sdk-batch16-min16-return.XNpW2a/output` in the
repository-owned Lorelei corpus at `research/corpus/`; the remote directory
is now a disposable working copy.

The 32-archive round-two output is authenticated by SHA-256
`cee18fc3f9e8824d6052c66e4d62ea1fffa047bbaefc666f47864bfa874b5514`
for `results.tsv`, `5213cd19fb8d5aa2fcb895a750a5c77e345ff0fc4116a0580994c85d2015f755`
for `INPUTS.tsv`, `aca2b78f5db46a399db6080ea9157ca6d3a8c48cb97ebd7a599af74388dff50`
for `CONFIG.json`, and
`46257b8c61a34f24935df1cf37be3c85ee55c0ee4ef35b947b7514ae5076fe57`
for `SHA256SUMS`. The verified return is preserved under
`opencfw-em9305-sdk-round2-return.4mZWiA/output` in the repository-owned
Lorelei corpus. Every individual report identity is enforced in
`tools/analyze_em9305_sdk_discovery.py`.

The first and second low-floor checksum ledgers hash to
`6df037edc55e1b3419147d13c57eddd8f33826ca9f718c98391e6577944e87f7`
and `34a29df939004dc1d38bcaefd1bbb9800c0ce189ac9678298342be307a484db9`;
their input ledgers hash to
`49f2342424c6691dfa2b585ed4430a624d4c3dbdbbf085107f25643e5f710c50`
and `148aef0872acd533995c0dd3b9d9ff8e91947dc6b856300cc508b84c5e2fd68e`.
The whole-application GNU ARCv2 EM disassembly used for branch/pointer entry
corroboration hashes to
`13d1e9c7c0d2c2d3db9436d21ec6d90a39622446cb8ab96de5c2c01ba752916f`.
The five candidates deliberately withheld from exact-function coverage are
`TI_RegisterModule @ 0x00312260`, `lctrExtAdvActAdvTerm @ 0x00319958`,
`lctrStoreDisconnectReason @ 0x0032CA90`, nested
`lctrCisLlcpActIntPeerDisc @ 0x0032CFF2`, and
`lctrTransferSyncActCancel @ 0x0032D0F4`.
