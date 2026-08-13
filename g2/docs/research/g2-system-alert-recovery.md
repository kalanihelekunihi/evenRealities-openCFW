# G2 app\gui\SystemAlert\systemAlert.c zero-anchor recovery

- Retained path: `app\gui\SystemAlert\systemAlert.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\app\gui\SystemAlert\systemAlert.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-system-alert-closure.tsv` (sha256 `dc3618004843ef868d7738df5a7c6e5e74226605a6abe7866a9fef0c5a44c166`)
- Function map: `tools/manifests/g2-system-alert-function-map.tsv` (sha256 `70bfe0ac4ea1d67fdc4aac21423d4c52f4b578a86d3610dd7a74e6a11a6ddb41`)
- Audit: `tools/analyze_g2_system_alert.py`; test: `tests/test_analyze_g2_system_alert.py`

## Identity evidence

- Path string at 0x006FD85C; pointer cell(s) 0x004D3424; 12 literal reference(s), all inside the mapped blocks.
- 12 module log-tag strings loaded by the mapped blocks, including:
- `0x00723B60` `[system_alert]PAGE_EVENT_FOREGROUND_ENTER_ANIM_COMPLETE`
- `0x00723B98` `[system_alert]send system alert auto exit event to self`
- `0x00723BD0` `[system_alert]PAGE_EVENT_FOREGROUND_EXIT_ANIM_COMPLETE`
- `0x0072E38C` `[system_alert]unknown system alert event type: %d`
- `0x00738F54` `[system_alert]MessageNotify recv data len = %d`
- `0x00738F84` `[system_alert]system_alert_ReflashEventHandler`
- `0x00744388` `[system_alert]system_alert_MainPage_init`
- `0x0075A9BC` `[system_alert]IMU Reflash Event.`

## Linked extents

Physical interval `[0x004D2B9A, 0x004D34C4)` = 2346 bytes (2176 body + 170 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x4d2b9a-0x4d2bce | 52 | 0 | 22 | `6215de2ee5c2a1b0...` |
| 0x4d2bce-0x4d2c42 | 116 | 1 | 43 | `6189a4e959fc4a0b...` |
| 0x4d2c42-0x4d2f48 | 774 | 7 | 283 | `801b96e90bc4eb30...` |
| 0x4d2f48-0x4d306c | 292 | 0 | 110 | `aea35e0460a4feb4...` |
| 0x4d306c-0x4d30ba | 78 | 0 | 33 | `0f20bbf47ca9dded...` |
| 0x4d30ba-0x4d3354 | 666 | 2 | 255 | `a3457b5a5d777194...` |
| 0x4d3354-0x4d341a | 198 | 2 | 83 | `282ceb27872c7463...` |

## Ingress (whole-image scans)

- direct BL entry sites: 7; strict-interior BL targets: 1
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 2
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

Seven blocks in gap [0x4D2B9A, 0x4D34C4). Identity: 12 path references across 4 blocks and 12 `[system_alert]` tags. Registration: descriptor cells 0x6A4684 (entry 0x4D2BCE) and 0x6A4688 (entry 0x4D3354); helper 0x4D306C is called externally (0x47D40C, 0x47D42E, 0x47D6E0, 0x47D70E, 0x58186C); entry 0x4D2B9A is reached by a strict-interior BL from inside block 0x4D2C42 (pinned). The trailing 170-byte pool carries the path cell 0x4D3424.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_system_alert -v
```
