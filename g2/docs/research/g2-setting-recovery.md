# G2 app\gui\setting\setting.c zero-anchor recovery

- Retained path: `app\gui\setting\setting.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\app\gui\setting\setting.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-setting-closure.tsv` (sha256 `902a937de908ee29800f3af7287b541175e0c6690ee3f8448c23b9ff4785fa55`)
- Function map: `tools/manifests/g2-setting-function-map.tsv` (sha256 `489307b2bd664218c8bf30d64bf874ed7376c7b6f48e356c494580cbc937b571`)
- Audit: `tools/analyze_g2_setting.py`; test: `tests/test_analyze_g2_setting.py`

## Identity evidence

- Path string at 0x0070F3A4; pointer cell(s) 0x004672EC 0x00467F10; 51 literal reference(s), all inside the mapped blocks.
- 51 module log-tag strings loaded by the mapped blocks, including:
- `0x006D5A58` `[setting]Received universal unit setting: unit_format=%d, distance_unit=%d, time_format=%d, date_format=%d, temperature_unit=%d`
- `0x006E5248` `[setting]dominant_hand ring_mac changed, reconnect required old[5-3]=%02X:%02X:%02X:`
- `0x006E52A0` `[setting]dominant_hand ring_mac changed, reconnect required new[5-3]=%02X:%02X:%02X:`
- `0x006E52F8` `[setting]dominant_hand: ring_mac recovered from factory placeholder, delay connect %ums`
- `0x006E9FDC` `[setting]dominant_hand ring_mac changed, reconnect required old[2-0]=%02X:%02X:%02X`
- `0x006EA030` `[setting]dominant_hand ring_mac changed, reconnect required new[2-0]=%02X:%02X:%02X`
- `0x006EA084` `[setting]setting_handle_dominant_hand: rejected within switch window, keep cur=%u`
- `0x006EFC78` `[setting]Updated gesture config: screen_off=[%d,%d,%d], screen_on=[%d,%d,%d]`

## Linked extents

Physical interval `[0x0046687C, 0x00467F08)` = 5772 bytes (5486 body + 286 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x46687c-0x466890 | 20 | 0 | 9 | `f39f93df5cac7f91...` |
| 0x466890-0x4668ae | 30 | 0 | 13 | `f87dec57883918eb...` |
| 0x4668ae-0x466976 | 200 | 2 | 73 | `5390649539decdeb...` |
| 0x466976-0x466abc | 326 | 4 | 116 | `0c57bf727e05064a...` |
| 0x466abc-0x466bec | 304 | 2 | 111 | `c8c663abff03b28c...` |
| 0x466bec-0x466e1c | 560 | 6 | 199 | `09be236db066bb6e...` |
| 0x466e1c-0x466ea2 | 134 | 1 | 48 | `b20a30dd9b6ba7f7...` |
| 0x466ea2-0x466f28 | 134 | 1 | 48 | `029adbeac90086a3...` |
| 0x466f28-0x467134 | 524 | 5 | 193 | `7a9bda3ee6fc7004...` |
| 0x467134-0x46713e | 10 | 0 | 4 | `921fc227e642c042...` |
| 0x46713e-0x4671a2 | 100 | 1 | 39 | `5846972019c733f6...` |
| 0x4671a2-0x467206 | 100 | 1 | 38 | `1b36ca5e9ce694f7...` |
| 0x467206-0x4672da | 212 | 2 | 84 | `b9ba55378bf9687e...` |
| 0x467308-0x4674a6 | 414 | 4 | 155 | `04e0dd3d92148646...` |
| 0x467540-0x467c18 | 1752 | 16 | 630 | `aeeaa02d0d5b2150...` |
| 0x467c34-0x467d52 | 286 | 4 | 109 | `57bb6b7164852592...` |
| 0x467d68-0x467e4a | 226 | 1 | 92 | `e3a55b3858430c16...` |
| 0x467e68-0x467f02 | 154 | 1 | 63 | `5c010c15b5e1c5a0...` |

## Ingress (whole-image scans)

- direct BL entry sites: 17; strict-interior BL targets: 0
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 4
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

Eighteen blocks in gap [0x46687C, 0x467F08), the largest object in this batch: 51 literal references to two retained path strings (cells 0x4672EC inside the interval and 0x467F10 pooled into the following object) across 17 blocks, and 51 `[setting]` log tags (universal unit setting, dominant-hand ring-mac recovery, etc.). Registration: descriptor cells 0x6A4634, 0x6A4644, 0x6A4648 and 0x793D03; intra-object call chain fans out from entry 0x4668AE; one external BL site 0x46C1A2 reaches helper 0x466890.

The head bytes [0x4667EA, 0x46687C) are excluded: they follow the preceding corpus function and decode as alignment/data residue of the previous object; the boundary is guard-pinned.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_setting -v
```
