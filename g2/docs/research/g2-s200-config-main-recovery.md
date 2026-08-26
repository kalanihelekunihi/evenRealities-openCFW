# G2 product\s200\app\config\main.c zero-anchor recovery

- Retained path: `product\s200\app\config\main.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\product\s200\app\config\main.c`
- Disposition: **implemented-in-source; hardware-blocked**
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-s200-config-main-closure.tsv` (sha256 `6d7f796812c37988d3925b98d5d81fdcfc88e4ab45d72d4078bbbbf8525cf165`)
- Function map: `tools/manifests/g2-s200-config-main-function-map.tsv` (sha256 `494176c0fd0f6710220a021787c5b2133aa78dc36d12bf232e3122c68b97e992`)
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

Refreshed authenticated-image analysis corrected the old linear-recovery
error at `0x5CDB88`: it begins pointer/data bytes, while the true second Thumb
entry is `0x5CDBAC`. Physical interval `[0x005CDB46, 0x005CE140)` remains
1,530 bytes (1,468 body + 62 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x5cdb46-0x5cdb7e | 56 | 0 | 24 | `baff21f7708cadc1...` |
| 0x5cdbac-0x5cdc90 | 228 | 0 | 92 | `445f2c95f9f0b158...` |
| 0x5cdc90-0x5cdd0c | 124 | 0 | 47 | `4892536cca79a248...` |
| 0x5cdd14-0x5cdd6c | 88 | 0 | 27 | `cb6282e54f31fbf1...` |
| 0x5cdd6c-0x5ce01e | 690 | 10 | 261 | `654534508a3b8547...` |
| 0x5ce01e-0x5ce138 | 282 | 4 | 113 | `7ab3827532079f00...` |

## Ingress (whole-image scans)

- direct BL entry sites: 2; strict-interior BL targets: 0
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 3
- function escapes: 0; indirect `blx` sites: 1

## Boundary attribution and notes

Identity rests on 14 literal references to the retained path across 2 blocks and 10 `[mainThread]` log tags (startup-reason and version banner strings).

Startup evidence: the Cortex-M vector table at 0x438000 holds initial SP 0x2007FB00, reset handler 0x005E4233, NMI 0x004397A7, HardFault 0x005B0115 (the 32 bytes at 0x437FE0-0x438000 are an image header, not vectors). The reset chain runs 0x5E4232 -> 0x5E4254 -> 0x5E4270 (CPACR/FPU enable) onward into corpus-covered startup.

Registration evidence: entry 0x5CDB46 is stored in LVGL class-table cell 0x7566B4 (next to the `lv_tabview` class string), entry 0x5CDC90 in cell 0x756760, and entry 0x5CDD14 in init-table cell 0x6D1E2C alongside other module initializers; one external BL site 0x5E472A also reaches the cluster. The file is a product configuration/startup grab-bag: custom LVGL widget constructors, an init hook, and the main thread body.

The former `0x5CDB88` escape was a false decode through data and has been
removed. One genuine indirect `blx` site exists at `0x5CE134`; it invokes the
startup hand-off stored in SRAM cell `0x200040D8`.

The trailing fragment [0x5CE140, 0x5CE1DC) is excluded: it tail-merges into this object and into the corpus-discovered entry 0x5CE1DC, which the baseline path census anchors to `platform\protocols\pb_service_ring\pb_service_ring.c`. It is left to that anchored path's closure and is pinned here only as a boundary note.

## Production source closure

`components/apollo_main/core_overlay/s200_config_main.c` provides all six
guarded production leaves. It preserves both LVGL callbacks, widget
construction, platform initialization order, release registration,
reset-reason priority and the brown-out status-clear side effect, product-RTOS
initialization, the SRAM startup hand-off, and the terminal main-thread loop.
EasyLogger-only diagnostics are deliberately excluded.

The leaves compile to 584 text bytes plus four alignment bytes under 47 strict
relocations, replacing all 1,468 stock body bytes while retaining the 62
literal/data bytes. Canonical artifacts are:

- overlay: 426,982 bytes, SHA-256 `20be6b6564d35dcaa5d4b0e6e6db659e93b7ebc287085bc5b263b8b6ccb5b4fd`
- Apollo component: 3,950,378 bytes, SHA-256 `5e92895a86a57ece34100c494e8ec99132d20e2567734b9e4c9285c0f152fa8a`
- package: 4,728,872 bytes, SHA-256 `8c7bd2469ac367b6b2139798ae68d7d08cf49f79e17f8c6fc9fd0fd47cb02eba` (byte-identical pinned rebuild)

No image was signed, flashed, or installed. Live startup, reset-controller,
clock/power, LVGL input, and task hand-off validation is explicitly blocked by
unavailable authorized physical evidence.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_s200_config_main tests.test_s200_config_main_candidate -v
```
