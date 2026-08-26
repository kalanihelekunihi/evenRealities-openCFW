# Ambiq Cordio vendor reset-sequence recovery

Status date: 2026-08-25
Target: G2 `s200_v2.2.6.10` Apollo main

## Closure

The stock vendor/reset object is `[0x00569B04,0x00569D4C)`, 584 bytes,
SHA-256 `9509223fa164fab9f580b13bb3cab31e17d41929c636f43b1a4ba5fc435af441`.
Four linked bodies contribute 546 bytes; a two-byte alignment plus nine-word
literal pool contributes 38 bytes. The linked bodies are the resolving-list
and maximum-data-length helpers, `hciCoreResetStart`, and
`hciCoreResetSequence`. Four trivial or bypassed vendor hooks are source-only:
`hciCoreVsCmdCmplRcvd`, `hciCoreVsEvtRcvd`, `hciCoreHwErrorRcvd`, and
`HciVsInit`.

Five exact direct calls enter the bodies and they issue 25 direct provider
calls. No stored pointer reaches an entry or strict interior, and no direct
branch reaches a strict interior. The two exterior roots are the HCI core's
reset-start call and the platform shim's command-completion forwarding call;
the other three calls are internal helper transitions.

## Product reset chain

Stock starts by queuing both HCI Reset and the custom BD-address update. The
command-completion state machine then performs this product-specific chain:

1. Reset (`0x0C03`) completion clears the four-command random counter and
   sends NVDS update `0xFFF2`.
2. NVDS completion sets RF power with parameter 6 through `0xFCC4`.
3. RF-power completion sends the standard event mask.
4. Standard, LE, and page-2 masks are followed by controller address, buffer,
   state, whitelist, 64-bit feature, resolving-list, and maximum-data-length
   discovery.
5. Four LE Random completions clear `hciCb.resetting` and emit the reset-
   sequence-complete callback.

The literal pool pins `hciCoreCb=0x20071478`, `hciCb=0x20073870`, the 64-bit
feature configuration at `0x20000028`, the random counter at `0x20074FD0`,
all three event masks, `hciCoreCb.bdAddr`, and `hciCoreCb.leStates`.

## Source lineage

AmbiqSuite R2.5.1 `hci_vs_apollo3.c` (blob
`d87b3476c0b0e3179476ea68e2b7fe6d1d2568d4`, SHA-256
`241e49dcd92b7d68300388df290144a6cf6dcd70419354ee1ad8316054cfbd2a`)
provides the older Apollo3 structure under the proprietary Arm Cordio SLA.
The later official R3.1.1 Apollo3 import (blob
`b994f4e4c625835877d37efeaa1bdc49b770d29c`, SHA-256
`6559513745a91da000187be7cef780ebe99543de0a983849e9c6c69559ad56e4`)
matches the stock reset-start topology and carries Ambiq's BSD-style notice.

The official R4.4.1 Cooper import (blob
`3dcbbb4e64011229d13e7865978a8e79816f8603`, SHA-256
`71b4914c5344bd6197c73ab3b124bfe25ef380d8afa15e9aa07bee79bae2ec78`)
supplies the newer NVDS-first idea but uses a different reset/link-layer-
feature order. Stock is therefore an independently evidenced Apollo3/Cooper
product hybrid, not an exact copy of either later file. The later imports are
reconstruction oracles rather than G2 historical producing commits; openCFW
imports no vendor implementation bytes.

[`analyze_g2_cordio_hci_vs.py`](../../tools/analyze_g2_cordio_hci_vs.py)
authenticates every body and literal, the complete source inventory, direct
ingress/provider digests, reset constants, and the absence of interior
ingress. The source and provenance ledgers live beside it under
`tools/manifests/ambiq-cordio-hci-vs-*.tsv`.

## Production admission

Clean-room `runtime_cordio_hci_vs.c` implements all eight definitions. Four
guarded redirects replace all 546 linked stock bytes with 862 compiled Thumb
bytes and six alignment bytes under 23 strict relocations. The four unlinked
hooks remain target-compilable fail-closed no-ops. No proprietary vendor source
was copied.

Host tests exercise feature-gated resolving-list and maximum-data-length
discovery, the exact Reset → NVDS → RF power → event-mask/capability chain,
state extraction, extension callback behavior and fallback, four-random reset
completion, null/non-command rejection, and all no-op hooks. The canonical
overlay/component/package are 375,186 / 3,898,582 / 4,677,076 bytes with
SHA-256 `8c05945a…a3c3`, `8dcb804c…8598`, and `e4579c12…b049`; the
3,937,595-byte flash plan hashes to `15a2fac0…e92` and contains 5,668 placed,
two unresolved, five container-only, and six protected regions.

Reproduction:

```sh
make cordio-hci-vs-closure
```

No image was signed, flashed, or installed. Live controller reset, NVDS,
address, RF-power, timing, and completion-callback validation remains blocked
by unavailable authorized responsive G2/EM9305 physical evidence. This
software slice is closed; wider HCI and firmware completeness is not claimed.
