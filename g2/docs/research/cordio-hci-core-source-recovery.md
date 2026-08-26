# Ambiq Cordio HCI core recovery

Status date: 2026-08-25
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

Stock G2 contains 22 of the 24 definitions in Ambiq's proprietary
`sources/hci/ambiq/hci_core.c`. The complete physical translation unit is
`[0x0052A67C,0x0052AE38)`, 1,980 bytes: 1,964 executable body bytes and one
16-byte literal pool. `hciCoreTxAclDataFragmented` and
`HciSetAclQueueWatermarks` are the only source-only definitions.

This is now both a complete inclusion result and a production source-ownership
result. Thirty-two
decoded direct `BL` sites reach all 22 surviving entries. An aligned
whole-image word scan finds no stored entry pointer and no pointer into a
strict body interior. Both removed functions lack a body slot, direct caller,
or stored pointer. The exact per-function source line span, source-body hash,
stock interval, body hash, and ingress classification are recorded in
[`ambiq-cordio-hci-core-function-map.tsv`](../../tools/manifests/ambiq-cordio-hci-core-function-map.tsv).

## Exact stock boundaries

| Object | Interval | Bytes | SHA-256 |
|---|---:|---:|---|
| Physical translation unit | `[0x0052A67C,0x0052AE38)` | 1,980 | `89aa38ab7907c0b6a8b18d1949c7dbf9d85dc382b528e396ac3a6e8f35b505e3` |
| Concatenated linked bodies | 22 spans | 1,964 | `5fdf336b7831dad9ec50157d35551af8ebdd9ee6e525d8ac5e99c487e42f7cd5` |
| Literal pool | `[0x0052AE14,0x0052AE24)` | 16 | `e6dc2ab51885972f75da408b86a5a46c89dcf84b311345328c11506fd92b4260` |

The literal pool separates `hciCoreCisByHandle` from the final two CIS
wrappers and contains exactly:

| Cell | Value | Meaning |
|---:|---:|---|
| `0x0052AE14` | `0x20071478` | `hciCoreCb` |
| `0x0052AE18` | `0x20073870` | external `hciCb` |
| `0x0052AE1C` | `0x20000028` | 64-bit `hciLeSupFeatCfg` |
| `0x0052AE20` | `0x200714CC` | `hciCoreCb.cis`, at control-block offset `0x54` |

The next translation unit begins at `0x0052AE38`. No retained `hci_core.c`
path exists, so ownership rests on source order, exact body semantics, the
closed caller graph, literal ownership, and the adjacent HCI event boundary.

## Recovered ABI and configuration

The stock control block begins at `0x20071478`. It contains three 28-byte
connection records, followed by six two-byte CIS handles at offset `0x54`.
The connection record's controller handle is at `+0x10`, fragmentation flag
at `+0x16`, flow-disabled flag at `+0x17`, queued-buffer count at `+0x18`, and
outstanding-buffer count at `+0x19`. The ACL queue begins at control-block
offset `0x70`; maximum receive length and queue watermarks are initialized to
27, 14, and 13.

`HciSetLeSupFeat` accepts a 64-bit mask in `r0:r1` plus the enable flag in
`r2`, then atomically ORs or clears those bits in the 64-bit object at
`0x20000028`. `HciCoreInit` also initializes all six CIS handles to `0xFFFF`.
Those two properties decisively exclude AmbiqSuite R2.5.1's 32-bit,
non-CIS implementation.

The public ACL sender queues the message, updates per-connection accounting,
starts service when the queue becomes nonempty and buffers are available, and
disables flow at the high watermark. Its indirect flow callback is at
`hciCb+0x14`. The lower `hciTrSendAclData` provider returns success/failure;
the core start/continue/ready paths preserve a queued fragment when the
transport declines it. Receive reassembly accepts a first fragment too short
to contain the full two-byte L2CAP length, fixes the expected length after a
continuation, and rejects overlong continuation data.

Reset drains the receive queue, frees all transmit and receive fragments for
the three connection records, restores the handles and fragmentation state,
services returned buffers, sets the external HCI resetting flag, and starts
the vendor reset sequence. Connection and CIS open/close calls originate in
the already closed event port.

## Public behavior source and proprietary lineage boundary

The implementation is independently adapted from Packetcraft Cordio r20.05c
`ble-host/sources/hci/common/hci_core.c` at commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6` (blob
`fe9a1f0cba1749c166e434d7cef90a167d1ed9c1`, 30,369 bytes, SHA-256
`6bfe1f1f37bf97bc86fa8f83345192bdbc813eff9ddac66108f91c2cf04c4b5e`).
That public behavior source is Apache-2.0. Authenticated disassembly supplies
only G2-specific ABI, inclusion, state-address, and behavioral facts.

The authenticated AmbiqSuite R2.5.1 file has 19 definitions, a 32-bit LE
feature configuration, and no CIS functions:

```text
blob    8d8202f644ebfdfd9fa4d604d0196c1f97d7d9fc
bytes   28,330
sha256  b3f5fb83b9fc7a50a305442bcf94715f674fbda3e94c722458f21ea2f5bd01bb
```

The selected reconstruction oracle is the later official AmbiqSuite R4.4.1
import:

```text
commit  4264b9309e03064ffad13a0468d5d0c1110c5288
blob    1f81040608ca6f977d37a58aad5ab0b63229d607
bytes   35,068
sha256  03ab8c9d340dd8cc9958779f6e336188cca2bbbc92ef39759dc165e84835e549
```

Its 24-definition, 64-bit/CIS architecture is the exact stock source family.
It is not an exact whole-file text match: that later neuralSPOT import inserts
a 500-microsecond delay in `HciSendAclData`, while stock has no such call. A
still-later nsx copy adds BT5.3/5.4 priority-queue and trace behavior that is
also absent. The most accurate classification is therefore **R4-era source
family with a product/local ACL-send variant**, while the historical G2
producing commit remains unresolved.

All three Ambiq lineage oracle files carry the proprietary Arm Cordio software
license. No proprietary source text, source-derived patch, object, or header
is copied into openCFW. The repository retains only clean-room facts from
those files: symbols, addresses, hashes, ABI, configuration, control flow, and
independently described behavior.

## Production admission

`runtime_cordio_hci_core.c` implements all 24 definitions. Twenty-two guarded
redirects replace all 1,964 bounded stock function bytes with 3,690 compiled
Thumb bytes plus 26 alignment bytes under 50 strict relocations. The two
source-only definitions target-compile. Host tests cover connection and CIS
lifecycle, transport refusal with fragment preservation, queued ACL flow,
partial-first-header L2CAP reassembly, overlong continuation rejection, reset
draining, 64-bit features, maximum-RX policy, and validated watermarks.

The common-core and platform-shim routes coexist in the canonical component;
the promotion and manifest synchronizers resolve their overlapping names by
most-specific prefix. The canonical overlay/component/package are 375,186 /
3,898,582 / 4,677,076 bytes with SHA-256 `8c05945a…a3c3`,
`8dcb804c…8598`, and `e4579c12…b049`. The 3,937,595-byte flash plan hashes to
`15a2fac0…e92` and contains 5,668 placed, two unresolved, five
container-only, and six protected regions.

## Reproduction

```sh
python3 tools/analyze_g2_cordio_hci_core.py --json
make cordio-hci-core-closure
```

No image was signed, flashed, or installed. Live controller ACL/event/ISO
flow, reset timing, RF behavior, and peer interoperability remain explicitly
blocked by unavailable authorized responsive G2/EM9305 physical evidence.
This software slice is closed; wider HCI and firmware functional completeness
is not claimed.
