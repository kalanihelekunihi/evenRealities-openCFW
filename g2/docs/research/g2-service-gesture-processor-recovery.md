# G2 platform\input\service_gesture_processor.c zero-anchor recovery

- Retained path: `platform\input\service_gesture_processor.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\platform\input\service_gesture_processor.c`
- Stock disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Production disposition: **implemented in compilable C / hardware-blocked**
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-service-gesture-processor-closure.tsv` (sha256 `716968c1639fc0f7aa34014d972e51391e235dc54aa065ece88555d21f972429`)
- Provenance manifest: `tools/manifests/g2-service-gesture-processor-provenance.tsv` (sha256 `679878c9a447d314366f847503d4490faff89cf0b16f31eee14255c7d7ea212d`)
- Function map: `tools/manifests/g2-service-gesture-processor-function-map.tsv` (sha256 `9cba1744560a8e25c60baae07d8b636af0fae55f19c03194e5049f255333e1c2`)
- Audit: `tools/analyze_g2_service_gesture_processor.py`; test: `tests/test_analyze_g2_service_gesture_processor.py`
- Production source: `components/apollo_main/core_overlay/service_gesture_processor.c` (13,061 bytes; sha256 `c69b64097eef2fc592c4be97a1d7a9b0bad9a701544ecc18510ad7aab6c7db4c`)
- Host behavior test: `tests/test_service_gesture_processor_candidate.py`

## Identity evidence

- Path string at 0x006EF958; pointer cell(s) 0x00503238; 5 literal reference(s), all inside the mapped blocks.
- 5 module log-tag strings loaded by the mapped blocks, including:
- `0x006D9974` `[touch.ges]prox:%d, bsln:%5d, kv_bsln:%5d, raw:%5d, diff:%4d, diffX:%3d, speed:%3d, slider:(0x%02x)%s`
- `0x007185A4` `[touch.ges]slider mask = 0x%02x(%s), diffX = %d, speed = %d`
- `0x00743258` `[touch.ges]SLIDER_EVENT_ERROR: reset touch`
- `0x0074DE6C` `[touch.ges]EVENT_SLIDER_SINGLE_CLICK`
- `0x0077B854` `[touch.ges]prox=%s(%u)`

## Linked extents

Physical interval `[0x00502D56, 0x00503298)` = 1346 bytes (1236 body + 110 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x502d56-0x502dae | 88 | 1 | 32 | `b9c55e0c9d939dbf...` |
| 0x502dae-0x502db6 | 8 | 0 | 3 | `b0b65aa4b0b432c3...` |
| 0x502db6-0x502dc2 | 12 | 0 | 4 | `6ca0a840c9b5efba...` |
| 0x502dc2-0x502eee | 300 | 0 | 130 | `6adc09e4ca0f4f67...` |
| 0x502ef4-0x503230 | 828 | 4 | 332 | `41d53f5bb5dd7ef9...` |

## Ingress (whole-image scans)

- direct BL entry sites: 11; strict-interior BL targets: 1
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 0
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

Five blocks recovered in the corpus gap [0x502D56, 0x503298). Identity: 5 path references across 2 blocks and 5 `[touch.ges]` log tags (proximity/slider gesture telemetry). Ingress: the small accessors at 0x502DAE/0x502DB6/0x502DC2 are called from the main block 0x502EF4 and from external sites (0x49EF6A, 0x5725CC-0x572616); the main block is called from 0x513138; one strict-interior BL targets 0x502D58 from inside the main block (shared entry into the first block, pinned).

## Production source closure

The production implementation owns all five recovered behaviors: production-mode single-click buzzer feedback, proximity-state access, retained event-name lookup, the eight-bit gesture-mask formatter, and the complete 16-byte touch-frame dispatcher. That dispatcher preserves debug telemetry, proximity notification, product-mode consumption, error reset/preemption, stock event ordering, and the recovered `difference_x` thresholds.

Apple clang 21 emits five selector-isolated Thumb leaves totaling 1,608 bytes plus six alignment bytes. The leaves are placed at `0x007C24B0`, `0x007C2528`, `0x007C2534`, `0x007C2544`, and `0x007C2790`; 53 strict relocations bind the retained touch, buzzer, product-mode, timestamp/event-publish, logging, SRAM, and sibling-source interfaces. Five guarded `B.W` replacements cover the entire stock physical interval `[0x00502D56, 0x00503298)`—1,346 bytes including both literal pools—so no stock gesture body remains reachable through the recovered ingress topology.

The resulting canonical artifacts are:

- overlay: 192,212 bytes, sha256 `a4c7927efe625a95e3bd928e5bb75b32c057837577dd9b9bf0cc3a5c19a42183`;
- Apollo-main component: 3,715,608 bytes, sha256 `026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a`;
- complete firmware package: 4,494,102 bytes, sha256 `03d4b3f7813ce41814ae821ccbdaa3a1f2802fe4a459cf20351487a18332e783`.

The software functional gap is closed. Physical touch/proximity validation remains explicitly blocked because no authorized G2 hardware or captured electrical/event/timing evidence is available. This is not treated as hardware validation and does not establish overall firmware functional completeness.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_service_gesture_processor -v
/usr/bin/python3 -m unittest tests.test_service_gesture_processor_candidate -v
```
