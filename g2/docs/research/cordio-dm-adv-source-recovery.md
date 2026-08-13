# Cordio common advertising source recovery

## Result

The G2 image links nine functions / 562 code bytes from the common Cordio
`ble-host/sources/stack/dm/dm_adv.c` translation unit. They occupy
`[0x004B3098,0x004B32CA)` and are followed by the ten-byte literal/alignment
pool `[0x004B32CA,0x004B32D4)`. The complete 572-byte interval has SHA-256
`602b39c3a5562ff91272adf5f5db48b27663df6a7c350bce5a4dbbd3fe175b71`.
All eleven direct call sites, all direct callees, and the absence of stored
entry/interior pointers are enforced by
[`analyze_g2_cordio_dm_adv.py`](../../tools/analyze_g2_cordio_dm_adv.py).

This is source identification, not production replacement. Every byte remains
stock-retained while IAR placement and whole-stack integration remain open.

## Exact source and ABI pin

Official AmbiqSuite R2.4.2 and R2.5.1 contain the same Apache-2.0 source:

- `dm_adv.c`: 16,977 bytes, Git blob
  `49be7fa0b651753aa7e13e170d5a6819d46b8196`, SHA-256
  `449c64cce932d729ccd165e3dfd8085b9301e5f3b4b0a87b3e4ce0604ca34df5`;
- `dm_adv.h`: 8,641 bytes, Git blob
  `e124306318f31f64679878ef35ce043530227604`, SHA-256
  `9a0c9f819650454a3044841cb63bfec6598e3a709426b78db30229b41faf9642`.

Packetcraft r19.02 and r20.05--r20.05c are close public comparators, but their
`dmAdvApiSetData_t` contains a payload pointer. Stock instead allocates
`sizeof(dmAdvApiSetData_t) + len`, copies bytes into the message, and passes
`message + 8` to the legacy consumer. That exactly selects Ambiq's flexible
array `uint8_t pData[]` ABI. Public Packetcraft is exact for the other fourteen
definition texts but is not a safe substitute for this message layout.

The surrounding stack still selects Packetcraft r20.05-or-later semantics in
ATT and SMP. The accurate tree-level description is therefore an Ambiq/vendor
fork carrying r20-era Cordio behavior with retained Ambiq advertising and
FreeRTOS ABIs, not one pristine upstream commit.

## Linked function map

| Function | Stock interval | Bytes | Direct callers |
|---|---:|---:|---:|
| `dmAdvCbInit` | `0x4B3098..0x4B30E4` | 76 | 1 |
| `dmAdvInit` | `0x4B30E4..0x4B310A` | 38 | 2 |
| `dmAdvGenConnCmpl` | `0x4B310A..0x4B3166` | 92 | 1 |
| `DmAdvConfig` | `0x4B3166..0x4B319E` | 56 | 1 |
| `DmAdvSetData` | `0x4B319E..0x4B31EA` | 76 | 1 |
| `DmAdvStart` | `0x4B31EA..0x4B3250` | 102 | 1 |
| `DmAdvStop` | `0x4B3250..0x4B3292` | 66 | 2 |
| `DmAdvSetInterval` | `0x4B3292..0x4B32B8` | 38 | 1 |
| `DmAdvSetAddrType` | `0x4B32B8..0x4B32CA` | 18 | 1 |

The exact per-function stock/source hashes and caller lists are in
[`packetcraft-cordio-dm-adv-function-map.tsv`](../../tools/manifests/packetcraft-cordio-dm-adv-function-map.tsv).
Six APIs are source-only/dead-stripped: `DmAdvRemoveAdvSet`,
`DmAdvClearAdvSets`, `DmAdvSetRandAddr`, `DmAdvSetChannelMap`,
`DmAdvSetAdValue`, and `DmAdvSetName`.

## Recovered configuration and dependencies

`DM_NUM_ADV_SETS=2`. The common control block is at `0x20073394`; `dmCb` is
at `0x20073B78`. `DmAdvSetData`'s eight-byte fixed message header is followed
immediately by copied payload. The linked provider closure is eleven symbols:
`BdaCpy`, `DmFindAdType`, `WsfMsgAlloc`, `WsfMsgSend`, `WsfTaskLock`,
`WsfTaskUnlock`, `dmCb`, `dmDevPassHciEvtToConn`, `memcpy`, `memmove`, and
`memset`.

The six eliminated APIs are excluded from stock coverage rather than labeled
opaque. The first four have no public-tree consumer; the advertising-value and
name helper chain is absent from this product image.

## Lorelei readiness

Lorelei compiled the exact Ambiq source/header overlay against the pinned
Packetcraft r20.05c dependency tree with `DM_NUM_ADV_SETS=2`,
`DM_CONN_MAX=3`, tracing disabled, and assertions disabled. ARM GCC 13.2.1
completed `-Os` and `-O1` profiles; both isolated closure ELFs have zero
undefined symbols. The compact, checksum-authenticated result is
[`dm-adv-readiness-artifact.tar.gz`](../../research/readiness/dm-adv/),
SHA-256 `11383daf11300da416384668c592e7e705e51a147b27738dee12a38837cde523`.
It deliberately excludes upstream source, firmware, objects, ELFs, and caches.

## Reproduce

```sh
python3 tools/analyze_g2_cordio_dm_adv.py --json
python3 -m unittest tests.test_analyze_g2_cordio_dm_adv
python3 tools/verify_research_corpus.py --json
```

The remaining work is exact IAR code-generation/placement comparison and
integration with a complete source-owned DM/WSF message path. Module-level
identification is 95--98%; production source ownership is unchanged.
