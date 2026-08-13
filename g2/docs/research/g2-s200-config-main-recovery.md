# G2 product\s200\app\config\main.c zero-anchor recovery

- Retained path: `product\s200\app\config\main.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\product\s200\app\config\main.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-s200-config-main-closure.tsv` (sha256 `67b43269009184ecf854757b32e2408b9c98df49dc06504be3e7350652b3c7c4`)
- Function map: `tools/manifests/g2-s200-config-main-function-map.tsv` (sha256 `0f9b3dc8e765f2da26bcde3e0c32942e36a78a15ae85db2c7e2ce53802359c2a`)
- Audit: `tools/analyze_g2_s200_config_main.py`; test: `tests/test_analyze_g2_s200_config_main.py`

## Identity evidence

- Path string at 0x00703ACC; pointer cell(s) 0x005CE154; 14 literal reference(s), all inside the mapped blocks.
- 14 module log-tag strings loaded by the mapped blocks, including:
- `0x0070CA24` `[mainThread]Startup reason: SW Power On Initialization reset`
- `0x00720328` `[mainThread]Software Version:[%s],Build time:[%s-%s].
`
- `0x0072AAE0` `[mainThread]Startup reason: Watch Dog Timer reset`
- `0x00735564` `[mainThread]Startup reason: SW Power-On reset`
- `0x0073FDEC` `[mainThread]Startup reason: External reset`
- `0x0073FE18` `[mainThread]Startup reason: Power-On reset`
- `0x0073FE44` `[mainThread]Startup reason: Brown-Out reset`
- `0x0073FE70` `[mainThread]Startup reason: Debugger reset`

## Linked extents

Physical interval `[0x005CDB46, 0x005CE140)` = 1530 bytes (1504 body + 26 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x5cdb46-0x5cdb7e | 56 | 0 | 24 | `baff21f7708cadc1...` |
| 0x5cdb88-0x5cdc90 | 264 | 0 | 110 | `5df338ce3d34990d...` |
| 0x5cdc90-0x5cdd0c | 124 | 0 | 47 | `4892536cca79a248...` |
| 0x5cdd14-0x5cdd6c | 88 | 0 | 27 | `cb6282e54f31fbf1...` |
| 0x5cdd6c-0x5ce01e | 690 | 10 | 261 | `654534508a3b8547...` |
| 0x5ce01e-0x5ce138 | 282 | 4 | 113 | `7ab3827532079f00...` |

## Ingress (whole-image scans)

- direct BL entry sites: 2; strict-interior BL targets: 0
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 3
- function escapes (tail merges/calls out of a block): 1; indirect blx sites: 1

## Boundary attribution and notes

Identity rests on 14 literal references to the retained path across 2 blocks and 10 `[mainThread]` log tags (startup-reason and version banner strings).

Startup evidence: the Cortex-M vector table at 0x438000 holds initial SP 0x2007FB00, reset handler 0x005E4233, NMI 0x004397A7, HardFault 0x005B0115 (the 32 bytes at 0x437FE0-0x438000 are an image header, not vectors). The reset chain runs 0x5E4232 -> 0x5E4254 -> 0x5E4270 (CPACR/FPU enable) onward into corpus-covered startup.

Registration evidence: entry 0x5CDB46 is stored in LVGL class-table cell 0x7566B4 (next to the `lv_tabview` class string), entry 0x5CDC90 in cell 0x756760, and entry 0x5CDD14 in init-table cell 0x6D1E2C alongside other module initializers; one external BL site 0x5E472A also reaches the cluster. The file is a product configuration/startup grab-bag: custom LVGL widget constructors, an init hook, and the main thread body.

Function 0x5CDB88 tail-branches into the interior of function 0x5CDB46 (shared compiler block, pinned as the single function escape); one indirect `blx` site exists at 0x5CE0B4.

The trailing fragment [0x5CE140, 0x5CE1DC) is excluded: it tail-merges into this object and into the corpus-discovered entry 0x5CE1DC, which the baseline path census anchors to `platform\protocols\pb_service_ring\pb_service_ring.c`. It is left to that anchored path's closure and is pinned here only as a boundary note.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_s200_config_main -v
```
