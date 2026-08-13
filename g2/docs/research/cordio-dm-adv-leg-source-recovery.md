# Cordio legacy-advertising source recovery

Status date: 2026-08-08  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

Seventeen of eighteen upstream `dm_adv_leg.c` definitions are linked. Their
4,396 code bytes occupy the source-order executable interval
`[0x004B9A80,0x004BAC4E)` together with 162 bytes of inline literals and
alignment. A 100-byte TU-owned trailing literal pool follows at
`[0x004BAC64,0x004BACC8)` after a 22-byte function from the next translation
unit. This IAR interleaving is modeled explicitly rather than falsely assigning
the foreign accessor to `dm_adv_leg.c`.

All function definitions have an exact Apache-2.0 Packetcraft route. The
source bodies alone are invariant from Packetcraft r19.02/AmbiqSuite
R2.4.2/R2.5.1 through Packetcraft r20.05c. Stock nevertheless exposes an
important vendor ABI discriminator: advertising data is stored inline at
message offset `+8`, matching Ambiq's flexible-array `dm_adv.h`, not public
Packetcraft's pointer field. All firmware bytes remain cut forward and package
ownership is unchanged.

## Upstream and ABI pins

The authenticated historical source is:

- Packetcraft r19.02 commit
  `86372d84ef0386d8834ed036e613c8f2ded1ff16`;
- Git blob `604cf245a9393e580670dafbded7b09238d2927c`;
- 18,455 bytes, SHA-256
  `6d07372cea9f22d670a97745b8eeb11b26259e5f5849bb3d3cf0560c25808cb0`.

AmbiqSuite R2.4.2 and R2.5.1 contain those exact bytes. Packetcraft r20.05
through r20.05c differ only in license-header formatting and file mode:

- selected public compatibility commit
  `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`;
- Git blob `d2da987b2aaa8453f2d27be83d3cc6df18b20a68`;
- 18,482 bytes, SHA-256
  `c1e285613912103ffc86b78bd699d65efe6586fc30cbcf4120059ec7045a10a2`.

The stock ABI oracle is Ambiq `dm_adv.h`, Git blob
`e124306318f31f64679878ef35ce043530227604`, SHA-256
`9a0c9f819650454a3044841cb63bfec6598e3a709426b78db30229b41faf9642`.
At `0x004B9E62` and `0x004B9E6E`, stock passes `pMsg + 8` directly to the HCI
advertising/scan-response commands. Public Packetcraft r19/r20 instead embeds
a pointer at that location and is not an exact header ABI oracle.

## Complete stock map

| Function | Stock interval | Bytes | Ingress |
|---|---:|---:|---:|
| `dmAdvConfig` | `0x4B9A80..0x4B9AC0` | 64 | 1 BL |
| `dmAdvActConfig` | `0x4B9AC0..0x4B9D1A` | 602 | action table |
| `dmAdvActSetData` | `0x4B9D24..0x4B9E7A` | 342 | action table |
| `dmAdvActStart` | `0x4B9E88..0x4BA0E6` | 606 | action table |
| `dmAdvActStop` | `0x4BA0F4..0x4BA332` | 574 | action table |
| `dmAdvActRemoveSet` | `0x4BA33C..0x4BA33E` | 2 | action table |
| `dmAdvActClearSets` | `0x4BA33E..0x4BA340` | 2 | action table |
| `dmAdvActSetRandAddr` | `0x4BA340..0x4BA342` | 2 | action table |
| `dmAdvActTimeout` | `0x4BA342..0x4BA456` | 276 | action table |
| `dmAdvReset` | `0x4BA45C..0x4BA490` | 52 | component table |
| `dmAdvHciHandler` | `0x4BA4B0..0x4BA6AC` | 508 | component table |
| `dmAdvMsgHandler` | `0x4BA6AC..0x4BA6C0` | 20 | component table |
| `dmAdvStartDirected` | `0x4BA6D4..0x4BA848` | 372 | 1 BL |
| `dmAdvStopDirected` | `0x4BA864..0x4BA9C8` | 356 | 1 BL |
| `dmAdvConnected` | `0x4BA9D4..0x4BAAF8` | 292 | 1 BL |
| `dmAdvConnectFailed` | `0x4BAB04..0x4BAC28` | 292 | 1 BL |
| `DmAdvInit` | `0x4BAC2C..0x4BAC4E` | 34 | 1 BL |

The concatenated body SHA-256 is
`6e9615c53d77a5e28ee26f6c7f8075cc2b2a02c9664ea857b44537c75726a2d7`.
Exact stock/source hashes and ingress are pinned in
`tools/manifests/packetcraft-cordio-dm-adv-leg-function-map.tsv`.
`DmAdvModeLeg` has no stock body, caller, or pointer and is dead-stripped.

The action table at `0x0075F550` registers eight action entries. The component
table at `0x0078A808` registers reset, HCI, and WSF-message handlers.
`DmAdvInit` installs the latter at `dmFcnIfTbl[DM_ID_ADV]` at `0x20000694`.
The retained path at `0x006DD0B4` has exactly two pointer cells,
`0x004BA4AC` and `0x004BAC8C`.

The six direct calls into the module are `0x4B9D14 -> dmAdvConfig`,
`0x536AD6 -> dmAdvStartDirected`, `0x536AE2 -> dmAdvStopDirected`,
`0x536AF6 -> dmAdvConnected`, `0x536B0A -> dmAdvConnectFailed`, and
`0x4B800E -> DmAdvInit`. Their sorted packed-site SHA-256 is
`bde4f5e02aff769195d83799fb20455d771afdedd4d18932abf2d8dc5e2e377f`.
The interface table is consumed indirectly by device reset, HCI event, and DM
message dispatch; the action handler masks the event to three bits and calls
the eight-entry action table. A full aligned scan finds only these eleven
intentional Thumb pointers and no strict-interior pointer.

The principal non-diagnostic relocations are closed: parameter configuration
calls `DmLlAddrType` and `HciLeSetAdvParamCmd`; set-data calls the advertising
or scan-response HCI command; start/stop/timeout and directed start/stop call
the HCI enable command; reset, HCI completion, connection success, and failure
use the WSF timer and DM private-event providers; initialization calls
`WsfTaskLock`, common `dmAdvInit`, and `WsfTaskUnlock`. Reset and HCI completion
also invoke the application callback indirectly, while message dispatch
invokes the selected action indirectly.

The logical TU identity is the executable/interstitial span concatenated with
its noncontiguous trailing pool, SHA-256
`902fea4c30311567807f9760ee68e22f7f065bf371847c4336b2d1e4033e1a19`.
The enclosing physical envelope includes the foreign accessor and therefore
has a separate SHA-256,
`fc58ec3553867362832beb6c7beffb32fdde45ba452bdc7c1780aa69c25f8d7d`;
it must not be assigned wholesale to this translation unit.

## Configuration and memory layout

Stock proves `DM_NUM_ADV_SETS=2`. The shared `dmAdvCb` at `0x20073394` has:

```text
+0x00 timer             +0x10 intervalMin[2]   +0x14 intervalMax[2]
+0x18 advType[2]        +0x1A channelMap[2]    +0x1C localAddrType
+0x1D advState[2]       +0x20 duration[2]      +0x24 enabled
+0x25 peerAddr[2][6]    +0x31 peerAddrType[2]
```

The legacy advertising-type byte is at `0x20074FB3`. Stable state values are
idle 0, advertising 1, starting-directed 2, starting 3, stopping-directed 4,
and stopping 5. The adjacent vendor accessor `[0x004BAC4E,0x004BAC64)` bounds
its handle argument at two and returns `dmAdvCb.advState[handle]`; it is not
`DmAdvModeLeg` and remains assigned to the following advertising/common-source
investigation.

## Lorelei result and reproducibility

The repository owns
`research/readiness/dm-adv-leg/` (5,952 bytes,
SHA-256
`f143a9a7d5ea51a57d0d6e300fadae142b87e6140b8107a8dda79a49ab9d1323`).
Its fifteen inner hashes authenticate the eighteen-function source inventory,
five conservative retained-path anchors / 1,914 bytes, two ARM GCC profiles,
twenty provider seams, source identities, and two zero-unresolved closure
links. Local authenticated binary closure expands the conservative result to
seventeen linked functions / 4,396 bytes.

The artifact excludes firmware, upstream source, decompilation, objects,
ELFs, and caches. Reproduce the fail-closed checks from `openCFW`:

```sh
python3 tools/analyze_g2_cordio_dm_adv_leg.py --json
python3 tools/verify_research_corpus.py --json
```

Production promotion still requires the forked message producer/header
closure, product diagnostics, exact IAR generation, provider relocations, and
placement. The next targeted pass is the associated common advertising module
and vendor state accessor; `smp_main.c` is the next compact retained-path
module, while `dm_conn.c` remains the largest byte-yield target.
