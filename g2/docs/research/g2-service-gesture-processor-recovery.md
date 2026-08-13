# G2 platform\input\service_gesture_processor.c zero-anchor recovery

- Retained path: `platform\input\service_gesture_processor.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\platform\input\service_gesture_processor.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-service-gesture-processor-closure.tsv` (sha256 `1b9731141c2e94281cb02261343218573c0a8de3fb55138e799fb9f0b1fcfb89`)
- Function map: `tools/manifests/g2-service-gesture-processor-function-map.tsv` (sha256 `9cba1744560a8e25c60baae07d8b636af0fae55f19c03194e5049f255333e1c2`)
- Audit: `tools/analyze_g2_service_gesture_processor.py`; test: `tests/test_analyze_g2_service_gesture_processor.py`

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

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_service_gesture_processor -v
```
