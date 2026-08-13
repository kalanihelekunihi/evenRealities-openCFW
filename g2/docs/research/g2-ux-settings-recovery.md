# G2 app\ux\ux_settings\ux_settings.c zero-anchor recovery

- Retained path: `app\ux\ux_settings\ux_settings.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\app\ux\ux_settings\ux_settings.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-ux-settings-closure.tsv` (sha256 `2dac6ddaf870fbd3a1fb58be4e453dcba2ea2db4ced5532ffe2bb386effe39f1`)
- Function map: `tools/manifests/g2-ux-settings-function-map.tsv` (sha256 `c16c735ee359dc273b2988b978b94078fa3fb502f3aeb22dccab27731bf68bf8`)
- Audit: `tools/analyze_g2_ux_settings.py`; test: `tests/test_analyze_g2_ux_settings.py`

## Identity evidence

- Path string at 0x006FF674; pointer cell(s) 0x005F9ED0; 7 literal reference(s), all inside the mapped blocks.
- 7 module log-tag strings loaded by the mapped blocks, including:
- `0x0071B3D0` `[ux.setting]pMsg->head.msgSelfRole = %d(MASTER_ROLE = %d)`
- `0x00730CC8` `[ux.setting]In production test mode, skip time sync`
- `0x0073B624` `[ux.setting]SID_UX_DEVICE_SETTINGS_APP_ID = %d`
- `0x0073B684` `[ux.setting]sysUtcSecond = %lu time_zone = %d`
- `0x00746AE4` `[ux.setting]pMsg->head.msgPeerRole = %d %d`
- `0x00746B10` `[ux.setting]eDevCfgCommandId_TIME_SYNC
`
- `0x0075142C` `[ux.setting]raw_data = 0x%x,len = %d`

## Linked extents

Physical interval `[0x005F9C8C, 0x005F9F14)` = 648 bytes (572 body + 76 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x5f9c8c-0x5f9ce0 | 84 | 1 | 35 | `7437d3da861c1925...` |
| 0x5f9ce0-0x5f9ec8 | 488 | 6 | 200 | `cca5ec94db188b46...` |

## Ingress (whole-image scans)

- direct BL entry sites: 0; strict-interior BL targets: 0
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 2
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

Two blocks in interval [0x5F9C8C, 0x5F9F14): 7 path references and 7 `[ux.setting]` tags (time sync, production-mode gating, device settings app). Registration: descriptor cells 0x6A4724 (entry 0x5F9C8C) and 0x6A4734 (entry 0x5F9CE0). The trailing 76-byte pool carries path cell 0x5F9ED0. This object shares its corpus gap with ux_production.c; the split at 0x5F9C8C is exact.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_ux_settings -v
```
