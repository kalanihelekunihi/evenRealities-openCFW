# G2 product\s200\app\config\board_config.c zero-anchor recovery

- Retained path: `product\s200\app\config\board_config.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\product\s200\app\config\board_config.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-s200-board-config-closure.tsv` (sha256 `c7607f5d1b6f5d92be97cb1d63d37b400cedcb0bcf8bfdd968b44cd86ce1a66d`)
- Function map: `tools/manifests/g2-s200-board-config-function-map.tsv` (sha256 `654e62f72051ac138d462dbcbf44be1bdf1c84b5ea767f499310b67c25c3db54`)
- Audit: `tools/analyze_g2_s200_board_config.py`; test: `tests/test_analyze_g2_s200_board_config.py`

## Identity evidence

- Path string at 0x006F1BDC; pointer cell(s) 0x005094B8; 1 literal reference(s), all inside the mapped blocks.
- 1 module log-tag strings loaded by the mapped blocks, including:
- `0x00752568` `[BSP]hw_version: %d, hw_adc_val: %d`

## Linked extents

Physical interval `[0x005093D0, 0x0050968C)` = 700 bytes (118 body + 582 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x5093d0-0x509446 | 118 | 1 | 48 | `27a44e873d5bb0e8...` |

## Ingress (whole-image scans)

- direct BL entry sites: 0; strict-interior BL targets: 0
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 0
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

A data-dominated object: 118 bytes of code (1 path reference, tag `[BSP]hw_version: %d, hw_adc_val: %d`) followed by 582 bytes of board configuration data (pinmux/peripheral constant words) up to the next corpus-discovered function at 0x50968C.

Board-config access code is corpus-covered and already documented elsewhere: the watchdog closure records selector provider 0x0050938E, and init-table cell 0x6D1E14 stores 0x005093AD (a corpus-region interior entry). This closure adds the previously unmapped block 0x5093D0-0x509446 plus the full data extent, completing the object.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_s200_board_config -v
```
