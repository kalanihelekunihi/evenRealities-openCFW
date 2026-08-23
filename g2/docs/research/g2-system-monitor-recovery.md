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

## Production source closure (2026-08-23)

`components/apollo_main/core_overlay/system_monitor.c` now implements the
complete peer-reboot callback as compilable freestanding C. Event five accepts
the authenticated six-byte `55 04 12 34 56 78` sentinel, requests a zeroed
display command for a running foreground or background application, waits at
most eleven 100-tick intervals for the display to quiesce, sends scheduler idle
from lens side one, then performs the dashboard, application-state,
onboarding-color, terminal-state, and lens-status reset/publication sequence.
The only deliberate behavioral correction rejects NULL or records shorter than
six bytes before the stock sentinel reads.

The Apple profile emits one 650-byte leaf at overlay offset 165,440 / runtime
`0x007BC964`. Forty-three fail-closed Thumb relocations bind the three
EasyLogger seams, display-state predicates, display command, source-owned
FreeRTOS delay and lens-side providers, scheduler-idle sender, reset providers,
and source-owned lens-status publisher. A guarded `B.W` plus NOP fill replaces
all 510 stock body bytes at `[0x00584EE4,0x005850E2)`; the descriptor at
`0x006A4674` continues to enter through that stock address.

Focused host tests cover rejected records, foreground/background dispatch,
the eleven-delay bound, master/secondary behavior, and the complete ordered
reset surface. Canonical overlay/component/package identities are
`166090/3689486/4467980` bytes with SHA-256 values
`1120724be7e02326ec5273397bd9fcacbbd973883b1787c67fcaa9835fc943e8`,
`18e578a6824ab184f35309489af07972a41a74da465bc5ecc07c182e2b42d05f`, and
`a643e0fdf5d90b8f34b9fe5b3833d239e27bd28dd2d18f7bc6163182c99e11e9`.
No hardware was accessed. Paired-device reboot, display, and scheduler timing
validation is explicitly blocked by unavailable authorized physical evidence.
