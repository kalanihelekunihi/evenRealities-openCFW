# G2 app\gui\navigation\navigation.c zero-anchor recovery

- Retained path: `app\gui\navigation\navigation.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\app\gui\navigation\navigation.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-navigation-closure.tsv` (sha256 `7ffa6b956b0227f84e6bb97b6f4aab5a92a4d947b25e90701ec61d27683d9843`)
- Function map: `tools/manifests/g2-navigation-function-map.tsv` (sha256 `f1729a40cf0f1152b31c31610459c331dc5b5becfd34e392b682029972cce053`)
- Audit: `tools/analyze_g2_navigation.py`; test: `tests/test_analyze_g2_navigation.py`

## Identity evidence

- Path string at 0x00703C64; pointer cell(s) 0x005863A8; 10 literal reference(s), all inside the mapped blocks.
- 9 module log-tag strings loaded by the mapped blocks, including:
- `0x0070CCA4` `[navigation.main]set navigation page root obj opacity to 50%%`
- `0x0070CCE4` `[navigation.main]set navigation page root obj opacity to 100%%`
- `0x0070CD24` `[navigation.main] stop process break,RequestDisplayStop again`
- `0x0070CD64` `[navigation.main]navigation_ui_event_handler UI_EVENT_TYPE_INIT`
- `0x00716510` `[navigation.main]navigation_ui_event_handler DISPLAY_EXIT`
- `0x00720478` `[navigation.main]PAGE_EVENT_SYSTEM_EXIT_NOTIFY Event.`
- `0x00756BB8` `[navigation.main]foregroundID = %d`
- `0x00756BDC` `[navigation.main]IMU Reflash Event.`

## Linked extents

Physical interval `[0x00585CBA, 0x00586448)` = 1934 bytes (1744 body + 190 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x585cba-0x585cc2 | 8 | 0 | 3 | `ec17d8a338753360...` |
| 0x585cc2-0x585cca | 8 | 0 | 3 | `66bc3762b6400ba1...` |
| 0x585cca-0x585ce0 | 22 | 0 | 10 | `b7e7725efe2a71e3...` |
| 0x585ce0-0x58607a | 922 | 8 | 345 | `9dae96c37cd056bb...` |
| 0x58607a-0x58638a | 784 | 2 | 326 | `f4fd8df7c1075b82...` |

## Ingress (whole-image scans)

- direct BL entry sites: 2; strict-interior BL targets: 1
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 2
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

Five blocks in gap [0x585CBA, 0x586448). Identity: 10 path references across 2 blocks and 9 `[navigation.main]` log tags. Registration: screen-descriptor cells 0x6A4594 (entry 0x585CCA) and 0x6A4598 (entry 0x58607A); two tiny accessors are called from external sites 0x54EB42/0x54EB4A; one strict-interior BL from 0x504DD0 targets the main block. The trailing 190-byte data pool carries the path cell 0x5863A8 and is included in the physical interval.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_navigation -v
```
