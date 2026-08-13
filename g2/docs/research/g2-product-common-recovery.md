# G2 platform\product_test\product_common.c zero-anchor recovery

- Retained path: `platform\product_test\product_common.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\platform\product_test\product_common.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-product-common-closure.tsv` (sha256 `72d45d341d5c401912cb0ba951ed5082367aec2ba5dc50ef7c95540fed5c2ac8`)
- Function map: `tools/manifests/g2-product-common-function-map.tsv` (sha256 `d3067c597fdc26238887bcd146d6ee3888498b6039025745d15639c12c1c3dea`)
- Audit: `tools/analyze_g2_product_common.py`; test: `tests/test_analyze_g2_product_common.py`

## Identity evidence

- Path string at 0x006F5360; pointer cell(s) 0x0058F4A4; 6 literal reference(s), all inside the mapped blocks.
- 6 module log-tag strings loaded by the mapped blocks, including:
- `0x0070DD24` `[product_common]font crc: mismatch, calc=0x%04x expect=0x%04x`
- `0x007179EC` `[product_common]font crc: len overflow, base=0x%08x len=%u`
- `0x00717A28` `[product_common]font crc: match, calc=0x%04x expect=0x%04x`
- `0x0072BE60` `[product_common]font crc: invalid base addr 0x%08x`
- `0x00736B54` `[product_common]font crc: len=%u, crc16=0x%04x`
- `0x0074C8B4` `[product_common]font crc: invalid len=0`

## Linked extents

Physical interval `[0x0058F1EC, 0x0058F4E4)` = 760 bytes (686 body + 74 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x58f1ec-0x58f208 | 28 | 0 | 11 | `0b0743f3eab2535a...` |
| 0x58f208-0x58f486 | 638 | 6 | 246 | `9eb5db1335d59c95...` |
| 0x58f486-0x58f490 | 10 | 0 | 4 | `574a735e745153b7...` |
| 0x58f490-0x58f49a | 10 | 0 | 4 | `0ebc276f82c1e48d...` |

## Ingress (whole-image scans)

- direct BL entry sites: 6; strict-interior BL targets: 0
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 0
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

Four blocks in gap [0x58F1EC, 0x58F4E4). Identity: 6 path references in block 0x58F208 and 6 `[product_common]` log tags covering the font CRC validation routine. The following block at 0x58F4E4 carries references to `platform\product_test\production_mic_func.c` (a different retained path); the boundary between the two product-test objects is exact and guard-pinned.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_product_common -v
```
