# G2 app\gui\system\system_monitor.c zero-anchor recovery

- Retained path: `app\gui\system\system_monitor.c`
- Product path: `D:\01_workspace\s200_ap510b_iar_git\app\gui\system\system_monitor.c`
- Disposition: **linked-unanchored** (code present; zero Ghidra-anchored/discovered functions)
- Image: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (sha256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`)
- Closure manifest: `tools/manifests/g2-system-monitor-closure.tsv` (sha256 `f91cb16eb47066893e9d398177291ade7602d65b3eb030998d07528d254b2584`)
- Function map: `tools/manifests/g2-system-monitor-function-map.tsv` (sha256 `d55d118073e2513f1073c343cc330bc3b91f7e00cd38736d292545b19268aab8`)
- Audit: `tools/analyze_g2_system_monitor.py`; test: `tests/test_analyze_g2_system_monitor.py`

## Identity evidence

- Path string at 0x00706590; pointer cell(s) 0x005850EC; 6 literal reference(s), all inside the mapped blocks.
- 6 module log-tag strings loaded by the mapped blocks, including:
- `0x006D9AAC` `[system_monitor]system_monitor_common_data_handler: master role, send idle command to schedule manager`
- `0x006EFEA8` `[system_monitor]system_monitor_common_data_handler: eventType = %d, len = %d`
- `0x006EFEF8` `[system_monitor]system_monitor_common_data_handler: foreground app is running`
- `0x006EFF48` `[system_monitor]system_monitor_common_data_handler: background app is running`
- `0x006FD814` `[system_monitor]system_monitor_common_data_handler: display is running`
- `0x0070FA64` `[system_monitor]system_monitor_common_data_handler: peer reboot`

## Linked extents

Physical interval `[0x00584EE4, 0x00585134)` = 592 bytes (510 body + 82 pool/data).

| extent | bytes | path refs | instructions | sha256 |
|---|---|---|---|---|
| 0x584ee4-0x5850e2 | 510 | 6 | 198 | `2ca72e1b082381cb...` |

## Ingress (whole-image scans)

- direct BL entry sites: 0; strict-interior BL targets: 0
- direct B.W entry sites: 0; direct 16-bit B entry sites: 0
- stored entry-pointer words: 1
- function escapes (tail merges/calls out of a block): 0; indirect blx sites: 0

## Boundary attribution and notes

A single 510-byte screen block with 6 path references and 6 `[system_monitor]` tags, registered through descriptor cell 0x6A4674, plus an 82-byte trailing pool carrying path cell 0x5850EC. Zero direct BL/B ingress; the descriptor is the sole entry vector.

## Verification

```
/usr/bin/python3 -m unittest tests.test_analyze_g2_system_monitor -v
```
